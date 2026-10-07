"""Persistent, app-owned LUT collection. No UI or webview dependencies."""
from dataclasses import dataclass
import hashlib
import json
import os
from pathlib import Path
import shutil
import tempfile
import uuid
import sys

from conversion_service import ConversionService

FILMS = (
    ("Fuji_Astia_Soft.cube", "Astia", "柔和人像"),
    ("Fuji_Classic_Chrome.cube", "Classic Chrome", "克制纪实"),
    ("Fuji_Classic_Negative_NC.cube", "Classic Negative", "复古负片"),
    ("Fuji_Monochrome.cube", "Monochrome", "黑白层次"),
    ("Fuji_Provia_Standard.cube", "Provia", "自然标准"),
    ("Fuji_Velvia_Vivid.cube", "Velvia", "鲜明风景"),
)


def default_library_root():
    if sys.platform == "win32":
        base = Path(os.getenv("LOCALAPPDATA", Path.home() / "AppData" / "Local"))
    elif sys.platform == "darwin":
        base = Path.home() / "Library" / "Application Support"
    else:
        base = Path(os.getenv("XDG_DATA_HOME", Path.home() / ".local" / "share"))
    return base / "CUBE TO XMP" / "Library"


@dataclass(frozen=True)
class LibraryItem:
    id: str
    path: Path
    name: str
    source: str
    size: int
    builtin: bool
    note: str = ""
    original_name: str = ""

    def public(self):
        return {"id": self.id, "name": self.name, "source": self.source,
                "size": self.size, "builtin": self.builtin, "note": self.note,
                "filename": self.original_name or self.path.name}


class LutLibrary:
    def __init__(self, bundle_root, data_root=None, service=None):
        self.bundle_root = Path(bundle_root)
        default_root = default_library_root()
        self.data_root = (Path(data_root) if data_root else default_root).resolve()
        self.files = self.data_root / "files"
        self.index_path = self.data_root / "library.json"
        self.service = service or ConversionService()
        self.files.mkdir(parents=True, exist_ok=True)
        self._records = self._read_index()

    def _read_index(self):
        if not self.index_path.exists():
            return []
        try:
            records = json.loads(self.index_path.read_text(encoding="utf-8"))
            if not isinstance(records, list):
                raise ValueError("Invalid library index")
            return [record for record in records if isinstance(record, dict)]
        except (ValueError, OSError):
            raise ValueError(f"LUT 库索引无法读取：{self.index_path}")

    def _save_index(self):
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=self.data_root,
                                         prefix=".library-", suffix=".tmp", delete=False) as stream:
            temporary = Path(stream.name)
            json.dump(self._records, stream, ensure_ascii=False, indent=2)
        try:
            os.replace(temporary, self.index_path)
        finally:
            temporary.unlink(missing_ok=True)

    def items(self):
        result = []
        for filename, label, note in FILMS:
            path = self.bundle_root / "built_in_luts" / filename
            if path.is_file():
                document = self.service.load_lut(path)
                result.append(LibraryItem("builtin:" + filename, path, label,
                                          document.source, document.size, True, note))
        for record in self._records:
            filename = record.get("file", "")
            if not isinstance(filename, str) or Path(filename).name != filename:
                continue
            path = self.files / filename
            if path.is_file():
                result.append(LibraryItem(record["id"], path, record["name"].replace("_", " "),
                                          record["source"], record["size"], False,
                                          original_name=record.get("original_name") or
                                          record["name"].replace(" ", "_") + "." + record["source"].lower()))
        return result

    def get(self, item_id):
        return next((item for item in self.items() if item.id == item_id), None)

    def import_paths(self, paths):
        added = []
        originals = list(self._records)
        fingerprints = {record.get("sha256") for record in self._records}
        copied = []
        candidates = []
        for path in paths:
            source = Path(path).resolve()
            document = self.service.load_lut(source)
            with source.open("rb") as stream:
                digest = hashlib.file_digest(stream, "sha256").hexdigest()
            if digest in fingerprints:
                continue
            fingerprints.add(digest)
            candidates.append((source, document, digest))
        try:
            for source, document, digest in candidates:
                item_id = uuid.uuid4().hex
                filename = item_id + source.suffix.lower()
                target = self.files / filename
                shutil.copyfile(source, target)
                copied.append(target)
                record = {"id": item_id, "file": filename,
                          "name": (document.title or source.stem).replace("_", " "),
                          "original_name": source.name,
                          "source": document.source, "size": document.size, "sha256": digest}
                self._records.append(record)
                added.append(item_id)
            if added:
                self._save_index()
        except OSError:
            self._records = originals
            for target in copied:
                target.unlink(missing_ok=True)
            raise
        return added

    def remove(self, item_id):
        record = next((r for r in self._records if r.get("id") == item_id), None)
        if not record:
            return False
        self._records.remove(record)
        self._save_index()
        (self.files / record["file"]).unlink(missing_ok=True)
        return True

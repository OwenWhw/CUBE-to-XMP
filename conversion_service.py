"""Local application backend. UI-independent contract for a future codec rewrite."""
from dataclasses import dataclass
from datetime import datetime
import math
import os
from pathlib import Path
import tempfile
import xml.etree.ElementTree as ET

from PIL import Image, ImageFilter, ImageOps
from lut_core import parse_cube, parse_xmp, build_cube, build_xmp, interpolate_3d


class ConversionError(ValueError):
    pass


@dataclass(frozen=True)
class LutDocument:
    path: Path
    title: str
    size: int
    samples: tuple
    source: str

    @property
    def target(self):
        return "XMP" if self.source == "CUBE" else "CUBE"


@dataclass(frozen=True)
class ExportResult:
    path: Path
    source: str
    target: str
    size: int
    created_at: str


def xmp_metadata(content, group, description):
    root = ET.fromstring(content)
    ns = {"crs": "http://ns.adobe.com/camera-raw-settings/1.0/",
          "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#"}
    for key, value in (("Group", group), ("Description", description)):
        node = root.find(f".//crs:{key}/rdf:Alt/rdf:li", ns)
        if node is not None:
            node.text = value
    ET.register_namespace("x", "adobe:ns:meta/")
    for key, uri in ns.items():
        ET.register_namespace(key, uri)
    return ET.tostring(root, encoding="unicode")


class ConversionService:
    """The frontend calls these real operations; no HTTP server is necessary."""
    sizes = (16, 17, 25, 32, 33, 64, 65)

    def load_lut(self, path):
        path = Path(path).resolve()
        suffix = path.suffix.lower()
        if suffix not in (".cube", ".xmp"):
            raise ConversionError("请选择 .cube 或包含 RGBTable 的 .xmp 文件。")
        if not path.is_file():
            raise ConversionError("文件不存在，请重新选择。")
        if path.stat().st_size > 100 * 1024 * 1024:
            raise ConversionError("LUT 文件过大（上限 100 MB）。")
        if suffix == ".cube":
            # The current codec supports normalized 3D LUTs. Reject unsupported
            # domains explicitly rather than silently applying incorrect colors.
            with path.open(encoding="utf-8-sig") as stream:
                for line in stream:
                    parts = line.split("#", 1)[0].split()
                    if not parts:
                        continue
                    if parts[0] == "LUT_1D_SIZE":
                        raise ConversionError("目前支持 3D LUT，不支持 1D LUT。")
                    if parts[0] in ("DOMAIN_MIN", "DOMAIN_MAX"):
                        expected = 0.0 if parts[0] == "DOMAIN_MIN" else 1.0
                        if len(parts) != 4 or any(float(v) != expected for v in parts[1:]):
                            raise ConversionError("目前仅支持 DOMAIN 0–1 的 LUT。")
        title, size, samples = parse_cube(path) if suffix == ".cube" else parse_xmp(path)
        if not isinstance(size, int) or not 2 <= size <= 65:
            raise ConversionError("LUT 网格需为 2–65。")
        if len(samples) != size**3:
            raise ConversionError(f"LUT 数据不完整：需要 {size**3} 个采样点，实际 {len(samples)} 个。")
        if not all(math.isfinite(v) for rgb in samples for v in rgb):
            raise ConversionError("LUT 包含无效数值。")
        return LutDocument(path, title, size, tuple(samples), suffix[1:].upper())

    def load_photo(self, path):
        with Image.open(path) as source:
            photo = ImageOps.exif_transpose(source).convert("RGB")
            photo.thumbnail((2560, 1920), Image.Resampling.LANCZOS)
            return photo.copy()

    def preview(self, photo, document):
        if document is None:
            return photo.copy()
        lut = ImageFilter.Color3DLUT(document.size, document.samples, channels=3)
        return photo.convert("RGB").filter(lut)

    def export(self, document, path, size, group="Profiles", description=""):
        size = int(size)
        if size not in self.sizes:
            raise ConversionError("请选择有效的输出网格。")
        path = Path(path).resolve()
        expected = "." + document.target.lower()
        if path.suffix.lower() != expected:
            raise ConversionError(f"输出文件扩展名应为 {expected}。")
        if path == document.path:
            raise ConversionError("输出路径不能覆盖当前源文件。")
        actual_size = min(size, 32) if document.target == "XMP" else size
        if document.target == "XMP" and any(not 0 <= v <= 1 for rgb in document.samples for v in rgb):
            raise ConversionError("当前 XMP 编码器仅支持 0–1 的输出色值；请先规范化此 LUT。")
        samples = (interpolate_3d(document.samples, document.size, actual_size)
                   if actual_size != document.size else document.samples)
        if document.target == "XMP":
            content = xmp_metadata(build_xmp(document.title, actual_size, samples), group, description)
        else:
            content = build_cube(document.title, actual_size, samples)
        # Stage beside the target so a conversion/write failure cannot leave a
        # truncated destination. The native save dialog handles overwrite consent.
        temp_path = None
        try:
            with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=path.parent,
                                             prefix=".lut-", suffix=".tmp", delete=False) as stream:
                temp_path = Path(stream.name)
                stream.write(content)
            os.replace(temp_path, path)
        finally:
            if temp_path and temp_path.exists():
                temp_path.unlink()
        return ExportResult(path, document.source, document.target, actual_size,
                            datetime.now().strftime("%H:%M:%S"))

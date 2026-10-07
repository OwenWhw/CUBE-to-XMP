"""WebView2 desktop shell and typed bridge to the local conversion service."""
import base64
from io import BytesIO
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
from threading import RLock

from PIL import Image
import webview

from conversion_service import ConversionService
from lut_library import LutLibrary
from window_chrome import color_webview_frame, prepare_webview_open, reveal_webview_window

ROOT = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent))


def open_local_folder(folder):
    if sys.platform == "win32":
        os.startfile(str(folder))
    else:
        subprocess.Popen(["open" if sys.platform == "darwin" else "xdg-open", str(folder)],
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def image_data(image, maximum=(2560, 1920), quality=93):
    preview = image.copy()
    preview.thumbnail(maximum, Image.Resampling.LANCZOS)
    output = BytesIO()
    preview.save(output, format="JPEG", quality=quality, optimize=True)
    return "data:image/jpeg;base64," + base64.b64encode(output.getvalue()).decode("ascii")


class StudioBridge:
    def __init__(self, root=ROOT, data_root=None):
        self._root = Path(root)
        self._service = ConversionService()
        self._library = LutLibrary(self._root, data_root, self._service)
        self._settings_path = self._library.data_root.parent / "settings.json"
        self._settings = self._load_settings()
        self._lock = RLock()
        self._window = None
        self._photo = self._service.load_photo(self._root / "assets" / "coastal-light.png")
        self._thumbnail_photo = self._make_thumbnail_photo(self._photo)
        self._photo_name = "内置演示照片"
        self._original_data = image_data(self._photo)
        self._selected = None
        self._document = None
        self._after_data = self._original_data
        self._history = []
        self._thumbnails = {}

    @staticmethod
    def _make_thumbnail_photo(photo):
        thumbnail = photo.copy()
        thumbnail.thumbnail((800, 500), Image.Resampling.LANCZOS)
        return thumbnail

    def _load_settings(self):
        defaults = {"language": "zh", "theme": "light", "motion": True}
        try:
            saved = json.loads(self._settings_path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            return defaults
        if not isinstance(saved, dict):
            return defaults
        return {key: saved.get(key) if saved.get(key) in choices else value
                for key, value, choices in (("language", "zh", ("zh", "en")),
                                             ("theme", "light", ("light", "dark")),
                                             ("motion", True, (True, False)))}

    def update_settings(self, changes):
        def action():
            if not isinstance(changes, dict):
                raise ValueError("无效的设置内容。")
            allowed = {"language": ("zh", "en"), "theme": ("light", "dark"),
                       "motion": (True, False)}
            for key, value in changes.items():
                if key not in allowed or value not in allowed[key] or (key == "motion" and not isinstance(value, bool)):
                    raise ValueError("无效的设置内容。")
            updated = {**self._settings, **changes}
            self._settings_path.parent.mkdir(parents=True, exist_ok=True)
            with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8",
                     dir=self._settings_path.parent, prefix=".settings-", suffix=".tmp",
                     delete=False) as stream:
                temporary = Path(stream.name)
                json.dump(updated, stream, ensure_ascii=False, indent=2)
            try:
                os.replace(temporary, self._settings_path)
            finally:
                temporary.unlink(missing_ok=True)
            self._settings = updated
            if "theme" in changes and self._window is not None:
                color_webview_frame(self._window, updated["theme"])
            return updated.copy()
        return self._reply(action)

    def _reply(self, action):
        try:
            with self._lock:
                return {"ok": True, "data": action()}
        except (OSError, ValueError, RuntimeError) as exc:
            return {"ok": False, "error": str(exc)}

    def _state(self, include_thumbnails=False):
        items = self._library.items()
        if include_thumbnails:
            for item in items:
                if item.id not in self._thumbnails:
                    document = self._service.load_lut(item.path)
                    image = self._service.preview(self._thumbnail_photo, document)
                    self._thumbnails[item.id] = image_data(image, (800, 500), 91)
        return {"items": [{**item.public(), "thumbnail": self._thumbnails.get(item.id, "")}
                          for item in items],
                "selected": self._selected,
                "document": {"title": self._document.title,
                             "displayName": next((item.name for item in items if item.id == self._selected),
                                                 self._document.title.replace("_", " ")),
                             "source": self._document.source,
                             "target": self._document.target, "size": self._document.size,
                             "filename": next((item.original_name or item.path.name for item in items
                                               if item.id == self._selected), self._document.path.name)} if self._document else None,
                "photoName": self._photo_name, "original": self._original_data,
                "processed": self._after_data, "history": self._history,
                "settings": self._settings.copy(),
                "libraryPath": str(self._library.data_root)}

    def state(self):
        return self._reply(lambda: self._state(True))

    def select(self, item_id):
        def action():
            item = self._library.get(item_id)
            if item is None:
                raise ValueError("这份 LUT 已不在库中。")
            document = self._service.load_lut(item.path)
            processed = self._service.preview(self._photo, document)
            self._document = document
            self._selected = item_id
            self._after_data = image_data(processed)
            return self._state(True)
        return self._reply(action)

    def import_luts(self):
        def action():
            paths = self._window.create_file_dialog(webview.FileDialog.OPEN, allow_multiple=True,
                       file_types=("LUT files (*.cube;*.xmp)",))
            if not paths:
                return self._state()
            added = self._library.import_paths(paths)
            if added:
                item = self._library.get(added[-1])
                self._document = self._service.load_lut(item.path)
                self._selected = item.id
                self._after_data = image_data(self._service.preview(self._photo, self._document))
            return self._state(True)
        return self._reply(action)

    def choose_photo(self):
        def action():
            paths = self._window.create_file_dialog(webview.FileDialog.OPEN,
                       file_types=("Photos (*.jpg;*.jpeg;*.png;*.tif;*.tiff;*.bmp)",))
            if not paths:
                return self._state()
            photo = self._service.load_photo(paths[0])
            self._photo = photo
            self._thumbnail_photo = self._make_thumbnail_photo(photo)
            self._photo_name = Path(paths[0]).name
            self._original_data = image_data(photo)
            self._after_data = image_data(self._service.preview(photo, self._document))
            self._thumbnails.clear()
            return self._state(True)
        return self._reply(action)

    def export(self, size, group="Profiles", description=""):
        def action():
            if self._document is None:
                raise ValueError("请先选择一份 LUT。")
            suffix = "." + self._document.target.lower()
            proposed_name = re.sub(r'[<>:"/\\|?*\x00-\x1f]', "-", self._document.title).strip(" .") or "LUT"
            path = self._window.create_file_dialog(webview.FileDialog.SAVE,
                       save_filename=proposed_name + suffix,
                       file_types=(self._document.target + " files (*" + suffix + ")",))
            if not path:
                return {"cancelled": True}
            result = self._service.export(self._document, path[0], size, group, description)
            item = {"path": str(result.path), "filename": result.path.name,
                    "source": result.source, "target": result.target,
                    "size": result.size, "createdAt": result.created_at}
            self._history.insert(0, item)
            return item
        return self._reply(action)

    def remove(self, item_id):
        def action():
            if not self._library.remove(item_id):
                raise ValueError("仅能移除已导入的 LUT。")
            if self._selected == item_id:
                self._selected = None
                self._document = None
                self._after_data = self._original_data
            self._thumbnails.pop(item_id, None)
            return self._state()
        return self._reply(action)

    def open_folder(self, path):
        def action():
            folder = Path(path).resolve().parent
            if not folder.is_dir():
                raise ValueError("文件夹不存在。")
            open_local_folder(folder)
            return True
        return self._reply(action)

    def open_library_folder(self):
        return self._reply(lambda: open_local_folder(self._library.data_root) or True)

    def window_action(self, command):
        def action():
            if command == "minimize":
                self._window.minimize()
            elif command == "maximize":
                self._window.maximize()
            elif command == "restore":
                self._window.restore()
            elif command == "close":
                self._window.destroy()
            else:
                raise ValueError("Unknown window action")
            return True
        return self._reply(action)


def main():
    bridge = StudioBridge()
    window = webview.create_window("CUBE TO XMP", str(ROOT / "frontend" / "index.html"),
             js_api=bridge, width=1440, height=840, min_size=(960, 640),
             resizable=True, frameless=sys.platform != "win32", easy_drag=False,
             shadow=sys.platform == "win32",
             background_color="#f5f5f2", text_select=True)
    bridge._window = window
    if bridge._settings["motion"]:
        window.events.before_show += prepare_webview_open
    # WinForms applies its border style during Show(), so change it afterwards.
    window.events.shown += lambda window: reveal_webview_window(
        window, bridge._settings["motion"], bridge._settings["theme"])
    gui = "edgechromium" if sys.platform == "win32" else "qt" if sys.platform.startswith("linux") else None
    icon = str(ROOT / ("icon.ico" if sys.platform == "win32" else "icon.png"))
    webview.start(gui=gui, icon=icon)


if __name__ == "__main__":
    main()

"""Open the real native WebView on macOS/Linux and exercise its bridge."""
from pathlib import Path
import sys
import tempfile
import time

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import webview
from web_studio import ROOT, StudioBridge


with tempfile.TemporaryDirectory() as directory:
    bridge = StudioBridge(ROOT, Path(directory) / "library")
    window = webview.create_window("CUBE TO XMP smoke", str(ROOT / "frontend" / "index.html"),
                                   js_api=bridge, width=1200, height=800,
                                   resizable=True, frameless=True, easy_drag=False)
    bridge._window = window
    failures = []

    def check():
        try:
            deadline = time.monotonic() + 20
            while time.monotonic() < deadline:
                try:
                    if window.evaluate_js("document.body.classList.contains('app-ready')"):
                        break
                except Exception:
                    pass
                time.sleep(.4)
            else:
                raise AssertionError("The interface did not become ready")
            assert window.evaluate_js("document.querySelectorAll('#film-strip .film-card').length") == 6
            window.evaluate_js("document.querySelector('#film-strip .film-card').click()")
            deadline = time.monotonic() + 10
            while time.monotonic() < deadline:
                if window.evaluate_js("document.getElementById('target-format').textContent") == "XMP":
                    break
                time.sleep(.4)
            else:
                raise AssertionError("Selecting a LUT did not reach the Python bridge")
            window.evaluate_js("document.querySelector('[data-view=library]').click()")
            assert window.evaluate_js("document.querySelectorAll('#library-grid .library-tile').length") == 6
            print("PASS: native WebView, six LUTs, bridge selection, library")
        except BaseException as error:
            failures.append(error)
        finally:
            window.destroy()

    webview.start(check, gui="qt" if sys.platform.startswith("linux") else None,
                  icon=str(ROOT / "icon.png"))
    if failures:
        raise failures[0]

"""Windows WebView2 smoke: render real pages and exercise Python bridge."""
from pathlib import Path
import sys
import tempfile
import time
import ctypes

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import webview
from web_studio import ROOT, StudioBridge
from window_chrome import color_webview_frame, prepare_webview_open, reveal_webview_window


with tempfile.TemporaryDirectory() as temp:
    bridge = StudioBridge(ROOT, Path(temp) / "library")
    source = Path(temp) / "imported.xmp"
    built_in = bridge._service.load_lut(ROOT / "built_in_luts" / "Fuji_Astia_Soft.cube")
    bridge._service.export(built_in, source, 16)
    bridge._library.import_paths([source])
    window = webview.create_window("CUBE TO XMP smoke", str(ROOT / "frontend" / "index.html"),
                                   js_api=bridge, width=1200, height=800,
                                   resizable=True, frameless=False)
    bridge._window = window
    window.events.before_show += prepare_webview_open
    window.events.shown += reveal_webview_window
    failures = []

    def check():
        try:
            time.sleep(3)
            window.evaluate_js("window.__smoke_errors=[]; window.addEventListener('unhandledrejection', e=>window.__smoke_errors.push(String(e.reason)))")
            assert window.evaluate_js("document.body.classList.contains('app-ready')")
            style = ctypes.windll.user32.GetWindowLongW(window.native.Handle.ToInt64(), -16)
            assert style & 0x00040000 and not style & 0x00C00000
            assert color_webview_frame(window) == (0, 0)
            assert window.native.Opacity == 1.0
            assert window.evaluate_js("typeof document.getElementById('import-hero').onclick") == "function"
            assert window.evaluate_js("getComputedStyle(document.querySelector('.app-shell')).animationName") == "studio-enter"
            window.resize(1000, 700)
            time.sleep(.25)
            assert window.evaluate_js("getComputedStyle(document.querySelector('.sidebar .side-label')).display") == "none"
            assert window.evaluate_js("getComputedStyle(document.querySelector('.inspector .side-label')).display") != "none"
            window.resize(1200, 800)
            window.evaluate_js("document.getElementById('settings-toggle').click()")
            assert window.evaluate_js("!document.getElementById('settings-panel').hidden")
            window.evaluate_js("document.querySelector('[data-setting=language] [data-value=en]').click()")
            time.sleep(.35)
            assert window.evaluate_js("document.documentElement.lang") == "en"
            assert window.evaluate_js("document.querySelector('[data-i18n=studioTitle]').textContent") == "See color in context."
            window.evaluate_js("document.querySelector('[data-setting=theme] [data-value=dark]').click()")
            time.sleep(.35)
            assert window.evaluate_js("document.documentElement.dataset.theme") == "dark"
            assert color_webview_frame(window, "dark") == (0, 0)
            window.evaluate_js("document.querySelector('[data-setting=motion] [data-value=false]').click()")
            time.sleep(.35)
            assert window.evaluate_js("document.documentElement.dataset.motion") == "off"
            assert window.evaluate_js("getComputedStyle(document.querySelector('.app-shell')).animationName") == "none"
            assert bridge._settings == {"language": "en", "theme": "dark", "motion": False}
            window.evaluate_js("document.querySelector('[data-setting=language] [data-value=zh]').click()")
            time.sleep(.35)
            window.evaluate_js("document.querySelector('[data-setting=theme] [data-value=light]').click()")
            time.sleep(.35)
            window.evaluate_js("document.querySelector('[data-setting=motion] [data-value=true]').click()")
            time.sleep(.35)
            assert window.evaluate_js("document.documentElement.lang") == "zh-CN"
            window.evaluate_js("document.getElementById('settings-close').click()")
            assert window.evaluate_js("document.getElementById('settings-panel').hidden")
            window.evaluate_js("document.querySelector('[data-view=library]').click()")
            time.sleep(.3)
            assert window.evaluate_js("document.querySelectorAll('#library-grid .library-tile').length") == 7
            assert window.evaluate_js("document.querySelector('#library-grid .tile-art').naturalWidth") >= 700
            assert window.evaluate_js("getComputedStyle(document.querySelector('#library-grid .tile-preview')).aspectRatio") == "3 / 2"
            window.evaluate_js("document.querySelector('[data-filter=imported]').click()")
            assert window.evaluate_js("document.querySelectorAll('#library-grid .library-tile').length") == 1
            window.evaluate_js("document.querySelector('#library-grid .tile-preview').click()")
            time.sleep(.7)
            assert window.evaluate_js("document.getElementById('target-format').textContent") == "CUBE"
            window.evaluate_js("document.querySelector('[data-view=library]').click()")
            window.evaluate_js("document.querySelector('#library-grid [data-remove]').click()")
            time.sleep(.3)
            assert window.evaluate_js("document.getElementById('library-count').textContent") == "06"
            assert window.evaluate_js("document.getElementById('target-format').textContent") == "—"
            window.evaluate_js("document.querySelector('[data-view=history]').click()")
            assert window.evaluate_js("document.querySelector('#history-list .empty-state') !== null")
            assert window.evaluate_js("window.__smoke_errors") == []
            print("PASS: animated opening, native resize frame, narrow layout, settings, library, selection, history")
        except BaseException as error:
            failures.append(error)
        finally:
            window.destroy()

    webview.start(check, gui="edgechromium")
    if failures:
        raise failures[0]

"""Integrated Windows headers for the legacy Tk and current WebView shells.

Only the caption style is removed. Windows retains its resize border, taskbar,
minimize, maximize, snapping, and system menu without a WNDPROC hook.
"""
import ctypes
from ctypes import wintypes
import sys
import time


class WindowChrome:
    def __init__(self, app):
        self.app = app
        self.handle = None
        if sys.platform != "win32":
            return
        self.api = ctypes.WinDLL("user32", use_last_error=True)
        self.api.GetParent.argtypes = [wintypes.HWND]
        self.api.GetParent.restype = wintypes.HWND
        self.api.GetWindowLongW.argtypes = [wintypes.HWND, ctypes.c_int]
        self.api.GetWindowLongW.restype = ctypes.c_long
        self.api.SetWindowLongW.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_long]
        self.api.SetWindowLongW.restype = ctypes.c_long
        self.api.SetWindowPos.argtypes = [wintypes.HWND, wintypes.HWND, ctypes.c_int,
                                         ctypes.c_int, ctypes.c_int, ctypes.c_int, wintypes.UINT]
        self.api.ShowWindow.argtypes = [wintypes.HWND, ctypes.c_int]
        self.api.IsZoomed.argtypes = [wintypes.HWND]
        self.api.IsZoomed.restype = wintypes.BOOL
        self.api.PostMessageW.argtypes = [wintypes.HWND, wintypes.UINT,
                                         ctypes.c_size_t, ctypes.c_ssize_t]
        self.api.PostMessageW.restype = wintypes.BOOL

    def install(self):
        if sys.platform != "win32":
            return
        self.handle = self.api.GetParent(self.app.winfo_id())
        style = self.api.GetWindowLongW(self.handle, -16)
        # WS_CAPTION only: retain WS_THICKFRAME / WS_SYSMENU / minimize / maximize.
        self.api.SetWindowLongW(self.handle, -16, style & ~0x00C00000)
        self.api.SetWindowPos(self.handle, None, 0, 0, 0, 0,
                              0x0001 | 0x0002 | 0x0004 | 0x0020 | 0x0010)
        self.update_border()

    def update_border(self):
        if not self.handle:
            return
        rgb = self.app.colors["panel"].lstrip("#")
        value = ctypes.c_uint(int(rgb[0:2], 16) | int(rgb[2:4], 16) << 8 | int(rgb[4:6], 16) << 16)
        # Windows 11 border color; older Windows simply ignore this attribute.
        ctypes.windll.dwmapi.DwmSetWindowAttribute(wintypes.HWND(self.handle), 34,
                                                  ctypes.byref(value), ctypes.sizeof(value))

    def bind_drag(self, widget, recursive=False):
        widget.bind("<Button-1>", self.drag, add="+")
        widget.bind("<Double-Button-1>", lambda event: self.toggle_maximize(), add="+")
        if recursive:
            for child in widget.winfo_children():
                self.bind_drag(child, recursive=True)

    def drag(self, event):
        if not self.handle:
            return
        self.api.ReleaseCapture()
        # Delegate moving and drag-to-restore to the native caption action.
        point = (event.x_root & 0xFFFF) | ((event.y_root & 0xFFFF) << 16)
        # Return from the Python/Tcl callback before entering the Windows move
        # loop. A synchronous SendMessage here reenters Tk with a released GIL.
        self.api.PostMessageW(self.handle, 0x00A1, 2, point)  # WM_NCLBUTTONDOWN, HTCAPTION

    def minimize(self):
        if self.handle:
            self.api.ShowWindow(self.handle, 6)

    def toggle_maximize(self):
        if self.handle:
            self.api.ShowWindow(self.handle, 9 if self.api.IsZoomed(self.handle) else 3)

    def maximized(self):
        return bool(self.handle and self.api.IsZoomed(self.handle))


def install_webview_resize_frame(window):
    """Keep the native sizing border while the HTML draws the title bar.

    pywebview's Windows `frameless=True` changes FormBorderStyle to None, which
    removes the Windows hit targets for edge/corner resizing. This hook runs in
    `before_show`, after the WinForms handle exists and before it is visible.
    """
    if sys.platform != "win32":
        return
    user32 = ctypes.WinDLL("user32", use_last_error=True)
    hwnd = wintypes.HWND(window.native.Handle.ToInt64())
    user32.GetWindowLongW.argtypes = [wintypes.HWND, ctypes.c_int]
    user32.GetWindowLongW.restype = ctypes.c_long
    user32.SetWindowLongW.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_long]
    user32.SetWindowLongW.restype = ctypes.c_long
    user32.SetWindowPos.argtypes = [wintypes.HWND, wintypes.HWND, ctypes.c_int,
                                     ctypes.c_int, ctypes.c_int, ctypes.c_int, wintypes.UINT]
    style = user32.GetWindowLongW(hwnd, -16)
    # Preserve WS_THICKFRAME, system menu, and minimize/maximize styles.
    style = (style | 0x00040000) & ~0x00C00000
    user32.SetWindowLongW(hwnd, -16, style)
    user32.SetWindowPos(hwnd, None, 0, 0, 0, 0,
                        0x0001 | 0x0002 | 0x0004 | 0x0020)


def color_webview_frame(window, theme="light"):
    """Blend the retained Windows resize frame into the HTML title bar."""
    if sys.platform != "win32":
        return
    hwnd = wintypes.HWND(window.native.Handle.ToInt64())
    dwm = ctypes.WinDLL("dwmapi", use_last_error=True)
    dwm.DwmSetWindowAttribute.argtypes = [wintypes.HWND, wintypes.DWORD,
                                         ctypes.c_void_p, wintypes.DWORD]
    dwm.DwmSetWindowAttribute.restype = ctypes.c_long
    # Windows 11: suppress the one-pixel outline, and color the residual
    # non-client strip to match the custom title bar. Older Windows ignore it.
    border = ctypes.c_uint32(0xFFFFFFFE)
    caption = ctypes.c_uint32(0x00222224 if theme == "dark" else 0x00F6F8F8)
    border_result = dwm.DwmSetWindowAttribute(hwnd, 34, ctypes.byref(border), ctypes.sizeof(border))
    caption_result = dwm.DwmSetWindowAttribute(hwnd, 35, ctypes.byref(caption), ctypes.sizeof(caption))
    return border_result, caption_result


def prepare_webview_open(window):
    """Keep the native caption hidden until its replacement is installed."""
    if sys.platform == "win32":
        window.native.Opacity = 0.01


def reveal_webview_window(window, motion=True, theme="light"):
    install_webview_resize_frame(window)
    color_webview_frame(window, theme)
    if sys.platform != "win32" or not motion:
        return
    try:
        for step in range(1, 11):
            window.native.Opacity = step / 10
            time.sleep(.018)
    finally:
        window.native.Opacity = 1.0

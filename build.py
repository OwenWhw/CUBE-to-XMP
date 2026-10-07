"""Build the native desktop shell for the host operating system."""
from pathlib import Path
import os
import subprocess
import sys

ROOT = Path(__file__).resolve().parent
NAME = "CUBE-TO-XMP"

def build_executable():
    command = [sys.executable, "-m", "PyInstaller", "--noconfirm", "--onedir", "--windowed",
               "--name", NAME, "--distpath", str(ROOT / "dist"),
               "--workpath", str(ROOT / "build" / "web-studio"),
               "--specpath", str(ROOT / "build"),
               "--collect-all", "webview"]
    if sys.platform in ("win32", "darwin"):
        command.extend(["--icon", str(ROOT / ("icon.ico" if sys.platform == "win32" else "icon.png"))])
    for source, destination in [("built_in_luts", "built_in_luts"), ("assets", "assets"),
                                ("frontend", "frontend"), ("fonts", "fonts"),
                                ("icon.ico", "."), ("icon.png", ".")]:
        command.extend(["--add-data", str(ROOT / source) + os.pathsep + destination])
    command.append(str(ROOT / "cube_to_xmp.py"))
    subprocess.run(command, cwd=ROOT, check=True)
    executable = (ROOT / "dist" / (NAME + ".app") / "Contents" / "MacOS" / NAME
                  if sys.platform == "darwin" else
                  ROOT / "dist" / NAME / (NAME + (".exe" if sys.platform == "win32" else "")))
    if not executable.exists():
        raise RuntimeError("Build completed without an executable")
    print("Built:", executable)
    return executable

if __name__ == "__main__":
    build_executable()

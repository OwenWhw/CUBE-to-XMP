# CUBE TO XMP

**See the look on a photograph. Carry it into your next edit.**

CUBE TO XMP is a local LUT workspace for photographers and color enthusiasts. Keep `.cube` files and `.xmp` files containing Adobe RGBTable data together, judge each look on an actual photograph, and convert it for the next application in your workflow. Importing, previewing, and converting happen on your computer.

[Download the latest release](https://github.com/OwenWhw/CUBE-to-XMP/releases/latest) · [Platforms and previous versions](docs/DOWNLOADS.md) · [简体中文](README.md)

![CUBE TO XMP studio with an original-versus-LUT photo comparison](docs/images/studio.png)

The photograph stays at the center of the studio. The right panel keeps the selected LUT and export settings within reach. Replace the sample photo to judge a look on your own work.

## What you can do

| Task | In the app |
| --- | --- |
| Preview a look | Choose one of six built-in film-inspired looks or import your LUT. Drag the divider to compare the original and processed photo. |
| Keep a library | Import multiple CUBE/XMP files, search and filter them, and remove imported items when no longer needed. The app keeps a local copy. |
| Convert | Export CUBE → XMP or XMP → CUBE with a selected output grid size. |
| Find your export | The session history shows files actually saved and opens their folders. |

The interface supports Chinese and English, light and dark themes, and optional motion.

![LUT library with large photo previews of different looks](docs/images/library.png)

## Download and run

Choose your system on the [v2.2.0 release page](https://github.com/OwenWhw/CUBE-to-XMP/releases/tag/v2.2.0). Package names follow `CUBE-TO-XMP-vMAJOR.MINOR.PATCH-platform-architecture.zip`.

| System | Download | Run after extracting |
| --- | --- | --- |
| Windows x64 | `CUBE-TO-XMP-v2.2.0-windows-x64.zip` | `CUBE-TO-XMP.exe`; keep `_internal` beside it. Requires Edge WebView2 Runtime. |
| macOS Apple silicon | `CUBE-TO-XMP-v2.2.0-macos-arm64.zip` | `CUBE-TO-XMP.app`. |
| macOS Intel | `CUBE-TO-XMP-v2.2.0-macos-x64.zip` | `CUBE-TO-XMP.app`. |
| Linux x64 | `CUBE-TO-XMP-v2.2.0-linux-x64.zip` | Run `CUBE-TO-XMP/CUBE-TO-XMP` after extracting. Built for an Ubuntu 24.04 desktop environment. |

Keep the entire extracted folder. The macOS builds are not code-signed or notarized, so macOS may ask you to confirm the source. See [downloads and older releases](docs/DOWNLOADS.md). The release includes `SHA256SUMS.txt` for verification. Python is not required to run the packaged app, and it does not upload your photos or LUTs.

## Convert a LUT

1. In the studio, select a built-in look or choose **Import LUT**. The right panel shows the input and output formats.
2. Drag the photo divider to compare the result. Use **Change preview photo** to load your own JPG, PNG, TIFF, or BMP; exporting a LUT never modifies that photo.
3. Choose an output grid, select **Export XMP** or **Export CUBE**, and save using the system file dialog. Your saved file appears in the session history.

Shortcuts: `Ctrl+O` imports LUTs, `Ctrl+P` changes the photo, and `Ctrl+S` exports. With the comparison focused, use the arrow keys, `Home`, or `End` to move the divider.

Imported files are copied into a local library, so deleting the original does not remove the library copy. The library lives at `%LOCALAPPDATA%\CUBE TO XMP\Library` on Windows, `~/Library/Application Support/CUBE TO XMP/Library` on macOS, and `~/.local/share/CUBE TO XMP/Library` on Linux (or under `XDG_DATA_HOME`).

## Supported formats and limits

- CUBE input: normalized 3D LUTs with grid sizes 2–65³ and a 0–1 input domain. 1D LUTs are not supported.
- XMP input: files with Adobe RGBTable data. An ordinary Lightroom or Camera Raw slider preset is not a convertible LUT.
- Output grids: 16, 17, 25, 32, 33, 64, or 65. XMP output is capped at 32³ and larger selections are resampled to 32³.
- The RGB photo preview is a visual guide. Color management in the target application may differ. Compatibility in a live Adobe Camera Raw or Lightroom installation has not yet been verified.

The six built-in looks are film-inspired presets; they are not official Fujifilm film simulations.

## Run from source

Use Python 3.12 and the WebView backend for your system: Edge WebView2 on Windows, system WebKit on macOS, or Qt WebEngine on Linux. Windows example:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe cube_to_xmp.py
```

Run the automated tests:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -p 'test_*.py' -q
.\.venv\Scripts\python.exe tests\smoke_web_ui.py
```

To build a portable app, install `pyinstaller` and run `.\.venv\Scripts\python.exe build.py`. Linux also needs `pywebview[qt]` and `PyQt6-WebEngine`. The UI lives in `frontend/`, the desktop bridge in `web_studio.py`, the conversion service and codec in `conversion_service.py` and `lut_core.py`, and the persistent library in `lut_library.py`.

[MIT License](LICENSE) · [v2.2.0 release notes](docs/RELEASE_v2.2.0.md)

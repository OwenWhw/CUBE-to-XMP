# CUBE TO XMP

See the color on a photograph before moving your LUT to the next workflow.

CUBE TO XMP is a local Windows workspace for photography LUTs. Import a `.cube` file or an `.xmp` file containing Adobe RGBTable data, compare its effect on a photo, convert it to the other format, and keep frequently used looks in your own library. Photos and LUTs stay on your device.

[Download for Windows](https://github.com/OwenWhw/CUBE-to-XMP/releases/latest) · [简体中文](README.md) · [Format details](docs/CONVERSION.md)

## What you can do

| Task | In the app |
| --- | --- |
| Preview a look | Choose one of six built-in film-inspired looks or import your LUT. Drag the divider to compare the original and processed photo. |
| Keep a library | Import multiple CUBE/XMP files, search and filter them, and remove imported items when no longer needed. The app keeps a local copy. |
| Convert | Export CUBE → XMP or XMP → CUBE with a selected output grid size. |
| Find your export | The session history shows files actually saved and opens their folders. |

The interface supports Chinese and English, light and dark themes, and optional motion.

## Install

1. Open the [latest release](https://github.com/OwenWhw/CUBE-to-XMP/releases/latest) and download `CUBE-TO-XMP-v2.1.0-windows-x64.zip`.
2. Extract the **entire** folder and run `CUBE-TO-XMP.exe`. Keep the adjacent `_internal` folder with the executable.
3. Microsoft Edge WebView2 Runtime is required. If it is missing, install it before launching the app.

This is a portable Windows x64 build; Python is not required to run it. The app does not upload photos or LUTs.

## Convert a LUT

1. In the studio, select a built-in look or choose **Import LUT**. The right panel shows the input and output formats.
2. Drag the photo divider to compare the result. Use **Change preview photo** to load your own JPG, PNG, TIFF, or BMP; exporting a LUT never modifies that photo.
3. Choose an output grid, select **Export XMP** or **Export CUBE**, and save using the Windows file dialog. Your saved file appears in the session history.

Shortcuts: `Ctrl+O` imports LUTs, `Ctrl+P` changes the photo, and `Ctrl+S` exports. With the comparison focused, use the arrow keys, `Home`, or `End` to move the divider.

Imported files are copied to `%LOCALAPPDATA%\CUBE TO XMP\Library`, so deleting the original does not remove the library copy.

## Supported formats and limits

- CUBE input: normalized 3D LUTs with grid sizes 2–65³ and a 0–1 input domain. 1D LUTs are not supported.
- XMP input: files with Adobe RGBTable data. An ordinary Lightroom or Camera Raw slider preset is not a convertible LUT.
- Output grids: 16, 17, 25, 32, 33, 64, or 65. XMP output is capped at 32³ and larger selections are resampled to 32³.
- The RGB photo preview is a visual guide. Color management in the target application may differ. Compatibility in a live Adobe Camera Raw or Lightroom installation has not yet been verified.

The six built-in looks are film-inspired presets; they are not official Fujifilm film simulations.

## Run from source

On Windows with Python 3.12 and Edge WebView2 Runtime:

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

To build a portable executable, install `pyinstaller` and run `.\.venv\Scripts\python.exe build.py`. The UI lives in `frontend/`, the desktop bridge in `web_studio.py`, the conversion service and codec in `conversion_service.py` and `lut_core.py`, and the persistent library in `lut_library.py`.

[MIT License](LICENSE) · [v2.1.0 release notes](docs/RELEASE_v2.1.0.md)

@echo off
cd /d "%~dp0"
if exist ".venv\Scripts\pythonw.exe" (
    start "" ".venv\Scripts\pythonw.exe" "cube_to_xmp.py"
    exit /b 0
)
if exist "dist\CUBE-TO-XMP\CUBE-TO-XMP.exe" (
    start "" "dist\CUBE-TO-XMP\CUBE-TO-XMP.exe"
    exit /b 0
)
python cube_to_xmp.py
if errorlevel 1 pause

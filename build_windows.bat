@echo off
cd /d "%~dp0"
if exist ".venv\Scripts\python.exe" (
    ".venv\Scripts\python.exe" build.py
) else (
    python build.py
)
if errorlevel 1 pause

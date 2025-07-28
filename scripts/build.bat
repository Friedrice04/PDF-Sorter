@echo off
REM Build script for OCR File Sorter
REM This script builds only the main executable (no installer)

echo ========================================
echo Building OCR File Sorter Executable
echo ========================================
echo.

REM Check if virtual environment exists
if not exist "..\\.venv\\Scripts\\activate.bat" (
    echo Error: Virtual environment not found!
    echo Please create a virtual environment first with: python -m venv .venv
    echo Then install build dependencies with: pip install -r config/requirements-build.txt
    pause
    exit /b 1
)

REM Activate virtual environment
echo Activating virtual environment...
call "..\\.venv\\Scripts\\activate.bat"

REM Check if PyInstaller is installed
python -c "import PyInstaller" 2>nul
if errorlevel 1 (
    echo PyInstaller not found. Installing build dependencies...
    pip install -r "../config/requirements-build.txt"
    if errorlevel 1 (
        echo Failed to install build dependencies!
        pause
        exit /b 1
    )
)

REM Clean previous build files
echo Cleaning previous build files...
if exist "..\\build" rmdir /s /q "..\\build"
if exist "..\\dist" rmdir /s /q "..\\dist"

REM Create directories
mkdir "..\\dist" 2>nul
mkdir "..\\build" 2>nul

REM Run the build script
echo.
echo Starting build process...
python build_exe.py

REM Check if build was successful
if exist "..\\dist\\OCR File Sorter.exe" (
    echo.
    echo ========================================
    echo BUILD SUCCESSFUL!
    echo ========================================
    echo Executable created: dist\\OCR File Sorter.exe
    echo.
    echo You can now distribute the exe file along with any required
    echo system dependencies (like Tesseract OCR if using OCR features^).
    echo.
    echo For a complete installer that includes Tesseract OCR, run:
    echo     build_complete.bat
    echo.
) else (
    echo.
    echo ========================================
    echo BUILD FAILED!
    echo ========================================
    echo Check the output above for error messages.
    echo.
)

echo Press any key to exit...
pause >nul

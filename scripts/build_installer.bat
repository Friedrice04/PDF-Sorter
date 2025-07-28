@echo off
REM Build script for OCR File Sorter - Installer Only
REM This script creates only the download-based installer executable

echo ========================================
echo Building OCR File Sorter Installer
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
"..\\.venv\\Scripts\\python.exe" -c "import PyInstaller" 2>nul
if errorlevel 1 (
    echo PyInstaller not found. Installing build dependencies...
    "..\\.venv\\Scripts\\pip.exe" install -r "../config/requirements-build.txt"
    if errorlevel 1 (
        echo Failed to install build dependencies!
        pause
        exit /b 1
    )
)

REM Clean previous installer build files
echo Cleaning previous installer files...
if exist "..\\build\\download_installer" rmdir /s /q "..\\build\\download_installer"
if exist "..\\dist\\OCR_File_Sorter_Download_Installer.exe" del "..\\dist\\OCR_File_Sorter_Download_Installer.exe"

REM Create directories
mkdir "..\\dist" 2>nul
mkdir "..\\build" 2>nul

echo.
echo Building download-based installer...
"..\\.venv\\Scripts\\python.exe" build_installer_exe.py

REM Check if installer was created
if exist "..\\dist\\OCR_File_Sorter_Download_Installer.exe" (
    echo.
    echo ========================================
    echo INSTALLER BUILD SUCCESSFUL!
    echo ========================================
    echo.
    echo 📦 Installer created: dist\\OCR_File_Sorter_Download_Installer.exe
    echo.
    echo 🌐 This download-based installer:
    echo    - Downloads the app from GitHub during installation
    echo    - Much smaller file size ^(approx 11 MB^)
    echo    - Includes Tesseract OCR installation
    echo    - Creates desktop shortcuts and Start Menu entries
    echo    - No administrator privileges required
    echo.
) else (
    echo.
    echo ========================================
    echo INSTALLER BUILD FAILED!
    echo ========================================
    echo Check the output above for error messages.
    echo.
)

echo Press any key to exit...
pause >nul

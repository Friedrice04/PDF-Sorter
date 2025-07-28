@echo off
REM Complete build script for OCR File Sorter
REM This script builds both the main application and the installer

echo ========================================
echo OCR File Sorter - Complete Build
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

echo Step 1: Building main application...
echo ========================================
call build.bat
if errorlevel 1 (
    echo.
    echo ❌ Application build failed!
    pause
    exit /b 1
)

echo.
echo.
echo Step 2: Building installer...
echo ========================================
call build_installer.bat
if errorlevel 1 (
    echo.
    echo ❌ Installer build failed!
    pause
    exit /b 1
)

echo.
echo.
echo ========================================
echo COMPLETE BUILD SUCCESSFUL!
echo ========================================
echo.
echo ✅ Application folder: dist\\OCR File Sorter\\
echo ✅ Application zip: dist\\OCR_File_Sorter.zip
echo ✅ Download installer: dist\\OCR_File_Sorter_Download_Installer.exe
echo.
echo 📋 DEPLOYMENT READY:
echo    1. Upload OCR_File_Sorter.zip to GitHub releases
echo    2. Distribute OCR_File_Sorter_Download_Installer.exe to users
echo    3. Users download small installer ^(~11MB^) which downloads app during install
echo.

echo Press any key to exit...
pause >nul

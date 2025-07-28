@echo off
REM Installer-only build script for OCR File Sorter
REM This script creates only the installer (requires main exe to exist)

echo ========================================
echo OCR File Sorter - Installer Build
echo ========================================
echo.

REM Check if main application exists
if not exist "..\\dist\\OCR File Sorter.exe" (
    echo Error: Main application not found!
    echo Please build the main application first with: build.bat
    echo Or run the complete build with: build_complete.bat
    pause
    exit /b 1
)

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

echo.
echo ========================================
echo Creating Single-File Installer
echo ========================================
echo.

REM Create the single-file installer
python installer.py --build

REM Check if installer was created
if exist "..\\dist\\OCR_File_Sorter_Installer.exe" (
    echo.
    echo ========================================
    echo INSTALLER BUILD SUCCESSFUL!
    echo ========================================
    echo.
    echo 📦 Installer created: dist\\OCR_File_Sorter_Installer.exe
    echo.
    echo 🚀 This installer includes:
    echo    - OCR File Sorter application
    echo    - User-specific Tesseract OCR installation
    echo    - Desktop shortcuts and Start Menu entries
    echo    - User PATH configuration
    echo    - No administrator privileges required
    echo.
    
    REM Show file size
    for %%f in ("..\\dist\\OCR_File_Sorter_Installer.exe") do echo    Installer size: %%~zf bytes
    
) else (
    echo.
    echo ========================================
    echo INSTALLER BUILD FAILED!
    echo ========================================
    echo Check the output above for error messages.
    echo.
)

echo.
echo Press any key to exit...
pause >nul

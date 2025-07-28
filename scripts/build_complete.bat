@echo off
REM Complete build script for OCR File Sorter with single-file installer
REM This script creates both the main application and a complete installer

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

echo.
echo ========================================
echo Step 1: Building Main Application
echo ========================================
echo.

REM Build the main application
python build_exe.py

REM Check if build was successful
if not exist "..\\dist\\OCR File Sorter.exe" (
    echo.
    echo ========================================
    echo MAIN APPLICATION BUILD FAILED!
    echo ========================================
    echo Check the output above for error messages.
    pause
    exit /b 1
)

echo.
echo ========================================
echo Step 2: Creating Single-File Installer
echo ========================================
echo.

REM Create the single-file installer
python installer.py --build

REM Check if installer was created
if exist "..\\dist\\OCR_File_Sorter_Installer.exe" (
    echo.
    echo ========================================
    echo BUILD SUCCESSFUL!
    echo ========================================
    echo.
    echo 📦 Distribution files created:
    echo    • dist\\OCR File Sorter.exe              - Main application
    echo    • dist\\OCR_File_Sorter_Installer.py     - Python installer script  
    echo    • dist\\OCR_File_Sorter_Installer.exe    - Complete self-contained installer
    echo.
    echo 🚀 For distribution, use: OCR_File_Sorter_Installer.exe
    echo    This installer includes:
    echo    - OCR File Sorter application
    echo    - User-specific Tesseract OCR installation
    echo    - Desktop shortcuts and Start Menu entries
    echo    - User PATH configuration
    echo    - No administrator privileges required
    echo.
    
    REM Show file sizes
    for %%f in ("..\\dist\\OCR File Sorter.exe") do echo    Main app size: %%~zf bytes
    for %%f in ("..\\dist\\OCR_File_Sorter_Installer.exe") do echo    Installer size: %%~zf bytes
    
) else (
    echo.
    echo ========================================
    echo INSTALLER BUILD FAILED!
    echo ========================================
    echo The main application was built successfully, but the installer creation failed.
    echo Check the output above for error messages.
    echo.
)

echo.
echo Press any key to exit...
pause >nul

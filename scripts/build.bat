@echo off
REM Build script for OCR File Sorter - Main Application
REM This script builds the main application in directory mode and creates a zip

echo ========================================
echo Building OCR File Sorter Application
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

REM Clean previous build files
echo Cleaning previous build files...
if exist "..\\build\\OCR File Sorter" rmdir /s /q "..\\build\\OCR File Sorter"
if exist "..\\dist\\OCR File Sorter" rmdir /s /q "..\\dist\\OCR File Sorter"
if exist "..\\dist\\OCR_File_Sorter.zip" del "..\\dist\\OCR_File_Sorter.zip"

REM Create directories
mkdir "..\\dist" 2>nul
mkdir "..\\build" 2>nul

REM Run the build script
echo.
echo Building application...
"..\\.venv\\Scripts\\python.exe" build_exe.py

REM Check if build was successful
if exist "..\\dist\\OCR File Sorter\\OCR File Sorter.exe" (
    echo.
    echo Application build successful!
    echo.
    echo Creating application zip...
    powershell -Command "cd '..\\dist'; Compress-Archive -Path 'OCR File Sorter\\*' -DestinationPath 'OCR_File_Sorter.zip' -Force"
    
    if exist "..\\dist\\OCR_File_Sorter.zip" (
        echo.
        echo ========================================
        echo BUILD SUCCESSFUL!
        echo ========================================
        echo Application folder: dist\\OCR File Sorter\\
        echo Application zip: dist\\OCR_File_Sorter.zip
        echo.
        echo The zip file is ready for distribution or upload to GitHub releases.
        echo.
    ) else (
        echo.
        echo Warning: Application built but zip creation failed!
        echo Application folder: dist\\OCR File Sorter\\
        echo.
    )
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

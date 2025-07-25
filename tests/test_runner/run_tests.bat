@echo off
REM Quick PDF Test Runner
REM Run this script to quickly test PDF sorting

cd /d "%~dp0"

echo ========================================
echo PDF Sorting Test Runner
echo ========================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python not found! Please install Python or add it to PATH.
    pause
    exit /b 1
)

REM Check for input files
if not exist "input_pdfs\*.pdf" (
    echo Warning: No PDF files found in input_pdfs folder!
    echo Please add some PDF files to test.
    echo.
)

REM Check for mapping files  
if not exist "test_mappings\*.json" (
    echo Warning: No mapping files found in test_mappings folder!
    echo Please add some JSON mapping files to test.
    echo.
)

echo Running PDF tests...
echo.

REM Use the virtual environment Python
if exist "..\..\\.venv\\Scripts\\python.exe" (
    "..\..\\.venv\\Scripts\\python.exe" run_pdf_tests.py --verbose --save-results
) else (
    echo No virtual environment found. Using system Python...
    python run_pdf_tests.py --verbose --save-results
)

echo.
echo ========================================
echo Test completed! Check the output above.
echo Results saved to the 'results' folder.
echo ========================================
echo.
pause

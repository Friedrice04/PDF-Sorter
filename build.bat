@echo off
REM Simple build script that delegates to the scripts folder
REM This provides a convenient way to build from the project root

echo ========================================
echo OCR File Sorter - Quick Build
echo ========================================
echo.
echo Delegating to scripts\build_complete.bat...
echo.

REM Change to scripts directory and run the complete build
cd scripts
call build_complete.bat

REM Return to original directory
cd ..
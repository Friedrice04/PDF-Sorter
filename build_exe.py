"""
Build script for OCR File Sorter executable using PyInstaller.
This script creates a standalone executable with all necessary dependencies.
"""

import PyInstaller.__main__
import os
import sys
from pathlib import Path

def build_executable():
    """Build the executable using PyInstaller with all necessary options."""
    
    # Get the current directory
    current_dir = Path.cwd()
    
    # Define paths
    main_script = current_dir / "src" / "main.py"
    icon_path = current_dir / "src" / "icons" / "sorterIcon.ico"
    
    # Ensure the main script exists
    if not main_script.exists():
        print(f"Error: Main script not found at {main_script}")
        sys.exit(1)
    
    # Ensure the icon exists
    if not icon_path.exists():
        print(f"Warning: Icon file not found at {icon_path}")
        icon_arg = []
    else:
        icon_arg = ['--icon', str(icon_path)]
    
    print("Building OCR File Sorter executable...")
    print(f"Main script: {main_script}")
    print(f"Output directory: {current_dir / 'dist'}")
    
    # PyInstaller arguments
    args = [
        '--name=OCR File Sorter',
        '--onefile',
        '--noconsole',
        '--distpath=./dist',
        '--workpath=./build',
        '--specpath=./build',
        # Add data files - use absolute paths
        f'--add-data={current_dir}/src/icons/*;src/icons',
        f'--add-data={current_dir}/src/mappings/example.json;src/mappings',
        f'--add-data={current_dir}/src/mappings/example_template;src/mappings/example_template',
        # Add hidden imports that might be needed
        '--hidden-import=tkinter',
        '--hidden-import=tkinterdnd2',
        '--hidden-import=PIL',
        '--hidden-import=fitz',
        '--hidden-import=pytesseract',
        # Clean build
        '--clean',
    ]
    
    # Add icon if it exists
    args.extend(icon_arg)
    
    # Add the main script
    args.append(str(main_script))
    
    try:
        PyInstaller.__main__.run(args)
        print("\n" + "="*50)
        print("Build completed successfully!")
        print(f"Executable location: {current_dir / 'dist' / 'OCR File Sorter.exe'}")
        print("="*50)
    except Exception as e:
        print(f"Build failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    build_executable()

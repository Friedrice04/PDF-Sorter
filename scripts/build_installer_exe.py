"""
Build script for the download-based installer using PyInstaller.
"""

import PyInstaller.__main__
from pathlib import Path
import sys

def build_installer():
    """Build the download-based installer executable."""
    
    # Get the project root directory (parent of scripts)
    current_dir = Path.cwd().parent
    
    # Define paths
    installer_script = current_dir / "scripts" / "download_installer.py"
    icon_path = current_dir / "src" / "icons" / "sorterIcon.ico"
    
    # Ensure the installer script exists
    if not installer_script.exists():
        print(f"Error: Installer script not found at {installer_script}")
        sys.exit(1)
    
    print("Building download-based installer...")
    print(f"Installer script: {installer_script}")
    print(f"Output directory: {current_dir / 'dist'}")
    
    # PyInstaller arguments
    args = [
        '--name=OCR_File_Sorter_Download_Installer',
        '--onefile',
        '--noconsole',
        '--distpath=../dist',
        '--workpath=../build/download_installer',
        '--specpath=../build/download_installer',
        '--hidden-import=tkinter',
        '--hidden-import=urllib.request',
        '--hidden-import=winreg',
        '--clean'
    ]
    
    # Add icon if it exists
    if icon_path.exists():
        args.extend(['--icon', str(icon_path)])
    else:
        print(f"Warning: Icon file not found at {icon_path}")
    
    # Add the installer script
    args.append(str(installer_script))
    
    try:
        PyInstaller.__main__.run(args)
        print("\n" + "="*50)
        print("Installer build completed successfully!")
        print(f"Installer location: {current_dir / 'dist' / 'OCR_File_Sorter_Download_Installer.exe'}")
        print("="*50)
    except Exception as e:
        print(f"Installer build failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    build_installer()

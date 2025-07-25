"""
Builder script for creating a single-file installer.
This script packages the OCR File Sorter executable and installer into one file.
"""

import os
import sys
import base64
import zipfile
import tempfile
from pathlib import Path

def create_single_file_installer():
    """Create a single-file installer with embedded application."""
    
    # Get the project root directory (parent of scripts)
    current_dir = Path.cwd().parent
    dist_dir = current_dir / "dist"
    
    # Check if the main executable exists
    main_exe = dist_dir / "OCR File Sorter.exe"
    if not main_exe.exists():
        print("Error: OCR File Sorter.exe not found in dist directory.")
        print("Please run 'build.bat' first to create the executable.")
        return False
    
    print("Creating single-file installer...")
    
    # Read the main executable
    with open(main_exe, 'rb') as f:
        exe_data = f.read()
    
    # Encode the executable as base64
    exe_base64 = base64.b64encode(exe_data).decode('ascii')
    
    # Read the installer template
    installer_template = current_dir / "single_file_installer.py"
    with open(installer_template, 'r', encoding='utf-8') as f:
        installer_code = f.read()
    
    # Replace the get_embedded_app_data method with actual data
    embedded_data_method = f'''
    def get_embedded_app_data(self):
        """Get embedded application data."""
        import base64
        
        # Embedded OCR File Sorter executable (base64 encoded)
        exe_data_b64 = """{exe_base64}"""
        
        try:
            return base64.b64decode(exe_data_b64)
        except Exception as e:
            raise Exception(f"Failed to decode embedded application data: {{e}}")
'''
    
    # Replace the placeholder method
    installer_code = installer_code.replace(
        '''    def get_embedded_app_data(self):
        """Get embedded application data."""
        # This would be replaced with actual embedded data
        # For now, return None to indicate no embedded data
        return None''',
        embedded_data_method
    )
    
    # Create the final installer
    installer_path = dist_dir / "OCR_File_Sorter_Installer.py"
    with open(installer_path, 'w', encoding='utf-8') as f:
        f.write(installer_code)
    
    print(f"Single-file installer created: {installer_path}")
    print(f"Installer size: {installer_path.stat().st_size / (1024*1024):.1f} MB")
    
    return True

def create_executable_installer():
    """Create an executable version of the installer."""
    
    # Get the project root directory (parent of scripts)
    current_dir = Path.cwd().parent
    dist_dir = current_dir / "dist"
    installer_py = dist_dir / "OCR_File_Sorter_Installer.py"
    
    if not installer_py.exists():
        print("Error: Python installer not found. Run create_single_file_installer() first.")
        return False
    
    print("Creating executable installer...")
    
    # Create a temporary spec file for the installer
    spec_content = f'''
# -*- mode: python ; coding: utf-8 -*-

a = Analysis(
    ['{installer_py}'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=['tkinter', 'urllib.request', 'winreg'],
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='OCR_File_Sorter_Installer',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    coerce_archive=True,
    icon='{current_dir}/src/icons/sorterIcon.ico',
    version_info=None,
)
'''
    
    spec_file = dist_dir / "installer.spec"
    with open(spec_file, 'w') as f:
        f.write(spec_content)
    
    # Run PyInstaller to create the executable installer
    try:
        import PyInstaller.__main__
        
        args = [
            '--onefile',
            '--noconsole',
            '--name=OCR_File_Sorter_Installer',
            f'--icon={current_dir}/src/icons/sorterIcon.ico',
            '--distpath=../dist',
            '--workpath=../build/installer',
            '--specpath=../build/installer',
            '--hidden-import=tkinter',
            '--hidden-import=urllib.request', 
            '--hidden-import=winreg',
            '--clean',
            str(installer_py)
        ]
        
        PyInstaller.__main__.run(args)
        
        # Check if the executable was created
        installer_exe = dist_dir / "OCR_File_Sorter_Installer.exe"
        if installer_exe.exists():
            print(f"Executable installer created: {installer_exe}")
            print(f"Installer size: {installer_exe.stat().st_size / (1024*1024):.1f} MB")
            
            # Clean up temporary files
            spec_file.unlink()
            
            return True
        else:
            print("Error: Failed to create executable installer")
            return False
            
    except Exception as e:
        print(f"Error creating executable installer: {e}")
        return False

def main():
    """Main function to create the single-file installer."""
    
    print("OCR File Sorter - Single File Installer Builder")
    print("=" * 50)
    
    # Step 1: Create Python installer with embedded data
    if not create_single_file_installer():
        print("Failed to create Python installer")
        return 1
    
    print()
    
    # Step 2: Create executable installer
    if not create_executable_installer():
        print("Failed to create executable installer")
        return 1
    
    print()
    print("✅ Single-file installer creation completed!")
    print()
    print("📦 Distribution files created:")
    print("   • OCR_File_Sorter_Installer.py   - Python installer script")
    print("   • OCR_File_Sorter_Installer.exe  - Self-contained executable installer")
    print()
    print("🚀 Users can run either file to install OCR File Sorter + Tesseract OCR")
    print("   The .exe file requires no Python installation on the target system.")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())

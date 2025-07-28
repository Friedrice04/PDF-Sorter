# 📦 OCR File Sorter - Single File Installer

A complete, self-contained installer for OCR File Sorter that includes everything needed to get users up and running quickly.

## 🎯 What It Includes

The single-file installer (`OCR_File_Sorter_Installer.exe`) contains:

- **OCR File Sorter Application** - The main PDF sorting program
- **Tesseract OCR Engine** - Automatic download and installation for scanned PDF support
- **Desktop Shortcuts** - Quick access from desktop and Start Menu
- **PATH Configuration** - Automatic system configuration
- **Uninstaller** - Clean removal when needed

## 🚀 Building the Installer

### Prerequisites
1. Virtual environment with dependencies installed:
   ```bash
   python -m venv .venv
   .venv\Scripts\activate
   pip install -r requirements-build.txt
   ```

### Quick Build (Recommended)
```bash
# Build everything in one step
build_complete.bat
```

This creates:
- `dist/OCR File Sorter.exe` - Main application
- `dist/OCR_File_Sorter_Installer.exe` - Complete installer for distribution

### Manual Build Steps
```bash
# Step 1: Build main application
build.bat

# Step 2: Create installer
python installer.py --build
```

## 📋 Installer Features

### 🖥️ **User-Friendly GUI**
- Clean, modern interface
- Progress tracking with status updates
- Customizable installation options
- Error handling with clear messages

### ⚙️ **Installation Options**
- **Installation Directory**: Choose where to install
- **Desktop Shortcut**: Quick access from desktop
- **Start Menu Entry**: Add to Windows Start Menu
- **Tesseract OCR**: Automatic OCR engine installation

### 🔧 **Automatic Configuration**
- Downloads and installs Tesseract OCR if needed
- Adds programs to system PATH
- Creates shortcuts and file associations
- Handles Windows registry updates

### 🛡️ **Robust Installation**
- Checks for existing installations
- Silent Tesseract installation when possible
- Fallback installation methods
- Comprehensive error handling
- Automatic cleanup on failure

## 📁 Installation Process

When users run `OCR_File_Sorter_Installer.exe`:

1. **Welcome Screen** - Shows what will be installed
2. **Choose Directory** - Select installation location
3. **Select Options** - Choose shortcuts and components
4. **Download Tesseract** - Automatic OCR engine installation
5. **Extract Application** - Install OCR File Sorter
6. **Create Shortcuts** - Desktop and Start Menu entries
7. **Configure System** - PATH and registry updates
8. **Complete** - Ready to use!

## 🎯 Distribution

### For End Users
1. Download `OCR_File_Sorter_Installer.exe`
2. Run the installer (Administrator recommended)
3. Follow the installation wizard
4. Start using OCR File Sorter!

### For Developers
The installer is completely self-contained and requires no additional files or dependencies on the target system.

## 🔧 Technical Details

### Installer Architecture
- **Base**: Python with tkinter GUI
- **Packaging**: PyInstaller for standalone executable
- **Embedded Data**: Base64-encoded application files
- **Downloads**: Tesseract from official GitHub releases
- **Shortcuts**: Windows COM objects with fallbacks

### File Sizes (Approximate)
- Main Application: ~50-80 MB
- Complete Installer: ~80-120 MB
- Tesseract Download: ~60 MB (downloaded during installation)

### System Requirements
- **OS**: Windows 10/11 (64-bit)
- **RAM**: 256 MB minimum
- **Disk**: 200 MB free space
- **Internet**: Required for Tesseract download

## 🛠️ Customization

### Modify Installation Options
Edit `installer.py`:
- Change default installation directory
- Add/remove installation options
- Modify GUI appearance
- Update Tesseract download URL

### Change Embedded Application
The `installer.py --build` command automatically embeds the latest built application from `dist/OCR File Sorter.exe`.

### Update Tesseract Version
Modify the `tesseract_url` in `installer.py` to point to a newer release:
```python
self.tesseract_url = "https://github.com/UB-Mannheim/tesseract/releases/download/v5.x.x/tesseract-ocr-w64-setup-5.x.x.exe"
```

## ⚠️ Troubleshooting

### Build Issues
- **PyInstaller not found**: Run `pip install -r requirements-build.txt`
- **Missing main executable**: Run `build.bat` first
- **Import errors**: Ensure virtual environment is activated

### Installation Issues
- **Administrator Rights**: Run installer as Administrator for system-wide installation
- **Antivirus**: Some antivirus software may flag the installer; add to whitelist
- **Download Failures**: Check internet connection for Tesseract download

### Runtime Issues
- **Tesseract not found**: Manually install Tesseract and add to PATH
- **Missing shortcuts**: Manually create shortcuts to the installed executable
- **PATH issues**: Restart Windows or manually add installation directory to PATH

## 📝 Notes

- The installer automatically detects existing Tesseract installations
- Silent installation is attempted first, with fallback to interactive mode
- All installation paths use proper Windows conventions
- The uninstaller removes files, shortcuts, and PATH entries
- Administrator rights are recommended but not required

---

This installer makes it incredibly easy to distribute OCR File Sorter to end users with zero technical knowledge required! 🎉

# OCR File Sorter - Simplified Build System

## Overview

The build system has been simplified into three focused batch scripts:

### 🔧 `build.bat` - Main Application
**Purpose**: Builds the main application in directory mode and creates a distribution zip

**What it does**:
- Builds `OCR File Sorter.exe` and supporting files in directory mode (not --onefile)
- Creates `dist/OCR File Sorter/` folder with all application files
- Creates `dist/OCR_File_Sorter.zip` containing the complete application
- The zip file is ready for upload to GitHub releases

**Output Files**:
- `dist/OCR File Sorter/OCR File Sorter.exe` - Main executable
- `dist/OCR File Sorter/_internal/` - Supporting libraries and data
- `dist/OCR_File_Sorter.zip` - Complete application package

### 📦 `build_installer.bat` - Installer Only
**Purpose**: Creates only the download-based installer executable

**What it does**:
- Builds `OCR_File_Sorter_Download_Installer.exe` as a single file
- The installer downloads the application zip from GitHub during installation
- Much smaller size (~11 MB) compared to embedded approach
- Includes Tesseract OCR installation and system integration

**Output Files**:
- `dist/OCR_File_Sorter_Download_Installer.exe` - Small installer that downloads app

### 🚀 `build_complete.bat` - Both Application and Installer
**Purpose**: Runs both builds in sequence for complete deployment preparation

**What it does**:
- Calls `build.bat` to create the application and zip
- Calls `build_installer.bat` to create the installer
- Provides complete deployment package

**Output Files**:
- All files from both `build.bat` and `build_installer.bat`

## Usage Examples

### Building Just the Application
```batch
cd scripts
build.bat
```
Use this when:
- You want to test the application locally
- You need to create a zip for GitHub releases
- You're doing development and don't need the installer

### Building Just the Installer
```batch
cd scripts
build_installer.bat
```
Use this when:
- The application zip is already uploaded to GitHub
- You only need to update the installer
- You want to test the installer functionality

### Building Everything
```batch
cd scripts
build_complete.bat
```
Use this when:
- Preparing for a new release
- You want both application and installer ready
- Setting up complete deployment package

## File Size Comparison

| Component | Size | Description |
|-----------|------|-------------|
| Application Directory | ~50 MB | Full app with all dependencies |
| Application Zip | ~38 MB | Compressed application package |
| Download Installer | ~11 MB | Small installer that downloads app |
| Total User Download | ~49 MB | Installer + App (downloaded separately) |

## Deployment Workflow

1. **Build Everything**: Run `build_complete.bat`
2. **Upload Zip**: Upload `OCR_File_Sorter.zip` to GitHub releases
3. **Distribute Installer**: Share `OCR_File_Sorter_Download_Installer.exe` with users
4. **User Experience**: Users download small installer → Installer downloads app → Installation complete

## Benefits of This Approach

### For Developers
- **Simple Commands**: One script = one purpose
- **Faster Iteration**: Build only what you need
- **Easy Testing**: Test application and installer separately
- **Clear Outputs**: Know exactly what each script produces

### For Users
- **Smaller Downloads**: Initial installer is much smaller
- **Reliable Installation**: Downloads from GitHub's fast CDN
- **Always Current**: Installer downloads latest uploaded version
- **No Large Files**: Don't need to download 100MB+ installers

### For Distribution
- **Easy Updates**: Just replace the zip file on GitHub
- **Version Control**: Can host multiple versions simultaneously
- **Bandwidth Friendly**: Users download in two smaller chunks
- **Flexible Hosting**: Can change download location easily

## Quick Reference

```batch
# Build application + zip
build.bat

# Build installer only  
build_installer.bat

# Build everything
build_complete.bat
```

All scripts automatically:
- ✅ Check for virtual environment
- ✅ Install dependencies if missing
- ✅ Clean previous builds
- ✅ Show clear success/failure messages
- ✅ Display output file locations and sizes

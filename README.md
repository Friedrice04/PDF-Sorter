# 📄 OCR File Sorter

A powerful, intelligent PDF sorting application that automatically organizes documents based on their content using OCR technology.

## 🚀 Quick Start

### For Users
1. Download the installer: `OCR_File_Sorter_Installer.exe`
2. Run the installer and follow the setup wizard
3. Start sorting your PDFs!

### For Developers
```bash
# Clone and setup
git clone https://github.com/Friedrice04/PDF-Sorter.git
cd PDF-Sorter

# Create virtual environment
python -m venv .venv
.venv\Scripts\activate

# Install dependencies
pip install -r config/requirements.txt

# Run the application
python src/main.py
```

## 📁 Project Structure

```
PDF-Sorter/
├── 📂 src/                    # Main application code
│   ├── main.py               # Application entry point
│   ├── gui.py                # User interface
│   ├── sorter.py             # Core sorting logic
│   ├── utils.py              # Utility functions
│   ├── 📂 icons/             # Application icons
│   ├── 📂 mappings/          # Sorting rule examples
│   └── 📂 mapping_editor/    # Mapping editor module
├── 📂 tests/                 # Test suite
│   ├── 📂 test_runner/       # PDF testing framework
│   └── ...                   # Unit and integration tests
├── 📂 scripts/               # Build and utility scripts
│   ├── build.bat            # Simple build script
│   ├── build_complete.bat   # Complete build with installer
│   ├── build_exe.py         # PyInstaller build script
│   └── installer.py         # Unified installer (build & install)
├── 📂 config/                # Configuration files
│   ├── requirements.txt     # Runtime dependencies
│   ├── requirements-build.txt # Build dependencies
│   └── requirements-dev.txt # Development dependencies
├── 📂 docs/                  # Documentation
│   ├── DISTRIBUTION_GUIDE.md # Distribution instructions
│   └── INSTALLER_README.md  # Installer technical details
├── 📂 build/                 # Build artifacts (ignored)
├── 📂 dist/                  # Distribution files
└── build.bat                 # Root-level build script
```

## ✨ Features

### 🤖 **Intelligent PDF Processing**
- **Text Extraction**: Direct PDF text reading with OCR fallback
- **Pattern Matching**: Flexible phrase-based sorting rules
- **OCR Support**: Handles scanned documents with Tesseract
- **Robust Parsing**: Handles OCR quirks and text variations

### 🎯 **Smart Sorting**
- **Custom Mappings**: Create your own sorting rules
- **Template System**: Predefined folder structures
- **Batch Processing**: Sort multiple files at once
- **File Naming**: Configurable output file naming schemes

### 🖥️ **User-Friendly Interface**
- **Drag & Drop**: Easy file selection
- **Progress Tracking**: Real-time sorting progress
- **Visual Feedback**: Clear status updates and error messages
- **Mapping Editor**: Built-in rule editor with preview

### 🔧 **Professional Features**
- **Comprehensive Testing**: PDF testing framework included
- **Easy Distribution**: Single-file installer with dependencies
- **Cross-Platform**: Windows focus with portable codebase
- **Extensible**: Modular architecture for easy enhancement

## 🛠️ Building

### Quick Build
```bash
# Build everything (application + installer)
build.bat
```

### Manual Build Steps
```bash
# 1. Install build dependencies
pip install -r config/requirements-build.txt

# 2. Build main application
cd scripts
python build_exe.py

# 3. Create installer (optional)
python installer.py --build
```

### Output Files
- `dist/OCR File Sorter.exe` - Main application
- `dist/OCR_File_Sorter_Installer.exe` - Complete installer

## 🧪 Testing

### Run Tests
```bash
# Run all tests
python -m pytest tests/

# Test PDF sorting specifically
cd tests/test_runner
python run_pdf_tests.py --verbose
```

### PDF Testing Framework
The included test runner lets you easily test PDF sorting:
1. Add PDFs to `tests/test_runner/input_pdfs/`
2. Add mapping files to `tests/test_runner/test_mappings/`
3. Run `run_pdf_tests.py` to see where each PDF would be sorted

## 📋 Requirements

### Runtime
- **OS**: Windows 10/11 (64-bit)
- **Python**: 3.8+ (for source)
- **Dependencies**: See `config/requirements.txt`

### Optional
- **Tesseract OCR**: For scanned PDF support (auto-installed with installer)

## 🎯 Use Cases

- **Document Management**: Organize invoices, contracts, reports
- **Office Automation**: Sort incoming documents by type
- **Archive Organization**: Clean up document collections
- **Workflow Integration**: Part of larger document processing pipelines

## 📝 License

This project is licensed under the terms specified in LICENCE.txt.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## 📚 Documentation

- [Distribution Guide](docs/DISTRIBUTION_GUIDE.md) - Complete distribution instructions
- [Installer README](docs/INSTALLER_README.md) - Installer technical details
- [Test Runner Guide](tests/test_runner/README.md) - PDF testing framework

## 🆘 Support

- Check the documentation in the `docs/` folder
- Review test examples in `tests/test_runner/`
- Open an issue for bugs or feature requests

---

**Transform your document chaos into organized bliss!** 📄✨

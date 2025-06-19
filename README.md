# OCR File Sorter

**OCR File Sorter** is a user-friendly desktop application for sorting PDF files into folders based on their content. It uses Optical Character Recognition (OCR) to find keywords or phrases inside documents and sorts them according to customizable mapping rules.

---

## Features

- **Content-Based Sorting:**  
  Reads text from within PDF documents to determine the correct destination folder.
- **Mapping Editor:**  
  Create, edit, and search mapping files (`.json`) that define which phrases/keywords map to which folders.
- **Template Directory Structure:**  
  Visualize, add, delete, and rename folders in your template directory.  
  Drag-and-drop folders from Windows Explorer to add their structure (folders only, no files).
- **Phrase-to-Folder Assignment:**  
  Assign phrases to destination folders using a table. Drag phrases onto folders in the tree to set destinations.
- **Auto-Build Template Tree:**  
  Automatically create the template folder structure based on all destinations in your mapping.
- **Mapping Import:**  
  Create a new mapping by importing from an existing mapping file.
- **Persistent Last Mapping:**  
  The last used mapping is remembered and auto-selected on next launch.
- **File Sorting:**  
  Select one or more folders to sort. Drag-and-drop folders into the app or use the "Add Folder" button.
- **Deep Audit:**  
  Optionally, after sorting, recursively find and move misplaced PDF files to their correct folders based on content.
- **Help and Tooltips:**  
  Built-in help and tooltips for all major controls.

---

## Getting Started

### Requirements

- Python 3.8+
- [tkinterdnd2](https://github.com/pmgagne/tkinterdnd2)
- [PyMuPDF](https://pypi.org/project/PyMuPDF/)

### Running the App

1. **Install dependencies:**
   ```
   pip install -r requirements.txt
   ```

2. **Start the application:**
   ```
   python -m src.main
   ```

---

## Usage

### Main Window

- **Select Mapping:**  
  Choose a mapping file from the dropdown. The last used mapping is auto-selected.
- **Edit/Create Mapping:**  
  Opens the Mapping Editor to modify or create mapping files (phrase-to-folder rules) and template folders.
- **Folders to Sort:**  
  Add folders containing PDFs to be sorted. Use the button or drag-and-drop from Explorer.
- **Deep Audit:**  
  Enable to recursively move misplaced PDFs after sorting based on their content.
- **Sort Files:**  
  Starts the sorting process for PDFs in the selected folders.

### Mapping Editor

- **Mapping File Selection:**  
  Dropdown and search for mapping files. Create new mappings or import from existing ones.
- **Phrase Table:**  
  Add, edit, remove, and reorder phrase-to-folder rules. Drag phrases onto folders in the tree to assign destinations.
- **Template Directory Structure:**  
  Visualize and manage the folder structure.  
  - Right-click for add/rename/delete.
  - Drag folders from Explorer to add their structure (folders only, no files).
  - Use "Auto-Build Tree" to create folders for all mapping destinations.
- **Save:**  
  Saves changes and returns to the main window.

---

## File Structure

```
src/
  gui.py                # Main GUI logic
  main.py               # Entry point
  sorter.py             # File sorting and OCR logic
  utils.py              # Utilities and tooltips
  settings.json         # Stores last used mapping
  mapping_editor/
    editor.py           # Mapping editor window
    dialogs.py          # Dialogs for mapping/template editing
    mapping_table.py    # Phrase-to-folder table widget
    template_tree.py    # Template folder tree widget
  mappings/
    *.json              # Mapping files
    *_template/         # Template folder structures
  icons/
    *.ico               # Application icons
```

---

## Notes

- **Mappings:**  
  Mapping files are JSON objects where the key is the phrase to search for (case-insensitive) and the value is the destination folder:
  ```json
  {
    "INVOICE": "Invoices",
    "Purchase Order": "Purchase Orders"
  }
  ```
- **Template Folders:**  
  Each mapping file has a corresponding `_template` folder for its folder structure.
- **Drag-and-Drop:**  
  Drag folders from Explorer to the template tree to add their structure (folders only, no files).

---

## Troubleshooting

- If the application doesn't start, ensure all dependencies from `requirements.txt` are installed.
- If drag-and-drop does not work, ensure `tkinterdnd2` is installed correctly.
- Sorting only applies to `.pdf` files. Other files will be ignored.

---

## Author

  Henry Dowd
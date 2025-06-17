# FileSorter

**FileSorter** is a user-friendly desktop application for sorting files into folders based on customizable mapping rules. It features a graphical interface for editing mapping files, managing template folder structures, and running file sorting operations with optional deep audit.

---

## Features

- **Mapping Editor:**  
  Create, edit, and search mapping files (`.json`) that define how files are sorted by pattern (wildcards supported).
- **Template Directory Structure:**  
  Visualize, add, delete, and rename folders in your template directory.  
  Drag-and-drop folders from Windows Explorer to add their structure (folders only, no files).
- **Pattern-to-Folder Assignment:**  
  Assign file patterns to destination folders using a table. Drag patterns onto folders in the tree to set destinations.
- **Auto-Build Template Tree:**  
  Automatically create the template folder structure based on all destinations in your mapping.
- **Mapping Import:**  
  Create a new mapping by importing from an existing mapping file, with clear indication of the selected import file.
- **Persistent Last Mapping:**  
  The last used mapping is remembered and auto-selected on next launch.
- **File Sorting:**  
  Select one or more folders to sort. Drag-and-drop folders into the app or use the "Add Folder" button.
- **Deep Audit:**  
  Optionally, after sorting, recursively move misplaced files to their correct folders.
- **Help and Tooltips:**  
  Built-in help and tooltips for all major controls.

---

## Getting Started

### Requirements

- Python 3.8+
- [tkinterdnd2](https://github.com/pmgagne/tkinterdnd2) (`pip install tkinterdnd2`)

### Running the App

1. **Install dependencies:**
   ```
   pip install tkinterdnd2
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
  Opens the Mapping Editor to modify or create mapping files and template folders.
- **Folders to Sort:**  
  Add folders using the button or drag-and-drop from Explorer. Remove with "Remove Selected".
- **Deep Audit:**  
  Enable to recursively move misplaced files after sorting.
- **Sort Files:**  
  Sorts files in the selected folders according to the mapping.

### Mapping Editor

- **Mapping File Selection:**  
  Dropdown and search for mapping files. Create new mappings or import from existing ones.
- **Pattern Table:**  
  Add, edit, remove, and reorder pattern-to-folder rules. Drag patterns onto folders in the tree to assign destinations.
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
  sorter.py             # File sorting logic
  utils.py              # Utilities and tooltips
  settings.json         # Stores last used mapping
  mapping_editor/
    editor.py           # Mapping editor window
    dialogs.py          # Dialogs for mapping/template editing
    mapping_table.py    # Pattern-to-folder table widget
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
  Mapping files are JSON objects:  
  ```json
  {
    "*.pdf": "PDF Documents",
    "Invoice*2024*.docx": "2024 Invoices"
  }
  ```
- **Template Folders:**  
  Each mapping file has a corresponding `_template` folder for its folder structure.
- **Drag-and-Drop:**  
  Drag folders from Explorer to the template tree to add their structure (folders only, no files).

---

## Troubleshooting

- If drag-and-drop does not work, ensure `tkinterdnd2` is installed.
- If you see errors about missing mappings or folders, ensure you have created at least one mapping and template directory.

---

## License

MIT License

---

## Author
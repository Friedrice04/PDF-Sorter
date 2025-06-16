Here’s a README that matches your current project structure and usage:

---

# FileSorter

A cross-platform tool to sort files into folders based on user-defined filename patterns.  
Includes a GUI for selecting mappings, directories, and editing mapping rules with a user-friendly pattern builder.

---

## Features

- **Sort files** in a folder or in all first-level subfolders.
- **Mapping Editor** with drag-and-drop, row numbering, and a Pattern Builder UI.
- **Pattern Builder**: Build filename patterns using "Starts with", "Contains", "Ends with", and "Extension" fields—no wildcard knowledge needed.
- **Deep Audit**: Optionally move misplaced files to their correct folders recursively.
- **Easy mapping management**: Create, edit, and save mapping files in JSON format.

---

## Project Structure

```
src/
  main.py
  gui.py
  sorter.py
  utils.py
  mappings/
    <your mapping files>.json
  mapping_editor/
    __init__.py
    editor.py
    pattern_builder.py
    tooltip.py
```

---

## Usage

### 1. **Run the Application**

From the src directory:

```bash
python main.py
```

### 2. **Sorting Files**

- Select a mapping file (or create/edit one).
- Choose the directory to sort.
- Select sorting mode:
  - **Single Folder**: Sorts files in the selected folder.
  - **Child Folders**: Sorts files in each first-level subfolder.
- (Optional) Enable **Deep Audit** to recursively fix misplaced files.
- Click **Sort Files**.

### 3. **Editing Mappings**

- Click **Edit/Create Mapping** to open the Mapping Editor.
- Add, update, delete, or reorder mapping rules.
- Use the **Pattern Builder** to create patterns without wildcards.
- Save your mapping file.

---

## Mapping File Format

Mapping files are JSON objects with patterns as keys and destination folders as values:

```json
{
    "PAYP*": "01 Pay",
    "APP*2024*.pdf": "Applications 2024",
    "Tr*FE": "Transfers"
}
```

Patterns use wildcards:
- `*` matches any number of characters
- `?` matches a single character

---

## Requirements

- Python 3.7+
- Standard library only (uses `tkinter` for GUI)

---

## Notes

- All mapping files are stored in the mappings folder.
- The Pattern Builder UI allows you to create patterns using simple fields—no need to know wildcard syntax.

---

## License

MIT License

---

**For any issues or suggestions, please open an issue or pull request.**
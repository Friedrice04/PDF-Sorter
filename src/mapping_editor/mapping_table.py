import tkinter as tk
from tkinter import ttk

class MappingTable(ttk.Treeview):
    """
    Custom Treeview for displaying and managing pattern → destination mappings.
    Handles drag start for drag-and-drop assignment.
    """
    def __init__(self, master, on_pattern_drag=None, **kwargs):
        columns = ("Pattern", "Destination")
        super().__init__(master, columns=columns, show="headings", selectmode="browse", **kwargs)
        self.heading("Pattern", text="Pattern")
        self.heading("Destination", text="Destination")
        self.column("Pattern", width=250, anchor="w")
        self.column("Destination", width=350, anchor="w")
        self.on_pattern_drag = on_pattern_drag

        self._dragged_pattern = None
        self._dragging = False

        self.bind("<ButtonPress-1>", self._on_drag_start)
        self.bind("<B1-Motion>", self._on_drag_motion)
        # No <ButtonRelease-1> binding here (handled globally in editor.py)

    def _on_drag_start(self, event):
        item = self.identify_row(event.y)
        if item:
            self._dragged_pattern = self.item(item, "values")[0]
            self.selection_set(item)
            self._dragging = True
            if self.on_pattern_drag:
                self.on_pattern_drag("start", self._dragged_pattern)
        else:
            self._dragged_pattern = None
            self._dragging = False

    def _on_drag_motion(self, event):
        if self._dragging and self.on_pattern_drag:
            self.on_pattern_drag("motion", self._dragged_pattern)

    def refresh(self, mappings):
        self.delete(*self.get_children())
        for pattern, dest in mappings.items():
            self.insert("", "end", values=(pattern, dest))
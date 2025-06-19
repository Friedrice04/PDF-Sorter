import tkinter as tk
from tkinter import ttk

class MappingTable(ttk.Treeview):
    """
    Custom Treeview for displaying and managing phrase → destination mappings.
    Handles drag start for drag-and-drop assignment.
    """
    def __init__(self, master, on_item_drag=None, **kwargs):
        columns = ("Phrase / Keyword", "Destination")
        super().__init__(master, columns=columns, show="headings", selectmode="browse", **kwargs)
        self.heading("Phrase / Keyword", text="Phrase / Keyword")
        self.heading("Destination", text="Destination")
        self.column("Phrase / Keyword", width=250, anchor="w")
        self.column("Destination", width=350, anchor="w")
        self.on_item_drag = on_item_drag

        self._dragged_item = None
        self._dragging = False

        self.bind("<ButtonPress-1>", self._on_drag_start)
        self.bind("<B1-Motion>", self._on_drag_motion)
        # No <ButtonRelease-1> binding here (handled globally in editor.py)

    def _on_drag_start(self, event):
        item = self.identify_row(event.y)
        if item:
            self._dragged_item = self.item(item, "values")[0]
            self.selection_set(item)
            self._dragging = True
            if self.on_item_drag:
                self.on_item_drag("start", self._dragged_item)
        else:
            self._dragged_item = None
            self._dragging = False

    def _on_drag_motion(self, event):
        if self._dragging and self.on_item_drag:
            self.on_item_drag("motion", self._dragged_item)

    def refresh(self, mappings):
        self.delete(*self.get_children())
        for phrase, dest in mappings.items():
            self.insert("", "end", values=(phrase, dest))
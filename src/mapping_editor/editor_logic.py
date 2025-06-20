import os
import shutil
from src import utils

class EditorLogic:
    """
    Handles the data and business logic for the Mapping Editor,
    decoupled from the UI.
    """
    def __init__(self):
        self.mappings = {}
        self.mapping_path = None
        self.template_dir = None
        self.is_dirty = False

    def load_mapping_file(self, file_path):
        """Loads a mapping file and its associated template directory."""
        self.mapping_path = file_path
        self.template_dir = self._get_template_dir(file_path)
        if not os.path.exists(self.template_dir):
            os.makedirs(self.template_dir)
        
        if utils.MappingUtils.is_valid_mapping_file(self.mapping_path):
            self.mappings = utils.MappingUtils.load_mapping(self.mapping_path)
        else:
            self.mappings = {}
        self.is_dirty = False
        return True

    def save_mappings(self):
        """Saves the current mappings to the file."""
        if not self.mapping_path:
            return False, "No mapping file selected."
        try:
            utils.MappingUtils.save_mapping(self.mapping_path, self.mappings)
            self.is_dirty = False
            return True, "Mapping saved successfully."
        except Exception as e:
            return False, f"Could not save mapping:\n{e}"

    def add_rule(self, phrase, dest):
        """Adds a new mapping rule."""
        if phrase in self.mappings:
            return False, "This phrase or keyword already exists."
        self.mappings[phrase] = dest
        self.is_dirty = True
        return True, None

    def update_rule(self, old_phrase, new_phrase, new_dest):
        """Updates an existing mapping rule."""
        if new_phrase != old_phrase and new_phrase in self.mappings:
            return False, "This phrase or keyword already exists."
        del self.mappings[old_phrase]
        self.mappings[new_phrase] = new_dest
        self.is_dirty = True
        return True, None

    def remove_rule(self, phrase):
        """Removes a mapping rule."""
        if phrase in self.mappings:
            del self.mappings[phrase]
            self.is_dirty = True
        return True, None

    def move_rule(self, phrase, direction):
        """Moves a rule up or down in the order."""
        keys = list(self.mappings.keys())
        try:
            index = keys.index(phrase)
        except ValueError:
            return False
        
        if direction == "up" and index > 0:
            keys.insert(index - 1, keys.pop(index))
        elif direction == "down" and index < len(keys) - 1:
            keys.insert(index + 1, keys.pop(index))
        else:
            return False # No move was possible

        self.mappings = {k: self.mappings[k] for k in keys}
        self.is_dirty = True
        return True

    def rename_template_folder(self, old_rel_path, new_folder_name):
        """Renames a folder in the template directory and updates mappings."""
        old_abs_path = os.path.join(self.template_dir, old_rel_path)
        new_rel_path = os.path.join(os.path.dirname(old_rel_path), new_folder_name)
        new_abs_path = os.path.join(self.template_dir, new_rel_path)

        if os.path.exists(new_abs_path):
            return False, "A folder with that name already exists."
        
        try:
            os.rename(old_abs_path, new_abs_path)
        except Exception as e:
            return False, f"Could not rename folder:\n{e}"

        # Update mappings
        for phrase, dest in self.mappings.items():
            if not dest or dest == ".": continue
            norm_dest = os.path.normpath(dest)
            norm_old = os.path.normpath(old_rel_path)
            if norm_dest == norm_old or norm_dest.startswith(norm_old + os.sep):
                new_dest = os.path.normpath(norm_dest.replace(norm_old, new_rel_path, 1))
                self.mappings[phrase] = new_dest
        
        self.is_dirty = True
        return True, None

    def autobuild_template_tree(self):
        """Creates template folders based on destinations in the mappings."""
        if not self.template_dir: return 0
        created = 0
        for dest in set(self.mappings.values()):
            if not dest or dest == ".": continue
            folder_path = os.path.join(self.template_dir, dest)
            if not os.path.exists(folder_path):
                os.makedirs(folder_path, exist_ok=True)
                created += 1
        return created

    def _get_template_dir(self, mapping_path):
        base, _ = os.path.splitext(mapping_path)
        return base + "_template"
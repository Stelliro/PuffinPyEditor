# PuffinPyEditor/app_core/file_handler.py
import os
import sys
import shutil
import subprocess
from PyQt6.QtWidgets import QFileDialog, QMessageBox, QApplication
from utils.logger import log
from app_core.settings_manager import settings_manager


class FileHandler:
    def __init__(self, parent_window=None):
        self.parent_window = parent_window

    def new_file(self):
        log.info("FileHandler: new_file action invoked.")
        return {"content": "", "filepath": None, "new_file_default_name": "Untitled"}

    def open_file_dialog(self):
        last_dir = settings_manager.get("last_opened_directory", os.path.expanduser("~"))
        filepath, _ = QFileDialog.getOpenFileName(
            self.parent_window, "Open File", last_dir, "Python Files (*.py *.pyw);;All Files (*)"
        )
        if not filepath: return None, None, None

        settings_manager.set("last_opened_directory", os.path.dirname(filepath))
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            self._add_to_recent_files(filepath)
            return filepath, content, None
        except Exception as e:
            msg = f"Error opening file {filepath}: {e}"
            log.error(msg, exc_info=True)
            QMessageBox.critical(self.parent_window, "Error Opening File", msg)
            return None, None, msg

    def save_file_content(self, filepath, content, save_as=False):
        if save_as or not filepath or not os.path.exists(os.path.dirname(filepath)):
            initial_dir = os.path.dirname(filepath) if filepath else settings_manager.get("last_saved_directory",
                                                                                          os.path.expanduser("~"))
            suggested_filename = os.path.basename(filepath) if filepath else "Untitled.py"

            filepath_from_dialog, _ = QFileDialog.getSaveFileName(
                self.parent_window, "Save File As", os.path.join(initial_dir, suggested_filename),
                "Python Files (*.py *.pyw);;All Files (*)"
            )
            if not filepath_from_dialog: return None
            filepath = filepath_from_dialog
            settings_manager.set("last_saved_directory", os.path.dirname(filepath))

        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            self._add_to_recent_files(filepath)
            return filepath
        except Exception as e:
            msg = f"Error saving file {filepath}: {e}"
            log.error(msg, exc_info=True)
            QMessageBox.critical(self.parent_window, "Error Saving File", msg)
            return None

    def _add_to_recent_files(self, filepath):
        if not filepath: return
        recents = settings_manager.get("recent_files", [])
        if filepath in recents: recents.remove(filepath)
        recents.insert(0, filepath)
        settings_manager.set("recent_files", recents[:settings_manager.get("max_recent_files", 10)])
        if self.parent_window and hasattr(self.parent_window, '_update_recent_files_menu'):
            self.parent_window._update_recent_files_menu()

    def create_file(self, path):
        try:
            if os.path.exists(path): return False, f"'{os.path.basename(path)}' already exists."
            with open(path, 'w', encoding='utf-8'):
                pass
            log.info(f"Created file: {path}")
            return True, None
        except OSError as e:
            return False, f"Failed to create file: {e}"

    def create_folder(self, path):
        try:
            if os.path.exists(path): return False, f"'{os.path.basename(path)}' already exists."
            os.makedirs(path);
            log.info(f"Created folder: {path}");
            return True, None
        except OSError as e:
            return False, f"Failed to create folder: {e}"

    def rename_item(self, old_path, new_name):
        if not new_name.strip(): return False, "Name cannot be empty."
        new_path = os.path.join(os.path.dirname(old_path), new_name)
        if os.path.exists(new_path): return False, f"'{new_name}' already exists here."
        try:
            os.rename(old_path, new_path); return True, new_path
        except OSError as e:
            return False, f"Failed to rename: {e}"

    def delete_item(self, path):
        try:
            if os.path.isfile(path):
                os.remove(path)
            elif os.path.isdir(path):
                shutil.rmtree(path)
            log.info(f"Deleted: {path}");
            return True, None
        except (OSError, shutil.Error) as e:
            return False, f"Failed to delete: {e}"

    def copy_path_to_clipboard(self, path):
        try:
            QApplication.clipboard().setText(os.path.normpath(path)); return True, None
        except Exception as e:
            return False, "Could not access clipboard."

    def reveal_in_explorer(self, path):
        try:
            if sys.platform == 'win32':
                subprocess.run(['explorer', '/select,', os.path.normpath(path)])
            elif sys.platform == 'darwin':
                subprocess.run(['open', '-R', os.path.normpath(path)])
            else:
                subprocess.run(['xdg-open', os.path.dirname(os.path.normpath(path))])
            return True, None
        except Exception as e:
            return False, f"Could not open file browser: {e}"

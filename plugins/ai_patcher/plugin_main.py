# PuffinPyEditor/app_core/file_handler.py
import os
import sys
import shutil
import subprocess
import re
from typing import Optional, Tuple, Any, Dict
from PyQt6.QtWidgets import QFileDialog, QMessageBox
from PyQt6.QtGui import QGuiApplication, QDesktopServices
from PyQt6.QtCore import QUrl, pyqtSignal, QObject
from .settings_manager import settings_manager
from utils.logger import log
from utils.helpers import clean_git_conflict_markers # Import the new utility


class FileHandler(QObject):
    item_created = pyqtSignal(str, str)
    item_renamed = pyqtSignal(str, str, str)
    item_deleted = pyqtSignal(str, str)
    recent_files_changed = pyqtSignal()

    def __init__(self, parent_window: Optional[Any] = None):
        super().__init__()
        self.parent_window = parent_window
        self._internal_clipboard: Dict[str, Optional[str]] = { "operation": None, "path": None }

    def new_file(self) -> Dict[str, Optional[str]]:
        log.info("FileHandler: new_file action invoked.")
        return { "content": "", "filepath": None, "new_file_default_name": "Untitled" }

    def open_file_dialog(self) -> Tuple[Optional[str], Optional[str], Optional[str]]:
        last_dir = settings_manager.get("last_opened_directory", os.path.expanduser("~"))
        filepath, _ = QFileDialog.getOpenFileName(self.parent_window, "Open File", last_dir, "Python Files (*.py *.pyw);;All Files (*)")
        if not filepath: return None, None, None
        settings_manager.set("last_opened_directory", os.path.dirname(filepath))
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                original_content = f.read()
            # Automatically clean git conflict markers when opening a file.
            content = clean_git_conflict_markers(original_content)
            if content != original_content:
                log.info(f"Cleaned git conflict markers from {filepath} on load.")
                # Ask user if they want to save the cleaned file
                reply = QMessageBox.question(
                    self.parent_window,
                    "Conflict Markers Removed",
                    f"Git conflict markers were found and removed from '{os.path.basename(filepath)}'.\n\n"
                    "Do you want to save these changes back to the file immediately?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                    QMessageBox.StandardButton.Yes
                )
                if reply == QMessageBox.StandardButton.Yes:
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(content)
                    log.info(f"Saved automatically cleaned file: {filepath}")

            self._add_to_recent_files(filepath)
            return filepath, content, None
        except (IOError, OSError, UnicodeDecodeError) as e:
            msg = (f"Error opening file '{os.path.basename(filepath)}'.\n\nReason: {e}")
            log.error(msg, exc_info=True); return None, None, msg

    def save_file_content(self, filepath: Optional[str], content: str, save_as: bool = False) -> Optional[str]:
        dir_exists = filepath and os.path.exists(os.path.dirname(filepath))
        if save_as or not filepath or not dir_exists:
            last_dir = os.path.dirname(filepath) if dir_exists else settings_manager.get("last_saved_directory", os.path.expanduser("~"))
            sugg_name = os.path.basename(filepath) if filepath else "Untitled.py"
            path_from_dialog, _ = QFileDialog.getSaveFileName(self.parent_window, "Save File As", os.path.join(last_dir, sugg_name), "Python Files (*.py *.pyw);;All Files (*)")
            if not path_from_dialog: return None
            filepath = path_from_dialog; settings_manager.set("last_saved_directory", os.path.dirname(filepath))
        try:
            with open(filepath, 'w', encoding='utf-8') as f: f.write(content)
            return filepath
        except (IOError, OSError) as e:
            msg = f"Error saving file '{filepath}': {e}"; log.error(msg, exc_info=True)
            QMessageBox.critical(self.parent_window, "Error Saving File", msg); return None

    def create_file(self, path: str) -> Tuple[bool, Optional[str]]:
        try:
            if os.path.exists(path): item_type = "folder" if os.path.isdir(path) else "file"; return False, f"A {item_type} named '{os.path.basename(path)}' already exists."
            with open(path, 'w', encoding='utf-8'): pass
            log.info(f"Created file: {path}"); self.item_created.emit("file", path); return True, None
        except OSError as e: log.error(f"Failed to create file at {path}: {e}", exc_info=True); return False, f"Failed to create file: {e}"

    def create_folder(self, path: str) -> Tuple[bool, Optional[str]]:
        try:
            if os.path.exists(path): item_type = "folder" if os.path.isdir(path) else "file"; return False, f"A {item_type} named '{os.path.basename(path)}' already exists."
            os.makedirs(path); log.info(f"Created folder: {path}"); self.item_created.emit("folder", path); return True, None
        except OSError as e: log.error(f"Failed to create folder at {path}: {e}", exc_info=True); return False, f"Failed to create folder: {e}"

    def rename_item(self, old_path, new_name):
        new_name = new_name.strip()
        if not new_name: return False, "Name cannot be empty."
        if re.search(r'[<>:"/\\|?*]', new_name): return False, 'Name contains illegal characters (e.g., \\ / : * ? " < > |).'
        new_path = os.path.join(os.path.dirname(old_path), new_name)
        if os.path.exists(new_path): return False, f"'{new_name}' already exists here."
        item_type = 'folder' if os.path.isdir(old_path) else 'file'
        try: os.rename(old_path, new_path); log.info(f"Renamed '{old_path}' to '{new_path}'"); self.item_renamed.emit(item_type, old_path, new_path); return True, new_path
        except OSError as e: log.error(f"Failed to rename '{old_path}': {e}", exc_info=True); return False, f"Failed to rename: {e}"

    def delete_item(self, path):
        item_type = 'file' if os.path.isfile(path) else 'folder'
        try:
            if os.path.isfile(path): os.remove(path)
            elif os.path.isdir(path): shutil.rmtree(path)
            log.info(f"Deleted item: {path}"); self.item_deleted.emit(item_type, path); return True, None
        except (OSError, shutil.Error) as e: log.error(f"Failed to delete '{path}': {e}", exc_info=True); return False, f"Failed to delete: {e}"

    def copy_path_to_clipboard(self, path):
        try:
            QGuiApplication.clipboard().setText(os.path.normpath(path)); log.info(f"Copied path to clipboard: {path}")
            if self.parent_window and hasattr(self.parent_window, "statusBar"): self.parent_window.statusBar().showMessage("Path copied to clipboard", 2000)
        except Exception as e: log.error(f"Could not copy path to clipboard: {e}")

    def reveal_in_explorer(self, path):
        path_to_show = os.path.normpath(path)
        try:
            if sys.platform == 'win32': subprocess.run(['explorer', '/select,', path_to_show] if not os.path.isdir(path_to_show) else ['explorer', path_to_show])
            elif sys.platform == 'darwin': subprocess.run(['open', path_to_show] if os.path.isdir(path_to_show) else ['open', '-R', path_to_show])
            else: subprocess.run(['xdg-open', path_to_show if os.path.isdir(path_to_show) else os.path.dirname(path_to_show)])
        except Exception as e: log.error(f"Could not open file browser for path '{path}': {e}"); QMessageBox.warning(self.parent_window, "Error", f"Could not open file browser: {e}")

    def open_with_default_app(self, path):
        try: QDesktopServices.openUrl(QUrl.fromLocalFile(path))
        except Exception as e: log.error(f"Failed to open '{path}' with default app: {e}"); QMessageBox.warning(self.parent_window, "Error", f"Could not open file with default application: {e}")

    def duplicate_item(self, path):
        dir_name, (base_name, ext) = os.path.dirname(path), os.path.splitext(os.path.basename(path))
        counter = 1; new_path = os.path.join(dir_name, f"{base_name}_copy{ext}")
        while os.path.exists(new_path): counter += 1; new_path = os.path.join(dir_name, f"{base_name}_copy_{counter}{ext}")
        try:
            item_type = "folder";
            if os.path.isfile(path): shutil.copy2(path, new_path); item_type = "file"
            elif os.path.isdir(path): shutil.copytree(path, new_path)
            log.info(f"Duplicated '{path}' to '{new_path}'"); self.item_created.emit(item_type, new_path); return True, None
        except (OSError, shutil.Error) as e: log.error(f"Failed to duplicate '{path}': {e}", exc_info=True); return False, f"Failed to duplicate: {e}"

    def cut_item(self, path): self._internal_clipboard = {"operation": "cut", "path": path}
    def copy_item(self, path): self._internal_clipboard = {"operation": "copy", "path": path}
    def paste_item(self, dest_dir):
        op, src_path = self._internal_clipboard.get("operation"), self._internal_clipboard.get("path")
        if not op or not src_path or not os.path.exists(src_path): return False, "Nothing to paste."
        if not os.path.isdir(dest_dir): return False, "Paste destination must be a folder."
        dest_path = os.path.join(dest_dir, os.path.basename(src_path))
        if os.path.exists(dest_path): return False, f"'{os.path.basename(dest_path)}' already exists in the destination."
        try:
            item_type = 'folder' if os.path.isdir(src_path) else 'file'
            if op == "cut":
                shutil.move(src_path, dest_path); log.info(f"Moved '{src_path}' to '{dest_path}'")
                self.item_renamed.emit(item_type, src_path, dest_path); self._internal_clipboard = {"operation": None, "path": None}
            elif op == "copy":
                shutil.copytree(src_path, dest_path) if os.path.isdir(src_path) else shutil.copy2(src_path, dest_path)
                log.info(f"Copied '{src_path}' to '{dest_path}'"); self.item_created.emit(item_type, dest_path)
            return True, None
        except (OSError, shutil.Error) as e: log.error(f"Paste operation failed: {e}", exc_info=True); return False, f"Paste operation failed: {e}"

    def move_item(self, src_path, dest_dir):
        if not os.path.exists(src_path): return False, "Source path does not exist."
        if not os.path.isdir(dest_dir): return False, "Destination must be a folder."
        dest_path = os.path.join(dest_dir, os.path.basename(src_path))
        if os.path.normpath(src_path) == os.path.normpath(dest_path): return True, dest_path
        if os.path.exists(dest_path): return False, f"'{os.path.basename(src_path)}' already exists in the destination."
        if os.path.isdir(src_path) and os.path.normpath(dest_dir).startswith(os.path.normpath(src_path)): return False, "Cannot move a folder into its own subdirectory."
        try: item_type = 'folder' if os.path.isdir(src_path) else 'file'; shutil.move(src_path, dest_path); log.info(f"Moved '{src_path}' to '{dest_path}'"); self.item_renamed.emit(item_type, src_path, dest_path); return True, dest_path
        except (OSError, shutil.Error) as e: log.error(f"Move operation failed: {e}", exc_info=True); return False, f"Move operation failed: {e}"

    def copy_item_to_dest(self, src_path: str, dest_dir: str) -> Tuple[bool, Optional[str]]:
        """Copies a file or folder to a destination directory."""
        if not os.path.exists(src_path):
            return False, "Source path does not exist."
        if not os.path.isdir(dest_dir):
            return False, "Destination must be a folder."

        dest_path = os.path.join(dest_dir, os.path.basename(src_path))
        if os.path.exists(dest_path):
            return False, f"'{os.path.basename(src_path)}' already exists in the destination."

        try:
            item_type = 'folder' if os.path.isdir(src_path) else 'file'
            if item_type == 'folder':
                shutil.copytree(src_path, dest_path)
            else:  # it's a file
                shutil.copy2(src_path, dest_path)

            log.info(f"Copied '{src_path}' to '{dest_path}'")
            self.item_created.emit(item_type, dest_path)
            return True, dest_path
        except (OSError, shutil.Error) as e:
            log.error(f"Copy operation failed: {e}", exc_info=True)
            return False, f"Copy operation failed: {e}"

    def get_clipboard_status(self): return self._internal_clipboard.get("operation")
    def _add_to_recent_files(self, filepath):
        if not filepath: return
        recents = settings_manager.get("recent_files", []);
        if filepath in recents: recents.remove(filepath)
        recents.insert(0, filepath); max_files = settings_manager.get("max_recent_files", 10)
        settings_manager.set("recent_files", recents[:max_files]); self.recent_files_changed.emit()
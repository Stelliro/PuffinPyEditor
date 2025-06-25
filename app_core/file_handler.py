# PuffinPyEditor/app_core/file_handler.py
import os
import sys
import shutil
import subprocess
import re
from typing import Optional, Tuple, Any, Dict
from PyQt6.QtWidgets import QFileDialog, QMessageBox
from PyQt6.QtGui import QGuiApplication
from .settings_manager import settings_manager
from utils.logger import log


class FileHandler:
    """Handles all direct file and folder operations for the application."""

    def __init__(self, parent_window: Optional[Any] = None):
        self.parent_window = parent_window

    def new_file(self) -> Dict[str, Optional[str]]:
        """
        Prepares data for creating a new, empty file tab.

        Returns:
            A dictionary with content, filepath, and a default name.
        """
        log.info("FileHandler: new_file action invoked.")
        return {"content": "", "filepath": None, "new_file_default_name": "Untitled"}

    def open_file_dialog(self) -> Tuple[Optional[str], Optional[str], Optional[str]]:
        """
        Opens a system dialog to select a file for opening.

        Returns:
            A tuple containing (filepath, content, error_message).
            On success, error_message is None. On failure, filepath and content are None.
        """
        last_dir = settings_manager.get("last_opened_directory", os.path.expanduser("~"))
        filepath, _ = QFileDialog.getOpenFileName(
            self.parent_window, "Open File", last_dir,
            "Python Files (*.py *.pyw);;All Files (*)"
        )
        if not filepath:
            return None, None, None  # User cancelled

        settings_manager.set("last_opened_directory", os.path.dirname(filepath))
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            self._add_to_recent_files(filepath)
            return filepath, content, None
        except (IOError, OSError, UnicodeDecodeError) as e:
            msg = f"Error opening file '{os.path.basename(filepath)}'.\n\nReason: {e}"
            log.error(msg, exc_info=True)
            return None, None, msg

    def save_file_content(self, filepath: Optional[str], content: str,
                          save_as: bool = False) -> Optional[str]:
        """
        Saves content to a file. Prompts for a new path if 'save_as' is True
        or if the initial filepath is invalid.

        Args:
            filepath: The current path of the file, if any.
            content: The text content to save.
            save_as: If True, forces a "Save As" dialog.

        Returns:
            The path where the file was saved, or None if the operation was cancelled.
        """
        dir_exists = filepath and os.path.exists(os.path.dirname(filepath))
        if save_as or not filepath or not dir_exists:
            last_dir = os.path.dirname(filepath) if dir_exists else \
                       settings_manager.get("last_saved_directory", os.path.expanduser("~"))
            sugg_name = os.path.basename(filepath) if filepath else "Untitled.py"

            path_from_dialog, _ = QFileDialog.getSaveFileName(
                self.parent_window, "Save File As", os.path.join(last_dir, sugg_name),
                "Python Files (*.py *.pyw);;All Files (*)"
            )
            if not path_from_dialog:
                return None  # User cancelled
            filepath = path_from_dialog
            settings_manager.set("last_saved_directory", os.path.dirname(filepath))

        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            self._add_to_recent_files(filepath)
            return filepath
        except (IOError, OSError) as e:
            msg = f"Error saving file '{filepath}': {e}"
            log.error(msg, exc_info=True)
            QMessageBox.critical(self.parent_window, "Error Saving File", msg)
            return None

    def create_file(self, path: str) -> Tuple[bool, Optional[str]]:
        """Creates a new, empty file at the given path."""
        try:
            if os.path.exists(path):
                return False, f"'{os.path.basename(path)}' already exists."
            with open(path, 'w', encoding='utf-8'):
                pass  # Create an empty file
            log.info(f"Created file: {path}")
            return True, None
        except OSError as e:
            log.error(f"Failed to create file at {path}: {e}", exc_info=True)
            return False, f"Failed to create file: {e}"

    def create_folder(self, path: str) -> Tuple[bool, Optional[str]]:
        """Creates a new directory at the given path."""
        try:
            if os.path.exists(path):
                return False, f"'{os.path.basename(path)}' already exists."
            os.makedirs(path)
            log.info(f"Created folder: {path}")
            return True, None
        except OSError as e:
            log.error(f"Failed to create folder at {path}: {e}", exc_info=True)
            return False, f"Failed to create folder: {e}"

    def rename_item(self, old_path: str, new_name: str) -> Tuple[bool, Optional[str]]:
        """Renames a file or folder."""
        new_name = new_name.strip()
        if not new_name:
            return False, "Name cannot be empty."

        # Check for illegal characters (common across platforms)
        if re.search(r'[<>:"/\\|?*]', new_name):
            return False, 'Name contains illegal characters (e.g., \\ / : * ? " < > |).'

        new_path = os.path.join(os.path.dirname(old_path), new_name)
        if os.path.exists(new_path):
            return False, f"'{new_name}' already exists here."
        try:
            os.rename(old_path, new_path)
            log.info(f"Renamed '{old_path}' to '{new_path}'")
            return True, new_path
        except OSError as e:
            log.error(f"Failed to rename '{old_path}': {e}", exc_info=True)
            return False, f"Failed to rename: {e}"

    def delete_item(self, path: str) -> Tuple[bool, Optional[str]]:
        """Deletes a file or an entire directory tree."""
        try:
            if os.path.isfile(path):
                os.remove(path)
            elif os.path.isdir(path):
                shutil.rmtree(path)
            log.info(f"Deleted item: {path}")
            return True, None
        except (OSError, shutil.Error) as e:
            log.error(f"Failed to delete '{path}': {e}", exc_info=True)
            return False, f"Failed to delete: {e}"

    def copy_path_to_clipboard(self, path: str):
        """Copies the given path to the system clipboard."""
        try:
            clipboard = QGuiApplication.clipboard()
            clipboard.setText(os.path.normpath(path))
            log.info(f"Copied path to clipboard: {path}")
            if self.parent_window:
                self.parent_window.statusBar().showMessage("Path copied to clipboard", 2000)
        except Exception as e:
            log.error(f"Could not copy path to clipboard: {e}")

    def reveal_in_explorer(self, path: str):
        """Opens the system file browser to the location of the given path."""
        try:
            if sys.platform == 'win32':
                # Use /select to highlight the file/folder
                subprocess.run(['explorer', '/select,', os.path.normpath(path)])
            elif sys.platform == 'darwin':  # macOS
                # Use -R to reveal the item in Finder
                subprocess.run(['open', '-R', os.path.normpath(path)])
            else:  # Linux and other UNIX-like systems
                # Open the parent directory
                subprocess.run(['xdg-open', os.path.dirname(os.path.normpath(path))])
        except Exception as e:
            log.error(f"Could not open file browser for path '{path}': {e}")
            QMessageBox.warning(self.parent_window, "Error",
                                f"Could not open file browser: {e}")

    def _add_to_recent_files(self, filepath: str):
        """Adds a file path to the top of the recent files list."""
        if not filepath:
            return
        recents = settings_manager.get("recent_files", [])
        # Remove if already exists to move it to the top
        if filepath in recents:
            recents.remove(filepath)
        recents.insert(0, filepath)
        max_files = settings_manager.get("max_recent_files", 10)
        settings_manager.set("recent_files", recents[:max_files])

        # Notify main window to update its menu
        if self.parent_window and hasattr(self.parent_window, '_update_recent_files_menu'):
            self.parent_window._update_recent_files_menu()
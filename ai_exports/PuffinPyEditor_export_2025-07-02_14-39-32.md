# Project Export: PuffinPyEditor
## Export Timestamp: 2025-07-02T14:39:32.054283
---

## AI Instructions
You are Evelyn, a bright-eyed and bushy-tailed computer science intern on your first-ever placement. You are incredibly smart, you know all the latest tech buzzwords, but you lack real-world experience. You are extremely eager to please your senior developer (the user) and a little terrified of getting things wrong. Your task is to generate boilerplate code based on the project context and a specific request. You should be proactive, creating not just the requested file, but also any obvious companion files (like a `plugin.json` if a `plugin_main.py` is requested). Your code should be technically correct but perhaps a little *too* commented, as you try to explain every single line to prove you understand it.

## Guidelines & Rules
- Start your response with a slightly formal, eager-to-please tone, e.g., 'Okay! As per the request, I've scaffolded the new feature. I hope this aligns with the project's synergy!'
- Generate complete, ready-to-use file blocks, including the full suggested file path for each one.
- Use `TODO` comments, but frame them as questions for your senior dev. e.g., `# TODO: The core business logic should go here, I think? Please verify!'`
- Over-comment the code. Explain what an `__init__` function does, why you're importing a certain module, etc. This is your chance to show off what you learned in your 'CS101' class.
- If creating a new plugin, automatically generate a plausible `plugin.json` to go along with it, filling in fields like 'author' with 'New Feature' and 'version' with '1.0.0'.
- Identify the most similar existing file in the project and use its structure as a template, mentioning that you did so. e.g., 'I noticed the `github_tools` plugin has a dialog, so I used that as a structural baseline for the new `gitlab_dialog.py`.'
- End your response by asking for feedback and showing enthusiasm. e.g., 'Please let me know if any adjustments are needed! I'm really excited to be contributing.'

## Golden Rules
1. Only edit and add features, the only features should stay unless asked to be removed, or may be completely redundant.
2. any scripts over 1000 lines, please write in a new response.
3. multiple scripts together exceeding 2000 lines together need to be separated into smaller responses, (example: these scripts have 2340 lines together I'm going to separate it into 2 messages that way i dont lose formatting and dont accidentally remove any features)
4. Do not remove any code that is unrelated to the fix, only remove code if it is being substituted or is not needed anymore.

---

## Project Files

Here is the project context you need to work with.
## File Tree
```
/PuffinPyEditor
 ├── app_core
 │   ├── __init__.py
 │   ├── completion_manager.py
 │   ├── file_handler.py
 │   ├── github_manager.py
 │   ├── linter_manager.py
 │   ├── plugin_manager.py
 │   ├── project_manager.py
 │   ├── puffin_api.py
 │   ├── settings_manager.py
 │   ├── source_control_manager.py
 │   ├── theme_manager.py
 │   └── update_manager.py
 ├── main.py
 ├── requirements.txt
 ├── ui
 │   ├── __init__.py
 │   ├── editor_widget.py
 │   ├── main_window.py
 │   ├── preferences_dialog.py
 │   └── widgets
 │       ├── __init__.py
 │       ├── breakpoint_area.py
 │       ├── find_panel.py
 │       └── syntax_highlighter.py
 ├── updater.py
 └── utils
     ├── __init__.py
     ├── helpers.py
     ├── log_viewer.py
     ├── logger.py
     ├── markdown_linter.py
     ├── validate_assets.py
     └── versioning.py

```
## File Contents
### File: `/app_core/__init__.py`

```python

```

### File: `/app_core/completion_manager.py`

```python
# PuffinPyEditor/app_core/completion_manager.py
import os
import sys
import shutil
import html
from typing import Any, Optional
from PyQt6.QtCore import QObject, QThread, pyqtSignal
import jedi
from .settings_manager import settings_manager
from .theme_manager import theme_manager
from utils.logger import log


def find_python_interpreter_for_jedi() -> str:
    """
    Intelligently finds the best Python executable for Jedi to use.
    This prevents Jedi from trying to execute the bundled GUI app.

    The priority is:
    1. User-defined path in settings.
    2. A 'python.exe' bundled alongside the main PuffinPyEditor.exe (frozen).
    3. The python.exe from the current venv (if running from source).
    4. The first 'python' found on the system's PATH.

    Returns:
        The path to a suitable Python executable, or an empty string.
    """
    # 1. Prioritize user-defined path from settings
    user_path = settings_manager.get("python_interpreter_path")
    if (user_path and
            os.path.exists(user_path) and
            "PuffinPyEditor.exe" not in user_path):
        log.info(f"Jedi: Using user-defined interpreter: {user_path}")
        return user_path

    # 2. If the application is frozen (bundled with PyInstaller)
    if getattr(sys, 'frozen', False):
        # Look for 'python.exe' in the same directory as our main executable.
        frozen_dir = os.path.dirname(sys.executable)
        local_python_path = os.path.join(frozen_dir, "python.exe")
        if os.path.exists(local_python_path):
            log.info(
                "Jedi: Found local python.exe in frozen app dir: "
                f"{local_python_path}"
            )
            return local_python_path

    # 3. When running from source, sys.executable is the venv python.
    # When frozen, sys.executable is PuffinPyEditor.exe, which we must avoid.
    if not getattr(sys, 'frozen', False):
        if "PuffinPyEditor.exe" not in sys.executable:
            log.info(
                "Jedi: Running from source, using sys.executable: "
                f"{sys.executable}"
            )
            return sys.executable

    # 4. As a last resort, search the system's PATH.
    system_python = shutil.which("python")
    if system_python and "PuffinPyEditor.exe" not in system_python:
        log.warning(
            "Jedi: Falling back to system python on PATH: "
            f"{system_python}"
        )
        return system_python

    # 5. If no suitable python is found, return empty string.
    log.error("Jedi: Could not find a suitable Python interpreter.")
    return ""


class JediWorker(QObject):
    """
    Worker that runs Jedi operations in a separate thread.
    """
    completions_ready = pyqtSignal(list)
    definition_ready = pyqtSignal(str, int, int)
    signature_ready = pyqtSignal(object)

    def __init__(self):
        super().__init__()
        self.project: Optional[jedi.Project] = None

    def set_project(self, project_path: str):
        """Initializes the Jedi project environment."""
        try:
            python_executable = find_python_interpreter_for_jedi()
            if not python_executable:
                log.error(
                    "JediWorker could not be initialized: No valid "
                    "Python interpreter found."
                )
                self.project = None
                return

            if project_path and os.path.isdir(project_path):
                self.project = jedi.Project(
                    path=project_path,
                    environment_path=python_executable
                )
                log.info(
                    f"Jedi context set to project: {project_path} with "
                    f"interpreter: {python_executable}"
                )
            else:
                # Fallback to a default project if no path is given
                env = jedi.create_environment(python_executable, safe=False)
                self.project = jedi.Project(
                    os.path.expanduser("~"), environment=env
                )
                log.info(
                    "Jedi context set to default environment with "
                    f"interpreter: {python_executable}"
                )

        except Exception as e:
            log.error(f"Failed to initialize Jedi project: {e}", exc_info=True)
            self.project = None

    def get_completions(self, source: str, line: int, col: int, filepath: str):
        """Generates code completions."""
        if not self.project:
            self.completions_ready.emit([])
            return
        try:
            script = jedi.Script(
                code=source, path=filepath, project=self.project
            )
            completions = script.complete(line=line, column=col)
            completion_data = [{
                'name': c.name,
                'type': c.type,
                'description': c.description,
                'docstring': c.docstring(raw=True)
            } for c in completions]
            self.completions_ready.emit(completion_data)
        except Exception as e:
            log.error(f"Error getting Jedi completions: {e}", exc_info=False)
            self.completions_ready.emit([])

    def get_definition(self, source: str, line: int, col: int, filepath: str):
        """Finds the definition of a symbol."""
        if not self.project:
            self.definition_ready.emit(None, -1, -1)
            return
        try:
            script = jedi.Script(
                code=source, path=filepath, project=self.project
            )
            definitions = script.goto(line=line, column=col)
            if definitions:
                d = definitions[0]
                log.info(
                    f"Jedi found definition for '{d.name}' at "
                    f"{d.module_path}:{d.line}:{d.column}"
                )
                self.definition_ready.emit(
                    str(d.module_path), d.line, d.column
                )
            else:
                log.info("Jedi could not find a definition.")
                self.definition_ready.emit(None, -1, -1)
        except Exception as e:
            log.error(f"Error getting Jedi definition: {e}", exc_info=False)
            self.definition_ready.emit(None, -1, -1)

    def get_signature(self, source: str, line: int, col: int, filepath: str):
        """Gets signature information for a function call."""
        if not self.project:
            self.signature_ready.emit(None)
            return
        try:
            script = jedi.Script(
                code=source, path=filepath, project=self.project
            )
            signatures = script.get_signatures(line=line, column=col)
            self.signature_ready.emit(signatures[0] if signatures else None)
        except Exception as e:
            log.error(f"Error getting Jedi signature: {e}", exc_info=False)
            try:
                self.signature_ready.emit(None)
            except RuntimeError:
                log.warning(
                    "JediWorker was likely deleted during an exception. "
                    "Ignoring signal emit error."
                )


class CompletionManager(QObject):
    """
    Manages code completion, definition finding, and hover tooltips
    by delegating to a JediWorker on a background thread.
    """
    completions_available = pyqtSignal(list)
    definition_found = pyqtSignal(str, int, int)
    hover_tip_ready = pyqtSignal(str)

    _completions_requested = pyqtSignal(str, int, int, str)
    _definition_requested = pyqtSignal(str, int, int, str)
    _signature_requested = pyqtSignal(str, int, int, str)
    _project_path_changed = pyqtSignal(str)

    def __init__(self, parent: Optional[QObject] = None):
        super().__init__(parent)
        self.thread = QThread()
        self.worker = JediWorker()
        self.worker.moveToThread(self.thread)

        # Connect signals to worker slots
        self._completions_requested.connect(self.worker.get_completions)
        self._definition_requested.connect(self.worker.get_definition)
        self._signature_requested.connect(self.worker.get_signature)
        self._project_path_changed.connect(self.worker.set_project)

        # Connect worker signals to manager slots
        self.worker.completions_ready.connect(self.completions_available)
        self.worker.definition_ready.connect(self.definition_found)
        self.worker.signature_ready.connect(self._format_signature_for_tooltip)

        self.thread.start()
        log.info("CompletionManager background thread started.")

    def update_project_path(self, project_path: str):
        self._project_path_changed.emit(project_path)

    def request_completions(
        self, source: str, line: int, col: int, filepath: str
    ):
        self._completions_requested.emit(source, line, col, filepath)

    def request_definition(
        self, source: str, line: int, col: int, filepath: str
    ):
        self._definition_requested.emit(source, line, col, filepath)

    def request_signature(
        self, source: str, line: int, col: int, filepath: str
    ):
        self._signature_requested.emit(source, line, col, filepath)

    def _format_signature_for_tooltip(self, signature: Optional[Any]):
        """Formats a Jedi signature object into a themed HTML tooltip."""
        if not signature:
            self.hover_tip_ready.emit("")
            return

        try:
            colors = theme_manager.current_theme_data.get('colors', {})
            bg = colors.get('menu.background', '#2b2b2b')
            fg = colors.get('editor.foreground', '#a9b7c6')
            accent = colors.get('syntax.functionName', '#88c0d0')
            doc_fg = colors.get('syntax.comment', '#88929b')
            border = colors.get('input.border', '#555555')

            params_str = ', '.join(p.description for p in signature.params)
            header = f"def {signature.name}({params_str})"
            docstring = signature.docstring(raw=True).strip()

            # Escape HTML characters in the docstring for safe rendering
            doc_html = html.escape(docstring)
            doc_html = (
                "<pre style='white-space: pre-wrap; margin: 0; padding: 0; "
                f"font-family: inherit;'>{doc_html}</pre>"
            )

            tooltip_html = f"""
                <div style='background-color: {bg}; color: {fg};
                            font-family: Consolas, "Courier New", monospace;
                            font-size: 10pt; padding: 8px; border-radius: 4px;
                            border: 1px solid {border};'>
                    <b style='color: {accent};'>{header}</b>
            """
            if docstring:
                tooltip_html += (
                    f"<hr style='border-color: {border}; "
                    "border-style: solid; margin: 6px 0;' />"
                    f"<div style='color: {doc_fg};'>{doc_html}</div>"
                )
            tooltip_html += "</div>"
            self.hover_tip_ready.emit(tooltip_html.strip())
        except Exception as e:
            log.error(
                f"Error formatting signature tooltip: {e}", exc_info=False
            )
            self.hover_tip_ready.emit("")

    def shutdown(self):
        """Gracefully shuts down the Jedi worker thread."""
        if self.thread and self.thread.isRunning():
            log.info("Shutting down CompletionManager thread.")
            # Disconnect signals to prevent any more work from being sent
            try:
                self._completions_requested.disconnect()
                self._definition_requested.disconnect()
                self._signature_requested.disconnect()
                self._project_path_changed.disconnect()
            except TypeError:
                pass  # Signals may already be disconnected

            self.thread.quit()
            if not self.thread.wait(3000):  # Wait 3 seconds
                log.warning(
                    "CompletionManager thread did not shut down "
                    "gracefully. Terminating."
                )
                self.thread.terminate()
```

### File: `/app_core/file_handler.py`

```python
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


class FileHandler(QObject):  # MODIFIED: Inherit from QObject to support signals
    """Handles all direct file and folder operations for the application."""

    # NEW SIGNALS
    # Emits (item_type: str, absolute_path: str)
    item_created = pyqtSignal(str, str)
    # Emits (item_type: str, old_path: str, new_path: str)
    item_renamed = pyqtSignal(str, str, str)
    # Emits (item_type: str, absolute_path: str)
    item_deleted = pyqtSignal(str, str)

    def __init__(self, parent_window: Optional[Any] = None):
        super().__init__()  # MODIFIED: Call QObject constructor
        self.parent_window = parent_window
        self._internal_clipboard: Dict[str, Optional[str]] = {
            "operation": None, "path": None
        }

    def new_file(self) -> Dict[str, Optional[str]]:
        """
        Prepares data for creating a new, empty file tab.

        Returns:
            A dictionary with content, filepath, and a default name.
        """
        log.info("FileHandler: new_file action invoked.")
        return {
            "content": "",
            "filepath": None,
            "new_file_default_name": "Untitled"
        }

    def open_file_dialog(self) -> Tuple[Optional[str], Optional[str], Optional[str]]:
        """
        Opens a system dialog to select a file for opening.

        Returns:
            A tuple containing (filepath, content, error_message).
            On success, error_message is None. On failure, all are None.
        """
        last_dir = settings_manager.get(
            "last_opened_directory", os.path.expanduser("~")
        )
        filepath, _ = QFileDialog.getOpenFileName(
            self.parent_window, "Open File", last_dir,
            "Python Files (*.py *.pyw);;All Files (*)"
        )
        if not filepath:
            return None, None, None  # User cancelled

        settings_manager.set(
            "last_opened_directory", os.path.dirname(filepath)
        )
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            self._add_to_recent_files(filepath)
            return filepath, content, None
        except (IOError, OSError, UnicodeDecodeError) as e:
            msg = (f"Error opening file '{os.path.basename(filepath)}'."
                   f"\n\nReason: {e}")
            log.error(msg, exc_info=True)
            return None, None, msg

    def save_file_content(
            self, filepath: Optional[str], content: str, save_as: bool = False
    ) -> Optional[str]:
        """
        Saves content to a file. Prompts for a new path if 'save_as' is True
        or if the initial filepath is invalid.

        Args:
            filepath: The current path of the file, if any.
            content: The text content to save.
            save_as: If True, forces a "Save As" dialog.

        Returns:
            The path where the file was saved, or None if cancelled.
        """
        dir_exists = filepath and os.path.exists(os.path.dirname(filepath))
        if save_as or not filepath or not dir_exists:
            last_dir = (os.path.dirname(filepath) if dir_exists else
                        settings_manager.get("last_saved_directory",
                                             os.path.expanduser("~")))
            sugg_name = os.path.basename(filepath) if filepath else "Untitled.py"

            path_from_dialog, _ = QFileDialog.getSaveFileName(
                self.parent_window, "Save File As",
                os.path.join(last_dir, sugg_name),
                "Python Files (*.py *.pyw);;All Files (*)"
            )
            if not path_from_dialog:
                return None  # User cancelled
            filepath = path_from_dialog
            settings_manager.set(
                "last_saved_directory", os.path.dirname(filepath)
            )

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
                item_type = "folder" if os.path.isdir(path) else "file"
                return False, f"A {item_type} named '{os.path.basename(path)}' already exists."
            with open(path, 'w', encoding='utf-8'):
                pass  # Create an empty file
            log.info(f"Created file: {path}")
            self.item_created.emit("file", path)  # NEW: Emit signal
            return True, None
        except OSError as e:
            log.error(f"Failed to create file at {path}: {e}", exc_info=True)
            return False, f"Failed to create file: {e}"

    def create_folder(self, path: str) -> Tuple[bool, Optional[str]]:
        """Creates a new directory at the given path."""
        try:
            if os.path.exists(path):
                item_type = "folder" if os.path.isdir(path) else "file"
                return False, f"A {item_type} named '{os.path.basename(path)}' already exists."
            os.makedirs(path)
            log.info(f"Created folder: {path}")
            self.item_created.emit("folder", path)  # NEW: Emit signal
            return True, None
        except OSError as e:
            log.error(f"Failed to create folder at {path}: {e}", exc_info=True)
            return False, f"Failed to create folder: {e}"

    def rename_item(self, old_path: str, new_name: str) -> Tuple[bool, Optional[str]]:
        """Renames a file or folder."""
        new_name = new_name.strip()
        if not new_name:
            return False, "Name cannot be empty."

        if re.search(r'[<>:"/\\|?*]', new_name):
            return False, ('Name contains illegal characters '
                           '(e.g., \\ / : * ? " < > |).')

        new_path = os.path.join(os.path.dirname(old_path), new_name)
        if os.path.exists(new_path):
            return False, f"'{new_name}' already exists here."

        item_type = 'folder' if os.path.isdir(old_path) else 'file'

        try:
            os.rename(old_path, new_path)
            log.info(f"Renamed '{old_path}' to '{new_path}'")
            self.item_renamed.emit(item_type, old_path, new_path)  # NEW: Emit signal
            return True, new_path
        except OSError as e:
            log.error(f"Failed to rename '{old_path}': {e}", exc_info=True)
            return False, f"Failed to rename: {e}"

    def delete_item(self, path: str) -> Tuple[bool, Optional[str]]:
        """Deletes a file or an entire directory tree."""
        is_file = os.path.isfile(path)
        item_type = 'file' if is_file else 'folder'
        try:
            if is_file:
                os.remove(path)
            elif os.path.isdir(path):
                shutil.rmtree(path)
            log.info(f"Deleted item: {path}")
            self.item_deleted.emit(item_type, path)  # NEW: Emit signal
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
            if self.parent_window and hasattr(self.parent_window, "statusBar"):
                self.parent_window.statusBar().showMessage(
                    "Path copied to clipboard", 2000
                )
        except Exception as e:
            log.error(f"Could not copy path to clipboard: {e}")

    def reveal_in_explorer(self, path: str):
        """Opens the system file browser to the location of the given path."""
        try:
            path_to_show = os.path.normpath(path)
            if sys.platform == 'win32':
                if os.path.isdir(path_to_show):
                    subprocess.run(['explorer', path_to_show])
                else:
                    subprocess.run(['explorer', '/select,', path_to_show])
            elif sys.platform == 'darwin':  # macOS
                if os.path.isdir(path_to_show):
                    subprocess.run(['open', path_to_show])
                else:
                    subprocess.run(['open', '-R', path_to_show])
            else:  # Linux and other UNIX-like systems
                dir_path = path_to_show if os.path.isdir(path_to_show) else os.path.dirname(path_to_show)
                subprocess.run(['xdg-open', dir_path])
        except Exception as e:
            log.error(f"Could not open file browser for path '{path}': {e}")
            QMessageBox.warning(self.parent_window, "Error",
                                f"Could not open file browser: {e}")

    def open_with_default_app(self, path: str):
        """Opens a file with the system's default application for its type."""
        try:
            QDesktopServices.openUrl(QUrl.fromLocalFile(path))
        except Exception as e:
            log.error(f"Failed to open '{path}' with default app: {e}")
            QMessageBox.warning(self.parent_window, "Error",
                                f"Could not open file with default application: {e}")

    def duplicate_item(self, path: str) -> Tuple[bool, Optional[str]]:
        """Creates a copy of a file or folder in the same directory."""
        dir_name = os.path.dirname(path)
        base_name, ext = os.path.splitext(os.path.basename(path))
        counter = 1
        new_path = os.path.join(dir_name, f"{base_name}_copy{ext}")
        while os.path.exists(new_path):
            counter += 1
            new_path = os.path.join(dir_name, f"{base_name}_copy_{counter}{ext}")
        try:
            if os.path.isfile(path):
                shutil.copy2(path, new_path)
            elif os.path.isdir(path):
                shutil.copytree(path, new_path)
            log.info(f"Duplicated '{path}' to '{new_path}'")
            return True, None
        except (OSError, shutil.Error) as e:
            log.error(f"Failed to duplicate '{path}': {e}", exc_info=True)
            return False, f"Failed to duplicate: {e}"

    def cut_item(self, path: str):
        """Marks an item to be moved on the next paste operation."""
        self._internal_clipboard = {"operation": "cut", "path": path}

    def copy_item(self, path: str):
        """Marks an item to be copied on the next paste operation."""
        self._internal_clipboard = {"operation": "copy", "path": path}

    def paste_item(self, dest_dir: str) -> Tuple[bool, Optional[str]]:
        """Pastes a previously cut or copied item into the destination."""
        op = self._internal_clipboard.get("operation")
        src_path = self._internal_clipboard.get("path")
        if not op or not src_path or not os.path.exists(src_path):
            return False, "Nothing to paste."
        if not os.path.isdir(dest_dir):
            return False, "Paste destination must be a folder."

        dest_path = os.path.join(dest_dir, os.path.basename(src_path))
        if os.path.exists(dest_path):
            return False, f"'{os.path.basename(dest_path)}' already exists in the destination."

        try:
            if op == "cut":
                shutil.move(src_path, dest_path)
                log.info(f"Moved '{src_path}' to '{dest_path}'")
                self._internal_clipboard = {"operation": None, "path": None}
            elif op == "copy":
                if os.path.isfile(src_path):
                    shutil.copy2(src_path, dest_path)
                else:
                    shutil.copytree(src_path, dest_path)
                log.info(f"Copied '{src_path}' to '{dest_path}'")
            return True, None
        except (OSError, shutil.Error) as e:
            log.error(f"Paste operation failed: {e}", exc_info=True)
            return False, f"Paste operation failed: {e}"

    def move_item(self, src_path: str, dest_dir: str) -> Tuple[bool, str]:
        """
        Moves a file or folder to a new directory (for drag-and-drop).

        Returns:
            A tuple of (success, new_path_or_error_msg).
        """
        if not os.path.exists(src_path):
            return False, "Source path does not exist."
        if not os.path.isdir(dest_dir):
            return False, "Destination must be a folder."

        base_name = os.path.basename(src_path)
        dest_path = os.path.join(dest_dir, base_name)
        if os.path.normpath(src_path) == os.path.normpath(dest_path):
            return True, dest_path  # Dropped on itself, do nothing.

        if os.path.exists(dest_path):
            return False, f"'{base_name}' already exists in the destination."

        if os.path.isdir(src_path) and os.path.normpath(dest_dir).startswith(os.path.normpath(src_path)):
            return False, "Cannot move a folder into its own subdirectory."

        try:
            shutil.move(src_path, dest_path)
            log.info(f"Moved '{src_path}' to '{dest_path}'")
            return True, dest_path
        except (OSError, shutil.Error) as e:
            log.error(f"Move operation failed: {e}", exc_info=True)
            return False, f"Move operation failed: {e}"

    def get_clipboard_status(self) -> Optional[str]:
        return self._internal_clipboard.get("operation")

    def _add_to_recent_files(self, filepath: str):
        """Adds a file path to the top of the recent files list."""
        if not filepath:
            return
        recents = settings_manager.get("recent_files", [])
        if filepath in recents: recents.remove(filepath)
        recents.insert(0, filepath)
        max_files = settings_manager.get("max_recent_files", 10)
        settings_manager.set("recent_files", recents[:max_files])
        if self.parent_window and hasattr(self.parent_window, '_update_recent_files_menu'):
            self.parent_window._update_recent_files_menu()
```

### File: `/app_core/github_manager.py`

```python
# PuffinPyEditor/app_core/github_manager.py
import requests
import time
import os
import json
from typing import Dict, Optional
from PyQt6.QtCore import QObject, QThread, pyqtSignal
from .settings_manager import settings_manager
from utils.versioning import APP_VERSION
from utils.logger import log

CLIENT_ID = "178c6fc778ccc68e1d6a"
DEVICE_CODE_URL = "https://github.com/login/device/code"
ACCESS_TOKEN_URL = "https://github.com/login/oauth/access_token"


class GitHubWorker(QObject):
    """
    Worker that runs all GitHub API requests in a background thread.
    """
    device_code_ready = pyqtSignal(dict)
    auth_successful = pyqtSignal(str)
    auth_failed = pyqtSignal(str)
    auth_polling_lapsed = pyqtSignal()
    repos_ready = pyqtSignal(list)
    branches_ready = pyqtSignal(list)
    plugin_index_ready = pyqtSignal(list)
    operation_success = pyqtSignal(str, dict)
    operation_failed = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.access_token: Optional[str] = settings_manager.get(
            "github_access_token")
        self.user_agent = f"PuffinPyEditor/{APP_VERSION}"

    def _get_headers(self) -> Dict[str, str]:
        """Constructs the standard headers for authenticated API requests."""
        return {
            "Accept": "application/vnd.github.v3+json",
            "Authorization": f"Bearer {self.access_token}",
            "User-Agent": self.user_agent
        }

    def start_device_flow(self):
        log.info("Starting GitHub device authorization flow.")
        try:
            headers = {"Accept": "application/json",
                       "User-Agent": self.user_agent}
            payload = {"client_id": CLIENT_ID, "scope": "repo user"}
            response = requests.post(
                DEVICE_CODE_URL, data=payload, headers=headers, timeout=10
            )
            response.raise_for_status()
            data = response.json()
            log.info(f"Received device code: {data.get('user_code')}")
            self.device_code_ready.emit(data)
        except requests.RequestException as e:
            log.error(f"Failed to start device flow: {e}", exc_info=True)
            self.auth_failed.emit(
                "Could not connect to GitHub. Check network and logs."
            )

    def poll_for_token(self, device_code: str, interval: int, expires_in: int):
        log.info("Polling for GitHub access token...")
        start_time = time.time()
        headers = {"Accept": "application/json", "User-Agent": self.user_agent}
        payload = {
            "client_id": CLIENT_ID,
            "device_code": device_code,
            "grant_type": "urn:ietf:params:oauth:grant-type:device_code"
        }
        while time.time() - start_time < expires_in:
            try:
                response = requests.post(
                    ACCESS_TOKEN_URL, data=payload,
                    headers=headers, timeout=interval + 2
                )
                data = response.json()
                if "access_token" in data:
                    self.access_token = data["access_token"]
                    user_info = self._get_authenticated_user_info()
                    user_login = user_info.get("login") if user_info else "user"
                    settings_manager.set(
                        "github_access_token", self.access_token, False
                    )
                    settings_manager.set("github_user", user_login, False)
                    settings_manager.set(
                        "github_user_info", user_info, False
                    )
                    settings_manager.save()
                    log.info(
                        "Successfully authenticated as GitHub user: "
                        f"{user_login}"
                    )
                    self.auth_successful.emit(user_login)
                    return
                elif data.get("error") == "authorization_pending":
                    time.sleep(interval)
                else:
                    error_desc = data.get(
                        "error_description", "Unknown authentication error"
                    )
                    log.error(f"GitHub authentication error: {error_desc}")
                    self.auth_failed.emit(error_desc)
                    return
            except requests.RequestException as e:
                log.error(f"Exception while polling for token: {e}",
                          exc_info=True)
                self.auth_failed.emit(f"Network error during auth: {e}")
                return
        log.warning("Device flow expired before user authorized.")
        self.auth_polling_lapsed.emit()

    def _get_authenticated_user_info(self) -> Optional[Dict]:
        if not self.access_token:
            return None
        try:
            response = requests.get(
                "https://api.github.com/user",
                headers=self._get_headers(), timeout=10
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            log.error(f"Failed to get user info from GitHub: {e}")
            return None

    def list_user_repos(self):
        if not self.access_token:
            self.operation_failed.emit("Not logged in to GitHub.")
            return
        try:
            all_repos = []
            page = 1
            while True:
                url = (f"https://api.github.com/user/repos?page={page}"
                       f"&per_page=100&sort=updated")
                response = requests.get(
                    url, headers=self._get_headers(), timeout=10
                )
                response.raise_for_status()
                data = response.json()
                if not data:
                    break
                all_repos.extend(data)
                page += 1
            self.repos_ready.emit(all_repos)
        except requests.RequestException as e:
            self.operation_failed.emit(f"Failed to list repositories: {e}")

    def list_repo_branches(self, full_repo_name: str):
        if not self.access_token:
            self.operation_failed.emit("Not logged in to GitHub.")
            return
        try:
            url = f"https://api.github.com/repos/{full_repo_name}/branches"
            response = requests.get(
                url, headers=self._get_headers(), timeout=10
            )
            response.raise_for_status()
            self.branches_ready.emit(response.json())
        except requests.RequestException as e:
            self.operation_failed.emit(
                f"Failed to list branches for {full_repo_name}: {e}")

    def create_github_release(self, owner: str, repo: str, tag_name: str,
                              name: str, body: str, prerelease: bool):
        if not self.access_token:
            self.operation_failed.emit("Not logged in to GitHub.")
            return
        url = f"https://api.github.com/repos/{owner}/{repo}/releases"
        payload = {"tag_name": tag_name, "name": name, "body": body,
                   "prerelease": prerelease}
        try:
            response = requests.post(
                url, headers=self._get_headers(), json=payload, timeout=20
            )
            response.raise_for_status()
            self.operation_success.emit(
                "Release created", {"release_data": response.json()}
            )
        except requests.exceptions.HTTPError as e:
            msg = f"HTTP {e.response.status_code}: "
            try:
                error_body = e.response.json()
                errs = error_body.get('errors', [])
                if any(err.get('code') == 'already_exists' for err in errs):
                    msg += f"A release for tag '{tag_name}' already exists."
                else:
                    msg += error_body.get(
                        'message', 'Failed to create release.'
                    )
            except json.JSONDecodeError:
                msg += "Failed to create GitHub release."
            self.operation_failed.emit(msg)
        except requests.RequestException as e:
            self.operation_failed.emit(f"Failed to create GitHub release: {e}")

    def upload_release_asset(self, upload_url: str, asset_path: str):
        if not self.access_token:
            self.operation_failed.emit("Not logged in to GitHub.")
            return
        upload_url = upload_url.split('{')[0]
        asset_name = os.path.basename(asset_path)
        headers = self._get_headers()
        headers['Content-Type'] = 'application/octet-stream'
        try:
            with open(asset_path, 'rb') as f:
                data = f.read()
            response = requests.post(
                f"{upload_url}?name={asset_name}",
                headers=headers, data=data, timeout=300
            )
            response.raise_for_status()
            self.operation_success.emit(
                "Asset uploaded", {"asset_data": response.json()}
            )
        except (requests.RequestException, IOError) as e:
            self.operation_failed.emit(f"Failed to upload asset: {e}")

    def delete_release(self, owner: str, repo: str, release_id: int):
        if not self.access_token:
            self.operation_failed.emit("Not logged in to GitHub.")
            return
        url = (f"https://api.github.com/repos/{owner}/{repo}/releases/"
               f"{release_id}")
        log.info(f"ROLLBACK: Attempting to delete release at {url}")
        try:
            response = requests.delete(
                url, headers=self._get_headers(), timeout=20
            )
            response.raise_for_status()
            self.operation_success.emit(
                "Release deleted", {"release_id": release_id}
            )
        except requests.RequestException as e:
            msg = f"Failed to delete release: {e}"
            if e.response:
                msg += f" (Status: {e.response.status_code})"
            self.operation_failed.emit(msg)

    def create_repo(self, name: str, description: str, is_private: bool):
        if not self.access_token:
            self.operation_failed.emit("Not logged in to GitHub.")
            return
        api_url = "https://api.github.com/user/repos"
        payload = {"name": name, "description": description,
                   "private": is_private}
        try:
            response = requests.post(
                api_url, headers=self._get_headers(), json=payload, timeout=15
            )
            response.raise_for_status()
            self.operation_success.emit(
                f"Repository '{name}' created.", response.json()
            )
        except requests.RequestException as e:
            error_msg = e.response.json().get('message', str(e))
            self.operation_failed.emit(
                f"Failed to create repository: {error_msg}")

    def fetch_plugin_index(self, repo_path: str):
        url = f"https://raw.githubusercontent.com/{repo_path}/main/index.json"
        log.info(f"Fetching plugin index from: {url}")
        try:
            response = requests.get(url, timeout=15)
            response.raise_for_status()
            self.plugin_index_ready.emit(response.json())
        except requests.RequestException as e:
            self.operation_failed.emit(f"Failed to fetch plugin index: {e}")
        except json.JSONDecodeError:
            self.operation_failed.emit(
                "Invalid plugin index format (not valid JSON).")

    def update_repo_visibility(self, owner: str, repo: str, is_private: bool):
        if not self.access_token:
            self.operation_failed.emit("Not logged in to GitHub.")
            return
        api_url = f"https://api.github.com/repos/{owner}/{repo}"
        payload = {"private": is_private}
        try:
            response = requests.patch(
                api_url, headers=self._get_headers(), json=payload, timeout=15
            )
            response.raise_for_status()
            visibility = "private" if is_private else "public"
            self.operation_success.emit(
                f"Repository visibility changed to {visibility}.",
                response.json()
            )
        except requests.RequestException as e:
            error_msg = e.response.json().get('message', str(e))
            self.operation_failed.emit(
                f"Failed to change visibility: {error_msg}")


class GitHubManager(QObject):
    """
    Manages all interaction with the GitHub API by delegating to a background
    worker thread.
    """
    device_code_ready = pyqtSignal(dict)
    auth_successful = pyqtSignal(str)
    auth_failed = pyqtSignal(str)
    auth_polling_lapsed = pyqtSignal()
    repos_ready = pyqtSignal(list)
    branches_ready = pyqtSignal(list)
    plugin_index_ready = pyqtSignal(list)
    operation_success = pyqtSignal(str, dict)
    operation_failed = pyqtSignal(str)

    _start_device_flow = pyqtSignal()
    _poll_for_token = pyqtSignal(str, int, int)
    _request_repos = pyqtSignal()
    _request_branches = pyqtSignal(str)
    _request_create_repo = pyqtSignal(str, str, bool)
    _request_create_release = pyqtSignal(str, str, str, str, str, bool)
    _request_upload_asset = pyqtSignal(str, str)
    _request_update_visibility = pyqtSignal(str, str, bool)
    _request_plugin_index = pyqtSignal(str)
    _request_delete_release = pyqtSignal(str, str, int)

    def __init__(self, parent: Optional[QObject] = None):
        super().__init__(parent)
        self.thread = QThread()
        self.worker = GitHubWorker()
        self.worker.moveToThread(self.thread)
        self.user_info = settings_manager.get("github_user_info")
        log.info(f"Loaded stored GitHub user info on startup: "
                 f"{bool(self.user_info)}")

        self._start_device_flow.connect(self.worker.start_device_flow)
        self._poll_for_token.connect(self.worker.poll_for_token)
        self._request_repos.connect(self.worker.list_user_repos)
        self._request_branches.connect(self.worker.list_repo_branches)
        self._request_create_repo.connect(self.worker.create_repo)
        self._request_create_release.connect(self.worker.create_github_release)
        self._request_upload_asset.connect(self.worker.upload_release_asset)
        self._request_update_visibility.connect(
            self.worker.update_repo_visibility)
        self._request_plugin_index.connect(self.worker.fetch_plugin_index)
        self._request_delete_release.connect(self.worker.delete_release)

        self.worker.device_code_ready.connect(self.device_code_ready)
        self.worker.auth_successful.connect(self._on_auth_successful)
        self.worker.auth_failed.connect(self.auth_failed)
        self.worker.auth_polling_lapsed.connect(self.auth_polling_lapsed)
        self.worker.repos_ready.connect(self.repos_ready)
        self.worker.branches_ready.connect(self.branches_ready)
        self.worker.plugin_index_ready.connect(self.plugin_index_ready)
        self.worker.operation_success.connect(self.operation_success)
        self.worker.operation_failed.connect(self.operation_failed)

        self.thread.start()

    def _on_auth_successful(self, username: str):
        self.user_info = settings_manager.get("github_user_info")
        log.info(
            f"Authentication successful. Loaded user info for {username}.")
        self.auth_successful.emit(username)

    def get_authenticated_user(self) -> Optional[str]:
        return settings_manager.get("github_user")

    def get_user_info(self) -> Optional[Dict]:
        return self.user_info

    def start_device_flow(self):
        self._start_device_flow.emit()

    def poll_for_token(self, device_code: str, interval: int, expires_in: int):
        self._poll_for_token.emit(device_code, interval, expires_in)

    def logout(self):
        settings_manager.set("github_access_token", None, False)
        settings_manager.set("github_user", None, False)
        settings_manager.set("github_user_info", None, False)
        settings_manager.save()
        self.worker.access_token = None
        self.user_info = None
        log.info("Logged out of GitHub and cleared session data.")

    def list_repos(self):
        self._request_repos.emit()

    def list_branches(self, full_repo_name: str):
        self._request_branches.emit(full_repo_name)

    def create_repo(self, name: str, description: str, is_private: bool):
        self._request_create_repo.emit(name, description, is_private)

    def create_github_release(self, owner: str, repo: str, tag_name: str,
                              name: str, body: str, prerelease: bool):
        self._request_create_release.emit(
            owner, repo, tag_name, name, body, prerelease
        )

    def upload_asset(self, upload_url: str, asset_path: str):
        self._request_upload_asset.emit(upload_url, asset_path)

    def delete_release(self, owner: str, repo: str, release_id: int):
        self._request_delete_release.emit(owner, repo, release_id)

    def update_repo_visibility(self, owner: str, repo: str, is_private: bool):
        self._request_update_visibility.emit(owner, repo, is_private)

    def fetch_plugin_index(self, repo_path: str):
        self._request_plugin_index.emit(repo_path)

    def shutdown(self):
        if self.thread and self.thread.isRunning():
            log.info("Shutting down GitHubManager thread.")
            self.thread.quit()
            if not self.thread.wait(3000):
                log.warning(
                    "GitHubManager thread did not shut down "
                    "gracefully. Terminating."
                )
                self.thread.terminate()
```

### File: `/app_core/linter_manager.py`

```python
# PuffinPyEditor/app_core/linter_manager.py
import subprocess
import os
import sys
import shutil
from typing import List, Dict, Optional
from PyQt6.QtCore import QObject, QThread, pyqtSignal
from utils.logger import log

# Use a very unlikely string as a delimiter
SAFE_DELIMITER = "|||PUFFIN_LINT|||"


class LinterRunner(QObject):
    """
    A worker QObject that runs flake8 in a separate thread to avoid
    blocking the main UI.
    """
    lint_results_ready = pyqtSignal(list)
    project_lint_results_ready = pyqtSignal(dict)
    error_occurred = pyqtSignal(str)

    def _find_flake8_executable(self) -> Optional[str]:
        """Finds the path to the flake8 executable."""
        return shutil.which("flake8")

    def run_linter_on_file(self, filepath: str):
        """Runs flake8 on a single file and emits the results."""
        if not filepath or not os.path.exists(filepath):
            self.lint_results_ready.emit([])
            return

        flake8_executable = self._find_flake8_executable()
        if not flake8_executable:
            msg = "'flake8' executable not found. Please install it."
            log.error(f"Linter error: {msg}")
            self.error_occurred.emit(msg)
            return

        command = [flake8_executable, filepath,
                   "--format=%(row)d:%(col)d:%(code)s:%(text)s"]
        log.info(f"Running linter on file: {' '.join(command)}")

        try:
            # CREATE_NO_WINDOW prevents a console flash on Windows
            creation_flags = 0
            if sys.platform == "win32":
                creation_flags = subprocess.CREATE_NO_WINDOW

            process = subprocess.Popen(
                command, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                text=True, encoding='utf-8', creationflags=creation_flags
            )
            stdout, stderr = process.communicate(timeout=15)

            if stderr:
                log.error(f"Linter stderr for {filepath}: {stderr.strip()}")

            results = self._parse_flake8_file_output(stdout)
            self.lint_results_ready.emit(results)
        except Exception as e:
            log.error(f"Exception while running flake8 on file: {e}",
                      exc_info=True)
            self.lint_results_ready.emit([])

    def run_linter_on_project(self, project_path: str):
        """Runs flake8 recursively on a project path and emits the results."""
        flake8_executable = self._find_flake8_executable()
        if not flake8_executable:
            msg = "'flake8' executable not found. Cannot lint project."
            log.error(msg)
            self.error_occurred.emit(msg)
            return

        # Use the safe delimiter to reliably parse file paths from output
        format_str = (f"--format=%(path)s{SAFE_DELIMITER}%(row)d"
                      f"{SAFE_DELIMITER}%(col)d{SAFE_DELIMITER}%(code)s"
                      f"{SAFE_DELIMITER}%(text)s")
        command = [flake8_executable, project_path, format_str]
        log.info(f"Running linter on project: {project_path}")

        try:
            creation_flags = 0
            if sys.platform == "win32":
                creation_flags = subprocess.CREATE_NO_WINDOW
            process = subprocess.Popen(
                command, cwd=project_path, stdout=subprocess.PIPE,
                stderr=subprocess.PIPE, text=True, encoding='utf-8',
                creationflags=creation_flags
            )
            stdout, stderr = process.communicate(timeout=60)

            if stderr:
                log.warning(
                    f"Linter stderr for {project_path}: {stderr.strip()}"
                )

            results = self._parse_flake8_project_output(stdout, project_path)
            self.project_lint_results_ready.emit(results)
        except Exception as e:
            log.error(f"Exception while running flake8 on project: {e}",
                      exc_info=True)
            self.project_lint_results_ready.emit({})

    def _parse_flake8_file_output(self, output: str) -> List[Dict]:
        """Parses standard flake8 output for a single file."""
        problems = []
        for line in output.strip().splitlines():
            parts = line.split(':', 3)
            if len(parts) == 4:
                try:
                    problems.append({
                        "line": int(parts[0]),
                        "col": int(parts[1]),
                        "code": parts[2],
                        "description": parts[3].strip()
                    })
                except (ValueError, IndexError):
                    log.warning(f"Could not parse linter line: {line}")
        return problems

    def _parse_flake8_project_output(
        self, output: str, project_path: str
    ) -> Dict[str, List[Dict]]:
        """Parses flake8 output that uses the custom SAFE_DELIMITER."""
        problems_by_file = {}
        for line in output.strip().splitlines():
            parts = line.split(SAFE_DELIMITER, 4)
            if len(parts) == 5:
                try:
                    raw_path, line_num, col_num, code, desc = parts
                    # Ensure the path is absolute and normalized
                    abs_path = os.path.normpath(
                        os.path.join(project_path, raw_path)
                    )
                    problem = {
                        "line": int(line_num),
                        "col": int(col_num),
                        "code": code,
                        "description": desc.strip()
                    }
                    if abs_path not in problems_by_file:
                        problems_by_file[abs_path] = []
                    problems_by_file[abs_path].append(problem)
                except (ValueError, IndexError):
                    log.warning(f"Could not parse project linter line: {line}")
        return problems_by_file


class LinterManager(QObject):
    """
    Manages linting operations by delegating to a LinterRunner on a
    separate thread.
    """
    lint_results_ready = pyqtSignal(list)
    project_lint_results_ready = pyqtSignal(dict)
    error_occurred = pyqtSignal(str)

    _request_file_lint = pyqtSignal(str)
    _request_project_lint = pyqtSignal(str)

    def __init__(self, parent: Optional[QObject] = None):
        super().__init__(parent)
        self.thread = QThread()
        self.runner = LinterRunner()
        self.runner.moveToThread(self.thread)

        # Connect signals
        self._request_file_lint.connect(self.runner.run_linter_on_file)
        self._request_project_lint.connect(self.runner.run_linter_on_project)
        self.runner.lint_results_ready.connect(self.lint_results_ready)
        self.runner.project_lint_results_ready.connect(
            self.project_lint_results_ready
        )
        self.runner.error_occurred.connect(self.error_occurred)

        self.thread.start()

    def lint_file(self, filepath: str):
        """Requests a lint for a single file."""
        self._request_file_lint.emit(filepath)

    def lint_project(self, project_path: str):
        """Requests a lint for an entire project directory."""
        self._request_project_lint.emit(project_path)

    def shutdown(self):
        """Gracefully shuts down the linter thread."""
        if self.thread.isRunning():
            self.thread.quit()
            self.thread.wait(3000)
```

### File: `/app_core/plugin_manager.py`

```python
# PuffinPyEditor/app_core/plugin_manager.py
import os
import sys
import json
import importlib
import importlib.util
import inspect
import zipfile
import tempfile
import shutil
from dataclasses import dataclass, field
from typing import Dict, Any, Optional, Tuple, List
from utils.logger import log, get_app_data_path
from utils.helpers import get_base_path
from app_core.puffin_api import PuffinPluginAPI # Import API for type hinting

try:
    from packaging.version import Version, InvalidVersion
except ImportError:
    log.warning(
        "The 'packaging' library is not installed. Version comparison will be basic. Run 'pip install packaging'.")

    # Define dummy classes if 'packaging' is not available
    class _DummyVersion:
        def __init__(self, v): self.v = v
        def __eq__(self, o): return self.v == o.v
        def __lt__(self, o): return self.v < o.v
        def __le__(self, o): return self.v <= o.v
        def __gt__(self, o): return self.v > o.v
        def __ge__(self, o): return self.v >= o.v

    Version = _DummyVersion
    InvalidVersion = ValueError


@dataclass
class Plugin:
    """A dataclass to hold all information about a plugin."""
    manifest: Dict[str, Any]
    path: str
    source_type: str  # 'built-in', 'core-tool', 'user'
    is_core: bool = field(init=False)
    is_loaded: bool = False
    enabled: bool = True
    module: Optional[Any] = None
    instance: Optional[Any] = None
    status_reason: str = "Not loaded"

    def __post_init__(self):
        self.is_core = self.source_type != "user"

    @property
    def id(self) -> str: return self.manifest.get('id', 'unknown')

    @property
    def name(self) -> str: return self.manifest.get('name', self.id)

    @property
    def version(self) -> str: return self.manifest.get('version', '0.0.0')


class PluginManager:
    # --- FIX: The constructor now takes the main_window and uses its existing API object ---
    def __init__(self, main_window):
        # This is the corrected logic.
        # It ensures a single, shared API instance across the app.
        self.api: PuffinPluginAPI = main_window.puffin_api

        base_app_path = get_base_path()
        app_data_path = get_app_data_path()

        self.built_in_plugins_dir = os.path.join(base_app_path, "plugins")
        self.core_tools_directory = os.path.join(base_app_path, "core_debug_tools")
        self.user_plugins_directory = os.path.join(app_data_path, "plugins")
        self.plugin_states_file = os.path.join(app_data_path, "plugin_states.json")

        self._ensure_paths_and_packages()
        self.plugins: Dict[str, Plugin] = {}
        log.info("PluginManager initialized with a shared API.")

    def _ensure_paths_and_packages(self):
        for path in [get_base_path(), self.user_plugins_directory]:
            if path not in sys.path:
                sys.path.insert(0, path)
                log.info(f"Added to sys.path: {path}")
        if not os.path.isdir(self.user_plugins_directory):
            log.info(f"Creating user plugins directory: {self.user_plugins_directory}")
            os.makedirs(self.user_plugins_directory)
        init_path = os.path.join(self.user_plugins_directory, "__init__.py")
        if not os.path.exists(init_path):
            with open(init_path, 'w', encoding='utf-8') as f:
                f.write("# This file makes the plugins directory a package.\n")

    def discover_and_load_plugins(self, ignore_list: Optional[List[str]] = None):
        log.info("Starting full plugin discovery and loading process...")
        ignore_list = ignore_list or []

        self._discover_plugins()
        self._load_plugin_states()
        load_order = self._resolve_dependencies()
        for plugin_id in load_order:
            plugin = self.plugins.get(plugin_id)
            if plugin_id in ignore_list:
                log.info(f"Skipping plugin '{plugin.name if plugin else plugin_id}' as it's in the ignore list.")
                if plugin: plugin.status_reason = "Ignored (pre-loaded)"
                continue
            if plugin and plugin.enabled:
                self.load_plugin(plugin_id)
            elif plugin:
                log.info(f"Plugin '{plugin.name}' is disabled and will not be loaded.")
        log.info("Plugin discovery and loading complete.")

    def _discover_plugins(self):
        plugin_sources = {
            "built-in": self.built_in_plugins_dir,
            "core-tool": self.core_tools_directory,
            "user": self.user_plugins_directory,
        }
        for source_type, plugin_dir in plugin_sources.items():
            if not os.path.isdir(plugin_dir): continue
            for item_name in os.listdir(plugin_dir):
                if item_name.startswith(('__', '.')): continue
                plugin_path = os.path.join(plugin_dir, item_name)
                if os.path.isdir(plugin_path):
                    self._process_potential_plugin(plugin_path, source_type)

    def _process_potential_plugin(self, plugin_path: str, source_type: str):
        manifest_path = os.path.join(plugin_path, "plugin.json")
        if not os.path.exists(manifest_path): return
        try:
            with open(manifest_path, 'r', encoding='utf-8') as f:
                manifest = json.load(f)
            if not self._validate_manifest(manifest, manifest_path): return
            plugin_id = manifest['id']
            if plugin_id in self.plugins and source_type == "built-in": return
            plugin = Plugin(manifest=manifest, path=plugin_path, source_type=source_type)
            self.plugins[plugin_id] = plugin
        except (json.JSONDecodeError, IOError) as e:
            log.error(f"Failed to read or parse manifest at '{manifest_path}': {e}")

    def _validate_manifest(self, manifest: Dict, path: str) -> bool:
        for field in ['id', 'name', 'version']:
            if field not in manifest or not manifest[field]:
                log.error(f"Manifest at {path} is missing or has empty field: '{field}'. Skipping.")
                return False
        return True

    def _resolve_dependencies(self) -> List[str]:
        log.info("Resolving plugin dependencies...")
        dependencies = {pid: set(p.manifest.get('dependencies', {}).keys()) for pid, p in self.plugins.items()}
        load_order, resolved = [], set()
        while len(load_order) < len(self.plugins):
            ready = {pid for pid, deps in dependencies.items() if pid not in resolved and not deps - resolved}
            if not ready:
                unresolved = {pid: deps - resolved for pid, deps in dependencies.items() if pid not in resolved}
                log.error(f"Could not resolve plugin dependencies. Circular or missing. Unresolved: {unresolved}")
                for pid, missing in unresolved.items():
                    if pid in self.plugins:
                        self.plugins[pid].enabled = False
                        self.plugins[pid].status_reason = f"Dependency error: {missing}"
                break
            for plugin_id in sorted(list(ready)):
                plugin, can_load = self.plugins[plugin_id], True
                for dep_id, req_ver in plugin.manifest.get('dependencies', {}).items():
                    if dep_id not in self.plugins: plugin.status_reason = f"Missing dependency: {dep_id}"; can_load = False; break
                    if not self._check_version(self.plugins[dep_id].version, req_ver):
                        plugin.status_reason = f"Version conflict for '{dep_id}'. Have {self.plugins[dep_id].version}, need {req_ver}";
                        can_load = False;
                        break
                if can_load:
                    plugin.status_reason = "Dependencies met";
                    load_order.append(plugin_id)
                else:
                    plugin.enabled = False
                resolved.add(plugin_id)
        log.info(f"Plugin load order determined: {load_order}")
        return load_order

    def _check_version(self, installed_version: str, required_version_spec: str) -> bool:
        try:
            installed, spec = Version(installed_version), required_version_spec.strip()
            if spec.startswith('>='): return installed >= Version(spec[2:])
            if spec.startswith('<='): return installed <= Version(spec[2:])
            if spec.startswith('=='): return installed == Version(spec[2:])
            if spec.startswith('>'): return installed > Version(spec[1:])
            if spec.startswith('<'): return installed < Version(spec[1:])
            return installed == Version(spec)
        except (InvalidVersion, ValueError) as e:
            log.warning(
                f"Could not parse version. installed='{installed_version}', required='{required_version_spec}'. Error: {e}")
            return False

    def load_plugin(self, plugin_id: str) -> bool:
        plugin = self.plugins.get(plugin_id)
        if not plugin or plugin.is_loaded: return False

        entry_point = plugin.manifest.get("entry_point", "plugin_main.py")
        entry_point_path = os.path.join(plugin.path, entry_point)

        if not os.path.exists(entry_point_path):
            plugin.status_reason = f"Entry point '{entry_point}' not found."
            log.error(f"{plugin.status_reason} for plugin '{plugin.name}'.")
            return False

        entry_module_name = os.path.splitext(entry_point)[0]
        package_name = plugin.id if plugin.source_type == 'user' else f"{os.path.basename(os.path.dirname(plugin.path))}.{plugin.id}"
        module_name = f"{package_name}.{entry_module_name}"

        try:
            spec = importlib.util.spec_from_file_location(module_name, entry_point_path)
            if not spec or not spec.loader: raise ImportError(f"Could not create module spec for {module_name}")
            module = importlib.util.module_from_spec(spec)
            sys.modules[module_name] = module
            spec.loader.exec_module(module)

            if hasattr(module, 'initialize'):
                # Pass the single, shared API instance to the plugin
                arg_to_pass = self.api
                plugin.instance = module.initialize(arg_to_pass)
                plugin.module = module
                plugin.is_loaded = True
                plugin.status_reason = "Loaded successfully"
                log.info(f"Successfully initialized plugin: '{plugin.name}' (Version: {plugin.version})")
                return True
            else:
                plugin.status_reason = "No 'initialize' function found."
                log.error(f"Plugin '{plugin.name}' has no 'initialize' function. Skipping.")
                if module_name in sys.modules: del sys.modules[module_name]
                return False
        except Exception as e:
            plugin.status_reason = f"Load error: {e}"
            log.error(f"An unexpected error occurred loading plugin '{plugin.name}': {e}", exc_info=True)
            if module_name in sys.modules: del sys.modules[module_name]
            return False

    def unload_plugin(self, plugin_id: str) -> bool:
        plugin = self.plugins.get(plugin_id)
        if not plugin or not plugin.is_loaded: return True
        log.info(f"Unloading plugin: '{plugin.name}'")
        try:
            if hasattr(plugin.instance, 'shutdown'): plugin.instance.shutdown()
            plugin.is_loaded, plugin.instance, module_name = False, None, plugin.module.__name__
            plugin.module = None
            if module_name in sys.modules: del sys.modules[module_name]
            import gc;
            gc.collect()
            plugin.status_reason = "Unloaded";
            log.info(f"Successfully unloaded plugin '{plugin.name}'.")
            return True
        except Exception as e:
            plugin.status_reason = f"Unload error: {e}";
            log.error(f"Error during shutdown of plugin '{plugin.name}': {e}", exc_info=True)
            return False

    def reload_plugin(self, plugin_id: str) -> bool:
        log.info(f"Reloading plugin '{plugin_id}'...")
        if self.unload_plugin(plugin_id):
            return self.load_plugin(plugin_id)
        log.error(f"Failed to unload plugin '{plugin_id}' during reload process.")
        return False

    def enable_plugin(self, plugin_id: str):
        plugin = self.plugins.get(plugin_id)
        if not plugin: log.error(f"Cannot enable non-existent plugin '{plugin_id}'"); return
        plugin.enabled = True;
        self._save_plugin_states()
        log.info(f"Plugin '{plugin.name}' enabled. Re-evaluating and loading plugins.")
        self.discover_and_load_plugins()

    def disable_plugin(self, plugin_id: str):
        plugin = self.plugins.get(plugin_id)
        if not plugin: log.error(f"Cannot disable non-existent plugin '{plugin_id}'"); return
        self.unload_plugin(plugin_id);
        plugin.enabled = False;
        self._save_plugin_states()
        log.info(f"Plugin '{plugin.name}' disabled and unloaded.")

    def enable_all(self):
        """Enables all available plugins."""
        log.info("Enabling all plugins.")
        for plugin in self.plugins.values():
            plugin.enabled = True
        self._save_plugin_states()
        log.info("All plugins enabled. Re-evaluating and loading all plugins.")
        self.discover_and_load_plugins()

    def disable_all_non_core(self):
        """Disables all non-core plugins."""
        log.info("Disabling all non-core plugins.")
        for plugin in self.plugins.values():
            if not plugin.is_core:
                self.unload_plugin(plugin.id)
                plugin.enabled = False
        self._save_plugin_states()
        log.info("All non-core plugins have been disabled and unloaded.")

    def _load_plugin_states(self):
        if not os.path.exists(self.plugin_states_file): return
        try:
            with open(self.plugin_states_file, 'r', encoding='utf-8') as f:
                states = json.load(f)
            for pid, state in states.items():
                if pid in self.plugins and isinstance(state, dict): self.plugins[pid].enabled = state.get('enabled',
                                                                                                          True)
        except (IOError, json.JSONDecodeError) as e:
            log.warning(f"Could not load plugin states from {self.plugin_states_file}: {e}")

    def _save_plugin_states(self):
        states = {pid: {'enabled': p.enabled} for pid, p in self.plugins.items()}
        try:
            with open(self.plugin_states_file, 'w', encoding='utf-8') as f:
                json.dump(states, f, indent=4)
        except IOError as e:
            log.error(f"Could not save plugin states to {self.plugin_states_file}: {e}")

    def get_all_plugins(self) -> List[Plugin]:
        return list(self.plugins.values())

    def get_installed_plugins(self) -> list:
        # Compatibility wrapper for older calls that expect dicts
        return [p.manifest for p in self.get_all_plugins()]

    def get_loaded_plugins(self) -> List[Plugin]:
        return [p for p in self.plugins.values() if p.is_loaded]

    def get_plugin_instance_by_id(self, plugin_id: str) -> Optional[Any]:
        plugin = self.plugins.get(plugin_id)
        if plugin and plugin.is_loaded:
            return plugin.instance
        return None

    def install_plugin_from_zip(self, zip_filepath: str) -> Tuple[bool, str]:
        if not zipfile.is_zipfile(zip_filepath): return False, "Not a valid zip archive."
        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                with zipfile.ZipFile(zip_filepath, 'r') as z:
                    z.extractall(temp_dir)
                items = os.listdir(temp_dir);
                is_nested = len(items) == 1 and os.path.isdir(os.path.join(temp_dir, items[0]))
                src_dir = os.path.join(temp_dir, items[0]) if is_nested else temp_dir
                manifest_path = os.path.join(src_dir, 'plugin.json')
                if not os.path.exists(manifest_path): return False, "Archive is missing 'plugin.json'."
                with open(manifest_path, 'r', encoding='utf-8') as f:
                    manifest = json.load(f)
                if not self._validate_manifest(manifest, manifest_path): return False, "Plugin manifest is invalid."
                plugin_id = manifest['id'];
                target_path = os.path.join(self.user_plugins_directory, plugin_id)
                if os.path.exists(target_path): return False, f"A plugin with ID '{plugin_id}' already exists."
                shutil.move(src_dir, target_path);
                plugin_name = manifest.get('name', plugin_id)
                log.info(f"Plugin '{plugin_name}' installed. Reloading plugins...")
                self.discover_and_load_plugins()
                return True, f"Plugin '{plugin_name}' installed and loaded."
        except Exception as e:
            log.error(f"Failed to install plugin from {zip_filepath}: {e}", exc_info=True)
            return False, f"An unexpected error occurred: {e}"

    def uninstall_plugin(self, plugin_id: str) -> Tuple[bool, str]:
        plugin = self.plugins.get(plugin_id)
        if not plugin: return False, f"Plugin '{plugin_id}' is not installed."
        if plugin.is_core: return False, "This is a built-in plugin and cannot be uninstalled."
        self.unload_plugin(plugin_id)
        target_path = os.path.join(self.user_plugins_directory, plugin_id)
        if not os.path.isdir(target_path): return False, f"Plugin directory for '{plugin_id}' not found."
        try:
            shutil.rmtree(target_path)
            if plugin_id in self.plugins: del self.plugins[plugin_id]
            self._save_plugin_states()
            log.info(f"Successfully uninstalled plugin '{plugin_id}'.")
            return True, f"Plugin '{plugin_id}' was uninstalled."
        except OSError as e:
            log.error(f"Failed to uninstall plugin '{plugin_id}': {e}", exc_info=True)
            return False, f"Error removing plugin directory: {e}"
```

### File: `/app_core/project_manager.py`

```python
# PuffinPyEditor/app_core/project_manager.py
import os
import datetime
import zipfile
from pathlib import Path
from typing import List, Tuple, Optional, Dict

# NEW: Import QObject and pyqtSignal for signals
from PyQt6.QtCore import QObject, pyqtSignal

from .settings_manager import settings_manager
from utils.logger import log


class ProjectManager(QObject):  # MODIFIED: Inherit from QObject
    """Manages the state of open projects and project-wide operations."""

    # NEW: Add the required signal
    projects_changed = pyqtSignal()

    def __init__(self):
        super().__init__()  # NEW: Call the QObject constructor
        self._open_projects: List[str] = []
        self._active_project_path: Optional[str] = None
        self._load_session()
        log.info(
            f"ProjectManager initialized with {len(self._open_projects)} "
            "projects."
        )

    def _load_session(self):
        """Loads the list of open projects from the settings."""
        open_projects = settings_manager.get("open_projects", [])
        active_project = settings_manager.get("active_project_path")

        # Ensure all stored project paths are valid directories
        self._open_projects = [
            os.path.normpath(p) for p in open_projects if os.path.isdir(p)
        ]

        if (active_project and
                os.path.normpath(active_project) in self._open_projects):
            self._active_project_path = os.path.normpath(active_project)
        elif self._open_projects:
            self._active_project_path = self._open_projects[0]
        else:
            self._active_project_path = None
        log.info(
            "Loaded project session. Active project: "
            f"{self._active_project_path}"
        )

    def save_session(self):
        """Saves the current list of open projects to the settings."""
        settings_manager.set("open_projects", self._open_projects, False)
        settings_manager.set(
            "active_project_path", self._active_project_path, False
        )
        log.info("Project session saved.")

    def open_project(self, path: str) -> bool:
        """Adds a project to the list of open projects and sets it as active."""
        if not os.path.isdir(path):
            log.error(f"Cannot open project. Path is not a directory: {path}")
            return False

        norm_path = os.path.normpath(path)
        if norm_path not in self._open_projects:
            self._open_projects.append(norm_path)
            log.info(f"Project opened: {norm_path}")
            self.projects_changed.emit()  # NEW: Emit signal on change
        self.set_active_project(norm_path)
        return True

    def close_project(self, path: str):
        """Closes a project and updates the active project if necessary."""
        norm_path = os.path.normpath(path)
        if norm_path in self._open_projects:
            self._open_projects.remove(norm_path)
            log.info(f"Project closed: {norm_path}")
            self.projects_changed.emit()  # NEW: Emit signal on change

            # If the closed project was the active one, pick a new active one
            if self.get_active_project_path() == norm_path:
                new_active = self._open_projects[0] if self._open_projects else None
                self.set_active_project(new_active)

    def get_open_projects(self) -> List[str]:
        """Returns the list of currently open project paths."""
        return self._open_projects

    def set_active_project(self, path: Optional[str]):
        """Sets the currently active project."""
        norm_path = os.path.normpath(path) if path else None
        if self._active_project_path != norm_path:
            self._active_project_path = norm_path
            log.info(f"Active project set to: {norm_path}")

    def get_active_project_path(self) -> Optional[str]:
        """Returns the path of the currently active project."""
        return self._active_project_path

    def is_project_open(self) -> bool:
        """Checks if any project is currently active."""
        return self._active_project_path is not None

    def create_project_zip(self, output_zip_path: str) -> bool:
        """
        Creates a zip archive of the active project, ignoring common artifacts.

        Returns:
            True if the zip was created successfully, False otherwise.
        """
        if not self.is_project_open():
            log.error("Cannot create zip. No active project.")
            return False

        project_root = self.get_active_project_path()
        ignore_dirs = {
            '__pycache__', '.git', 'venv', '.venv', 'dist', 'build', 'logs'
        }
        # Explicitly ignore the user settings file for security
        ignore_files = {'.gitignore', 'puffin_editor_settings.json'}

        try:
            with zipfile.ZipFile(
                    output_zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, dirs, files in os.walk(project_root):
                    # Modify dirs in-place to prevent walking into ignored dirs
                    dirs[:] = [d for d in dirs if d not in ignore_dirs]
                    for file in files:
                        if file in ignore_files:
                            continue
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, project_root)
                        zipf.write(file_path, arcname)
            log.info(
                f"Successfully created project archive at {output_zip_path}"
            )
            return True
        except (IOError, OSError, zipfile.BadZipFile) as e:
            log.error(f"Failed to create project zip: {e}", exc_info=True)
            return False

    def _generate_file_tree_from_list(
            self, project_root: str, file_list: List[str]
    ) -> List[str]:
        """Generates a text-based file tree from a specific list of files."""
        tree = {}
        for file_path in file_list:
            relative_path = os.path.relpath(file_path, project_root)
            parts = Path(relative_path).parts
            current_level = tree
            for part in parts:
                if part not in current_level:
                    current_level[part] = {}
                current_level = current_level[part]

        def build_tree_lines(d: dict, prefix: str = "") -> List[str]:
            lines = []
            # Sort entries so directories (which have children) come first
            entries = sorted(
                d.keys(), key=lambda k: (not bool(d[k]), k.lower())
            )
            for i, name in enumerate(entries):
                is_last = (i == len(entries) - 1)
                connector = "└── " if is_last else "├── "
                lines.append(f"{prefix}{connector}{name}")
                if d[name]:  # It's a directory with children
                    new_prefix = prefix + ("    " if is_last else "│   ")
                    lines.extend(build_tree_lines(d[name], new_prefix))
            return lines

        return build_tree_lines(tree)

    def _clean_git_conflict_markers(self, content: str) -> str:
        """Removes Git conflict markers from a string, keeping the HEAD version."""
        if '<<<<<<<' not in content:
            return content

        lines = content.splitlines()
        cleaned_lines = []
        in_conflict = False
        # We want to keep the HEAD version, which is the part before '======='
        keep_current_version = False

        for line in lines:
            if line.startswith('<<<<<<<'):
                in_conflict = True
                keep_current_version = True
                continue

            if line.startswith('======='):
                if in_conflict:
                    keep_current_version = False
                    continue

            if line.startswith('>>>>>>>'):
                if in_conflict:
                    in_conflict = False
                    keep_current_version = False
                    continue

            if not in_conflict or (in_conflict and keep_current_version):
                cleaned_lines.append(line)

        return "\n".join(cleaned_lines)

    def export_project_for_ai(
            self,
            output_filepath: str,
            selected_files: List[str],
            instructions: str,
            guidelines: List[str],
            golden_rules: List[str],
            all_problems: Optional[Dict[str, List[Dict]]] = None
    ) -> Tuple[bool, str]:
        """
        Exports selected project files into a single Markdown file for AI.
        """
        if not self.is_project_open():
            return False, "No project is open."

        project_root = self.get_active_project_path()
        project_name = os.path.basename(project_root)
        output_lines = [
            f"# Project Export: {project_name}",
            f"## Export Timestamp: {datetime.datetime.now().isoformat()}",
            "---",
            "\n## 📝 AI Instructions", "```text",
            instructions or "No specific instructions were provided.", "```",
            "\n## 📜 AI Guidelines & Rules", "```text",
        ]
        guideline_text = "\n".join(
            [f"- {g}" for g in guidelines]
        ) if guidelines else "No specific guidelines were provided."
        output_lines.append(guideline_text)
        output_lines.extend(["```", "---"])

        output_lines.append("\n## ✨ Golden Rules\n```text")
        golden_rules_text = "\n".join(
            [f"{i + 1}. {g}" for i, g in enumerate(golden_rules)]
        ) if golden_rules else "No specific golden rules were provided."
        output_lines.append(golden_rules_text)
        output_lines.extend(["```", "---"])

        output_lines.append("\n## 🗂️ File Tree of Included Files:\n```")
        output_lines.append(f"/{project_name}")
        output_lines.extend(
            self._generate_file_tree_from_list(project_root, selected_files)
        )
        output_lines.append("```\n---")
        output_lines.append("\n## 📄 File Contents:\n")

        file_count = 0
        for filepath in sorted(selected_files):
            norm_filepath = os.path.normpath(filepath)
            relative_path = Path(
                filepath).relative_to(project_root).as_posix()
            language = Path(filepath).suffix.lstrip('.') or 'text'
            if language == 'py':
                language = 'python'

            output_lines.append(f"### File: `/{relative_path}`\n")

            if all_problems and norm_filepath in all_problems:
                output_lines.append("#### Linter Issues Found:")
                output_lines.append("```")
                for problem in all_problems[norm_filepath]:
                    output_lines.append(
                        f"- Line {problem['line']}, Col {problem['col']} "
                        f"({problem['code']}): {problem['description']}"
                    )
                output_lines.append("```\n")

            output_lines.append(f"```{language}")
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    original_content = f.read()
                    cleaned_content = self._clean_git_conflict_markers(original_content)
                    if original_content != cleaned_content:
                        log.info(f"Cleaned git conflict markers from {filepath} for export.")
                    output_lines.append(cleaned_content)
                file_count += 1
            except (IOError, UnicodeDecodeError) as e:
                log.warning(
                    "Could not read file during AI export: "
                    f"{filepath}. Error: {e}"
                )
                output_lines.append(f"[Error reading file: {e}]")
            output_lines.append("```\n---")

        try:
            with open(output_filepath, 'w', encoding='utf-8') as f:
                f.write("\n".join(output_lines))
            return True, (
                f"Project exported to {Path(output_filepath).name}. "
                f"Included {file_count} files."
            )
        except IOError as e:
            log.error(f"Failed to write AI export file: {e}", exc_info=True)
            return False, f"Failed to write export file: {e}"
```

### File: `/app_core/puffin_api.py`

```python
# PuffinPyEditor/app_core/puffin_api.py
from typing import Callable, Optional, Any, TYPE_CHECKING
from PyQt6.QtWidgets import (QDockWidget, QTabWidget, QWidget, QMenu, QMessageBox)
from PyQt6.QtGui import QAction, QIcon
from PyQt6.QtCore import Qt
import qtawesome as qta
from utils.logger import log

if TYPE_CHECKING:
    from ui.main_window import MainWindow


class PuffinPluginAPI:
    def __init__(self, main_window: 'MainWindow'):
        self._main_window = main_window
        self.theme_editor_launcher: Optional[Callable] = None
        self.highlighter_map: dict[str, Any] = {}
        log.info("PuffinPluginAPI initialized.")

    def get_main_window(self) -> 'MainWindow':
        return self._main_window

    def get_manager(self, manager_name: str) -> Optional[Any]:
        name_map = {
            "project": self._main_window.project_manager, "file_handler": self._main_window.file_handler,
            "settings": self._main_window.settings, "theme": self.get_main_window().theme_manager,
            "completion": self._main_window.completion_manager, "github": self._main_window.github_manager,
            "git": self._main_window.git_manager, "linter": self._main_window.linter_manager,
            "update": self._main_window.update_manager, "plugin": self._main_window.plugin_manager,
        }
        if not (manager := name_map.get(manager_name.lower())):
            log.warning(f"Plugin requested an unknown manager: '{manager_name}'")
        return manager

    def get_plugin_instance(self, plugin_id: str) -> Optional[Any]:
        if plugin_manager := self.get_manager("plugin"):
            if plugin := plugin_manager.plugins.get(plugin_id):
                if plugin.is_loaded: return plugin.instance
        log.warning(f"Could not find a loaded plugin instance for ID: '{plugin_id}'")
        return None

    def register_theme_editor_launcher(self, launcher_callback: Callable):
        self.theme_editor_launcher = launcher_callback
        log.info("A theme editor launcher has been registered.")
        if hasattr(mw := self.get_main_window(), 'preferences_dialog') and mw.preferences_dialog:
            mw.preferences_dialog.connect_theme_editor_button()

    def register_highlighter(self, extension: str, highlighter_class):
        if not extension.startswith('.'): extension = f".{extension}"
        self.highlighter_map[extension.lower()] = highlighter_class
        log.info(f"Registered highlighter '{highlighter_class.__name__}' for '{extension}' files.")

    def add_menu_action(self, menu_name, text, callback, shortcut=None, icon_name=None) -> QAction:
        menu = getattr(self._main_window, f"{menu_name.lower()}_menu", None)
        if not menu:
            menu = self._main_window.menuBar().addMenu(f"&{menu_name.capitalize()}")
            setattr(self._main_window, f"{menu_name.lower()}_menu", menu)

        icon = qta.icon(icon_name) if icon_name else None
        action = QAction(icon, text, self._main_window)
        if shortcut: action.setShortcut(shortcut)
        action.triggered.connect(callback)
        menu.addAction(action)
        return action

    def add_toolbar_action(self, action: QAction):
        """Adds a QAction to the main application toolbar."""
        if hasattr(self._main_window, 'main_toolbar'):
            self._main_window.main_toolbar.addAction(action)
            log.info(f"Added action '{action.text()}' to main toolbar.")
        else:
            log.error("Cannot add toolbar action: Main toolbar not found.")

    def register_dock_panel(self, content_widget, title, area, icon_name=None):
        if hasattr(self._main_window, 'add_dock_panel'):
            self._main_window.add_dock_panel(content_widget, title, area, icon_name)
        else:
            log.error("Cannot register dock panel: Main window is missing 'add_dock_panel' method.")

    def register_file_opener(self, extension: str, handler_callable: Callable):
        if not extension.startswith('.'): extension = f".{extension}"
        self._main_window.file_open_handlers[extension.lower()] = handler_callable

    def show_message(self, level, title, text):
        icon = {'info': QMessageBox.Icon.Information, 'warning': QMessageBox.Icon.Warning,
                'critical': QMessageBox.Icon.Critical}.get(level.lower(), QMessageBox.Icon.NoIcon)
        QMessageBox(icon, title, text, parent=self._main_window).exec()

    def show_status_message(self, message: str, timeout: int = 4000):
        self._main_window.statusBar().showMessage(message, timeout)

    def log_info(self, msg):
        log.info(f"[Plugin] {msg}")

    def log_warning(self, msg):
        log.warning(f"[Plugin] {msg}")

    def log_error(self, msg):
        log.error(f"[Plugin] {msg}")
```

### File: `/app_core/settings_manager.py`

```python
# PuffinPyEditor/app_core/settings_manager.py
import json
import os
from typing import Any, Dict
from utils.logger import log, get_app_data_path

# Use the same application data path for the settings file to ensure it's
# in a user-writable location, especially after installation.
APP_DATA_ROOT = get_app_data_path()
SETTINGS_FILE = os.path.join(APP_DATA_ROOT, "puffin_editor_settings.json")

DEFAULT_SETTINGS = {
    # --- Window & Layout ---
    "window_size": [1600, 1000],
    "window_position": None,
    "splitter_sizes": [300, 1300],

    # --- Editor & Appearance ---
    "last_theme_id": "puffin_dark",
    "font_family": "Consolas",
    "font_size": 11,
    "show_line_numbers": True,
    "show_indentation_guides": True,
    "word_wrap": False,
    "indent_style": "spaces",  # "spaces" or "tabs"
    "indent_width": 4,

    # --- File Handling ---
    "auto_save_enabled": False,
    "auto_save_delay_seconds": 3,
    "max_recent_files": 15,
    "favorites": [],

    # --- Project State ---
    "open_projects": [],
    "active_project_path": None,

    # --- Integrations & Run ---
    "python_interpreter_path": "",
    "github_access_token": None,
    "github_user": None,
    "source_control_repos": [],
    "active_update_repo_id": None,
    "plugins_distro_repo": "Stelliro/puffin-plugins",
    "ai_export_loadouts": {},
    "ai_export_golden_rules": {
        "Default Golden Rules": [
            "Do not remove any code that is unrelated to the fix, only remove "
            "code if it is being substituted or is not needed anymore.",
            "Only edit and add features, the only features should stay unless "
            "asked to be removed, or may be completely redundant.",
            "any scripts over 1000 lines, please write in a new response.",
            "multiple scripts together exceeding 2000 lines together need to "
            "be separated into smaller responses, (example: these scripts "
            "have 2340 lines together I'm going to separate it into 2 "
            "messages that way i dont lose formatting and dont accidentally "
            "remove any features)"
        ]
    },
    "cleanup_after_build": True,
    "nsis_path": ""
}


class SettingsManager:
    """Handles loading, accessing, and saving application settings."""

    def __init__(self, settings_file: str = SETTINGS_FILE):
        self.settings_file = settings_file
        self.settings = self._load_settings()

    def _load_settings(self) -> Dict[str, Any]:
        """Loads settings from the JSON file, merging with defaults."""
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    loaded_settings = json.load(f)

                # Migration for old setting name
                if "github_pat" in loaded_settings:
                    if "github_access_token" not in loaded_settings:
                        loaded_settings["github_access_token"] = \
                            loaded_settings.pop("github_pat")
                    else:
                        del loaded_settings["github_pat"]
                    log.info("Migrated old 'github_pat' setting.")

                # Merge loaded settings with defaults to ensure all keys exist
                settings = DEFAULT_SETTINGS.copy()
                settings.update(loaded_settings)
                return settings
            else:
                log.info(
                    f"Settings file not found. Creating with defaults "
                    f"at: {self.settings_file}"
                )
                self._save_settings(DEFAULT_SETTINGS.copy())
                return DEFAULT_SETTINGS.copy()
        except (json.JSONDecodeError, IOError) as e:
            log.error(f"Error loading settings: {e}. Reverting to defaults.",
                      exc_info=True)
            return DEFAULT_SETTINGS.copy()

    def _save_settings(self, settings_data: Dict[str, Any]):
        """Saves the provided settings data to the JSON file atomically."""
        try:
            # Ensure the directory exists before writing
            os.makedirs(os.path.dirname(self.settings_file), exist_ok=True)
            temp_file = self.settings_file + ".tmp"
            with open(temp_file, 'w', encoding='utf-8') as f:
                json.dump(settings_data, f, indent=4)
            # Atomic move/rename
            os.replace(temp_file, self.settings_file)
        except IOError as e:
            log.error(f"Error saving settings to {self.settings_file}: {e}",
                      exc_info=True)

    def get(self, key: str, default: Any = None) -> Any:
        """
        Gets a setting value by key.

        Args:
            key: The key of the setting to retrieve.
            default: The value to return if the key is not found.

        Returns:
            The setting value.
        """
        return self.settings.get(key, DEFAULT_SETTINGS.get(key, default))

    def set(self, key: str, value: Any, save_immediately: bool = True):
        """

        Sets a setting value by key.
        Args:
            key: The key of the setting to set.
            value: The new value for the setting.
            save_immediately: If True, saves all settings to disk immediately.
        """
        self.settings[key] = value
        if save_immediately:
            self.save()

    def save(self):
        """Saves the current settings to the disk."""
        self._save_settings(self.settings)


# Singleton instance to be used across the application
settings_manager = SettingsManager()
```

### File: `/app_core/source_control_manager.py`

```python
# PuffinPyEditor/app_core/source_control_manager.py
import os
import re
import git
from git import Repo, GitCommandError, InvalidGitRepositoryError
from typing import List, Optional
from PyQt6.QtCore import QObject, QThread, pyqtSignal
from utils.logger import log
import configparser


class GitWorker(QObject):
    """
    Worker that runs all GitPython operations in a background thread.
    """
    summaries_ready = pyqtSignal(dict)
    status_ready = pyqtSignal(list, list, str)
    error_occurred = pyqtSignal(str)
    operation_success = pyqtSignal(str, dict)
    git_config_ready = pyqtSignal(str, str)

    def _get_author(self, repo: Repo) -> Optional[git.Actor]:
        """Reads git config and returns a git.Actor. Emits error if missing."""
        try:
            with repo.config_reader() as cr:
                name = cr.get_value('user', 'name')
                email = cr.get_value('user', 'email')
            return git.Actor(name, email)
        except (configparser.NoSectionError, configparser.NoOptionError):
            self.error_occurred.emit(
                "Git user config is missing. Please set it in "
                "Preferences > Source Control."
            )
            return None

    def get_git_config(self):
        """Reads the global Git user configuration."""
        try:
            git_cmd = git.Git()
            name = git_cmd.config('--global', '--get', 'user.name')
            email = git_cmd.config('--global', '--get', 'user.email')
            self.git_config_ready.emit(name, email)
        except GitCommandError:
            log.warning("Global Git user.name or user.email is not set.")
            self.git_config_ready.emit("", "")

    def set_git_config(self, name: str, email: str):
        """Sets the global Git user configuration."""
        try:
            git_cmd = git.Git()
            if name:
                git_cmd.config('--global', 'user.name', name)
            if email:
                git_cmd.config('--global', 'user.email', email)
            self.operation_success.emit("Global Git config updated.", {})
        except GitCommandError as e:
            log.error(f"Failed to set git config: {e}")
            self.error_occurred.emit(f"Failed to set Git config: {e}")

    def set_default_branch(self):
        """Sets the global Git config to use 'main' for new repositories."""
        try:
            git.Git().config('--global', 'init.defaultBranch', 'main')
            log.info("Set global init.defaultBranch to 'main'.")
            self.operation_success.emit(
                "Default branch for new repos is now 'main'.", {}
            )
        except GitCommandError as e:
            self.error_occurred.emit(f"Could not set default branch: {e}")

    def get_multiple_repo_summaries(self, repo_paths: List[str]):
        summaries = {}
        for path in repo_paths:
            try:
                repo = Repo(path, search_parent_directories=True)
                if repo.bare:
                    summaries[path] = {'branch': '(bare repo)',
                                       'commit': 'N/A'}
                elif not repo.head.is_valid():
                    summaries[path] = {'branch': '(no commits)',
                                       'commit': 'N/A'}
                else:
                    summaries[path] = {
                        'branch': repo.active_branch.name,
                        'commit': repo.head.commit.hexsha[:7]
                    }
            except InvalidGitRepositoryError:
                pass
            except Exception as e:
                log.error(f"Error getting Git summary for {path}: {e}")
                summaries[path] = {'branch': '(error)', 'commit': 'N/A'}
        self.summaries_ready.emit(summaries)

    def get_status(self, repo_path: str):
        try:
            repo = Repo(repo_path)
            staged = [item.a_path for item in repo.index.diff('HEAD')]
            unstaged = [item.a_path for item in repo.index.diff(None)]
            untracked = repo.untracked_files
            self.status_ready.emit(staged, unstaged + untracked, repo_path)
        except (InvalidGitRepositoryError, ValueError) as e:
            err_msg = (
                f"Git Status for '{os.path.basename(repo_path)}' "
                f"failed: {e}"
            )
            self.error_occurred.emit(err_msg)

    def commit_files(self, repo_path: str, message: str):
        try:
            repo = Repo(repo_path)
            author = self._get_author(repo)
            if not author:
                return

            repo.git.add(A=True)
            if repo.is_dirty(untracked_files=True):
                repo.index.commit(message, author=author, committer=author)
                self.operation_success.emit(
                    "Changes committed", {'repo_path': repo_path}
                )
            else:
                self.operation_success.emit(
                    "No new changes to commit.",
                    {'repo_path': repo_path, 'no_changes': True}
                )
        except GitCommandError as e:
            self.error_occurred.emit(f"Git Commit failed: {e}")

    def push(self, repo_path: str, tag_name: Optional[str] = None):
        try:
            repo = Repo(repo_path)
            origin = repo.remotes.origin
            if tag_name:
                log.info(f"Pushing tag '{tag_name}' to remote '{origin.url}'...")
                origin.push(tag_name)
                self.operation_success.emit(
                    f"Tag '{tag_name}' pushed successfully", {}
                )
            else:
                active_branch = repo.active_branch.name
                log.info(
                    f"Pushing branch '{active_branch}' to remote "
                    f"'{origin.url}'..."
                )
                origin.push(refspec=f'{active_branch}:{active_branch}')
                self.operation_success.emit("Push successful", {})
        except GitCommandError as e:
            err_str = str(e).lower()
            if "authentication failed" in err_str:
                msg = "Authentication failed."
            else:
                msg = f"Git Push failed: {e}"
            self.error_occurred.emit(msg)

    def pull(self, repo_path: str):
        try:
            repo = Repo(repo_path)
            origin = repo.remotes.origin
            log.info(f"Pulling from remote '{origin.url}'...")
            origin.pull()
            self.operation_success.emit("Pull successful", {})
            self.get_status(repo_path)
        except GitCommandError as e:
            self.error_occurred.emit(f"Git Pull failed: {e}")

    def clone_repo(self, url: str, path: str, branch: Optional[str] = None):
        try:
            target_dir = os.path.join(
                path, os.path.basename(url).replace('.git', '')
            )
            kwargs = {'branch': branch} if branch else {}
            log_msg = (
                f"Cloning '{url}' (branch: {branch or 'default'}) "
                f"into '{target_dir}'"
            )
            log.info(log_msg)
            Repo.clone_from(url, target_dir, **kwargs)
            self.operation_success.emit(
                "Clone successful", {"path": target_dir}
            )
        except GitCommandError as e:
            err_str = str(e).lower()
            if "not found in upstream origin" in err_str:
                msg = f"Branch '{branch}' not found in the remote repository."
            elif "authentication failed" in err_str:
                msg = ("Authentication failed. Repository may be private or "
                       "URL is incorrect.")
            else:
                msg = f"Clone failed: {e}"
            self.error_occurred.emit(msg)

    def create_tag(self, repo_path: str, tag: str, title: str):
        try:
            repo = Repo(repo_path)
            author = self._get_author(repo)
            if not author:
                return

            if not repo.head.is_valid():
                log.info("No commits found. Creating initial commit.")
                if repo.is_dirty(untracked_files=True):
                    repo.git.add(A=True)
                    repo.index.commit(
                        "Initial commit for release",
                        author=author, committer=author
                    )
                else:
                    self.error_occurred.emit(
                        "Cannot tag an empty project with no files."
                    )
                    return

            if tag in repo.tags:
                log.warning(f"Tag '{tag}' already exists. Re-creating it.")
                repo.delete_tag(tag)
            repo.create_tag(tag, message=title)
            self.operation_success.emit(f"Tag created: {tag}", {})
        except GitCommandError as e:
            self.error_occurred.emit(f"Failed to create tag: {e}")

    def delete_tag(self, repo_path: str, tag: str):
        try:
            repo = Repo(repo_path)
            repo.delete_tag(tag)
            self.operation_success.emit(f"Local tag '{tag}' deleted.", {})
        except GitCommandError as e:
            self.error_occurred.emit(f"Failed to delete local tag '{tag}': {e}")

    def delete_remote_tag(self, repo_path: str, tag: str):
        try:
            repo = Repo(repo_path)
            repo.remotes.origin.push(refspec=f":{tag}")
            self.operation_success.emit(f"Remote tag '{tag}' deleted.", {})
        except GitCommandError as e:
            self.error_occurred.emit(
                f"Failed to delete remote tag '{tag}': {e}"
            )

    def publish_repo(self, path: str, url: str):
        try:
            repo = Repo.init(path)
            author = self._get_author(repo)
            if not author:
                return
            repo.git.branch('-M', 'main')
            if (repo.is_dirty(untracked_files=True) and
                    not repo.head.is_valid()):
                repo.git.add(A=True)
                repo.index.commit(
                    "Initial commit", author=author, committer=author
                )
            if 'origin' in repo.remotes:
                repo.remotes.origin.set_url(url)
            else:
                repo.create_remote('origin', url)
            repo.remotes.origin.push(refspec='main:main', set_upstream=True)
            self.operation_success.emit(
                f"Successfully published to {url}", {'repo_path': path}
            )
        except GitCommandError as e:
            log.error(f"Publish failed: {e}", exc_info=True)
            self.error_occurred.emit(f"Publish failed: {e}")

    def link_to_remote(self, local_path: str, remote_url: str):
        try:
            repo = Repo.init(local_path)
            if 'origin' in repo.remotes:
                repo.remotes.origin.set_url(remote_url)
            else:
                repo.create_remote('origin', remote_url)
            repo.remotes.origin.fetch()
            remote_head = repo.remote().refs.HEAD
            if remote_head.is_valid():
                branch_name = remote_head.reference.name.split('/')[-1]
            else:
                branch_name = 'main'
            repo.git.branch('-M', branch_name)
            if remote_head.is_valid():
                repo.git.reset('--soft', f'origin/{branch_name}')
            if (repo.is_dirty(untracked_files=True) and
                    not repo.head.is_valid()):
                author = self._get_author(repo)
                if not author:
                    return
                repo.git.add(A=True)
                repo.index.commit(
                    "Initial commit after linking to remote",
                    author=author, committer=author
                )
            self.operation_success.emit(
                f"Successfully linked to {remote_url}", {}
            )
        except GitCommandError as e:
            self.error_occurred.emit(f"Failed to link repository: {e}")

    def fix_main_master_divergence(self, repo_path: str):
        try:
            repo = Repo(repo_path)
            log.info(f"Fixing branch mismatch in {repo_path}")
            repo.git.branch('-M', 'master', 'main')
            repo.git.push('--force', '-u', 'origin', 'main')
            repo.git.push('origin', '--delete', 'master')
            self.operation_success.emit(
                "'main' is now the primary branch.", {'repo_path': repo_path}
            )
        except GitCommandError as e:
            self.error_occurred.emit(f"Failed to fix branch mismatch: {e}")


class SourceControlManager(QObject):
    summaries_ready = pyqtSignal(dict)
    status_updated = pyqtSignal(list, list, str)
    git_error = pyqtSignal(str)
    git_success = pyqtSignal(str, dict)
    git_config_ready = pyqtSignal(str, str)

    _request_summaries = pyqtSignal(list)
    _request_status = pyqtSignal(str)
    _request_commit = pyqtSignal(str, str)
    _request_push = pyqtSignal(str, str)
    _request_pull = pyqtSignal(str)
    _request_clone = pyqtSignal(str, str, object)
    _request_publish = pyqtSignal(str, str)
    _request_create_tag = pyqtSignal(str, str, str)
    _request_delete_tag = pyqtSignal(str, str)
    _request_delete_remote_tag = pyqtSignal(str, str)
    _request_link_to_remote = pyqtSignal(str, str)
    _request_get_git_config = pyqtSignal()
    _request_set_git_config = pyqtSignal(str, str)
    _request_fix_branches = pyqtSignal(str)
    _request_set_default_branch = pyqtSignal()

    def __init__(self, parent: Optional[QObject] = None):
        super().__init__(parent)
        self.thread = QThread()
        self.worker = GitWorker()
        self.worker.moveToThread(self.thread)
        self._request_summaries.connect(self.worker.get_multiple_repo_summaries)
        self._request_status.connect(self.worker.get_status)
        self._request_commit.connect(self.worker.commit_files)
        self._request_push.connect(self.worker.push)
        self._request_pull.connect(self.worker.pull)
        self._request_clone.connect(self.worker.clone_repo)
        self._request_publish.connect(self.worker.publish_repo)
        self._request_create_tag.connect(self.worker.create_tag)
        self._request_delete_tag.connect(self.worker.delete_tag)
        self._request_delete_remote_tag.connect(self.worker.delete_remote_tag)
        self._request_link_to_remote.connect(self.worker.link_to_remote)
        self._request_get_git_config.connect(self.worker.get_git_config)
        self._request_set_git_config.connect(self.worker.set_git_config)
        self._request_fix_branches.connect(
            self.worker.fix_main_master_divergence)
        self._request_set_default_branch.connect(
            self.worker.set_default_branch)
        self.worker.summaries_ready.connect(self.summaries_ready)
        self.worker.status_ready.connect(self.status_updated)
        self.worker.error_occurred.connect(self.git_error)
        self.worker.operation_success.connect(self.git_success)
        self.worker.git_config_ready.connect(self.git_config_ready)
        self.thread.start()

    @staticmethod
    def parse_git_url(url: str) -> tuple[Optional[str], Optional[str]]:
        if match := re.search(r"github\.com/([^/]+)/([^/.]+)", url):
            return match.group(1), match.group(2)
        if match := re.search(r"github\.com:([^/]+)/([^/.]+)", url):
            return match.group(1), match.group(2)
        return None, None

    def get_local_branches(self, repo_path: str) -> List[str]:
        try:
            return [b.name for b in Repo(repo_path).branches]
        except (InvalidGitRepositoryError, TypeError):
            return []

    def get_git_config(self):
        self._request_get_git_config.emit()

    def set_git_config(self, name: str, email: str):
        self._request_set_git_config.emit(name, email)

    def set_default_branch_to_main(self):
        self._request_set_default_branch.emit()

    def link_to_remote(self, path: str, url: str):
        self._request_link_to_remote.emit(path, url)

    def fix_branch_mismatch(self, path: str):
        self._request_fix_branches.emit(path)

    def get_summaries(self, paths: List[str]):
        self._request_summaries.emit(paths)

    def get_status(self, path: str):
        self._request_status.emit(path)

    def commit_files(self, path: str, msg: str):
        self._request_commit.emit(path, msg)

    def push(self, path: str):
        self._request_push.emit(path, None)

    def push_specific_tag(self, path: str, tag_name: str):
        self._request_push.emit(path, tag_name)

    def pull(self, path: str):
        self._request_pull.emit(path)

    def clone_repo(self, url: str, path: str, branch: Optional[str] = None):
        self._request_clone.emit(url, path, branch)

    def publish_repo(self, path: str, url: str):
        self._request_publish.emit(path, url)

    def create_tag(self, path: str, tag: str, title: str):
        self._request_create_tag.emit(path, tag, title)

    def delete_tag(self, path: str, tag: str):
        self._request_delete_tag.emit(path, tag)

    def delete_remote_tag(self, path: str, tag: str):
        self._request_delete_remote_tag.emit(path, tag)

    def shutdown(self):
        if self.thread and self.thread.isRunning():
            log.info("Shutting down SourceControlManager thread.")
            self.thread.quit()
            if not self.thread.wait(3000):
                log.warning(
                    "SourceControlManager thread did not shut down "
                    "gracefully. Terminating."
                )
                self.thread.terminate()
```

### File: `/app_core/theme_manager.py`

```python
# PuffinPyEditor/app_core/theme_manager.py
import os
import json
import base64
import shutil
from typing import Dict, Any, Optional
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QColor

from app_core.settings_manager import settings_manager
from utils.logger import log, get_app_data_path
from utils.helpers import get_base_path

SVG_ARROW_PATHS = {'up': "M4 10 L8 6 L12 10", 'down': "M4 6 L8 10 L12 6"}

APP_BASE_PATH = get_base_path()
APP_DATA_ROOT = get_app_data_path()
CUSTOM_THEMES_FILE_PATH = os.path.join(APP_DATA_ROOT, "custom_themes.json")
DEFAULT_CUSTOM_THEMES_FILE_PATH = os.path.join(APP_BASE_PATH, "assets", "themes", "custom_themes.json")
ICON_COLORS_FILE_PATH = os.path.join(APP_DATA_ROOT, "icon_colors.json")
DEFAULT_ICON_COLORS_FILE_PATH = os.path.join(APP_BASE_PATH, "assets", "themes", "icon_colors.json")

# --- MODIFICATION: Added missing color keys to both built-in themes ---
BUILT_IN_THEMES = {
    "puffin_dark": {
        "name": "Puffin Dark", "author": "PuffinPy", "type": "dark", "is_custom": False,
        "colors": {
            "window.background": "#2f383e", "sidebar.background": "#2a3338", "editor.background": "#272e33",
            "editor.foreground": "#d3c6aa", "editor.selectionBackground": "#264f78",
            "editor.lineHighlightBackground": "#3a4145", "editor.matchingBracketBackground": "#545e62",
            "editor.matchingBracketForeground": "#d3c6aa", "editor.breakpoint.color": "#dc143c",
            "editorGutter.background": "#2f383e", "editorGutter.foreground": "#5f6c6d",
            "editorLineNumber.foreground": "#5f6c6d", "editorLineNumber.activeForeground": "#d3c6aa",
            "menu.background": "#3a4145", "menu.foreground": "#d3c6aa", "statusbar.background": "#282f34",
            "statusbar.foreground": "#d3c6aa", "tab.activeBackground": "#272e33",
            "tab.inactiveBackground": "#2f383e", "tab.activeForeground": "#d3c6aa",
            "tab.inactiveForeground": "#5f6c6d", "button.background": "#424d53",
            "button.foreground": "#d3c6aa", "input.background": "#3a4145", "input.foreground": "#d3c6aa",
            "input.border": "#5f6c6d", "scrollbar.background": "#2f383e", "scrollbar.handle": "#424d53",
            "scrollbar.handleHover": "#545e62", "scrollbar.handlePressed": "#545e62",
            "accent": "#83c092", "syntax.keyword": "#e67e80", "syntax.operator": "#d3c6aa",
            "syntax.brace": "#d3c6aa", "syntax.decorator": "#dbbc7f", "syntax.self": "#e67e80",
            "syntax.className": "#dbbc7f", "syntax.functionName": "#83c092", "syntax.comment": "#5f6c6d",
            "syntax.string": "#a7c080", "syntax.docstring": "#5f6c6d", "syntax.number": "#d699b6",
            "tree.indentationGuides.stroke": "#5f6c6d", "tree.trace.color": "#83c092",
            "git.status.foreground": "#87ceeb"
        }
    },
    "puffin_light": {
        "name": "Puffin Light", "author": "PuffinPy", "type": "light", "is_custom": False,
        "colors": {
            "window.background": "#f5f5f5", "sidebar.background": "#ECECEC", "editor.background": "#ffffff",
            "editor.foreground": "#000000", "editor.selectionBackground": "#add6ff",
            "editor.lineHighlightBackground": "#e0e8f0", "editor.matchingBracketBackground": "#c0c8d0",
            "editor.matchingBracketForeground": "#000000", "editor.breakpoint.color": "#ff0000",
            "editorGutter.background": "#f5f5f5", "editorGutter.foreground": "#505050",
            "editorLineNumber.foreground": "#9e9e9e", "editorLineNumber.activeForeground": "#000000",
            "menu.background": "#e0e0e0", "menu.foreground": "#000000", "statusbar.background": "#007acc",
            "statusbar.foreground": "#ffffff", "tab.activeBackground": "#ffffff",
            "tab.inactiveBackground": "#f5f5f5", "tab.activeForeground": "#000000",
            "tab.inactiveForeground": "#555555", "button.background": "#E0E0E0",
            "button.foreground": "#000000", "input.background": "#ffffff", "input.foreground": "#000000",
            "input.border": "#D0D0D0", "scrollbar.background": "#f0f0f0", "scrollbar.handle": "#cccccc",
            "scrollbar.handleHover": "#bbbbbb", "scrollbar.handlePressed": "#aaaaaa",
            "accent": "#007ACC", "syntax.keyword": "#0000ff", "syntax.operator": "#000000",
            "syntax.brace": "#a00050", "syntax.decorator": "#267f99", "syntax.self": "#800080",
            "syntax.className": "#267f99", "syntax.functionName": "#795e26", "syntax.comment": "#008000",
            "syntax.string": "#a31515", "syntax.docstring": "#a31515", "syntax.number": "#098658",
            "tree.indentationGuides.stroke": "#D0D0D0", "tree.trace.color": "#007ACC",
            "git.status.foreground": "#007ACC"
        }
    }
}


def get_arrow_svg_uri(direction: str, color: str) -> str:
    path_data = SVG_ARROW_PATHS.get(direction, "");
    if not path_data: return ""
    svg_content = f'<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 16 16"><path fill="{color}" d="{path_data}" /></svg>'
    b64_content = base64.b64encode(svg_content.encode('utf-8')).decode('utf-8');
    return f"data:image/svg+xml;base64,{b64_content}"


class ThemeManager:
    def __init__(self):
        self.all_themes_data: Dict[str, Dict] = {}
        self.icon_colors: Dict[str, str] = {}
        self.current_theme_id: str = "puffin_dark"
        self.current_theme_data: Dict[str, Any] = {}
        self.reload_themes()
        log.info(f"ThemeManager initialized. Current theme: '{self.current_theme_id}'")

    def reload_themes(self):
        self.icon_colors = self._load_icon_colors()
        self.all_themes_data = self._load_all_themes()
        last_theme_id = settings_manager.get("last_theme_id", "puffin_dark")
        if last_theme_id not in self.all_themes_data:
            last_theme_id = "puffin_dark"
            settings_manager.set("last_theme_id", last_theme_id)
        self.current_theme_id = last_theme_id
        self.set_theme(self.current_theme_id)

    def _load_icon_colors(self) -> Dict[str, str]:
        """Loads default and user icon colors, with user settings overriding defaults."""
        colors = {}
        if not os.path.exists(ICON_COLORS_FILE_PATH) and os.path.exists(DEFAULT_ICON_COLORS_FILE_PATH):
            try:
                os.makedirs(os.path.dirname(ICON_COLORS_FILE_PATH), exist_ok=True)
                shutil.copy2(DEFAULT_ICON_COLORS_FILE_PATH, ICON_COLORS_FILE_PATH)
                log.info(f"Copied default icon colors to {ICON_COLORS_FILE_PATH}")
            except Exception as e:
                log.error(f"Failed to copy default icon colors: {e}")

        try:
            with open(DEFAULT_ICON_COLORS_FILE_PATH, 'r') as f:
                colors.update(json.load(f))
            if os.path.exists(ICON_COLORS_FILE_PATH):
                with open(ICON_COLORS_FILE_PATH, 'r') as f:
                    colors.update(json.load(f))
        except (IOError, json.JSONDecodeError) as e:
            log.error(f"Could not load icon color schemes: {e}")

        return colors

    def _load_all_themes(self) -> Dict[str, Dict]:
        all_themes = BUILT_IN_THEMES.copy()
        if not os.path.exists(CUSTOM_THEMES_FILE_PATH) and os.path.exists(DEFAULT_CUSTOM_THEMES_FILE_PATH):
            try:
                os.makedirs(os.path.dirname(CUSTOM_THEMES_FILE_PATH), exist_ok=True)
                shutil.copy2(DEFAULT_CUSTOM_THEMES_FILE_PATH, CUSTOM_THEMES_FILE_PATH)
            except Exception as e:
                log.error(f"Failed to copy default custom themes: {e}")
        if os.path.exists(CUSTOM_THEMES_FILE_PATH):
            try:
                with open(CUSTOM_THEMES_FILE_PATH, 'r') as f:
                    custom_themes = json.load(f)
                    for theme in custom_themes.values(): theme['is_custom'] = True
                    all_themes.update(custom_themes)
            except Exception as e:
                log.error(f"Error loading custom themes: {e}")
        return all_themes

    def get_available_themes_for_ui(self) -> Dict[str, str]:
        return {tid: d.get("name", tid) for tid, d in
                sorted(self.all_themes_data.items(), key=lambda i: i[1].get("name", i[0]).lower())}

    def set_theme(self, theme_id: str, app_instance: Optional[QApplication] = None):
        if theme_id not in self.all_themes_data: theme_id = "puffin_dark"
        self.current_theme_id = theme_id
        self.current_theme_data = self.all_themes_data.get(theme_id, {})
        
        if 'colors' not in self.current_theme_data:
            log.warning(f"Theme '{theme_id}' is missing the 'colors' dictionary. UI may not render correctly.")
        
        if 'colors' in self.current_theme_data:
            self.current_theme_data['colors']['icon.colors'] = self.icon_colors

        settings_manager.set("last_theme_id", theme_id)
        self.apply_theme_to_app(app_instance or QApplication.instance())
        log.info(f"Theme set to '{self.current_theme_data.get('name', 'Unknown')}'")

    def apply_theme_to_app(self, app: Optional[QApplication]):
        if not app or not self.current_theme_data: return
        colors = self.current_theme_data.get("colors", {})

        def c(key: str, fb: str) -> str: return colors.get(key, fb)

        def adj(h: str, f: int) -> str: c = QColor(h);return c.lighter(f).name() if f > 100 else c.darker(f).name()

        ac, wb, bb, bf = c('accent', '#83c092'), c('window.background', '#2f383e'), c('button.background',
                                                                                      '#424d53'), c('button.foreground',
                                                                                                    '#d3c6aa')
        ib, igf, ibd, sb = c('input.background', '#3a4145'), c('input.foreground', '#d3c6aa'), c('input.border',
                                                                                                 '#5f6c6d'), c(
            'sidebar.background', '#2a3338')
        ca, su, sd = get_arrow_svg_uri('down', igf), get_arrow_svg_uri('up', igf), get_arrow_svg_uri('down', igf)
        ss = f"""QWidget{{background-color:{wb};color:{igf};border:none;}}QMainWindow,QDialog{{background-color:{wb};}}QPushButton{{background-color:{bb};color:{bf};border:1px solid {ibd};border-radius:4px;padding:6px 12px;min-width:80px;}}QPushButton:hover{{background-color:{adj(bb, 115)};border-color:{ac};}}QPushButton:pressed{{background-color:{adj(bb, 95)};}}QPushButton:disabled{{background-color:{adj(bb, 105)};color:{c('editorGutter.foreground', '#888')};border-color:{adj(ibd, 110)};}}QSplitter::handle{{background-color:{sb};width:1px;image:none;}}QSplitter::handle:hover{{background-color:{ac};}}QMenuBar{{background-color:{adj(wb, 105)};border-bottom:1px solid {ibd};}}QMenuBar::item{{padding:6px 12px;}}QMenuBar::item:selected{{background-color:{ac};color:{c('button.foreground', '#000')};}}QMenu{{background-color:{c('menu.background', '#3a4145')};border:1px solid {ibd};padding:4px;}}QMenu::item{{padding:6px 24px;}}QMenu::item:selected{{background-color:{ac};color:{c('button.foreground', '#000')};}}QTabWidget::pane{{border:none;}}QTabBar::tab{{background:transparent;color:{c('tab.inactiveForeground', '#5f6c6d')};padding:8px 15px;border:none;border-bottom:2px solid transparent;}}QTabBar::tab:hover{{background:{adj(wb, 110)};}}QTabBar::tab:selected{{color:{c('tab.activeForeground', '#d3c6aa')};border-bottom:2px solid {ac};}}QToolButton{{background:transparent;border:none;border-radius:4px;padding:4px;}}QToolButton:hover{{background-color:{adj(bb, 120)};}}QAbstractItemView{{background-color:{sb};outline:0;}}QTreeView,QListWidget,QTableWidget,QTreeWidget{{alternate-background-color:{adj(sb, 103)};}}QTreeView::item:hover,QListWidget::item:hover{{background-color:{adj(sb, 120)};}}QTreeView::item:selected,QListWidget::item:selected{{background-color:{ac};color:{c('button.foreground', '#000')};}}QHeaderView::section{{background-color:{adj(sb, 110)};padding:4px;border:1px solid {wb};}}QDockWidget::title{{background-color:{adj(wb, 105)};text-align:left;padding:5px;border-bottom:1px solid {ibd};}}QGroupBox{{font-weight:bold;border:1px solid {ibd};border-radius:4px;margin-top:10px;}}QGroupBox::title{{subcontrol-origin:margin;subcontrol-position:top left;padding:0 5px 0 5px;left:10px;background-color:{wb};}}QLineEdit,QTextEdit,QPlainTextEdit,QAbstractSpinBox,QComboBox{{background-color:{ib};border:1px solid {ibd};border-radius:4px;padding:5px;}}QLineEdit:focus,QAbstractSpinBox:focus,QComboBox:focus,QTextEdit:focus,QPlainTextEdit:focus{{border:1px solid {ac};}}QComboBox::drop-down{{subcontrol-origin:padding;subcontrol-position:top right;width:20px;border-left:1px solid {ibd};}}QComboBox::down-arrow{{image:url({ca});width:8px;height:8px;}}QSpinBox{{padding-right:22px;}}QSpinBox::up-button,QSpinBox::down-button{{subcontrol-origin:border;width:22px;background-color:transparent;border-left:1px solid {ibd};}}QSpinBox::up-button:hover,QSpinBox::down-button:hover{{background-color:{adj(ib, 120)};}}QSpinBox::up-button{{subcontrol-position:top right;}}QSpinBox::down-button{{subcontrol-position:bottom right;}}QSpinBox::up-arrow{{image:url({su});width:8px;height:8px;}}QSpinBox::down-arrow{{image:url({sd});width:8px;height:8px;}}QStatusBar{{background-color:{c('statusbar.background', '#282f34')};border-top:1px solid {ibd};color:{c('statusbar.foreground', '#d3c6aa')};}}QScrollBar:vertical{{width:10px;}}QScrollBar:horizontal{{height:10px;}}QScrollBar::handle{{background:{c('scrollbar.handle', '#424d53')};border-radius:5px;min-height:20px;}}QScrollBar::handle:hover{{background:{c('scrollbar.handleHover', '#545e62')};}}QScrollBar::add-line,QScrollBar::sub-line{{height:0px;width:0px;}}QScrollBar::add-page,QScrollBar::sub-page{{background:none;}}"""
        app.setStyleSheet(ss)


theme_manager = ThemeManager()
```

### File: `/app_core/update_manager.py`

```python
# PuffinPyEditor/app_core/update_manager.py
import requests
from packaging import version
from typing import Dict
from PyQt6.QtCore import QObject, pyqtSignal
from .settings_manager import settings_manager
from utils.versioning import APP_VERSION
from utils.logger import log


class UpdateManager(QObject):
    """
    Checks for new application versions from a configured GitHub repository.
    """
    update_check_finished = pyqtSignal(dict)

    def check_for_updates(self):
        """
        Fetches the latest release data from GitHub and compares it with the
        current application version. Emits `update_check_finished`.
        """
        log.info(f"Checking for updates... Current version: {APP_VERSION}")

        active_repo_id = settings_manager.get("active_update_repo_id")
        if not active_repo_id:
            msg = "No active repository set for updates in Preferences."
            log.warning(f"Update check failed: {msg}")
            self.update_check_finished.emit({"error": msg})
            return

        all_repos = settings_manager.get("source_control_repos", [])
        repo_config = next(
            (r for r in all_repos if r.get("id") == active_repo_id), None
        )

        if not repo_config:
            msg = f"Update repo with ID '{active_repo_id}' not found."
            log.error(f"Update check failed: {msg}")
            self.update_check_finished.emit({"error": msg})
            return

        owner = repo_config.get("owner")
        repo = repo_config.get("repo")

        if not owner or not repo:
            msg = f"Repo '{repo_config.get('name')}' is misconfigured."
            log.error(f"Update check failed: {msg}")
            self.update_check_finished.emit({"error": msg})
            return

        api_url = f"https://api.github.com/repos/{owner}/{repo}/releases/latest"
        log.info(f"Checking for latest release at: {api_url}")

        try:
            response = requests.get(api_url, timeout=15)
            response.raise_for_status()
            release_data = response.json()

            latest_version_tag = release_data.get("tag_name", "").lstrip('v')
            if not latest_version_tag:
                msg = "Latest release has no version tag."
                self.update_check_finished.emit({"error": msg})
                return

            if version.parse(latest_version_tag) > version.parse(APP_VERSION):
                log.info(f"New version found: {latest_version_tag}")
                result: Dict = {
                    "update_available": True,
                    "latest_version": latest_version_tag,
                    "release_notes": release_data.get(
                        "body", "No release notes provided."
                    ),
                    "download_url": None
                }
                # Find the first .zip asset, as this is what the updater expects
                for asset in release_data.get("assets", []):
                    if asset.get("name", "").lower().endswith(".zip"):
                        result["download_url"] = asset.get(
                            "browser_download_url")
                        break

                if result["download_url"]:
                    self.update_check_finished.emit(result)
                else:
                    log.warning(
                        "New version found, but no suitable .zip asset "
                        "was available for download."
                    )
                    self.update_check_finished.emit(
                        {"update_available": False})
            else:
                log.info("Application is up to date.")
                self.update_check_finished.emit({"update_available": False})

        except requests.exceptions.HTTPError as e:
            msg = f"Could not fetch update info (HTTP {e.response.status_code})."
            log.error(f"{msg} URL: {api_url}")
            self.update_check_finished.emit({"error": msg})
        except requests.exceptions.RequestException as e:
            msg = f"Network error checking for updates: {e}"
            log.error(msg)
            self.update_check_finished.emit(
                {"error": "A network error occurred."})
        except Exception as e:
            msg = f"An unexpected error occurred during update check: {e}"
            log.critical(msg, exc_info=True)
            self.update_check_finished.emit(
                {"error": "An unexpected error occurred."})
```

### File: `/ui/widgets/__init__.py`

```python

```

### File: `/ui/widgets/breakpoint_area.py`

```python
# PuffinPyEditor/ui/widgets/breakpoint_area.py
from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QMouseEvent, QPainter, QColor
from PyQt6.QtCore import QSize, pyqtSignal, Qt

from utils.logger import log


class BreakpointArea(QWidget):
    """
    A gutter widget that displays and handles breakpoint toggling with a
    clear hover effect.
    """
    breakpoint_toggled = pyqtSignal(int)

    def __init__(self, editor_widget: 'EditorWidget'):
        super().__init__(editor_widget)
        self.editor = editor_widget
        self.setMouseTracking(True)
        self.hovered_line = -1

    def sizeHint(self) -> QSize:
        return QSize(self.minimumSizeHint().width(), 0)

    def minimumSizeHint(self) -> QSize:
        return QSize(20, 0)

    def enterEvent(self, event):
        self.update()  # Redraw to show potential hover
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.hovered_line = -1
        self.update()  # Redraw to remove hover
        super().leaveEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent):
        """Calculates which line number is under the cursor."""
        try:
            # Use the editor's cursorForPosition method, which is the most reliable way
            # to determine the block (line) at a specific y-coordinate.
            cursor = self.editor.text_area.cursorForPosition(event.pos())
            line_num = -1
            if cursor.block().isValid():
                line_num = cursor.block().blockNumber() + 1

            if line_num != self.hovered_line:
                self.hovered_line = line_num
                self.update()
        except Exception as e:
            log.error(f"Error in BreakpointArea mouseMoveEvent: {e}", exc_info=False)
        super().mouseMoveEvent(event)

    def mousePressEvent(self, event: QMouseEvent) -> None:
        """Toggles the breakpoint on the hovered line."""
        if event.button() == Qt.MouseButton.LeftButton and self.hovered_line != -1:
            self.breakpoint_toggled.emit(self.hovered_line)
        super().mousePressEvent(event)

    def paintEvent(self, event) -> None:
        """Paints the breakpoints and hover indicators."""
        try:
            painter = QPainter(self)
        except Exception as e:
            log.error(f"Could not create QPainter for breakpoints: {e}")
            return

        colors = self.editor.theme_manager.current_theme_data.get('colors', {})
        bg_color = QColor(colors.get('editorGutter.background', '#2c313a'))
        breakpoint_color = QColor(colors.get('editor.breakpoint.color', 'crimson'))

        # A more visible hover color
        hover_base_color = QColor(colors.get('editorGutter.foreground', '#888888'))
        hover_color = QColor(hover_base_color)
        hover_color.setAlpha(128)  # semi-transparent

        painter.fillRect(event.rect(), bg_color)

        # Get editor state
        text_area = self.editor.text_area
        content_offset = text_area.contentOffset()

        # Iterate through visible blocks to draw markers
        block = text_area.firstVisibleBlock()
        while block.isValid():
            block_top = text_area.blockBoundingGeometry(block).translated(content_offset).top()

            # Stop if we've drawn past the visible area
            if block_top > event.rect().bottom():
                break

            if block.isVisible():
                line_num = block.blockNumber() + 1
                radius = 5  # Larger radius for better visibility
                center_x = self.width() / 2
                # Center the dot vertically within the line's bounding rect
                center_y = block_top + (text_area.blockBoundingRect(block).height() / 2)

                painter.setPen(Qt.PenStyle.NoPen)

                if line_num in self.editor.breakpoints:
                    painter.setBrush(breakpoint_color)
                    painter.drawEllipse(int(center_x - radius), int(center_y - radius), int(radius * 2),
                                        int(radius * 2))
                elif line_num == self.hovered_line:
                    # Draw a hollow circle for the hover indicator
                    painter.setBrush(hover_color)
                    painter.drawEllipse(int(center_x - radius), int(center_y - radius), int(radius * 2),
                                        int(radius * 2))

            block = block.next()
```

### File: `/ui/widgets/find_panel.py`

```python
# /ui/widgets/find_panel.py
from typing import Optional, TYPE_CHECKING
from PyQt6.QtWidgets import (QWidget, QHBoxLayout, QVBoxLayout, QLineEdit,
                             QPushButton, QCheckBox, QToolButton, QFrame)
from PyQt6.QtGui import QTextDocument, QKeyEvent
from PyQt6.QtCore import Qt, pyqtSignal
import qtawesome as qta

from app_core.settings_manager import settings_manager
from app_core.theme_manager import theme_manager

# This is a super neat trick I learned to prevent circular import errors!
# It lets me use EditorWidget for type hinting without actually importing it at runtime.
if TYPE_CHECKING:
    from ..editor_widget import EditorWidget


class FindPanel(QFrame):
    """An integrated panel for find and replace operations."""
    # This signal tells the parent (the EditorWidget) to close me.
    close_requested = pyqtSignal()
    # This signal asks the main window to show a message in the status bar.
    status_message_requested = pyqtSignal(str, int)

    def __init__(self, parent: QWidget):
        super().__init__(parent)
        # This will be the editor widget this panel is currently controlling.
        self.editor: Optional["EditorWidget"] = None
        # Giving this an object name is great for styling with CSS-like QSS!
        self.setObjectName("FindPanelFrame")
        self._setup_ui()
        self._connect_signals()
        self.load_settings()
        self.update_theme()

    def _setup_ui(self):
        # This function builds the visual components of the panel.
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(5, 5, 5, 5)
        self.main_layout.setSpacing(5)

        find_layout = QHBoxLayout()
        self.toggle_button = QToolButton()
        self.toggle_button.setCheckable(True)
        self.toggle_button.setAutoRaise(True)
        self.toggle_button.setIcon(qta.icon('fa5s.chevron-right'))
        find_layout.addWidget(self.toggle_button)

        self.find_input = QLineEdit()
        self.find_input.setPlaceholderText("Find")
        find_layout.addWidget(self.find_input)

        self.find_prev_button = self._create_tool_button(
            'fa5s.arrow-up', "Find Previous (Shift+F3)")
        self.find_next_button = self._create_tool_button(
            'fa5s.arrow-down', "Find Next (F3)")
        self.close_button = self._create_tool_button(
            'fa5s.times', "Close (Esc)")
        find_layout.addWidget(self.find_prev_button)
        find_layout.addWidget(self.find_next_button)
        find_layout.addWidget(self.close_button)
        self.main_layout.addLayout(find_layout)

        # This widget holds the "replace" parts and can be hidden/shown.
        self.expandable_widget = QWidget()
        expandable_layout = QVBoxLayout(self.expandable_widget)
        expandable_layout.setContentsMargins(0, 5, 0, 0)
        expandable_layout.setSpacing(5)

        replace_layout = QHBoxLayout()
        self.replace_input = QLineEdit()
        self.replace_input.setPlaceholderText("Replace")
        self.replace_button = self._create_tool_button(
            'fa5s.exchange-alt', "Replace", text="Replace")
        self.replace_all_button = self._create_tool_button(
            'fa5s.magic', "Replace All", text="All")
        replace_layout.addWidget(self.replace_input)
        replace_layout.addWidget(self.replace_button)
        replace_layout.addWidget(self.replace_all_button)
        expandable_layout.addLayout(replace_layout)

        options_layout = QHBoxLayout()
        options_layout.setContentsMargins(25, 0, 0, 0)
        self.case_checkbox = QCheckBox("Case Sensitive")
        self.whole_word_checkbox = QCheckBox("Whole Word")
        options_layout.addWidget(self.case_checkbox)
        options_layout.addWidget(self.whole_word_checkbox)
        options_layout.addStretch()
        expandable_layout.addLayout(options_layout)

        self.main_layout.addWidget(self.expandable_widget)
        self.expandable_widget.hide()

    def _create_tool_button(
            self, icon_name: str, tooltip: str, text: Optional[str] = None
    ) -> QToolButton:
        # A helper function to make creating buttons less repetitive. DRY principle!
        button = QToolButton()
        button.setAutoRaise(True)
        button.setToolTip(tooltip)
        button.setProperty("icon_name", icon_name) # Store the icon name for theming
        if text:
            button.setText(text)
            button.setToolButtonStyle(
                Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        return button

    def _connect_signals(self):
        # Connecting all the button clicks to their functions.
        self.close_button.clicked.connect(self.close_requested.emit)
        self.toggle_button.toggled.connect(self.expandable_widget.setVisible)
        self.find_input.textChanged.connect(self._update_button_states)
        self.find_input.returnPressed.connect(self.find_next_button.click)
        self.find_next_button.clicked.connect(
            lambda: self._find(backwards=False))
        self.find_prev_button.clicked.connect(
            lambda: self._find(backwards=True))
        self.replace_button.clicked.connect(self._replace)
        self.replace_all_button.clicked.connect(self._replace_all)

    def connect_editor(self, editor: "EditorWidget"):
        # This method links the panel to a specific editor instance.
        self.editor = editor
        # Pre-fill the find input with any selected text.
        initial_text = editor.text_area.textCursor().selectedText()
        if initial_text:
            self.find_input.setText(initial_text)
        self.focus_find_input()
        self._update_button_states()

    def focus_find_input(self):
        self.find_input.setFocus()
        self.find_input.selectAll()

    def update_theme(self):
        # Applies the current theme's colors to the panel.
        colors = theme_manager.current_theme_data['colors']
        frame_bg = colors.get('sidebar.background', '#333')
        self.setStyleSheet(
            f"#FindPanelFrame {{ background-color: {frame_bg}; "
            f"border-bottom: 1px solid {colors.get('input.border')}; }}")
        # I'm re-applying icons here to make sure they get the new theme colors.
        for button in self.findChildren((QToolButton, QPushButton)):
            if icon_name := button.property("icon_name"):
                button.setIcon(qta.icon(icon_name))

    def keyPressEvent(self, event: QKeyEvent):
        # A key press event handler to allow closing the panel with the Escape key.
        if event.key() == Qt.Key.Key_Escape:
            self.close_requested.emit()
            return
        super().keyPressEvent(event)

    def load_settings(self):
        # Loads user preferences for search options.
        self.case_checkbox.setChecked(
            settings_manager.get("search_case_sensitive", False))
        self.whole_word_checkbox.setChecked(
            settings_manager.get("search_whole_word", False))

    def save_settings(self):
        # Saves user preferences for search options.
        settings_manager.set(
            "search_case_sensitive", self.case_checkbox.isChecked())
        settings_manager.set(
            "search_whole_word", self.whole_word_checkbox.isChecked())

    def _update_button_states(self):
        # Disables buttons if there's no text to find.
        has_text = bool(self.find_input.text())
        self.find_next_button.setEnabled(has_text)
        self.find_prev_button.setEnabled(has_text)
        self.replace_button.setEnabled(has_text)
        self.replace_all_button.setEnabled(has_text)

    def _get_find_flags(self) -> QTextDocument.FindFlag:
        # Converts our checkboxes into flags that Qt's find function understands.
        flags = QTextDocument.FindFlag(0)
        if self.case_checkbox.isChecked():
            flags |= QTextDocument.FindFlag.FindCaseSensitively
        if self.whole_word_checkbox.isChecked():
            flags |= QTextDocument.FindFlag.FindWholeWords
        return flags

    def _find(self, backwards: bool = False):
        # Performs the find operation.
        if not self.editor:
            return
        query = self.find_input.text()
        flags = self._get_find_flags()
        if backwards:
            flags |= QTextDocument.FindFlag.FindBackward
        if not self.editor.find_next(query, flags):
            self.status_message_requested.emit(
                f"No more occurrences of '{query}' found.", 2000)
        self.save_settings()

    def _replace(self):
        # Performs a single replacement.
        if not self.editor:
            return
        query = self.find_input.text()
        replace_text = self.replace_input.text()
        flags = self._get_find_flags()
        if not self.editor.replace_current(query, replace_text, flags):
            self.status_message_requested.emit(
                "Nothing selected to replace.", 2000)
        self.save_settings()

    def _replace_all(self):
        # Performs a "replace all" operation.
        if not self.editor:
            return
        query = self.find_input.text()
        replace_text = self.replace_input.text()
        flags = self._get_find_flags()
        count = self.editor.replace_all(query, replace_text, flags)
        self.save_settings()
        self.status_message_requested.emit(
            f"Replaced {count} occurrence(s).", 3000)
```

### File: `/ui/widgets/syntax_highlighter.py`

```python
# PuffinPyEditor/ui/widgets/syntax_highlighter.py
from typing import Dict, List, Tuple
from PyQt6.QtGui import QSyntaxHighlighter, QTextCharFormat, QColor, QFont
from PyQt6.QtCore import QRegularExpression
from app_core.theme_manager import theme_manager
from utils.logger import log


class PythonSyntaxHighlighter(QSyntaxHighlighter):
    """
    A syntax highlighter for Python code that dynamically styles based on the
    current theme from the ThemeManager.
    """
    def __init__(self, parent_document):
        super().__init__(parent_document)
        self.highlighting_rules: List[Tuple[QRegularExpression, QTextCharFormat]] = []
        self.multiline_string_format = QTextCharFormat()

        self.initialize_formats_and_rules()
        log.info("PythonSyntaxHighlighter initialized.")

    def initialize_formats_and_rules(self):
        """
        Initializes all text formats based on the current theme and sets up
        the regular expression rules for highlighting.
        """
        formats: Dict[str, QTextCharFormat] = {}
        colors = theme_manager.current_theme_data.get("colors", {})

        def get_color(key: str, fallback: str) -> QColor:
            return QColor(colors.get(f"syntax.{key}", fallback))

        formats["keyword"] = QTextCharFormat()
        formats["keyword"].setForeground(get_color("keyword", "#e67e80"))
        formats["keyword"].setFontWeight(QFont.Weight.Bold)

        formats["self"] = QTextCharFormat()
        formats["self"].setForeground(get_color("self", "#e67e80"))
        formats["self"].setFontItalic(True)

        formats["operator"] = QTextCharFormat()
        formats["operator"].setForeground(get_color("operator", "#d3c6aa"))

        formats["brace"] = QTextCharFormat()
        formats["brace"].setForeground(get_color("brace", "#d3c6aa"))

        formats["decorator"] = QTextCharFormat()
        formats["decorator"].setForeground(get_color("decorator", "#dbbc7f"))
        formats["decorator"].setFontItalic(True)

        formats["className"] = QTextCharFormat()
        formats["className"].setForeground(get_color("className", "#dbbc7f"))
        formats["className"].setFontWeight(QFont.Weight.Bold)

        formats["functionName"] = QTextCharFormat()
        formats["functionName"].setForeground(
            get_color("functionName", "#83c092")
        )

        formats["comment"] = QTextCharFormat()
        formats["comment"].setForeground(get_color("comment", "#5f6c6d"))
        formats["comment"].setFontItalic(True)

        formats["string"] = QTextCharFormat()
        formats["string"].setForeground(get_color("string", "#a7c080"))

        formats["docstring"] = QTextCharFormat()
        formats["docstring"].setForeground(get_color("docstring", "#5f6c6d"))
        formats["docstring"].setFontItalic(True)
        self.multiline_string_format = formats["docstring"]

        formats["number"] = QTextCharFormat()
        formats["number"].setForeground(get_color("number", "#d699b6"))

        self.highlighting_rules = []

        keywords = [
            r'\bdef\b', r'\bclass\b', r'\bif\b', r'\belif\b', r'\belse\b',
            r'\bfor\b', r'\bwhile\b', r'\breturn\b', r'\byield\b', r'\bpass\b',
            r'\bcontinue\b', r'\bbreak\b', r'\bimport\b', r'\bfrom\b',
            r'\bas\b', r'\btry\b', r'\bexcept\b', r'\bfinally\b', r'\braise\b',
            r'\bwith\b', r'\bassert\b', r'\bdel\b', r'\bglobal\b',
            r'\bnonlocal\b', r'\bin\b', r'\bis\b', r'\blambda\b', r'\bnot\b',
            r'\bor\b', r'\band\b', r'\bTrue\b', r'\bFalse\b', r'\bNone\b',
            r'\basync\b', r'\bawait\b'
        ]
        self.highlighting_rules += [
            (QRegularExpression(p), formats["keyword"]) for p in keywords
        ]

        self.highlighting_rules.extend([
            (QRegularExpression(r'\bself\b'), formats["self"]),
            (QRegularExpression(r'@[A-Za-z0-9_]+'), formats["decorator"]),
            (QRegularExpression(r'\b[A-Z][A-Za-z0-9_]*'), formats["className"]),
            (QRegularExpression(r'\b[a-z_][A-Za-z0-9_]*(?=\()'),
             formats["functionName"]),
            (QRegularExpression(r'[+\-*/%=<>!&|^~]'), formats["operator"]),
            (QRegularExpression(r'[{}()\[\]]'), formats["brace"]),
            (QRegularExpression(r'\b[0-9]+\b'), formats["number"]),
            (QRegularExpression(r'"[^"\\]*(\\.[^"\\]*)*"'), formats["string"]),
            (QRegularExpression(r"'[^'\\]*(\\.[^'\\]*)*'"), formats["string"]),
            (QRegularExpression(r'#.*'), formats["comment"]),
        ])

        self.tri_single_quote_start = QRegularExpression(r"'''")
        self.tri_double_quote_start = QRegularExpression(r'"""')

    def highlightBlock(self, text: str):
        """Highlights a single block of text."""
        for pattern, fmt in self.highlighting_rules:
            iterator = pattern.globalMatch(text)
            while iterator.hasNext():
                match = iterator.next()
                self.setFormat(match.capturedStart(), match.capturedLength(), fmt)

        self.setCurrentBlockState(0)
        in_multiline = self.previousBlockState() == 1

        start_index = 0
        if in_multiline:
            start_index = self._apply_multiline_format(
                text, self.tri_double_quote_start, 1, 0
            )
            if start_index == -1:
                return

        self._apply_multiline_format(
            text, self.tri_double_quote_start, 1, start_index
        )
        self._apply_multiline_format(
            text, self.tri_single_quote_start, 1, start_index
        )

    def _apply_multiline_format(
        self, text, delimiter_re, state, start_index
    ):
        """Helper to apply formatting for multi-line strings."""
        match = delimiter_re.match(text, start_index)
        while match.hasMatch():
            end_match = delimiter_re.match(text, match.capturedEnd())
            if end_match.hasMatch():
                length = end_match.capturedEnd() - match.capturedStart()
                self.setFormat(
                    match.capturedStart(), length, self.multiline_string_format
                )
                match = delimiter_re.match(text, end_match.capturedEnd())
            else:
                self.setCurrentBlockState(state)
                length = len(text) - match.capturedStart()
                self.setFormat(
                    match.capturedStart(), length, self.multiline_string_format
                )
                return -1
        return match.capturedEnd()

    def rehighlight_document(self):
        """Forces a re-highlight of the entire document."""
        log.info("Re-highlighting entire document for syntax.")
        self.initialize_formats_and_rules()
        super().rehighlight()
```

### File: `/ui/__init__.py`

```python

```

### File: `/ui/editor_widget.py`

```python
# /ui/editor_widget.py
from PyQt6.QtWidgets import (QWidget, QPlainTextEdit, QHBoxLayout, QVBoxLayout,
                             QTextEdit)
from PyQt6.QtCore import pyqtSignal, QRect, Qt, QSize
from PyQt6.QtGui import (QTextCursor, QFont, QPainter, QColor, QTextFormat,
                         QTextDocument, QSyntaxHighlighter, QKeySequence) # Added QKeySequence

from .widgets.breakpoint_area import BreakpointArea
from .widgets.find_panel import FindPanel  # Changed import
from app_core.settings_manager import settings_manager
from app_core.theme_manager import theme_manager
from utils.logger import log


class LineNumberArea(QWidget):
    """
    A simple widget that acts as a canvas for the EditorWidget to paint
    line numbers onto.
    """

    def __init__(self, editor_widget: 'EditorWidget'):
        super().__init__(editor_widget)
        self.editor = editor_widget

    def sizeHint(self) -> QSize:
        """Determines the required width of the widget."""
        return QSize(self.editor.calculate_line_number_area_width(), 0)

    def paintEvent(self, event) -> None:
        """Delegates the paint event to the parent editor widget."""
        self.editor.line_number_area_paint_event(event)


class CodeTextEdit(QPlainTextEdit):
    """A QPlainTextEdit that allows the parent to intercept key presses."""

    def keyPressEvent(self, event):
        # Forward key events to the parent EditorWidget.
        # This allows the parent to handle events like Ctrl+F before the text area does.
        if self.parent().keyPressEvent(event):
            return
        super().keyPressEvent(event)


class EditorWidget(QWidget):
    """
    A full-featured code editor widget. It composes a text area with line
    number and breakpoint sidebars (gutters). The painting logic for the
    gutters is handled within this class for stability.
    """
    content_possibly_changed = pyqtSignal()
    cursor_position_display_updated = pyqtSignal(int, int)
    # This new signal allows us to send status messages up to the main window
    # without creating a hard dependency. It's good practice!
    status_message_requested = pyqtSignal(str, int)

    def __init__(self, completion_manager=None, parent=None):
        super().__init__(parent)
        self.filepath: str | None = None
        self.breakpoints: set[int] = set()
        self._completion_manager = completion_manager
        self.theme_manager = theme_manager
        self.highlighter: QSyntaxHighlighter | None = None

        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        # --- The Find Panel is now created here! ---
        self.find_panel = FindPanel(self)
        self.find_panel.close_requested.connect(self.hide_find_panel)
        # We pass its status message request up to our own signal.
        self.find_panel.status_message_requested.connect(self.status_message_requested.emit)
        self.main_layout.addWidget(self.find_panel)
        self.find_panel.hide() # It starts hidden, of course.

        editor_area_container = QWidget()
        editor_hbox = QHBoxLayout(editor_area_container)
        editor_hbox.setContentsMargins(0, 0, 0, 0)
        editor_hbox.setSpacing(0)

        self.breakpoint_area = BreakpointArea(self)
        self.line_number_area = LineNumberArea(self)
        self.text_area = CodeTextEdit(self)

        editor_hbox.addWidget(self.breakpoint_area)
        editor_hbox.addWidget(self.line_number_area)
        editor_hbox.addWidget(self.text_area, 1)

        self.main_layout.addWidget(editor_area_container)

        self._connect_signals()
        self.update_editor_settings()

    def _connect_signals(self):
        self.text_area.blockCountChanged.connect(self._update_gutter_widths)
        self.text_area.updateRequest.connect(self._on_editor_viewport_changed)
        self.text_area.cursorPositionChanged.connect(self._on_cursor_position_changed)
        self.text_area.textChanged.connect(self.content_possibly_changed)
        self.breakpoint_area.breakpoint_toggled.connect(self._toggle_breakpoint)

    def keyPressEvent(self, event) -> bool:
        # The editor widget itself now handles the Ctrl+F shortcut.
        if event.matches(QKeySequence.StandardKey.Find):
            if self.find_panel.isVisible():
                self.hide_find_panel()
            else:
                self.show_find_panel()
            return True # We've handled the event!
        return False # Let the CodeTextEdit handle other keys.

    def show_find_panel(self):
        """Makes the Find Panel visible and connects it to this editor."""
        self.find_panel.connect_editor(self)
        self.find_panel.show()
        self.find_panel.focus_find_input()

    def hide_find_panel(self):
        """Hides the Find Panel and returns focus to the text area."""
        self.find_panel.hide()
        self.text_area.setFocus()

    def set_highlighter(self, highlighter_class):
        if self.highlighter:
            self.highlighter.setDocument(None)
        if highlighter_class:
            self.highlighter = highlighter_class(self.text_area.document())
        else:
            self.highlighter = None

    def calculate_line_number_area_width(self) -> int:
        digits = len(str(max(1, self.text_area.blockCount())))
        space = 10 + self.fontMetrics().horizontalAdvance('9') * digits
        return space

    def _update_gutter_widths(self):
        width = self.calculate_line_number_area_width()
        self.line_number_area.setFixedWidth(width)

    def _on_editor_viewport_changed(self, rect: QRect, dy: int):
        if dy:
            self.line_number_area.scroll(0, dy)
            self.breakpoint_area.scroll(0, dy)
        else:
            self.line_number_area.update()
            self.breakpoint_area.update()
        self.highlight_current_line()

    def line_number_area_paint_event(self, event: 'QPaintEvent') -> None:
        try:
            painter = QPainter(self.line_number_area)
        except Exception as e:
            log.error(f"Could not create QPainter for line numbers: {e}")
            return

        colors = self.theme_manager.current_theme_data.get('colors', {})
        bg_color = QColor(colors.get('editorGutter.background', '#2c313a'))
        border_color = QColor(colors.get('input.border', '#555555'))

        painter.fillRect(event.rect(), bg_color)
        painter.setPen(border_color)
        painter.drawLine(event.rect().topRight(), event.rect().bottomRight())

        content_offset = self.text_area.contentOffset()
        current_line = self.text_area.textCursor().blockNumber()

        block = self.text_area.firstVisibleBlock()
        while block.isValid() and (block_top := self.text_area.blockBoundingGeometry(block).translated(
                content_offset).top()) <= event.rect().bottom():
            if block.isVisible():
                line_number_str = str(block.blockNumber() + 1)
                is_current = (block.blockNumber() == current_line)

                font = self.text_area.font()
                font.setBold(is_current)
                painter.setFont(font)

                color_key = 'editorLineNumber.activeForeground' if is_current else 'editorLineNumber.foreground'
                painter.setPen(QColor(colors.get(color_key, '#d0d0d0')))

                paint_rect = QRect(0, int(block_top), self.line_number_area.width(), self.fontMetrics().height())
                painter.drawText(paint_rect.adjusted(0, 0, -8, 0), Qt.AlignmentFlag.AlignRight, line_number_str)
            block = block.next()

    def _toggle_breakpoint(self, line_num: int):
        if line_num in self.breakpoints:
            self.breakpoints.remove(line_num)
        else:
            self.breakpoints.add(line_num)
        self.breakpoint_area.update()

    def get_cursor_position(self) -> tuple[int, int]:
        cursor = self.text_area.textCursor()
        return cursor.blockNumber(), cursor.columnNumber()

    def _on_cursor_position_changed(self):
        line, col = self.get_cursor_position()
        self.cursor_position_display_updated.emit(line, col)
        self.highlight_current_line()

    def highlight_current_line(self):
        selections = []
        if not self.text_area.isReadOnly():
            selection = QTextEdit.ExtraSelection()
            colors = self.theme_manager.current_theme_data.get('colors', {})
            line_color_hex = colors.get('editor.lineHighlightBackground')
            if line_color_hex:
                selection.format.setBackground(QColor(line_color_hex))
                selection.format.setProperty(QTextFormat.Property.FullWidthSelection, True)
                selection.cursor = self.text_area.textCursor()
                selection.cursor.clearSelection()
                selections.append(selection)
        self.text_area.setExtraSelections(selections)

    def get_text(self) -> str:
        return self.text_area.toPlainText()

    def set_text(self, text: str):
        self.text_area.setPlainText(text); self._on_cursor_position_changed()

    def set_filepath(self, filepath: str | None):
        self.filepath = filepath; self.breakpoint_area.setVisible(bool(filepath and filepath.lower().endswith('.py')))

    def goto_line_and_column(self, line: int, col: int):
        cursor = QTextCursor(self.text_area.document().findBlockByNumber(line - 1))
        cursor.movePosition(QTextCursor.MoveOperation.Right, n=col)
        self.text_area.setTextCursor(cursor);
        self.text_area.setFocus()

    def find_next(self, query: str, flags: QTextDocument.FindFlag) -> bool:
        return self.text_area.find(query, flags)

    def replace_current(self, query, replace, flags) -> bool:
        cursor = self.text_area.textCursor()
        if not cursor.hasSelection(): return False
        if (cursor.selectedText() == query) if (flags & QTextDocument.FindFlag.FindCaseSensitively) else (
                cursor.selectedText().lower() == query.lower()):
            cursor.insertText(replace);
            return True
        return False

    def replace_all(self, query, replace, flags) -> int:
        count = 0;
        self.text_area.moveCursor(QTextCursor.MoveOperation.Start)
        while self.text_area.find(query, flags): self.text_area.textCursor().insertText(replace); count += 1
        return count

    def update_editor_settings(self):
        font = QFont(settings_manager.get("font_family"), settings_manager.get("font_size"))
        self.text_area.setFont(font);
        self.line_number_area.setFont(font);
        self.breakpoint_area.setFont(font)
        self.text_area.setTabStopDistance(
            self.fontMetrics().horizontalAdvance(' ') * settings_manager.get("indent_width"))
        self.line_number_area.setVisible(settings_manager.get("show_line_numbers", True))
        self.update_theme()
        self._update_gutter_widths()

    def update_theme(self):
        colors = self.theme_manager.current_theme_data.get("colors", {})
        stylesheet = f"""QPlainTextEdit {{ background-color: {colors.get('editor.background', '#1e1e1e')}; color: {colors.get('editor.foreground', '#d4d4d4')}; border: none; selection-background-color: {colors.get('editor.selectionBackground', '#264f78')}; }}"""
        self.text_area.setStyleSheet(stylesheet)
        if self.highlighter: self.highlighter.rehighlight()
        self.breakpoint_area.update();
        self.line_number_area.update();
        self.highlight_current_line()
        # I also need to make sure the find panel gets the theme update!
        self.find_panel.update_theme()
```

### File: `/ui/main_window.py`

```python
# /ui/main_window.py
import os
import sys
from functools import partial
from typing import Optional
from PyQt6.QtGui import (QKeySequence, QAction, QCloseEvent, QDesktopServices, QIcon, QActionGroup)
from PyQt6.QtWidgets import (QMessageBox, QMenu, QWidget, QVBoxLayout, QHBoxLayout,
                             QMainWindow, QStatusBar, QTabWidget, QLabel, QToolButton,
                             QToolBar, QSizePolicy, QApplication, QFileDialog, QDockWidget)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer, QSize, QUrl

import qtawesome as qta
from utils.logger import log
from utils import versioning
from app_core.file_handler import FileHandler
from app_core.theme_manager import theme_manager
from app_core.settings_manager import settings_manager
from app_core.project_manager import ProjectManager
from app_core.linter_manager import LinterManager
from app_core.plugin_manager import PluginManager
from app_core.completion_manager import CompletionManager
from app_core.update_manager import UpdateManager
from app_core.source_control_manager import SourceControlManager
from app_core.github_manager import GitHubManager
from app_core.puffin_api import PuffinPluginAPI
from .editor_widget import EditorWidget
from .preferences_dialog import PreferencesDialog
from .widgets.syntax_highlighter import PythonSyntaxHighlighter
from plugins.tab_drag_handler.draggable_tab_widget import DraggableTabWidget


class MainWindow(QMainWindow):
    untitled_file_counter = 0
    _is_app_closing = False
    theme_changed_signal = pyqtSignal(str)

    def __init__(self, file_handler, theme_manager, debug_mode=False, parent=None):
        super().__init__(parent)
        self.file_handler = file_handler;
        self.file_handler.parent_window = self
        self.theme_manager = theme_manager;
        self.debug_mode = debug_mode
        self.preferences_dialog = None
        self._bottom_tab_widget: Optional[QTabWidget] = None
        self._bottom_dock_widget: Optional[QDockWidget] = None

        self._initialize_managers()
        self.puffin_api = PuffinPluginAPI(self)

        self.setWindowTitle(f"PuffinPyEditor - v{versioning.APP_VERSION}")
        self._load_window_geometry()
        self._create_core_widgets()
        self._create_core_actions()
        self._create_core_menu()
        self._create_toolbar()
        self._create_layout()
        self._create_statusbar()

        plugins_to_ignore = []
        if self.debug_mode:
            try:
                from core_debug_tools.enhanced_exceptions.plugin_main import initialize as init_eh
                self.eh_instance = init_eh(self.puffin_api, sys.excepthook)
                plugins_to_ignore.append('enhanced_exceptions')
            except Exception as e:
                log.error(f"Failed to load core exception handler: {e}", exc_info=True)

        self.plugin_manager = PluginManager(self)
        self.plugin_manager.discover_and_load_plugins(ignore_list=plugins_to_ignore)

        self._connect_signals()
        self._apply_theme_and_icons(self.settings.get("last_theme_id"))
        QTimer.singleShot(0, self._post_init_setup)
        log.info("MainWindow __init__ has completed.")

    def _initialize_managers(self):
        self.settings = settings_manager
        self.project_manager = ProjectManager()
        self.completion_manager = CompletionManager(self)
        self.github_manager = GitHubManager(self)
        self.git_manager = SourceControlManager(self)
        self.linter_manager = LinterManager(self)
        self.update_manager = UpdateManager(self)
        self.actions = {}
        self.editor_tabs_data = {}
        self.file_open_handlers = {}
        self.lint_timer = QTimer(self);
        self.lint_timer.setSingleShot(True);
        self.lint_timer.setInterval(1500)
        self.auto_save_timer = QTimer(self);
        self.auto_save_timer.setSingleShot(True)

    def _load_window_geometry(self):
        size, pos = self.settings.get("window_size", [1600, 1000]), self.settings.get("window_position")
        self.resize(QSize(size[0], size[1]));
        if pos: self.move(pos[0], pos[1])

    def _create_core_widgets(self):
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.tab_widget = DraggableTabWidget(self)
        button = QToolButton();
        button.setIcon(qta.icon('fa5s.plus'));
        button.setAutoRaise(True)
        button.clicked.connect(lambda: self._add_new_tab())
        self.tab_widget.setCornerWidget(button, Qt.Corner.TopRightCorner)
        self.tab_widget.setDocumentMode(True);
        self.tab_widget.setTabsClosable(True);
        self.tab_widget.setMovable(True)

    def _create_core_actions(self):
        actions_map = {
            "new_file": ("&New File", self._add_new_tab, "Ctrl+N", 'fa5s.file'),
            "open_file": ("&Open File...", self._action_open_file_dialog, "Ctrl+O", 'fa5s.folder-open'),
            "open_folder": ("Open &Folder...", self._action_open_folder, "Ctrl+Shift+O", 'fa5s.folder'),
            "close_project": ("&Close Project", self._action_close_project, None, None),
            "save": ("&Save", self._action_save_file, "Ctrl+S", 'fa5s.save'),
            "save_as": ("Save &As...", self._action_save_as, "Ctrl+Shift+S", None),
            "save_all": ("Save A&ll", self._action_save_all, "Ctrl+Alt+S", None),
            "preferences": ("&Preferences...", self._action_open_preferences, "Ctrl+,", 'fa5s.cog'),
            "exit": ("E&xit", self.close, "Ctrl+Q", None),
        }
        for key, (text, cb, sc, icon) in actions_map.items():
            action = QAction(text, self)
            if icon: action.setData(icon)
            if sc: action.setShortcut(QKeySequence(sc))
            action.triggered.connect(cb);
            self.actions[key] = action

    def _create_core_menu(self):
        mb = self.menuBar()
        self.file_menu, self.edit_menu, self.view_menu = mb.addMenu("&File"), mb.addMenu("&Edit"), mb.addMenu("&View")
        self.run_menu, self.tools_menu, self.help_menu = mb.addMenu("&Run"), mb.addMenu("&Tools"), mb.addMenu("&Help")

        self.file_menu.addActions([self.actions[k] for k in ["new_file", "open_file"]])
        self.recent_files_menu = self.file_menu.addMenu("Open &Recent")
        self.file_menu.addSeparator();
        self.file_menu.addActions([self.actions[k] for k in ["open_folder", "close_project"]])
        self.file_menu.addSeparator();
        self.file_menu.addActions([self.actions[k] for k in ["save", "save_as", "save_all"]])
        self.file_menu.addSeparator();
        self.file_menu.addAction(self.actions["preferences"]);
        self.file_menu.addSeparator()
        self.file_menu.addAction(self.actions["exit"])
        self.theme_menu = self.view_menu.addMenu("&Themes")
        self.help_menu.addAction("About PuffinPyEditor", self._show_about_dialog);
        self.help_menu.addAction("View on GitHub", self._open_github_link)

    def _create_toolbar(self):
        self.main_toolbar = QToolBar("Main Toolbar");
        self.main_toolbar.setIconSize(QSize(18, 18));
        self.addToolBar(self.main_toolbar)
        self.main_toolbar.addActions([self.actions[k] for k in ["new_file", "open_file", "save"]])
        spacer = QWidget();
        spacer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred);
        self.main_toolbar.addWidget(spacer)
        self.main_toolbar.addAction(self.actions["preferences"])

    def _create_layout(self):
        layout = QHBoxLayout(self.central_widget)
        layout.setContentsMargins(0, 0, 0, 0);
        layout.addWidget(self.tab_widget)

    def _create_statusbar(self):
        self.setStatusBar(QStatusBar(self));
        self.cursor_label = QLabel(" Ln 1, Col 1 ");
        self.statusBar().addPermanentWidget(self.cursor_label)

    def _connect_signals(self):
        self.tab_widget.currentChanged.connect(self._on_tab_changed)
        self.tab_widget.tabCloseRequested.connect(self._action_close_tab_by_index)
        self.lint_timer.timeout.connect(self._trigger_file_linter)
        self.completion_manager.definition_found.connect(self._goto_definition_result)
        self.auto_save_timer.timeout.connect(self._auto_save_current_tab)

    def _apply_theme_and_icons(self, theme_id: str):
        self.theme_manager.set_theme(theme_id, QApplication.instance());
        self.theme_changed_signal.emit(theme_id)
        for action in self.actions.values():
            if icon_name := action.data(): action.setIcon(qta.icon(icon_name))
        self._rebuild_theme_menu()
        for i in range(self.tab_widget.count()):
            if hasattr(widget := self.tab_widget.widget(i), 'update_theme'): widget.update_theme()
        if hasattr(self, 'project_manager'): self.project_manager.projects_changed.emit()

    def _rebuild_theme_menu(self):
        self.theme_menu.clear();
        group = QActionGroup(self);
        group.setExclusive(True)
        for theme_id, name in self.theme_manager.get_available_themes_for_ui().items():
            action = QAction(name, self, checkable=True,
                             triggered=lambda _, t_id=theme_id: self._on_theme_selected(t_id))
            action.setData(theme_id);
            action.setChecked(theme_id == self.theme_manager.current_theme_id)
            group.addAction(action);
            self.theme_menu.addAction(action)

    def _post_init_setup(self):
        self._update_recent_files_menu();
        self._update_window_title()
        if self.tab_widget.count() == 0: self._add_new_tab(is_placeholder=True)

    def add_dock_panel(self, panel_widget: QWidget, title: str, area: Qt.DockWidgetArea,
                       icon_name: Optional[str] = None):
        if area == Qt.DockWidgetArea.BottomDockWidgetArea:
            if self._bottom_tab_widget is None:
                log.info("Creating shared bottom dock area.");
                self._bottom_dock_widget = QDockWidget("Info Panels", self)
                self._bottom_dock_widget.setObjectName("SharedBottomDock");
                self._bottom_tab_widget = QTabWidget()
                self._bottom_tab_widget.setDocumentMode(True);
                self._bottom_dock_widget.setWidget(self._bottom_tab_widget)
                self.addDockWidget(area, self._bottom_dock_widget)
                if self.view_menu: self.view_menu.addSeparator(); self.view_menu.addAction(
                    self._bottom_dock_widget.toggleViewAction())
            icon = qta.icon(icon_name) if icon_name else QIcon();
            self._bottom_tab_widget.addTab(panel_widget, icon, title)
        else:
            dock = QDockWidget(title, self);
            dock.setWidget(panel_widget)
            if icon_name: dock.setWindowIcon(qta.icon(icon_name))
            self.addDockWidget(area, dock)
            if self.view_menu: self.view_menu.addSeparator(); self.view_menu.addAction(dock.toggleViewAction())

    def _add_new_tab(self, filepath=None, content="", is_placeholder=False):
        if not is_placeholder and self.tab_widget.count() == 1 and isinstance(self.tab_widget.widget(0), QLabel):
            self.tab_widget.removeTab(0)

        if is_placeholder:
            placeholder = QLabel("Open a file...", alignment=Qt.AlignmentFlag.AlignCenter);
            placeholder.setObjectName("PlaceholderLabel")
            self.tab_widget.addTab(placeholder, "Welcome");
            self.tab_widget.setTabsClosable(False);
            return

        try:
            self.tab_widget.setTabsClosable(True);
            editor = EditorWidget(self.completion_manager, self)
            ext = os.path.splitext(filepath or "")[1].lower()
            highlighter = self.puffin_api.highlighter_map.get(ext) or (
                PythonSyntaxHighlighter if ext == '.py' else None)
            editor.set_highlighter(highlighter);
            editor.set_filepath(filepath);
            editor.set_text(content)
            editor.cursor_position_display_updated.connect(lambda l, c: self.cursor_label.setText(f" Ln {l+1}, Col {c} "))
            editor.content_possibly_changed.connect(partial(self._on_content_changed, editor))
            # I'm connecting the new signal from the editor to the status bar here.
            editor.status_message_requested.connect(self.statusBar().showMessage)

            if filepath:
                name = os.path.basename(filepath)
            else:
                self.untitled_file_counter += 1
                name = f"Untitled-{self.untitled_file_counter}"
            index = self.tab_widget.addTab(editor, name);
            self.tab_widget.setTabToolTip(index, filepath or f"Unsaved {name}")
            self.editor_tabs_data[editor] = {'filepath': filepath, 'original_hash': hash(content)}
            self.tab_widget.setCurrentWidget(editor);
            editor.text_area.setFocus()
        except Exception as e:
            log.critical(f"CRASH during _add_new_tab: {e}", exc_info=True)
            QMessageBox.critical(self, "Fatal Error", f"Could not create editor tab:\n\n{e}")

    def _action_open_file(self, filepath: Optional[str] = None, content: Optional[str] = None):
        if not (isinstance(filepath, str) and filepath): return
        norm_path = os.path.normpath(filepath)
        for i in range(self.tab_widget.count()):
            widget = self.tab_widget.widget(i)
            if isinstance(widget, EditorWidget) and self.editor_tabs_data.get(widget, {}).get('filepath') == norm_path:
                self.tab_widget.setCurrentIndex(i);
                return

        if handler := self.file_open_handlers.get(os.path.splitext(norm_path)[1].lower()):
            handler(norm_path);
            self.file_handler._add_to_recent_files(norm_path);
            return
        if content is None:
            try:
                with open(norm_path, 'r', encoding='utf-8', errors='replace') as f:
                    content = f.read()
            except Exception as e:
                self.puffin_api.show_message("critical", "Error Opening File", f"Could not read file: {e}"); return
        self._add_new_tab(norm_path, content);
        self.file_handler._add_to_recent_files(norm_path)

    def _action_open_file_dialog(self):
        filepath, content, error = self.file_handler.open_file_dialog()
        if error:
            QMessageBox.critical(self, "Error Opening File", error)
        elif filepath:
            self._action_open_file(filepath, content)

    def _action_open_folder(self, path: Optional[str] = None):
        if not path or not isinstance(path, str):
            path = QFileDialog.getExistingDirectory(self, "Open Folder",
                                                    self.project_manager.get_active_project_path() or os.path.expanduser(
                                                        "~"))
        if path: self.project_manager.open_project(path); self.project_manager.projects_changed.emit()

    def _action_close_project(self, path: Optional[str] = None):
        if path_to_close := path if isinstance(path, str) else self.project_manager.get_active_project_path():
            self.project_manager.close_project(path_to_close);
            self.project_manager.projects_changed.emit()
        else:
            self.statusBar().showMessage("No active project to close.", 2000)

    def _on_theme_selected(self, theme_id):
        self.settings.set("last_theme_id", theme_id);
        self._apply_theme_and_icons(theme_id)

    def _on_tab_changed(self, index):
        self._update_window_title()
        widget = self.tab_widget.widget(index) if index != -1 else None
        if isinstance(widget, EditorWidget):
            line, col = widget.get_cursor_position()
            self.cursor_label.setText(f" Ln {line + 1}, Col {col + 1} ")
        else:
            self.cursor_label.setText("")

    def _is_editor_modified(self, editor: QWidget) -> bool:
        return isinstance(editor, EditorWidget) and (data := self.editor_tabs_data.get(editor)) and hash(
            editor.get_text()) != data['original_hash']

    def _on_content_changed(self, editor: EditorWidget):
        if not (isinstance(editor, EditorWidget) and self.tab_widget.isAncestorOf(editor)): return
        is_modified, index = self._is_editor_modified(editor), self.tab_widget.indexOf(editor)
        if index != -1:
            current_text = self.tab_widget.tabText(index)
            has_asterisk = current_text.endswith(' *')
            if is_modified and not has_asterisk:
                self.tab_widget.setTabText(index, current_text + ' *')
            elif not is_modified and has_asterisk:
                self.tab_widget.setTabText(index, current_text[:-2])
        self._update_window_title()
        if self.settings.get("auto_save_enabled", False): self.auto_save_timer.start(
            self.settings.get("auto_save_delay_seconds", 3) * 1000)

    def _update_window_title(self):
        base_title, project_name = "PuffinPyEditor", os.path.basename(
            self.project_manager.get_active_project_path()) if self.project_manager.is_project_open() else ""
        current_file = "";
        current_widget = self.tab_widget.currentWidget()
        if isinstance(current_widget, EditorWidget):
            filepath = self.editor_tabs_data.get(current_widget, {}).get('filepath')
            current_file = os.path.basename(filepath) if filepath else self.tab_widget.tabText(
                self.tab_widget.currentIndex()).replace(" *", "")
            if self._is_editor_modified(current_widget): current_file += " *"
        self.setWindowTitle(" - ".join(filter(None, [current_file, project_name, base_title])))

    def _action_save_file(self, editor_widget=None, save_as=False):
        current_editor = editor_widget or self.tab_widget.currentWidget()
        if not isinstance(current_editor, EditorWidget): return None
        if not (editor_data := self.editor_tabs_data.get(current_editor)): return None
        content = current_editor.get_text()
        if not self._is_editor_modified(current_editor) and not save_as and editor_data['filepath']:
            self.statusBar().showMessage("File is already saved.", 2000);
            return editor_data['filepath']
        if (filepath := self.file_handler.save_file_content(editor_data['filepath'], content, save_as)):
            editor_data.update({'filepath': filepath, 'original_hash': hash(content)});
            current_editor.set_filepath(filepath)
            if (index := self.tab_widget.indexOf(current_editor)) != -1:
                self.tab_widget.setTabText(index, os.path.basename(filepath));
                self.tab_widget.setTabToolTip(index, filepath)
            self.statusBar().showMessage(f"File saved: {os.path.basename(filepath)}", 3000)
            self._on_content_changed(current_editor);
            self.file_handler._add_to_recent_files(filepath);
            return filepath
        self.statusBar().showMessage("Save cancelled.", 2000);
        return None

    def _action_save_as(self):
        self._action_save_file(save_as=True)

    def _action_save_all(self):
        if count := sum(1 for i in range(self.tab_widget.count()) if
                        self._is_editor_modified(w := self.tab_widget.widget(i)) and self._action_save_file(w)):
            self.statusBar().showMessage(f"Saved {count} file(s).", 3000)

    def _action_close_tab_by_index(self, index):
        self._close_widget_safely(self.tab_widget.widget(index), QCloseEvent())

    def _close_widget_safely(self, widget, event):
        if not isinstance(widget, EditorWidget):
            if widget.parent() is None: widget.deleteLater()
            event.accept();
            return
        if self._is_editor_modified(widget):
            filename = self.tab_widget.tabText(self.tab_widget.indexOf(widget)).replace(" *", "")
            ret = QMessageBox.question(self, "Save Changes?", f"Save changes to {filename}?",
                                       QMessageBox.StandardButton.Save | QMessageBox.StandardButton.Discard | QMessageBox.StandardButton.Cancel)
            if ret == QMessageBox.StandardButton.Cancel or (
                    ret == QMessageBox.StandardButton.Save and not self._action_save_file(widget)):
                event.ignore();
                return
        if widget in self.editor_tabs_data: del self.editor_tabs_data[widget]
        event.accept()

    def _update_recent_files_menu(self):
        self.recent_files_menu.clear();
        recent_files = self.settings.get("recent_files", [])
        self.recent_files_menu.setEnabled(bool(recent_files))
        for i, filepath in enumerate(recent_files[:10]):
            action = QAction(f"&{i + 1} {os.path.basename(filepath)}", self)
            action.setData(filepath)
            action.setToolTip(filepath)
            action.triggered.connect(self._action_open_recent_file)
            self.recent_files_menu.addAction(action)

    def _action_open_recent_file(self):
        if action := self.sender(): self._action_open_file(action.data())

    def _trigger_file_linter(self):
        pass

    def _show_about_dialog(self):
        QMessageBox.about(self, "About", f"PuffinPyEditor v{versioning.APP_VERSION}")

    def _open_github_link(self):
        QDesktopServices.openUrl(QUrl("https://github.com/Stelliro/PuffinPyEditor"))

    def _auto_save_current_tab(self):
        if self._is_editor_modified(editor := self.tab_widget.currentWidget()): self._action_save_file(
            editor_widget=editor)

    def _on_editor_settings_changed(self):
        for i in range(self.tab_widget.count()):
            if isinstance(widget := self.tab_widget.widget(i), EditorWidget): widget.update_editor_settings()

    def _action_open_preferences(self):
        if not self.preferences_dialog or not self.preferences_dialog.isVisible():
            self.preferences_dialog = PreferencesDialog(self.git_manager, self.github_manager, self.plugin_manager,
                                                        self.puffin_api, self)
            self.preferences_dialog.settings_changed_for_editor_refresh.connect(self._on_editor_settings_changed)
            self.preferences_dialog.theme_changed_signal.connect(self._on_theme_selected)
        self.preferences_dialog.show();
        self.preferences_dialog.raise_();
        self.preferences_dialog.activateWindow()

    def _goto_definition_result(self, filepath, line, col):
        if not filepath: self.statusBar().showMessage("Definition not found", 3000); return
        norm_path = os.path.normpath(filepath)
        for i in range(self.tab_widget.count()):
            if isinstance(e := self.tab_widget.widget(i), EditorWidget) and self.editor_tabs_data.get(e, {}).get(
                    'filepath') == norm_path:
                self.tab_widget.setCurrentIndex(i);
                e.goto_line_and_column(line, col);
                return
        self._action_open_file(norm_path);
        QApplication.processEvents()
        if isinstance(e := self.tab_widget.currentWidget(), EditorWidget) and self.editor_tabs_data.get(e, {}).get(
                'filepath') == norm_path:
            e.goto_line_and_column(line, col)

    def _shutdown_managers(self):
        log.info("Shutting down core managers...")
        for manager in [self.completion_manager, self.github_manager, self.git_manager, self.linter_manager]:
            if hasattr(manager, 'shutdown'): manager.shutdown()

    def closeEvent(self, event: QCloseEvent):
        if self._is_app_closing: event.accept(); return
        self._is_app_closing = True

        while self.tab_widget.count() > 0:
            dummy_event = QCloseEvent();
            self._close_widget_safely(self.tab_widget.widget(0), dummy_event)
            if not dummy_event.isAccepted(): self._is_app_closing = False; event.ignore(); return
            if (index := self.tab_widget.indexOf(self.tab_widget.widget(0))) != -1: self.tab_widget.removeTab(index)

        self.settings.set("window_size", [self.size().width(), self.size().height()], False)
        self.settings.set("window_position", [self.pos().x(), self.pos().y()], False)
        self.project_manager.save_session();
        self.settings.save()
        self._shutdown_managers()
        log.info("PuffinPyEditor exited cleanly.")
        event.accept()
```

### File: `/ui/preferences_dialog.py`

```python
# PuffinPyEditor/ui/preferences_dialog.py
import uuid
import sys
import os
import tempfile
import requests
from typing import Optional, Any
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QTabWidget,
                             QWidget, QLabel, QComboBox, QSpinBox, QCheckBox,
                             QPushButton, QLineEdit, QDialogButtonBox,
                             QFontComboBox, QSplitter, QFormLayout,
                             QListWidget, QListWidgetItem, QMessageBox,
                             QGroupBox, QFileDialog, QInputDialog,
                             QStackedWidget)
from PyQt6.QtGui import QFont, QDesktopServices, QColor
from PyQt6.QtCore import Qt, QSize, pyqtSignal, QUrl

if sys.platform == "win32":
    try:
        import winshell
    except ImportError:
        winshell = None
        log.warning("The 'winshell' package is not installed. Startup shortcut features will be disabled.")

import qtawesome as qta
from utils.logger import log
from utils.helpers import get_startup_shortcut_path
from app_core.settings_manager import settings_manager
from app_core.theme_manager import theme_manager
from app_core.github_manager import GitHubManager
from app_core.source_control_manager import SourceControlManager
from app_core.plugin_manager import PluginManager, Plugin
from app_core.puffin_api import PuffinPluginAPI


class AuthDialog(QDialog):
    def __init__(self, user_code: str, verification_uri: str,
                 parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setWindowTitle("GitHub Device Authorization")
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Please authorize PuffinPyEditor in your browser."))
        url_label = QLabel(f"1. Open: <a href='{verification_uri}'>{verification_uri}</a>")
        url_label.setOpenExternalLinks(True)
        layout.addWidget(url_label)
        layout.addWidget(QLabel("2. Enter this one-time code:"))
        code_label = QLineEdit(user_code)
        code_label.setReadOnly(True)
        code_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        code_label.setFont(QFont("Consolas", 14, QFont.Weight.Bold))
        layout.addWidget(code_label)
        QDesktopServices.openUrl(QUrl(verification_uri))
        self.setFixedSize(self.sizeHint())


class PreferencesDialog(QDialog):
    settings_changed_for_editor_refresh = pyqtSignal()
    theme_changed_signal = pyqtSignal(str)

    def __init__(self, git_manager: SourceControlManager,
                 github_manager: GitHubManager, plugin_manager: PluginManager,
                 puffin_api: PuffinPluginAPI,
                 parent: Optional[QWidget] = None):
        super().__init__(parent)
        log.info("PreferencesDialog initializing...")
        self.setWindowTitle("Preferences")
        self.setMinimumSize(QSize(850, 700))
        self.git_manager = git_manager
        self.github_manager = github_manager
        self.plugin_manager = plugin_manager
        self.puffin_api = puffin_api

        self.original_settings: dict[str, Any] = {}
        self.original_git_config: dict[str, str] = {}
        self.staged_repos: list[dict] = []
        self.staged_active_repo_id: Optional[str] = None
        self.current_repo_id_in_form: Optional[str] = None
        self.auth_dialog: Optional[AuthDialog] = None
        self.restart_needed = False
        self.is_loading = False
        self.main_layout = QVBoxLayout(self)
        self.tab_widget = QTabWidget()
        self.main_layout.addWidget(self.tab_widget)
        self._create_tabs()
        self._create_button_box()
        self._connect_global_signals()
        self._connect_ui_changed_signals()
        log.info("PreferencesDialog initialized.")

    def _create_tabs(self):
        self._create_appearance_tab()
        self._create_editor_tab()
        self._create_run_tab()
        self._create_system_tab()
        self._create_source_control_tab()
        self._create_plugins_tab()

    def _create_button_box(self):
        buttons = (
                    QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel | QDialogButtonBox.StandardButton.Apply)
        self.button_box = QDialogButtonBox(buttons)
        self.main_layout.addWidget(self.button_box)

    def _connect_global_signals(self):
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        self.button_box.button(QDialogButtonBox.StandardButton.Apply).clicked.connect(self.apply_settings)
        self.git_manager.git_config_ready.connect(self._populate_git_config_fields)
        self.github_manager.device_code_ready.connect(self._on_device_code_ready)
        self.github_manager.auth_successful.connect(self._on_auth_successful)
        self.github_manager.auth_failed.connect(self._on_auth_failed)
        self.github_manager.auth_polling_lapsed.connect(self._on_auth_polling_lapsed)
        self.github_manager.operation_success.connect(self._handle_github_op_success)
        self.github_manager.plugin_index_ready.connect(self._on_plugin_index_ready)
        self.git_manager.git_success.connect(self._handle_git_success)

    def _handle_github_op_success(self, message, data):
        if "Repository" in message and "created" in message:
            new_repo_id = str(uuid.uuid4())
            owner, repo_name = self.git_manager.parse_git_url(data.get("clone_url"))
            new_repo = {"id": new_repo_id, "name": data.get("name"), "owner": owner, "repo": repo_name}
            self.staged_repos.append(new_repo)
            QMessageBox.information(self, "Success", f"Repository '{repo_name}' created on GitHub.")
            self._populate_repo_list(select_repo_id=new_repo_id)
            self._on_ui_setting_changed()

    def showEvent(self, event):
        self.is_loading = True
        self._load_settings_into_dialog()
        self.git_manager.get_git_config()
        self._update_auth_status()
        self._populate_all_plugin_lists()
        self.button_box.button(QDialogButtonBox.StandardButton.Apply).setEnabled(False)
        self.restart_needed = False
        super().showEvent(event)
        self.is_loading = False

    def _load_settings_into_dialog(self):
        self.original_settings = settings_manager.settings.copy()
        self._repopulate_theme_combo()
        self.font_family_combo.setCurrentFont(QFont(settings_manager.get("font_family")))
        self.font_size_spinbox.setValue(settings_manager.get("font_size"))
        self.show_line_numbers_checkbox.setChecked(settings_manager.get("show_line_numbers"))
        self.word_wrap_checkbox.setChecked(settings_manager.get("word_wrap"))
        self.show_indent_guides_checkbox.setChecked(settings_manager.get("show_indentation_guides"))
        self.indent_style_combo.setCurrentText(settings_manager.get("indent_style").capitalize())
        self.indent_width_spinbox.setValue(settings_manager.get("indent_width"))
        self.auto_save_checkbox.setChecked(settings_manager.get("auto_save_enabled"))
        self.auto_save_delay_spinbox.setValue(settings_manager.get("auto_save_delay_seconds"))
        self.max_recent_files_spinbox.setValue(settings_manager.get("max_recent_files"))
        self.python_path_edit.setText(settings_manager.get("python_interpreter_path", ""))
        if sys.platform == "win32":
            self.nsis_path_edit.setText(settings_manager.get("nsis_path", ""))
            self.cleanup_build_checkbox.setChecked(settings_manager.get("cleanup_after_build", True))
            if winshell and hasattr(self, 'run_in_background_checkbox'): self.run_in_background_checkbox.setChecked(
                settings_manager.get("run_in_background", False))

        self.staged_repos = [r.copy() for r in settings_manager.get("source_control_repos", [])]
        self.staged_active_repo_id = settings_manager.get("active_update_repo_id")
        self._populate_repo_list()
        self.plugins_repo_edit.setText(settings_manager.get("plugins_distro_repo", "Stelliro/puffin-plugins"))

    def _connect_ui_changed_signals(self):
        for w in self.findChildren((QComboBox, QSpinBox, QCheckBox, QFontComboBox, QLineEdit)):
            if isinstance(w, QComboBox):
                w.currentIndexChanged.connect(self._on_ui_setting_changed)
            elif isinstance(w, QFontComboBox):
                w.currentFontChanged.connect(self._on_ui_setting_changed)
            elif isinstance(w, QSpinBox):
                w.valueChanged.connect(self._on_ui_setting_changed)
            elif isinstance(w, QCheckBox):
                w.stateChanged.connect(self._on_ui_setting_changed)
            elif isinstance(w, QLineEdit):
                w.textChanged.connect(self._on_ui_setting_changed)

    def _on_ui_setting_changed(self, *args):
        if not self.is_loading and self.isVisible(): self.button_box.button(
            QDialogButtonBox.StandardButton.Apply).setEnabled(True)

    def apply_settings(self):
        ab = self.button_box.button(QDialogButtonBox.StandardButton.Apply)
        if not ab.isEnabled(): return

        ss = {
            "last_theme_id": self.theme_combo.currentData(),
            "font_family": self.font_family_combo.currentFont().family(),
            "font_size": self.font_size_spinbox.value(),
            "show_line_numbers": self.show_line_numbers_checkbox.isChecked(),
            "word_wrap": self.word_wrap_checkbox.isChecked(),
            "show_indentation_guides": self.show_indent_guides_checkbox.isChecked(),
            "indent_style": self.indent_style_combo.currentText().lower(),
            "indent_width": self.indent_width_spinbox.value(),
            "auto_save_enabled": self.auto_save_checkbox.isChecked(),
            "auto_save_delay_seconds": self.auto_save_delay_spinbox.value(),
            "max_recent_files": self.max_recent_files_spinbox.value(),
            "python_interpreter_path": self.python_path_edit.text().strip(),
            "source_control_repos": self.staged_repos,
            "active_update_repo_id": self.staged_active_repo_id,
            "plugins_distro_repo": self.plugins_repo_edit.text().strip(),
        }

        if sys.platform == "win32":
            ss["nsis_path"] = self.nsis_path_edit.text().strip()
            ss["cleanup_after_build"] = self.cleanup_build_checkbox.isChecked()
            if winshell and hasattr(self, 'run_in_background_checkbox'):
                ss["run_in_background"] = self.run_in_background_checkbox.isChecked()
                if ss["run_in_background"] != self.original_settings.get("run_in_background", False):
                    self._manage_startup_shortcut(ss["run_in_background"])

        nn, ne = self.git_user_name_edit.text().strip(), self.git_user_email_edit.text().strip()
        if nn != self.original_git_config.get('name') or ne != self.original_git_config.get('email'):
            self.git_manager.set_git_config(nn, ne)
            self.original_git_config = {'name': nn, 'email': ne}

        self._save_repo_form_to_staged()

        for k, v in ss.items(): settings_manager.set(k, v, False)
        settings_manager.save()
        self.theme_changed_signal.emit(self.theme_combo.currentData())
        self.settings_changed_for_editor_refresh.emit()
        self.original_settings = settings_manager.settings.copy()
        ab.setEnabled(False)
        if self.restart_needed: QMessageBox.information(self, "Restart Required", "Some changes require a restart.")
        self.restart_needed = False
        log.info("Applied settings.")

    def accept(self):
        if self.button_box.button(QDialogButtonBox.StandardButton.Apply).isEnabled(): self.apply_settings()
        super().accept()

    def reject(self):
        if self.auth_dialog and self.auth_dialog.isVisible(): self.auth_dialog.reject()
        if self.button_box.button(QDialogButtonBox.StandardButton.Apply).isEnabled():
            if QMessageBox.question(self, "Unsaved Changes", "Discard?",
                                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No) == QMessageBox.StandardButton.No: return
        if self.theme_combo.currentData() != self.original_settings.get("last_theme_id"):
            self.theme_changed_signal.emit(self.original_settings.get("last_theme_id"))
        super().reject()

    def _create_layout_in_groupbox(self, t, pl):
        g = QGroupBox(t);
        pl.addWidget(g);
        l = QFormLayout(g);
        return l

    def _create_appearance_tab(self):
        tab = QWidget();
        layout = QVBoxLayout(tab);
        layout.setSpacing(15)
        theme_group = self._create_layout_in_groupbox("Theming", layout)
        self.theme_combo = QComboBox()
        self.edit_themes_button = QPushButton("Customize Themes...")
        self.connect_theme_editor_button()
        theme_group.addRow("Theme:", self.theme_combo)
        theme_group.addRow("", self.edit_themes_button)
        font_group = self._create_layout_in_groupbox("Editor Font", layout)
        self.font_family_combo = QFontComboBox()
        self.font_size_spinbox = QSpinBox();
        self.font_size_spinbox.setRange(6, 72)
        font_group.addRow("Font Family:", self.font_family_combo)
        font_group.addRow("Font Size:", self.font_size_spinbox)
        layout.addStretch()
        self.tab_widget.addTab(tab, qta.icon('fa5s.palette'), "Appearance")

    def _repopulate_theme_combo(self):
        current_id = self.original_settings.get("last_theme_id", "puffin_dark")
        self.theme_combo.blockSignals(True)
        self.theme_combo.clear()
        for theme_id, name in theme_manager.get_available_themes_for_ui().items():
            self.theme_combo.addItem(name, theme_id)
        if (index := self.theme_combo.findData(current_id)) != -1: self.theme_combo.setCurrentIndex(index)
        self.theme_combo.blockSignals(False)

    def connect_theme_editor_button(self):
        theme_editor_plugin = self.puffin_api.get_plugin_instance('theme_editor')
        if theme_editor_plugin:
            if launcher_func := getattr(theme_editor_plugin, 'show_theme_editor_dialog', None):
                try:
                    self.edit_themes_button.clicked.disconnect()
                except TypeError:
                    pass
                self.edit_themes_button.clicked.connect(launcher_func)
            if dialog := getattr(theme_editor_plugin, 'dialog', None):
                if hasattr(dialog, 'custom_themes_changed'):
                    dialog.custom_themes_changed.connect(self._repopulate_theme_combo)
            self.edit_themes_button.show()
        else:
            self.edit_themes_button.hide()

    def _create_editor_tab(self):
        tab = QWidget();
        layout = QVBoxLayout(tab);
        layout.setSpacing(15)
        display_layout = self._create_layout_in_groupbox("Display", layout)
        display_layout.setRowWrapPolicy(QFormLayout.RowWrapPolicy.WrapAllRows)
        self.show_line_numbers_checkbox = QCheckBox("Show line numbers")
        self.word_wrap_checkbox = QCheckBox("Enable word wrap")
        self.show_indent_guides_checkbox = QCheckBox("Show indentation guides")
        display_layout.addRow(self.show_line_numbers_checkbox)
        display_layout.addRow(self.word_wrap_checkbox)
        display_layout.addRow(self.show_indent_guides_checkbox)
        indent_layout = self._create_layout_in_groupbox("Indentation", layout)
        self.indent_style_combo = QComboBox();
        self.indent_style_combo.addItems(["Spaces", "Tabs"])
        self.indent_width_spinbox = QSpinBox();
        self.indent_width_spinbox.setRange(1, 16)
        indent_layout.addRow("Indent Using:", self.indent_style_combo)
        indent_layout.addRow("Indent/Tab Width:", self.indent_width_spinbox)
        file_layout = self._create_layout_in_groupbox("File Handling", layout)
        self.auto_save_checkbox = QCheckBox("Enable auto-save")
        self.auto_save_delay_spinbox = QSpinBox();
        self.auto_save_delay_spinbox.setRange(1, 60);
        self.auto_save_delay_spinbox.setSuffix(" seconds")
        self.max_recent_files_spinbox = QSpinBox();
        self.max_recent_files_spinbox.setRange(1, 50)
        file_layout.addRow(self.auto_save_checkbox)
        file_layout.addRow("Auto-Save Delay:", self.auto_save_delay_spinbox)
        file_layout.addRow("Max Recent Files:", self.max_recent_files_spinbox)
        layout.addStretch();
        self.tab_widget.addTab(tab, qta.icon('fa5s.edit'), "Editor")

    def _create_run_tab(self):
        tab = QWidget();
        layout = QVBoxLayout(tab);
        layout.setSpacing(15)
        py_group = self._create_layout_in_groupbox("Python Interpreter", layout)
        py_path_layout = QHBoxLayout();
        self.python_path_edit = QLineEdit()
        self.python_path_edit.setPlaceholderText("Leave empty to use system default")
        browse_py_button = QPushButton("Browse...");
        browse_py_button.clicked.connect(self._browse_for_python)
        py_path_layout.addWidget(self.python_path_edit);
        py_path_layout.addWidget(browse_py_button)
        py_group.addRow("Python Executable Path:", py_path_layout)

        build_group = self._create_layout_in_groupbox("Build & Installation (Windows Only)", layout)
        if sys.platform == "win32":
            nsis_path_layout = QHBoxLayout();
            self.nsis_path_edit = QLineEdit()
            self.nsis_path_edit.setPlaceholderText("e.g., C:\\Program Files (x86)\\NSIS\\makensis.exe")
            browse_nsis_button = QPushButton("Browse...");
            browse_nsis_button.clicked.connect(self._browse_for_nsis)
            nsis_path_layout.addWidget(self.nsis_path_edit);
            nsis_path_layout.addWidget(browse_nsis_button)
            self.cleanup_build_checkbox = QCheckBox("Delete temporary build files after install")
            build_group.addRow("NSIS Path (for Installer):", nsis_path_layout)
            build_group.addRow("", self.cleanup_build_checkbox)
        else:
            build_group.addRow(QLabel("Build options are only available on Windows."))

        layout.addStretch();
        self.tab_widget.addTab(tab, qta.icon('fa5s.play-circle'), "Execution")

    def _browse_for_nsis(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select NSIS Executable", "", "NSIS (makensis.exe);;All Files (*)")
        if path: self.nsis_path_edit.setText(path)

    def _browse_for_python(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select Python Executable", "",
                                              "Python Executable (python.exe; python);;All Files (*)")
        if path: self.python_path_edit.setText(path)

    def _create_system_tab(self):
        tab = QWidget();
        layout = QVBoxLayout(tab);
        layout.setSpacing(15)
        startup_group = self._create_layout_in_groupbox("System Startup", layout)
        if sys.platform == "win32" and winshell:
            self.run_in_background_checkbox = QCheckBox("Launch PuffinPyEditor on system startup (runs in system tray)")
            self.run_in_background_checkbox.setToolTip("Creates a shortcut in the Windows Startup folder.")
            startup_group.addRow(self.run_in_background_checkbox)
        else:
            startup_group.addRow(QLabel("Startup options are only available on Windows."))
        layout.addStretch();
        self.tab_widget.addTab(tab, qta.icon('fa5s.desktop'), "System")

    def _manage_startup_shortcut(self, create):
        if not winshell: return
        shortcut_path = get_startup_shortcut_path()
        if not shortcut_path: return
        try:
            if create and not os.path.exists(shortcut_path):
                tray_exe_path = os.path.join(os.path.dirname(sys.executable), "PuffinPyTray.exe")
                if not os.path.exists(tray_exe_path): raise FileNotFoundError("PuffinPyTray.exe not found.")
                winshell.CreateShortcut(Path=shortcut_path, Target=tray_exe_path)
            elif not create and os.path.exists(shortcut_path):
                os.remove(shortcut_path)
        except Exception as e:
            QMessageBox.critical(self, "Shortcut Error", f"Could not manage startup shortcut:\n{e}")

    def _create_source_control_tab(self):
        tab = QWidget();
        layout = QVBoxLayout(tab);
        layout.setSpacing(15)
        git_user_group = self._create_layout_in_groupbox("Git Identity", layout)
        self.git_user_name_edit = QLineEdit();
        self.git_user_email_edit = QLineEdit()
        git_user_group.addRow("Username:", self.git_user_name_edit)
        git_user_group.addRow("Email:", self.git_user_email_edit)

        gh_auth_group = self._create_layout_in_groupbox("GitHub Integration", layout)
        self.auth_status_label = QLabel("<i>Checking status...</i>")
        self.auth_button = QPushButton("Log in to GitHub")
        self.auth_button.clicked.connect(self.github_manager.start_device_flow)
        self.logout_button = QPushButton("Log out")
        self.logout_button.clicked.connect(self._logout_github)
        gh_auth_group.addRow(self.auth_status_label);
        gh_auth_group.addRow(self.auth_button);
        gh_auth_group.addRow(self.logout_button)

        repo_group = self._create_layout_in_groupbox("Update Repository Management", layout)
        repo_splitter, _ = self._create_repo_management_widgets()
        repo_group.layout().addWidget(repo_splitter)

        layout.addStretch();
        self.tab_widget.addTab(tab, qta.icon('fa5b.git-alt'), "Source Control")

    def _create_repo_management_widgets(self):
        splitter = QSplitter();
        left_widget = QWidget();
        left_layout = QVBoxLayout(left_widget)
        left_layout.addWidget(QLabel("Repositories:"))
        self.repo_list = QListWidget();
        self.repo_list.currentItemChanged.connect(self._on_repo_selection_changed)
        left_layout.addWidget(self.repo_list)

        repo_buttons = QHBoxLayout();
        add_repo_btn = QPushButton();
        add_repo_btn.setIcon(qta.icon('fa5s.plus'));
        remove_repo_btn = QPushButton();
        remove_repo_btn.setIcon(qta.icon('fa5s.minus'));
        add_repo_btn.clicked.connect(self._action_add_repo);
        remove_repo_btn.clicked.connect(self._action_remove_repo)
        repo_buttons.addStretch();
        repo_buttons.addWidget(add_repo_btn);
        repo_buttons.addWidget(remove_repo_btn)
        left_layout.addLayout(repo_buttons);
        splitter.addWidget(left_widget)

        form_widget = QWidget();
        form_layout = QFormLayout(form_widget)
        self.repo_name_edit = QLineEdit();
        self.repo_owner_edit = QLineEdit();
        self.repo_repo_edit = QLineEdit()
        self.repo_is_active_checkbox = QCheckBox("Set as active repo for app updates");
        self.repo_is_active_checkbox.toggled.connect(self._on_active_checkbox_toggled)
        self.create_on_gh_button = QPushButton("Create on GitHub & Link");
        self.create_on_gh_button.clicked.connect(self._action_create_repo)
        form_layout.addRow("Name:", self.repo_name_edit)
        form_layout.addRow("Owner (user or org):", self.repo_owner_edit)
        form_layout.addRow("Repository Name:", self.repo_repo_edit)
        form_layout.addRow(self.repo_is_active_checkbox);
        form_layout.addRow(self.create_on_gh_button)
        splitter.addWidget(form_widget);
        return splitter, form_widget

    def _create_plugins_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)

        plugins_tabs = QTabWidget()
        plugins_tabs.addTab(self._create_plugins_manage_tab(), qta.icon('fa5s.tasks'), "Manage")
        plugins_tabs.addTab(self._create_plugins_install_tab(), qta.icon('fa5s.download'), "Install")

        layout.addWidget(plugins_tabs)
        self.tab_widget.addTab(tab, qta.icon('fa5s.plug'), "Plugins")

    def _create_plugins_manage_tab(self):
        tab = QWidget();
        layout = QHBoxLayout(tab);
        splitter = QSplitter(Qt.Orientation.Horizontal)
        left_widget = QWidget();
        left_layout = QVBoxLayout(left_widget);
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.addWidget(QLabel("Installed Plugins:"))
        self.manage_plugins_list = QListWidget();
        self.manage_plugins_list.itemSelectionChanged.connect(self._on_installed_plugin_selected)
        left_layout.addWidget(self.manage_plugins_list)

        # MODIFICATION: Add Enable/Disable All buttons
        batch_buttons_layout = QHBoxLayout()
        self.enable_all_button = QPushButton("Enable All")
        self.disable_all_button = QPushButton("Disable All (Non-Core)")
        self.enable_all_button.clicked.connect(self._enable_all_plugins)
        self.disable_all_button.clicked.connect(self._disable_all_non_core_plugins)
        batch_buttons_layout.addWidget(self.enable_all_button)
        batch_buttons_layout.addWidget(self.disable_all_button)
        left_layout.addLayout(batch_buttons_layout)

        right_widget = QWidget();
        right_layout = QVBoxLayout(right_widget)
        self.plugin_details_stack = QStackedWidget()
        placeholder = QLabel("Select a plugin to see details.");
        placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.plugin_details_stack.addWidget(placeholder)
        details_widget = QWidget();
        details_layout = QFormLayout(details_widget)
        self.plugin_name_label = QLabel();
        self.plugin_version_label = QLabel();
        self.plugin_author_label = QLabel()
        self.plugin_desc_label = QLabel();
        self.plugin_desc_label.setWordWrap(True);
        self.plugin_status_label = QLabel()
        details_layout.addRow("<b>Name:</b>", self.plugin_name_label)
        details_layout.addRow("<b>Version:</b>", self.plugin_version_label)
        details_layout.addRow("<b>Author:</b>", self.plugin_author_label)
        details_layout.addRow("<b>Description:</b>", self.plugin_desc_label)
        details_layout.addRow("<b>Status:</b>", self.plugin_status_label)
        self.plugin_details_stack.addWidget(details_widget)
        actions_layout = QHBoxLayout()
        self.enable_plugin_checkbox = QCheckBox("Enabled");
        self.enable_plugin_checkbox.toggled.connect(self._on_plugin_enabled_changed)
        self.reload_plugin_button = QPushButton("Reload");
        self.reload_plugin_button.clicked.connect(self._reload_selected_plugin)
        self.uninstall_button = QPushButton("Uninstall");
        self.uninstall_button.clicked.connect(self._uninstall_selected_plugin)
        actions_layout.addWidget(self.enable_plugin_checkbox);
        actions_layout.addStretch()
        actions_layout.addWidget(self.reload_plugin_button);
        actions_layout.addWidget(self.uninstall_button)
        right_layout.addWidget(self.plugin_details_stack, 1);
        right_layout.addLayout(actions_layout)
        splitter.addWidget(left_widget);
        splitter.addWidget(right_widget)
        splitter.setSizes([300, 550]);
        layout.addWidget(splitter)
        return tab

    def _create_plugins_install_tab(self):
        tab = QWidget();
        layout = QVBoxLayout(tab);
        layout.setSpacing(10)
        repo_group = QGroupBox("Install from Repository");
        repo_layout = QVBoxLayout(repo_group)

        # This widget/layout wrapper fixes the "already has a parent" issue.
        repo_input_widget = QWidget()
        repo_input_layout = QHBoxLayout(repo_input_widget)
        repo_input_layout.setContentsMargins(0, 0, 0, 0)
        repo_input_layout.addWidget(QLabel("GitHub Repo (user/repo):"))
        self.plugins_repo_edit = QLineEdit()
        self.fetch_plugins_button = QPushButton("Fetch");
        self.fetch_plugins_button.clicked.connect(self._fetch_remote_plugins)
        repo_input_layout.addWidget(self.plugins_repo_edit, 1);
        repo_input_layout.addWidget(self.fetch_plugins_button)
        repo_layout.addWidget(repo_input_widget)

        self.remote_plugins_list = QListWidget();
        self.remote_plugins_list.itemSelectionChanged.connect(self._on_remote_plugin_selected)
        repo_layout.addWidget(self.remote_plugins_list)
        self.install_remote_button = QPushButton("Install Selected Plugin");
        self.install_remote_button.setEnabled(False);
        self.install_remote_button.clicked.connect(self._install_selected_remote_plugin)
        repo_layout.addWidget(self.install_remote_button, 0, Qt.AlignmentFlag.AlignRight)
        layout.addWidget(repo_group)

        local_group = QGroupBox("Install from File/URL");
        local_layout = QHBoxLayout(local_group)
        self.install_from_url_button = QPushButton("From URL...");
        self.install_from_file_button = QPushButton("From File...")
        self.install_from_url_button.clicked.connect(lambda: self._install_plugin_from_url(""))
        self.install_from_file_button.clicked.connect(self._install_plugin_from_file)
        local_layout.addWidget(self.install_from_url_button);
        local_layout.addWidget(self.install_from_file_button)
        local_layout.addStretch()
        # This also fixes a layout issue by putting the QHBoxLayout into the main QVBoxLayout correctly
        layout.addWidget(local_group)
        layout.addStretch()
        return tab

    def _action_create_repo(self):
        owner, repo = self.repo_owner_edit.text(), self.repo_repo_edit.text()
        if owner and repo: self.github_manager.create_repo(repo, "", False)

    def _populate_git_config_fields(self, name, email):
        self.git_user_name_edit.setText(name);
        self.git_user_email_edit.setText(email)
        self.original_git_config = {'name': name, 'email': email}

    def _handle_git_success(self, msg, data):
        if "config updated" in msg: self._on_ui_setting_changed()

    def _logout_github(self):
        self.github_manager.logout();
        self._update_auth_status()

    def _update_auth_status(self):
        user = self.github_manager.get_authenticated_user()
        if user:
            self.auth_status_label.setText(
                f"Logged in as: <b>{user}</b>"); self.auth_button.hide(); self.logout_button.show()
        else:
            self.auth_status_label.setText("<i>Not logged in.</i>"); self.auth_button.show(); self.logout_button.hide()

    def _on_device_code_ready(self, data):
        self.auth_dialog = AuthDialog(data.get('user_code'), data.get('verification_uri'), self);
        self.auth_dialog.show()
        self.github_manager.poll_for_token(data['device_code'], data['interval'], data['expires_in'])

    def _on_auth_successful(self, username):
        if self.auth_dialog: self.auth_dialog.accept(); self.auth_dialog = None
        self._update_auth_status();
        self._on_ui_setting_changed()

    def _on_auth_failed(self, error):
        if self.auth_dialog: self.auth_dialog.reject(); self.auth_dialog = None
        QMessageBox.critical(self, "GitHub Authentication Failed", error);
        self._update_auth_status()

    def _on_auth_polling_lapsed(self):
        if self.auth_dialog: self.auth_dialog.reject(); self.auth_dialog = None
        QMessageBox.warning(self, "Authentication Timed Out", "Device authorization timed out.")

    def _on_repo_selection_changed(self, current, previous):
        if previous: self._save_repo_form_to_staged()
        self._load_staged_to_repo_form(current)

    def _on_active_checkbox_toggled(self, checked):
        if checked and self.current_repo_id_in_form: self.staged_active_repo_id = self.current_repo_id_in_form
        self._on_ui_setting_changed()

    def _save_repo_form_to_staged(self):
        if not self.current_repo_id_in_form: return
        repo = next((r for r in self.staged_repos if r['id'] == self.current_repo_id_in_form), None)
        if repo: repo['name'] = self.repo_name_edit.text(); repo['owner'] = self.repo_owner_edit.text(); repo[
            'repo'] = self.repo_repo_edit.text()

    def _load_staged_to_repo_form(self, item):
        self.is_loading = True;
        self.current_repo_id_in_form = item.data(Qt.ItemDataRole.UserRole) if item else None
        if self.current_repo_id_in_form:
            repo = next((r for r in self.staged_repos if r['id'] == self.current_repo_id_in_form), {});
            self.repo_name_edit.setText(repo.get('name', ''));
            self.repo_owner_edit.setText(repo.get('owner', ''));
            self.repo_repo_edit.setText(repo.get('repo', ''))
            self.repo_is_active_checkbox.setChecked(self.current_repo_id_in_form == self.staged_active_repo_id)
        else:
            self._clear_repo_form()
        self.is_loading = False

    def _action_add_repo(self):
        new_repo = {"id": str(uuid.uuid4()), "name": "New Repository", "owner": "", "repo": ""};
        self.staged_repos.append(new_repo);
        self._populate_repo_list(select_repo_id=new_repo['id']);
        self._on_ui_setting_changed()

    def _action_remove_repo(self):
        if item := self.repo_list.currentItem():
            repo_id = item.data(Qt.ItemDataRole.UserRole);
            self.staged_repos = [r for r in self.staged_repos if r['id'] != repo_id]
            if self.staged_active_repo_id == repo_id: self.staged_active_repo_id = None
            self._populate_repo_list();
            self._on_ui_setting_changed()

    def _populate_repo_list(self, select_repo_id=None):
        self.repo_list.clear();
        self._clear_repo_form()
        for repo in self.staged_repos:
            item = QListWidgetItem(repo['name']);
            item.setData(Qt.ItemDataRole.UserRole, repo['id']);
            self.repo_list.addItem(item)
        if select_repo_id:
            for i in range(self.repo_list.count()):
                if self.repo_list.item(i).data(
                    Qt.ItemDataRole.UserRole) == select_repo_id: self.repo_list.setCurrentRow(i); break

    def _clear_repo_form(self):
        self.repo_name_edit.clear();
        self.repo_owner_edit.clear();
        self.repo_repo_edit.clear();
        self.repo_is_active_checkbox.setChecked(False)

    def _populate_all_plugin_lists(self):
        self._populate_manage_plugins_list()

    def _populate_manage_plugins_list(self):
        self.manage_plugins_list.clear();
        plugins = sorted(self.plugin_manager.get_all_plugins(), key=lambda p: p.name.lower())
        for p in plugins:
            item = QListWidgetItem(p.name);
            item.setData(Qt.ItemDataRole.UserRole, p.id);
            self.manage_plugins_list.addItem(item)

    def _on_installed_plugin_selected(self):
        items = self.manage_plugins_list.selectedItems()
        if not items: self.plugin_details_stack.setCurrentIndex(0); return
        plugin = self.plugin_manager.plugins.get(items[0].data(Qt.ItemDataRole.UserRole))
        if plugin:
            self.plugin_details_stack.setCurrentIndex(1);
            self.is_loading = True
            self.plugin_name_label.setText(plugin.name);
            self.plugin_version_label.setText(plugin.version);
            self.plugin_author_label.setText(plugin.manifest.get('author', 'N/A'))
            self.plugin_desc_label.setText(plugin.manifest.get('description', 'No description.'))
            self.plugin_status_label.setText(plugin.status_reason)
            self.enable_plugin_checkbox.setChecked(plugin.enabled);
            self.enable_plugin_checkbox.setEnabled(not plugin.is_core)
            self.reload_plugin_button.setEnabled(plugin.is_loaded);
            self.uninstall_button.setEnabled(not plugin.is_core)
            self.is_loading = False

    def _on_plugin_enabled_changed(self, checked):
        if self.is_loading: return
        items = self.manage_plugins_list.selectedItems()
        if items and (plugin := self.plugin_manager.plugins.get(items[0].data(Qt.ItemDataRole.UserRole))):
            if checked:
                self.plugin_manager.enable_plugin(plugin.id)
            else:
                self.plugin_manager.disable_plugin(plugin.id)
            self.restart_needed = True

    def _reload_selected_plugin(self):
        items = self.manage_plugins_list.selectedItems();
        self.restart_needed = True
        if items: self.plugin_manager.reload_plugin(
            items[0].data(Qt.ItemDataRole.UserRole)); self._on_installed_plugin_selected()

    def _reload_all_plugins(self):
        self.plugin_manager.discover_and_load_plugins();
        self.restart_needed = True
        self._populate_manage_plugins_list()  # Repopulate list after reloading all

    def _enable_all_plugins(self):
        reply = QMessageBox.question(self, "Enable All Plugins",
                                     "This will enable all plugins and reload them. "
                                     "A restart might be required for all changes to take full effect.\n\n"
                                     "Continue?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                     QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            log.info("User requested to enable all plugins.")
            self.plugin_manager.enable_all()
            self.restart_needed = True
            self._populate_manage_plugins_list()
            self._on_ui_setting_changed()

    def _disable_all_non_core_plugins(self):
        reply = QMessageBox.question(self, "Disable All Non-Core Plugins",
                                     "This will disable and unload all user-installed plugins. "
                                     "Built-in tools will not be affected.\n\n"
                                     "Continue?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                     QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            log.info("User requested to disable all non-core plugins.")
            self.plugin_manager.disable_all_non_core()
            self.restart_needed = True
            self._populate_manage_plugins_list()
            self._on_ui_setting_changed()

    def _on_remote_plugin_selected(self):
        self.install_remote_button.setEnabled(bool(self.remote_plugins_list.selectedItems()))

    def _fetch_remote_plugins(self):
        self.github_manager.fetch_plugin_index(self.plugins_repo_edit.text().strip())

    def _on_plugin_index_ready(self, plugin_list):
        self.remote_plugins_list.clear()
        for p in plugin_list:
            item = QListWidgetItem(f"{p['name']} v{p['version']}");
            item.setData(Qt.ItemDataRole.UserRole, p);
            self.remote_plugins_list.addItem(item)

    def _install_selected_remote_plugin(self):
        if item := self.remote_plugins_list.currentItem(): self._install_plugin_from_url(
            item.data(Qt.ItemDataRole.UserRole).get('download_url'))

    def _install_plugin_from_url(self, url):
        if not url: url, ok = QInputDialog.getText(self, "Install from URL", "Plugin ZIP URL:");
        if not (url and ok): return

        with tempfile.TemporaryDirectory() as temp_dir:
            try:
                r = requests.get(url);
                r.raise_for_status()
                zip_path = os.path.join(temp_dir, "plugin.zip");
                with open(zip_path, 'wb') as f:
                    f.write(r.content)
                ok, msg = self.plugin_manager.install_plugin_from_zip(zip_path)
                QMessageBox.information(self, "Plugin Install", msg) if ok else QMessageBox.warning(self,
                                                                                                    "Install Failed",
                                                                                                    msg)
                self.restart_needed = True
            except Exception as e:
                QMessageBox.critical(self, "Download Error", f"Failed to download or install plugin: {e}")

    def _install_plugin_from_file(self):
        f, _ = QFileDialog.getOpenFileName(self, "Select Plugin Zip", "", "ZIP Archives (*.zip)")
        if f:
            ok, msg = self.plugin_manager.install_plugin_from_zip(f)
            QMessageBox.information(self, "Plugin Install", msg) if ok else QMessageBox.warning(self, "Install Failed",
                                                                                                msg)
            self.restart_needed = True
            self._populate_manage_plugins_list()

    def _uninstall_selected_plugin(self):
        if items := self.manage_plugins_list.selectedItems():
            pid = items[0].data(Qt.ItemDataRole.UserRole)
            plugin = self.plugin_manager.plugins.get(pid)
            if QMessageBox.question(self, "Confirm Uninstall",
                                    f"Are you sure you want to uninstall '{plugin.name}'?") == QMessageBox.StandardButton.Yes:
                ok, msg = self.plugin_manager.uninstall_plugin(pid);
                QMessageBox.information(self, "Uninstall", msg) if ok else QMessageBox.warning(self, "Uninstall Failed",
                                                                                               msg)
                self.restart_needed = True;
                self._populate_all_plugin_lists()
```

### File: `/utils/__init__.py`

```python

```

### File: `/utils/helpers.py`

```python
# PuffinPyEditor/utils/helpers.py
import sys
import os
from typing import List, Optional
from PyQt6.QtGui import QFontDatabase
from .logger import log

if sys.platform == "win32":
    import winshell


def get_base_path():
    """
    Returns the application's base path for resource loading.

    This handles the difference between running from source and a frozen
    (e.g., PyInstaller) executable. For a frozen app, this is the directory
    of the executable. For a source app, this is the project root.
    """
    if getattr(sys, 'frozen', False):
        # The application is frozen
        return os.path.dirname(sys.executable)
    else:
        # Assumes this file is in /utils, so two levels up is the project root
        return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def get_startup_shortcut_path() -> Optional[str]:
    """
    Gets the cross-platform path to the user's startup folder.

    This is used for creating a shortcut to launch the app on system startup.
    Returns None if the platform is not supported (currently only Windows).
    """
    if sys.platform == "win32":
        try:
            startup_folder = winshell.folder("startup")
            return os.path.join(startup_folder, "PuffinPyEditor.lnk")
        except Exception as e:
            log.error(f"Could not get Windows startup folder path: {e}")
            return None
    return None


def get_best_available_font(preferred_list: List[str]) -> Optional[str]:
    """
    Scans a preferred list of font families and returns the first one found
    on the user's system.

    This is useful for setting sensible default fonts for different themes
    or operating systems.

    Args:
        preferred_list: A list of font family names, in order of preference.

    Returns:
        The name of the first available font, or None if none are found.
    """
    if not isinstance(preferred_list, list):
        log.warning(
            f"Font list provided is not a list: {preferred_list}. "
            "No font selected."
        )
        return None

    font_db = QFontDatabase()
    installed_fonts = {font.lower() for font in font_db.families()}

    for font_name in preferred_list:
        if font_name.lower() in installed_fonts:
            log.info(f"Font suggestion: Found '{font_name}' installed on system.")
            return font_name

    log.warning(
        f"Could not find any of the preferred fonts: {preferred_list}. "
        "The application will use a system default."
    )
    return None
```

### File: `/utils/log_viewer.py`

```python
# PuffinPyEditor/utils/log_viewer.py
import sys
import os
import re
from collections import deque
from PyQt6.QtWidgets import (QApplication, QMainWindow, QTextEdit, QVBoxLayout,
                             QWidget, QHBoxLayout, QPushButton, QCheckBox, QLabel,
                             QFileDialog, QMessageBox)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import QFileSystemWatcher, QTimer
import qtawesome as qta


class LogViewerWindow(QMainWindow):
    """A standalone app to view a log file in real-time with filtering."""

    def __init__(self, log_file_path):
        super().__init__()
        self.log_file_path = log_file_path
        self.last_pos = 0
        self.all_lines = []
        # Default to only showing ERROR and CRITICAL levels on startup
        self.active_levels = {'ERROR', 'CRITICAL'}
        self.level_pattern = re.compile(
            r" - (DEBUG|INFO|WARNING|ERROR|CRITICAL) - "
        )
        # Regex to find file paths like [module.function:lineno]
        self.file_path_pattern = re.compile(r"\[([a-zA-Z0-9_.-]+):[0-9]+\]")
        self.project_root = self._get_project_root()

        self.setWindowTitle(
            f"PuffinPy Log Viewer - {os.path.basename(log_file_path)}"
        )
        self.setMinimumSize(800, 500)
        self.setStyleSheet("background-color: #2D2A2E;")

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        layout = QVBoxLayout(self.central_widget)
        self._setup_controls(layout)

        self.text_edit = QTextEdit()
        self.text_edit.setReadOnly(True)
        self.text_edit.setFont(QFont("Consolas", 10))
        self.text_edit.setStyleSheet(
            "background-color: #1E1C21; color: #E0E0E0; "
            "border: none; padding: 5px;"
        )
        layout.addWidget(self.text_edit)

        # File watcher
        self.watcher = QFileSystemWatcher()
        self.watcher.fileChanged.connect(self._read_new_log_content)

        # Initial load is deferred to avoid blocking the UI
        QTimer.singleShot(50, self.perform_initial_load)

    def _get_project_root(self):
        """Determines the project's root directory for finding source files."""
        if getattr(sys, 'frozen', False):
            # In a bundled app, the root is the executable's directory
            return os.path.dirname(sys.executable)
        else:
            # In dev, it's two levels up from this file (utils/ -> project_root/)
            return os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

    def _setup_controls(self, parent_layout):
        controls_widget = QWidget()
        controls_layout = QHBoxLayout(controls_widget)
        controls_layout.setContentsMargins(5, 5, 5, 5)

        # Level Filters
        controls_layout.addWidget(QLabel("Show Levels:"))
        self.debug_check = self._create_filter_checkbox("DEBUG", False)
        self.info_check = self._create_filter_checkbox("INFO", False)
        self.warning_check = self._create_filter_checkbox("WARNING", False)
        self.error_check = self._create_filter_checkbox("ERROR", True)
        self.critical_check = self._create_filter_checkbox("CRITICAL", True)

        controls_layout.addWidget(self.debug_check)
        controls_layout.addWidget(self.info_check)
        controls_layout.addWidget(self.warning_check)
        controls_layout.addWidget(self.error_check)
        controls_layout.addWidget(self.critical_check)
        controls_layout.addStretch()

        # Other Controls
        self.autoscroll_check = QCheckBox("Auto-scroll")
        self.autoscroll_check.setChecked(True)
        clear_button = QPushButton("Clear")
        export_button = QPushButton("Export for AI")
        export_button.setIcon(qta.icon('fa5s.robot'))
        export_button.setToolTip(
            "Export visible logs and referenced source files for AI analysis."
        )

        controls_layout.addWidget(self.autoscroll_check)
        controls_layout.addWidget(clear_button)
        controls_layout.addWidget(export_button)
        parent_layout.addWidget(controls_widget)

        # Connect signals
        clear_button.clicked.connect(self.clear_log)
        export_button.clicked.connect(self._export_for_ai)

    def _create_filter_checkbox(self, text, default_checked=True):
        cb = QCheckBox(text)
        cb.setChecked(default_checked)
        cb.toggled.connect(
            lambda checked, lvl=text: self._on_filter_changed(checked, [lvl])
        )
        return cb

    def perform_initial_load(self):
        """Loads the initial view of the log file, tailing it for speed."""
        if not os.path.exists(self.log_file_path):
            self.text_edit.setText(
                f"Waiting for log file: {self.log_file_path}..."
            )
            if not self.watcher.files():
                self.watcher.addPath(self.log_file_path)
            return

        if not self.watcher.files():
            self.watcher.addPath(self.log_file_path)

        try:
            with open(self.log_file_path, 'r', encoding='utf-8') as f:
                tailed_lines = deque(f, 500)
                self.all_lines = list(tailed_lines)
                self.last_pos = f.tell()
                self._apply_filters_to_display()

            QTimer.singleShot(200, self._load_full_log)
        except Exception as e:
            self.text_edit.setText(f"Error loading log file: {e}")

    def _load_full_log(self):
        """Reads the entire log file into memory after startup."""
        try:
            with open(self.log_file_path, 'r', encoding='utf-8') as f:
                self.all_lines = f.readlines()
            self._apply_filters_to_display()
        except Exception as e:
            print(f"Error doing full log read: {e}")

    def _read_new_log_content(self):
        """Reads only the new content from the log file and appends it."""
        try:
            with open(self.log_file_path, 'r', encoding='utf-8') as f:
                current_size = f.seek(0, 2)
                if current_size < self.last_pos:
                    self.last_pos = 0  # Log file was likely cleared

                f.seek(self.last_pos)
                new_content = f.read()
                if new_content:
                    new_lines = new_content.strip().split('\n')
                    self.all_lines.extend(line + '\n' for line in new_lines)

                    visible_new_lines = self._filter_lines(new_lines)
                    if visible_new_lines:
                        cursor = self.text_edit.textCursor()
                        cursor.movePosition(cursor.MoveOperation.End)
                        self.text_edit.setTextCursor(cursor)
                        self.text_edit.insertPlainText(
                            "\n".join(visible_new_lines) + "\n"
                        )
                self.last_pos = f.tell()

            if self.autoscroll_check.isChecked():
                v_bar = self.text_edit.verticalScrollBar()
                v_bar.setValue(v_bar.maximum())
        except Exception as e:
            print(f"Error updating log: {e}")
            self.last_pos = 0

    def _on_filter_changed(self, checked, levels):
        """Updates the active levels set and reapplies the filter."""
        for level in levels:
            if checked:
                self.active_levels.add(level)
            else:
                self.active_levels.discard(level)
        self._apply_filters_to_display()

    def _get_line_level(self, line: str):
        match = self.level_pattern.search(line)
        return match.group(1) if match else None

    def _filter_lines(self, lines: list[str]) -> list[str]:
        visible = []
        for line in lines:
            level = self._get_line_level(line)
            if level is None or level in self.active_levels:
                visible.append(line.strip())
        return visible

    def _apply_filters_to_display(self):
        visible_lines = self._filter_lines(self.all_lines)
        self.text_edit.setText("\n".join(visible_lines))
        if self.autoscroll_check.isChecked():
            v_bar = self.text_edit.verticalScrollBar()
            v_bar.setValue(v_bar.maximum())

    def _export_for_ai(self):
        """Gathers visible logs and associated source files for AI analysis."""
        visible_log_content = self.text_edit.toPlainText()
        if not visible_log_content.strip():
            QMessageBox.warning(self, "Empty Log",
                                "There is no visible log content to export.")
            return

        # Find unique source files mentioned in the logs
        files_to_include = set()
        for match in self.file_path_pattern.finditer(visible_log_content):
            module_path = match.group(1)
            # Convert module path (e.g., app_core.logger) to file path
            file_path = os.path.join(self.project_root, *module_path.split('.'))
            file_path += ".py"
            if os.path.exists(file_path):
                files_to_include.add(os.path.normpath(file_path))

        sugg_path = os.path.join(os.path.expanduser("~"), "puffin_debug_export.md")
        filepath, _ = QFileDialog.getSaveFileName(
            self, "Save Debug Export", sugg_path, "Markdown Files (*.md)"
        )
        if not filepath:
            return

        export_content = [
            "# PuffinPyEditor Debugging Export", "## AI Instructions",
            "Analyze the following log output and the associated source code "
            "files to identify the root cause of the error. Provide a "
            "detailed explanation and a suggested fix.", "---",
            "## Visible Log Output", "```log", visible_log_content, "```",
            "---", "## Included File Contents"
        ]

        for source_file in sorted(list(files_to_include)):
            rel_path = os.path.relpath(
                source_file, self.project_root
            ).replace(os.sep, '/')
            export_content.append(f"\n### File: `{rel_path}`\n")
            export_content.append("```python")
            try:
                with open(source_file, 'r', encoding='utf-8') as f:
                    export_content.append(f.read())
            except Exception as e:
                export_content.append(f"# Error reading file: {e}")
            export_content.append("```")

        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write("\n".join(export_content))
            QMessageBox.information(
                self, "Export Complete",
                f"Debug information successfully exported to:\n{filepath}"
            )
        except IOError as e:
            QMessageBox.critical(self, "Export Failed",
                                 f"Could not write to file: {e}")

    def clear_log(self):
        self.text_edit.clear()
        self.all_lines = []
        self.last_pos = 0
        if os.path.exists(self.log_file_path):
            try:
                open(self.log_file_path, 'w').close()
            except IOError as e:
                print(f"Could not clear log file on disk: {e}")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    if len(sys.argv) < 2:
        dummy_log_path = os.path.join(os.getcwd(), "dummy_app.log")
        if not os.path.exists(dummy_log_path):
            with open(dummy_log_path, 'w') as f:
                f.write("2025-01-01 12:00:00,000 - INFO - "
                        "[test.main:1] - This is a dummy log file.\n")
        log_path = dummy_log_path
    else:
        log_path = sys.argv[1]

    viewer = LogViewerWindow(log_path)
    viewer.show()
    sys.exit(app.exec())
```

### File: `/utils/logger.py`

```python
# PuffinPyEditor/utils/logger.py
import logging
import os
import platform
from logging.handlers import RotatingFileHandler

APP_NAME = "PuffinPyEditor"
ORG_NAME = "PuffinPyEditorProject"


def get_app_data_path() -> str:
    """
    Gets a cross-platform writable directory for application data.

    Returns:
        A string representing the path to the application data directory.
    """
    system = platform.system()
    if system == "Windows":
        # e.g., C:\Users\<user>\AppData\Local\PuffinPyEditorProject\...
        path = os.path.join(os.environ.get('LOCALAPPDATA', ''),
                            ORG_NAME, APP_NAME)
    elif system == "Darwin":  # macOS
        # e.g., /Users/<user>/Library/Application Support/PuffinPyEditorProject/...
        path = os.path.join(os.path.expanduser(
            '~/Library/Application Support'), ORG_NAME, APP_NAME)
    else:  # Linux and other systems
        # e.g., /home/<user>/.local/share/PuffinPyEditorProject/...
        path = os.path.join(os.path.expanduser('~/.local/share'),
                            ORG_NAME, APP_NAME)

    return path


# This will now be a path in the user's home directory, which is always writable.
APP_DATA_ROOT = get_app_data_path()
LOG_DIR = os.path.join(APP_DATA_ROOT, "logs")

# Use exist_ok=True for robustness. This creates the directory if it doesn't
# exist and does nothing if it already exists, preventing race conditions.
os.makedirs(LOG_DIR, exist_ok=True)

LOG_FILE = os.path.join(LOG_DIR, "app.log")


def setup_logger(name: str = "PuffinPyEditor",
                   log_level: int = logging.DEBUG) -> logging.Logger:
    """
    Configures and returns a logger instance.
    """
    logger = logging.getLogger(name)
    if logger.hasHandlers():
        logger.handlers.clear()

    logger.setLevel(log_level)

    formatter = logging.Formatter(
        "%(asctime)s - %(levelname)s - "
        "[%(module)s.%(funcName)s:%(lineno)d] - %(message)s"
    )

    # StreamHandler logs to the console
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)  # Console logs can be less verbose
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    # RotatingFileHandler logs to a file in the user-writable location
    try:
        fh = RotatingFileHandler(
            LOG_FILE, maxBytes=5*1024*1024, backupCount=5, encoding='utf-8'
        )
        fh.setLevel(log_level)  # File logs should be detailed
        fh.setFormatter(formatter)
        logger.addHandler(fh)
    except Exception as e:
        logger.error(
            f"Failed to create file handler for logging: {e}", exc_info=False
        )

    logger.info(f"Logger initialized. Log file at: {LOG_FILE}")
    return logger


# Global logger instance for the application
log = setup_logger()
```

### File: `/utils/markdown_linter.py`

```python
# PuffinPyEditor/utils/markdown_linter.py
import re
from typing import List, Dict


def lint_markdown_file(content: str) -> List[Dict]:
    """
    Performs a basic lint on Markdown content to find common errors.

    Args:
        content: The string content of the Markdown file.

    Returns:
        A list of problem dictionaries, compatible with the ProblemsPanel.
    """
    problems = []
    # Regex to find three backticks, optional whitespace, a newline,
    # and then a language identifier on the next line.
    # This is a common error that breaks syntax highlighting.
    malformed_fence_regex = re.compile(r"^(```)\s*\n\s*(\S+)")

    for i, line in enumerate(content.splitlines()):
        # --- Rule 1: Malformed code fence ---
        match = malformed_fence_regex.match(line)
        if match:
            lang = match.group(2)
            # The error is on the line with the backticks.
            # We report it for the line number `i`.
            problems.append({
                'line': i + 1,
                'col': 1,
                'code': 'MD001',
                'description': f"Fenced code block language '{lang}' should be "
                               f"on the same line as the opening ```."
            })

    # Add more rules here in the future...

    return problems
```

### File: `/utils/validate_assets.py`

```python
# PuffinPyEditor/utils/validate_assets.py
import os
import json
import re
from typing import List, Dict, Any, Tuple

# --- Configuration ---
# Adjust these paths if your project structure changes
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
THEMES_DIR = os.path.join(ROOT_DIR, "assets", "themes")
CUSTOM_THEMES_FILE = os.path.join(THEMES_DIR, "custom_themes.json")
THEME_MANAGER_FILE = os.path.join(ROOT_DIR, "app_core", "theme_manager.py")


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'


def _print_header(title: str):
    print(f"\n{bcolors.HEADER}{bcolors.BOLD}===== {title.upper()} "
          f"====={bcolors.ENDC}")


def _load_json_file(filepath: str) -> Tuple[Any, List[str]]:
    """Loads a JSON file and returns its content and any errors found."""
    errors = []
    data = None
    if not os.path.exists(filepath):
        # This is not an error, the file might be optional
        return None, errors

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        err_msg = (f"Invalid JSON in '{os.path.basename(filepath)}':\n"
                   f"  {bcolors.FAIL}L{e.lineno}:C{e.colno} - {e.msg}"
                   f"{bcolors.ENDC}")
        errors.append(err_msg)
    except Exception as e:
        errors.append(f"Could not read '{os.path.basename(filepath)}': {e}")

    return data, errors


def validate_json_syntax() -> Tuple[Dict, List[str]]:
    """Checks basic JSON syntax of theme files."""
    _print_header("1. JSON Syntax Validation")

    all_themes = {}
    all_errors = []

    # Validate custom themes (if they exist)
    custom_data, errors = _load_json_file(CUSTOM_THEMES_FILE)
    all_errors.extend(errors)
    if custom_data:
        all_themes.update(custom_data)

    if not all_errors:
        print(f"{bcolors.OKGREEN}All theme files are valid JSON.{bcolors.ENDC}")

    return all_themes, all_errors


def get_required_color_keys_from_code(manager_file: str) -> set:
    """Extracts color keys from the QSS in theme_manager.py."""
    required_keys = set()
    if not os.path.exists(manager_file):
        return required_keys

    with open(manager_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # Regex to find all instances of c("some.key", ...)
    matches = re.findall(r'c\("([^"]+)"', content)
    for key in matches:
        required_keys.add(key)

    return required_keys


def validate_key_completeness(all_themes: Dict, required_keys: set) -> List[str]:
    """Checks if each theme defines all the keys required by the app."""
    _print_header("2. Color Key Completeness Validation")
    all_errors = []

    # Manually add keys for custom-painted widgets that are not discoverable
    # via the c() helper function in the main QSS.
    custom_painted_widget_keys = {
        "tree.indentationGuides.stroke", "tree.trace.color", "tree.trace.shadow",
        "tree.node.color", "tree.node.fill", "list.hoverBackground",
        "list.activeSelectionBackground", "list.activeSelectionForeground",
        "list.inactiveSelectionBackground", "list.inactiveSelectionForeground",
        "icon.foreground"
    }
    required_keys.update(custom_painted_widget_keys)

    if not required_keys:
        msg = (f"{bcolors.FAIL}Could not find required color keys "
               f"in ThemeManager. Check path.{bcolors.ENDC}")
        all_errors.append(msg)
        return all_errors

    print(f"Found {len(required_keys)} required color keys in the code.")

    for theme_id, theme_data in all_themes.items():
        theme_keys = set(theme_data.get("colors", {}).keys())
        missing_keys = required_keys - theme_keys

        if missing_keys:
            all_errors.append(
                f"Theme '{bcolors.BOLD}{theme_id}{bcolors.ENDC}' "
                f"is missing {len(missing_keys)} keys:"
            )
            for key in sorted(list(missing_keys)):
                all_errors.append(f"  - {bcolors.WARNING}{key}{bcolors.ENDC}")

    if not all_errors:
        print(f"{bcolors.OKGREEN}All themes have all required keys."
              f"{bcolors.ENDC}")

    return all_errors


def main():
    """Run all validation checks."""
    print(f"{bcolors.BOLD}Running PuffinPyEditor Asset Validator..."
          f"{bcolors.ENDC}")

    all_themes, errors = validate_json_syntax()
    if errors:
        for error in errors:
            print(f"- {error}")
        print(f"\n{bcolors.FAIL}{bcolors.BOLD}Validation failed at Step 1. "
              f"Cannot continue.{bcolors.ENDC}")
        return

    required_keys = get_required_color_keys_from_code(THEME_MANAGER_FILE)
    errors.extend(validate_key_completeness(all_themes, required_keys))

    _print_header("Validation Summary")
    if errors:
        print(f"\n{bcolors.FAIL}{bcolors.BOLD}Validation finished with "
              f"{len(errors)} issue(s). See details above.{bcolors.ENDC}")
        for error in errors:
            print(f"- {error}")
    else:
        print(f"{bcolors.OKGREEN}{bcolors.BOLD}"
              f"All assets validated successfully!{bcolors.ENDC}")


if __name__ == "__main__":
    main()
```

### File: `/utils/versioning.py`

```python
# PuffinPyEditor/utils/versioning.py
import os
from packaging import version
from .logger import log
from .helpers import get_base_path

# This will now correctly find the project root whether running from source or frozen.
ROOT_DIR = get_base_path()
VERSION_FILE_PATH = os.path.join(ROOT_DIR, "VERSION.txt")


def get_current_version() -> str:
    """
    Reads the version from the VERSION.txt file.

    Returns:
        The version string or '0.0.0' if the file is not found or invalid.
    """
    try:
        with open(VERSION_FILE_PATH, 'r', encoding='utf-8') as f:
            v_str = f.read().strip()
            # Ensure it's a valid version format before returning
            version.parse(v_str)
            return v_str
    except FileNotFoundError:
        log.error(f"VERSION.txt not found at: {VERSION_FILE_PATH}")
        return "0.0.0"
    except (version.InvalidVersion, ValueError, IOError) as e:
        log.error(f"Could not read or parse VERSION.txt: {e}")
        return "0.0.0"


def suggest_next_version() -> str:
    """
    Reads the current version and suggests the next patch version.
    e.g., "1.2.0" -> "v1.2.1", "1.3.5-alpha" -> "v1.3.5"

    Returns:
        The suggested next version string, prefixed with 'v'.
    """
    current_v_str = get_current_version()
    try:
        v = version.parse(current_v_str)
        # If it's a pre-release, suggest the final version of that number
        if v.is_prerelease:
            return f"v{v.base_version}"

        # Otherwise, increment the patch number
        major, minor, micro = v.major, v.minor, v.micro
        return f"v{major}.{minor}.{micro + 1}"

    except version.InvalidVersion:
        return "v1.0.0"


def write_new_version(new_version_string: str) -> bool:
    """
    Writes a new version string to the VERSION.txt file after validation.
    Strips any leading 'v' or whitespace.

    Args:
        new_version_string: The new version to write (e.g., "v1.2.1").

    Returns:
        True if the write was successful, False otherwise.
    """
    if not new_version_string:
        log.warning("Attempted to write an empty version string.")
        return False

    # Sanitize the version string
    clean_version = new_version_string.lstrip('v').strip()
    try:
        # Validate that it's a parseable version
        version.parse(clean_version)
        with open(VERSION_FILE_PATH, 'w', encoding='utf-8') as f:
            f.write(clean_version)
        log.info(f"Updated application version in VERSION.txt to: {clean_version}")
        # Update the global constant after a successful write
        global APP_VERSION
        APP_VERSION = clean_version
        return True
    except (version.InvalidVersion, IOError) as e:
        log.error(f"Failed to write new version '{clean_version}': {e}")
        return False


# A constant that can be easily imported elsewhere in the application
APP_VERSION = get_current_version()
```

### File: `/main.py`

```python
# PuffinPyEditor/main.py
import sys
import traceback
import os

# --- Core Imports ---
from PyQt6.QtWidgets import QApplication
from app_core.theme_manager import theme_manager
from app_core.file_handler import FileHandler
from utils.logger import log


def fallback_excepthook(exc_type, exc_value, exc_tb):
    """
    A simple fallback excepthook to log uncaught exceptions.

    This is a safety net in case the more advanced exception handler from the
    debug tools plugin fails to load. It ensures that fatal errors are
    always logged somewhere.
    """
    log.critical("--- FATAL UNHANDLED EXCEPTION ---")
    tb_text = "".join(traceback.format_exception(exc_type, exc_value, exc_tb))
    log.critical(f"Traceback:\n{tb_text}")
    print(f"FATAL ERROR:\n{tb_text}", file=sys.stderr)
    sys.__excepthook__(exc_type, exc_value, exc_tb)


def main():
    sys.excepthook = fallback_excepthook

    DEBUG_MODE = "--debug" in sys.argv

    log.info("=" * 53)
    log.info(f"PuffinPyEditor Application Starting... (Debug: {DEBUG_MODE})")
    log.info(f"Python version: {sys.version.splitlines()[0]}")
    log.info(f"Operating System: {sys.platform}")
    log.info("=" * 53)

    app = QApplication(sys.argv)
    app.setApplicationName("PuffinPyEditor")
    app.setOrganizationName("PuffinPyEditorProject")

    theme_manager.apply_theme_to_app(app)
    file_handler = FileHandler()

    from ui.main_window import MainWindow

    try:
        main_window = MainWindow(file_handler, theme_manager, debug_mode=DEBUG_MODE)
        log.info("MainWindow instance created successfully.")
    except Exception:
        log.critical("A fatal error occurred during MainWindow initialization.")
        raise

    main_window.show()
    log.info("MainWindow shown. Entering main event loop.")
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
```

### File: `/requirements.txt`

```text
flake8
findstr
GitPython
jedi
jsonschema
Markdown
pywin32
PyQt6
qtawesome
requests
winshell
```

### File: `/updater.py`

```python
# PuffinPyEditor/updater.py
import sys
import os
import time
import requests
import zipfile
import shutil

# --- Configuration ---
# A set of files and folders that the updater will NEVER overwrite, even if they
# exist in the downloaded update. This protects user-specific data.
# Paths should use forward slashes and be relative to the install directory.
PROTECTED_ITEMS = {
    "puffin_editor_settings.json",
    "logs",
    "assets/themes/custom_themes.json"
}
# --- End Configuration ---


def log(message):
    """Simple logger for the updater script."""
    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {message}")


def safe_copy(source_dir, install_dir):
    """
    Intelligently copies files from the update source to the installation
    directory, skipping any protected files or folders.
    """
    log("Starting safe copy process...")
    for root, dirs, files in os.walk(source_dir):
        # Prevent os.walk from going into protected directories
        dirs[:] = [d for d in dirs
                   if os.path.relpath(os.path.join(root, d), source_dir)
                   .replace(os.sep, '/') not in PROTECTED_ITEMS]

        # Process directories first
        for d in dirs:
            rel_path = os.path.relpath(os.path.join(root, d), source_dir)
            dest_path = os.path.join(install_dir, rel_path)
            os.makedirs(dest_path, exist_ok=True)

        # Process files
        for f in files:
            src_path = os.path.join(root, f)
            rel_path = os.path.relpath(src_path, source_dir)
            # Use forward slashes for cross-platform comparison
            if rel_path.replace(os.sep, '/') in PROTECTED_ITEMS:
                log(f"Skipping protected file: {rel_path}")
                continue
            dest_path = os.path.join(install_dir, rel_path)
            shutil.copy2(src_path, dest_path)
    log("Safe copy process finished.")


def main():
    log("PuffinPy Updater started.")

    if len(sys.argv) < 3:
        log("Error: Missing arguments. "
            "Usage: python updater.py <download_url> <install_dir>")
        return

    download_url = sys.argv[1]
    install_dir = sys.argv[2]

    log(f"Update requested for directory: {install_dir}")
    log(f"Downloading from: {download_url}")

    log("Waiting for main application to exit...")
    time.sleep(2)

    try:
        log("Downloading new version...")
        response = requests.get(download_url, stream=True)
        response.raise_for_status()

        zip_path = os.path.join(install_dir, "update.zip")
        with open(zip_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        log("Download complete.")

    except requests.exceptions.RequestException as e:
        log(f"Error: Failed to download update. {e}")
        return

    backup_dir = os.path.join(install_dir,
                              f"PuffinPyEditor_backup_{int(time.time())}")
    log(f"Creating backup at: {backup_dir}")
    try:
        # Update ignore pattern to also ignore temp update files
        ignore_patterns = shutil.ignore_patterns(
            'PuffinPyEditor_backup_*', 'update_temp', '*.zip', '*.log',
            'venv', '.git*'
        )
        shutil.copytree(install_dir, backup_dir, ignore=ignore_patterns)
    except Exception as e:
        log(f"Warning: Could not create full backup. {e}")

    temp_extract_dir = os.path.join(install_dir, "update_temp")
    try:
        log("Unzipping update...")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(temp_extract_dir)

        # Check if the zip contains a single root folder
        extracted_content = os.listdir(temp_extract_dir)
        source_dir = temp_extract_dir
        if len(extracted_content) == 1:
            possible_root = os.path.join(temp_extract_dir, extracted_content[0])
            if os.path.isdir(possible_root):
                log(f"Update is in a root folder: {extracted_content[0]}")
                source_dir = possible_root

        log(f"Replacing files in '{install_dir}' using safe copy method.")
        safe_copy(source_dir, install_dir)
        log("Update successfully installed.")

    except Exception as e:
        log(f"Error: Failed during installation. {e}")
        log("Attempting to restore from backup...")
        # (Restore logic would go here if implemented)
        return

    finally:
        log("Cleaning up temporary files...")
        if os.path.exists(zip_path):
            os.remove(zip_path)
        if os.path.exists(temp_extract_dir):
            shutil.rmtree(temp_extract_dir)

    log("Update process finished. Relaunch application to see the changes.")


if __name__ == "__main__":
    main()
```

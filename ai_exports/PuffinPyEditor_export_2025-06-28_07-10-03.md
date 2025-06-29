# Project Export: PuffinPyEditor
## Export Timestamp: 2025-06-28T07:10:03.225071
---

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
 │   ├── plugin_api.py
 │   ├── plugin_manager.py
 │   ├── project_manager.py
 │   ├── puffin_api.py
 │   ├── settings_manager.py
 │   ├── source_control_manager.py
 │   ├── theme_manager.py
 │   └── update_manager.py
 ├── main.py
 ├── plugins
 │   ├── __init__.py
 │   ├── ai_export_viewer
 │   │   ├── __init__.py
 │   │   ├── ai_export_viewer_widget.py
 │   │   ├── plugin.json
 │   │   └── plugin_main.py
 │   ├── ai_quick_actions
 │   │   ├── __init__.py
 │   │   ├── plugin.json
 │   │   └── plugin_main.py
 │   ├── ai_tools
 │   │   ├── __init__.py
 │   │   ├── ai_export_dialog.py
 │   │   ├── ai_response_dialog.py
 │   │   ├── api_client.py
 │   │   ├── plugin.json
 │   │   └── plugin_main.py
 │   ├── api_keys_manager
 │   │   ├── __init__.py
 │   │   ├── api_keys_settings_page.py
 │   │   ├── plugin.json
 │   │   └── plugin_main.py
 │   ├── find_replace
 │   │   ├── __init__.py
 │   │   ├── find_panel.py
 │   │   ├── plugin.json
 │   │   └── plugin_main.py
 │   ├── github_tools
 │   │   ├── __init__.py
 │   │   ├── github_dialog.py
 │   │   ├── new_release_dialog.py
 │   │   ├── plugin.json
 │   │   ├── plugin_main.py
 │   │   └── select_repo_dialog.py
 │   ├── global_drag_drop_handler
 │   │   ├── __init__.py
 │   │   ├── plugin.json
 │   │   └── plugin_main.py
 │   ├── linter_ui
 │   │   ├── __init__.py
 │   │   ├── plugin.json
 │   │   ├── plugin_main.py
 │   │   └── problems_panel.py
 │   ├── markdown_viewer
 │   │   ├── __init__.py
 │   │   ├── markdown_editor_widget.py
 │   │   ├── markdown_syntax_highlighter.py
 │   │   ├── markdown_widget.py
 │   │   ├── plugin.json
 │   │   └── plugin_main.py
 │   ├── plugin_publisher
 │   │   ├── __init__.py
 │   │   ├── plugin.json
 │   │   ├── plugin_main.py
 │   │   └── publish_dialog.py
 │   ├── python_runner
 │   │   ├── code_runner.py
 │   │   ├── output_panel.py
 │   │   ├── plugin.json
 │   │   └── plugin_main.py
 │   ├── source_control_ui
 │   │   ├── plugin.json
 │   │   ├── plugin_main.py
 │   │   └── project_source_control_panel.py
 │   └── tab_drag_handler
 │       ├── __init__.py
 │       ├── draggable_tab_widget.py
 │       ├── plugin.json
 │       └── plugin_main.py
 ├── requirements.txt
 ├── ui
 │   ├── __init__.py
 │   ├── editor_widget.py
 │   ├── file_tree_view.py
 │   ├── line_number_area.py
 │   ├── main_window.py
 │   ├── preferences_dialog.py
 │   ├── theme_editor_dialog.py
 │   └── widgets
 │       ├── __init__.py
 │       ├── breakpoint_area.py
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

#### Linter Issues Found:
```

- L306 (W292) No message available

```


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

#### Linter Issues Found:
```

- L34 (E501) No message available

- L86 (E501) No message available

- L136 (E501) No message available

- L219 (W292) No message available

```


```python
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
            return False, ('Name contains illegal characters '
                           '(e.g., \\ / : * ? " < > |).')

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
                self.parent_window.statusBar().showMessage(
                    "Path copied to clipboard", 2000
                )
        except Exception as e:
            log.error(f"Could not copy path to clipboard: {e}")

    def reveal_in_explorer(self, path: str):
        """Opens the system file browser to the location of the given path."""
        try:
            if sys.platform == 'win32':
                # Use /select to highlight the file/folder
                subprocess.run(['explorer', '/select,',
                                os.path.normpath(path)])
            elif sys.platform == 'darwin':  # macOS
                # Use -R to reveal the item in Finder
                subprocess.run(['open', '-R', os.path.normpath(path)])
            else:  # Linux and other UNIX-like systems
                # Open the parent directory
                dir_path = os.path.dirname(os.path.normpath(path))
                subprocess.run(['xdg-open', dir_path])
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
        if self.parent_window and hasattr(
            self.parent_window, '_update_recent_files_menu'
        ):
            self.parent_window._update_recent_files_menu()
```

### File: `/app_core/github_manager.py`

#### Linter Issues Found:
```

- L83 (E501) No message available

- L420 (W292) No message available

```


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

#### Linter Issues Found:
```

- L191 (W292) No message available

```


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

### File: `/app_core/plugin_api.py`

#### Linter Issues Found:
```

- L20 (E501) No message available

- L31 (W292) No message available

```


```python
# PuffinPyEditor/app_core/plugin_api.py
from utils.logger import log


class PluginAPI:
    """A dedicated, safe API for plugins to interact with the editor."""

    def __init__(self, main_window):
        self._main_window = main_window
        self.log = log  # Expose the logger safely

    def get_main_window(self):
        """Provides access to the main application window."""
        return self._main_window

    def add_menu_item(self, menu_name: str, item_name: str, callback):
        """Adds a new item to a specified top-level menu."""
        # In a real Qt/Tkinter app, you would find the menu and add the action.
        log.info(f"API: Adding '{item_name}' to menu '{menu_name}'.")
        # self._main_window.menuBar().findChild(QMenu, menu_name).addAction(...)

    def get_current_editor_text(self) -> str:
        """Returns the full text of the currently active editor tab."""
        # return self._main_window.tab_widget.currentWidget().toPlainText()
        log.info("API: Getting current editor text.")
        return "Example text from the current editor."

    def set_current_editor_text(self, text: str):
        """Sets the full text of the currently active editor tab."""
        # self._main_window.tab_widget.currentWidget().setPlainText(text)
        log.info("API: Setting current editor text.")
```

### File: `/app_core/plugin_manager.py`

#### Linter Issues Found:
```

- L79 (E501) No message available

- L130 (E501) No message available

- L151 (E501) No message available

- L161 (E501) No message available

- L246 (E501) No message available

- L248 (E501) No message available

- L275 (E501) No message available

- L400 (E501) No message available

- L407 (E501) No message available

- L411 (E501) No message available

- L453 (E501) No message available

- L487 (E501) No message available

- L546 (E501) No message available

- L567 (E501) No message available

- L586 (E501) No message available

- L587 (W292) No message available

```


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

# Using packaging is the standard for version comparison.
# If you don't have it, run: pip install packaging
try:
    from packaging.version import Version, InvalidVersion
except ImportError:
    # Basic fallback if 'packaging' is not installed
    log.warning(
        "The 'packaging' library is not installed. Version comparison "
        "will be basic. Run 'pip install packaging'."
    )
    Version = InvalidVersion = None

from utils.helpers import get_base_path


# This assumes your API class is in app_core.
# from app_core.puffin_api import PuffinPluginAPI

# Dummy PluginAPI for demonstration if it's not available
class PuffinPluginAPI:
    def __init__(self, main_window):
        self._main_window = main_window

    def get_main_window(self):
        return self._main_window


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
    def id(self) -> str:
        return self.manifest.get('id', 'unknown')

    @property
    def name(self) -> str:
        return self.manifest.get('name', self.id)

    @property
    def version(self) -> str:
        return self.manifest.get('version', '0.0.0')


class PluginManager:

    def __init__(self, main_window, built_in_dir: Optional[str] = None,
                 user_dir: Optional[str] = None,
                 core_tools_dir: Optional[str] = None):
        """
        Initializes the Plugin Manager.

        Note: Passing main_window is a temporary bridge. In the future, this should
        take a dedicated API object. For now, we'll create the API here.
        """
        # Local import to avoid circular dependency
        from app_core.puffin_api import PuffinPluginAPI
        self.api = PuffinPluginAPI(main_window)
        base_app_path = get_base_path()
        app_data_path = get_app_data_path()

        # Configurable plugin directories with sensible defaults
        self.built_in_plugins_dir = built_in_dir or os.path.join(
            base_app_path, "plugins")
        self.core_tools_directory = core_tools_dir or os.path.join(
            base_app_path, "core_debug_tools")
        self.user_plugins_directory = user_dir or os.path.join(
            app_data_path, "plugins")

        self.plugin_states_file = os.path.join(
            app_data_path, "plugin_states.json")

        self._ensure_paths_and_packages()

        self.plugins: Dict[str, Plugin] = {}  # Store Plugin objects by ID
        log.info("PluginManager initialized.")

    def _ensure_paths_and_packages(self):
        """Ensures all plugin directories exist and are on sys.path."""
        for path in [get_base_path(), self.user_plugins_directory]:
            if path not in sys.path:
                sys.path.insert(0, path)
                log.info(f"Added to sys.path: {path}")

        if not os.path.isdir(self.user_plugins_directory):
            log.info(
                "Creating user plugins directory: "
                f"{self.user_plugins_directory}"
            )
            os.makedirs(self.user_plugins_directory)

        # Make user plugins directory a package
        init_path = os.path.join(self.user_plugins_directory, "__init__.py")
        if not os.path.exists(init_path):
            with open(init_path, 'w', encoding='utf-8') as f:
                f.write("# This file makes the plugins directory a package.\n")

    def discover_and_load_plugins(self,
                                  ignore_list: Optional[List[str]] = None):
        """
        Discovers all plugins, resolves dependencies, and loads enabled ones.

        Args:
            ignore_list: A list of plugin IDs to skip loading (e.g., loaded manually).
        """
        log.info("Starting full plugin discovery and loading process...")
        if ignore_list is None:
            ignore_list = []

        # 1. Discover all available plugins from all sources.
        self._discover_plugins()

        # 2. Load enabled/disabled states from config
        self._load_plugin_states()

        # 3. Resolve dependencies and determine load order
        load_order = self._resolve_dependencies()

        # 4. Load plugins in the correct order
        for plugin_id in load_order:
            plugin = self.plugins.get(plugin_id)

            if plugin_id in ignore_list:
                log.info(
                    f"Skipping plugin '{plugin.name if plugin else plugin_id}' "
                    "as it's in the ignore list.")
                if plugin:
                    plugin.status_reason = "Ignored (pre-loaded)"
                continue

            if plugin and plugin.enabled:
                self.load_plugin(plugin_id)
            elif plugin:
                log.info(
                    f"Plugin '{plugin.name}' is disabled and will not be loaded."
                )

        log.info("Plugin discovery and loading complete.")

    def _discover_plugins(self):
        """Scans directories and populates the self.plugins dictionary."""
        plugin_sources = {
            "built-in": self.built_in_plugins_dir,
            "core-tool": self.core_tools_directory,
            "user": self.user_plugins_directory,
        }

        for source_type, plugin_dir in plugin_sources.items():
            if not os.path.isdir(plugin_dir):
                log.warning(
                    f"Plugin directory not found: '{plugin_dir}'. Skipping.")
                continue

            for item_name in os.listdir(plugin_dir):
                if item_name.startswith(('__', '.')):
                    continue
                plugin_path = os.path.join(plugin_dir, item_name)
                if os.path.isdir(plugin_path):
                    self._process_potential_plugin(plugin_path, source_type)

    def _process_potential_plugin(self, plugin_path: str, source_type: str):
        """Reads a plugin's manifest and adds it to the discovery list."""
        manifest_path = os.path.join(plugin_path, "plugin.json")
        if not os.path.exists(manifest_path):
            return

        try:
            with open(manifest_path, 'r', encoding='utf-8') as f:
                manifest = json.load(f)

            if not self._validate_manifest(manifest, manifest_path):
                return

            plugin_id = manifest['id']

            if plugin_id in self.plugins and source_type == "built-in":
                log.warning(
                    f"Plugin '{plugin_id}' from '{source_type}' is being "
                    "overridden by a user/core version.")
                return

            plugin = Plugin(
                manifest=manifest, path=plugin_path, source_type=source_type)
            self.plugins[plugin_id] = plugin
            log.debug(f"Discovered plugin: '{plugin.name}' (ID: {plugin_id})")

        except (json.JSONDecodeError, IOError) as e:
            log.error(
                f"Failed to read or parse manifest at '{manifest_path}': {e}")

    def _validate_manifest(self, manifest: Dict, path: str) -> bool:
        """Validates that the manifest contains required fields."""
        required_fields = ['id', 'name', 'version']
        for field_name in required_fields:
            if field_name not in manifest or not manifest[field_name]:
                log.error(
                    f"Manifest at {path} is missing required field or "
                    f"it is empty: '{field_name}'. Skipping.")
                return False
        return True

    def _resolve_dependencies(self) -> List[str]:
        """Resolves plugin dependencies and returns a valid load order."""
        log.info("Resolving plugin dependencies...")
        dependencies = {
            pid: set(p.manifest.get('dependencies', {}).keys())
            for pid, p in self.plugins.items()}
        load_order = []
        resolved = set()

        while len(load_order) < len(self.plugins):
            ready_to_load = {
                pid for pid, deps in dependencies.items()
                if pid not in resolved and not deps - resolved
            }

            if not ready_to_load:
                unresolved_deps = {
                    pid: deps - resolved
                    for pid, deps in dependencies.items() if pid not in resolved}
                log.error(
                    "Could not resolve plugin dependencies. Circular dependency"
                    " or missing plugins detected.")
                log.error(f"Unresolved dependencies: {unresolved_deps}")
                for pid in unresolved_deps:
                    if pid in self.plugins:
                        self.plugins[pid].enabled = False
                        self.plugins[pid].status_reason = (
                            f"Dependency error: {unresolved_deps[pid]}"
                        )
                break

            for plugin_id in sorted(list(ready_to_load)):
                plugin = self.plugins[plugin_id]
                deps_manifest = plugin.manifest.get('dependencies', {})

                can_load = True
                for dep_id, req_version_str in deps_manifest.items():
                    if dep_id not in self.plugins:
                        plugin.status_reason = f"Missing dependency: {dep_id}"
                        can_load = False
                        break

                    dep_plugin = self.plugins[dep_id]
                    if not self._check_version(
                            dep_plugin.version, req_version_str):
                        plugin.status_reason = (
                            f"Dependency '{dep_id}' version incompatibility. "
                            f"Have {dep_plugin.version}, need {req_version_str}"
                        )
                        can_load = False
                        break

                if can_load:
                    plugin.status_reason = "Dependencies met"
                    load_order.append(plugin_id)
                else:
                    plugin.enabled = False

                resolved.add(plugin_id)

        log.info(f"Plugin load order determined: {load_order}")
        return load_order

    def _check_version(
            self, installed_version: str, required_version_spec: str) -> bool:
        """Checks if an installed version satisfies a requirement specifier."""
        if Version is None:  # Fallback if 'packaging' is not installed
            return installed_version == required_version_spec

        try:
            installed_v = Version(installed_version)
            spec = required_version_spec.strip()

            if spec.startswith('>='):
                return installed_v >= Version(spec[2:])
            if spec.startswith('<='):
                return installed_v <= Version(spec[2:])
            if spec.startswith('=='):
                return installed_v == Version(spec[2:])
            if spec.startswith('>'):
                return installed_v > Version(spec[1:])
            if spec.startswith('<'):
                return installed_v < Version(spec[1:])
            return installed_v == Version(spec)
        except (InvalidVersion, ValueError) as e:
            log.warning(
                f"Could not parse version. installed='{installed_version}', "
                f"required='{required_version_spec}'. Error: {e}")
            return False

    def load_plugin(self, plugin_id: str) -> bool:
        """Loads a single, already discovered plugin."""
        plugin = self.plugins.get(plugin_id)
        if not plugin:
            log.error(f"Attempted to load non-existent plugin '{plugin_id}'.")
            return False
        if plugin.is_loaded:
            log.warning(f"Plugin '{plugin.name}' is already loaded.")
            return True

        entry_point = plugin.manifest.get("entry_point", "plugin_main.py")
        entry_point_path = os.path.join(plugin.path, entry_point)

        if not os.path.exists(entry_point_path):
            plugin.status_reason = f"Entry point '{entry_point}' not found."
            log.error(f"{plugin.status_reason} for plugin '{plugin.name}'.")
            return False

        entry_module_name = os.path.splitext(entry_point)[0]

        if plugin.source_type == 'user':
            package_name = plugin.id
        else:
            parent_package = os.path.basename(os.path.dirname(plugin.path))
            package_name = f"{parent_package}.{plugin.id}"

        module_name = f"{package_name}.{entry_module_name}"

        try:
            spec = importlib.util.spec_from_file_location(
                module_name, entry_point_path)
            if not spec or not spec.loader:
                raise ImportError(
                    f"Could not create module spec for {module_name}")

            module = importlib.util.module_from_spec(spec)
            sys.modules[module_name] = module
            spec.loader.exec_module(module)

            if hasattr(module, 'initialize'):
                # Smartly pass argument based on signature
                arg_to_pass = self.api
                try:
                    sig = inspect.signature(module.initialize)
                    # Check if the first parameter is NOT 'puffin_api'. This is
                    # our heuristic for identifying a legacy plugin.
                    if sig.parameters:
                        first_param_name = list(sig.parameters.keys())[0]
                        if first_param_name != 'puffin_api':
                            log.warning(
                                f"Plugin '{plugin.name}' has legacy signature "
                                f"(expects '{first_param_name}'). Passing "
                                "MainWindow directly for compatibility."
                            )
                            arg_to_pass = self.api.get_main_window()
                except (ValueError, IndexError) as e:
                    log.warning(
                        f"Could not inspect signature for plugin "
                        f"'{plugin.name}': {e}. Defaulting to passing "
                        f"modern API object.")

                instance = module.initialize(arg_to_pass)
                plugin.module = module
                plugin.instance = instance
                plugin.is_loaded = True
                plugin.status_reason = "Loaded successfully"
                log.info(
                    f"Successfully initialized plugin: '{plugin.name}' "
                    f"(Version: {plugin.version})")
                return True
            else:
                plugin.status_reason = "No 'initialize' function found."
                log.error(
                    f"Plugin '{plugin.name}' has no 'initialize' function. "
                    "Skipping.")
                if module_name in sys.modules:
                    del sys.modules[module_name]
                return False

        except Exception as e:
            plugin.status_reason = f"Load error: {e}"
            log.error(
                f"An unexpected error occurred loading plugin '{plugin.name}': "
                f"{e}", exc_info=True)
            if module_name in sys.modules:
                del sys.modules[module_name]
            return False

    def unload_plugin(self, plugin_id: str) -> bool:
        """Unloads a single plugin, calling its shutdown method if it exists."""
        plugin = self.plugins.get(plugin_id)
        if not plugin or not plugin.is_loaded:
            log.warning(
                f"Attempted to unload plugin '{plugin_id}' which is not loaded."
            )
            return True

        log.info(f"Unloading plugin: '{plugin.name}'")

        try:
            if hasattr(plugin.instance, 'shutdown'):
                plugin.instance.shutdown()

            plugin.is_loaded = False
            plugin.instance = None

            if plugin.module:
                module_name = plugin.module.__name__
                plugin.module = None
                if module_name in sys.modules:
                    del sys.modules[module_name]

                import gc
                gc.collect()

            plugin.status_reason = "Unloaded"
            log.info(f"Successfully unloaded plugin '{plugin.name}'.")
            return True
        except Exception as e:
            plugin.status_reason = f"Unload error: {e}"
            log.error(
                f"Error during shutdown of plugin '{plugin.name}': {e}",
                exc_info=True)
            return False

    def reload_plugin(self, plugin_id: str) -> bool:
        """Reloads a single plugin."""
        log.info(f"Reloading plugin '{plugin_id}'...")
        if self.unload_plugin(plugin_id):
            return self.load_plugin(plugin_id)
        log.error(
            f"Failed to unload plugin '{plugin_id}' during reload process.")
        return False

    def enable_plugin(self, plugin_id: str):
        """Enables a plugin, saves state, and loads it if dependencies are met."""
        plugin = self.plugins.get(plugin_id)
        if not plugin:
            log.error(f"Cannot enable non-existent plugin '{plugin_id}'")
            return

        plugin.enabled = True
        self._save_plugin_states()
        log.info(
            f"Plugin '{plugin.name}' enabled. Re-evaluating and loading "
            "plugins.")
        self.discover_and_load_plugins()

    def disable_plugin(self, plugin_id: str):
        """Disables a plugin, unloads it, and saves the state."""
        plugin = self.plugins.get(plugin_id)
        if not plugin:
            log.error(f"Cannot disable non-existent plugin '{plugin_id}'")
            return

        self.unload_plugin(plugin_id)
        plugin.enabled = False
        self._save_plugin_states()
        log.info(f"Plugin '{plugin.name}' disabled and unloaded.")

    def _load_plugin_states(self):
        """Loads the enabled/disabled state of plugins from a JSON file."""
        if not os.path.exists(self.plugin_states_file):
            return
        try:
            with open(self.plugin_states_file, 'r', encoding='utf-8') as f:
                states = json.load(f)
            for plugin_id, state in states.items():
                if plugin_id in self.plugins and isinstance(state, dict):
                    self.plugins[plugin_id].enabled = state.get('enabled', True)
        except (IOError, json.JSONDecodeError) as e:
            log.warning(
                "Could not load plugin states from "
                f"{self.plugin_states_file}: {e}"
            )

    def _save_plugin_states(self):
        """Saves the current enabled/disabled state of all known plugins."""
        states = {
            pid: {'enabled': p.enabled} for pid, p in self.plugins.items()
        }
        try:
            with open(self.plugin_states_file, 'w', encoding='utf-8') as f:
                json.dump(states, f, indent=4)
        except IOError as e:
            log.error(
                "Could not save plugin states to "
                f"{self.plugin_states_file}: {e}"
            )

    def get_all_plugins(self) -> List[Plugin]:
        """Returns a list of all discovered Plugin objects."""
        return list(self.plugins.values())

    def get_loaded_plugins(self) -> List[Plugin]:
        """Returns a list of currently loaded Plugin objects."""
        return [p for p in self.plugins.values() if p.is_loaded]

    def install_plugin_from_zip(self, zip_filepath: str) -> Tuple[bool, str]:
        """Installs a plugin from a zip file into the user directory."""
        if not zipfile.is_zipfile(zip_filepath):
            return False, "Not a valid zip archive."
        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                with zipfile.ZipFile(zip_filepath, 'r') as z:
                    z.extractall(temp_dir)

                items = os.listdir(temp_dir)
                is_nested = len(items) == 1 and os.path.isdir(
                    os.path.join(temp_dir, items[0]))
                src_dir = os.path.join(temp_dir,
                                       items[0]) if is_nested else temp_dir

                manifest_path = os.path.join(src_dir, 'plugin.json')
                if not os.path.exists(manifest_path):
                    return False, "Archive is missing 'plugin.json'."

                with open(manifest_path, 'r', encoding='utf-8') as f:
                    manifest = json.load(f)

                if not self._validate_manifest(manifest, manifest_path):
                    return False, "Plugin manifest is invalid."

                plugin_id = manifest['id']
                target_path = os.path.join(
                    self.user_plugins_directory, plugin_id)

                if os.path.exists(target_path):
                    return False, f"A plugin with ID '{plugin_id}' already exists."

                shutil.move(src_dir, target_path)
                plugin_name = manifest.get('name', plugin_id)
                log.info(
                    f"Plugin '{plugin_name}' installed. Reloading plugins...")

                self.discover_and_load_plugins()

                return True, f"Plugin '{plugin_name}' installed and loaded."
        except Exception as e:
            log.error(f"Failed to install plugin from {zip_filepath}: {e}",
                      exc_info=True)
            return False, f"An unexpected error occurred: {e}"

    def uninstall_plugin(self, plugin_id: str) -> Tuple[bool, str]:
        """Uninstalls a user plugin."""
        plugin = self.plugins.get(plugin_id)
        if not plugin:
            return False, f"Plugin '{plugin_id}' is not installed."
        if plugin.is_core:
            return False, "This is a built-in plugin and cannot be uninstalled."

        self.unload_plugin(plugin_id)

        target_path = os.path.join(self.user_plugins_directory, plugin_id)
        if not os.path.isdir(target_path):
            return False, f"Plugin directory for '{plugin_id}' not found."

        try:
            shutil.rmtree(target_path)

            if plugin_id in self.plugins:
                del self.plugins[plugin_id]
            self._save_plugin_states()

            log.info(f"Successfully uninstalled plugin '{plugin_id}'.")
            return True, f"Plugin '{plugin_id}' was uninstalled."
        except OSError as e:
            log.error(
                f"Failed to uninstall plugin '{plugin_id}': {e}", exc_info=True)
            return False, f"Error removing plugin directory: {e}"
```

### File: `/app_core/project_manager.py`

#### Linter Issues Found:
```

- L54 (E501) No message available

- L75 (E501) No message available

- L255 (W292) No message available

```


```python
# PuffinPyEditor/app_core/project_manager.py
import os
import datetime
import zipfile
from pathlib import Path
from typing import List, Tuple, Optional, Dict
from .settings_manager import settings_manager
from utils.logger import log


class ProjectManager:
    """Manages the state of open projects and project-wide operations."""

    def __init__(self):
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
        self.set_active_project(norm_path)
        return True

    def close_project(self, path: str):
        """Closes a project and updates the active project if necessary."""
        norm_path = os.path.normpath(path)
        if norm_path in self._open_projects:
            self._open_projects.remove(norm_path)
            log.info(f"Project closed: {norm_path}")

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
            [f"{i+1}. {g}" for i, g in enumerate(golden_rules)]
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
                    output_lines.append(f.read())
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

#### Linter Issues Found:
```

- L34 (E501) No message available

- L39 (E501) No message available

- L201 (W292) No message available

```


```python
# PuffinPyEditor/app_core/puffin_api.py
from typing import Callable, Optional
from PyQt6.QtWidgets import (QDockWidget, QTabWidget, QWidget, QMenu,
                             QMessageBox)
from PyQt6.QtGui import QAction
from PyQt6.QtCore import Qt
import qtawesome as qta
from utils.logger import log


class PuffinPluginAPI:
    """
    A stable API for plugins to interact with the MainWindow.
    This version includes proxying capabilities for backward compatibility with
    plugins that expect the main_window object directly.
    """

    def __init__(self, main_window):
        self._main_window = main_window
        self._bottom_dock_widget: Optional[QDockWidget] = None
        self._bottom_tab_widget: Optional[QTabWidget] = None
        log.info("PuffinPluginAPI initialized.")

    @property
    def puffin_api(self):
        """
        Provides backward compatibility for plugins that were written to
        expect main_window.puffin_api.
        """
        return self

    def __getattr__(self, name: str):
        """
        Proxy for attributes not found on the API, allowing access to MainWindow
        attributes for legacy plugins. This provides backward compatibility.
        """
        if hasattr(self._main_window, name):
            log.warning(
                f"Plugin is accessing 'MainWindow.{name}' directly via the API. "
                "This is a deprecated behavior. Please update the plugin to "
                "use a dedicated API method if available."
            )
            return getattr(self._main_window, name)

        raise AttributeError(
            f"'PuffinPluginAPI' object (and its wrapped 'MainWindow') has no "
            f"attribute '{name}'"
        )

    def get_main_window(self):
        """Returns the main application window instance."""
        return self._main_window

    def get_manager(self, manager_name: str) -> Optional[object]:
        """
        Gets a core application manager instance by name.
        This uses if/elif to avoid creating a large dictionary and eagerly
        evaluating all manager attributes on every call.
        """
        name = manager_name.lower()
        if name == "settings":
            return self._main_window.settings
        elif name == "theme":
            return self._main_window.theme_manager
        elif name == "project":
            return self._main_window.project_manager
        elif name == "completion":
            return self._main_window.completion_manager
        elif name == "github":
            return self._main_window.github_manager
        elif name == "git":
            return self._main_window.git_manager
        elif name == "file_handler":
            return self._main_window.file_handler
        elif name == "linter":
            return self._main_window.linter_manager
        elif name == "update":
            return self._main_window.update_manager
        elif name == "plugin":
            return self._main_window.plugin_manager

        log.warning(f"Plugin requested unknown manager: '{manager_name}'")
        return None

    def get_menu(self, menu_name: str) -> Optional[QMenu]:
        """Gets a QMenu by name from the main window."""
        return getattr(self._main_window, f"{menu_name}_menu", None)

    def add_menu_action(self, menu_name: str, text: str, callback: Callable,
                        shortcut: Optional[str] = None,
                        icon_name: Optional[str] = None) -> QAction:
        """
        Adds an action to a menu. Creates and inserts the menu in a standard
        order if it doesn't exist, enhancing modularity.
        """
        menu = self.get_menu(menu_name)
        if not menu:
            # If the menu doesn't exist, create it and insert it logically.
            log.info(f"Menu '{menu_name}' not found. Creating it dynamically.")
            menu_bar = self._main_window.menuBar()

            # Define the standard order of menus for logical placement
            standard_order = [
                "file", "edit", "view", "go", "run", "tools", "help"
            ]
            insert_before_action = None
            try:
                # Find where the new menu should go
                current_menu_index = standard_order.index(menu_name)
                # Find the next menu in the standard list that already exists
                for next_menu_name in standard_order[current_menu_index + 1:]:
                    if next_menu := self.get_menu(next_menu_name):
                        insert_before_action = next_menu.menuAction()
                        break
            except ValueError:
                # Not a standard menu, will be added at the end
                pass

            new_menu = QMenu(f"&{menu_name.capitalize()}", self._main_window)

            if insert_before_action:
                menu_bar.insertMenu(insert_before_action, new_menu)
            else:
                # Add to the end if no subsequent standard menu exists
                menu_bar.addMenu(new_menu)

            # Store the new menu on the main window instance
            setattr(self._main_window, f"{menu_name}_menu", new_menu)
            menu = new_menu
            log.info(f"Dynamically created and inserted menu '{menu_name}'.")

        icon = qta.icon(icon_name) if icon_name else None
        action = QAction(icon, text, self._main_window)
        if icon_name:
            action.setData(icon_name)
        if shortcut:
            action.setShortcut(shortcut)
        action.triggered.connect(callback)
        menu.addAction(action)
        log.info(f"Added action '{text}' to menu '{menu_name}'.")
        return action

    def add_toolbar_action(self, action: QAction):
        self._main_window.main_toolbar.addAction(action)
        log.info(f"Added action '{action.text()}' to main toolbar.")

    def register_dock_panel(self, panel_widget: QWidget, title: str,
                            area: Qt.DockWidgetArea, icon_name: str = None):
        """Registers a widget as a dock panel, grouping bottom panels."""
        if area == Qt.DockWidgetArea.BottomDockWidgetArea:
            if self._bottom_tab_widget is None:
                log.info("Creating shared bottom dock area for plugins.")
                self._bottom_dock_widget = QDockWidget("Info Panels",
                                                       self._main_window)
                self._bottom_dock_widget.setObjectName("SharedBottomDock")
                self._bottom_tab_widget = QTabWidget()
                self._bottom_tab_widget.setDocumentMode(True)
                self._bottom_dock_widget.setWidget(self._bottom_tab_widget)
                self._main_window.addDockWidget(area, self._bottom_dock_widget)
                self._main_window.view_menu.addSeparator()
                action = self._bottom_dock_widget.toggleViewAction()
                self._main_window.view_menu.addAction(action)

            icon = qta.icon(icon_name) if icon_name else None
            self._bottom_tab_widget.addTab(panel_widget, icon, title)
        else:
            dock = QDockWidget(title, self._main_window)
            dock.setWidget(panel_widget)
            self._main_window.addDockWidget(area, dock)
            self._main_window.view_menu.addSeparator()
            self._main_window.view_menu.addAction(dock.toggleViewAction())

        log.info(f"Registered panel '{title}'")

    def register_file_opener(self, extension: str, handler_func: Callable):
        if not extension.startswith('.'):
            extension = '.' + extension
        self._main_window.file_open_handlers[extension.lower()] = handler_func
        log.info(f"Registered custom opener for '{extension}' files.")

    def show_message(self, level: str, title: str, text: str):
        level_map = {
            'info': QMessageBox.Icon.Information,
            'warning': QMessageBox.Icon.Warning,
            'critical': QMessageBox.Icon.Critical
        }
        icon = level_map.get(level, QMessageBox.Icon.NoIcon)
        msg_box = QMessageBox(icon, title, text, parent=self._main_window)
        msg_box.exec()

    def show_status_message(self, text: str, timeout_ms: int = 3000):
        self._main_window.statusBar().showMessage(text, timeout_ms)

    def log_info(self, message: str):
        log.info(f"[Plugin] {message}")

    def log_warning(self, message: str):
        log.warning(f"[Plugin] {message}")

    def log_error(self, message: str):
        log.error(f"[Plugin] {message}")
```

### File: `/app_core/settings_manager.py`

#### Linter Issues Found:
```

- L150 (W292) No message available

```


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

#### Linter Issues Found:
```

- L134 (E501) No message available

- L227 (E501) No message available

- L338 (E501) No message available

- L433 (W292) No message available

```


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

#### Linter Issues Found:
```

- L124 (E501) No message available

- L448 (W292) No message available

```


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

# Correct, valid SVG path data for simple arrow/chevron icons.
SVG_ARROW_PATHS = {
    'up': "M4 10 L8 6 L12 10",
    'down': "M4 6 L8 10 L12 6"
}

# --- Paths for themes ---
APP_BASE_PATH = get_base_path()
APP_DATA_ROOT = get_app_data_path()
CUSTOM_THEMES_FILE_PATH = os.path.join(APP_DATA_ROOT, "custom_themes.json")
DEFAULT_CUSTOM_THEMES_FILE_PATH = os.path.join(
    APP_BASE_PATH, "assets", "themes", "custom_themes.json"
)

BUILT_IN_THEMES = {
    "puffin_dark": {
        "name": "Puffin Dark", "author": "PuffinPy", "type": "dark",
        "is_custom": False,
        "colors": {
            "window.background": "#2f383e",
            "sidebar.background": "#2a3338",
            "editor.background": "#272e33",
            "editor.foreground": "#d3c6aa",
            "editorGutter.background": "#2f383e",
            "editorGutter.foreground": "#5f6c6d",
            "editor.lineHighlightBackground": "#3a4145",
            "editor.matchingBracketBackground": "#545e62",
            "editor.matchingBracketForeground": "#d3c6aa",
            "menu.background": "#3a4145",
            "menu.foreground": "#d3c6aa",
            "statusbar.background": "#282f34",
            "statusbar.foreground": "#d3c6aa",
            "tab.activeBackground": "#272e33",
            "tab.inactiveBackground": "#2f383e",
            "tab.activeForeground": "#d3c6aa",
            "tab.inactiveForeground": "#5f6c6d",
            "button.background": "#424d53",
            "button.foreground": "#d3c6aa",
            "input.background": "#3a4145",
            "input.foreground": "#d3c6aa",
            "input.border": "#5f6c6d",
            "scrollbar.background": "#2f383e",
            "scrollbar.handle": "#424d53",
            "scrollbar.handleHover": "#545e62",
            "scrollbar.handlePressed": "#545e62",
            "accent": "#83c092",
            "syntax.keyword": "#e67e80",
            "syntax.operator": "#d3c6aa",
            "syntax.brace": "#d3c6aa",
            "syntax.decorator": "#dbbc7f",
            "syntax.self": "#e67e80",
            "syntax.className": "#dbbc7f",
            "syntax.functionName": "#83c092",
            "syntax.comment": "#5f6c6d",
            "syntax.string": "#a7c080",
            "syntax.docstring": "#5f6c6d",
            "syntax.number": "#d699b6"
        }
    },
    "puffin_light": {
        "name": "Puffin Light", "author": "PuffinPy", "type": "light",
        "is_custom": False,
        "colors": {
            "window.background": "#f5f5f5",
            "sidebar.background": "#ECECEC",
            "editor.background": "#ffffff",
            "editor.foreground": "#000000",
            "editorGutter.background": "#f5f5f5",
            "editorGutter.foreground": "#505050",
            "editor.lineHighlightBackground": "#e0e8f0",
            "editor.matchingBracketBackground": "#c0c8d0",
            "editor.matchingBracketForeground": "#000000",
            "menu.background": "#e0e0e0",
            "menu.foreground": "#000000",
            "statusbar.background": "#007acc",
            "statusbar.foreground": "#ffffff",
            "tab.activeBackground": "#ffffff",
            "tab.inactiveBackground": "#f5f5f5",
            "tab.activeForeground": "#000000",
            "tab.inactiveForeground": "#555555",
            "button.background": "#E0E0E0",
            "button.foreground": "#000000",
            "input.background": "#ffffff",
            "input.foreground": "#000000",
            "input.border": "#D0D0D0",
            "scrollbar.background": "#f0f0f0",
            "scrollbar.handle": "#cccccc",
            "scrollbar.handleHover": "#bbbbbb",
            "scrollbar.handlePressed": "#aaaaaa",
            "accent": "#007ACC",
            "syntax.keyword": "#0000ff",
            "syntax.operator": "#000000",
            "syntax.brace": "#a00050",
            "syntax.decorator": "#267f99",
            "syntax.self": "#800080",
            "syntax.className": "#267f99",
            "syntax.functionName": "#795e26",
            "syntax.comment": "#008000",
            "syntax.string": "#a31515",
            "syntax.docstring": "#a31515",
            "syntax.number": "#098658"
        }
    }
}


def get_arrow_svg_uri(direction: str, color: str) -> str:
    """Builds a robust, dependency-free SVG data URI for an arrow icon."""
    path_data = SVG_ARROW_PATHS.get(direction, "")
    if not path_data:
        log.warning(f"Invalid arrow direction '{direction}' requested for SVG.")
        return ""

    # Correctly generates a fill-based solid arrow icon for consistency.
    svg_content = (
        '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" '
        'viewBox="0 0 16 16">'
        f'<path fill="{color}" d="{path_data}" />'
        '</svg>'
    )
    b64_content = base64.b64encode(svg_content.encode('utf-8')).decode('utf-8')
    return f"data:image/svg+xml;base64,{b64_content}"


class ThemeManager:
    """Manages loading, applying, and customizing UI themes."""

    def __init__(self):
        self.all_themes_data: Dict[str, Dict] = {}
        self.current_theme_id: str = "puffin_dark"
        self.current_theme_data: Dict[str, Any] = {}
        self.reload_themes()
        log.info(
            f"ThemeManager initialized. Current theme: "
            f"'{self.current_theme_id}'"
        )

    def reload_themes(self):
        """Loads built-in and custom themes from disk."""
        self.all_themes_data = self._load_all_themes()
        last_theme_id = settings_manager.get("last_theme_id", "puffin_dark")

        if last_theme_id not in self.all_themes_data:
            log.warning(
                f"Last used theme '{last_theme_id}' not found. Reverting."
            )
            last_theme_id = "puffin_dark"
            settings_manager.set("last_theme_id", last_theme_id)

        self.current_theme_id = last_theme_id
        self.current_theme_data = self.all_themes_data.get(
            self.current_theme_id, {})

    def _load_all_themes(self) -> Dict[str, Dict]:
        """
        Loads themes from the built-in dictionary and the user's custom file.
        """
        all_themes = BUILT_IN_THEMES.copy()

        if not os.path.exists(CUSTOM_THEMES_FILE_PATH):
            log.info(
                f"User custom themes file not found at "
                f"{CUSTOM_THEMES_FILE_PATH}."
            )
            if os.path.exists(DEFAULT_CUSTOM_THEMES_FILE_PATH):
                try:
                    log.info("Copying default custom themes to user data dir.")
                    os.makedirs(os.path.dirname(CUSTOM_THEMES_FILE_PATH),
                                exist_ok=True)
                    shutil.copy2(DEFAULT_CUSTOM_THEMES_FILE_PATH,
                                 CUSTOM_THEMES_FILE_PATH)
                except Exception as e:
                    log.error(f"Failed to copy default custom themes: {e}")

        if os.path.exists(CUSTOM_THEMES_FILE_PATH):
            try:
                with open(CUSTOM_THEMES_FILE_PATH, 'r', encoding='utf-8') as f:
                    custom_themes_data = json.load(f)
                    for theme_data in custom_themes_data.values():
                        theme_data['is_custom'] = True
                    all_themes.update(custom_themes_data)
            except Exception as e:
                log.error(f"Error loading user custom themes: {e}")

        return all_themes

    def _save_custom_themes(self):
        """Saves only the themes marked as custom to the user-writable file."""
        custom_themes = {
            theme_id: data for theme_id, data in self.all_themes_data.items()
            if data.get("is_custom")
        }
        temp_file = CUSTOM_THEMES_FILE_PATH + ".tmp"
        try:
            os.makedirs(
                os.path.dirname(CUSTOM_THEMES_FILE_PATH), exist_ok=True)
            with open(temp_file, 'w', encoding='utf-8') as f:
                json.dump(custom_themes, f, indent=4)
            os.replace(temp_file, CUSTOM_THEMES_FILE_PATH)
            log.info("Custom themes saved successfully.")
        except IOError as e:
            log.error(f"Failed to save custom themes: {e}", exc_info=True)

    def add_or_update_custom_theme(self, theme_id: str, theme_data: Dict):
        """Adds or updates a theme, ensuring it's marked as custom."""
        theme_data['is_custom'] = True
        self.all_themes_data[theme_id] = theme_data
        self._save_custom_themes()

    def delete_custom_theme(self, theme_id: str):
        """Deletes a custom theme by its ID."""
        if (theme_id in self.all_themes_data and
                self.all_themes_data[theme_id].get("is_custom")):
            del self.all_themes_data[theme_id]
            self._save_custom_themes()

    def get_available_themes_for_ui(self) -> Dict[str, str]:
        """Returns a dict of {theme_id: theme_name} for UI display."""
        return {
            tid: d.get("name", tid) for tid, d in
            sorted(
                self.all_themes_data.items(),
                key=lambda i: i[1].get("name", i[0]).lower()
            )
        }

    def get_theme_data_by_id(self, theme_id: str) -> Optional[Dict]:
        """Gets the full data for a single theme by its ID."""
        return self.all_themes_data.get(theme_id)

    def set_theme(self, theme_id: str,
                  app_instance: Optional[QApplication] = None):
        """Sets and applies a new theme to the application."""
        if theme_id not in self.all_themes_data:
            log.warning(
                f"Attempted to set non-existent theme '{theme_id}'. Reverting."
            )
            theme_id = "puffin_dark"

        self.current_theme_id = theme_id
        self.current_theme_data = self.all_themes_data.get(theme_id, {})
        settings_manager.set("last_theme_id", theme_id)
        self.apply_theme_to_app(app_instance or QApplication.instance())
        theme_name = self.current_theme_data.get('name', 'Unknown')
        log.info(f"Theme set to '{theme_name}'")

    def apply_theme_to_app(self, app: Optional[QApplication]):
        """Generates and applies the global stylesheet."""
        if not app or not self.current_theme_data:
            return

        colors = self.current_theme_data.get("colors", {})

        def c(key: str, fallback: str) -> str:
            return colors.get(key, fallback)

        def adjust_color(hex_str: str, factor: int) -> str:
            color = QColor(hex_str)
            if factor > 100:
                return color.lighter(factor).name()
            return color.darker(factor).name()

        accent = c('accent', '#83c092')
        win_bg = c('window.background', '#2f383e')
        btn_bg = c('button.background', '#424d53')
        btn_fg = c('button.foreground', '#d3c6aa')
        input_bg = c('input.background', '#3a4145')
        input_fg = c('input.foreground', '#d3c6aa')
        input_border = c('input.border', '#5f6c6d')
        sidebar_bg = c('sidebar.background', '#2a3338')

        combo_arrow_uri = get_arrow_svg_uri('down', color=input_fg)
        spin_up_arrow_uri = get_arrow_svg_uri('up', color=input_fg)
        spin_down_arrow_uri = get_arrow_svg_uri('down', color=input_fg)

        stylesheet = f"""
            QWidget {{
                background-color: {win_bg}; color: {input_fg}; border: none;
            }}
            QMainWindow, QDialog {{ background-color: {win_bg}; }}
            QPushButton {{
                background-color: {btn_bg}; color: {btn_fg};
                border: 1px solid {input_border}; border-radius: 4px;
                padding: 6px 12px; min-width: 80px;
            }}
            QPushButton:hover {{
                background-color: {adjust_color(btn_bg, 115)};
                border-color: {accent};
            }}
            QPushButton:pressed {{
                background-color: {adjust_color(btn_bg, 95)};
            }}
            QPushButton:disabled {{
                background-color: {adjust_color(btn_bg, 105)};
                color: {c('editorGutter.foreground', '#888')};
                border-color: {adjust_color(input_border, 110)};
            }}
            QSplitter::handle {{
                background-color: {sidebar_bg}; width: 1px; image: none;
            }}
            QSplitter::handle:hover {{ background-color: {accent}; }}
            QMenuBar {{
                background-color: {adjust_color(win_bg, 105)};
                border-bottom: 1px solid {input_border};
            }}
            QMenuBar::item {{ padding: 6px 12px; }}
            QMenuBar::item:selected {{
                background-color: {accent};
                color: {c('button.foreground', '#000')};
            }}
            QMenu {{
                background-color: {c('menu.background', '#3a4145')};
                border: 1px solid {input_border}; padding: 4px;
            }}
            QMenu::item {{ padding: 6px 24px; }}
            QMenu::item:selected {{
                background-color: {accent};
                color: {c('button.foreground', '#000')};
            }}
            QTabWidget::pane {{ border: none; }}
            QTabBar::tab {{
                background: transparent;
                color: {c('tab.inactiveForeground', '#5f6c6d')};
                padding: 8px 15px; border: none;
                border-bottom: 2px solid transparent;
            }}
            QTabBar::tab:hover {{ background: {adjust_color(win_bg, 110)}; }}
            QTabBar::tab:selected {{
                color: {c('tab.activeForeground', '#d3c6aa')};
                border-bottom: 2px solid {accent};
            }}
            QToolButton {{
                background: transparent; border: none;
                border-radius: 4px; padding: 4px;
            }}
            QToolButton:hover {{
                background-color: {adjust_color(btn_bg, 120)};
            }}
            QAbstractItemView {{
                background-color: {sidebar_bg}; outline: 0;
            }}
            QTreeView, QListWidget, QTableWidget, QTreeWidget {{
                alternate-background-color: {adjust_color(sidebar_bg, 103)};
            }}
            QTreeView::item:hover, QListWidget::item:hover {{
                background-color: {adjust_color(sidebar_bg, 120)};
            }}
            QTreeView::item:selected, QListWidget::item:selected {{
                background-color: {accent};
                color: {c('button.foreground', '#000')};
            }}
            QHeaderView::section {{
                background-color: {adjust_color(sidebar_bg, 110)};
                padding: 4px; border: 1px solid {win_bg};
            }}
            QDockWidget::title {{
                background-color: {adjust_color(win_bg, 105)};
                text-align: left; padding: 5px;
                border-bottom: 1px solid {input_border};
            }}
            QGroupBox {{
                font-weight: bold;
                border: 1px solid {input_border};
                border-radius: 4px;
                margin-top: 10px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 0 5px 0 5px;
                left: 10px;
                background-color: {win_bg};
            }}
            QLineEdit, QTextEdit, QPlainTextEdit, QAbstractSpinBox,
            QComboBox {{
                background-color: {input_bg};
                border: 1px solid {input_border};
                border-radius: 4px; padding: 5px;
            }}
            QLineEdit:focus, QAbstractSpinBox:focus, QComboBox:focus,
            QTextEdit:focus, QPlainTextEdit:focus {{
                border: 1px solid {accent};
            }}
            QComboBox::drop-down {{
                subcontrol-origin: padding; subcontrol-position: top right;
                width: 20px; border-left: 1px solid {input_border};
            }}
            QComboBox::down-arrow {{
                image: url({combo_arrow_uri});
                width: 8px; height: 8px;
            }}
            QSpinBox {{ padding-right: 22px; }}
            QSpinBox::up-button, QSpinBox::down-button {{
                subcontrol-origin: border; width: 22px;
                background-color: transparent;
                border-left: 1px solid {input_border};
            }}
            QSpinBox::up-button:hover, QSpinBox::down-button:hover {{
                background-color: {adjust_color(input_bg, 120)};
            }}
            QSpinBox::up-button {{ subcontrol-position: top right; }}
            QSpinBox::down-button {{ subcontrol-position: bottom right; }}
            QSpinBox::up-arrow {{
                image: url({spin_up_arrow_uri}); width: 8px; height: 8px;
            }}
            QSpinBox::down-arrow {{
                image: url({spin_down_arrow_uri}); width: 8px; height: 8px;
            }}
            QStatusBar {{
                background-color: {c('statusbar.background', '#282f34')};
                border-top: 1px solid {input_border};
                color: {c('statusbar.foreground', '#d3c6aa')};
            }}
            QScrollBar:vertical {{ width: 10px; }}
            QScrollBar:horizontal {{ height: 10px; }}
            QScrollBar::handle {{
                background: {c('scrollbar.handle', '#424d53')};
                border-radius: 5px; min-height: 20px;
            }}
            QScrollBar::handle:hover {{
                background: {c('scrollbar.handleHover', '#545e62')};
            }}
            QScrollBar::add-line, QScrollBar::sub-line {{
                height: 0px; width: 0px;
            }}
            QScrollBar::add-page, QScrollBar::sub-page {{ background: none; }}
        """
        try:
            app.setStyleSheet(stylesheet)
        except Exception as e:
            log.error(f"Failed to apply stylesheet: {e}", exc_info=True)


# Singleton instance
theme_manager = ThemeManager()
```

### File: `/app_core/update_manager.py`

#### Linter Issues Found:
```

- L51 (E501) No message available

- L75 (E501) No message available

- L96 (E501) No message available

- L108 (W292) No message available

```


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

### File: `/plugins/ai_export_viewer/__init__.py`

```python

```

### File: `/plugins/ai_export_viewer/ai_export_viewer_widget.py`

#### Linter Issues Found:
```

- L131 (E127) No message available

- L147 (E501) No message available

- L169 (F841) No message available

- L214 (W292) No message available

```


```python
# PuffinPyEditor/plugins/ai_export_viewer/ai_export_viewer_widget.py
import os
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QListWidget, QListWidgetItem,
    QTextEdit, QPushButton, QMessageBox, QSplitter, QFrame
)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt
from markdown import markdown
import qtawesome as qta
from utils.helpers import get_base_path
from utils.logger import log
from app_core.theme_manager import theme_manager
from app_core.settings_manager import settings_manager


class AIExportViewerWidget(QWidget):
    """
    A widget that displays a list of past AI exports and their content,
    designed to be embedded in a tab.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.export_dir = os.path.join(get_base_path(), "ai_exports")
        self._ensure_export_dir_exists()

        self.setObjectName("AIExportViewerWidget")
        self._setup_ui()
        self._connect_signals()
        self.update_theme()
        self.refresh_list()

    def _setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Toolbar
        toolbar = QFrame()
        toolbar.setObjectName("ExportViewerToolbar")
        toolbar_layout = QHBoxLayout(toolbar)
        toolbar_layout.setContentsMargins(5, 5, 5, 5)

        self.refresh_button = QPushButton(qta.icon('fa5s.sync-alt'), "Refresh")
        self.delete_button = QPushButton(qta.icon('fa5s.trash-alt'), "Delete")
        toolbar_layout.addWidget(self.refresh_button)
        toolbar_layout.addWidget(self.delete_button)
        toolbar_layout.addStretch()
        main_layout.addWidget(toolbar)

        # Main content area
        splitter = QSplitter(Qt.Orientation.Horizontal)
        main_layout.addWidget(splitter)

        # Left pane for the list of exports
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)
        self.export_list_widget = QListWidget()
        self.export_list_widget.setAlternatingRowColors(True)
        left_layout.addWidget(self.export_list_widget)
        splitter.addWidget(left_widget)

        # Right pane for viewing the content of an export
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)
        self.content_view = QTextEdit()
        self.content_view.setReadOnly(True)
        right_layout.addWidget(self.content_view)
        splitter.addWidget(right_widget)

        splitter.setSizes([250, 550])

    def _connect_signals(self):
        self.export_list_widget.currentItemChanged.connect(
            self._on_export_selected
        )
        self.refresh_button.clicked.connect(self.refresh_list)
        self.delete_button.clicked.connect(self._delete_selected_export)

    def _ensure_export_dir_exists(self):
        try:
            os.makedirs(self.export_dir, exist_ok=True)
        except OSError as e:
            log.error(f"Could not create export directory: {e}", exc_info=True)

    def refresh_list(self):
        self.export_list_widget.clear()
        self.content_view.clear()
        self.delete_button.setEnabled(False)
        try:
            files = [
                f for f in os.listdir(self.export_dir)
                if f.endswith('.md') and
                os.path.isfile(os.path.join(self.export_dir, f))
            ]
            files.sort(reverse=True)  # Show newest first

            if not files:
                self.export_list_widget.addItem("No exports found.")
                self.export_list_widget.setEnabled(False)
                return

            self.export_list_widget.setEnabled(True)
            for filename in files:
                path = os.path.join(self.export_dir, filename)
                item = QListWidgetItem(filename)
                item.setData(Qt.ItemDataRole.UserRole, path)
                self.export_list_widget.addItem(item)
            if self.export_list_widget.count() > 0:
                self.export_list_widget.setCurrentRow(0)

        except OSError as e:
            log.error(f"Error reading export directory {self.export_dir}: {e}")
            self.export_list_widget.addItem("Error reading directory.")
            self.export_list_widget.setEnabled(False)

    def _on_export_selected(self, current: QListWidgetItem, _):
        if not current or not current.data(Qt.ItemDataRole.UserRole):
            self.content_view.clear()
            self.delete_button.setEnabled(False)
            return

        self.delete_button.setEnabled(True)
        filepath = current.data(Qt.ItemDataRole.UserRole)
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            html = markdown(content, extensions=['fenced_code', 'tables',
                                                  'extra', 'sane_lists'])
            self.content_view.setHtml(html)
        except Exception as e:
            error_message = f"Error reading file:\n{filepath}\n\n{str(e)}"
            self.content_view.setText(error_message)
            log.error(f"Failed to read export file {filepath}: {e}")

    def _delete_selected_export(self):
        current_item = self.export_list_widget.currentItem()
        if not current_item:
            return

        filepath = current_item.data(Qt.ItemDataRole.UserRole)
        filename = os.path.basename(filepath)
        reply = QMessageBox.question(
            self, "Confirm Deletion",
            f"Are you sure you want to permanently delete this export?\n\n{filename}",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            try:
                os.remove(filepath)
                log.info(f"Deleted AI export file: {filepath}")
                self.refresh_list()
            except OSError as e:
                log.error(f"Failed to delete file {filepath}: {e}")
                QMessageBox.critical(
                    self, "Deletion Failed", f"Could not delete file:\n{e}"
                )

    def update_theme(self):
        """Applies colors and fonts from the current theme."""
        colors = theme_manager.current_theme_data.get('colors', {})
        font_family = settings_manager.get("font_family", "Consolas")
        font_size = settings_manager.get("font_size", 11)

        bg_color = colors.get('editor.background', '#2b2b2b')
        fg_color = colors.get('editor.foreground', '#a9b7c6')
        accent = colors.get('accent', '#88c0d0')
        line_bg = colors.get('editor.lineHighlightBackground', '#323232')
        comment = colors.get('syntax.comment', '#808080')
        string = colors.get('syntax.string', '#6A8759')
        toolbar_bg = colors.get('sidebar.background', '#3c3f41')
        border = colors.get('input.border', '#555')

        self.setStyleSheet(f"""
            AIExportViewerWidget {{ background-color: {bg_color}; }}
            #ExportViewerToolbar {{
                background-color: {toolbar_bg};
                border-bottom: 1px solid {border};
            }}
            QListWidget {{ background-color: {bg_color}; border: none; }}
        """)

        md_style = f"""
            h1,h2,h3,h4,h5,h6 {{
                color:{accent}; border-bottom:1px solid {line_bg};
                padding-bottom:4px; margin-top:15px;
            }}
            a {{ color:{string}; text-decoration:none; }}
            a:hover {{ text-decoration:underline; }}
            p,li {{ font-size:{font_size}pt; }}
            pre,code {{
                background-color:{line_bg}; border:1px solid {border};
                border-radius:4px; padding:10px; font-family:"{font_family}";
            }}
            code {{ padding:2px 4px; border:none; }}
            blockquote {{
                color:{comment}; border-left:3px solid {accent};
                padding-left:10px; margin-left:5px;
            }}
            table{{border-collapse:collapse;}}
            th,td{{border:1px solid {border}; padding:6px;}}
            th{{background-color:{line_bg};}}
        """
        self.content_view.document().setDefaultStyleSheet(md_style)
        font = QFont(settings_manager.get("font_family", "Arial"), font_size)
        self.content_view.document().setDefaultFont(font)
        self.content_view.setStyleSheet(
            f"background-color: {bg_color}; border:none; padding:10px;")

        if item := self.export_list_widget.currentItem():
            self._on_export_selected(item, None)
```

### File: `/plugins/ai_export_viewer/plugin.json`

```json
{
    "id": "ai_export_viewer",
    "name": "AI Export Viewer",
    "author": "PuffinPy Team",
    "version": "1.1.0",
    "description": "Provides a tab-based viewer to manage and review past AI project exports.",
    "entry_point": "plugin_main.py"
}
```

### File: `/plugins/ai_export_viewer/plugin_main.py`

#### Linter Issues Found:
```

- L44 (E501) No message available

- L72 (W292) No message available

```


```python
# PuffinPyEditor/plugins/ai_export_viewer/plugin_main.py
import qtawesome as qta
from .ai_export_viewer_widget import AIExportViewerWidget
from utils.logger import log


class AIExportViewerPlugin:
    """
    Manages the lifecycle and functionality of the AI Export Viewer.
    Opens the viewer in a persistent tab instead of a modal dialog.
    """
    VIEWER_TAB_NAME = "AI Exports"

    def __init__(self, main_window):
        self.api = main_window.puffin_api
        self.main_window = self.api.get_main_window()
        self.api.add_menu_action(
            menu_name="tools",
            text="View AI Exports...",
            callback=self.open_export_viewer_tab,
            icon_name="fa5s.history"
        )

    def open_export_viewer_tab(self):
        """
        Opens the AI Export Viewer in a new tab, or focuses it if already open.
        """
        log.info("AI Export Viewer: Handling request to open viewer tab.")

        # Check if the viewer tab is already open
        for i in range(self.main_window.tab_widget.count()):
            tab_text = self.main_window.tab_widget.tabText(i)
            if tab_text == self.VIEWER_TAB_NAME:
                self.main_window.tab_widget.setCurrentIndex(i)
                widget = self.main_window.tab_widget.widget(i)
                if isinstance(widget, AIExportViewerWidget):
                    widget.refresh_list()
                return

        # If a placeholder "Welcome" tab exists, remove it
        if self.main_window.tab_widget.count() == 1:
            current_widget = self.main_window.tab_widget.widget(0)
            is_placeholder = (hasattr(current_widget, 'objectName') and
                              current_widget.objectName() == "PlaceholderLabel")
            if is_placeholder:
                self.main_window.tab_widget.removeTab(0)

        # Create the viewer widget and add it to a new tab
        viewer_widget = AIExportViewerWidget(self.main_window)
        icon = qta.icon("fa5s.history", color='grey')
        index = self.main_window.tab_widget.addTab(
            viewer_widget, icon, self.VIEWER_TAB_NAME
        )
        self.main_window.tab_widget.setTabToolTip(
            index, "Browse and manage AI exports")
        self.main_window.tab_widget.setCurrentIndex(index)
        self.main_window.tab_widget.setTabsClosable(True)


def initialize(main_window):
    """
    Entry point function for PuffinPyEditor to load the plugin.
    """
    try:
        plugin_instance = AIExportViewerPlugin(main_window)
        log.info("AI Export Viewer Plugin initialized successfully.")
        return plugin_instance
    except Exception as e:
        log.error(
            f"Failed to initialize AI Export Viewer Plugin: {e}", exc_info=True
        )
        return None
```

### File: `/plugins/ai_quick_actions/__init__.py`

```python

```

### File: `/plugins/ai_quick_actions/plugin.json`

```json
{
    "id": "ai_quick_actions",
    "name": "AI Quick Actions",
    "author": "PuffinPy Team",
    "version": "1.0.0",
    "description": "Adds AI-powered actions like 'Explain' and 'Refactor' to the editor's context menu.",
    "entry_point": "plugin_main.py"
}
```

### File: `/plugins/ai_quick_actions/plugin_main.py`

#### Linter Issues Found:
```

- L44 (E501) No message available

- L55 (E501) No message available

- L65 (E501) No message available

- L141 (W292) No message available

```


```python
# PuffinPyEditor/plugins/ai_quick_actions/plugin_main.py
from functools import partial
from PyQt6.QtWidgets import QMessageBox
from PyQt6.QtCore import QObject, QRunnable, QThreadPool, pyqtSignal

from plugins.ai_tools.api_client import ApiClient
from plugins.ai_tools.ai_response_dialog import AIResponseDialog


class AIWorker(QRunnable):
    """A runnable worker to execute AI API calls in a separate thread."""
    class Signals(QObject):
        finished = pyqtSignal(bool, str)

    def __init__(self, api_client, provider, model, system_prompt,
                 user_prompt):
        super().__init__()
        self.api_client = api_client
        self.provider = provider
        self.model = model
        self.system_prompt = system_prompt
        self.user_prompt = user_prompt
        self.signals = self.Signals()

    def run(self):
        """Execute the request and emit the result."""
        success, response = self.api_client.send_request(
            self.provider, self.model, self.system_prompt, self.user_prompt
        )
        self.signals.finished.emit(success, response)


class AIQuickActionsPlugin:
    """Adds AI-powered actions to a new 'AI' top-level menu."""
    ACTIONS = [
        {
            "name": "Explain this code",
            "icon": "fa5s.question-circle",
            "system": (
                "You are an expert developer. Explain the following code "
                "snippet clearly and concisely. Describe its purpose, "
                "inputs, and outputs."
            ),
            "user": "Please explain this code:\n\n```python\n{selected_code}\n```"
        },
        {
            "name": "Suggest a refactoring",
            "icon": "fa5s.magic",
            "system": (
                "You are a senior developer focused on writing clean, "
                "efficient, and maintainable Python code. Refactor the "
                "following code snippet, explaining the key improvements "
                "you made."
            ),
            "user": "Please refactor this code:\n\n```python\n{selected_code}\n```"
        },
        {
            "name": "Find potential bugs",
            "icon": "fa5s.bug",
            "system": (
                "You are a quality assurance expert. Analyze the following "
                "code for potential bugs, logical errors, or edge cases "
                "that might not be handled correctly."
            ),
            "user": "Please find potential bugs in this code:\n\n```python\n{selected_code}\n```"
        }
    ]

    def __init__(self, main_window):
        self.api = main_window.puffin_api
        self.settings_manager = self.api.get_manager("settings")
        self.main_window = self.api.get_main_window()

        self.api_client = ApiClient(self.settings_manager)
        self.thread_pool = QThreadPool()

        for action_config in self.ACTIONS:
            callback = partial(self._run_action, action_config)
            self.api.add_menu_action(
                menu_name="ai",
                text=action_config["name"],
                callback=callback,
                icon_name=action_config["icon"]
            )

    def _run_action(self, config):
        """Callback executed when a menu action is clicked."""
        # Access the current editor widget via the central 'tabs' attribute
        # which is a standard name for a QTabWidget in the main window.
        current_editor = self.main_window.tabs.currentWidget()

        if not current_editor:
            self.api.show_message(
                "info", "No File Open", "Please open a file to use AI actions."
            )
            return

        selected_text = current_editor.textCursor().selectedText()
        if not selected_text:
            self.api.show_message(
                "info", "No Text Selected",
                "Please select some code to use this AI action."
            )
            return

        provider = "OpenAI"
        api_key = self.api_client.get_api_key(provider)
        if not api_key:
            QMessageBox.warning(
                self.api.get_main_window(),
                "API Key Missing",
                f"API Key for {provider} not found. Please go to "
                "Tools -> Manage API Keys... to add it."
            )
            return

        model = self.api_client.PROVIDER_CONFIG.get(
            provider, {}).get("models", [])[0]
        system_prompt = config["system"]
        user_prompt = config["user"].format(selected_code=selected_text)

        self.api.show_status_message(f"Sending selection to {model}...", 3000)

        worker = AIWorker(
            self.api_client, provider, model, system_prompt, user_prompt)
        worker.signals.finished.connect(self._on_action_finished)
        self.thread_pool.start(worker)

    def _on_action_finished(self, success, response):
        """Handles the response from the AI worker thread."""
        self.api.show_status_message("AI response received.", 2000)
        if success:
            dialog = AIResponseDialog(response, self.api.get_main_window())
            dialog.exec()
        else:
            QMessageBox.critical(
                self.api.get_main_window(), "API Error", response)


def initialize(main_window):
    return AIQuickActionsPlugin(main_window)
```

### File: `/plugins/ai_tools/__init__.py`

```python

```

### File: `/plugins/ai_tools/ai_export_dialog.py`

#### Linter Issues Found:
```

- L42 (E501) No message available

- L74 (E501) No message available

- L394 (E501) No message available

- L517 (E501) No message available

- L558 (E501) No message available

- L572 (E501) No message available

- L601 (E501) No message available

- L865 (E501) No message available

- L873 (E501) No message available

- L877 (E501) No message available

- L882 (E501) No message available

- L894 (W292) No message available

```


```python
# PuffinPyEditor/plugins/ai_tools/ai_export_dialog.py
import os
import json
from typing import List, Dict, Optional
from datetime import datetime
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QSplitter, QWidget, QGroupBox,
    QTreeView, QTextEdit, QListWidget, QListWidgetItem, QPushButton,
    QDialogButtonBox, QMessageBox, QInputDialog, QComboBox, QProgressDialog,
    QApplication, QCheckBox, QLabel, QToolButton
)
from PyQt6.QtGui import QStandardItemModel, QStandardItem, QCursor
from PyQt6.QtCore import Qt, QCoreApplication
import qtawesome as qta

from app_core.settings_manager import settings_manager
from app_core.project_manager import ProjectManager
from app_core.linter_manager import LinterManager
from utils.logger import log
from utils.helpers import get_base_path
from .api_client import ApiClient
from .ai_response_dialog import AIResponseDialog

PROMPT_TYPE_DEFAULT = "default"
PROMPT_TYPE_GENERATIVE = "generative"
PROMPT_TYPE_COMMUNITY = "community"
PROMPT_TYPE_USER = "user"

DEFAULT_LOADOUTS = {
    "Code Review": {
        "instructions": (
            "You are a senior Python developer performing a code review. "
            "Analyze the provided code for issues related to correctness, "
            "style, performance, and maintainability. Provide constructive "
            "feedback and concrete examples for improvement."
        ),
        "guidelines": [
            "Check for compliance with PEP 8 style guidelines.",
            "Identify potential bugs or logical errors.",
            "Suggest more efficient or 'Pythonic' ways to write the code.",
            "Comment on code clarity, variable naming, and documentation.",
            "Do not suggest new features; focus on improving the existing code.",
            "Structure your feedback by file, then by line number where "
            "applicable."
        ]
    },
    "Documentation Generation": {
        "instructions": (
            "You are a technical writer. Your task is to generate clear and "
            "comprehensive documentation for the provided Python code. Create "
            "docstrings for all public classes, methods, and functions that "
            "are missing them. Follow the Google Python Style Guide for "
            "docstrings."
        ),
        "guidelines": [
            "For each function/method, include an 'Args:' section for "
            "parameters and a 'Returns:' section for the return value.",
            "The main description of the function should be a concise, "
            "one-sentence summary.",
            "If a function raises exceptions, include a 'Raises:' section.",
            "Ensure the generated documentation is professional and ready to "
            "be used in the project."
        ]
    }
}


class AIExportDialog(QDialog):
    """
    A dialog for configuring and exporting a project's context for an AI
    model.
    """
    def __init__(self, project_path: str, project_manager: ProjectManager,
                 linter_manager: LinterManager, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.project_path = project_path
        self.project_manager = project_manager
        self.linter_manager = linter_manager
        self.api_client = ApiClient(settings_manager)
        self.loadouts: Dict[str, Dict] = {}
        self.golden_rule_sets: Dict[str, List[str]] = {}
        self.prompt_sources: Dict[str, Dict] = {}
        self.selected_files: List[str] = []
        self._is_updating_checks = False

        self.setWindowTitle("Export Project for AI")
        self.setMinimumSize(950, 700)
        self.setObjectName("AIExportDialog")

        self._setup_ui()
        self._connect_signals()
        self._populate_file_tree()
        self._load_and_populate_prompts()
        self._load_and_populate_golden_rule_sets()
        self._update_toggle_button_state()

    def _setup_ui(self):
        self.main_layout = QVBoxLayout(self)
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        self.main_layout.addWidget(self.splitter)
        self._create_left_pane()
        self._create_right_pane()
        self.splitter.setSizes([350, 600])

        bottom_layout = QHBoxLayout()

        # --- Combined API and Context Options Group ---
        api_context_group = QGroupBox("Execution & Context")
        api_context_layout = QVBoxLayout(api_context_group)
        api_mode_layout = QHBoxLayout()
        self.api_mode_checkbox = QCheckBox("Enable API Mode")
        self.api_mode_checkbox.setToolTip(
            "Send context directly to an AI API instead of exporting a file.")
        api_mode_layout.addWidget(self.api_mode_checkbox)
        self.api_provider_combo = QComboBox()
        self.api_provider_combo.addItems(
            self.api_client.PROVIDER_CONFIG.keys()
        )
        api_mode_layout.addWidget(QLabel("Provider:"))
        api_mode_layout.addWidget(self.api_provider_combo)
        self.api_model_combo = QComboBox()
        api_mode_layout.addWidget(QLabel("Model:"))
        api_mode_layout.addWidget(self.api_model_combo)
        api_context_layout.addLayout(api_mode_layout)

        context_options_layout = QHBoxLayout()
        self.include_linter_checkbox = QCheckBox("Include linter issues")
        self.include_linter_checkbox.setChecked(True)
        self.include_linter_checkbox.setToolTip(
            "Include linter analysis in the context.")
        context_options_layout.addWidget(self.include_linter_checkbox)
        context_options_layout.addStretch()
        api_context_layout.addLayout(context_options_layout)
        bottom_layout.addWidget(api_context_group, 1)

        # --- File Export Options (only visible when not in API mode) ---
        self.export_options_group = QGroupBox("File Export Options")
        export_options_layout = QHBoxLayout(self.export_options_group)
        export_options_layout.addWidget(QLabel("Format:"))
        self.format_combo = QComboBox()
        self.format_combo.addItems(["AI-Optimized", "Standard Markdown"])
        self.format_combo.setToolTip(
            "Choose export format. 'AI-Optimized' is cleaner for models."
        )
        export_options_layout.addWidget(self.format_combo)
        bottom_layout.addWidget(self.export_options_group, 1)

        self.main_layout.addLayout(bottom_layout)

        self.button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Cancel |
            QDialogButtonBox.StandardButton.Ok)
        self.ok_button = self.button_box.button(
            QDialogButtonBox.StandardButton.Ok)
        self.ok_button.setText("Export")
        self.main_layout.addWidget(self.button_box)
        self._toggle_api_mode(self.api_mode_checkbox.isChecked())

    def _create_left_pane(self):
        left_pane = QWidget()
        left_layout = QVBoxLayout(left_pane)
        self.splitter.addWidget(left_pane)
        loadouts_group = QGroupBox("Prompt Loadouts")
        loadouts_layout = QVBoxLayout(loadouts_group)
        self.loadout_combo = QComboBox()
        loadouts_layout.addWidget(self.loadout_combo)
        loadout_buttons_layout = QHBoxLayout()
        self.save_loadout_button = QPushButton("Save")
        self.delete_loadout_button = QPushButton("Delete")
        loadout_buttons_layout.addStretch()
        loadout_buttons_layout.addWidget(self.save_loadout_button)
        loadout_buttons_layout.addWidget(self.delete_loadout_button)
        loadouts_layout.addLayout(loadout_buttons_layout)
        left_layout.addWidget(loadouts_group)

        files_group = QGroupBox("Select Files to Include")
        files_layout = QVBoxLayout(files_group)
        file_actions_layout = QHBoxLayout()
        self.expand_all_button = QToolButton()
        self.expand_all_button.setIcon(
            qta.icon('fa5s.angle-double-down', color='grey'))
        self.expand_all_button.setToolTip("Expand all folders in the tree.")

        self.collapse_all_button = QToolButton()
        self.collapse_all_button.setIcon(
            qta.icon('fa5s.angle-double-up', color='grey'))
        self.collapse_all_button.setToolTip(
            "Collapse all folders in the tree.")

        self.toggle_select_button = QToolButton()
        self.toggle_select_button.setAutoRaise(True)

        for button in [self.expand_all_button, self.collapse_all_button]:
            button.setAutoRaise(True)

        file_actions_layout.addWidget(self.expand_all_button)
        file_actions_layout.addWidget(self.collapse_all_button)
        file_actions_layout.addStretch()
        file_actions_layout.addWidget(self.toggle_select_button)
        files_layout.addLayout(file_actions_layout)

        self.file_tree = QTreeView()
        self.file_tree.setHeaderHidden(True)
        self.file_model = QStandardItemModel()
        self.file_tree.setModel(self.file_model)
        files_layout.addWidget(self.file_tree)
        left_layout.addWidget(files_group, 1)

    def _create_right_pane(self):
        right_pane = QWidget()
        right_layout = QVBoxLayout(right_pane)
        self.splitter.addWidget(right_pane)
        instructions_group = QGroupBox("Instructions for the AI")
        instructions_layout = QVBoxLayout(instructions_group)
        self.instructions_edit = QTextEdit()
        self.instructions_edit.setPlaceholderText(
            "e.g., Act as a senior developer...")
        instructions_layout.addWidget(self.instructions_edit)
        right_layout.addWidget(instructions_group, 1)
        guidelines_group = QGroupBox("Specific Guidelines & Rules")
        guidelines_layout = QVBoxLayout(guidelines_group)
        self.guidelines_list = QListWidget()
        self.guidelines_list.setAlternatingRowColors(True)
        guidelines_layout.addWidget(self.guidelines_list, 1)
        guideline_buttons_layout = QHBoxLayout()
        self.add_guideline_button = QPushButton("Add")
        self.edit_guideline_button = QPushButton("Edit")
        self.remove_guideline_button = QPushButton("Remove")
        guideline_buttons_layout.addStretch()
        guideline_buttons_layout.addWidget(self.add_guideline_button)
        guideline_buttons_layout.addWidget(self.edit_guideline_button)
        guideline_buttons_layout.addWidget(self.remove_guideline_button)
        guidelines_layout.addLayout(guideline_buttons_layout)
        right_layout.addWidget(guidelines_group, 1)
        golden_rules_group = QGroupBox("Golden Rules")
        golden_rules_layout = QVBoxLayout(golden_rules_group)
        golden_rules_top_layout = QHBoxLayout()
        self.golden_rules_combo = QComboBox()
        self.save_golden_rules_button = QPushButton("Save As New...")
        self.delete_golden_rules_button = QPushButton("Delete")
        golden_rules_top_layout.addWidget(self.golden_rules_combo, 1)
        golden_rules_top_layout.addWidget(self.save_golden_rules_button)
        golden_rules_top_layout.addWidget(self.delete_golden_rules_button)
        golden_rules_layout.addLayout(golden_rules_top_layout)
        self.golden_rules_list = QListWidget()
        self.golden_rules_list.setAlternatingRowColors(True)
        golden_rules_layout.addWidget(self.golden_rules_list, 1)
        golden_rules_buttons_layout = QHBoxLayout()
        self.add_golden_rule_button = QPushButton("Add")
        self.edit_golden_rule_button = QPushButton("Edit")
        self.remove_golden_rule_button = QPushButton("Remove")
        golden_rules_buttons_layout.addStretch()
        golden_rules_buttons_layout.addWidget(self.add_golden_rule_button)
        golden_rules_buttons_layout.addWidget(self.edit_golden_rule_button)
        golden_rules_buttons_layout.addWidget(self.remove_golden_rule_button)
        golden_rules_layout.addLayout(golden_rules_buttons_layout)
        right_layout.addWidget(golden_rules_group, 1)

    def _connect_signals(self):
        self.button_box.accepted.connect(self._start_export)
        self.button_box.rejected.connect(self.reject)
        self.file_model.itemChanged.connect(self._on_item_changed)
        self.expand_all_button.clicked.connect(self.file_tree.expandAll)
        self.collapse_all_button.clicked.connect(self.file_tree.collapseAll)
        self.toggle_select_button.clicked.connect(
            self._on_toggle_select_clicked)
        self.loadout_combo.currentIndexChanged.connect(
            self._on_loadout_selected)
        self.save_loadout_button.clicked.connect(self._save_loadout)
        self.delete_loadout_button.clicked.connect(self._delete_loadout)
        self.add_guideline_button.clicked.connect(self._add_guideline)
        self.edit_guideline_button.clicked.connect(self._edit_guideline)
        self.remove_guideline_button.clicked.connect(self._remove_guideline)
        self.golden_rules_combo.currentIndexChanged.connect(
            self._on_golden_rule_set_selected)
        self.save_golden_rules_button.clicked.connect(
            self._save_golden_rule_set)
        self.delete_golden_rules_button.clicked.connect(
            self._delete_golden_rule_set)
        self.add_golden_rule_button.clicked.connect(self._add_golden_rule)
        self.edit_golden_rule_button.clicked.connect(self._edit_golden_rule)
        self.remove_golden_rule_button.clicked.connect(
            self._remove_golden_rule)
        self.api_mode_checkbox.toggled.connect(self._toggle_api_mode)
        self.api_provider_combo.currentIndexChanged.connect(
            self._on_api_provider_changed)

    def _toggle_api_mode(self, checked):
        is_api_mode = checked
        for w in [self.api_provider_combo, self.api_model_combo]:
            w.setVisible(is_api_mode)

        self.export_options_group.setVisible(not is_api_mode)
        self.ok_button.setText("Send to AI" if is_api_mode else "Export")

        if is_api_mode:
            self._on_api_provider_changed()

    def _on_api_provider_changed(self):
        provider = self.api_provider_combo.currentText()
        config = self.api_client.PROVIDER_CONFIG.get(provider, {})
        models = config.get("models", [])
        self.api_model_combo.clear()
        self.api_model_combo.addItems(models)

    def _set_all_check_states(self, state: Qt.CheckState):
        self._is_updating_checks = True
        try:
            root = self.file_model.invisibleRootItem()
            for row in range(root.rowCount()):
                self._recursive_set_check_state(root.child(row), state)
        finally:
            self._is_updating_checks = False
        self._update_toggle_button_state()

    def _recursive_set_check_state(
        self, item: QStandardItem, state: Qt.CheckState
    ):
        if item.isCheckable():
            item.setCheckState(state)
        for row in range(item.rowCount()):
            if child_item := item.child(row):
                self._recursive_set_check_state(child_item, state)

    def _on_toggle_select_clicked(self):
        if self._are_all_items_checked():
            self._set_all_check_states(Qt.CheckState.Unchecked)
        else:
            self._set_all_check_states(Qt.CheckState.Checked)

    def _update_toggle_button_state(self):
        if self._are_all_items_checked():
            self.toggle_select_button.setIcon(
                qta.icon('fa5s.check-square', color='grey'))
            self.toggle_select_button.setToolTip("Deselect all files.")
        else:
            self.toggle_select_button.setIcon(
                qta.icon('fa5.square', color='grey'))
            self.toggle_select_button.setToolTip("Select all files.")

    def _get_all_checkable_items(self) -> List[QStandardItem]:
        items = []
        root = self.file_model.invisibleRootItem()

        def recurse(parent_item):
            for row in range(parent_item.rowCount()):
                child = parent_item.child(row)
                if child:
                    if child.isCheckable():
                        items.append(child)
                    if child.hasChildren():
                        recurse(child)
        recurse(root)
        return items

    def _are_all_items_checked(self) -> bool:
        items = self._get_all_checkable_items()
        return bool(items) and all(
            item.checkState() == Qt.CheckState.Checked for item in items)

    def _populate_file_tree(self):
        self.file_model.clear()
        root_node = self.file_model.invisibleRootItem()
        path_map = {self.project_path: root_node}
        ignore_dirs = {
            '__pycache__', '.git', 'venv', '.venv', 'dist', 'build', 'logs',
            'ai_exports'
        }
        ignore_files = {'puffin_editor_settings.json'}
        include_extensions = [
            '.py', '.md', '.txt', '.json', '.html', '.css', '.js', '.yml',
            '.bat'
        ]
        for dirpath, dirnames, filenames in os.walk(
            self.project_path, topdown=True
        ):
            dirnames[:] = [d for d in dirnames if d not in ignore_dirs]
            parent_node = path_map.get(os.path.normpath(dirpath))
            if parent_node is None:
                continue
            for dirname in sorted(dirnames):
                dir_item = QStandardItem(dirname)
                dir_item.setIcon(qta.icon('fa5.folder', color='grey'))
                dir_item.setCheckable(True)
                dir_item.setCheckState(Qt.CheckState.Checked)
                path = os.path.join(dirpath, dirname)
                dir_item.setData(path, Qt.ItemDataRole.UserRole)
                parent_node.appendRow(dir_item)
                path_map[path] = dir_item
            for filename in sorted(filenames):
                if filename in ignore_files:
                    continue
                ext_match = any(
                    filename.lower().endswith(ext) for ext in include_extensions
                )
                if "LICENSE" not in filename and not ext_match:
                    continue
                file_item = QStandardItem(filename)
                file_item.setIcon(qta.icon('fa5.file-alt', color='grey'))
                file_item.setCheckable(True)
                file_item.setCheckState(Qt.CheckState.Checked)
                path = os.path.join(dirpath, filename)
                file_item.setData(path, Qt.ItemDataRole.UserRole)
                parent_node.appendRow(file_item)
        self.file_tree.expandToDepth(0)

    def _on_item_changed(self, item: QStandardItem):
        if self._is_updating_checks:
            return
        self._is_updating_checks = True
        try:
            check_state = item.checkState()
            if check_state != Qt.CheckState.PartiallyChecked:
                self._update_descendant_states(item, check_state)
            if item.parent():
                self._update_ancestor_states(item.parent())
        finally:
            self._is_updating_checks = False
            self._update_toggle_button_state()

    def _update_descendant_states(self, parent_item, state):
        for row in range(parent_item.rowCount()):
            child = parent_item.child(row)
            if child and child.isCheckable() and child.checkState() != state:
                child.setCheckState(state)
                if child.hasChildren():
                    self._update_descendant_states(child, state)

    def _update_ancestor_states(self, parent_item):
        if not parent_item:
            return
        child_states = [
            parent_item.child(r).checkState() for r in
            range(parent_item.rowCount())
        ]
        if all(s == Qt.CheckState.Checked for s in child_states):
            new_state = Qt.CheckState.Checked
        elif all(s == Qt.CheckState.Unchecked for s in child_states):
            new_state = Qt.CheckState.Unchecked
        else:
            new_state = Qt.CheckState.PartiallyChecked
        if parent_item.checkState() != new_state:
            parent_item.setCheckState(new_state)

    def _get_checked_files(self) -> List[str]:
        checked_files = []
        root = self.file_model.invisibleRootItem()
        for row in range(root.rowCount()):
            self._recurse_get_checked(root.child(row), checked_files)
        return checked_files

    def _recurse_get_checked(self, parent_item, file_list):
        if parent_item.checkState() == Qt.CheckState.Unchecked:
            return
        path = parent_item.data(Qt.ItemDataRole.UserRole)
        is_file = path and os.path.isfile(path)
        is_checked = parent_item.checkState() == Qt.CheckState.Checked
        if is_file and is_checked:
            file_list.append(path)
        if parent_item.hasChildren():
            for row in range(parent_item.rowCount()):
                if child := parent_item.child(row):
                    self._recurse_get_checked(child, file_list)

    def _load_prompt_source(self, prompt_type: str, filepath: str):
        if os.path.exists(filepath):
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    self.prompt_sources[prompt_type] = json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                log.error(f"Failed to load prompts from {filepath}: {e}")

    def _load_and_populate_prompts(self):
        self.loadouts = settings_manager.get("ai_export_loadouts", {})
        self.prompt_sources = {PROMPT_TYPE_DEFAULT: DEFAULT_LOADOUTS}
        base_path = get_base_path()
        generative_path = os.path.join(
            base_path, "assets", "prompts", "generative_prompts.json"
        )
        community_path = os.path.join(
            base_path, "assets", "prompts", "additional_prompts.json"
        )
        self._load_prompt_source(PROMPT_TYPE_GENERATIVE, generative_path)
        self._load_prompt_source(PROMPT_TYPE_COMMUNITY, community_path)
        self.loadout_combo.clear()
        self.loadout_combo.addItem("--- Select a Loadout ---", None)
        self.loadout_combo.insertSeparator(self.loadout_combo.count())
        self._add_prompts_to_combo("Default", PROMPT_TYPE_DEFAULT)
        self._add_prompts_to_combo("New Feature", PROMPT_TYPE_GENERATIVE)
        self._add_prompts_to_combo("Community", PROMPT_TYPE_COMMUNITY)
        if self.loadouts:
            self.loadout_combo.insertSeparator(self.loadout_combo.count())
            for name in sorted(self.loadouts.keys()):
                self.loadout_combo.addItem(name, (PROMPT_TYPE_USER, name))
        self.loadout_combo.setCurrentIndex(0)

    def _add_prompts_to_combo(self, prefix, prompt_type):
        if source := self.prompt_sources.get(prompt_type):
            self.loadout_combo.insertSeparator(self.loadout_combo.count())
            for name in sorted(source.keys()):
                self.loadout_combo.addItem(
                    f"({prefix}) {name}", (prompt_type, name))

    def _on_loadout_selected(self, index):
        data = self.loadout_combo.itemData(index)
        if not data:
            self.instructions_edit.clear()
            self.guidelines_list.clear()
            return
        prompt_type, name = data
        if prompt_type == PROMPT_TYPE_USER:
            loadout_data = self.loadouts.get(name)
        else:
            loadout_data = self.prompt_sources.get(prompt_type, {}).get(name)

        if loadout_data:
            self.instructions_edit.setText(loadout_data.get("instructions", ""))
            self.guidelines_list.clear()
            self.guidelines_list.addItems(loadout_data.get("guidelines", []))
        is_user_loadout = (prompt_type == PROMPT_TYPE_USER)
        self.save_loadout_button.setText("Save As New...")
        self.save_loadout_button.setToolTip(
            "Save the current configuration as a new custom loadout.")
        self.delete_loadout_button.setEnabled(is_user_loadout)
        self.delete_loadout_button.setToolTip(
            "Delete this custom loadout." if is_user_loadout else
            "Cannot delete built-in loadouts."
        )
        if is_user_loadout:
            self.save_loadout_button.setText(f"Update '{name}'")
            self.save_loadout_button.setToolTip(
                f"Update the custom loadout '{name}'.")

    def _save_loadout(self):
        data = self.loadout_combo.currentData()
        is_update = data and data[0] == PROMPT_TYPE_USER
        name_to_save = data[1] if is_update else None
        if not is_update:
            name, ok = QInputDialog.getText(
                self, "Save Loadout As", "Enter name for new loadout:")
            if not (ok and name):
                return
            if name in self.loadouts or any(
                name in s for s in self.prompt_sources.values()
            ):
                QMessageBox.warning(self, "Name Exists",
                                    "A loadout with this name already exists.")
                return
            name_to_save = name
        guidelines = [self.guidelines_list.item(i).text() for i in
                      range(self.guidelines_list.count())]
        self.loadouts[name_to_save] = {
            "instructions": self.instructions_edit.toPlainText(),
            "guidelines": guidelines
        }
        settings_manager.set("ai_export_loadouts", self.loadouts)
        self._load_and_populate_prompts()
        new_index = self.loadout_combo.findData((PROMPT_TYPE_USER, name_to_save))
        if new_index != -1:
            self.loadout_combo.setCurrentIndex(new_index)
        QMessageBox.information(
            self, "Success", f"Loadout '{name_to_save}' saved.")

    def _delete_loadout(self):
        data = self.loadout_combo.currentData()
        if not data or data[0] != PROMPT_TYPE_USER:
            return
        name_to_delete = data[1]
        reply = QMessageBox.question(
            self, "Confirm Delete", f"Delete '{name_to_delete}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes and name_to_delete in self.loadouts:
            del self.loadouts[name_to_delete]
            settings_manager.set("ai_export_loadouts", self.loadouts)
            self._load_and_populate_prompts()

    def _add_guideline(self):
        text, ok = QInputDialog.getText(
            self, "Add Guideline", "Enter new guideline:")
        if ok and text:
            self.guidelines_list.addItem(QListWidgetItem(text))

    def _edit_guideline(self):
        if not (item := self.guidelines_list.currentItem()):
            return
        text, ok = QInputDialog.getText(
            self, "Edit Guideline", "Edit guideline:", text=item.text())
        if ok and text:
            item.setText(text)

    def _remove_guideline(self):
        if (item := self.guidelines_list.currentItem()):
            row = self.guidelines_list.row(item)
            self.guidelines_list.takeItem(row)

    def _load_and_populate_golden_rule_sets(self):
        self.golden_rule_sets = settings_manager.get(
            "ai_export_golden_rules", {})
        self.golden_rules_combo.clear()
        self.golden_rules_combo.addItem("--- Select a Rule Set ---", None)
        self.golden_rules_combo.insertSeparator(self.golden_rules_combo.count())
        for name in sorted(self.golden_rule_sets.keys()):
            self.golden_rules_combo.addItem(name)
        if "Default Golden Rules" in self.golden_rule_sets:
            self.golden_rules_combo.setCurrentText("Default Golden Rules")
        else:
            self.golden_rules_combo.setCurrentIndex(0)

    def _on_golden_rule_set_selected(self, index):
        name = self.golden_rules_combo.currentText()
        is_user_set = name not in ["--- Select a Rule Set ---"]
        if rules := self.golden_rule_sets.get(name):
            self.golden_rules_list.clear()
            self.golden_rules_list.addItems(rules)
        self.save_golden_rules_button.setText("Save As New...")
        self.save_golden_rules_button.setToolTip(
            "Save the current rules as a new set.")
        self.delete_golden_rules_button.setEnabled(
            is_user_set and name != "Default Golden Rules")
        if is_user_set:
            self.save_golden_rules_button.setText(f"Update '{name}'")
            self.save_golden_rules_button.setToolTip(
                f"Update the rule set '{name}'.")

    def _save_golden_rule_set(self):
        current_name = self.golden_rules_combo.currentText()
        is_update = current_name not in ["--- Select a Rule Set ---"]
        name_to_save = current_name if is_update else None
        if not is_update:
            name, ok = QInputDialog.getText(
                self, "Save Rule Set", "Enter name for rule set:")
            if not (ok and name):
                return
            if name in self.golden_rule_sets:
                QMessageBox.warning(
                    self, "Name Exists",
                    "A rule set with this name already exists.")
                return
            name_to_save = name
        rules = [self.golden_rules_list.item(i).text() for i in
                 range(self.golden_rules_list.count())]
        self.golden_rule_sets[name_to_save] = rules
        settings_manager.set("ai_export_golden_rules", self.golden_rule_sets)
        self._load_and_populate_golden_rule_sets()
        if (new_index := self.golden_rules_combo.findText(name_to_save)) != -1:
            self.golden_rules_combo.setCurrentIndex(new_index)
        QMessageBox.information(
            self, "Success", f"Golden Rule set '{name_to_save}' saved.")

    def _delete_golden_rule_set(self):
        name = self.golden_rules_combo.currentText()
        if name in self.golden_rule_sets and name != "Default Golden Rules":
            reply = QMessageBox.question(
                self, "Confirm Delete", f"Delete the rule set '{name}'?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.Yes:
                del self.golden_rule_sets[name]
                settings_manager.set(
                    "ai_export_golden_rules", self.golden_rule_sets)
                self._load_and_populate_golden_rule_sets()

    def _add_golden_rule(self):
        text, ok = QInputDialog.getText(
            self, "Add Golden Rule", "Enter new rule:")
        if ok and text:
            self.golden_rules_list.addItem(QListWidgetItem(text))

    def _edit_golden_rule(self):
        if not (item := self.golden_rules_list.currentItem()):
            return
        text, ok = QInputDialog.getText(
            self, "Edit Golden Rule", "Edit rule:", text=item.text())
        if ok and text:
            item.setText(text)

    def _remove_golden_rule(self):
        if (item := self.golden_rules_list.currentItem()):
            row = self.golden_rules_list.row(item)
            self.golden_rules_list.takeItem(row)

    def _generate_file_content_string(
        self, files: List[str], problems: Dict[str, List[Dict]]
    ) -> str:
        """Generates the file content portion of the prompt as a string."""
        content_parts = []
        for file_path in files:
            rel_path = os.path.relpath(
                file_path, self.project_path).replace(os.sep, '/')
            content_parts.append(f"### File: `/{rel_path}`\n")
            if file_problems := problems.get(file_path):
                content_parts.append("#### Linter Issues Found:\n```\n")
                for p in file_problems:
                    line_info = f"- L{p.get('line', '?')}"
                    if 'column' in p and p.get('column') is not None:
                        line_info += f":C{p.get('column')}"
                    code = p.get('code', 'N/A')
                    message = p.get('message', 'No message available')
                    msg = f"{line_info} ({code}) {message}\n"
                    content_parts.append(msg)
                content_parts.append("```\n\n")
            try:
                with open(file_path, 'r', encoding='utf-8') as cf:
                    content = cf.read()
                lang = self._get_lang_for_file(file_path)
                content_parts.append(f"```{lang}\n{content}\n```\n")
            except Exception as e:
                content_parts.append(f"```\nError reading file: {e}\n```\n")
        return "\n".join(content_parts)

    def _generate_file_tree_text(self, files: List[str]) -> str:
        tree = {}
        base_path = self.project_path
        for f in files:
            rel_path = os.path.relpath(f, base_path)
            parts = rel_path.split(os.sep)
            curr_level = tree
            for part in parts[:-1]:
                curr_level = curr_level.setdefault(part, {})
            curr_level[parts[-1]] = None

        def build_tree_string(d, indent=''):
            s = ''
            items = sorted(d.items())
            for i, (key, value) in enumerate(items):
                is_last = i == len(items) - 1
                s += indent + ('└── ' if is_last else '├── ') + key + '\n'
                if value is not None:
                    new_indent = indent + ('    ' if is_last else '│   ')
                    s += build_tree_string(value, new_indent)
            return s
        return (f"/{os.path.basename(base_path)}\n"
                f"{build_tree_string(tree, ' ')}")

    def _get_lang_for_file(self, file_path: str) -> str:
        ext = os.path.splitext(file_path)[1].lower()
        return {
            '.py': 'python', '.json': 'json', '.md': 'markdown',
            '.html': 'html', '.css': 'css', '.js': 'javascript',
            '.ts': 'typescript', '.yml': 'yaml', '.yaml': 'yaml',
            '.xml': 'xml', '.sh': 'shell', '.bat': 'batch',
        }.get(ext, 'text')

    def _build_prompt(
        self, instructions, guidelines, golden_rules, files, problems
    ) -> tuple[str, str]:
        """Builds system and user prompts for an API request."""
        system_parts = []
        if instructions:
            system_parts.append(f"## AI Instructions\n{instructions}")
        if guidelines:
            rules_str = "\n".join(f"- {rule}" for rule in guidelines)
            system_parts.append(f"## Guidelines & Rules\n{rules_str}")
        if golden_rules:
            rules_str = "\n".join(
                f"{i}. {rule}" for i, rule in enumerate(golden_rules, 1))
            system_parts.append(f"## Golden Rules\n{rules_str}")
        system_prompt = "\n\n".join(system_parts)
        user_prompt = "\n".join([
            "Here is the project context you need to work with.",
            "## File Tree\n```",
            self._generate_file_tree_text(files),
            "```",
            "## File Contents",
            self._generate_file_content_string(files, problems)
        ])
        return system_prompt, user_prompt

    def _start_export(self):
        self.selected_files = self._get_checked_files()
        if not self.selected_files:
            QMessageBox.warning(
                self, "No Files Selected", "Please select files to include.")
            return
        self.progress = QProgressDialog(
            "Linting selected files...", "Cancel", 0, 0, self)
        self.progress.setWindowModality(Qt.WindowModality.WindowModal)
        self.progress.show()
        QCoreApplication.processEvents()
        self.linter_manager.project_lint_results_ready.connect(
            self._on_lint_complete)
        self.linter_manager.lint_project(self.project_path)

    def _on_lint_complete(self, all_problems: Dict[str, List[Dict]]):
        self.linter_manager.project_lint_results_ready.disconnect(
            self._on_lint_complete)
        if self.progress.wasCanceled():
            return

        self.progress.setLabelText("Preparing context...")
        QCoreApplication.processEvents()

        instructions = self.instructions_edit.toPlainText()
        guidelines = [self.guidelines_list.item(i).text() for i in
                      range(self.guidelines_list.count())]
        golden_rules = [self.golden_rules_list.item(i).text() for i in
                        range(self.golden_rules_list.count())]

        selected_problems = {}
        if self.include_linter_checkbox.isChecked():
            selected_problems = {k: v for k, v in all_problems.items()
                                 if k in self.selected_files}

        if self.api_mode_checkbox.isChecked():
            self.progress.setLabelText("Sending to AI...")
            self._handle_api_request(
                instructions, guidelines, golden_rules, selected_problems)
        else:
            self.progress.setLabelText("Saving file...")
            self._handle_file_export(
                instructions, guidelines, golden_rules, selected_problems)
        if not self.progress.wasCanceled():
            self.progress.close()

    def _handle_api_request(
        self, instructions, guidelines, golden_rules, problems
    ):
        QApplication.setOverrideCursor(QCursor(Qt.CursorShape.WaitCursor))
        try:
            provider = self.api_provider_combo.currentText()
            model = self.api_model_combo.currentText()
            system_prompt, user_prompt = self._build_prompt(
                instructions, guidelines, golden_rules, self.selected_files,
                problems
            )
            success, response = self.api_client.send_request(
                provider, model, system_prompt, user_prompt)

            if success:
                response_dialog = AIResponseDialog(response, self)
                response_dialog.exec()
                self.accept()
            else:
                QMessageBox.critical(self, "API Error", response)
        finally:
            QApplication.restoreOverrideCursor()

    def _handle_file_export(
        self, instructions, guidelines, golden_rules, problems
    ):
        base_path = get_base_path()
        export_dir = os.path.join(base_path, "ai_exports")
        try:
            os.makedirs(export_dir, exist_ok=True)
        except OSError as e:
            msg = f"Could not create export directory at {export_dir}: {e}"
            log.error(msg)
            QMessageBox.critical(self, "Export Failed", msg)
            return

        proj_name = os.path.basename(self.project_path)
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"{proj_name}_export_{timestamp}.md"
        output_filepath = os.path.join(export_dir, filename)

        QApplication.setOverrideCursor(QCursor(Qt.CursorShape.WaitCursor))
        try:
            if "Standard Markdown" in self.format_combo.currentText():
                success, msg = self.project_manager.export_project_for_ai(
                    output_filepath=output_filepath,
                    selected_files=self.selected_files,
                    instructions=instructions, guidelines=guidelines,
                    golden_rules=golden_rules, all_problems=problems
                )
                if success:
                    message = f"Project exported successfully to:\n{output_filepath}"
                else:
                    message = msg
            else:
                system_prompt, user_prompt = self._build_prompt(
                    instructions, guidelines, golden_rules,
                    self.selected_files, problems)
                header = (
                    f"# Project Export: {os.path.basename(self.project_path)}\n"
                    f"## Export Timestamp: {datetime.now().isoformat()}\n---"
                )
                content = "\n\n".join(
                    [header, system_prompt, "---", "## Project Files", user_prompt]
                )
                with open(output_filepath, 'w', encoding='utf-8') as f:
                    f.write(content)
                success = True
                message = f"Project exported successfully to:\n{output_filepath}"

            if success:
                QMessageBox.information(self, "Export Complete", message)
                self.accept()
            else:
                QMessageBox.critical(self, "Export Failed", message)
        except Exception as e:
            log.error(f"Export failed with exception: {e}", exc_info=True)
            QMessageBox.critical(self, "Export Failed",
                                 f"An error occurred: '{e}'")
        finally:
            QApplication.restoreOverrideCursor()
```

### File: `/plugins/ai_tools/ai_response_dialog.py`

#### Linter Issues Found:
```

- L42 (W292) No message available

```


```python
# PuffinPyEditor/plugins/ai_tools/ai_response_dialog.py
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QTextEdit, QDialogButtonBox, QPushButton,
    QApplication
)
import qtawesome as qta


class AIResponseDialog(QDialog):
    """A dialog to display the response from an AI model."""
    def __init__(self, response_text: str, parent=None):
        super().__init__(parent)
        self.response_text = response_text
        self.setWindowTitle("AI Response")
        self.setMinimumSize(700, 500)
        self.setObjectName("AIResponseDialog")

        self.layout = QVBoxLayout(self)

        self.text_edit = QTextEdit()
        self.text_edit.setMarkdown(self.response_text)
        self.text_edit.setReadOnly(True)
        self.layout.addWidget(self.text_edit)

        self.button_box = QDialogButtonBox()
        self.copy_button = QPushButton(
            qta.icon('fa5s.copy'), "Copy to Clipboard"
        )
        self.button_box.addButton(
            self.copy_button, QDialogButtonBox.ButtonRole.ActionRole
        )
        self.button_box.addButton(QDialogButtonBox.StandardButton.Close)
        self.layout.addWidget(self.button_box)

        self.copy_button.clicked.connect(self._copy_to_clipboard)
        self.button_box.rejected.connect(self.reject)

    def _copy_to_clipboard(self):
        """Copies the response text to the system clipboard."""
        QApplication.clipboard().setText(self.response_text)
        self.copy_button.setText("Copied!")
        self.copy_button.setEnabled(False)
```

### File: `/plugins/ai_tools/api_client.py`

#### Linter Issues Found:
```

- L4 (F401) No message available

- L89 (W292) No message available

```


```python
# PuffinPyEditor/plugins/ai_tools/api_client.py
import requests
import json
from typing import Dict, Tuple
from utils.logger import log


class ApiClient:
    """A client to interact with various AI model APIs."""

    PROVIDER_CONFIG = {
        "OpenAI": {
            "endpoint": "https://api.openai.com/v1/chat/completions",
            "models": ["gpt-4o", "gpt-4-turbo", "gpt-3.5-turbo"],
        }
        # Other providers like Anthropic or Gemini could be added here
    }

    def __init__(self, settings_manager):
        self.settings_manager = settings_manager

    def get_api_key(self, provider: str) -> str | None:
        """Retrieves an API key for a given provider from settings."""
        api_keys = self.settings_manager.get("api_keys", {})
        return api_keys.get(provider)

    def send_request(
        self, provider: str, model: str, system_prompt: str, user_prompt: str
    ) -> Tuple[bool, str]:
        """
        Sends a request to the specified AI provider.

        Returns a tuple: (success: bool, response_content: str)
        """
        api_key = self.get_api_key(provider)
        if not api_key:
            msg = (
                f"API Key for {provider} not found. Please configure it in "
                "the settings."
            )
            return False, msg

        config = self.PROVIDER_CONFIG.get(provider)
        if not config:
            return False, f"Configuration for provider '{provider}' not found."

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "max_tokens": 4096,
        }

        try:
            log.info(f"Sending request to {provider} model {model}...")
            response = requests.post(
                config["endpoint"],
                headers=headers,
                data=json.dumps(payload),
                timeout=120  # 2-minute timeout
            )
            response.raise_for_status()

            data = response.json()
            content = data['choices'][0]['message']['content']
            log.info("Successfully received response from AI.")
            return True, content.strip()

        except requests.exceptions.RequestException as e:
            error_message = f"API request failed: {e}"
            if e.response is not None:
                error_message += f"\nResponse: {e.response.text}"
            log.error(error_message)
            return False, error_message
        except (KeyError, IndexError) as e:
            error_message = f"Failed to parse AI response: {e}"
            log.error(f"{error_message}\nFull Response: {response.text}")
            return False, error_message
        except Exception as e:
            error_message = f"An unexpected error occurred: {e}"
            log.error(error_message)
            return False, error_message
```

### File: `/plugins/ai_tools/plugin.json`

```json
{
    "id": "ai_tools",
    "name": "AI Tools",
    "author": "PuffinPy Team",
    "version": "1.2.0",
    "description": "Adds a highly configurable 'Export for AI' dialog and API integration.",
    "entry_point": "plugin_main.py"
}
```

### File: `/plugins/ai_tools/plugin_main.py`

#### Linter Issues Found:
```

- L35 (W292) No message available

```


```python
# PuffinPyEditor/plugins/ai_tools/plugin_main.py
from .ai_export_dialog import AIExportDialog


class AIToolsPlugin:
    def __init__(self, main_window):
        self.api = main_window.puffin_api
        self.api.add_menu_action(
            menu_name="tools",
            text="Export Project for AI...",
            callback=self.show_export_dialog,
            icon_name="fa5s.robot"
        )

    def show_export_dialog(self):
        project_manager = self.api.get_manager("project")
        project_path = project_manager.get_active_project_path()
        if not project_path:
            self.api.show_message(
                "info", "No Project Open",
                "Please open a project to use the AI Export tool."
            )
            return

        dialog = AIExportDialog(
            project_path,
            project_manager,
            self.api.get_manager("linter"),
            self.api.get_main_window()
        )
        dialog.exec()


def initialize(main_window):
    return AIToolsPlugin(main_window)
```

### File: `/plugins/api_keys_manager/__init__.py`

```python

```

### File: `/plugins/api_keys_manager/api_keys_settings_page.py`

#### Linter Issues Found:
```

- L78 (W292) No message available

```


```python
# PuffinPyEditor/plugins/api_keys_manager/api_keys_settings_page.py
from PyQt6.QtWidgets import (
    QDialog, QFormLayout, QLineEdit, QHBoxLayout, QPushButton, QLabel,
    QDialogButtonBox, QVBoxLayout
)
import qtawesome as qta


class ApiKeysDialog(QDialog):
    """A dialog for managing API keys."""
    def __init__(self, settings_manager, parent=None):
        super().__init__(parent)
        self.settings_manager = settings_manager

        self.setWindowTitle("Manage API Keys")
        self.setMinimumWidth(500)

        main_layout = QVBoxLayout(self)
        form_layout = QFormLayout()

        info_label = QLabel(
            "Enter your API keys below. They are stored locally and securely."
        )
        form_layout.addRow(info_label)

        # Add providers here. We'll start with OpenAI.
        self.openai_key_input, openai_layout = self._create_key_input()
        form_layout.addRow("OpenAI API Key:", openai_layout)

        main_layout.addLayout(form_layout)

        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok |
            QDialogButtonBox.StandardButton.Cancel
        )
        main_layout.addWidget(button_box)

        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)

        self.load_settings()

    def _create_key_input(self) -> tuple[QLineEdit, QHBoxLayout]:
        """Creates a password-style QLineEdit with a show/hide button."""
        layout = QHBoxLayout()
        line_edit = QLineEdit()
        line_edit.setEchoMode(QLineEdit.EchoMode.Password)

        show_hide_button = QPushButton(qta.icon('fa5s.eye'), "")
        show_hide_button.setCheckable(True)
        show_hide_button.setToolTip("Show/Hide Key")
        show_hide_button.setFixedWidth(30)
        show_hide_button.toggled.connect(
            lambda c: line_edit.setEchoMode(
                QLineEdit.EchoMode.Normal if c
                else QLineEdit.EchoMode.Password)
        )

        layout.addWidget(line_edit)
        layout.addWidget(show_hide_button)
        return line_edit, layout

    def load_settings(self):
        """Loads saved API keys into the input fields."""
        keys = self.settings_manager.get("api_keys", {})
        self.openai_key_input.setText(keys.get("OpenAI", ""))

    def save_settings(self):
        """Saves the API keys from the input fields."""
        keys = self.settings_manager.get("api_keys", {})
        keys["OpenAI"] = self.openai_key_input.text()
        self.settings_manager.set("api_keys", keys)
        self.settings_manager.save()

    def accept(self):
        """Saves settings and closes the dialog."""
        self.save_settings()
        super().accept()
```

### File: `/plugins/api_keys_manager/plugin.json`

```json
{
    "id": "api_keys_manager",
    "name": "API Keys Manager",
    "author": "PuffinPy Team",
    "version": "1.0.0",
    "description": "Provides a secure settings page for managing API provider keys.",
    "entry_point": "plugin_main.py"
}
```

### File: `/plugins/api_keys_manager/plugin_main.py`

#### Linter Issues Found:
```

- L25 (W292) No message available

```


```python
# PuffinPyEditor/plugins/api_keys_manager/plugin_main.py
from .api_keys_settings_page import ApiKeysDialog


class ApiKeysManagerPlugin:
    def __init__(self, main_window):
        self.api = main_window.puffin_api
        self.settings_manager = self.api.get_manager("settings")
        self.main_window = self.api.get_main_window()

        self.api.add_menu_action(
            menu_name="tools",
            text="Manage API Keys...",
            callback=self.show_api_keys_dialog,
            icon_name="fa5s.key"
        )

    def show_api_keys_dialog(self):
        """Create and show the API keys management dialog."""
        dialog = ApiKeysDialog(self.settings_manager, self.main_window)
        dialog.exec()


def initialize(main_window):
    return ApiKeysManagerPlugin(main_window)
```

### File: `/plugins/find_replace/__init__.py`

```python

```

### File: `/plugins/find_replace/find_panel.py`

#### Linter Issues Found:
```

- L197 (W292) No message available

```


```python
# /plugins/find_replace/find_panel.py
from typing import Optional
from PyQt6.QtWidgets import (QWidget, QHBoxLayout, QVBoxLayout, QLineEdit,
                             QPushButton, QCheckBox, QToolButton, QFrame)
from PyQt6.QtGui import QTextDocument, QKeyEvent
from PyQt6.QtCore import Qt, pyqtSignal
import qtawesome as qta

from app_core.settings_manager import settings_manager
from ui.editor_widget import EditorWidget
from app_core.theme_manager import theme_manager


class FindPanel(QFrame):
    """An integrated panel for find and replace operations."""
    close_requested = pyqtSignal()
    status_message_requested = pyqtSignal(str, int)

    def __init__(self, parent: QWidget):
        super().__init__(parent)
        self.editor: Optional[EditorWidget] = None
        self.setObjectName("FindPanelFrame")
        self._setup_ui()
        self._connect_signals()
        self.load_settings()
        self.update_theme()

    def _setup_ui(self):
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
        button = QToolButton()
        button.setAutoRaise(True)
        button.setToolTip(tooltip)
        button.setProperty("icon_name", icon_name)
        if text:
            button.setText(text)
            button.setToolButtonStyle(
                Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        return button

    def _connect_signals(self):
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

    def connect_editor(self, editor: EditorWidget):
        self.editor = editor
        initial_text = editor.text_area.textCursor().selectedText()
        if initial_text:
            self.find_input.setText(initial_text)
        self.focus_find_input()
        self._update_button_states()

    def focus_find_input(self):
        self.find_input.setFocus()
        self.find_input.selectAll()

    def update_theme(self):
        colors = theme_manager.current_theme_data['colors']
        frame_bg = colors.get('sidebar.background', '#333')
        self.setStyleSheet(
            f"#FindPanelFrame {{ background-color: {frame_bg}; "
            f"border-bottom: 1px solid {colors.get('input.border')}; }}")
        for button in self.findChildren((QToolButton, QPushButton)):
            icon_name = button.property("icon_name")
            if icon_name:
                button.setIcon(qta.icon(icon_name))

    def keyPressEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key.Key_Escape:
            self.close_requested.emit()
            return
        super().keyPressEvent(event)

    def load_settings(self):
        self.case_checkbox.setChecked(
            settings_manager.get("search_case_sensitive", False))
        self.whole_word_checkbox.setChecked(
            settings_manager.get("search_whole_word", False))

    def save_settings(self):
        settings_manager.set(
            "search_case_sensitive", self.case_checkbox.isChecked())
        settings_manager.set(
            "search_whole_word", self.whole_word_checkbox.isChecked())

    def _update_button_states(self):
        has_text = bool(self.find_input.text())
        self.find_next_button.setEnabled(has_text)
        self.find_prev_button.setEnabled(has_text)
        self.replace_button.setEnabled(has_text)
        self.replace_all_button.setEnabled(has_text)

    def _get_find_flags(self) -> QTextDocument.FindFlag:
        flags = QTextDocument.FindFlag(0)
        if self.case_checkbox.isChecked():
            flags |= QTextDocument.FindFlag.FindCaseSensitively
        if self.whole_word_checkbox.isChecked():
            flags |= QTextDocument.FindFlag.FindWholeWords
        return flags

    def _find(self, backwards: bool = False):
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

### File: `/plugins/find_replace/plugin.json`

```json
{
    "id": "find_replace",
    "name": "Find/Replace",
    "author": "PuffinPy Team",
    "version": "1.1.1",
    "description": "Adds a Find/Replace dialog (Ctrl+F).",
    "entry_point": "plugin_main.py"
}
```

### File: `/plugins/find_replace/plugin_main.py`

#### Linter Issues Found:
```

- L38 (E501) No message available

- L90 (W292) No message available

```


```python
# PuffinPyEditor/plugins/find_replace/plugin_main.py
from PyQt6.QtGui import QAction
from .find_panel import FindPanel
from ui.editor_widget import EditorWidget
import qtawesome as qta


class FindReplacePlugin:
    def __init__(self, main_window):
        self.main_window = main_window
        self.api = main_window.puffin_api

        # Action with shortcut, added to both menu and toolbar
        self.find_action = self.api.add_menu_action(
            "edit", "&Find/Replace...", self.toggle_find_panel,
            "Ctrl+F", "fa5s.search"
        )
        # Add a dedicated instance of the action to the toolbar
        toolbar_find_action = QAction(qta.icon('fa5s.search'), "Find/Replace",
                                      self.main_window)
        toolbar_find_action.setToolTip("Find/Replace (Ctrl+F)")
        toolbar_find_action.triggered.connect(self.toggle_find_panel)

        prefs_action = self.main_window.actions.get("preferences")
        if prefs_action:
            self.main_window.main_toolbar.insertAction(
                prefs_action, toolbar_find_action)
        else:
            self.api.add_toolbar_action(toolbar_find_action)

        self.find_action.setEnabled(False)
        toolbar_find_action.setEnabled(False)  # Keep them in sync
        self.toolbar_find_action = toolbar_find_action

        self.find_panel = None

        # Connect signals
        self.main_window.tab_widget.currentChanged.connect(self._on_tab_changed)

        # Initial check
        self._on_tab_changed(self.main_window.tab_widget.currentIndex())

    def _ensure_panel_exists(self):
        """Creates the panel instance on-demand."""
        if self.find_panel is None:
            self.find_panel = FindPanel(self.main_window)
            self.find_panel.status_message_requested.connect(
                self.api.show_status_message)
            self.find_panel.close_requested.connect(self.handle_panel_close)
            self.find_panel.hide()

    def toggle_find_panel(self):
        editor = self.main_window.tab_widget.currentWidget()
        if not isinstance(editor, EditorWidget):
            return

        self._ensure_panel_exists()

        if self.find_panel.isVisible():
            self.handle_panel_close()
        else:
            # Attach the panel to the current editor
            self.find_panel.setParent(editor)
            editor.main_layout.insertWidget(0, self.find_panel)
            self.find_panel.connect_editor(editor)
            self.find_panel.show()

    def handle_panel_close(self):
        """Hides the panel and returns focus to the editor."""
        if self.find_panel:
            editor_to_focus = self.find_panel.editor
            self.find_panel.hide()
            self.find_panel.setParent(None)  # Detach from editor
            if editor_to_focus:
                editor_to_focus.text_area.setFocus()

    def _on_tab_changed(self, index: int):
        widget = self.main_window.tab_widget.widget(index)
        is_editor = isinstance(widget, EditorWidget)
        self.find_action.setEnabled(is_editor)
        self.toolbar_find_action.setEnabled(is_editor)

        # Always hide the panel when switching tabs
        if self.find_panel and self.find_panel.isVisible():
            self.handle_panel_close()


def initialize(main_window):
    """Entry point for the Find/Replace plugin."""
    return FindReplacePlugin(main_window)
```

### File: `/plugins/github_tools/__init__.py`

```python

```

### File: `/plugins/github_tools/github_dialog.py`

```python
# PuffinPyEditor/plugins/github_tools/github_dialog.py
import os
from typing import Optional, List, Dict, Any
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QWidget,
                             QSplitter, QLabel, QListWidget, QListWidgetItem,
                             QPushButton, QMessageBox, QFileDialog)
from PyQt6.QtCore import Qt, pyqtSignal
from app_core.github_manager import GitHubManager
from app_core.source_control_manager import SourceControlManager
import qtawesome as qta


class GitHubDialog(QDialog):
    """
    A dialog for browsing and cloning a user's GitHub repositories.
    """
    project_cloned = pyqtSignal(str)

    def __init__(self, github_manager: GitHubManager,
                 git_manager: SourceControlManager,
                 parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.github_manager = github_manager
        self.git_manager = git_manager

        self.setWindowTitle("GitHub Repository Management")
        self.setMinimumSize(800, 600)
        self._setup_ui()
        self._connect_signals()

    def _setup_ui(self):
        layout = QVBoxLayout(self)

        top_bar_layout = QHBoxLayout()
        self.user_label = QLabel("<i>Checking authentication...</i>")
        top_bar_layout.addWidget(self.user_label)
        top_bar_layout.addStretch()
        layout.addLayout(top_bar_layout)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        layout.addWidget(splitter)
        left_pane = self._create_repo_list_pane()
        right_pane = self._create_details_pane()
        splitter.addWidget(left_pane)
        splitter.addWidget(right_pane)
        splitter.setSizes([300, 500])

    def _create_repo_list_pane(self) -> QWidget:
        pane = QWidget()
        layout = QVBoxLayout(pane)
        layout.setContentsMargins(0, 0, 0, 0)
        toolbar_layout = QHBoxLayout()
        self.refresh_button = QPushButton("Refresh List")
        self.refresh_button.setIcon(qta.icon('fa5s.sync-alt'))
        toolbar_layout.addWidget(self.refresh_button)
        toolbar_layout.addStretch()
        self.repo_list = QListWidget()
        layout.addLayout(toolbar_layout)
        layout.addWidget(self.repo_list)
        return pane

    def _create_details_pane(self) -> QWidget:
        pane = QWidget()
        layout = QVBoxLayout(pane)
        self.repo_details_label = QLabel("<i>Select a repository...</i>")
        self.repo_details_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.repo_details_label.setWordWrap(True)
        layout.addWidget(self.repo_details_label, 1)
        layout.addWidget(QLabel("<b>Branches:</b>"))
        self.branch_list = QListWidget()
        layout.addWidget(self.branch_list, 2)
        self.clone_button = QPushButton("Clone Selected Branch")
        self.clone_button.setIcon(qta.icon('fa5s.download'))
        self.clone_button.setEnabled(False)
        layout.addWidget(self.clone_button)
        return pane

    def _connect_signals(self):
        self.github_manager.repos_ready.connect(self.populate_repo_list)
        self.github_manager.branches_ready.connect(self.populate_branch_list)
        self.github_manager.operation_failed.connect(
            self._on_operation_failed)
        self.repo_list.currentItemChanged.connect(self.on_repo_selected)
        self.refresh_button.clicked.connect(self.github_manager.list_repos)
        self.clone_button.clicked.connect(self.on_clone_clicked)

    def showEvent(self, event):
        super().showEvent(event)
        self._update_user_info()
        self.refresh_button.click()

    def closeEvent(self, event):
        try:
            self.github_manager.repos_ready.disconnect(self.populate_repo_list)
            self.github_manager.branches_ready.disconnect(
                self.populate_branch_list)
            self.github_manager.operation_failed.disconnect(
                self._on_operation_failed)
        except TypeError:
            pass  # Suppress errors if signals are not connected
        super().closeEvent(event)

    def _update_user_info(self):
        user_info = self.github_manager.get_user_info()
        if user_info and user_info.get('login'):
            self.user_label.setText(
                f"Authenticated as: <b>{user_info['login']}</b>")
        else:
            self.user_label.setText(
                "<i>Authentication details not available.</i>")

    def populate_repo_list(self, repos: List[Dict[str, Any]]):
        self.repo_list.clear()
        for repo in sorted(repos, key=lambda r: r['name'].lower()):
            item = QListWidgetItem(repo['name'])
            item.setToolTip(repo['full_name'])
            item.setData(Qt.ItemDataRole.UserRole, repo)
            self.repo_list.addItem(item)

    def populate_branch_list(self, branches: List[Dict[str, Any]]):
        self.branch_list.clear()
        for branch in branches:
            item = QListWidgetItem(branch['name'])
            item.setData(Qt.ItemDataRole.UserRole, branch)
            self.branch_list.addItem(item)
        if branches:
            self.branch_list.setCurrentRow(0)

    def on_repo_selected(self, current_item: QListWidgetItem):
        self.branch_list.clear()
        self.clone_button.setEnabled(False)
        if not current_item:
            self.repo_details_label.setText("<i>Select a repository...</i>")
            return
        repo_data = current_item.data(Qt.ItemDataRole.UserRole)
        desc = repo_data.get('description') or 'No description provided.'
        self.repo_details_label.setText(
            f"<b>{repo_data['full_name']}</b><br/><small>{desc}</small>")
        self.github_manager.list_branches(repo_data['full_name'])
        self.clone_button.setEnabled(True)

    def on_clone_clicked(self):
        repo_item = self.repo_list.currentItem()
        branch_item = self.branch_list.currentItem()
        if not repo_item or not branch_item:
            QMessageBox.warning(self, "Selection Required",
                                "Please select a repository and a branch.")
            return
        repo_data = repo_item.data(Qt.ItemDataRole.UserRole)
        branch_data = branch_item.data(Qt.ItemDataRole.UserRole)
        path = QFileDialog.getExistingDirectory(
            self, f"Select Folder to Clone '{repo_data['name']}' Into")
        if not path:
            return
        clone_path = os.path.join(path, repo_data['name'])
        if os.path.exists(clone_path):
            QMessageBox.critical(
                self, "Folder Exists",
                f"The folder '{repo_data['name']}' already exists here.")
            return
        self.git_manager.clone_repo(
            repo_data['clone_url'], path, branch_data['name'])
        QMessageBox.information(
            self, "Clone Started",
            "Cloning has started. The project will open when complete.")
        self.project_cloned.emit(clone_path)
        self.accept()

    def _on_operation_failed(self, error_message: str):
        QMessageBox.critical(self, "GitHub Error", error_message)

```

### File: `/plugins/github_tools/new_release_dialog.py`

#### Linter Issues Found:
```

- L150 (E501) No message available

- L183 (W292) No message available

```


```python
# PuffinPyEditor/plugins/github_tools/new_release_dialog.py
from typing import Optional, Dict, Any
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QFormLayout,
                             QDialogButtonBox, QLineEdit, QTextEdit, QLabel,
                             QCheckBox, QComboBox, QHBoxLayout, QWidget,
                             QGroupBox, QPushButton, QMessageBox)
from app_core.source_control_manager import SourceControlManager
from utils.versioning import suggest_next_version

try:
    import git
except ImportError:
    git = None


class NewReleaseDialog(QDialog):
    """
    A dialog for creating a new GitHub release. It collects tag name, title,
    notes, and other release options.
    """

    def __init__(self, project_path: str, git_manager: SourceControlManager,
                 parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.project_path = project_path
        self.git_manager = git_manager

        self.setWindowTitle("Create New Release")
        self.setMinimumWidth(500)

        self._setup_ui()
        self._connect_signals()
        self._populate_branches()
        self._validate_input()

    def _setup_ui(self):
        """Creates the main UI layout and widgets."""
        self.main_layout = QVBoxLayout(self)

        # Use a FormLayout for standard label-field pairs
        form_layout = QFormLayout()
        form_layout.setRowWrapPolicy(QFormLayout.RowWrapPolicy.WrapAllRows)

        # Tag Name
        tag_layout_widget = QWidget()
        tag_layout = QHBoxLayout(tag_layout_widget)
        tag_layout.setContentsMargins(0, 0, 0, 0)
        suggested_tag = suggest_next_version()
        self.tag_edit = QLineEdit(suggested_tag)
        self.tag_edit.setPlaceholderText("e.g., v1.2.1")
        self.branch_combo = QComboBox()
        self.branch_combo.setToolTip(
            "Select the branch to create the release from.")
        tag_layout.addWidget(self.tag_edit, 2)
        tag_layout.addWidget(QLabel("on branch:"))
        tag_layout.addWidget(self.branch_combo, 1)
        form_layout.addRow("<b>Tag Name:</b>", tag_layout_widget)

        # Release Title
        self.title_edit = QLineEdit()
        self.title_edit.setText(suggested_tag)
        self.title_edit.setPlaceholderText(
            "e.g., Feature Update and Bug Fixes")
        form_layout.addRow("<b>Release Title:</b>", self.title_edit)

        # Add the form layout to the main dialog layout
        self.main_layout.addLayout(form_layout)

        # --- Release Notes Section (manual layout) ---
        notes_header_layout = QHBoxLayout()
        notes_header_layout.addWidget(QLabel("<b>Release Notes:</b>"))
        notes_header_layout.addStretch()
        self.generate_notes_button = QPushButton("Generate from Commits")
        self.generate_notes_button.setToolTip(
            "Generate release notes from commits since the last tag.")
        notes_header_layout.addWidget(self.generate_notes_button)
        self.main_layout.addLayout(notes_header_layout)

        self.notes_edit = QTextEdit()
        self.notes_edit.setPlaceholderText(
            "Describe the changes in this release (Markdown is supported).")
        self.notes_edit.setMinimumHeight(150)
        self.main_layout.addWidget(self.notes_edit)
        # --- End of Release Notes Section ---

        # Options and Assets Groups
        options_group = QGroupBox("Options")
        options_layout = QVBoxLayout(options_group)
        self.prerelease_checkbox = QCheckBox("Mark as a pre-release")
        self.prerelease_checkbox.setToolTip(
            "Indicates that this is not a production-ready release.")
        options_layout.addWidget(self.prerelease_checkbox)
        options_layout.addStretch()
        self.main_layout.addWidget(options_group)

        assets_group = QGroupBox("Release Assets")
        assets_layout = QVBoxLayout(assets_group)
        self.build_installer_checkbox = QCheckBox(
            "Build and attach installer")
        self.build_installer_checkbox.setToolTip(
            "Runs the project's build script and uploads the setup file.")
        self.build_installer_checkbox.setChecked(True)
        assets_layout.addWidget(self.build_installer_checkbox)
        assets_layout.addStretch()
        self.main_layout.addWidget(assets_group)

        # Dialog Buttons
        self.button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok |
            QDialogButtonBox.StandardButton.Cancel
        )
        self.main_layout.addWidget(self.button_box)

    def _connect_signals(self):
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        self.tag_edit.textChanged.connect(self._validate_input)
        self.title_edit.textChanged.connect(self._validate_input)
        self.generate_notes_button.clicked.connect(
            self._generate_release_notes)

    def _populate_branches(self):
        branches = self.git_manager.get_local_branches(self.project_path)
        self.branch_combo.addItems(branches)
        if 'main' in branches:
            self.branch_combo.setCurrentText('main')
        elif 'master' in branches:
            self.branch_combo.setCurrentText('master')

    def _validate_input(self):
        is_valid = bool(
            self.tag_edit.text().strip() and
            self.title_edit.text().strip() and
            self.branch_combo.currentText()
        )
        ok_button = self.button_box.button(QDialogButtonBox.StandardButton.Ok)
        ok_button.setEnabled(is_valid)

    def _generate_release_notes(self):
        if git is None:
            QMessageBox.critical(
                self, "Missing Dependency",
                "The 'GitPython' library is not installed. Please install it "
                "(`pip install GitPython`) to use this feature.")
            return
        try:
            repo = git.Repo(self.project_path, search_parent_directories=True)
            tags = sorted(repo.tags, key=lambda t: t.commit.committed_datetime)
            latest_tag = tags[-1] if tags else None
            latest_tag_name = latest_tag.name if latest_tag else "the beginning"
            target_branch = self.branch_combo.currentText()

            rev_range = target_branch
            if latest_tag:
                rev_range = f"{latest_tag.commit.hexsha}..{target_branch}"

            commits = list(repo.iter_commits(rev_range))
            commit_log = []
            for commit in commits:
                if len(commit.parents) > 1:  # Skip merge commits
                    continue
                commit_log.append(f"- {commit.summary} ({commit.hexsha[:7]})")

            if commit_log:
                self.notes_edit.setText("\n".join(commit_log))
            else:
                QMessageBox.information(
                    self, "No New Commits",
                    "No new commits found on branch "
                    f"'{target_branch}' since tag '{latest_tag_name}'.")
        except Exception as e:
            QMessageBox.critical(self, "Error Generating Notes",
                                 f"An error occurred: {e}")

    def get_release_data(self) -> Dict[str, Any]:
        return {
            "tag": self.tag_edit.text().strip(),
            "title": self.title_edit.text().strip(),
            "notes": self.notes_edit.toPlainText().strip(),
            "prerelease": self.prerelease_checkbox.isChecked(),
            "target_branch": self.branch_combo.currentText(),
            "build_installer": self.build_installer_checkbox.isChecked()
        }
```

### File: `/plugins/github_tools/plugin.json`

```json
{
    "id": "github_tools",
    "name": "GitHub Tools",
    "author": "PuffinPy Team",
    "version": "1.2.0",
    "description": "Provides UI for cloning, releases, and other GitHub interactions.",
    "entry_point": "plugin_main.py"
}
```

### File: `/plugins/github_tools/plugin_main.py`

#### Linter Issues Found:
```

- L458 (E128) No message available

- L520 (W292) No message available

```


```python
# PuffinPyEditor/plugins/github_tools/plugin_main.py
import os
import shutil
import tempfile
import git
import subprocess

from PyQt6.QtWidgets import (QInputDialog, QMessageBox, QProgressDialog,
                             QTextEdit)
from PyQt6.QtCore import Qt, QCoreApplication
from PyQt6.QtGui import QFont

from .new_release_dialog import NewReleaseDialog
from .select_repo_dialog import SelectRepoDialog
from .github_dialog import GitHubDialog
from utils import versioning


class GitHubToolsPlugin:
    def __init__(self, main_window):
        self.main_window = main_window
        self.api = main_window.puffin_api
        self.project_manager = self.api.get_manager("project")
        self.git_manager = self.api.get_manager("git")
        self.github_manager = self.api.get_manager("github")

        self.github_dialog = None
        self._release_state = {}  # Central dictionary to manage release state

        self.api.log_info("GitHub Tools plugin initialized.")

        self.api.add_menu_action(
            "tools", "Build Project Installer",
            self._show_build_installer_dialog,
            icon_name="fa5s.cogs"
        )

    def _get_sc_panel(self):
        # FIX: The plugin manager stores Plugin objects, not dicts.
        sc_plugin_obj = self.main_window.plugin_manager.plugins.get(
            'source_control_ui')
        if sc_plugin_obj and sc_plugin_obj.instance:
            return sc_plugin_obj.instance.source_control_panel
        return None

    def _ensure_git_identity(self, project_path: str) -> bool:
        self.api.log_info("Checking Git author information...")
        user_info = self.github_manager.get_user_info()
        if not user_info:
            self.api.show_message("warning", "GitHub User Not Found",
                                  "Could not fetch GitHub user info. "
                                  "Please log in.")
            return False
        try:
            repo = git.Repo(project_path)
            user_name = user_info.get('login')
            user_email = user_info.get('email')

            if not user_email:
                # Fallback to the private no-reply email
                user_email = (f"{user_info.get('id')}+{user_name}"
                              "@users.noreply.github.com")
                self.api.log_info(
                    "GitHub email is private. Falling back to no-reply "
                    "address. To see contributions, enable 'Keep my email "
                    "addresses private' in GitHub settings."
                )
            self.api.log_info(f"Setting git author for this operation to: "
                              f"Name='{user_name}', Email='{user_email}'")

            with repo.config_writer() as config:
                config.set_value('user', 'name', user_name)
                config.set_value('user', 'email', user_email)
            self.api.log_info("Git author configured for this operation.")
            return True
        except Exception as e:
            self.api.show_message("warning", "Git Config Failed",
                                  f"Failed to set Git author info: {e}")
            return False

    def show_create_release_dialog(self):
        """
        Public method to show the 'Create Release' dialog. Intended to be
        called from other plugins.
        """
        project_path = self.project_manager.get_active_project_path()
        if not project_path:
            self.api.show_message("info", "No Project Open",
                                  "Please open a project to create a release.")
            return
        self._create_release(project_path)

    def _create_release(self, project_path):
        if not self._ensure_git_identity(project_path):
            self.api.show_status_message(
                "Release cancelled: Git identity misconfiguration.", 5000)
            return

        try:
            repo = git.Repo(project_path)
            if not repo.remotes:
                self.api.show_message("warning", "No Remote",
                                      "This project has no remote repository.")
                return
            remote_url = repo.remotes.origin.url
            if 'github.com' not in remote_url:
                self.api.show_message(
                    "warning", "Not a GitHub Remote",
                    "The 'origin' remote of this project does not appear "
                    "to be a GitHub repository."
                )
                return

            owner, repo_name = self.git_manager.parse_git_url(remote_url)
            if not owner or not repo_name:
                self.api.show_message(
                    "critical", "Error",
                    "Could not parse owner/repo from remote.")
                return
        except Exception as e:
            self.api.show_message(
                "critical", "Error", f"Could not analyze repository: {e}")
            return

        dialog = NewReleaseDialog(
            project_path, self.git_manager, self.main_window)
        if not dialog.exec():
            self.api.show_status_message("Release cancelled.", 3000)
            return

        self._release_state = {
            'dialog_data': dialog.get_release_data(),
            'project_path': project_path,
            'owner': owner,
            'repo_name': repo_name,
            'step': None
        }

        self._advance_release_state("CREATE_TAG")

    def _advance_release_state(self, next_step):
        self._release_state['step'] = next_step
        step = self._release_state['step']
        dialog_data = self._release_state['dialog_data']
        project_path = self._release_state['project_path']

        self._cleanup_all_connections()

        if sc_panel := self._get_sc_panel():
            sc_panel.set_ui_locked(
                True, f"Step: {step.replace('_', ' ').title()}...")

        if step == "CREATE_TAG":
            self.git_manager.git_success.connect(
                self._on_release_step_succeeded)
            self.git_manager.git_error.connect(self._on_release_step_failed)
            self.git_manager.create_tag(
                project_path, dialog_data['tag'], dialog_data['title'])
        elif step == "PUSH_TAG":
            self.git_manager.git_success.connect(
                self._on_release_step_succeeded)
            self.git_manager.git_error.connect(self._on_release_step_failed)
            self.git_manager.push_specific_tag(
                project_path, dialog_data['tag'])
        elif step == "CREATE_RELEASE":
            self.github_manager.operation_success.connect(
                self._on_release_step_succeeded)
            self.github_manager.operation_failed.connect(
                self._on_release_step_failed)
            self.github_manager.create_github_release(
                owner=self._release_state['owner'],
                repo=self._release_state['repo_name'],
                tag_name=dialog_data['tag'], name=dialog_data['title'],
                body=dialog_data['notes'],
                prerelease=dialog_data['prerelease'])
        elif step == "BUILD_ASSETS":
            self._run_build_script(project_path)
        elif step == "UPLOAD_ASSETS":
            self._upload_assets()
        elif step == "BUMP_VERSION_COMMIT":
            if not versioning.write_new_version(dialog_data['tag']):
                self._on_release_step_failed(
                    "Failed to write new version to VERSION.txt.")
                return
            self.main_window._update_window_title()
            self.git_manager.git_success.connect(
                self._on_release_step_succeeded)
            self.git_manager.git_error.connect(self._on_release_step_failed)
            self.git_manager.commit_files(
                project_path, f"ci: Release {dialog_data['tag']}")
        elif step == "FINAL_PUSH":
            self.git_manager.git_success.connect(
                self._on_release_step_succeeded)
            self.git_manager.git_error.connect(self._on_release_step_failed)
            self.git_manager.push(project_path)

    def _on_release_step_succeeded(self, msg, data):
        step = self._release_state.get('step')
        self.api.log_info(f"SUCCESS on step '{step}': {msg}")

        if step == "CREATE_TAG":
            self._advance_release_state("PUSH_TAG")
        elif step == "PUSH_TAG":
            self._advance_release_state("CREATE_RELEASE")
        elif step == "CREATE_RELEASE":
            self._release_state['release_info'] = data.get("release_data", {})
            if dialog_data := self._release_state.get('dialog_data'):
                if dialog_data.get("build_installer"):
                    self._advance_release_state("BUILD_ASSETS")
                else:
                    self._advance_release_state("UPLOAD_ASSETS")
        elif step == "UPLOAD_ASSET":
            self._upload_next_asset()
        elif step == "BUMP_VERSION_COMMIT":
            self._advance_release_state("FINAL_PUSH")
        elif step == "FINAL_PUSH":
            tag = self._release_state['dialog_data']['tag']
            success_msg = f"Release '{tag}' published successfully!"
            self.api.show_status_message(success_msg, 5000)
            QMessageBox.information(self.main_window, "Success", success_msg)
            self._cleanup_release_process()

    def _run_build_script(self, project_path):
        build_script = os.path.join(project_path, "installer", "build.bat")
        if not os.path.exists(build_script):
            self._on_release_step_failed(
                f"Build script not found at '{build_script}'.")
            return

        progress = QProgressDialog("Building Application...",
                                   "This may take a moment...", 0, 0,
                                   self.main_window)
        progress.setCancelButton(None)
        progress.setWindowModality(Qt.WindowModality.WindowModal)
        progress.show()
        QCoreApplication.processEvents()

        args = [build_script]
        if self.api.get_manager("settings").get("cleanup_after_build", True):
            args.append("cleanup")
        version_str = self._release_state['dialog_data']['tag'].lstrip('v')
        args.extend(["--version", version_str])
        if nsis_path := self.api.get_manager("settings").get("nsis_path"):
            args.extend(["--nsis-path", nsis_path])

        self.api.log_info(
            f"Executing build script with subprocess: {' '.join(args)}")
        try:
            result = subprocess.run(
                args,
                capture_output=True,
                text=True,
                encoding='utf-8',
                shell=True,
                cwd=project_path
            )
        finally:
            progress.close()

        if result.returncode != 0:
            error_msg = "The build script failed. See details below."
            full_output = (f"--- STDOUT ---\n{result.stdout}\n\n"
                           f"--- STDERR ---\n{result.stderr}")
            self._show_build_error_dialog(error_msg, full_output)
            self._on_release_step_failed(
                f"Build script failed with exit code {result.returncode}.")
        else:
            self.api.show_status_message("Build successful.", 3000)
            self._advance_release_state("UPLOAD_ASSETS")

    def _show_build_error_dialog(self, summary: str, details: str):
        dialog = QMessageBox(self.main_window)
        dialog.setIcon(QMessageBox.Icon.Critical)
        dialog.setWindowTitle("Build Failed")
        dialog.setText(summary)
        # Use a larger fixed-size layout for the error dialog
        dialog.layout().setColumnStretch(1, 1)
        text_edit = QTextEdit()
        text_edit.setReadOnly(True)
        text_edit.setFont(QFont("Consolas", 9))
        text_edit.setText(details)
        text_edit.setMinimumSize(600, 300)
        dialog.layout().addWidget(text_edit, 1, 0, 1, -1)
        dialog.exec()

    def _show_build_installer_dialog(self):
        project_path = self.project_manager.get_active_project_path()
        if not project_path:
            self.api.show_message("info", "No Project",
                                  "Please open a project.")
            return

        reply = QMessageBox.question(
            self.main_window, "Confirm Build",
            "This will run the project's full build. Continue?",
            QMessageBox.StandardButton.Yes |
            QMessageBox.StandardButton.Cancel)
        if reply == QMessageBox.StandardButton.Yes:
            self._release_state = {
                'dialog_data': {'tag': f"v{versioning.APP_VERSION}",
                                'build_installer': True},
                'project_path': project_path
            }
            self._run_build_script(project_path)

    def _upload_assets(self):
        assets_to_upload = []
        dialog_data = self._release_state['dialog_data']
        repo_name = self._release_state['repo_name']
        project_path = self._release_state['project_path']

        try:
            temp_zip_dir = tempfile.mkdtemp()
            self._release_state['temp_dir'] = temp_zip_dir  # Store for cleanup
            zip_name = f"{repo_name}-{dialog_data['tag']}.zip"
            zip_path = os.path.join(temp_zip_dir, zip_name)
            if self.project_manager.create_project_zip(zip_path):
                assets_to_upload.append(zip_path)
        except Exception as e:
            self.api.log_error(f"Error creating source zip: {e}")

        if dialog_data.get("build_installer"):
            dist_path = os.path.join(project_path, "dist")
            version_str = dialog_data['tag'].lstrip('v')
            installer_name = f"PuffinPyEditor_v{version_str}_Setup.exe"
            installer_path = os.path.join(dist_path, installer_name)
            if os.path.exists(installer_path):
                assets_to_upload.append(installer_path)
            else:
                self.api.log_warning(
                    f"Installer not found after build: {installer_path}")

        if not assets_to_upload:
            self.api.log_info("No assets to upload, moving to finalize.")
            self._advance_release_state("BUMP_VERSION_COMMIT")
            return

        self._release_state['asset_queue'] = assets_to_upload
        self._upload_next_asset()

    def _upload_next_asset(self):
        asset_queue = self._release_state.get('asset_queue', [])
        if not asset_queue:
            self.api.log_info("All assets uploaded. Moving to finalize.")
            self._advance_release_state("BUMP_VERSION_COMMIT")
            return

        asset_path = asset_queue.pop(0)
        upload_url = self._release_state.get(
            'release_info', {}).get('upload_url')
        if sc_panel := self._get_sc_panel():
            asset_name = os.path.basename(asset_path)
            sc_panel.set_ui_locked(True, f"Uploading {asset_name}...")

        self._release_state['step'] = "UPLOAD_ASSET"
        self.github_manager.operation_success.connect(
            self._on_release_step_succeeded)
        self.github_manager.operation_failed.connect(
            self._on_release_step_failed)
        self.github_manager.upload_asset(upload_url, asset_path)

    def _on_release_step_failed(self, error_message):
        step = self._release_state.get('step', 'UNKNOWN')
        failure_msg = (
            f"An error occurred at step '{step}': {error_message}")

        if step in ["BUMP_VERSION_COMMIT", "FINAL_PUSH"]:
            failure_msg += (
                "\n\nA local commit to bump the version may have been "
                "created. You might need to undo it manually "
                "(e.g., 'git reset HEAD~1')."
            )

        self.api.log_error(f"Release failed: {failure_msg}")
        self.api.show_message("critical", "Release Failed",
                              f"{failure_msg}\n\nAttempting to roll back...")

        tag_name = self._release_state.get('dialog_data', {}).get('tag')
        release_id = self._release_state.get('release_info', {}).get('id')

        if release_id:
            msg = f"ROLLBACK: Deleting GitHub release ID {release_id}"
            self.api.log_info(msg)
            self.github_manager.delete_release(
                self._release_state['owner'],
                self._release_state['repo_name'],
                release_id)
        if tag_name and step != "CREATE_TAG":
            msg = f"ROLLBACK: Deleting remote tag '{tag_name}'"
            self.api.log_info(msg)
            self.git_manager.delete_remote_tag(
                self._release_state['project_path'], tag_name)
        if tag_name:
            self.api.log_info(f"ROLLBACK: Deleting local tag '{tag_name}'")
            self.git_manager.delete_tag(
                self._release_state['project_path'], tag_name)

        self._cleanup_release_process()

    def _cleanup_all_connections(self):
        try:
            self.git_manager.git_success.disconnect(
                self._on_release_step_succeeded)
            self.git_manager.git_error.disconnect(self._on_release_step_failed)
            self.github_manager.operation_success.disconnect(
                self._on_release_step_succeeded)
            self.github_manager.operation_failed.disconnect(
                self._on_release_step_failed)
        except TypeError:
            pass

    def _cleanup_release_process(self):
        self.api.log_info("Cleaning up release process state.")
        self._cleanup_all_connections()

        if sc_panel := self._get_sc_panel():
            sc_panel.set_ui_locked(False, "Release process finished.")

        temp_dir = self._release_state.get('temp_dir')
        if temp_dir and os.path.exists(temp_dir):
            shutil.rmtree(temp_dir, ignore_errors=True)
            self.api.log_info(f"Cleaned temp dir: {temp_dir}")

        self._release_state = {}

    def _publish_repo(self, local_path):
        if not self._ensure_git_identity(local_path):
            if sc_panel := self._get_sc_panel():
                sc_panel.set_ui_locked(False, "Publish cancelled.")
            return

        repo_name, ok = QInputDialog.getText(
            self.main_window, "Publish to GitHub", "Repository Name:",
            text=os.path.basename(local_path))
        if not ok or not repo_name:
            if sc_panel := self._get_sc_panel():
                sc_panel.set_ui_locked(False, "Publish cancelled.")
            return

        description, _ = QInputDialog.getText(
            self.main_window, "Publish to GitHub", "Description (optional):")
        is_private = QMessageBox.question(
            self.main_window, "Visibility", "Make this repository private?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No) == QMessageBox.StandardButton.Yes

        def on_repo_created(msg, data, path=local_path):
            if "Repository" in msg and "created" in msg:
                self._cleanup_all_connections()
                clone_url = data.get("clone_url")
                if sc_panel := self._get_sc_panel():
                    sc_panel.set_ui_locked(True, "Linking and pushing...")
                self.git_manager.publish_repo(path, clone_url)

        self.github_manager.operation_success.connect(on_repo_created)
        self.github_manager.operation_failed.connect(
            lambda msg: self._get_sc_panel().set_ui_locked(False,
                                                          f"Error: {msg}"))
        if sc_panel := self._get_sc_panel():
            sc_panel.set_ui_locked(True,
                                   f"Creating '{repo_name}' on GitHub...")
        self.github_manager.create_repo(repo_name, description, is_private)

    def _link_repo(self, local_path):
        dialog = SelectRepoDialog(self.github_manager, self.main_window)
        if dialog.exec() and (repo_data := dialog.selected_repo_data):
            if clone_url := repo_data.get('clone_url'):
                if sc_panel := self._get_sc_panel():
                    sc_panel.set_ui_locked(True, "Linking to remote...")
                self.git_manager.link_to_remote(local_path, clone_url)

    def _change_visibility(self, local_path):
        try:
            repo = git.Repo(local_path)
            if not repo.remotes:
                return
            remote_url = repo.remotes.origin.url
            owner, repo_name = self.git_manager.parse_git_url(remote_url)
            if not owner or not repo_name:
                return
            is_private = QMessageBox.question(
                self.main_window, "Change Visibility",
                "Make repository private?",
                QMessageBox.StandardButton.Yes |
                QMessageBox.StandardButton.No
            ) == QMessageBox.StandardButton.Yes

            if sc_panel := self._get_sc_panel():
                sc_panel.set_ui_locked(True, "Changing visibility...")
            self.github_manager.update_repo_visibility(
                owner, repo_name, is_private)
        except Exception as e:
            self.api.show_message("critical", "Error",
                                  f"Could not get repository info: {e}")

    def _show_github_dialog(self):
        if not self.github_dialog:
            self.github_dialog = GitHubDialog(self.github_manager,
                                              self.git_manager,
                                              self.main_window)
            self.github_dialog.project_cloned.connect(
                lambda path: self.project_manager.open_project(path))
        self.github_dialog.show()


def initialize(main_window):
    """
    Initializes the GitHub Tools plugin.
    """
    plugin = GitHubToolsPlugin(main_window)
    plugin.api.add_menu_action(
        "tools", "GitHub Repositories...", plugin._show_github_dialog,
        icon_name="fa5b.github")

    plugin.api.add_menu_action(
        "tools", "New Release...", plugin.show_create_release_dialog,
        icon_name="fa5s.tag"
    )

    return plugin
```

### File: `/plugins/github_tools/select_repo_dialog.py`

#### Linter Issues Found:
```

- L101 (W292) No message available

```


```python
# PuffinPyEditor/plugins/github_tools/select_repo_dialog.py
from typing import Optional, List, Dict, Any
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QListWidget,
                             QListWidgetItem, QDialogButtonBox, QMessageBox,
                             QLineEdit, QHBoxLayout, QLabel, QWidget)
from PyQt6.QtCore import Qt
from app_core.github_manager import GitHubManager


class SelectRepoDialog(QDialog):
    """
    A reusable dialog for selecting a GitHub repository from a user's account.
    """
    def __init__(self, github_manager: GitHubManager,
                 parent: Optional[QWidget] = None,
                 title: str = "Select Target Repository"):
        super().__init__(parent)
        self.github_manager = github_manager
        self.selected_repo_data: Optional[Dict[str, Any]] = None
        self.all_repos: List[Dict[str, Any]] = []

        self.setWindowTitle(title)
        self.setMinimumSize(500, 400)
        self.main_layout = QVBoxLayout(self)

        self._setup_ui()
        self._connect_signals()
        self.github_manager.list_repos()

    def _setup_ui(self):
        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("Filter:"))
        self.filter_edit = QLineEdit()
        self.filter_edit.setPlaceholderText("Type to filter repositories...")
        search_layout.addWidget(self.filter_edit)
        self.main_layout.addLayout(search_layout)

        self.repo_list_widget = QListWidget()
        self.repo_list_widget.itemDoubleClicked.connect(self.accept)
        self.main_layout.addWidget(self.repo_list_widget)

        self.button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok |
            QDialogButtonBox.StandardButton.Cancel
        )
        self.main_layout.addWidget(self.button_box)
        ok_button = self.button_box.button(QDialogButtonBox.StandardButton.Ok)
        ok_button.setEnabled(False)

    def _connect_signals(self):
        self.github_manager.repos_ready.connect(self._handle_repos_loaded)
        self.github_manager.operation_failed.connect(self._on_load_failed)
        self.filter_edit.textChanged.connect(self._filter_repo_list)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)

    def closeEvent(self, event):
        try:
            self.github_manager.repos_ready.disconnect(
                self._handle_repos_loaded)
            self.github_manager.operation_failed.disconnect(
                self._on_load_failed)
        except TypeError:
            pass  # Suppress errors if signals are not connected
        super().closeEvent(event)

    def _handle_repos_loaded(self, repos: List[Dict[str, Any]]):
        self.all_repos = sorted(repos, key=lambda r: r['full_name'].lower())
        self._populate_repo_list()
        if self.repo_list_widget.count() > 0:
            ok_button = self.button_box.button(
                QDialogButtonBox.StandardButton.Ok)
            ok_button.setEnabled(True)
            self.repo_list_widget.setCurrentRow(0)

    def _populate_repo_list(self):
        self.repo_list_widget.clear()
        filter_text = self.filter_edit.text().lower()
        for repo in self.all_repos:
            if filter_text in repo['full_name'].lower():
                item = QListWidgetItem(repo['full_name'])
                item.setToolTip(repo.get('description', 'No description'))
                item.setData(Qt.ItemDataRole.UserRole, repo)
                self.repo_list_widget.addItem(item)

    def _filter_repo_list(self):
        self._populate_repo_list()

    def _on_load_failed(self, error_message: str):
        QMessageBox.critical(self, "Failed to Load Repositories",
                             error_message)
        self.reject()

    def accept(self):
        current_item = self.repo_list_widget.currentItem()
        if not current_item:
            QMessageBox.warning(self, "No Selection",
                                "Please select a repository.")
            return
        self.selected_repo_data = current_item.data(Qt.ItemDataRole.UserRole)
        super().accept()
```

### File: `/plugins/global_drag_drop_handler/__init__.py`

```python

```

### File: `/plugins/global_drag_drop_handler/plugin.json`

```json
{
    "id": "global_drag_drop_handler",
    "name": "Global Drag and Drop Handler",
    "author": "PuffinPy Team",
    "version": "1.0.0",
    "description": "Enables dragging and dropping files from the OS onto the application to open them in tabs.",
    "entry_point": "plugin_main.py"
}
```

### File: `/plugins/global_drag_drop_handler/plugin_main.py`

#### Linter Issues Found:
```

- L16 (W293) No message available

- L27 (E501) No message available

- L49 (E501) No message available

- L58 (W293) No message available

- L71 (E501) No message available

- L76 (E501) No message available

- L77 (W292) No message available

```


```python
# PuffinPyEditor/plugins/global_drag_drop_handler/plugin_main.py
import os
from PyQt6.QtCore import QObject, QEvent
from utils.logger import log


class GlobalDragDropHandlerPlugin(QObject):
    """
    A plugin that installs an event filter on the main window to handle
    files being dragged and dropped from the operating system.
    """
    def __init__(self, main_window):
        # We need the API and the main_window object itself
        self.api = main_window.puffin_api
        self.main_window = self.api.get_main_window()
        
        # Initialize the QObject base class AFTER setting our properties
        super().__init__(self.main_window)

        # Tell the main window to send its events to our eventFilter method
        self.main_window.installEventFilter(self)
        self.main_window.setAcceptDrops(True)  # Explicitly enable drops
        log.info("Global Drag and Drop handler installed on main window.")

    def eventFilter(self, obj, event: QEvent) -> bool:
        """
        This method intercepts events from the object it's watching (the main window).
        """
        # Ensure we are only filtering events for the main_window
        if obj is not self.main_window:
            return super().eventFilter(obj, event)

        if event.type() == QEvent.Type.DragEnter:
            # A drag operation has entered the widget's boundaries.
            # Check if the data being dragged contains file URLs.
            if event.mimeData().hasUrls():
                # Accept the event, which changes the cursor to indicate
                # that a drop is possible.
                event.acceptProposedAction()
                return True  # Event handled

        if event.type() == QEvent.Type.Drop:
            # The user has released the mouse button to drop the data.
            if event.mimeData().hasUrls():
                files_to_open = []
                for url in event.mimeData().urls():
                    if url.isLocalFile():
                        file_path = url.toLocalFile()
                        # We only want to open files, not directories, via this method.
                        if os.path.isfile(file_path):
                            files_to_open.append(file_path)

                if files_to_open:
                    log.info(f"Accepted drop event for files: {files_to_open}")
                    # Use the main window's existing logic to open files
                    for f_path in files_to_open:
                        self.main_window._action_open_file(f_path)
                    
                    event.acceptProposedAction()
                    return True  # Event handled

        # For all other events, pass them on to the default handler.
        return super().eventFilter(obj, event)


def initialize(main_window):
    """
    Entry point function for PuffinPyEditor to load the plugin.
    """
    try:
        # We must return the instance so the plugin manager can hold a reference
        plugin_instance = GlobalDragDropHandlerPlugin(main_window)
        log.info("Global Drag and Drop Plugin initialized successfully.")
        return plugin_instance
    except Exception as e:
        log.error(f"Failed to initialize Global D&D Plugin: {e}", exc_info=True)
        return None
```

### File: `/plugins/linter_ui/__init__.py`

```python

```

### File: `/plugins/linter_ui/plugin.json`

```json
{
    "id": "linter_ui",
    "name": "Linter UI",
    "author": "PuffinPy Team",
    "version": "1.1.1",
    "description": "Provides the 'Problems' panel to display linter results from Flake8.",
    "entry_point": "plugin_main.py"
}
```

### File: `/plugins/linter_ui/plugin_main.py`

#### Linter Issues Found:
```

- L43 (W292) No message available

```


```python
# PuffinPyEditor/plugins/linter_ui/plugin_main.py
from PyQt6.QtCore import Qt
from .problems_panel import ProblemsPanel
from ui.editor_widget import EditorWidget


class LinterUIPlugin:
    def __init__(self, main_window):
        self.main_window = main_window
        self.api = main_window.puffin_api
        self.linter_manager = self.api.get_manager("linter")
        self.problems_panel = ProblemsPanel(main_window)
        self._setup_ui()
        self._connect_signals()

    def _setup_ui(self):
        self.api.register_dock_panel(
            self.problems_panel, "Problems",
            Qt.DockWidgetArea.BottomDockWidgetArea, "fa5s.bug"
        )

    def _connect_signals(self):
        self.linter_manager.lint_results_ready.connect(self._update_problems)
        self.linter_manager.error_occurred.connect(
            lambda err: self.problems_panel.show_info_message(
                f"Linter Error: {err}")
        )
        self.problems_panel.problem_selected.connect(
            self.main_window._goto_definition_result)

    def _update_problems(self, problems: list):
        editor = self.main_window.tab_widget.currentWidget()
        if not isinstance(editor, EditorWidget):
            return

        filepath = self.main_window.editor_tabs_data.get(
            editor, {}).get('filepath')
        if filepath:
            self.problems_panel.update_problems({filepath: problems})


def initialize(main_window):
    return LinterUIPlugin(main_window)
```

### File: `/plugins/linter_ui/problems_panel.py`

#### Linter Issues Found:
```

- L95 (W292) No message available

```


```python
# PuffinPyEditor/plugins/linter_ui/problems_panel.py
import os
from typing import Dict, List, Optional
from PyQt6.QtWidgets import QTreeWidget, QTreeWidgetItem, QHeaderView, QWidget
from PyQt6.QtCore import pyqtSignal, Qt
from utils.logger import log


class ProblemsPanel(QTreeWidget):
    """
    A widget that displays linting problems in a hierarchical tree view,
    grouped by file.
    """
    problem_selected = pyqtSignal(str, int, int)

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        log.info("ProblemsPanel initializing...")

        self.setColumnCount(4)
        self.setHeaderLabels(["Description", "File", "Line", "Code"])
        self.setSelectionBehavior(QTreeWidget.SelectionBehavior.SelectRows)
        self.setSelectionMode(QTreeWidget.SelectionMode.SingleSelection)
        self.setEditTriggers(QTreeWidget.EditTrigger.NoEditTriggers)
        self.setAlternatingRowColors(True)
        self.setIndentation(12)
        self.setSortingEnabled(True)

        header = self.header()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)

        self.itemDoubleClicked.connect(self._on_item_double_clicked)
        log.info("ProblemsPanel initialized as QTreeWidget.")

    def update_problems(self, problems_by_file: Dict[str, List[Dict]]):
        """
        Clears and repopulates the tree with a new set of problems.
        """
        self.clear()
        self.setSortingEnabled(False)

        if not problems_by_file:
            self.show_info_message("No problems found.")
            return

        for filepath, problems in problems_by_file.items():
            if not problems:
                continue

            file_node = QTreeWidgetItem(self)
            file_node.setText(
                0, f"{os.path.basename(filepath)} ({len(problems)} issues)")
            file_node.setData(
                0, Qt.ItemDataRole.UserRole, {'is_file_node': True})
            file_node.setFirstColumnSpanned(True)

            for problem in problems:
                problem_node = QTreeWidgetItem(file_node)
                problem_node.setText(0, problem.get("description", ""))
                problem_node.setText(1, os.path.basename(filepath))
                problem_node.setText(2, str(problem.get("line", "")))
                problem_node.setText(3, problem.get("code", ""))
                problem_node.setData(0, Qt.ItemDataRole.UserRole, {
                    'filepath': filepath,
                    'line': problem.get("line"),
                    'col': problem.get("col")
                })
        self.expandAll()
        self.setSortingEnabled(True)
        self.sortByColumn(1, Qt.SortOrder.AscendingOrder)

    def clear_problems(self):
        """Clears all items from the panel."""
        self.clear()

    def show_info_message(self, message: str):
        """Displays a single, un-clickable informational message."""
        self.clear()
        info_item = QTreeWidgetItem(self, [message])
        info_item.setFirstColumnSpanned(True)
        info_item.setDisabled(True)

    def _on_item_double_clicked(self, item: QTreeWidgetItem, column: int):
        """Emits a signal when a specific problem item is double-clicked."""
        problem_data = item.data(0, Qt.ItemDataRole.UserRole)
        if problem_data and not problem_data.get('is_file_node', False):
            filepath = problem_data.get("filepath")
            line = problem_data.get("line")
            col = problem_data.get("col")
            if filepath and line is not None:
                log.debug(f"Problem selected: Go to {filepath}:{line}:{col}")
                self.problem_selected.emit(filepath, line, col)
```

### File: `/plugins/markdown_viewer/__init__.py`

```python

```

### File: `/plugins/markdown_viewer/markdown_editor_widget.py`

#### Linter Issues Found:
```

- L79 (E501) No message available

- L151 (E501) No message available

- L468 (W292) No message available

```


```python
# /plugins/markdown_viewer/markdown_editor_widget.py
import qtawesome as qta
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTextBrowser,
                             QPlainTextEdit, QSplitter, QMenu, QLineEdit,
                             QToolButton, QFrame)
from PyQt6.QtGui import (QFont, QTextCursor, QMouseEvent, QPainter, QColor,
                         QKeySequence, QAction)
from PyQt6.QtCore import QTimer, pyqtSignal, Qt, QSize
from markdown import markdown

from app_core.theme_manager import theme_manager
from app_core.settings_manager import settings_manager
from utils.logger import log
from .markdown_syntax_highlighter import MarkdownSyntaxHighlighter


# =============================================================================
# Floating Formatting Toolbar
# =============================================================================
class MarkdownFormattingToolbar(QWidget):
    """A floating, horizontal toolbar for rich text formatting."""
    format_bold_requested = pyqtSignal()
    format_italic_requested = pyqtSignal()
    format_strikethrough_requested = pyqtSignal()
    format_inline_code_requested = pyqtSignal()
    heading_level_requested = pyqtSignal(int)
    code_block_requested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(
            Qt.WindowType.ToolTip | Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self.frame = QFrame(self)
        self.frame.setObjectName("FormattingToolbarFrame")

        self.layout = QHBoxLayout(self.frame)
        self.layout.setContentsMargins(4, 4, 4, 4)
        self.layout.setSpacing(2)

        self._add_tool_button("fa5s.bold", "Bold (Ctrl+B)",
                              self.format_bold_requested)
        self._add_tool_button("fa5s.italic", "Italic (Ctrl+I)",
                              self.format_italic_requested)
        self._add_tool_button("fa5s.strikethrough", "Strikethrough",
                              self.format_strikethrough_requested)
        self._add_tool_button("fa5s.code", "Inline Code",
                              self.format_inline_code_requested)
        self._add_separator()
        self._create_heading_menu()
        self._add_separator()
        self._add_tool_button(
            "fa5s.file-code", "Insert Code Block", self.code_block_requested
        )

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(self.frame)
        self.update_theme()

    def _add_tool_button(self, icon_name, tooltip, signal_to_emit):
        button = QToolButton()
        button.setIcon(qta.icon(icon_name, color='white'))
        button.setToolTip(tooltip)
        button.clicked.connect(signal_to_emit.emit)
        self.layout.addWidget(button)

    def _add_separator(self):
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.VLine)
        sep.setFrameShadow(QFrame.Shadow.Sunken)
        self.layout.addWidget(sep)

    def _create_heading_menu(self):
        heading_button = QToolButton()
        heading_button.setIcon(qta.icon("fa5s.heading", color='white'))
        heading_button.setToolTip("Apply Heading")
        heading_button.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        heading_menu = QMenu(self)
        for i in range(1, 7):
            action = QAction(f"Heading {i}", self)
            action.triggered.connect(
                lambda _, level=i: self.heading_level_requested.emit(level))
            heading_menu.addAction(action)
        heading_button.setMenu(heading_menu)
        self.layout.addWidget(heading_button)

    def update_theme(self):
        colors = theme_manager.current_theme_data.get('colors', {})
        menu_bg = colors.get('menu.background', '#3a4145')
        border_color = colors.get('input.border', '#555555')
        self.frame.setStyleSheet(f"""
            #FormattingToolbarFrame {{
                background-color: {menu_bg};
                border: 1px solid {border_color};
                border-radius: 6px;
            }}
            QToolButton {{
                background-color: transparent; border: none; padding: 5px;
                border-radius: 4px;
            }}
            QToolButton:hover {{
                background-color: {colors.get('accent', '#88c0d0')};
            }}
            QFrame[frameShape="5"] {{ color: {border_color}; }}
        """)

    def show_at(self, pos):
        self.move(pos)
        self.show()
        self.activateWindow()
        self.setFocus()

    def focusOutEvent(self, event):
        self.hide()
        super().focusOutEvent(event)


class LineNumberArea(QWidget):
    def __init__(self, editor):
        super().__init__(editor)
        self.source_editor = editor

    def sizeHint(self):
        return QSize(self.source_editor.line_number_area_width(), 0)

    def paintEvent(self, event):
        self.source_editor.line_number_area_paint_event(event)


class InteractiveTextBrowser(QTextBrowser):
    source_focus_requested = pyqtSignal(str)

    def mouseDoubleClickEvent(self, event: QMouseEvent):
        cursor = self.cursorForPosition(event.pos())
        cursor.select(QTextCursor.SelectionType.BlockUnderCursor)
        if (clicked_text := cursor.selectedText().strip()):
            self.source_focus_requested.emit(clicked_text)
        super().mouseDoubleClickEvent(event)


class MarkdownSourceEditor(QPlainTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.line_number_area = LineNumberArea(self)
        self.blockCountChanged.connect(self.update_line_number_area_width)
        self.updateRequest.connect(self.update_line_number_area)
        self.update_line_number_area_width(0)
        self.formatting_toolbar = MarkdownFormattingToolbar(self)
        self.formatting_toolbar.format_bold_requested.connect(self._format_bold)
        self.formatting_toolbar.format_italic_requested.connect(
            self._format_italic)
        self.formatting_toolbar.format_strikethrough_requested.connect(
            self._format_strikethrough)
        self.formatting_toolbar.format_inline_code_requested.connect(
            self._format_inline_code)
        self.formatting_toolbar.heading_level_requested.connect(
            self._format_heading)
        self.formatting_toolbar.code_block_requested.connect(
            self._insert_code_block)

    def line_number_area_width(self):
        digits = len(str(max(1, self.blockCount())))
        return 10 + self.fontMetrics().horizontalAdvance('9') * digits

    def update_line_number_area_width(self, _):
        self.setViewportMargins(self.line_number_area_width(), 0, 0, 0)

    def update_line_number_area(self, rect, dy):
        if dy:
            self.line_number_area.scroll(0, dy)
        else:
            self.line_number_area.update(0, rect.y(),
                                         self.line_number_area.width(),
                                         rect.height())
        if rect.contains(self.viewport().rect()):
            self.update_line_number_area_width(0)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        cr = self.contentsRect()
        self.line_number_area.setGeometry(
            cr.left(), cr.top(), self.line_number_area_width(), cr.height())

    def line_number_area_paint_event(self, event):
        painter = QPainter(self.line_number_area)
        colors = theme_manager.current_theme_data.get('colors', {})
        gutter_bg = colors.get('editorGutter.background', '#f0f0f0')
        painter.fillRect(event.rect(), QColor(gutter_bg))

        block = self.firstVisibleBlock()
        block_geo = self.blockBoundingGeometry(block)
        top = block_geo.translated(self.contentOffset()).top()
        bottom = top + self.blockBoundingRect(block).height()

        current_line_num = self.textCursor().blockNumber()
        block_number = block.blockNumber()
        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                number = str(block_number + 1)
                is_current = block_number == current_line_num
                pen_color = colors.get(
                    'editor.foreground' if is_current else
                    'editorGutter.foreground'
                )
                painter.setPen(QColor(pen_color))
                painter.drawText(
                    0, int(top), self.line_number_area.width() - 5,
                    self.fontMetrics().height(),
                    Qt.AlignmentFlag.AlignRight, number
                )
            block = block.next()
            top = bottom
            bottom = top + self.blockBoundingRect(block).height()
            block_number += 1

    def contextMenuEvent(self, event):
        self.formatting_toolbar.show_at(event.globalPos())

    def keyPressEvent(self, event):
        if event.matches(QKeySequence.StandardKey.Bold):
            self._format_bold()
        elif event.matches(QKeySequence.StandardKey.Italic):
            self._format_italic()
        else:
            super().keyPressEvent(event)

    def _wrap_selection(self, prefix, suffix=None):
        suffix = suffix or prefix
        cursor = self.textCursor()
        if not cursor.hasSelection():
            cursor.insertText(f"{prefix}text{suffix}")
            cursor.movePosition(QTextCursor.MoveOperation.Left, n=len(suffix))
            cursor.movePosition(QTextCursor.MoveOperation.Left,
                                QTextCursor.MoveMode.KeepAnchor, n=4)
        else:
            text = cursor.selectedText()
            cursor.insertText(f"{prefix}{text}{suffix}")
        self.setTextCursor(cursor)

    def _format_bold(self):
        self._wrap_selection("**")

    def _format_italic(self):
        self._wrap_selection("*")

    def _format_strikethrough(self):
        self._wrap_selection("~~")

    def _format_inline_code(self):
        self._wrap_selection("`")

    def _format_heading(self, level):
        cursor = self.textCursor()
        cursor.beginEditBlock()
        cursor.movePosition(QTextCursor.MoveOperation.StartOfBlock)
        cursor.insertText(f'{"#" * level} ')
        cursor.endEditBlock()

    def _insert_code_block(self):
        cursor = self.textCursor()
        cursor.beginEditBlock()
        cursor.insertText("\n```python\n\n```\n")
        cursor.movePosition(QTextCursor.MoveOperation.Up, n=2)
        cursor.endEditBlock()
        self.setTextCursor(cursor)


class MarkdownEditorWidget(QWidget):
    content_changed = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.filepath = None
        self.original_hash = 0
        self.is_syncing_scroll = False
        self._setup_ui()
        self._connect_signals()
        self.update_theme()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        self.search_bar = QWidget()
        search_layout = QHBoxLayout(self.search_bar)
        search_layout.setContentsMargins(5, 2, 5, 2)
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Find...")
        self.prev_button = QToolButton()
        self.prev_button.setIcon(qta.icon('fa5s.arrow-up'))
        self.next_button = QToolButton()
        self.next_button.setIcon(qta.icon('fa5s.arrow-down'))
        self.close_search_button = QToolButton()
        self.close_search_button.setIcon(qta.icon('fa5s.times'))
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(self.prev_button)
        search_layout.addWidget(self.next_button)
        search_layout.addWidget(self.close_search_button)
        layout.addWidget(self.search_bar)
        self.search_bar.hide()
        splitter = QSplitter(self)
        layout.addWidget(splitter)
        self.editor = MarkdownSourceEditor()
        self.editor_scrollbar = self.editor.verticalScrollBar()
        self.highlighter = MarkdownSyntaxHighlighter(self.editor.document())
        self.viewer = InteractiveTextBrowser()
        self.viewer.setOpenExternalLinks(True)
        self.viewer_scrollbar = self.viewer.verticalScrollBar()
        splitter.addWidget(self.editor)
        splitter.addWidget(self.viewer)
        splitter.setSizes([self.width() // 2, self.width() // 2])

    def _connect_signals(self):
        self.update_timer = QTimer(self)
        self.update_timer.setSingleShot(True)
        self.update_timer.setInterval(300)
        self.update_timer.timeout.connect(self._render_preview)
        self.editor.textChanged.connect(self.update_timer.start)
        self.editor.textChanged.connect(self.content_changed.emit)
        self.editor_scrollbar.valueChanged.connect(self._sync_viewer_scroll)
        self.viewer_scrollbar.valueChanged.connect(self._sync_editor_scroll)
        self.viewer.source_focus_requested.connect(self._focus_source_text)
        self.search_input.returnPressed.connect(self.next_button.click)
        self.next_button.clicked.connect(lambda: self._find_text())
        self.prev_button.clicked.connect(
            lambda: self._find_text(backwards=True))
        self.close_search_button.clicked.connect(self.search_bar.hide)

    def keyPressEvent(self, event):
        if event.matches(QKeySequence.StandardKey.Find):
            self.search_bar.show()
            self.search_input.setFocus()
            self.search_input.selectAll()
        elif event.key() == Qt.Key.Key_Escape and self.search_bar.isVisible():
            self.search_bar.hide()
        else:
            self.editor.keyPressEvent(event)
            super().keyPressEvent(event)

    def _find_text(self, backwards=False):
        query = self.search_input.text()
        if not query:
            return
        flags = QTextCursor.FindFlag(0)
        if self.editor.find(
                query, flags | QTextCursor.FindFlag.FindCaseSensitively):
            flags |= QTextCursor.FindFlag.FindCaseSensitively
        if backwards:
            flags |= QTextCursor.FindFlag.FindBackward
        self.editor.find(query, flags)

    def _focus_source_text(self, text_to_find: str):
        if self.editor.find(text_to_find):
            self.editor.setFocus()
        elif self.editor.find(text_to_find.splitlines()[0]):
            self.editor.setFocus()

    def _sync_viewer_scroll(self, value):
        if self.is_syncing_scroll:
            return
        self.is_syncing_scroll = True
        editor_max = self.editor_scrollbar.maximum()
        scroll_ratio = value / editor_max if editor_max > 0 else 0
        self.viewer_scrollbar.setValue(
            int(self.viewer_scrollbar.maximum() * scroll_ratio))
        self.is_syncing_scroll = False

    def _sync_editor_scroll(self, value):
        if self.is_syncing_scroll:
            return
        self.is_syncing_scroll = True
        viewer_max = self.viewer_scrollbar.maximum()
        scroll_ratio = value / viewer_max if viewer_max > 0 else 0
        self.editor_scrollbar.setValue(
            int(self.editor_scrollbar.maximum() * scroll_ratio))
        self.is_syncing_scroll = False

    def load_file(self, filepath: str):
        self.filepath = filepath
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            self.original_hash = hash(content)
            self.editor.setPlainText(content)
        except Exception as e:
            log.error(f"Error loading Markdown file {filepath}: {e}")
            self.editor.setPlainText(f"# Error loading file\n\n{e}")

    def get_content(self) -> str:
        return self.editor.toPlainText()

    def _render_preview(self):
        scroll_max = self.viewer_scrollbar.maximum()
        old_pos_percent = (self.viewer_scrollbar.value() / scroll_max
                           if scroll_max > 0 else 0)
        raw_text = self.editor.toPlainText()
        html = markdown(raw_text,
                        extensions=['fenced_code', 'tables', 'extra',
                                    'sane_lists'])
        self.viewer.setHtml(html)

        def restore_scroll():
            new_max = self.viewer_scrollbar.maximum()
            self.viewer_scrollbar.setValue(int(new_max * old_pos_percent))

        QTimer.singleShot(0, restore_scroll)

    def update_theme(self):
        colors = theme_manager.current_theme_data.get('colors', {})
        font_family = settings_manager.get("font_family", "Consolas")
        font_size = settings_manager.get("font_size", 11)
        font = QFont(font_family, font_size)
        self.editor.setFont(font)
        self.editor.update_line_number_area_width(0)
        editor_bg = colors.get('editor.background', '#2b2b2b')
        editor_fg = colors.get('editor.foreground', '#a9b7c6')
        self.editor.setStyleSheet(
            f"background-color: {editor_bg}; color: {editor_fg}; "
            f"border: none; padding: 0px;")
        self.highlighter.rehighlight_document()
        if self.editor.formatting_toolbar:
            self.editor.formatting_toolbar.update_theme()
        viewer_bg = colors.get('window.background', '#2f383e')
        accent_color = colors.get('accent', '#88c0d0')
        line_highlight_bg = colors.get(
            'editor.lineHighlightBackground', '#323232')
        comment_color = colors.get('syntax.comment', '#808080')
        string_color = colors.get('syntax.string', '#6A8759')
        style_sheet = f"""
            h1, h2, h3, h4, h5, h6 {{
                color: {accent_color};
                border-bottom: 1px solid {line_highlight_bg};
                padding-bottom: 4px; margin-top: 15px;
            }}
            a {{ color: {string_color}; text-decoration: none; }}
            a:hover {{ text-decoration: underline; }}
            p, li {{ font-size: {font_size}pt; }}
            pre {{
                background-color: {editor_bg};
                border: 1px solid {colors.get('input.border', '#555')};
                border-radius: 4px; padding: 10px;
                font-family: "{font_family}";
            }}
            code {{
                background-color: {line_highlight_bg};
                font-family: "{font_family}";
                border-radius: 2px; padding: 2px 4px;
            }}
            blockquote {{
                color: {comment_color};
                border-left: 3px solid {accent_color};
                padding-left: 10px; margin-left: 5px;
            }}
            table {{ border-collapse: collapse; }}
            th, td {{
                border: 1px solid {colors.get('input.border', '#555')};
                padding: 6px;
            }}
            th {{ background-color: {line_highlight_bg}; }}"""
        self.viewer.document().setDefaultStyleSheet(style_sheet)
        default_font = QFont(
            settings_manager.get("font_family", "Arial"), font_size
        )
        self.viewer.document().setDefaultFont(default_font)
        self.viewer.setStyleSheet(
            f"background-color: {viewer_bg}; border:none;")
        self._render_preview()
```

### File: `/plugins/markdown_viewer/markdown_syntax_highlighter.py`

#### Linter Issues Found:
```

- L54 (E501) No message available

- L111 (W292) No message available

```


```python
# /plugins/markdown_viewer/markdown_syntax_highlighter.py
from PyQt6.QtGui import QSyntaxHighlighter, QTextCharFormat, QColor, QFont
from PyQt6.QtCore import QRegularExpression
from app_core.theme_manager import theme_manager


class MarkdownSyntaxHighlighter(QSyntaxHighlighter):
    """
    A syntax highlighter that provides a rich, WYSIWYG-like experience
    for editing Markdown source by visually styling the syntax.
    """
    def __init__(self, parent_document):
        super().__init__(parent_document)
        self.formats = {}
        self.initialize_formats_and_rules()

    def initialize_formats_and_rules(self):
        colors = theme_manager.current_theme_data.get("colors", {})
        editor_bg = QColor(colors.get('editor.background', '#2b2b2b'))

        self.formats['marker'] = QTextCharFormat()
        self.formats['marker'].setForeground(editor_bg.lighter(130))
        self.formats['marker'].setFontWeight(QFont.Weight.Bold)

        self.formats['h1'] = QTextCharFormat()
        self.formats['h1'].setFontPointSize(20)
        self.formats['h1'].setFontWeight(QFont.Weight.Bold)
        self.formats['h1'].setForeground(
            QColor(colors.get('accent', '#88c0d0')))

        self.formats['h2'] = QTextCharFormat()
        self.formats['h2'].setFontPointSize(18)
        self.formats['h2'].setFontWeight(QFont.Weight.Bold)

        self.formats['h3'] = QTextCharFormat()
        self.formats['h3'].setFontPointSize(16)
        self.formats['h3'].setFontWeight(QFont.Weight.Bold)

        self.formats['bold'] = QTextCharFormat()
        self.formats['bold'].setFontWeight(QFont.Weight.Bold)

        self.formats['italic'] = QTextCharFormat()
        self.formats['italic'].setFontItalic(True)

        self.formats['strikethrough'] = QTextCharFormat()
        self.formats['strikethrough'].setFontStrikeOut(True)

        self.formats['code_block'] = QTextCharFormat()
        code_block_bg = colors.get('editor.lineHighlightBackground', '#323232')
        self.formats['code_block'].setBackground(QColor(code_block_bg))
        self.formats['code_block'].setFontFamily("Consolas")

        self.formats['inline_code'] = QTextCharFormat()
        inline_code_bg = colors.get('editor.lineHighlightBackground', '#323232')
        inline_code_fg = colors.get('syntax.string', '#a7c080')
        self.formats['inline_code'].setBackground(QColor(inline_code_bg))
        self.formats['inline_code'].setForeground(QColor(inline_code_fg))
        self.formats['inline_code'].setFontFamily("Consolas")

        self.rules = [
            (QRegularExpression(r"^(#{1,3})\s"), self._format_heading),
            (QRegularExpression(r"(\*\*)([^\*]+)(\*\*)"),
             self._format_inline('bold')),
            (QRegularExpression(r"(\*)([^\*]+)(\*)"),
             self._format_inline('italic')),
            (QRegularExpression(r"(`)([^`]+)(`)"),
             self._format_inline('inline_code')),
            (QRegularExpression(r"(~~)([^~]+)(~~)"),
             self._format_inline('strikethrough')),
        ]
        self.code_block_delimiter = QRegularExpression(r"^```")

    def _format_heading(self, match):
        marker = match.captured(1)
        level = len(marker)
        self.setFormat(
            match.capturedStart(1), len(marker), self.formats['marker'])
        self.setFormat(match.capturedEnd(1), self.currentBlock().length(),
                       self.formats[f'h{level}'])

    def _format_inline(self, fmt_name):
        def formatter(match):
            self.setFormat(match.capturedStart(1), len(match.captured(1)),
                           self.formats['marker'])
            self.setFormat(match.capturedStart(3), len(match.captured(3)),
                           self.formats['marker'])
            self.setFormat(match.capturedStart(2), len(match.captured(2)),
                           self.formats[fmt_name])
        return formatter

    def highlightBlock(self, text: str):
        if (self.code_block_delimiter.match(text).hasMatch() or
                self.previousBlockState() == 1):
            self.setFormat(0, len(text), self.formats['code_block'])
            in_code_block = True

            if (self.code_block_delimiter.match(text).hasMatch() and
                    self.previousBlockState() == 1):
                in_code_block = False

            self.setCurrentBlockState(1 if in_code_block else 0)
            return

        for pattern, formatter in self.rules:
            iterator = pattern.globalMatch(text)
            while iterator.hasNext():
                formatter(iterator.next())

    def rehighlight_document(self):
        self.initialize_formats_and_rules()
        super().rehighlight()
```

### File: `/plugins/markdown_viewer/markdown_widget.py`

#### Linter Issues Found:
```

- L110 (W292) No message available

```


```python
# /plugins/markdown_viewer/markdown_widget.py
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTextBrowser
from PyQt6.QtGui import QFont
from markdown import markdown
from app_core.theme_manager import theme_manager
from app_core.settings_manager import settings_manager
from utils.logger import log


class MarkdownViewerWidget(QWidget):
    """
    A widget that displays rendered Markdown content.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.filepath = None

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)

        self.browser = QTextBrowser()
        self.browser.setOpenExternalLinks(True)
        self.layout.addWidget(self.browser)

        self.update_theme()

    def load_markdown_file(self, filepath: str):
        """Reads a .md file and renders its content."""
        self.filepath = filepath
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                md_text = f.read()
            # Convert Markdown to HTML
            html = markdown(md_text, extensions=['fenced_code', 'tables'])
            self.browser.setHtml(html)
        except FileNotFoundError:
            msg = f"<h1>Error</h1><p>File not found: {filepath}</p>"
            self.browser.setHtml(msg)
        except Exception as e:
            log.error(f"Error reading/rendering Markdown file {filepath}: {e}")
            msg = f"<h1>Error</h1><p>Could not render file: {e}</p>"
            self.browser.setHtml(msg)

    def set_markdown_content(self, md_text: str):
        """Sets the content from a string directly."""
        html = markdown(md_text, extensions=['fenced_code', 'tables'])
        self.browser.setHtml(html)

    def update_theme(self):
        """Applies colors and fonts from the current theme."""
        colors = theme_manager.current_theme_data.get('colors', {})
        font_family = settings_manager.get("font_family", "Consolas")
        font_size = settings_manager.get("font_size", 11)

        # Base styles
        bg_color = colors.get('editor.background', '#2b2b2b')
        fg_color = colors.get('editor.foreground', '#a9b7c6')
        accent_color = colors.get('accent', '#88c0d0')
        line_highlight_bg = colors.get(
            'editor.lineHighlightBackground', '#323232')
        comment_color = colors.get('syntax.comment', '#808080')
        string_color = colors.get('syntax.string', '#6A8759')

        style_sheet = f"""
        QTextBrowser {{
            background-color: {bg_color};
            color: {fg_color};
            border: none;
            padding: 10px;
        }}
        h1, h2, h3, h4, h5, h6 {{
            color: {accent_color};
            border-bottom: 1px solid {line_highlight_bg};
            padding-bottom: 4px;
            margin-top: 15px;
        }}
        a {{
            color: {string_color};
            text-decoration: none;
        }}
        a:hover {{
            text-decoration: underline;
        }}
        p, li {{
            font-size: {font_size}pt;
        }}
        pre {{
            background-color: {line_highlight_bg};
            border: 1px solid {colors.get('input.border', '#555')};
            border-radius: 4px;
            padding: 10px;
            font-family: "{font_family}";
        }}
        code {{
            background-color: {line_highlight_bg};
            font-family: "{font_family}";
            border-radius: 2px;
            padding: 2px 4px;
        }}
        blockquote {{
            color: {comment_color};
            border-left: 3px solid {accent_color};
            padding-left: 10px;
            margin-left: 5px;
        }}
        """
        self.browser.document().setDefaultStyleSheet(style_sheet)
        self.browser.document().setDefaultFont(QFont(font_family, font_size))
        # We have to reload the content for the stylesheet to apply
        self.browser.reload()
```

### File: `/plugins/markdown_viewer/plugin.json`

```json
{
    "id": "markdown_viewer",
    "name": "Markdown Viewer",
    "author": "AI Assistant",
    "version": "1.0.1",
    "description": "Adds support for viewing rendered Markdown (.md) files in a separate tab. It intercepts file open calls to provide a rich text view instead of a plain text editor for .md files.",
    "entry_point": "plugin_main.py"
}
```

### File: `/plugins/markdown_viewer/plugin_main.py`

#### Linter Issues Found:
```

- L40 (E501) No message available

- L68 (W292) No message available

```


```python
# /plugins/markdown_viewer/plugin_main.py
import os
from .markdown_editor_widget import MarkdownEditorWidget
from utils.logger import log


class MarkdownPlugin:
    """
    Manages the lifecycle and functionality of the Markdown Editor plugin.
    This version uses the file opener hook to handle .md files.
    """

    def __init__(self, main_window):
        self.main_window = main_window
        self.api = main_window.puffin_api

        # Register this plugin as the handler for .md files
        self.api.register_file_opener('.md', self.open_markdown_file)
        log.info("Markdown Editor: Registered as handler for .md files.")

    def open_markdown_file(self, filepath: str):
        """
        Callback function to open a .md file in the custom editor.
        This is called by MainWindow when a .md file is opened.
        """
        log.info(f"Markdown Editor: Handling request to open '{filepath}'.")

        # Check if this file is already open in a viewer
        for i in range(self.main_window.tab_widget.count()):
            widget = self.main_window.tab_widget.widget(i)
            if (isinstance(widget, MarkdownEditorWidget) and
                    widget.filepath == filepath):
                self.main_window.tab_widget.setCurrentIndex(i)
                return

        # If a placeholder "Welcome" tab exists, remove it
        if self.main_window.tab_widget.count() == 1:
            current_widget = self.main_window.tab_widget.widget(0)
            is_placeholder = (hasattr(current_widget, 'objectName') and
                              current_widget.objectName() == "PlaceholderLabel")
            if is_placeholder:
                self.main_window.tab_widget.removeTab(0)

        editor = MarkdownEditorWidget(self.main_window)
        editor.load_file(filepath)
        # Connect editor's signal to the main window's handler
        editor.content_changed.connect(self.main_window._on_content_changed)

        tab_name = os.path.basename(filepath)
        index = self.main_window.tab_widget.addTab(editor, tab_name)
        self.main_window.tab_widget.setTabToolTip(index, filepath)
        self.main_window.tab_widget.setCurrentIndex(index)
        self.main_window.tab_widget.setTabsClosable(True)


def initialize(main_window):
    """
    Entry point function for PuffinPyEditor to load the plugin.
    """
    try:
        plugin_instance = MarkdownPlugin(main_window)
        log.info("Markdown Editor Plugin initialized successfully.")
        return plugin_instance
    except Exception as e:
        log.error(
            f"Failed to initialize Markdown Editor Plugin: {e}", exc_info=True
        )
        return None
```

### File: `/plugins/plugin_publisher/__init__.py`

```python

```

### File: `/plugins/plugin_publisher/plugin.json`

```json
{
    "id": "plugin_publisher",
    "name": "Plugin Publisher",
    "author": "AI Assistant",
    "version": "1.0.0",
    "description": "Provides a tool to package and publish installed plugins to a specified GitHub distribution repository. Manages versioning and updates the repository's index.json.",
    "entry_point": "plugin_main.py"
}
```

### File: `/plugins/plugin_publisher/plugin_main.py`

#### Linter Issues Found:
```

- L69 (W292) No message available

```


```python
# PuffinPyEditor/plugins/plugin_publisher/plugin_main.py
from .publish_dialog import PublishDialog


class PluginPublisherPlugin:
    """
    Integrates the plugin publishing tool into the main application UI.
    """

    def __init__(self, main_window):
        self.main_window = main_window
        self.api = main_window.puffin_api
        self.publish_dialog = None

        # Add the action to the "Tools" menu
        self.publish_action = self.api.add_menu_action(
            menu_name="tools",
            text="Publish Plugin...",
            callback=self.show_publish_dialog,
            icon_name="fa5s.cloud-upload-alt"
        )
        self.update_action_state()

        # Connect to the github manager's auth signal to update action state
        github_manager = self.api.get_manager("github")
        github_manager.auth_successful.connect(
            lambda user: self.update_action_state())
        github_manager.auth_failed.connect(
            lambda err: self.update_action_state())

    def show_publish_dialog(self):
        """
        Checks for authentication and then shows the publishing dialog.
        """
        github_manager = self.api.get_manager("github")
        if not github_manager or not github_manager.get_authenticated_user():
            self.api.show_message(
                "warning",
                "Login Required",
                "You must be logged into GitHub to publish a plugin. "
                "Please log in via Preferences > Source Control."
            )
            return

        # Lazily create the dialog instance
        if self.publish_dialog is None or not self.publish_dialog.isVisible():
            self.publish_dialog = PublishDialog(self.api, self.main_window)
            self.publish_dialog.show()
        else:
            self.publish_dialog.raise_()
            self.publish_dialog.activateWindow()

    def update_action_state(self):
        """
        Enables or disables the menu action based on GitHub login status.
        """
        github_manager = self.api.get_manager("github")
        if github_manager:
            is_logged_in = bool(github_manager.get_authenticated_user())
            self.publish_action.setEnabled(is_logged_in)
            tooltip = ("Upload an installed plugin to your distribution repo."
                       if is_logged_in else
                       "Log in to GitHub in Preferences to use this feature.")
            self.publish_action.setToolTip(tooltip)


def initialize(main_window):
    """Entry point for PuffinPyEditor to initialize the plugin."""
    return PluginPublisherPlugin(main_window)
```

### File: `/plugins/plugin_publisher/publish_dialog.py`

#### Linter Issues Found:
```

- L18 (E501) No message available

- L49 (E501) No message available

- L50 (E501) No message available

- L61 (E501) No message available

- L72 (E501) No message available

- L117 (E501) No message available

- L151 (E501) No message available

- L301 (E501) No message available

- L341 (E501) No message available

- L432 (E501) No message available

- L487 (E501) No message available

- L532 (E501) No message available

- L557 (E501) No message available

- L568 (E501) No message available

- L592 (E501) No message available

- L623 (E501) No message available

- L630 (E501) No message available

- L632 (E501) No message available

- L634 (E501) No message available

- L641 (E501) No message available

- L642 (W292) No message available

```


```python
# PuffinPyEditor/plugins/plugin_publisher/publish_dialog.py
import os
import shutil
import tempfile
import json
import copy
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QFormLayout, QComboBox,
                             QTextEdit, QPushButton, QDialogButtonBox, QLabel,
                             QMessageBox, QHBoxLayout, QListWidget,
                             QListWidgetItem, QRadioButton, QGroupBox,
                             QLineEdit)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

# --- Content for auto-initializing a distro repo ---
README_CONTENT = """# PuffinPyEditor Plugin Distribution Repository
This repository is structured to serve plugins for the PuffinPyEditor.
- `index.json`: A manifest file listing all available plugins and their download URLs.
- `zips/`: This directory contains the packaged `.zip` files for each plugin.
To publish a new version of a plugin, use the "Publish Plugin" tool inside
PuffinPyEditor.
"""
GITIGNORE_CONTENT = """# Ignore common temp files
*.tmp, *.bak, *~
# Ignore local environment
venv/, .venv/
"""


def _bump_version(version_str, level='patch'):
    """Bumps a semantic version string."""
    try:
        parts = version_str.split('.')
        if len(parts) != 3 or not all(p.isdigit() for p in parts):
            return version_str
        major, minor, patch = [int(p) for p in parts]
        if level == 'patch':
            patch += 1
        elif level == 'minor':
            minor, patch = minor + 1, 0
        elif level == 'major':
            major, minor, patch = major + 1, 0, 0
        return f"{major}.{minor}.{patch}"
    except Exception:
        return version_str


class VersionConflictDialog(QDialog):
    """Dialog to resolve a version conflict by overwriting or creating a new version."""
    def __init__(self, plugin_name, local_version, remote_version, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Version Conflict")
        self.result = (None, None)  # (action, version)
        self.local_version = local_version

        layout = QVBoxLayout(self)
        msg = f"A version conflict was detected for <b>{plugin_name}</b>."
        layout.addWidget(QLabel(msg))

        info_layout = QFormLayout()
        info_layout.addRow("Your local version:", QLabel(f"<b>{local_version}</b>"))
        info_layout.addRow("Version in repository:",
                           QLabel(f"<b>{remote_version}</b>"))
        layout.addLayout(info_layout)

        group = QGroupBox("Choose an action:")
        group_layout = QVBoxLayout(group)

        self.overwrite_radio = QRadioButton(
            f"Overwrite with version {local_version}")
        self.new_version_radio = QRadioButton("Create a new version:")
        self.new_version_edit = QLineEdit(_bump_version(remote_version, 'patch'))

        new_version_layout = QHBoxLayout()
        new_version_layout.addWidget(self.new_version_radio)
        new_version_layout.addWidget(self.new_version_edit)

        group_layout.addWidget(self.overwrite_radio)
        group_layout.addLayout(new_version_layout)
        self.new_version_radio.setChecked(True)
        self.overwrite_radio.toggled.connect(self.toggle_line_edit)
        layout.addWidget(group)

        buttons = (QDialogButtonBox.StandardButton.Ok |
                   QDialogButtonBox.StandardButton.Cancel)
        button_box = QDialogButtonBox(buttons)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        self.toggle_line_edit(True)

    def toggle_line_edit(self, checked):
        self.new_version_edit.setEnabled(self.new_version_radio.isChecked())

    def accept(self):
        if self.overwrite_radio.isChecked():
            self.result = ('overwrite', self.local_version)
        elif self.new_version_radio.isChecked():
            new_version = self.new_version_edit.text().strip()
            if not new_version:
                QMessageBox.warning(self, "Invalid Version",
                                    "New version cannot be empty.")
                return
            self.result = ('new', new_version)
        super().accept()


class BumpVersionDialog(QDialog):
    """Dialog to ask the user how to bump the version of a new plugin."""
    def __init__(self, current_version, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Set Initial Version")
        self.current_version = current_version
        self.new_version = current_version

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Publishing a new plugin with initial version:"))

        group = QGroupBox("Choose version:")
        group_layout = QVBoxLayout(group)

        self.radios = {
            'none': QRadioButton(f"Keep current version ({current_version})"),
            'patch': QRadioButton(
                f"Patch -> {_bump_version(current_version, 'patch')}"),
            'minor': QRadioButton(
                f"Minor -> {_bump_version(current_version, 'minor')}"),
            'major': QRadioButton(
                f"Major -> {_bump_version(current_version, 'major')}")
        }

        self.radios['none'].setChecked(True)
        for radio in self.radios.values():
            group_layout.addWidget(radio)

        layout.addWidget(group)

        buttons = (QDialogButtonBox.StandardButton.Ok |
                   QDialogButtonBox.StandardButton.Cancel)
        button_box = QDialogButtonBox(buttons)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

    def accept(self):
        for level, radio in self.radios.items():
            if radio.isChecked():
                if level == 'none':
                    self.new_version = self.current_version
                else:
                    self.new_version = _bump_version(self.current_version, level)
                break
        super().accept()


class MultiPublishSelectionDialog(QDialog):
    """A dialog to select which plugins to include in a batch publish."""
    def __init__(self, plugins, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Select Plugins to Publish")
        self.setMinimumSize(400, 300)
        layout = QVBoxLayout(self)

        layout.addWidget(QLabel("Select plugins to include in this batch:"))
        self.list_widget = QListWidget()
        for plugin_data in plugins:
            display = (f"{plugin_data.get('name', 'Unknown')} "
                       f"v{plugin_data.get('version', '0.0.0')}")
            item = QListWidgetItem(display)
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            item.setCheckState(Qt.CheckState.Checked)
            item.setData(Qt.ItemDataRole.UserRole, plugin_data)
            self.list_widget.addItem(item)
        layout.addWidget(self.list_widget)

        buttons = (QDialogButtonBox.StandardButton.Ok |
                   QDialogButtonBox.StandardButton.Cancel)
        button_box = QDialogButtonBox(buttons)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

    def get_selected_plugins(self):
        selected = []
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            if item.checkState() == Qt.CheckState.Checked:
                selected.append(item.data(Qt.ItemDataRole.UserRole))
        return selected


class PublishDialog(QDialog):
    """A dialog to manage the process of publishing a plugin."""

    def __init__(self, api, parent):
        super().__init__(parent)
        self.api = api
        self.git_manager = api.get_manager("git")
        self.github_manager = api.get_manager("github")
        self.plugin_manager = api.get_manager("plugin")
        self.settings = api.get_manager("settings")
        self.publish_queue = []
        self._temp_dir = None
        self._current_step = None
        self.cloned_repo_path = None
        self.auto_increment_choice = False

        self.setWindowTitle("Publish a Plugin")
        self.setMinimumSize(600, 450)
        self._setup_ui()
        self._connect_ui_signals()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        form_layout = QFormLayout()

        self.plugin_selector = QComboBox()
        form_layout.addRow("Plugin to Publish:", self.plugin_selector)

        repo_layout = QHBoxLayout()
        repo_layout.setContentsMargins(0, 0, 0, 0)
        self.repo_combo = QComboBox()
        self.manage_repos_button = QPushButton("Manage...")
        repo_layout.addWidget(self.repo_combo, 1)
        repo_layout.addWidget(self.manage_repos_button)
        form_layout.addRow("Target Repository:", repo_layout)

        self.commit_message = QTextEdit()
        self.commit_message.setFixedHeight(80)
        form_layout.addRow("Commit Message:", self.commit_message)
        layout.addLayout(form_layout)

        layout.addWidget(QLabel("Log:"))
        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        self.log_output.setFont(QFont("Consolas", 9))
        self.log_output.setStyleSheet(
            "background-color: #1E1E1E; color: #D4D4D4;")
        layout.addWidget(self.log_output, 1)

        self.button_box = QDialogButtonBox()
        self.publish_button = self.button_box.addButton(
            "Publish Selected", QDialogButtonBox.ButtonRole.AcceptRole)
        self.auto_publish_button = self.button_box.addButton(
            "Publish Multiple...", QDialogButtonBox.ButtonRole.ActionRole)
        self.close_button = self.button_box.addButton(
            "Close", QDialogButtonBox.ButtonRole.RejectRole)
        layout.addWidget(self.button_box)

    def _connect_ui_signals(self):
        self.publish_button.clicked.connect(self._start_single_publish_flow)
        self.auto_publish_button.clicked.connect(self._start_auto_publish_flow)
        self.close_button.clicked.connect(self.reject)
        self.manage_repos_button.clicked.connect(self._open_preferences)
        self.plugin_selector.currentIndexChanged.connect(
            self._on_plugin_selected)

    def _open_preferences(self):
        self.api.get_main_window()._action_open_preferences()

    def _set_ui_locked(self, locked: bool):
        self.publish_button.setEnabled(not locked)
        self.auto_publish_button.setEnabled(not locked)
        self.plugin_selector.setEnabled(not locked)
        self.repo_combo.setEnabled(not locked)
        self.commit_message.setEnabled(not locked)
        self.manage_repos_button.setEnabled(not locked)
        self.close_button.setText("Cancel" if locked else "Close")

    def _add_log(self, message, is_error=False, is_warning=False):
        color = ("#FF5555" if is_error else
                 "#FFC66D" if is_warning else "#A9B7C6")
        self.log_output.append(
            f"<span style='color: {color};'>{message}</span>")
        self.api.log_info(f"[Plugin Publisher] {message}")

    def showEvent(self, event):
        super().showEvent(event)
        self._populate_plugins()
        self._populate_repos()
        can_publish = bool(self.repo_combo.count() and
                           self.plugin_selector.count())
        self.publish_button.setEnabled(can_publish)
        self.auto_publish_button.setEnabled(can_publish)
        tooltip = ""
        if not can_publish:
            tooltip = "Configure a distribution repo and select a plugin."
        self.publish_button.setToolTip(tooltip)
        self.auto_publish_button.setToolTip(tooltip)
        self.log_output.clear()

    def _populate_plugins(self):
        self.plugin_selector.clear()
        for plugin in self._get_publishable_plugins():
            display = (f"{plugin.get('name', 'Unknown')} "
                       f"(v{plugin.get('version', '0.0.0')})")
            self.plugin_selector.addItem(display, plugin)
        self._on_plugin_selected()

    def _get_publishable_plugins(self):
        """Gets a list of publishable plugin metadata from the plugin manager."""
        return self.plugin_manager.get_installed_plugins()

    def _populate_repos(self):
        self.repo_combo.clear()
        all_repos = self.settings.get("source_control_repos", [])
        primary_repo_id = self.settings.get("active_update_repo_id")
        primary_idx = -1
        for i, repo_config in enumerate(all_repos):
            repo_path = f"{repo_config.get('owner')}/{repo_config.get('repo')}"
            self.repo_combo.addItem(repo_path, repo_config)
            if repo_config.get('id') == primary_repo_id:
                primary_idx = i
        if primary_idx != -1:
            self.repo_combo.setCurrentIndex(primary_idx)

    def _on_plugin_selected(self, index=0):
        plugin_data = self.plugin_selector.currentData()
        if not plugin_data:
            self.commit_message.clear()
            return

        name = plugin_data.get('name', 'Unknown Plugin')
        version = plugin_data.get('version', '0.0.0')
        commit_msg = f"feat(plugin): Publish {name} v{version}"
        self.commit_message.setText(commit_msg)

    def _cleanup(self, success=True):
        self._set_ui_locked(False)
        self.git_manager.git_success.disconnect(self._on_git_step_success)
        self.git_manager.git_error.disconnect(self._on_publish_failed)
        if self._temp_dir and os.path.exists(self._temp_dir):
            shutil.rmtree(self._temp_dir, ignore_errors=True)
            self._add_log("Cleaned up temporary directory.")
        self._temp_dir = None
        self.cloned_repo_path = None
        self._current_step = None
        self.publish_queue = []

    def _on_publish_failed(self, error_message):
        self._add_log(f"FAILED on step '{self._current_step}': {error_message}",
                      is_error=True)
        self._cleanup(success=False)

    def _start_single_publish_flow(self):
        plugin_data = self.plugin_selector.currentData()
        if not plugin_data:
            QMessageBox.warning(self, "No Plugin Selected",
                                "Please select a plugin.")
            return

        publish_item = {
            "original_data": plugin_data,
            "run_data": copy.deepcopy(plugin_data)
        }
        self.auto_increment_choice = False
        self._start_publish_flow([publish_item])

    def _start_auto_publish_flow(self):
        all_plugins = self._get_publishable_plugins()
        if not all_plugins:
            QMessageBox.information(self, "No Plugins",
                                    "No publishable plugins found.")
            return

        dialog = MultiPublishSelectionDialog(all_plugins, self)
        if not dialog.exec():
            return

        plugins_to_publish = dialog.get_selected_plugins()
        if not plugins_to_publish:
            QMessageBox.information(self, "No Selection",
                                    "No plugins were selected.")
            return

        reply = QMessageBox.question(
            self, "Auto-increment Versions?",
            "Do you want to automatically increment the patch version for "
            "plugins that are not newer than the repository version?",
            (QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No |
             QMessageBox.StandardButton.Cancel),
            QMessageBox.StandardButton.Yes)

        if reply == QMessageBox.StandardButton.Cancel:
            return

        self.auto_increment_choice = (reply == QMessageBox.StandardButton.Yes)
        publish_list = [{"original_data": p, "run_data": copy.deepcopy(p)}
                        for p in plugins_to_publish]
        self._start_publish_flow(publish_list)

    def _start_publish_flow(self, publish_list):
        repo_data = self.repo_combo.currentData()
        if not repo_data:
            QMessageBox.warning(self, "Missing Repository",
                                "Please select a distribution repository.")
            return

        commit_text = self.commit_message.toPlainText().strip()
        if len(publish_list) == 1 and not commit_text:
            QMessageBox.warning(self, "Missing Commit Message",
                                "Please provide a commit message.")
            return

        self.publish_queue = publish_list
        owner = repo_data.get('owner')
        repo = repo_data.get('repo')
        self.distro_repo_path = f"{owner}/{repo}"

        self._set_ui_locked(True)
        self.log_output.clear()
        self._add_log("Starting plugin publication process...")
        self._temp_dir = tempfile.mkdtemp(prefix="puffin-plugin-publish-")
        self.git_manager.git_success.connect(self._on_git_step_success)
        self.git_manager.git_error.connect(self._on_publish_failed)
        self._current_step = "CLONE"
        self._add_log(f"Cloning '{self.distro_repo_path}'...")
        repo_url = f"https://github.com/{self.distro_repo_path}.git"
        self.git_manager.clone_repo(repo_url, self._temp_dir)

    def _on_git_step_success(self, message: str, data: dict):
        if self._current_step == "CLONE":
            self.cloned_repo_path = data.get("path")
            self._add_log("Successfully cloned repository.")
            index_json_path = os.path.join(self.cloned_repo_path, "index.json")

            if not os.path.exists(index_json_path):
                self._current_step = "INITIALIZE_COMMIT"
                self._add_log("Empty repo detected. Initializing structure...")
                self._initialize_distro_repo()
                commit_msg = "ci: Initialize plugin distribution repository"
                self.git_manager.commit_files(self.cloned_repo_path, commit_msg)
            else:
                self._process_publish_queue()

        elif self._current_step == "INITIALIZE_COMMIT":
            self._add_log("Initial commit successful.")
            self._process_publish_queue()

        elif self._current_step == "PUBLISH_COMMIT":
            self._add_log(f"Commit successful. {message}")
            self._current_step = "PUSH"
            self._add_log(f"Pushing changes to '{self.distro_repo_path}'...")
            self.git_manager.push(self.cloned_repo_path)

        elif self._current_step == "PUSH":
            self._add_log("Push successful!")
            for item in self.publish_queue:
                original_version = item["original_data"].get("version")
                new_version = item["run_data"].get("version")
                if new_version != original_version:
                    self._update_local_plugin_json(item["original_data"],
                                                   new_version)

            self._add_log("\n--- PUBLICATION COMPLETE ---")
            self._cleanup(success=True)
            self._populate_plugins()

    def _process_publish_queue(self):
        self._current_step = "PROCESS_PLUGINS"
        is_batch = len(self.publish_queue) > 1
        index_path = os.path.join(self.cloned_repo_path, 'index.json')
        index_data = []
        try:
            if os.path.exists(index_path):
                with open(index_path, 'r', encoding='utf-8') as f:
                    index_data = json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            self._on_publish_failed(f"Failed to load or parse index.json: {e}")
            return

        processed_items = []
        for item in self.publish_queue:
            plugin_data = item["run_data"]
            plugin_name = plugin_data.get('name', 'Unknown')
            self._add_log(f"--- Processing {plugin_name} ---")
            try:
                should_publish, final_version = self._check_version(
                    item, index_data, batch_mode=is_batch)

                if should_publish:
                    item['run_data']['version'] = final_version
                    self._package_plugin(item['run_data'])
                    self._update_index_data(item['run_data'], index_data)
                    processed_items.append(item)
                else:
                    self._add_log(f"Skipping '{plugin_name}'.", is_warning=True)
            except FileNotFoundError as e:
                self._add_log(f"ERROR for '{plugin_name}': {e}. Skipping.",
                              is_error=True)
            except Exception as e:
                msg = f"UNEXPECTED ERROR for '{plugin_name}': {e}. Skipping."
                self._add_log(msg, is_error=True)

        self.publish_queue = processed_items
        if not self.publish_queue:
            msg = "No plugins processed for publication. Nothing to commit."
            self._add_log(msg, is_warning=True)
            self._cleanup()
            return

        try:
            with open(index_path, 'w', encoding='utf-8') as f:
                json.dump(index_data, f, indent=4)
        except IOError as e:
            self._on_publish_failed(f"Failed to write updated index.json: {e}")
            return

        commit_msg = self.commit_message.toPlainText()
        if is_batch:
            count = len(self.publish_queue)
            plural = 's' if count > 1 else ''
            commit_msg = f"feat(plugins): Update {count} plugin{plural}"
        elif len(self.publish_queue) == 1:
            p_data = self.publish_queue[0]['run_data']
            p_name = p_data.get('name', 'Unknown')
            p_ver = p_data.get('version', '0.0.0')
            commit_msg = f"feat(plugin): Publish {p_name} v{p_ver}"
        self.commit_message.setText(commit_msg)

        count = len(self.publish_queue)
        self._add_log(f"Committing updates for {count} plugin(s)...")
        self._current_step = "PUBLISH_COMMIT"
        self.git_manager.commit_files(self.cloned_repo_path, commit_msg)

    def _check_version(self, publish_item, index_data, batch_mode=False):
        local_data = publish_item['original_data']
        local_version = local_data.get('version', '0.0.0')
        plugin_id = local_data.get('id')
        plugin_name = local_data.get('name', 'Unknown')

        old_entry = next((p for p in index_data if p.get('id') == plugin_id), None)

        if not old_entry:
            self._add_log(f"New plugin '{plugin_id}'.")
            if not batch_mode:
                dialog = BumpVersionDialog(local_version, self)
                if dialog.exec():
                    self._add_log(f"User selected initial version "
                                  f"{dialog.new_version}.")
                    return True, dialog.new_version
                return False, None
            return True, local_version

        remote_version = old_entry.get('version')
        if not remote_version:
            return True, local_version

        if local_version > remote_version:
            self._add_log(f"Newer version found: {remote_version} -> "
                          f"{local_version}.")
            return True, local_version

        if batch_mode:
            if self.auto_increment_choice:
                new_version = _bump_version(remote_version, 'patch')
                self._add_log(f"Auto-incrementing version: {remote_version} -> "
                              f"{new_version}.")
                return True, new_version
            else:
                return False, None

        dialog = VersionConflictDialog(
            plugin_name, local_version, remote_version, self)
        if dialog.exec():
            action, version = dialog.result
            if action:
                self._add_log(f"User chose to '{action}' with version {version}.")
                return True, version

        return False, None

    def _package_plugin(self, plugin_data):
        plugin_id = plugin_data.get('id')
        plugin_source_path = plugin_data.get('path')

        if not plugin_source_path or not os.path.isdir(plugin_source_path):
            raise FileNotFoundError(
                f"Source directory for '{plugin_id}' not found in metadata")

        zips_dir = os.path.join(self.cloned_repo_path, 'zips')
        os.makedirs(zips_dir, exist_ok=True)
        final_zip_path = os.path.join(zips_dir, f"{plugin_id}.zip")

        self._add_log(f"Packaging '{plugin_id}' to zip from "
                      f"'{plugin_source_path}'...")
        shutil.make_archive(os.path.splitext(final_zip_path)[0], 'zip',
                            plugin_source_path)

    def _update_index_data(self, plugin_data, index_data):
        plugin_id = plugin_data.get('id')
        rel_zip_path = os.path.join('zips', f"{plugin_id}.zip").replace("\\", "/")
        download_url = (f"https://raw.githubusercontent.com/"
                        f"{self.distro_repo_path}/main/{rel_zip_path}")

        new_entry = {k: plugin_data.get(k) for k in
                     ('id', 'name', 'author', 'version', 'description')}
        new_entry['download_url'] = download_url

        index_data[:] = [entry for entry in index_data
                         if entry.get('id') != plugin_id]
        index_data.append(new_entry)
        self._add_log(f"Updated index for '{plugin_id}'.")

    def _update_local_plugin_json(self, plugin_data, new_version):
        plugin_id = plugin_data.get('id')
        self._add_log(f"Updating local plugin.json for '{plugin_id}' to "
                      f"v{new_version}")
        try:
            plugin_source_path = plugin_data.get('path')
            if not plugin_source_path:
                raise FileNotFoundError(
                    f"Source path for {plugin_id} not found in metadata.")

            json_file_path = os.path.join(plugin_source_path, 'plugin.json')

            with open(json_file_path, 'r+', encoding='utf-8') as f:
                plugin_json = json.load(f)
                plugin_json['version'] = new_version
                f.seek(0)
                json.dump(plugin_json, f, indent=4)
                f.truncate()
            self._add_log(f"Successfully updated local version for {plugin_id}.")
        except Exception as e:
            self._add_log(f"Could not update local plugin.json for "
                          f"{plugin_id}: {e}", is_error=True)

    def _initialize_distro_repo(self):
        try:
            with open(os.path.join(self.cloned_repo_path, 'index.json'), 'w') as f:
                json.dump([], f, indent=4)
            with open(os.path.join(self.cloned_repo_path, 'README.md'), 'w') as f:
                f.write(README_CONTENT)
            with open(os.path.join(self.cloned_repo_path, '.gitignore'), 'w') as f:
                f.write(GITIGNORE_CONTENT)
            zips_dir = os.path.join(self.cloned_repo_path, 'zips')
            os.makedirs(zips_dir, exist_ok=True)
            with open(os.path.join(zips_dir, '.gitkeep'), 'w') as f:
                pass
        except Exception as e:
            self._on_publish_failed(f"Error initializing distro repo files: {e}")
            raise
```

### File: `/plugins/python_runner/code_runner.py`

#### Linter Issues Found:
```

- L34 (E501) No message available

- L87 (E501) No message available

- L95 (E501) No message available

- L118 (E501) No message available

- L134 (E501) No message available

- L141 (E501) No message available

- L143 (E501) No message available

- L145 (E501) No message available

- L151 (E501) No message available

- L156 (E501) No message available

- L159 (E501) No message available

- L160 (E501) No message available

- L171 (E501) No message available

- L174 (W292) No message available

```


```python
# PuffinPyEditor/plugins/python_runner/code_runner.py
import os
import sys
import shutil
from PyQt6.QtCore import QObject, pyqtSignal, QProcess
from app_core.settings_manager import settings_manager
from utils.logger import log
from typing import Optional


def _find_python_interpreter() -> str:
    """
    Intelligently finds the best Python executable for running scripts.
    This prevents the app from trying to execute itself when frozen.

    Priority:
    1. User-defined path in settings.
    2. A 'python.exe' bundled alongside the main PuffinPyEditor.exe.
    3. The python.exe from the current virtual environment (if from source).
    4. The first 'python' found on the system's PATH.

    Returns:
        The path to a suitable Python executable, or an empty string.
    """
    # 1. User-defined path
    user_path = settings_manager.get("python_interpreter_path", "").strip()
    if user_path and os.path.exists(user_path) and \
            "PuffinPyEditor.exe" not in user_path:
        log.info(f"CodeRunner: Using user-defined interpreter: {user_path}")
        return user_path

    # 2. Local python.exe if frozen (e.g., if bundled with the app)
    if getattr(sys, 'frozen', False):
        local_python_path = os.path.join(os.path.dirname(sys.executable), "python.exe")
        if os.path.exists(local_python_path):
            log.info("CodeRunner: Found local python.exe in frozen app dir: "
                     f"{local_python_path}")
            return local_python_path

    # 3. Venv python if running from source
    if not getattr(sys, 'frozen', False):
        # Ensure we don't return the main app if it was launched via a script
        if "PuffinPyEditor.exe" not in sys.executable:
            log.info("CodeRunner: Running from source, using sys.executable: "
                     f"{sys.executable}")
            return sys.executable

    # 4. System PATH python
    system_python = shutil.which("python")
    if system_python and "PuffinPyEditor.exe" not in system_python:
        log.info(f"CodeRunner: Found system python on PATH: {system_python}")
        return system_python

    log.error("CodeRunner: Could not find a suitable Python interpreter.")
    return ""


class CodeRunner(QObject):
    """
    Manages the execution of Python scripts in a separate process.
    """
    output_received = pyqtSignal(str)
    error_received = pyqtSignal(str)
    process_finished = pyqtSignal(int)

    def __init__(self, parent: Optional[QObject] = None):
        super().__init__(parent)
        self.process: Optional[QProcess] = None

    def run_script(self, script_filepath: str):
        """
        Executes a Python script using the configured interpreter.

        Args:
            script_filepath: The absolute path to the Python script to run.
        """
        if not script_filepath or not os.path.exists(script_filepath):
            err_msg = f"Script path is invalid: {script_filepath}"
            log.error(err_msg)
            self.error_received.emit(err_msg + "\n")
            self.process_finished.emit(-1)
            return

        interpreter_path = _find_python_interpreter()

        if not interpreter_path:
            err_msg = ("Could not find a valid Python interpreter.\nPlease set "
                       "a path in Preferences or ensure 'python' is in your "
                       "system PATH.")
            log.error(err_msg)
            self.error_received.emit(err_msg + "\n")
            self.process_finished.emit(-1)
            return

        if self.process and self.process.state() != QProcess.ProcessState.NotRunning:
            warning_msg = "A script is already running. Please wait."
            log.warning(warning_msg)
            self.error_received.emit(f"[INFO] {warning_msg}\n")
            return

        self.process = QProcess()
        self.process.setProgram(interpreter_path)
        self.process.setArguments([script_filepath])

        # Set working dir to script's dir for correct relative imports
        script_dir = os.path.dirname(script_filepath)
        self.process.setWorkingDirectory(script_dir)
        log.info(f"Setting working directory for script to: {script_dir}")

        # Connect signals
        self.process.readyReadStandardOutput.connect(self._handle_stdout)
        self.process.readyReadStandardError.connect(self._handle_stderr)
        self.process.finished.connect(self._handle_finished)
        self.process.errorOccurred.connect(self._handle_process_error)

        log.info(f"Starting script: '{interpreter_path}' '{script_filepath}'")
        self.output_received.emit(
            f"[PuffinPyRun] Executing: {os.path.basename(script_filepath)} ...\n")
        self.process.start()

        if not self.process.waitForStarted(5000):
            err_msg = f"Failed to start process: {self.process.errorString()}"
            log.error(err_msg)
            self.error_received.emit(err_msg + "\n")
            self.process_finished.emit(self.process.exitCode())
            self.process = None  # Clean up the failed process
            return

        pid = self.process.processId() if self.process else 'N/A'
        log.debug(f"Process started successfully (PID: {pid}).")

    def stop_script(self):
        """Terminates the currently running script process."""
        if self.process and self.process.state() != QProcess.ProcessState.NotRunning:
            pid = self.process.processId()
            log.info(f"Attempting to terminate process (PID: {pid}).")
            self.output_received.emit("[PuffinPyRun] Terminating script...\n")
            self.process.terminate()
            # If terminate fails, forcefully kill it
            if not self.process.waitForFinished(1000):
                log.warning(f"Process {pid} did not terminate gracefully, killing.")
                self.process.kill()
                self.output_received.emit("[PuffinPyRun] Script process killed.\n")
            else:
                self.output_received.emit("[PuffinPyRun] Script process terminated.\n")
        else:
            log.info("Stop script requested, but no process is running.")

    def _handle_stdout(self):
        if self.process:
            data = self.process.readAllStandardOutput().data().decode(errors='replace')
            self.output_received.emit(data)

    def _handle_stderr(self):
        if self.process:
            data = self.process.readAllStandardError().data().decode(errors='replace')
            self.error_received.emit(data)

    def _handle_finished(self, exit_code: int, exit_status: QProcess.ExitStatus):
        log.info(f"Script finished. Exit code: {exit_code}, Status: {exit_status.name}")
        if exit_status == QProcess.ExitStatus.CrashExit:
            self.error_received.emit("[PuffinPyRun] Script process crashed.\n")

        self.output_received.emit(
            f"[PuffinPyRun] Process finished with exit code {exit_code}.\n")
        self.process_finished.emit(exit_code)
        self.process = None  # Clean up after finishing

    def _handle_process_error(self, error: QProcess.ProcessError):
        if self.process:
            err_msg = f"[PuffinPyRun] QProcess Error: {self.process.errorString()} " \
                      f"(Code: {error.name})"
            log.error(err_msg)
            self.error_received.emit(err_msg + "\n")
```

### File: `/plugins/python_runner/output_panel.py`

#### Linter Issues Found:
```

- L2 (E501) No message available

- L41 (E501) No message available

- L63 (E127) No message available

- L63 (E501) No message available

- L63 (W292) No message available

```


```python
# PuffinPyEditor/plugins/python_runner/output_panel.py
from PyQt6.QtWidgets import QDockWidget, QTextEdit, QVBoxLayout, QWidget, QPushButton, QHBoxLayout
from PyQt6.QtGui import QFont, QColor
from PyQt6.QtCore import Qt
from app_core.settings_manager import settings_manager
from app_core.theme_manager import theme_manager


class OutputPanel(QDockWidget):
    def __init__(self, parent=None):
        super().__init__("Output", parent)
        self.setObjectName("OutputPanelDock")
        self.setAllowedAreas(Qt.DockWidgetArea.BottomDockWidgetArea |
                             Qt.DockWidgetArea.RightDockWidgetArea)

        self.container_widget = QWidget()
        self.layout = QVBoxLayout(self.container_widget)
        self.layout.setContentsMargins(2, 2, 2, 2)

        self.control_bar_layout = QHBoxLayout()
        self.clear_button = QPushButton("Clear")
        self.clear_button.clicked.connect(self.clear_output)
        self.control_bar_layout.addWidget(self.clear_button)
        self.control_bar_layout.addStretch(1)
        self.layout.addLayout(self.control_bar_layout)

        self.output_text_edit = QTextEdit()
        self.output_text_edit.setReadOnly(True)
        self.layout.addWidget(self.output_text_edit)

        self.container_widget.setLayout(self.layout)
        self.setWidget(self.container_widget)

        self.update_theme()

    def append_output(self, text: str, is_error: bool = False):
        original_text_color = self.output_text_edit.textColor()
        if is_error:
            colors = theme_manager.current_theme_data.get("colors", {})
            error_color_hex = colors.get("syntax.comment", "#FF4444")
            error_color = QColor(error_color_hex if error_color_hex else "#FF0000")
            self.output_text_edit.setTextColor(error_color)

        self.output_text_edit.append(text.strip())
        if is_error:
            self.output_text_edit.setTextColor(original_text_color)
        scrollbar = self.output_text_edit.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def clear_output(self):
        self.output_text_edit.clear()

    def update_theme(self):
        font_family = settings_manager.get("font_family", "Consolas")
        font_size = settings_manager.get("font_size", 10)
        font = QFont(font_family, font_size)
        self.output_text_edit.setFont(font)

        colors = theme_manager.current_theme_data.get("colors", {})
        bg_color = colors.get("editor.background", "#1e1e1e")
        fg_color = colors.get("editor.foreground", "#d4d4d4")
        self.output_text_edit.setStyleSheet(f"background-color: {bg_color}; "
                                              f"color: {fg_color}; border: none;")
```

### File: `/plugins/python_runner/plugin.json`

```json
{
    "id": "python_runner",
    "name": "Python Runner",
    "author": "PuffinPy Team",
    "version": "1.1.1",
    "description": "Adds functionality to run Python scripts (F5).",
    "entry_point": "plugin_main.py"
}
```

### File: `/plugins/python_runner/plugin_main.py`

#### Linter Issues Found:
```

- L22 (E501) No message available

- L25 (E501) No message available

- L27 (E501) No message available

- L28 (E501) No message available

- L35 (E501) No message available

- L39 (E501) No message available

- L45 (E501) No message available

- L54 (E501) No message available

- L58 (E501) No message available

- L68 (E501) No message available

- L74 (W292) No message available

```


```python
# PuffinPyEditor/plugins/python_runner/plugin_main.py
import os
from PyQt6.QtWidgets import QMessageBox
from PyQt6.QtCore import Qt, QObject
from ui.editor_widget import EditorWidget
from .output_panel import OutputPanel
from .code_runner import CodeRunner


class PythonRunnerPlugin(QObject):
    def __init__(self, main_window):
        super().__init__()
        self.api = main_window.puffin_api
        self.main_window = self.api.get_main_window()
        self.code_runner = CodeRunner(self)
        self.output_panel = OutputPanel(self.main_window)
        self._setup_ui()
        self._connect_signals()

    def _setup_ui(self):
        self.api.register_dock_panel(
            self.output_panel, "Output", Qt.DockWidgetArea.BottomDockWidgetArea, 'fa5s.terminal'
        )
        self.run_action = self.api.add_menu_action("run", "Run Script",
                                                   self._run_script, "F5", 'fa5s.play')
        self.stop_action = self.api.add_menu_action("run", "Stop Script",
                                                    self.code_runner.stop_script,
                                                    "Ctrl+F5", 'fa5s.stop-circle')
        self.stop_action.setEnabled(False)

        self.api.add_toolbar_action(self.run_action)
        self.api.add_toolbar_action(self.stop_action)

    def _connect_signals(self):
        self.code_runner.output_received.connect(self.output_panel.append_output)
        self.code_runner.error_received.connect(
            lambda text: self.output_panel.append_output(text, is_error=True))
        self.code_runner.process_finished.connect(self._on_run_finished)
        self.main_window.theme_changed_signal.connect(self.output_panel.update_theme)

    def _run_script(self):
        editor = self.main_window.tab_widget.currentWidget()
        if not isinstance(editor, EditorWidget):
            return
        filepath = self.main_window.editor_tabs_data.get(editor, {}).get('filepath')
        if not filepath:
            if QMessageBox.question(self.main_window, "Save Required",
                                    "File must be saved to be executed.",
                                    QMessageBox.StandardButton.Save |
                                    QMessageBox.StandardButton.Cancel
                                    ) == QMessageBox.StandardButton.Save:
                if not self.main_window._action_save_as():
                    return
                filepath = self.main_window.editor_tabs_data.get(editor, {}).get('filepath')
            else:
                return

        elif hash(editor.get_text()) != self.main_window.editor_tabs_data[editor]['original_hash']:
            self.main_window._action_save_file()

        if filepath and os.path.exists(filepath):
            self.output_panel.clear_output()
            self.run_action.setEnabled(False)
            self.stop_action.setEnabled(True)
            self.code_runner.run_script(filepath)

    def _on_run_finished(self, exit_code):
        self.api.show_status_message(f"Process finished with exit code {exit_code}", 4000)
        self.run_action.setEnabled(True)
        self.stop_action.setEnabled(False)


def initialize(main_window):
    return PythonRunnerPlugin(main_window)
```

### File: `/plugins/source_control_ui/plugin.json`

```json
{
    "id": "source_control_ui",
    "name": "Source Control UI",
    "author": "PuffinPy Team",
    "version": "1.1.1",
    "description": "Provides the 'Source Control' panel to view Git status.",
    "entry_point": "plugin_main.py"
}
```

### File: `/plugins/source_control_ui/plugin_main.py`

#### Linter Issues Found:
```

- L5 (E302) No message available

- L23 (E501) No message available

- L24 (E501) No message available

- L25 (E501) No message available

- L33 (W292) No message available

```


```python
# PuffinPyEditor/plugins/source_control_ui/plugin_main.py
from PyQt6.QtCore import Qt
from .project_source_control_panel import ProjectSourceControlPanel

class SourceControlUIPlugin:
    def __init__(self, main_window):
        self.api = main_window.puffin_api
        project_manager = self.api.get_manager("project")
        git_manager = self.api.get_manager("git")
        self.source_control_panel = ProjectSourceControlPanel(
            project_manager, git_manager, main_window)
        self._setup_ui()
        self._connect_signals()

    def _setup_ui(self):
        self.api.register_dock_panel(
            self.source_control_panel, "Source Control",
            Qt.DockWidgetArea.BottomDockWidgetArea, "fa5b.git-alt"
        )

    def _connect_signals(self):
        main_window = self.api.get_main_window()
        # Refresh the panel when the active project changes or a git operation succeeds
        main_window.project_tabs.currentChanged.connect(self.source_control_panel.refresh_all_projects)
        main_window.theme_changed_signal.connect(self.source_control_panel.update_icons)
        self.api.get_manager("git").git_success.connect(
            self.source_control_panel.refresh_all_projects)
        self.api.get_manager("github").operation_success.connect(
            self.source_control_panel.refresh_all_projects)


def initialize(main_window):
    return SourceControlUIPlugin(main_window)
```

### File: `/plugins/source_control_ui/project_source_control_panel.py`

#### Linter Issues Found:
```

- L5 (E501) No message available

- L6 (E501) No message available

- L52 (E501) No message available

- L66 (E501) No message available

- L79 (E501) No message available

- L121 (E501) No message available

- L124 (E501) No message available

- L129 (E501) No message available

- L135 (E501) No message available

- L164 (E501) No message available

- L165 (E501) No message available

- L170 (E501) No message available

- L176 (E501) No message available

- L177 (E501) No message available

- L179 (E501) No message available

- L180 (E501) No message available

- L189 (E501) No message available

- L198 (E501) No message available

- L214 (E501) No message available

- L215 (E501) No message available

- L220 (E501) No message available

- L221 (E501) No message available

- L222 (E501) No message available

- L228 (E501) No message available

- L232 (W292) No message available

```


```python
# PuffinPyEditor/plugins/source_control_ui/project_source_control_panel.py
import os
from typing import List, Dict, Optional
from git import Repo, InvalidGitRepositoryError
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTreeWidget,
                             QTreeWidgetItem, QMenu, QMessageBox, QLabel, QHeaderView, QLineEdit)
from PyQt6.QtGui import QColor
from PyQt6.QtCore import Qt, pyqtSignal, QPoint
import qtawesome as qta

from app_core.project_manager import ProjectManager
from app_core.source_control_manager import SourceControlManager


class ProjectSourceControlPanel(QWidget):
    """
    A widget that displays the Git status for all open projects and provides
    controls for common Git operations.
    """
    publish_repo_requested = pyqtSignal(str)
    create_release_requested = pyqtSignal(str)
    link_to_remote_requested = pyqtSignal(str)
    change_visibility_requested = pyqtSignal(str)

    def __init__(self, project_manager: ProjectManager,
                 git_manager: SourceControlManager, parent=None):
        super().__init__(parent)
        self.project_manager = project_manager
        self.git_manager = git_manager
        self.staged_color = QColor("#A7C080")
        self.unstaged_color = QColor("#DBBC7F")
        self._setup_ui()
        self._connect_signals()
        self.update_icons()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        toolbar_layout = QHBoxLayout()
        self.refresh_all_button = QPushButton("Refresh")
        self.pull_button = QPushButton("Pull")
        self.push_button = QPushButton("Push")
        self.new_release_button = QPushButton("New Release...")
        toolbar_layout.addWidget(self.refresh_all_button)
        toolbar_layout.addWidget(self.pull_button)
        toolbar_layout.addWidget(self.push_button)
        toolbar_layout.addStretch()
        toolbar_layout.addWidget(self.new_release_button)
        layout.addLayout(toolbar_layout)
        self.project_tree = QTreeWidget()
        self.project_tree.setHeaderLabels(["Project / Changes", ""])
        self.project_tree.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        header = self.project_tree.header()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        layout.addWidget(self.project_tree)
        self.commit_message_edit = QLineEdit()
        self.commit_message_edit.setPlaceholderText("Commit message...")
        self.commit_button = QPushButton("Commit All")
        commit_layout = QHBoxLayout()
        commit_layout.addWidget(self.commit_message_edit)
        commit_layout.addWidget(self.commit_button)
        layout.addLayout(commit_layout)
        self.status_label = QLabel("Ready.")
        layout.addWidget(self.status_label)
        self.action_buttons = [self.refresh_all_button, self.pull_button, self.push_button,
                               self.new_release_button, self.commit_button]

    def _connect_signals(self):
        self.git_manager.summaries_ready.connect(self._populate_tree)
        self.git_manager.status_updated.connect(self._update_project_files)
        self.git_manager.git_error.connect(self._handle_git_error)
        self.git_manager.git_success.connect(self._handle_git_success)
        self.refresh_all_button.clicked.connect(self.refresh_all_projects)
        self.push_button.clicked.connect(self._on_push_clicked)
        self.pull_button.clicked.connect(self._on_pull_clicked)
        self.new_release_button.clicked.connect(self._on_new_release_clicked)
        self.commit_button.clicked.connect(self._on_commit_clicked)
        self.project_tree.customContextMenuRequested.connect(self._show_context_menu)

    def set_ui_locked(self, locked: bool, message: str = ""):
        for button in self.action_buttons:
            button.setEnabled(not locked)
        self.commit_message_edit.setEnabled(not locked)
        self.status_label.setText(message)

    def update_icons(self):
        self.refresh_all_button.setIcon(qta.icon('fa5s.sync-alt'))
        self.pull_button.setIcon(qta.icon('fa5s.arrow-down'))
        self.push_button.setIcon(qta.icon('fa5s.arrow-up'))
        self.new_release_button.setIcon(qta.icon('fa5s.tag'))
        self.commit_button.setIcon(qta.icon('fa5s.check'))

    def _get_selected_project_path(self) -> Optional[str]:
        item = self.project_tree.currentItem()
        if not item:
            return self.project_manager.get_active_project_path()
        while parent := item.parent():
            item = parent
        data = item.data(0, Qt.ItemDataRole.UserRole)
        return data.get('path') if data else None

    def _on_push_clicked(self):
        if path := self._get_selected_project_path():
            self.set_ui_locked(True, f"Pushing {os.path.basename(path)}...")
            self.git_manager.push(path)

    def _on_pull_clicked(self):
        if path := self._get_selected_project_path():
            self.set_ui_locked(True, f"Pulling {os.path.basename(path)}...")
            self.git_manager.pull(path)

    def _on_new_release_clicked(self):
        if path := self._get_selected_project_path():
            self.create_release_requested.emit(path)

    def _on_commit_clicked(self):
        path = self._get_selected_project_path()
        message = self.commit_message_edit.text().strip()
        if not path or not message:
            QMessageBox.warning(self, "Commit Failed", "A project must be selected "
                                "and a commit message must be provided.")
            return
        self.set_ui_locked(True, f"Committing changes in {os.path.basename(path)}...")
        self.git_manager.commit_files(path, message)

    def _on_fix_branch_mismatch_clicked(self, path: str):
        reply = QMessageBox.warning(
            self, "Confirm Branch Fix", "This will perform a force-push and delete "
            "the 'master' branch from the remote. Are you sure?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.Cancel,
            QMessageBox.StandardButton.Cancel
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.set_ui_locked(True, f"Fixing branch mismatch for {os.path.basename(path)}...")
            self.git_manager.fix_branch_mismatch(path)

    def _handle_git_success(self, message: str, data: dict):
        self.set_ui_locked(False, f"Success: {message}")
        self.refresh_all_projects()
        if "committed" in message.lower() and not data.get('no_changes'):
            self.commit_message_edit.clear()

    def _handle_git_error(self, error_message: str):
        self.set_ui_locked(False, f"Error: {error_message}")
        self.refresh_all_projects()

    def refresh_all_projects(self):
        self.set_ui_locked(True, "Fetching project statuses...")
        all_projects = self.project_manager.get_open_projects()
        if all_projects:
            self.git_manager.get_summaries(all_projects)
        else:
            self.project_tree.clear()
            self.set_ui_locked(False, "No projects open.")

    def _populate_tree(self, summaries: Dict[str, Dict]):
        self.project_tree.clear()
        git_project_paths = summaries.keys()
        for path in self.project_manager.get_open_projects():
            project_name = os.path.basename(path)
            if path in git_project_paths:
                summary = summaries[path]
                item = QTreeWidgetItem(self.project_tree, [project_name, f"Branch: {summary.get('branch', 'N/A')}"])
                item.setData(0, Qt.ItemDataRole.UserRole, {'type': 'project', 'path': path})
                item.setIcon(0, qta.icon('fa5b.git-alt'))
                self.git_manager.get_status(path)
            else:
                item = QTreeWidgetItem(self.project_tree, [project_name])
                item.setData(0, Qt.ItemDataRole.UserRole, {'type': 'non-git-project', 'path': path})
                item.setIcon(0, qta.icon('fa5.folder', color='gray'))
                actions_widget = QWidget()
                actions_layout = QHBoxLayout(actions_widget)
                actions_layout.setContentsMargins(0, 0, 0, 0)
                link_button = QPushButton("Link...")
                link_button.setToolTip("Link this local folder to an existing GitHub repository")
                link_button.clicked.connect(lambda _, p=path: self.link_to_remote_requested.emit(p))
                publish_button = QPushButton("Publish...")
                publish_button.setToolTip("Create a new repository on GitHub from this project")
                publish_button.clicked.connect(lambda _, p=path: self.publish_repo_requested.emit(p))
                actions_layout.addStretch()
                actions_layout.addWidget(link_button)
                actions_layout.addWidget(publish_button)
                self.project_tree.setItemWidget(item, 1, actions_widget)
        self.set_ui_locked(False, "Ready.")
        if self.project_tree.topLevelItemCount() > 0:
            self.project_tree.setCurrentItem(self.project_tree.topLevelItem(0))

    def _update_project_files(self, staged: List[str], unstaged: List[str], repo_path: str):
        root = self.project_tree.invisibleRootItem()
        for i in range(root.childCount()):
            project_item = root.child(i)
            item_data = project_item.data(0, Qt.ItemDataRole.UserRole)
            if item_data and item_data.get('path') == repo_path:
                project_item.takeChildren()
                for f in sorted(list(set(staged + unstaged))):
                    child = QTreeWidgetItem(project_item, [f])
                    child.setForeground(0, self.staged_color if f in staged else self.unstaged_color)
                project_item.setExpanded(True)
                break

    def _show_context_menu(self, position: QPoint):
        item = self.project_tree.itemAt(position)
        if not item:
            return
        data = item.data(0, Qt.ItemDataRole.UserRole)
        if not (data and (path := data.get('path'))):
            return

        menu = QMenu()
        if data['type'] == 'project':
            menu.addAction(qta.icon('fa5s.sync-alt'), "Refresh Status",
                           lambda: self.git_manager.get_status(path))
            vis_action = menu.addAction(qta.icon('fa5s.eye'), "Change GitHub Visibility...")
            vis_action.triggered.connect(lambda: self.change_visibility_requested.emit(path))
            try:
                branches = [b.name for b in Repo(path).branches]
                if 'main' in branches and 'master' in branches:
                    menu.addSeparator()
                    fix_action = menu.addAction(qta.icon('fa5s.exclamation-triangle',
                                                         color='orange'), "Fix Branch Mismatch...")
                    fix_action.triggered.connect(lambda: self._on_fix_branch_mismatch_clicked(path))
            except (InvalidGitRepositoryError, TypeError):
                pass
        elif data['type'] == 'non-git-project':
            menu.addAction(qta.icon('fa5s.link'), "Link to GitHub Repo...",
                           lambda: self.link_to_remote_requested.emit(path))
            menu.addAction(qta.icon('fa5s.cloud-upload-alt'), "Publish to GitHub...",
                           lambda: self.publish_repo_requested.emit(path))

        if menu.actions():
            menu.exec(self.project_tree.viewport().mapToGlobal(position))
```

### File: `/plugins/tab_drag_handler/__init__.py`

```python

```

### File: `/plugins/tab_drag_handler/draggable_tab_widget.py`

#### Linter Issues Found:
```

- L39 (E501) No message available

- L40 (E501) No message available

- L48 (E501) No message available

- L68 (E501) No message available

- L70 (E501) No message available

- L97 (E501) No message available

- L109 (E501) No message available

- L139 (E501) No message available

- L145 (E501) No message available

- L157 (W293) No message available

- L178 (W293) No message available

- L180 (W293) No message available

- L188 (E501) No message available

- L194 (E501) No message available

- L199 (W293) No message available

- L201 (W293) No message available

- L203 (F821) No message available

- L203 (E501) No message available

- L206 (W293) No message available

- L217 (W293) No message available

- L222 (W292) No message available

```


```python
# PuffinPyEditor/plugins/tab_drag_handler/draggable_tab_widget.py
from PyQt6.QtWidgets import (QTabWidget, QTabBar, QMainWindow, QWidget,
                             QApplication)
from PyQt6.QtCore import Qt, pyqtSignal, QPoint, QMimeData, QByteArray
from PyQt6.QtGui import QMouseEvent, QDrag
from utils.logger import log

# [NEW] Define a custom MIME type to identify our widget drags
WIDGET_REFERENCE_MIME_TYPE = "application/x-puffin-widget-reference"


class FloatingTabWindow(QMainWindow):
    """
    A QMainWindow to host a detached tab. It now knows how to be dragged.
    """
    def __init__(self, main_window_ref, widget, tab_text, tooltip_text, icon):
        super().__init__()
        self.main_window_ref = main_window_ref
        self.hosted_widget = widget

        self.setWindowTitle(f"{tab_text} - PuffinPyEditor")
        self.setCentralWidget(self.hosted_widget)
        if icon:
            self.setWindowIcon(icon)

        self.resize(800, 600)
        self.setToolTip(tooltip_text)

        # [NEW] Attribute to handle starting a drag operation
        self.drag_start_pos = None

    # [MODIFIED] closeEvent now delegates to the main window's generic closer
    def closeEvent(self, event):
        self.main_window_ref._close_widget_safely(self.hosted_widget, event)

    # [NEW] mousePressEvent to initiate a potential drag
    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            # We only start a drag if the click is on the window frame (title bar)
            # A simple way to approximate this is to check if the click is outside
            # the bounds of the central widget.
            if not self.centralWidget().geometry().contains(event.pos()):
                self.drag_start_pos = event.pos()
        super().mousePressEvent(event)

    # [NEW] mouseMoveEvent to perform the drag
    def mouseMoveEvent(self, event: QMouseEvent):
        if not (event.buttons() & Qt.MouseButton.LeftButton) or not self.drag_start_pos:
            return super().mouseMoveEvent(event)

        manhattan_len = (event.pos() - self.drag_start_pos).manhattanLength()
        if manhattan_len < QApplication.startDragDistance():
            return super().mouseMoveEvent(event)

        log.info(f"Initiating drag for widget ID: {id(self.hosted_widget)}")
        drag = QDrag(self)
        mime_data = QMimeData()

        # Create a reference to the widget using its memory ID. This is how
        # the receiving tab bar will know which widget is being dragged.
        widget_id_bytes = QByteArray(str(id(self.hosted_widget)).encode())
        mime_data.setData(WIDGET_REFERENCE_MIME_TYPE, widget_id_bytes)
        drag.setMimeData(mime_data)

        # The drag has started, hide the window. If the drag is cancelled,
        # we'll show it again.
        self.hide()
        # The 'exec()' call blocks until the drag is finished (dropped or cancelled).
        if drag.exec(Qt.DropAction.MoveAction) == Qt.DropAction.IgnoreAction:
            # If the drop was cancelled (or unsuccessful), show the window again.
            log.debug("Tab drag cancelled, showing floating window again.")
            self.show()

        self.drag_start_pos = None


class DraggableTabBar(QTabBar):
    """
    A QTabBar that detects dragging out and now also accepts drops from
    floating windows.
    """
    tab_dragged_out = pyqtSignal(int, QPoint)
    # [NEW] Signal to re-insert a dropped widget. We pass a widget reference.
    tab_reinserted = pyqtSignal(QWidget, int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.drag_start_pos = None
        self.setAcceptDrops(True)  # [MODIFIED] Explicitly accept drops

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_start_pos = event.pos()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent):
        if not (event.buttons() & Qt.MouseButton.LeftButton) or self.drag_start_pos is None:
            return super().mouseMoveEvent(event)

        manhattan_len = (event.pos() - self.drag_start_pos).manhattanLength()
        if manhattan_len < QApplication.startDragDistance():
            return super().mouseMoveEvent(event)

        if self.rect().contains(event.pos()):
            return super().mouseMoveEvent(event)

        tab_index = self.tabAt(self.drag_start_pos)
        if tab_index > -1:
            self.tab_dragged_out.emit(tab_index, event.globalPosition().toPoint())
            self.drag_start_pos = None

    # [NEW] dragEnterEvent to check if we can accept the drop
    def dragEnterEvent(self, event):
        if event.mimeData().hasFormat(WIDGET_REFERENCE_MIME_TYPE):
            event.acceptProposedAction()
        else:
            super().dragEnterEvent(event)

    # [NEW] dropEvent to handle the actual re-insertion
    def dropEvent(self, event):
        if not event.mimeData().hasFormat(WIDGET_REFERENCE_MIME_TYPE):
            return super().dropEvent(event)

        # Get the widget ID from the drag's MIME data
        widget_id_bytes = event.mimeData().data(WIDGET_REFERENCE_MIME_TYPE)
        widget_id_str = widget_id_bytes.data().decode()

        # Find the actual widget instance from the main window's tracking dict
        main_window = self.parentWidget().main_window_ref
        widget_to_reinsert = None
        for widget, data in main_window.editor_tabs_data.items():
            if str(id(widget)) == widget_id_str:
                widget_to_reinsert = widget
                break

        if widget_to_reinsert:
            # Determine the insertion index based on drop position
            drop_index = self.tabAt(event.position().toPoint())
            log.info(f"Dropping widget ID {widget_id_str} at tab index {drop_index}")

            # Emit signal for the parent TabWidget to handle the logic
            self.tab_reinserted.emit(widget_to_reinsert, drop_index)
            event.acceptProposedAction()
        else:
            log.warning(f"Could not find widget with ID {widget_id_str} to re-insert.")
            event.ignore()


class DraggableTabWidget(QTabWidget):
    """
    A QTabWidget that uses a DraggableTabBar to allow detaching and
    re-attaching tabs.
    """
    def __init__(self, main_window_ref, parent=None):
        super().__init__(parent)
        self.main_window_ref = main_window_ref
        
        tab_bar = DraggableTabBar(self)
        self.setTabBar(tab_bar)

        tab_bar.tab_dragged_out.connect(self._handle_tab_drag_out)
        # [NEW] Connect the re-insertion signal
        tab_bar.tab_reinserted.connect(self._handle_tab_reinsert)

    def _handle_tab_drag_out(self, index: int, global_pos: QPoint):
        log.info(f"Detaching tab at index {index}.")

        widget = self.widget(index)
        widget_data = self.main_window_ref.editor_tabs_data.get(widget)
        if not widget or not widget_data:
            log.warning("Could not detach tab: widget or its data not found.")
            return

        # Preserve info before removing the tab
        tab_text = self.tabText(index)
        tooltip = self.tabToolTip(index)
        icon = self.tabIcon(index)
        
        self.removeTab(index)
        
        floating_window = FloatingTabWindow(
            self.main_window_ref, widget, tab_text, tooltip, icon
        )
        floating_window.move(global_pos)
        floating_window.show()

    def _handle_tab_reinsert(self, widget: QWidget, index: int):
        """Re-integrates a widget from a floating window back into this tab bar."""
        log.info(f"Re-inserting widget into tab bar at index: {index}")

        # Find the floating window that holds this widget
        floating_window = widget.window()
        if not isinstance(floating_window, FloatingTabWindow):
            log.error("Re-insert failed: could not find floating parent window.")
            # If something went wrong, ensure the hidden window is shown again.
            if floating_window and hasattr(floating_window, "show"):
                floating_window.show()
            return
            
        widget_data = self.main_window_ref.editor_tabs_data.get(widget, {})
        
        # Prepare for re-insertion
        tab_text = os.path.basename(widget_data.get('filepath')) if widget_data.get('filepath') else "Untitled"
        tooltip = widget_data.get('filepath', "Unsaved file")
        icon = floating_window.windowIcon()
        
        # Reparent the widget back to the tab widget before inserting
        widget.setParent(self)

        if index < 0:  # If dropped on an empty area, append to the end
            index = self.count()

        # Insert tab, set tooltip, and make it active
        self.insertTab(index, widget, icon, tab_text)
        self.setTabToolTip(index, tooltip)
        self.setCurrentWidget(widget)
        
        # Cleanly close the now-empty floating window.
        # Set its central widget to None to prevent it from being
        # garbage-collected with the window.
        floating_window.setCentralWidget(None)
        floating_window.close()
```

### File: `/plugins/tab_drag_handler/plugin.json`

```json
{
    "id": "tab_drag_handler",
    "name": "Draggable Tabs Handler",
    "author": "PuffinPy Team",
    "version": "1.0.0",
    "description": "Upgrades the main editor tab widget to allow tabs to be dragged out into separate floating windows.",
    "entry_point": "plugin_main.py"
}
```

### File: `/plugins/tab_drag_handler/plugin_main.py`

#### Linter Issues Found:
```

- L15 (E501) No message available

- L17 (W293) No message available

- L30 (W293) No message available

- L34 (E261) No message available

- L43 (W293) No message available

- L44 (E501) No message available

- L47 (E501) No message available

- L55 (E501) No message available

- L56 (W292) No message available

```


```python
# PuffinPyEditor/plugins/tab_drag_handler/plugin_main.py
from .draggable_tab_widget import DraggableTabWidget
from utils.logger import log


class TabDragHandlerPlugin:
    def __init__(self, main_window):
        api = main_window.puffin_api
        mw = api.get_main_window()

        # Find the original QTabWidget and its place in the layout
        old_tab_widget = mw.tab_widget
        parent_layout = old_tab_widget.parent().layout()
        if not parent_layout:
            log.error("TabDragHandler: Could not find parent layout of tab_widget.")
            return
            
        # Create an instance of our new draggable widget
        new_tab_widget = DraggableTabWidget(mw)

        # Transfer all existing tabs from the old widget to the new one
        while old_tab_widget.count() > 0:
            widget = old_tab_widget.widget(0)
            text = old_tab_widget.tabText(0)
            icon = old_tab_widget.tabIcon(0)
            tooltip = old_tab_widget.tabToolTip(0)
            old_tab_widget.removeTab(0)
            new_tab_widget.addTab(widget, icon, text)
            new_tab_widget.setTabToolTip(new_tab_widget.count() - 1, tooltip)
        
        # Copy over essential properties
        new_tab_widget.setDocumentMode(old_tab_widget.documentMode())
        new_tab_widget.setTabsClosable(old_tab_widget.tabsClosable())
        new_tab_widget.setMovable(True) # Our new one is always movable

        # Re-connect signals that the main window relies on
        new_tab_widget.currentChanged.connect(mw._on_tab_changed)
        new_tab_widget.tabCloseRequested.connect(mw._action_close_tab_by_index)

        # Replace the widget in the layout
        parent_layout.replaceWidget(old_tab_widget, new_tab_widget)
        old_tab_widget.deleteLater()  # Safely delete the old widget
        
        # Crucially, update the main window's reference to point to our new widget
        mw.tab_widget = new_tab_widget

        log.info("TabDragHandler: Upgraded main QTabWidget to DraggableTabWidget.")


def initialize(main_window):
    """Entry point for the TabDragHandler plugin."""
    try:
        return TabDragHandlerPlugin(main_window)
    except Exception as e:
        log.error(f"Failed to initialize TabDragHandlerPlugin: {e}", exc_info=True)
        return None
```

### File: `/plugins/__init__.py`

```python

```

### File: `/ui/widgets/__init__.py`

```python

```

### File: `/ui/widgets/breakpoint_area.py`

#### Linter Issues Found:
```

- L8 (E501) No message available

- L14 (W293) No message available

- L28 (E261) No message available

- L42 (W293) No message available

- L43 (E501) No message available

- L47 (W293) No message available

- L54 (W293) No message available

- L57 (E501) No message available

- L59 (E261) No message available

- L62 (W293) No message available

- L66 (W293) No message available

- L70 (W293) No message available

- L86 (W293) No message available

- L89 (W293) No message available

- L97 (W292) No message available

```


```python
# PuffinPyEditor/ui/widgets/breakpoint_area.py
from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QMouseEvent, QPainter, QColor
from PyQt6.QtCore import QSize, pyqtSignal, Qt


class BreakpointArea(QWidget):
    """A widget that displays and handles breakpoint toggling with a hover effect."""
    breakpoint_toggled = pyqtSignal(int)

    def __init__(self, editor_widget):
        super().__init__(editor_widget)
        self.editor_widget = editor_widget
        
        # [NEW] Enable mouse tracking to get hover events
        self.setMouseTracking(True)
        # [NEW] Variable to store the line number currently being hovered over
        self.hovered_line = -1

    def sizeHint(self) -> QSize:
        return QSize(self.minimumSizeHint().width(), 0)

    def minimumSizeHint(self) -> QSize:
        return QSize(20, 0)

    # [NEW] Track when the mouse enters the widget
    def enterEvent(self, event):
        self.update() # Trigger a repaint
        super().enterEvent(event)

    # [NEW] Clear hover state when the mouse leaves
    def leaveEvent(self, event):
        self.hovered_line = -1
        self.update()
        super().leaveEvent(event)

    # [NEW] Detect which line is being hovered over
    def mouseMoveEvent(self, event: QMouseEvent):
        text_area = self.editor_widget.text_area
        cursor = text_area.cursorForPosition(event.pos())
        line_num = cursor.block().blockNumber() + 1
        
        # If the hovered line has changed, update the state and trigger a repaint
        if line_num != self.hovered_line:
            self.hovered_line = line_num
            self.update()
        
        super().mouseMoveEvent(event)

    # [MODIFIED] paintEvent now includes logic to draw the hover indicator
    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        colors = self.editor_widget.theme_manager.current_theme_data['colors']
        
        # Define colors
        bg_color = QColor(colors.get('editorGutter.background', '#2c313a'))
        breakpoint_color = QColor(colors.get('editor.breakpoint.color', 'crimson'))
        hover_color = QColor(colors.get('editorGutter.foreground', '#888888'))
        hover_color.setAlpha(128) # Make it semi-transparent

        painter.fillRect(event.rect(), bg_color)
        
        text_area = self.editor_widget.text_area
        offset = text_area.contentOffset()
        block = text_area.firstVisibleBlock()
        
        while block.isValid() and block.isVisible():
            geom = text_area.blockBoundingGeometry(block).translated(offset)
            line_num = block.blockNumber() + 1
            
            radius = 4
            dot_x = self.width() // 2 - radius
            dot_y = int(geom.top() + (geom.height() - radius * 2) / 2)

            # --- Main Drawing Logic ---
            if line_num in self.editor_widget.breakpoints:
                # If there's a breakpoint, draw the solid red dot
                painter.setBrush(breakpoint_color)
                painter.setPen(Qt.PenStyle.NoPen)
                painter.drawEllipse(dot_x, dot_y, radius * 2, radius * 2)
            elif line_num == self.hovered_line:
                # Otherwise, if we are hovering here, draw the "ghost" dot
                painter.setBrush(hover_color)
                painter.setPen(Qt.PenStyle.NoPen)
                painter.drawEllipse(dot_x, dot_y, radius * 2, radius * 2)
            
            if geom.top() > self.height():
                break
            
            block = block.next()

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            # The hover line is always the correct line to toggle
            if self.hovered_line != -1:
                self.breakpoint_toggled.emit(self.hovered_line)
        super().mousePressEvent(event)
```

### File: `/ui/widgets/syntax_highlighter.py`

#### Linter Issues Found:
```

- L16 (E501) No message available

- L94 (E501) No message available

- L114 (E501) No message available

- L160 (W292) No message available

```


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

#### Linter Issues Found:
```

- L4 (E501) No message available

- L60 (E501) No message available

- L68 (E501) No message available

- L72 (E501) No message available

- L83 (E501) No message available

- L97 (E501) No message available

- L168 (E501) No message available

- L173 (E501) No message available

- L185 (E501) No message available

- L191 (E501) No message available

- L198 (E501) No message available

- L218 (E501) No message available

- L223 (E501) No message available

- L231 (E501) No message available

- L232 (E501) No message available

- L250 (E501) No message available

- L258 (E303) No message available

- L272 (E501) No message available

- L280 (E501) No message available

- L285 (E501) No message available

- L286 (E501) No message available

- L292 (E701) No message available

- L299 (E501) No message available

- L300 (E701) No message available

- L309 (E701) No message available

- L311 (E501) No message available

- L312 (E501) No message available

- L316 (E501) No message available

- L321 (E501) No message available

- L325 (E501) No message available

- L329 (E501) No message available

- L333 (E701) No message available

- L337 (W292) No message available

```


```python
# PuffinPyEditor/ui/editor_widget.py
from PyQt6.QtWidgets import (QPlainTextEdit, QWidget, QHBoxLayout, QTextEdit,
                             QToolTip, QVBoxLayout, QMainWindow)
from PyQt6.QtGui import (QFont, QColor, QPainter, QKeyEvent, QTextCursor, QAction,
                         QCursor, QPen, QTextFormat, QWheelEvent)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer, QRect
from utils.logger import log
from app_core.settings_manager import settings_manager
from app_core.completion_manager import CompletionManager
from app_core.theme_manager import theme_manager
# [MODIFIED] Import the new component locations
from .line_number_area import LineNumberArea
from .widgets.breakpoint_area import BreakpointArea
from .widgets.syntax_highlighter import PythonSyntaxHighlighter


class CustomPlainTextEdit(QPlainTextEdit):
    cursor_position_changed_signal = pyqtSignal(int, int)
    definition_requested_from_menu = pyqtSignal()

    def __init__(self, editor_widget_ref, parent=None):
        super().__init__(parent)
        self.editor_widget_ref = editor_widget_ref
        self.setMouseTracking(True)
        self.hover_timer = QTimer(self)
        self.hover_timer.setSingleShot(True)
        self.hover_timer.setInterval(600)
        self.hover_timer.timeout.connect(self._request_hover_tip)
        self.cursorPositionChanged.connect(self._on_cursor_position_changed)
        self.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)

    def wheelEvent(self, event: QWheelEvent):
        if event.modifiers() == Qt.KeyboardModifier.ControlModifier:
            angle = event.angleDelta().y()
            if angle > 0:
                self.editor_widget_ref.change_font_size(1)
            elif angle < 0:
                self.editor_widget_ref.change_font_size(-1)
            event.accept()
        else:
            super().wheelEvent(event)

    def keyPressEvent(self, event: QKeyEvent) -> None:
        if event.key() == Qt.Key.Key_Print:
            event.ignore()
            return

        is_shift = bool(event.modifiers() & Qt.KeyboardModifier.ShiftModifier)
        if event.key() in (Qt.Key.Key_Tab, Qt.Key.Key_Backtab):
            if self.textCursor().hasSelection():
                self._indent_selection(indent=not is_shift)
            elif not is_shift:
                self._insert_indentation()
            return
        super().keyPressEvent(event)

    def _insert_indentation(self):
        style = settings_manager.get("indent_style")
        width = settings_manager.get("indent_width")
        self.textCursor().insertText(" " * width if style == "spaces" else "\t")

    def _indent_selection(self, indent: bool = True):
        cursor = self.textCursor()
        start, end = cursor.selectionStart(), cursor.selectionEnd()
        cursor.setPosition(start)
        start_block = cursor.blockNumber()
        cursor.setPosition(end)
        end_block = (cursor.blockNumber() if cursor.columnNumber() != 0 or end == start else cursor.blockNumber() - 1)

        cursor.beginEditBlock()
        width = settings_manager.get("indent_width")
        indent_str = (" " * width if settings_manager.get("indent_style") == "spaces" else "\t")

        for i in range(start_block, end_block + 1):
            cursor.setPosition(self.document().findBlockByNumber(i).position())
            if indent:
                cursor.insertText(indent_str)
            else:
                block_text = cursor.block().text()
                if block_text.startswith("\t"):
                    cursor.deleteChar()
                else:
                    leading_spaces = len(block_text) - len(block_text.lstrip(' '))
                    for _ in range(min(leading_spaces, width)):
                        cursor.deleteChar()
        cursor.endEditBlock()
        # Restore selection
        new_cursor = QTextCursor(self.document())
        new_cursor.setPosition(start)
        new_cursor.setPosition(end, QTextCursor.MoveMode.KeepAnchor)
        self.setTextCursor(new_cursor)

    def contextMenuEvent(self, event):
        menu = self.createStandardContextMenu()
        menu.addSeparator()
        goto_def_action = QAction("Go to Definition", self, shortcut="F12")
        goto_def_action.triggered.connect(self.definition_requested_from_menu.emit)
        menu.addAction(goto_def_action)
        menu.exec(event.globalPos())

    def mouseMoveEvent(self, event):
        self.hover_timer.start()
        super().mouseMoveEvent(event)

    def _request_hover_tip(self):
        pos = self.viewport().mapFromGlobal(QCursor.pos())
        cursor = self.cursorForPosition(pos)
        self.editor_widget_ref.request_signature(
            cursor.blockNumber() + 1, cursor.columnNumber()
        )

    def _on_cursor_position_changed(self):
        cursor = self.textCursor()
        self.cursor_position_changed_signal.emit(
            cursor.blockNumber() + 1, cursor.columnNumber() + 1
        )
        self.hover_timer.stop()
        QToolTip.hideText()
        self.editor_widget_ref._update_dynamic_highlights()

    def paintEvent(self, event):
        super().paintEvent(event)
        self.editor_widget_ref.paint_indentation_guides(self)


class EditorWidget(QWidget):
    content_possibly_changed = pyqtSignal()
    cursor_position_display_updated = pyqtSignal(int, int)

    def __init__(self, completion_manager: CompletionManager, parent=None):
        super().__init__(parent)
        self.filepath = None
        self.completion_manager = completion_manager
        self.theme_manager = theme_manager
        self.breakpoints = set()

        # [MODIFIED] Setup UI with new components
        self._setup_ui()
        # [MODIFIED] Connect signals for the new architecture
        self._connect_signals()

        self.update_editor_settings()
        self._update_gutter_areas()

    def _setup_ui(self):
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)

        editor_area_widget = QWidget()
        self.layout = QHBoxLayout(editor_area_widget)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

        self.text_area = CustomPlainTextEdit(self)
        self.breakpoint_area = BreakpointArea(self)
        self.line_number_area = LineNumberArea(self)

        self.layout.addWidget(self.breakpoint_area)
        self.layout.addWidget(self.line_number_area)
        self.layout.addWidget(self.text_area)

        self.main_layout.addWidget(editor_area_widget)
        self.highlighter = PythonSyntaxHighlighter(self.text_area.document())

    def _connect_signals(self):
        self.text_area.blockCountChanged.connect(self._on_geometry_changed)
        self.text_area.updateRequest.connect(self._on_update_request)
        self.text_area.cursor_position_changed_signal.connect(self._on_cursor_changed)
        self.text_area.textChanged.connect(self.content_possibly_changed.emit)

        self.completion_manager.hover_tip_ready.connect(self._display_tooltip)
        self.breakpoint_area.breakpoint_toggled.connect(self.toggle_breakpoint)
        self.text_area.definition_requested_from_menu.connect(self.request_definition_from_context)

    def set_filepath(self, filepath: str | None):
        self.filepath = filepath

    def get_text(self) -> str:
        return self.text_area.toPlainText()

    def set_text(self, text: str):
        self.text_area.setPlainText(text)

    def update_editor_settings(self):
        font = QFont(settings_manager.get("font_family"), settings_manager.get("font_size"))
        self.text_area.setFont(font)
        # The gutter widgets will query the editor's font when they paint

        metrics = self.text_area.fontMetrics()
        tab_width = settings_manager.get("indent_width")
        self.text_area.setTabStopDistance(tab_width * metrics.horizontalAdvance(' '))

        self._on_geometry_changed()  # Recalculate everything based on new font
        log.debug("Editor settings applied.")

    def _on_cursor_changed(self, line: int, col: int):
        self.cursor_position_display_updated.emit(line, col)
        # When cursor moves, the line number and breakpoint area need to repaint
        # to show the active line state.
        self.line_number_area.update()
        self.breakpoint_area.update()

    def _on_geometry_changed(self):
        self._update_gutter_areas()
        self.text_area.viewport().update()  # Redraw indentation guides

    def _on_update_request(self, rect: QRect, dy: int):
        if dy:  # On scroll
            self.line_number_area.scroll(0, dy)
            self.breakpoint_area.scroll(0, dy)
        else:  # On other updates, like selection change
            self._update_gutter_areas(rect)

    def line_number_area_width(self) -> int:
        count = max(1, self.text_area.blockCount())
        digits = len(str(count))
        # Calculate width with padding
        space = 10 + self.text_area.fontMetrics().horizontalAdvance('9') * digits
        return space

    def _update_gutter_areas(self, rect=None):
        # Calculate total width needed for all gutters
        total_gutter_width = self.breakpoint_area.minimumSizeHint().width() + self.line_number_area_width()
        self.text_area.setViewportMargins(total_gutter_width, 0, 0, 0)

        # Position and update each gutter widget
        cr = self.text_area.contentsRect()
        bp_width = self.breakpoint_area.minimumSizeHint().width()
        ln_width = self.line_number_area_width()

        self.breakpoint_area.setGeometry(QRect(cr.left(), cr.top(), bp_width, cr.height()))
        self.line_number_area.setGeometry(QRect(cr.left() + bp_width, cr.top(), ln_width, cr.height()))

        if rect:
            self.line_number_area.update(0, rect.y(), ln_width, rect.height())
            self.breakpoint_area.update(0, rect.y(), bp_width, rect.height())
        else:
            self.line_number_area.update()
            self.breakpoint_area.update()

    # --- Feature Logic ---
    def change_font_size(self, delta: int):
        """Changes the editor font size and saves it to global settings."""
        current_size = settings_manager.get("font_size")
        new_size = current_size + delta
        if 6 <= new_size <= 72:  # Reasonable font size limits
            settings_manager.set("font_size", new_size, save_immediately=True)
            # Find the main window to trigger a global settings refresh
            main_win = self.window()
            if isinstance(main_win, QMainWindow) and hasattr(main_win, '_on_editor_settings_changed'):
                # This will call update_editor_settings() on all open editors
                main_win._on_editor_settings_changed()
            else:
                # Fallback for floating windows or different hierarchy
                self.update_editor_settings()


    def toggle_breakpoint(self, line_number: int):
        if line_number in self.breakpoints:
            self.breakpoints.remove(line_number)
        else:
            self.breakpoints.add(line_number)
        self._update_dynamic_highlights()
        self.breakpoint_area.update()  # Trigger a repaint

    def _update_dynamic_highlights(self):
        # Handles highlighting for current line and breakpoints
        selections = []
        colors = self.theme_manager.current_theme_data['colors']

        # Current line highlight
        current_line_color = QColor(colors.get('editor.lineHighlightBackground', '#ffffff'))
        sel = QTextEdit.ExtraSelection()
        sel.format.setBackground(current_line_color)
        sel.format.setProperty(QTextFormat.Property.FullWidthSelection, True)
        sel.cursor = self.text_area.textCursor()
        selections.append(sel)

        # Breakpoint line highlight
        bp_color = QColor(colors.get('editor.breakpoint.background', '#ff0000'))
        bp_color.setAlpha(65)
        for line_num in self.breakpoints:
            bp_sel = QTextEdit.ExtraSelection()
            bp_sel.format.setBackground(bp_color)
            bp_sel.format.setProperty(QTextFormat.Property.FullWidthSelection, True)
            bp_sel.cursor = QTextCursor(self.text_area.document().findBlockByNumber(line_num - 1))
            selections.append(bp_sel)

        self.text_area.setExtraSelections(selections)

    def paint_indentation_guides(self, text_area):
        if not settings_manager.get("show_indentation_guides"): return
        painter = QPainter(text_area.viewport())
        colors = self.theme_manager.current_theme_data['colors']
        pen = QPen(QColor(colors.get('input.border', '#555555')))
        pen.setStyle(Qt.PenStyle.DotLine)
        painter.setPen(pen)

        tab_width_px = text_area.fontMetrics().horizontalAdvance(' ') * settings_manager.get("indent_width")
        if tab_width_px <= 0: return

        offset = text_area.contentOffset()
        block = text_area.firstVisibleBlock()
        while block.isValid() and block.isVisible():
            geom = text_area.blockBoundingGeometry(block).translated(offset)
            if geom.bottom() < 0:
                block = block.next()
                continue
            if geom.top() > text_area.viewport().height(): break

            text = block.text().replace('\t', ' ' * settings_manager.get("indent_width"))
            indent_level = (len(text) - len(text.lstrip(' '))) // settings_manager.get("indent_width")

            for i in range(1, indent_level + 1):
                x = geom.left() + (i * tab_width_px)
                painter.drawLine(int(x), int(geom.top()), int(x), int(geom.bottom()))
            block = block.next()

    def request_definition_from_context(self):
        cursor = self.text_area.textCursor()
        self.completion_manager.request_definition(self.get_text(), cursor.blockNumber() + 1, cursor.columnNumber(),
                                                   self.filepath)

    def request_signature(self, line: int, col: int):
        self.completion_manager.request_signature(self.get_text(), line, col, self.filepath)

    def _display_tooltip(self, html_content: str):
        if html_content:
            QToolTip.showText(QCursor.pos(), html_content, self.text_area.viewport())

    def goto_line_and_column(self, line: int, col: int):
        block = self.text_area.document().findBlockByNumber(line - 1)
        if not block.isValid(): return
        cursor = QTextCursor(block)
        cursor.movePosition(QTextCursor.MoveOperation.Right, n=max(0, col - 1))
        self.text_area.setTextCursor(cursor)
        self.text_area.setFocus()
```

### File: `/ui/file_tree_view.py`

#### Linter Issues Found:
```

- L4 (E501) No message available

- L7 (E501) No message available

- L9 (F401) No message available

- L14 (E302) No message available

- L21 (E501) No message available

- L22 (E501) No message available

- L23 (E501) No message available

- L24 (E501) No message available

- L25 (E501) No message available

- L26 (E501) No message available

- L27 (E501) No message available

- L28 (E501) No message available

- L40 (E501) No message available

- L41 (E501) No message available

- L42 (E501) No message available

- L43 (E501) No message available

- L53 (E501) No message available

- L55 (E501) No message available

- L60 (E501) No message available

- L63 (E302) No message available

- L64 (E501) No message available

- L69 (W293) No message available

- L71 (E261) No message available

- L90 (E501) No message available

- L94 (W293) No message available

- L97 (W293) No message available

- L99 (E501) No message available

- L102 (E261) No message available

- L103 (W293) No message available

- L129 (E702) No message available

- L129 (E501) No message available

- L130 (E702) No message available

- L130 (E501) No message available

- L131 (E702) No message available

- L131 (E501) No message available

- L140 (E501) No message available

- L146 (E501) No message available

- L148 (W293) No message available

- L153 (E501) No message available

- L154 (E501) No message available

- L155 (W293) No message available

- L160 (W293) No message available

- L161 (E501) No message available

- L167 (W293) No message available

- L171 (E501) No message available

- L175 (E501) No message available

- L177 (W293) No message available

- L181 (E501) No message available

- L182 (E501) No message available

- L185 (E501) No message available

- L190 (E501) No message available

- L193 (W293) No message available

- L202 (W293) No message available

- L204 (E701) No message available

- L218 (W291) No message available

- L222 (E501) No message available

- L225 (E501) No message available

- L226 (E501) No message available

- L229 (E501) No message available

- L230 (E501) No message available

- L239 (E501) No message available

- L240 (E302) No message available

- L244 (E501) No message available

- L260 (E501) No message available

- L261 (E501) No message available

- L265 (E501) No message available

- L266 (E501) No message available

- L289 (E501) No message available

- L296 (E501) No message available

- L300 (E701) No message available

- L301 (E501) No message available

- L320 (E501) No message available

- L323 (E701) No message available

- L325 (E501) No message available

- L326 (E501) No message available

- L329 (E501) No message available

- L330 (E501) No message available

- L332 (E501) No message available

- L333 (E231) No message available

- L333 (E501) No message available

- L341 (E701) No message available

- L342 (E701) No message available

- L345 (E501) No message available

- L347 (E501) No message available

- L348 (E701) No message available

- L352 (E501) No message available

- L355 (E701) No message available

- L362 (E501) No message available

- L363 (E501) No message available

- L366 (E701) No message available

- L366 (W292) No message available

```


```python
# PuffinPyEditor/ui/file_tree_view.py
import os
from functools import partial
from PyQt6.QtGui import QFileSystemModel, QPainter, QPen, QColor, QPolygon, QPainterPath
from PyQt6.QtWidgets import (QTreeView, QMessageBox, QMenu, QInputDialog,
                             QWidget, QVBoxLayout, QFileIconProvider)
from PyQt6.QtCore import QDir, Qt, pyqtSignal, QModelIndex, QPoint, QTimer, QRect
import qtawesome as qta
from utils.logger import log
from app_core.file_handler import FileHandler
from app_core.theme_manager import ThemeManager

# --- CustomFileIconProvider class remains the same ---
class CustomFileIconProvider(QFileIconProvider):
    """Provides custom, theme-aware icons for the file tree."""
    def __init__(self, theme_manager):
        super().__init__()
        self.theme_manager = theme_manager
        self.project_root_path = None
        self._icon_map = {
            ".py": "mdi.language-python", ".js": "mdi.language-javascript", ".ts": "mdi.language-typescript",
            ".java": "mdi.language-java", ".cs": "mdi.language-csharp", ".cpp": "mdi.language-cpp",
            ".hpp": "mdi.language-cpp", ".h": "mdi.language-cpp", ".rs": "mdi.language-rust",
            ".html": "mdi.language-html5", ".css": "mdi.language-css3", ".scss": "mdi.language-css3",
            ".json": "mdi.code-json", ".md": "mdi.markdown", ".yaml": "mdi.yaml", ".yml": "mdi.yaml",
            ".xml": "mdi.xml", ".gitignore": "mdi.git", ".git": "mdi.git", "Dockerfile": "mdi.docker",
            ".dockerignore": "mdi.docker", ".txt": "mdi.file-document-outline", ".log": "mdi.file-document-outline",
            "__pycache__": "fa5s.archive", "venv": "fa5s.box-open", ".venv": "fa5s.box-open",
            "dist": "fa5s.box-open", "node_modules": "mdi.folder-npm-outline",
        }

    def set_project_root_path(self, path: str):
        self.project_root_path = path

    def icon(self, fileInfo):
        colors = self.theme_manager.current_theme_data.get('colors', {})
        base_color = colors.get('icon.foreground', '#d0d0d0')
        accent_color = colors.get('accent', '#be5046')
        color_palette = {
            ".py": "#4B8BBE", ".js": "#F7DF1E", ".ts": "#3178C6", ".java": "#B07219",
            ".cs": "#68217A", ".cpp": "#689AD6", ".hpp": "#689AD6", ".h": "#689AD6",
            ".rs": "#DEA584", ".html": "#E34F26", ".css": "#1572B6", ".scss": "#1572B6",
            ".json": "#FBC02D", ".md": "#90A4AE", ".yaml": "#A0A0A0", ".yml": "#A0A0A0",
            ".xml": "#009900", ".gitignore": "#F44336", ".git": "#F44336",
            "Dockerfile": "#2496ED", ".dockerignore": "#2496ED",
            "__pycache__": "#546E7A", "venv": "#546E7A", ".venv": "#546E7A",
            "dist": "#546E7A", "node_modules": "#CB3837",
        }
        file_name = fileInfo.fileName()
        file_path = fileInfo.filePath()

        if file_path == self.project_root_path and fileInfo.isDir():
            return qta.icon('mdi.folder-home-outline', color=accent_color, scale_factor=1.1)
        if file_name in self._icon_map:
            return qta.icon(self._icon_map[file_name], color=color_palette.get(file_name, base_color))
        if fileInfo.isDir():
            return qta.icon('mdi.folder-outline', color=base_color)
        _, ext = os.path.splitext(file_name)
        if ext in self._icon_map:
            return qta.icon(self._icon_map[ext], color=color_palette.get(ext, base_color))
        return qta.icon('mdi.file-outline', color=base_color)

class FileTree(QTreeView):
    """The core TreeView with a manually drawn, highly stylized 'circuitry' theme."""
    def __init__(self, model, theme_manager, parent=None):
        super().__init__(parent)
        self.setModel(model)
        self.theme_manager = theme_manager
        
        self.setAnimated(True)
        self.setIndentation(22) # Give a little more room for the new traces
        self.setSortingEnabled(True)
        self.sortByColumn(0, Qt.SortOrder.AscendingOrder)
        self.setHeaderHidden(True)
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.setDropIndicatorShown(True)
        self.setDragDropMode(self.DragDropMode.InternalMove)
        self.setRootIsDecorated(True)

        for i in range(1, self.model().columnCount()):
            self.setColumnHidden(i, True)

    def drawBranches(self, painter, rect, index):
        """ Overridden to do nothing, preventing default branch drawing. """
        pass

    def paintEvent(self, event):
        """
        Manually paints a high-tech "schematic" style, featuring solid vertical buses,
        and shadowed, angled "lightning bolt" traces connecting to each item.
        """
        super().paintEvent(event)
        
        painter = QPainter(self.viewport())
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        colors = self.theme_manager.current_theme_data.get('colors', {})
        bus_color = QColor(colors.get('tree.indentationGuides.stroke', '#5c6370'))
        trace_color = QColor(colors.get('accent', '#be5046'))
        shadow_color = QColor(bus_color)
        shadow_color.setAlpha(100) # Dark, subtle shadow
        
        model = self.model()
        indent = self.indentation()
        offset = self.header().offset()

        # --- Drawing constants for the schematic style ---
        bus_width = 4
        kink_amount = 6
        node_size = 5
        terminus_radius = 2.5
        line_to_item_margin = 4
        trace_thickness = 1.8
        shadow_offset = QPoint(1, 1)

        current_index = self.indexAt(QPoint(0, 0))
        while current_index.isValid():
            rect = self.visualRect(current_index)
            if not rect.isValid() or rect.height() == 0:
                current_index = self.indexBelow(current_index)
                continue

            depth = self._get_depth(current_index)
            y_connect = rect.center().y()
            stem_x = offset + (indent * depth) + (indent // 2)

            opacity = max(0.4, 1.0 - depth * 0.1)
            faded_bus_color = QColor(bus_color); faded_bus_color.setAlphaF(opacity * 0.7)
            faded_trace_color = QColor(trace_color); faded_trace_color.setAlphaF(opacity)
            faded_shadow_color = QColor(shadow_color); faded_shadow_color.setAlphaF(opacity)

            # --- 1. Draw Parent Solid "Bus" and Guide Lines ---
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(faded_bus_color)
            ancestor_index = current_index.parent()
            for i in range(depth):
                if self._has_siblings_below(ancestor_index):
                    parent_bus_x = offset + (indent * i) + (indent // 2)
                    bus_rect = QRect(parent_bus_x - bus_width // 2, rect.top(), bus_width, rect.height())
                    painter.drawRect(bus_rect)
                ancestor_index = ancestor_index.parent()

            # --- 2. Draw This Item's Vertical Bus and Guide Lines ---
            # Solid part of the bus stops at the connection point
            bus_rect = QRect(stem_x - bus_width // 2, rect.top(), bus_width, y_connect - rect.top())
            painter.drawRect(bus_rect)
            
            # If item has siblings below, draw thin guide lines continuing down
            if self._has_siblings_below(current_index):
                painter.setPen(QPen(faded_bus_color, 1.0))
                painter.setBrush(Qt.BrushStyle.NoBrush)
                painter.drawLine(stem_x - bus_width // 2, y_connect, stem_x - bus_width // 2, rect.bottom())
                painter.drawLine(stem_x + bus_width // 2, y_connect, stem_x + bus_width // 2, rect.bottom())
            
            # --- 3. Draw the "Lightning Bolt" Trace with 3D Shadow ---
            start_p = QPoint(stem_x, y_connect)
            end_p = QPoint(rect.left() - line_to_item_margin, y_connect)
            mid_p = QPoint((start_p.x() + end_p.x()) // 2, y_connect)
            
            kink_p = QPoint(mid_p.x(), mid_p.y() + (kink_amount if current_index.row() % 2 == 0 else -kink_amount))

            trace_path = QPainterPath()
            trace_path.moveTo(start_p)
            trace_path.lineTo(kink_p)
            trace_path.lineTo(end_p)
            
            # Draw shadow first
            shadow_path = QPainterPath(trace_path)
            shadow_path.translate(shadow_offset)
            painter.setPen(QPen(faded_shadow_color, trace_thickness, cap=Qt.PenCapStyle.RoundCap, join=Qt.PenJoinStyle.RoundJoin))
            painter.drawPath(shadow_path)

            # Draw main trace on top
            painter.setPen(QPen(faded_trace_color, trace_thickness, cap=Qt.PenCapStyle.RoundCap, join=Qt.PenJoinStyle.RoundJoin))
            painter.drawPath(trace_path)
            
            # --- 4. Draw Junction Node (diamond) or Terminus (circle) ---
            if model.hasChildren(current_index):
                diamond_poly = QPolygon([
                    QPoint(stem_x, y_connect - node_size), QPoint(stem_x + node_size, y_connect),
                    QPoint(stem_x, y_connect + node_size), QPoint(stem_x - node_size, y_connect)
                ])
                painter.setPen(QPen(faded_trace_color, 1.5))
                painter.setBrush(faded_trace_color if self.isExpanded(current_index) else Qt.BrushStyle.NoBrush)
                painter.drawPolygon(diamond_poly)
            else:
                painter.setBrush(faded_bus_color)
                painter.setPen(Qt.PenStyle.NoPen)
                painter.drawEllipse(QPoint(stem_x, y_connect), terminus_radius, terminus_radius)

            current_index = self.indexBelow(current_index)
    
    def _get_depth(self, index: QModelIndex) -> int:
        depth = 0
        p = index.parent()
        root = self.rootIndex()
        while p.isValid() and p != root:
            depth += 1
            p = p.parent()
        return depth
        
    def _has_siblings_below(self, index: QModelIndex) -> bool:
        if not index.isValid(): return False
        parent = index.parent()
        return index.row() < self.model().rowCount(parent) - 1

    def update_theme(self, colors):
        style_sheet = f"""
            QTreeView {{
                background-color: transparent;
                color: {colors.get('sidebar.foreground', '#d0d0d0')};
                border: none;
                outline: 0px;
                font-size: 9.5pt;
            }}
            QTreeView::item {{
                padding: 3px 4px; 
                border-radius: 4px;
            }}
            QTreeView::item:hover {{
                background-color: {colors.get('list.hoverBackground', '#3a4149')};
            }}
            QTreeView::item:selected:active {{
                background-color: {colors.get('list.activeSelectionBackground', '#4a5160')};
                color: {colors.get('list.activeSelectionForeground', '#ffffff')};
            }}
            QTreeView::item:selected:!active {{
                background-color: {colors.get('list.inactiveSelectionBackground', '#3a4149')};
                color: {colors.get('list.inactiveSelectionForeground', '#d0d0d0')};
            }}
            QTreeView::branch {{
                background: transparent;
            }}
        """
        self.setStyleSheet(style_sheet)
        self.viewport().update()

# --- The FileTreeViewWidget class remains the same as the last stable version ---
class FileTreeViewWidget(QWidget):
    file_open_requested = pyqtSignal(str)
    file_to_open_created = pyqtSignal(str)

    def __init__(self, file_handler: FileHandler, theme_manager: ThemeManager, parent=None):
        super().__init__(parent)
        self.file_handler = file_handler
        self.theme_manager = theme_manager
        self.project_root_path = None
        self._setup_ui()
        self._connect_signals()
        self.update_theme()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        self.file_system_model = QFileSystemModel()
        self.icon_provider = CustomFileIconProvider(self.theme_manager)
        self.file_system_model.setIconProvider(self.icon_provider)
        self.file_system_model.setFilter(QDir.Filter.AllDirs | QDir.Filter.NoDotAndDotDot | QDir.Filter.AllEntries)
        self.tree_view = FileTree(self.file_system_model, self.theme_manager, self)
        layout.addWidget(self.tree_view)

    def _connect_signals(self):
        self.tree_view.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.tree_view.customContextMenuRequested.connect(self._show_context_menu)
        self.tree_view.doubleClicked.connect(self._on_item_double_clicked)

    def update_theme(self):
        colors = self.theme_manager.current_theme_data.get('colors', {})
        self.tree_view.update_theme(colors)
        self.icon_provider = CustomFileIconProvider(self.theme_manager)
        if self.project_root_path:
            self.icon_provider.set_project_root_path(self.project_root_path)
        self.file_system_model.setIconProvider(self.icon_provider)
        self.tree_view.viewport().update()

    def set_project_root(self, path: str | None):
        if path and QDir(path).exists():
            self.project_root_path = path
            self.icon_provider.set_project_root_path(self.project_root_path)
            parent_dir_path = os.path.dirname(path)
            project_dir_name = os.path.basename(path)
            self.file_system_model.setRootPath(parent_dir_path)
            root_index = self.file_system_model.index(parent_dir_path)
            self.tree_view.setRootIndex(root_index)
            for i in range(1, self.file_system_model.columnCount()):
                self.tree_view.setColumnHidden(i, True)
            QTimer.singleShot(50, lambda: self._filter_to_project_folder(root_index, project_dir_name, path))
        else:
            self.project_root_path = None
            self.icon_provider.set_project_root_path(None)
            self.file_system_model.setRootPath("")
            self.tree_view.setRootIndex(QModelIndex())

    def _filter_to_project_folder(self, root_index, project_dir_name, project_path):
        project_found = False
        for row in range(self.file_system_model.rowCount(root_index)):
            child_index = self.file_system_model.index(row, 0, root_index)
            if not child_index.isValid(): continue
            if self.file_system_model.fileName(child_index) != project_dir_name:
                self.tree_view.setRowHidden(row, root_index, True)
            else:
                project_found = True
        if project_found:
            project_index = self.file_system_model.index(project_path)
            if project_index.isValid():
                self.tree_view.expand(project_index)

    def _on_item_double_clicked(self, index: QModelIndex):
        if index.isValid() and not self.file_system_model.isDir(index):
            file_path = self.file_system_model.filePath(index)
            self.file_open_requested.emit(file_path)

    def _show_context_menu(self, position: QPoint):
        index = self.tree_view.indexAt(position)
        menu = QMenu()
        if index.isValid():
            clicked_path = self.file_system_model.filePath(index)
            target_dir = clicked_path if self.file_system_model.isDir(index) else os.path.dirname(clicked_path)
        else:
            clicked_path = self.project_root_path
            if not clicked_path: return
            target_dir = clicked_path
        menu.addAction(qta.icon('mdi.file-plus-outline'), "New File...", partial(self._action_new_file, target_dir))
        menu.addAction(qta.icon('mdi.folder-plus-outline'), "New Folder...", partial(self._action_new_folder, target_dir))
        if index.isValid():
            menu.addSeparator()
            menu.addAction(qta.icon('mdi.pencil-outline'), "Rename...", partial(self._action_rename, clicked_path))
            menu.addAction(qta.icon('mdi.trash-can-outline', color='crimson'), "Delete", partial(self._action_delete, clicked_path))
            menu.addSeparator()
            menu.addAction(qta.icon('mdi.content-copy'), "Copy Path", partial(self.file_handler.copy_path_to_clipboard, clicked_path))
            menu.addAction(qta.icon('mdi.folder-search-outline'),"Reveal in File Explorer", partial(self.file_handler.reveal_in_explorer, clicked_path))
        menu.exec(self.tree_view.viewport().mapToGlobal(position))

    def _action_new_file(self, base_path: str):
        name, ok = QInputDialog.getText(self, "New File", "Enter file name:")
        if ok and name:
            new_path = os.path.join(base_path, name)
            success, error = self.file_handler.create_file(new_path)
            if success: self.file_to_open_created.emit(new_path)
            else: QMessageBox.warning(self, "Error", error)

    def _action_new_folder(self, base_path: str):
        name, ok = QInputDialog.getText(self, "New Folder", "Enter folder name:")
        if ok and name:
            success, error = self.file_handler.create_folder(os.path.join(base_path, name))
            if not success: QMessageBox.warning(self, "Error", error)

    def _action_rename(self, path: str):
        current_name = os.path.basename(path)
        new_name, ok = QInputDialog.getText(self, "Rename", "Enter new name:", text=current_name)
        if ok and new_name and new_name != current_name:
            success, result = self.file_handler.rename_item(path, new_name)
            if not success: QMessageBox.warning(self, "Error", result)

    def _action_delete(self, path: str):
        item_name = os.path.basename(path)
        is_dir = os.path.isdir(path)
        reply = QMessageBox.question(
            self, "Confirm Delete",
            f"Are you sure you want to permanently delete this {'folder' if is_dir else 'file'}?\n\n'{item_name}'",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.Cancel, QMessageBox.StandardButton.Cancel)
        if reply == QMessageBox.StandardButton.Yes:
            success, error = self.file_handler.delete_item(path)
            if not success: QMessageBox.warning(self, "Error", error)
```

### File: `/ui/line_number_area.py`

#### Linter Issues Found:
```

- L9 (E501) No message available

- L47 (E501) No message available

- L52 (E501) No message available

- L56 (E501) No message available

- L62 (E501) No message available

- L71 (W292) No message available

```


```python
# PuffinPyEditor/ui/line_number_area.py
from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QPainter, QColor
from PyQt6.QtCore import QSize, Qt


class LineNumberArea(QWidget):
    """
    An interactive widget that displays line numbers with pixel-perfect alignment
    by querying the editor's text block geometry directly.
    """

    def __init__(self, editor_widget):
        super().__init__(editor_widget)
        self.editor_widget = editor_widget

    def sizeHint(self) -> QSize:
        """Determines the required width of the widget based on line count."""
        return QSize(self.editor_widget.line_number_area_width(), 0)

    def paintEvent(self, event) -> None:
        """
        Paints the line numbers with perfect alignment by using the exact
        geometry of the text blocks from the editor.
        """
        painter = QPainter(self)
        colors = self.editor_widget.theme_manager.current_theme_data['colors']
        text_area = self.editor_widget.text_area

        # 1. Fill the background
        bg_color = QColor(colors.get('editorGutter.background', '#2c313a'))
        painter.fillRect(event.rect(), bg_color)

        # 2. Get the geometry of the first visible line to start drawing
        block = text_area.firstVisibleBlock()
        block_number = block.blockNumber()
        offset = text_area.contentOffset()

        current_line = text_area.textCursor().blockNumber()

        # 3. Iterate through all visible blocks (lines)
        while block.isValid() and block.isVisible():
            # Get the exact geometry for this specific line
            geom = text_area.blockBoundingGeometry(block).translated(offset)

            # Check if this line is within the area that needs to be repainted
            if geom.bottom() >= event.rect().top() and geom.top() <= event.rect().bottom():
                number = str(block_number + 1)

                # Set color: bright for the current line, faded for others
                is_current = (block_number == current_line)
                pen_color_name = 'editorLineNumber.activeForeground' if is_current else 'editorLineNumber.foreground'
                pen_color = QColor(colors.get(pen_color_name, '#d0d0d0'))
                painter.setPen(pen_color)

                # 4. Draw the number using the block's exact geometry. This is the key.
                painter.drawText(
                    0,
                    int(geom.top()),
                    self.width() - 8,  # 8px right-side padding
                    int(geom.height()),
                    Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter,
                    number
                )

            # Stop drawing if we are past the visible viewport
            if geom.top() > self.height():
                break

            block = block.next()
            block_number += 1
```

### File: `/ui/main_window.py`

#### Linter Issues Found:
```

- L5 (F401) No message available

- L5 (F401) No message available

- L7 (F401) No message available

- L7 (F401) No message available

- L7 (E501) No message available

- L8 (E501) No message available

- L9 (F401) No message available

- L9 (F401) No message available

- L9 (E501) No message available

- L10 (E501) No message available

- L11 (E501) No message available

- L12 (F401) No message available

- L12 (E501) No message available

- L19 (F401) No message available

- L35 (F811) No message available

- L40 (E501) No message available

- L41 (E501) No message available

- L42 (E501) No message available

- L43 (E501) No message available

- L44 (E501) No message available

- L45 (E501) No message available

- L46 (E501) No message available

- L47 (E501) No message available

- L59 (E501) No message available

- L60 (E501) No message available

- L61 (E501) No message available

- L62 (E501) No message available

- L63 (E501) No message available

- L64 (E501) No message available

- L69 (E501) No message available

- L71 (E501) No message available

- L76 (E501) No message available

- L81 (F811) No message available

- L106 (E501) No message available

- L130 (E703) No message available

- L132 (E703) No message available

- L134 (E703) No message available

- L142 (E501) No message available

- L145 (E501) No message available

- L150 (E501) No message available

- L151 (E501) No message available

- L155 (E501) No message available

- L163 (E501) No message available

- L166 (E501) No message available

- L170 (E501) No message available

- L171 (E501) No message available

- L174 (E501) No message available

- L179 (E501) No message available

- L192 (E701) No message available

- L206 (W291) No message available

- L210 (E501) No message available

- L213 (E501) No message available

- L214 (E501) No message available

- L217 (E501) No message available

- L218 (E501) No message available

- L232 (F811) No message available

- L232 (E501) No message available

- L248 (E501) No message available

- L249 (E501) No message available

- L253 (E501) No message available

- L254 (E501) No message available

- L277 (E501) No message available

- L284 (E501) No message available

- L288 (E701) No message available

- L289 (E501) No message available

- L308 (E501) No message available

- L311 (E701) No message available

- L313 (E501) No message available

- L318 (E501) No message available

- L319 (E501) No message available

- L323 (E501) No message available

- L324 (E501) No message available

- L325 (E501) No message available

- L339 (E501) No message available

- L341 (E501) No message available

- L342 (E701) No message available

- L346 (E501) No message available

- L349 (E701) No message available

- L355 (E501) No message available

- L356 (E501) No message available

- L360 (E701) No message available

- L368 (F811) No message available

- L368 (E501) No message available

- L374 (E501) No message available

- L394 (E501) No message available

- L396 (E501) No message available

- L399 (E501) No message available

- L401 (E501) No message available

- L404 (E501) No message available

- L439 (E501) No message available

- L451 (E501) No message available

- L455 (E501) No message available

- L456 (E501) No message available

- L457 (E501) No message available

- L458 (E501) No message available

- L460 (E501) No message available

- L461 (E501) No message available

- L462 (E501) No message available

- L467 (E701) No message available

- L468 (E701) No message available

- L480 (E501) No message available

- L483 (E501) No message available

- L485 (E501) No message available

- L493 (E501) No message available

- L494 (E501) No message available

- L502 (E501) No message available

- L503 (E703) No message available

- L504 (E501) No message available

- L520 (E501) No message available

- L522 (E501) No message available

- L524 (E501) No message available

- L545 (E501) No message available

- L547 (E501) No message available

- L565 (E501) No message available

- L572 (E701) No message available

- L576 (E701) No message available

- L579 (E501) No message available

- L582 (E501) No message available

- L592 (E501) No message available

- L594 (E701) No message available

- L595 (E501) No message available

- L598 (E501) No message available

- L606 (E501) No message available

- L611 (E501) No message available

- L614 (E501) No message available

- L614 (E703) No message available

- L626 (F821) No message available

- L632 (E701) No message available

- L692 (E501) No message available

- L694 (E501) No message available

- L695 (E501) No message available

- L702 (E703) No message available

- L707 (E501) No message available

- L714 (E501) No message available

- L719 (W292) No message available

```


```python
# PuffinPyEditor/ui/main_window.py
import os
import sys
from functools import partial
from typing import Optional, Callable
# *** FIX: Add QActionGroup to the list of QtGui imports ***
from PyQt6.QtGui import (QFileSystemModel, QPainter, QPen, QColor, QPolygon, QPainterPath,
                         QKeySequence, QAction, QDesktopServices, QCloseEvent, QActionGroup)
from PyQt6.QtWidgets import (QTreeView, QMessageBox, QMenu, QInputDialog, QWidget, QVBoxLayout, QHBoxLayout,
                             QFileIconProvider, QMainWindow, QStatusBar, QDockWidget, QTextEdit,
                             QTabWidget, QSplitter, QLabel, QToolButton, QToolBar, QSizePolicy, QApplication)
from PyQt6.QtCore import (QDir, Qt, pyqtSignal, QModelIndex, QPoint, QTimer, QRect, QPointF,
                          QSize, QUrl)
import qtawesome as qta

from utils.logger import log
from utils import versioning
from app_core.file_handler import FileHandler
from app_core.theme_manager import ThemeManager, theme_manager
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


# --- CustomFileIconProvider and FileTree classes remain the same ---
class CustomFileIconProvider(QFileIconProvider):
    def __init__(self, theme_manager):
        super().__init__()
        self.theme_manager = theme_manager
        self.project_root_path = None
        self._icon_map = {
            ".py": "mdi.language-python", ".js": "mdi.language-javascript", ".ts": "mdi.language-typescript",
            ".java": "mdi.language-java", ".cs": "mdi.language-csharp", ".cpp": "mdi.language-cpp",
            ".hpp": "mdi.language-cpp", ".h": "mdi.language-cpp", ".rs": "mdi.language-rust",
            ".html": "mdi.language-html5", ".css": "mdi.language-css3", ".scss": "mdi.language-css3",
            ".json": "mdi.code-json", ".md": "mdi.markdown", ".yaml": "mdi.yaml", ".yml": "mdi.yaml",
            ".xml": "mdi.xml", ".gitignore": "mdi.git", ".git": "mdi.git", "Dockerfile": "mdi.docker",
            ".dockerignore": "mdi.docker", ".txt": "mdi.file-document-outline", ".log": "mdi.file-document-outline",
            "__pycache__": "fa5s.archive", "venv": "fa5s.box-open", ".venv": "fa5s.box-open",
            "dist": "fa5s.box-open", "node_modules": "mdi.folder-npm-outline",
        }

    def set_project_root_path(self, path: str):
        self.project_root_path = path

    def icon(self, fileInfo):
        colors = self.theme_manager.current_theme_data.get('colors', {})
        base_color = colors.get('icon.foreground', '#d0d0d0')
        accent_color = colors.get('accent', '#be5046')
        color_palette = {
            ".py": "#4B8BBE", ".js": "#F7DF1E", ".ts": "#3178C6", ".java": "#B07219", ".cs": "#68217A",
            ".cpp": "#689AD6", ".hpp": "#689AD6", ".h": "#689AD6", ".rs": "#DEA584", ".html": "#E34F26",
            ".css": "#1572B6", ".scss": "#1572B6", ".json": "#FBC02D", ".md": "#90A4AE", ".yaml": "#A0A0A0",
            ".yml": "#A0A0A0", ".xml": "#009900", ".gitignore": "#F44336", ".git": "#F44336",
            "Dockerfile": "#2496ED", ".dockerignore": "#2496ED", "__pycache__": "#546E7A",
            "venv": "#546E7A", ".venv": "#546E7A", "dist": "#546E7A", "node_modules": "#CB3837",
        }
        file_name = fileInfo.fileName()
        file_path = fileInfo.filePath()
        if file_path == self.project_root_path and fileInfo.isDir():
            return qta.icon('mdi.folder-home-outline', color=accent_color, scale_factor=1.1)
        if file_name in self._icon_map:
            return qta.icon(self._icon_map[file_name], color=color_palette.get(file_name, base_color))
        if fileInfo.isDir():
            return qta.icon('mdi.folder-outline', color=base_color)
        _, ext = os.path.splitext(file_name)
        if ext in self._icon_map:
            return qta.icon(self._icon_map[ext], color=color_palette.get(ext, base_color))
        return qta.icon('mdi.file-outline', color=base_color)


class FileTree(QTreeView):
    def __init__(self, model, theme_manager, parent=None):
        super().__init__(parent)
        self.setModel(model)
        self.theme_manager = theme_manager
        self.setAnimated(True)
        self.setIndentation(22)
        self.setSortingEnabled(True)
        self.sortByColumn(0, Qt.SortOrder.AscendingOrder)
        self.setHeaderHidden(True)
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.setDropIndicatorShown(True)
        self.setDragDropMode(self.DragDropMode.InternalMove)
        self.setRootIsDecorated(True)
        for i in range(1, self.model().columnCount()):
            self.setColumnHidden(i, True)

    def drawBranches(self, painter, rect, index):
        pass

    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self.viewport())
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        colors = self.theme_manager.current_theme_data.get('colors', {})
        bus_color = QColor(colors.get('tree.indentationGuides.stroke', '#5c6370'))
        trace_color = QColor(colors.get('accent', '#be5046'))
        shadow_color = QColor(bus_color)
        shadow_color.setAlpha(100)
        model = self.model()
        indent = self.indentation()
        offset = self.header().offset()
        bus_width = 4
        kink_amount = 6
        node_size = 5
        terminus_radius = 2.5
        line_to_item_margin = 4
        trace_thickness = 1.8
        shadow_offset = QPointF(1, 1)
        current_index = self.indexAt(QPoint(0, 0))
        while current_index.isValid():
            rect = self.visualRect(current_index)
            if not rect.isValid() or rect.height() == 0:
                current_index = self.indexBelow(current_index)
                continue
            depth = self._get_depth(current_index)
            y_connect = rect.center().y()
            stem_x = offset + (indent * depth) + (indent // 2)
            opacity = max(0.4, 1.0 - depth * 0.1)
            faded_bus_color = QColor(bus_color);
            faded_bus_color.setAlphaF(opacity * 0.7)
            faded_trace_color = QColor(trace_color);
            faded_trace_color.setAlphaF(opacity)
            faded_shadow_color = QColor(shadow_color);
            faded_shadow_color.setAlphaF(opacity)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(faded_bus_color)
            ancestor_index = current_index.parent()
            for i in range(depth):
                if self._has_siblings_below(ancestor_index):
                    parent_bus_x = offset + (indent * i) + (indent // 2)
                    bus_rect = QRect(parent_bus_x - bus_width // 2, rect.top(), bus_width, rect.height())
                    painter.drawRect(bus_rect)
                ancestor_index = ancestor_index.parent()
            bus_rect = QRect(stem_x - bus_width // 2, rect.top(), bus_width, y_connect - rect.top())
            painter.drawRect(bus_rect)
            if self._has_siblings_below(current_index):
                painter.setPen(QPen(faded_bus_color, 1.0))
                painter.setBrush(Qt.BrushStyle.NoBrush)
                painter.drawLine(stem_x - bus_width // 2, y_connect, stem_x - bus_width // 2, rect.bottom())
                painter.drawLine(stem_x + bus_width // 2, y_connect, stem_x + bus_width // 2, rect.bottom())
            start_p = QPointF(stem_x, y_connect)
            end_p = QPointF(rect.left() - line_to_item_margin, y_connect)
            mid_p = QPointF((start_p.x() + end_p.x()) / 2.0, y_connect)
            kink_p = QPointF(mid_p.x(), mid_p.y() + (kink_amount if current_index.row() % 2 == 0 else -kink_amount))
            trace_path = QPainterPath()
            trace_path.moveTo(start_p)
            trace_path.lineTo(kink_p)
            trace_path.lineTo(end_p)
            shadow_path = QPainterPath(trace_path)
            shadow_path.translate(shadow_offset)
            painter.setPen(
                QPen(faded_shadow_color, trace_thickness, cap=Qt.PenCapStyle.RoundCap, join=Qt.PenJoinStyle.RoundJoin))
            painter.drawPath(shadow_path)
            painter.setPen(
                QPen(faded_trace_color, trace_thickness, cap=Qt.PenCapStyle.RoundCap, join=Qt.PenJoinStyle.RoundJoin))
            painter.drawPath(trace_path)
            if model.hasChildren(current_index):
                diamond_poly = QPolygon([
                    QPoint(stem_x, y_connect - node_size), QPoint(stem_x + node_size, y_connect),
                    QPoint(stem_x, y_connect + node_size), QPoint(stem_x - node_size, y_connect)
                ])
                painter.setPen(QPen(faded_trace_color, 1.5))
                painter.setBrush(faded_trace_color if self.isExpanded(current_index) else Qt.BrushStyle.NoBrush)
                painter.drawPolygon(diamond_poly)
            else:
                painter.setBrush(faded_bus_color)
                painter.setPen(Qt.PenStyle.NoPen)
                painter.drawEllipse(QPointF(stem_x, y_connect), terminus_radius, terminus_radius)
            current_index = self.indexBelow(current_index)

    def _get_depth(self, index: QModelIndex) -> int:
        depth = 0
        p = index.parent()
        root = self.rootIndex()
        while p.isValid() and p != root:
            depth += 1
            p = p.parent()
        return depth

    def _has_siblings_below(self, index: QModelIndex) -> bool:
        if not index.isValid(): return False
        parent = index.parent()
        return index.row() < self.model().rowCount(parent) - 1

    def update_theme(self, colors):
        style_sheet = f"""
            QTreeView {{
                background-color: transparent;
                color: {colors.get('sidebar.foreground', '#d0d0d0')};
                border: none;
                outline: 0px;
                font-size: 9.5pt;
            }}
            QTreeView::item {{
                padding: 3px 4px; 
                border-radius: 4px;
            }}
            QTreeView::item:hover {{
                background-color: {colors.get('list.hoverBackground', '#3a4149')};
            }}
            QTreeView::item:selected:active {{
                background-color: {colors.get('list.activeSelectionBackground', '#4a5160')};
                color: {colors.get('list.activeSelectionForeground', '#ffffff')};
            }}
            QTreeView::item:selected:!active {{
                background-color: {colors.get('list.inactiveSelectionBackground', '#3a4149')};
                color: {colors.get('list.inactiveSelectionForeground', '#d0d0d0')};
            }}
            QTreeView::branch {{
                background: transparent;
            }}
        """
        self.setStyleSheet(style_sheet)
        self.viewport().update()


class FileTreeViewWidget(QWidget):
    file_open_requested = pyqtSignal(str)
    file_to_open_created = pyqtSignal(str)

    def __init__(self, file_handler: FileHandler, theme_manager: ThemeManager, parent=None):
        super().__init__(parent)
        self.file_handler = file_handler
        self.theme_manager = theme_manager
        self.project_root_path = None
        self._setup_ui()
        self._connect_signals()
        self.update_theme()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        self.file_system_model = QFileSystemModel()
        self.icon_provider = CustomFileIconProvider(self.theme_manager)
        self.file_system_model.setIconProvider(self.icon_provider)
        self.file_system_model.setFilter(QDir.Filter.AllDirs | QDir.Filter.NoDotAndDotDot | QDir.Filter.AllEntries)
        self.tree_view = FileTree(self.file_system_model, self.theme_manager, self)
        layout.addWidget(self.tree_view)

    def _connect_signals(self):
        self.tree_view.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.tree_view.customContextMenuRequested.connect(self._show_context_menu)
        self.tree_view.doubleClicked.connect(self._on_item_double_clicked)

    def update_theme(self):
        colors = self.theme_manager.current_theme_data.get('colors', {})
        self.tree_view.update_theme(colors)
        self.icon_provider = CustomFileIconProvider(self.theme_manager)
        if self.project_root_path:
            self.icon_provider.set_project_root_path(self.project_root_path)
        self.file_system_model.setIconProvider(self.icon_provider)
        self.tree_view.viewport().update()

    def set_project_root(self, path: str | None):
        if path and QDir(path).exists():
            self.project_root_path = path
            self.icon_provider.set_project_root_path(self.project_root_path)
            parent_dir_path = os.path.dirname(path)
            project_dir_name = os.path.basename(path)
            self.file_system_model.setRootPath(parent_dir_path)
            root_index = self.file_system_model.index(parent_dir_path)
            self.tree_view.setRootIndex(root_index)
            for i in range(1, self.file_system_model.columnCount()):
                self.tree_view.setColumnHidden(i, True)
            QTimer.singleShot(50, lambda: self._filter_to_project_folder(root_index, project_dir_name, path))
        else:
            self.project_root_path = None
            self.icon_provider.set_project_root_path(None)
            self.file_system_model.setRootPath("")
            self.tree_view.setRootIndex(QModelIndex())

    def _filter_to_project_folder(self, root_index, project_dir_name, project_path):
        project_found = False
        for row in range(self.file_system_model.rowCount(root_index)):
            child_index = self.file_system_model.index(row, 0, root_index)
            if not child_index.isValid(): continue
            if self.file_system_model.fileName(child_index) != project_dir_name:
                self.tree_view.setRowHidden(row, root_index, True)
            else:
                project_found = True
        if project_found:
            project_index = self.file_system_model.index(project_path)
            if project_index.isValid():
                self.tree_view.expand(project_index)

    def _on_item_double_clicked(self, index: QModelIndex):
        if index.isValid() and not self.file_system_model.isDir(index):
            file_path = self.file_system_model.filePath(index)
            self.file_open_requested.emit(file_path)

    def _show_context_menu(self, position: QPoint):
        index = self.tree_view.indexAt(position)
        menu = QMenu()
        if index.isValid():
            clicked_path = self.file_system_model.filePath(index)
            target_dir = clicked_path if self.file_system_model.isDir(index) else os.path.dirname(clicked_path)
        else:
            clicked_path = self.project_root_path
            if not clicked_path: return
            target_dir = clicked_path
        menu.addAction(qta.icon('mdi.file-plus-outline'), "New File...", partial(self._action_new_file, target_dir))
        menu.addAction(qta.icon('mdi.folder-plus-outline'), "New Folder...",
                       partial(self._action_new_folder, target_dir))
        if index.isValid():
            menu.addSeparator()
            menu.addAction(qta.icon('mdi.pencil-outline'), "Rename...", partial(self._action_rename, clicked_path))
            menu.addAction(qta.icon('mdi.trash-can-outline', color='crimson'), "Delete",
                           partial(self._action_delete, clicked_path))
            menu.addSeparator()
            menu.addAction(qta.icon('mdi.content-copy'), "Copy Path",
                           partial(self.file_handler.copy_path_to_clipboard, clicked_path))
            menu.addAction(qta.icon('mdi.folder-search-outline'), "Reveal in File Explorer",
                           partial(self.file_handler.reveal_in_explorer, clicked_path))
        menu.exec(self.tree_view.viewport().mapToGlobal(position))

    def _action_new_file(self, base_path: str):
        name, ok = QInputDialog.getText(self, "New File", "Enter file name:")
        if ok and name:
            new_path = os.path.join(base_path, name)
            success, error = self.file_handler.create_file(new_path)
            if success:
                self.file_to_open_created.emit(new_path)
            else:
                QMessageBox.warning(self, "Error", error)

    def _action_new_folder(self, base_path: str):
        name, ok = QInputDialog.getText(self, "New Folder", "Enter folder name:")
        if ok and name:
            success, error = self.file_handler.create_folder(os.path.join(base_path, name))
            if not success: QMessageBox.warning(self, "Error", error)

    def _action_rename(self, path: str):
        current_name = os.path.basename(path)
        new_name, ok = QInputDialog.getText(self, "Rename", "Enter new name:", text=current_name)
        if ok and new_name and new_name != current_name:
            success, result = self.file_handler.rename_item(path, new_name)
            if not success: QMessageBox.warning(self, "Error", result)

    def _action_delete(self, path: str):
        item_name = os.path.basename(path)
        is_dir = os.path.isdir(path)
        reply = QMessageBox.question(self, "Confirm Delete",
                                     f"Are you sure you want to permanently delete this {'folder' if is_dir else 'file'}?\n\n'{item_name}'",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.Cancel,
                                     QMessageBox.StandardButton.Cancel)
        if reply == QMessageBox.StandardButton.Yes:
            success, error = self.file_handler.delete_item(path)
            if not success: QMessageBox.warning(self, "Error", error)


class MainWindow(QMainWindow):
    untitled_file_counter = 0
    _is_app_closing = False
    theme_changed_signal = pyqtSignal(str)

    def __init__(self, file_handler, theme_manager, debug_mode=False, parent=None):
        super().__init__(parent)
        self.file_handler = file_handler
        self.theme_manager = theme_manager
        self.debug_mode = debug_mode
        self.preferences_dialog = None
        log.info(f"PuffinPyEditor v{versioning.APP_VERSION} starting... (Debug: {self.debug_mode})")

        self._initialize_managers()
        self.puffin_api = PuffinPluginAPI(self)
        self.file_open_handlers = {}
        log.info("Core API initialized.")

        self.setWindowTitle(f"PuffinPyEditor - v{versioning.APP_VERSION}")
        self._load_window_geometry()
        self._create_core_widgets()
        self._create_core_actions()
        self._create_core_menu()
        self._create_toolbar()
        self._create_layout()
        self._create_statusbar()

        # *** FIX: Restore special loading logic for debug plugins ***
        plugins_to_ignore = []
        if self.debug_mode:
            try:
                from core_debug_tools.enhanced_exceptions.plugin_main import initialize as init_eh
                self.eh_instance = init_eh(self, sys.excepthook)
                log.info("Core debug tool 'Enhanced Exceptions' loaded manually.")
                plugins_to_ignore.append('enhanced_exceptions')
            except Exception as e:
                log.error(f"Failed to load core exception handler: {e}", exc_info=True)
                QMessageBox.critical(self, "Debug Tools Failed",
                                     f"Could not initialize core exception handler.\n\nError: {e}")

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
        self.lint_timer = QTimer(self)
        self.lint_timer.setSingleShot(True)
        self.lint_timer.setInterval(1500)
        self.auto_save_timer = QTimer(self)
        self.auto_save_timer.setSingleShot(True)

    def _load_window_geometry(self):
        size = self.settings.get("window_size", [1600, 1000])
        pos = self.settings.get("window_position")
        self.resize(QSize(size[0], size[1]))
        if pos:
            self.move(pos[0], pos[1])

    def _create_core_widgets(self):
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.tab_widget = QTabWidget()
        self.project_tabs = QTabWidget()
        for tab_widget, action in [(self.tab_widget, self._add_new_tab), (self.project_tabs, self._action_open_folder)]:
            button = QToolButton()
            button.setIcon(qta.icon('fa5s.plus'))
            button.setAutoRaise(True)
            button.clicked.connect(action)
            tab_widget.setCornerWidget(button, Qt.Corner.TopRightCorner)
            tab_widget.setDocumentMode(True)
            tab_widget.setTabsClosable(True)
            tab_widget.setMovable(True)

        self.file_tree_dock = QDockWidget("Project Explorer", self)
        self.file_tree_dock.setWidget(self.project_tabs)
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.file_tree_dock)

    def _create_core_actions(self):
        actions_map = {
            "new_file": ("&New File", self._add_new_tab, "Ctrl+N", 'fa5s.file'),
            "open_file": ("&Open File...", self._action_open_file_dialog, "Ctrl+O", 'fa5s.folder-open'),
            "open_folder": ("Open &Folder...", self._action_open_folder, None, 'fa5s.folder'),
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
            action.triggered.connect(cb)
            self.actions[key] = action

    def _create_core_menu(self):
        menu_bar = self.menuBar()
        self.file_menu = menu_bar.addMenu("&File")
        self.edit_menu = menu_bar.addMenu("&Edit")
        self.view_menu = menu_bar.addMenu("&View")
        self.tools_menu = menu_bar.addMenu("&Tools")
        self.help_menu = menu_bar.addMenu("&Help")

        self.file_menu.addActions([self.actions[k] for k in ["new_file", "open_file"]])
        self.recent_files_menu = self.file_menu.addMenu("Open &Recent")
        self.file_menu.addSeparator()
        self.file_menu.addActions([self.actions[k] for k in ["open_folder", "close_project"]])
        self.file_menu.addSeparator()
        self.file_menu.addActions([self.actions[k] for k in ["save", "save_as", "save_all"]])
        self.file_menu.addSeparator()
        self.file_menu.addAction(self.actions["preferences"])
        self.file_menu.addSeparator()
        self.file_menu.addAction(self.actions["exit"])

        self.theme_menu = self.view_menu.addMenu("&Themes")

        about_action = QAction("About PuffinPyEditor", self, triggered=self._show_about_dialog)
        github_action = QAction("View on GitHub", self, triggered=self._open_github_link)
        self.help_menu.addAction(about_action)
        self.help_menu.addAction(github_action)

    def _create_toolbar(self):
        self.main_toolbar = QToolBar("Main Toolbar")
        self.main_toolbar.setIconSize(QSize(18, 18))
        self.addToolBar(self.main_toolbar)
        self.main_toolbar.addActions([self.actions[k] for k in ["new_file", "open_file", "save"]])
        spacer = QWidget();
        spacer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self.main_toolbar.addWidget(spacer)
        self.main_toolbar.addAction(self.actions["preferences"])

    def _create_layout(self):
        layout = QHBoxLayout(self.central_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.tab_widget)

    def _create_statusbar(self):
        self.setStatusBar(QStatusBar(self))
        self.cursor_label = QLabel(" Ln 1, Col 1 ")
        self.statusBar().addPermanentWidget(self.cursor_label)

    def _connect_signals(self):
        self.project_tabs.currentChanged.connect(self._on_project_tab_changed)
        self.project_tabs.tabCloseRequested.connect(self._action_close_project_by_index)
        self.tab_widget.currentChanged.connect(self._on_tab_changed)
        self.tab_widget.tabCloseRequested.connect(self._action_close_tab_by_index)
        self.lint_timer.timeout.connect(self._trigger_file_linter)
        self.completion_manager.definition_found.connect(self._goto_definition_result)
        self.auto_save_timer.timeout.connect(self._auto_save_current_tab)

    def _apply_theme_and_icons(self, theme_id: str):
        self.theme_manager.set_theme(theme_id, QApplication.instance())
        self.theme_changed_signal.emit(theme_id)
        for action in self.actions.values():
            if icon_name := action.data():
                action.setIcon(qta.icon(icon_name))
        self._rebuild_theme_menu()
        for i in range(self.tab_widget.count()):
            widget = self.tab_widget.widget(i)
            if isinstance(widget, EditorWidget):
                widget.highlighter.rehighlight_document()
            elif hasattr(widget, 'update_theme'):
                widget.update_theme()

    def _rebuild_theme_menu(self):
        self.theme_menu.clear()
        group = QActionGroup(self)
        group.setExclusive(True)
        for theme_id, name in self.theme_manager.get_available_themes_for_ui().items():
            action = QAction(name, self, checkable=True,
                             triggered=lambda _, t_id=theme_id: self._on_theme_selected(t_id))
            action.setData(theme_id)
            action.setChecked(theme_id == self.theme_manager.current_theme_id)
            group.addAction(action)
            self.theme_menu.addAction(action)

    def _post_init_setup(self):
        self._initialize_project_views()
        self._update_window_title()

    def _initialize_project_views(self):
        active_project = self.project_manager.get_active_project_path()
        self.project_tabs.blockSignals(True)
        self.project_tabs.clear()
        open_projects = self.project_manager.get_open_projects()
        self.file_tree_dock.setVisible(len(open_projects) > 0)
        active_index = 0
        for i, path in enumerate(open_projects):
            tree = FileTreeViewWidget(self.file_handler, self.theme_manager, self)
            tree.file_open_requested.connect(self._action_open_file)
            tree.file_to_open_created.connect(self._add_new_tab)
            self.theme_changed_signal.connect(tree.update_theme)
            tree.set_project_root(path)
            tab_index = self.project_tabs.addTab(tree, os.path.basename(path))
            self.project_tabs.setTabToolTip(tab_index, path)
            if path == active_project: active_index = i
        self.project_tabs.setCurrentIndex(active_index)
        self.project_tabs.blockSignals(False)
        self._on_project_tab_changed(active_index if open_projects else -1)
        if self.tab_widget.count() == 0: self._add_new_tab(is_placeholder=True)

    def _add_new_tab(self, filepath=None, content="", is_placeholder=False):
        if self.tab_widget.count() == 1 and isinstance(self.tab_widget.widget(0), QLabel):
            self.tab_widget.removeTab(0)
        if is_placeholder:
            placeholder = QLabel("Open a file or create a new one to start.", alignment=Qt.AlignmentFlag.AlignCenter)
            placeholder.setObjectName("PlaceholderLabel")
            self.tab_widget.addTab(placeholder, "Welcome")
            self.tab_widget.setTabsClosable(False)
            return
        self.tab_widget.setTabsClosable(True)
        editor = EditorWidget(self.completion_manager, self)
        editor.set_filepath(filepath)
        editor.set_text(content)
        editor.cursor_position_display_updated.connect(
            lambda line, col: self.cursor_label.setText(f" Ln {line}, Col {col} "))
        editor.content_possibly_changed.connect(self._on_content_changed)
        if not filepath: self.untitled_file_counter += 1
        name = os.path.basename(filepath) if filepath else f"Untitled-{self.untitled_file_counter}"
        index = self.tab_widget.addTab(editor, name)
        self.tab_widget.setTabToolTip(index, filepath or f"Unsaved {name}")
        self.editor_tabs_data[editor] = {'filepath': filepath, 'original_hash': hash(content)}
        self.tab_widget.setCurrentWidget(editor)
        editor.text_area.setFocus()

    def _action_open_file(self, filepath: str, content: str = None):
        norm_path = os.path.normpath(filepath)
        for i in range(self.tab_widget.count()):
            widget = self.tab_widget.widget(i)
            if isinstance(widget, EditorWidget) and self.editor_tabs_data.get(widget, {}).get('filepath') == norm_path:
                self.tab_widget.setCurrentIndex(i)
                return
        if content is None:
            try:
                with open(norm_path, 'r', encoding='utf-8', errors='replace') as f:
                    content = f.read()
            except Exception as e:
                QMessageBox.critical(self, "Error Opening File", f"Could not read file: {e}");
                return
        self._add_new_tab(norm_path, content)

    def _action_open_file_dialog(self):
        filepath, content, error = self.file_handler.open_file_dialog()
        if error:
            QMessageBox.critical(self, "Error Opening File", error)
        elif filepath:
            self._action_open_file(filepath, content)

    def _action_open_folder(self):
        path = QFileDialog.getExistingDirectory(self, "Open Folder")
        if path:
            self.project_manager.open_project(path)
            self._initialize_project_views()

    def _action_close_project_by_index(self, index: int):
        if not (0 <= index < self.project_tabs.count()): return
        path = self.project_tabs.tabToolTip(index)
        self.project_manager.close_project(path)
        self._initialize_project_views()

    def _action_close_project(self):
        self._action_close_project_by_index(self.project_tabs.currentIndex())

    def _on_theme_selected(self, theme_id):
        self._apply_theme_and_icons(theme_id)

    def _on_tab_changed(self, index):
        self._update_window_title()

    def _on_content_changed(self):
        self._update_window_title()

    def _on_project_tab_changed(self, index):
        self._update_window_title()

    def _update_window_title(self):
        pass

    def _action_save_file(self):
        pass

    def _action_save_as(self):
        pass

    def _action_save_all(self):
        pass

    def _action_close_tab_by_index(self, index):
        pass

    def _update_recent_files_menu(self):
        pass

    def _action_open_recent_file(self):
        pass

    def _trigger_file_linter(self):
        pass

    def _show_about_dialog(self):
        pass

    def _open_github_link(self):
        pass

    def _auto_save_current_tab(self):
        pass

    def _on_editor_settings_changed(self):
        for i in range(self.tab_widget.count()):
            if isinstance(widget := self.tab_widget.widget(i), EditorWidget):
                widget.update_editor_settings()

    def _action_open_preferences(self):
        if self.preferences_dialog is None:
            self.preferences_dialog = PreferencesDialog(self.git_manager, self.github_manager, self.plugin_manager,
                                                        self)
            self.preferences_dialog.settings_changed_for_editor_refresh.connect(self._on_editor_settings_changed)
            self.preferences_dialog.theme_changed_signal.connect(self._apply_theme_and_icons)
        self.preferences_dialog.show()
        self.preferences_dialog.raise_()
        self.preferences_dialog.activateWindow()

    def _goto_definition_result(self, filepath: str, line: int, col: int):
        if not filepath:
            self.statusBar().showMessage("Definition not found", 3000);
            return
        norm_path = os.path.normpath(filepath)
        for i in range(self.tab_widget.count()):
            editor = self.tab_widget.widget(i)
            if isinstance(editor, EditorWidget) and self.editor_tabs_data.get(editor, {}).get('filepath') == norm_path:
                self.tab_widget.setCurrentIndex(i)
                editor.goto_line_and_column(line, col)
                return
        self._action_open_file(norm_path)
        QApplication.processEvents()
        editor = self.tab_widget.currentWidget()
        if isinstance(editor, EditorWidget) and self.editor_tabs_data.get(editor, {}).get('filepath') == norm_path:
            editor.goto_line_and_column(line, col)

    def set_project_root(self, path: str | None):
        self.project_manager.open_project(path)
        self._initialize_project_views()
```

### File: `/ui/preferences_dialog.py`

#### Linter Issues Found:
```

- L28 (F401) No message available

- L107 (E501) No message available

- L109 (E501) No message available

- L110 (E501) No message available

- L113 (E501) No message available

- L114 (E501) No message available

- L115 (E501) No message available

- L121 (E501) No message available

- L123 (E501) No message available

- L138 (E501) No message available

- L146 (E501) No message available

- L148 (E501) No message available

- L150 (E501) No message available

- L151 (E501) No message available

- L152 (E501) No message available

- L153 (E501) No message available

- L154 (E501) No message available

- L155 (E501) No message available

- L156 (E501) No message available

- L157 (E501) No message available

- L159 (E501) No message available

- L160 (E501) No message available

- L161 (E501) No message available

- L163 (E501) No message available

- L166 (E501) No message available

- L167 (E701) No message available

- L167 (E501) No message available

- L168 (E701) No message available

- L168 (E501) No message available

- L169 (E701) No message available

- L169 (E501) No message available

- L170 (E701) No message available

- L170 (E501) No message available

- L171 (E701) No message available

- L171 (E501) No message available

- L174 (E701) No message available

- L175 (E501) No message available

- L178 (E501) No message available

- L179 (E701) No message available

- L181 (E501) No message available

- L182 (E501) No message available

- L183 (W293) No message available

- L184 (E501) No message available

- L185 (E501) No message available

- L196 (E501) No message available

- L220 (E501) No message available

- L225 (E501) No message available

- L230 (E701) No message available

- L230 (E501) No message available

- L231 (E501) No message available

- L232 (E501) No message available

- L234 (E501) No message available

- L235 (E501) No message available

- L238 (E501) No message available

- L267 (E501) No message available

- L269 (E701) No message available

- L269 (E501) No message available

- L275 (E501) No message available

- L300 (E702) No message available

- L300 (E501) No message available

- L313 (E501) No message available

- L317 (E702) No message available

- L317 (E501) No message available

- L318 (E702) No message available

- L318 (E501) No message available

- L320 (E501) No message available

- L321 (E702) No message available

- L321 (E501) No message available

- L327 (E501) No message available

- L328 (E501) No message available

- L335 (E501) No message available

- L337 (E501) No message available

- L340 (E501) No message available

- L341 (E501) No message available

- L342 (E702) No message available

- L342 (E501) No message available

- L343 (E702) No message available

- L343 (E501) No message available

- L348 (E701) No message available

- L352 (E501) No message available

- L353 (E702) No message available

- L357 (E501) No message available

- L358 (E702) No message available

- L360 (E501) No message available

- L367 (E501) No message available

- L371 (E702) No message available

- L371 (E702) No message available

- L371 (E501) No message available

- L372 (E501) No message available

- L374 (E702) No message available

- L374 (E702) No message available

- L374 (E501) No message available

- L374 (E231) No message available

- L374 (E231) No message available

- L374 (E231) No message available

- L376 (E702) No message available

- L376 (E501) No message available

- L376 (E702) No message available

- L377 (E702) No message available

- L377 (E501) No message available

- L377 (E702) No message available

- L379 (E501) No message available

- L380 (E702) No message available

- L380 (E501) No message available

- L381 (E702) No message available

- L381 (E501) No message available

- L382 (E702) No message available

- L382 (E501) No message available

- L383 (E231) No message available

- L383 (E231) No message available

- L383 (E231) No message available

- L383 (E702) No message available

- L383 (E501) No message available

- L383 (E702) No message available

- L387 (E501) No message available

- L389 (E702) No message available

- L389 (E501) No message available

- L390 (E702) No message available

- L390 (E501) No message available

- L391 (E702) No message available

- L391 (E501) No message available

- L393 (E501) No message available

- L394 (E501) No message available

- L396 (E702) No message available

- L396 (E501) No message available

- L397 (E702) No message available

- L397 (E501) No message available

- L399 (E702) No message available

- L399 (E702) No message available

- L399 (E501) No message available

- L404 (E501) No message available

- L407 (E501) No message available

- L411 (E702) No message available

- L411 (E501) No message available

- L412 (E702) No message available

- L412 (E501) No message available

- L413 (E702) No message available

- L413 (E501) No message available

- L414 (E702) No message available

- L414 (E501) No message available

- L414 (E702) No message available

- L414 (E702) No message available

- L415 (E702) No message available

- L415 (E501) No message available

- L416 (E702) No message available

- L416 (E501) No message available

- L417 (E501) No message available

- L418 (E501) No message available

- L420 (E501) No message available

- L421 (E501) No message available

- L423 (E501) No message available

- L424 (E702) No message available

- L424 (E501) No message available

- L425 (E702) No message available

- L425 (E501) No message available

- L426 (E702) No message available

- L426 (E501) No message available

- L427 (E702) No message available

- L427 (E501) No message available

- L428 (E501) No message available

- L432 (E501) No message available

- L432 (E701) No message available

- L433 (E501) No message available

- L434 (E501) No message available

- L436 (E501) No message available

- L441 (E702) No message available

- L441 (E501) No message available

- L444 (E701) No message available

- L444 (E501) No message available

- L447 (E702) No message available

- L450 (E501) No message available

- L451 (E701) No message available

- L452 (E501) No message available

- L453 (E702) No message available

- L453 (E501) No message available

- L456 (E501) No message available

- L458 (E501) No message available

- L461 (E701) No message available

- L462 (E501) No message available

- L464 (E701) No message available

- L464 (E501) No message available

- L465 (E701) No message available

- L465 (E501) No message available

- L468 (E701) No message available

- L469 (E702) No message available

- L469 (E501) No message available

- L472 (E701) No message available

- L473 (E501) No message available

- L473 (E702) No message available

- L475 (E501) No message available

- L476 (E701) No message available

- L477 (E701) No message available

- L478 (E701) No message available

- L478 (E501) No message available

- L481 (E701) No message available

- L482 (E501) No message available

- L487 (E701) No message available

- L488 (E501) No message available

- L489 (E501) No message available

- L492 (E501) No message available

- L493 (E702) No message available

- L495 (E501) No message available

- L495 (E701) No message available

- L496 (E702) No message available

- L496 (E501) No message available

- L497 (E702) No message available

- L497 (E501) No message available

- L498 (E501) No message available

- L498 (E701) No message available

- L499 (E702) No message available

- L504 (E501) No message available

- L506 (E702) No message available

- L510 (E701) No message available

- L512 (E501) No message available

- L513 (E501) No message available

- L514 (E501) No message available

- L515 (E501) No message available

- L516 (E701) No message available

- L516 (E501) No message available

- L517 (E702) No message available

- L520 (E702) No message available

- L520 (E501) No message available

- L520 (E702) No message available

- L521 (E501) No message available

- L522 (E702) No message available

- L522 (E501) No message available

- L523 (E701) No message available

- L523 (E501) No message available

- L525 (E701) No message available

- L527 (E701) No message available

- L528 (E701) No message available

- L532 (E501) No message available

- L532 (E701) No message available

- L533 (E702) No message available

- L533 (E501) No message available

- L533 (E702) No message available

- L536 (E702) No message available

- L538 (E501) No message available

- L539 (E501) No message available

- L540 (E501) No message available

- L542 (E501) No message available

- L543 (W293) No message available

- L551 (E702) No message available

- L551 (E702) No message available

- L553 (E501) No message available

- L556 (E702) No message available

- L556 (E501) No message available

- L557 (E702) No message available

- L557 (E501) No message available

- L567 (E702) No message available

- L567 (E501) No message available

- L568 (E501) No message available

- L569 (E702) No message available

- L569 (E501) No message available

- L571 (E701) No message available

- L571 (E501) No message available

- L572 (E501) No message available

- L573 (E501) No message available

- L576 (W293) No message available

- L580 (E701) No message available

- L581 (E701) No message available

- L583 (E501) No message available

- L587 (E701) No message available

- L590 (E501) No message available

- L592 (W293) No message available

- L595 (E501) No message available

- L600 (E702) No message available

- L602 (W293) No message available

- L607 (E702) No message available

- L607 (E501) No message available

- L608 (E702) No message available

- L608 (E501) No message available

- L609 (E702) No message available

- L609 (E501) No message available

- L614 (E702) No message available

- L614 (E501) No message available

- L616 (E702) No message available

- L616 (E501) No message available

- L618 (E702) No message available

- L618 (E501) No message available

- L625 (E702) No message available

- L625 (E501) No message available

- L628 (E501) No message available

- L630 (W293) No message available

- L633 (W293) No message available

- L636 (E501) No message available

- L637 (E501) No message available

- L638 (E501) No message available

- L639 (E501) No message available

- L644 (E501) No message available

- L645 (E501) No message available

- L646 (E702) No message available

- L646 (E501) No message available

- L647 (E701) No message available

- L649 (W293) No message available

- L653 (E501) No message available

- L656 (E501) No message available

- L660 (E501) No message available

- L661 (E501) No message available

- L661 (E702) No message available

- L662 (E702) No message available

- L662 (E501) No message available

- L663 (E702) No message available

- L663 (E501) No message available

- L667 (E702) No message available

- L667 (E501) No message available

- L671 (E501) No message available

- L672 (E702) No message available

- L672 (E501) No message available

- L673 (E701) No message available

- L673 (E501) No message available

- L673 (E702) No message available

- L678 (E501) No message available

- L681 (E701) No message available

- L681 (E501) No message available

- L681 (E702) No message available

- L683 (E501) No message available

- L685 (E701) No message available

- L687 (E501) No message available

- L688 (E501) No message available

- L689 (E701) No message available

- L689 (E702) No message available

- L689 (E501) No message available

- L689 (E702) No message available

- L690 (E701) No message available

- L690 (E501) No message available

- L692 (E701) No message available

- L692 (E501) No message available

- L695 (E501) No message available

- L695 (E701) No message available

- L696 (E501) No message available

- L697 (E501) No message available

- L698 (E701) No message available

- L698 (E702) No message available

- L698 (E501) No message available

- L701 (E701) No message available

- L703 (E701) No message available

- L703 (E501) No message available

- L703 (E702) No message available

- L704 (E501) No message available

- L706 (E501) No message available

- L707 (E701) No message available

- L707 (E702) No message available

- L707 (E501) No message available

- L711 (E702) No message available

- L715 (W293) No message available

- L717 (E501) No message available

- L721 (W293) No message available

- L727 (E501) No message available

- L739 (E501) No message available

- L741 (W293) No message available

- L749 (E261) No message available

- L751 (W293) No message available

- L760 (E261) No message available

- L760 (W292) No message available

```


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
    import winshell

import qtawesome as qta
from utils.logger import log
from utils.helpers import get_startup_shortcut_path
from app_core.settings_manager import settings_manager
from app_core.theme_manager import theme_manager
from app_core.github_manager import GitHubManager
from app_core.source_control_manager import SourceControlManager
from app_core.plugin_manager import PluginManager, Plugin
from .theme_editor_dialog import ThemeEditorDialog


class AuthDialog(QDialog):
    def __init__(self, user_code: str, verification_uri: str,
                 parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setWindowTitle("GitHub Device Authorization")
        layout = QVBoxLayout(self)
        layout.addWidget(
            QLabel("Please authorize PuffinPyEditor in your browser.")
        )
        url_label = QLabel(
            f"1. Open: <a href='{verification_uri}'>{verification_uri}</a>"
        )
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
                 parent: Optional[QWidget] = None):
        super().__init__(parent)
        log.info("PreferencesDialog initializing...")
        self.setWindowTitle("Preferences")
        self.setMinimumSize(QSize(850, 700))
        self.git_manager = git_manager
        self.github_manager = github_manager
        self.plugin_manager = plugin_manager
        self.original_settings: dict[str, Any] = {}
        self.original_git_config: dict[str, str] = {}
        self.staged_repos: list[dict] = []
        self.staged_active_repo_id: Optional[str] = None
        self.current_repo_id_in_form: Optional[str] = None
        self.auth_dialog: Optional[AuthDialog] = None
        self.theme_editor_dialog_instance: Optional[ThemeEditorDialog] = None
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
        buttons = (QDialogButtonBox.StandardButton.Ok |
                   QDialogButtonBox.StandardButton.Cancel |
                   QDialogButtonBox.StandardButton.Apply)
        self.button_box = QDialogButtonBox(buttons)
        self.main_layout.addWidget(self.button_box)

    def _connect_global_signals(self):
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        self.button_box.button(
            QDialogButtonBox.StandardButton.Apply).clicked.connect(self.apply_settings)

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
            new_repo = {
                "id": new_repo_id, "name": data.get("name"), "owner": owner, "repo": repo_name
            }
            self.staged_repos.append(new_repo)
            QMessageBox.information(
                self, "Success", f"Repository '{repo_name}' created on GitHub."
            )
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
        self.python_path_edit.setText(settings_manager.get("python_interpreter_path", sys.executable))
        self.run_in_background_checkbox.setChecked(settings_manager.get("run_in_background", False))
        self.nsis_path_edit.setText(settings_manager.get("nsis_path", ""))
        self.cleanup_build_checkbox.setChecked(settings_manager.get("cleanup_after_build", True))
        self.staged_repos = [r.copy() for r in settings_manager.get("source_control_repos", [])]
        self.staged_active_repo_id = settings_manager.get("active_update_repo_id")
        self._populate_repo_list()
        self.plugins_repo_edit.setText(settings_manager.get("plugins_distro_repo", "Stelliro/puffin-plugins"))

    def _connect_ui_changed_signals(self):
        for widget in self.findChildren((QComboBox, QSpinBox, QCheckBox, QFontComboBox, QLineEdit)):
            if isinstance(widget, QComboBox): widget.currentIndexChanged.connect(self._on_ui_setting_changed)
            elif isinstance(widget, QFontComboBox): widget.currentFontChanged.connect(self._on_ui_setting_changed)
            elif isinstance(widget, QSpinBox): widget.valueChanged.connect(self._on_ui_setting_changed)
            elif isinstance(widget, QCheckBox): widget.stateChanged.connect(self._on_ui_setting_changed)
            elif isinstance(widget, QLineEdit): widget.textChanged.connect(self._on_ui_setting_changed)

    def _on_ui_setting_changed(self, *args):
        if self.is_loading or not self.isVisible(): return
        self.button_box.button(QDialogButtonBox.StandardButton.Apply).setEnabled(True)

    def apply_settings(self):
        apply_button = self.button_box.button(QDialogButtonBox.StandardButton.Apply)
        if not apply_button.isEnabled(): return

        if sys.platform == "win32" and self.run_in_background_checkbox.isChecked() != self.original_settings.get("run_in_background", False):
            self._manage_startup_shortcut(self.run_in_background_checkbox.isChecked())
        
        new_name, new_email = self.git_user_name_edit.text().strip(), self.git_user_email_edit.text().strip()
        if new_name != self.original_git_config.get('name') or new_email != self.original_git_config.get('email'):
            self.git_manager.set_git_config(new_name, new_email)
            self.original_git_config = {'name': new_name, 'email': new_email}

        self._save_repo_form_to_staged()
        settings_to_set = {
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
            "run_in_background": self.run_in_background_checkbox.isChecked(),
            "nsis_path": self.nsis_path_edit.text().strip(),
            "cleanup_after_build": self.cleanup_build_checkbox.isChecked(),
            "source_control_repos": self.staged_repos,
            "active_update_repo_id": self.staged_active_repo_id,
            "plugins_distro_repo": self.plugins_repo_edit.text().strip(),
        }
        for key, value in settings_to_set.items():
            settings_manager.set(key, value, save_immediately=False)
        settings_manager.save()

        self.theme_changed_signal.emit(self.theme_combo.currentData())
        self.settings_changed_for_editor_refresh.emit()
        self.original_settings = settings_manager.settings.copy()
        apply_button.setEnabled(False)

        if self.restart_needed:
            QMessageBox.information(self, "Restart Required", "Some changes require a restart of the application to take effect.")
            self.restart_needed = False
        log.info("Applied settings from Preferences dialog.")

    def accept(self):
        if self.button_box.button(QDialogButtonBox.StandardButton.Apply).isEnabled():
            self.apply_settings()
        super().accept()

    def reject(self):
        if self.auth_dialog and self.auth_dialog.isVisible(): self.auth_dialog.reject()
        if self.button_box.button(QDialogButtonBox.StandardButton.Apply).isEnabled():
            if QMessageBox.question(self, "Unsaved Changes", "Discard unsaved changes?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.No) == QMessageBox.StandardButton.No:
                return
        if self.theme_combo.currentData() != self.original_settings.get("last_theme_id"):
            self.theme_changed_signal.emit(self.original_settings.get("last_theme_id"))
        super().reject()

    def _create_layout_in_groupbox(self, title: str, parent_layout: QVBoxLayout) -> QFormLayout:
        group = QGroupBox(title)
        parent_layout.addWidget(group)
        layout = QFormLayout(group)
        return layout

    def _create_appearance_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(15)
        theme_layout = self._create_layout_in_groupbox("Theming", layout)
        self.theme_combo = QComboBox()
        self.edit_themes_button = QPushButton("Customize Themes...")
        self.edit_themes_button.clicked.connect(self._open_theme_editor_dialog)
        theme_layout.addRow("Theme:", self.theme_combo)
        theme_layout.addRow("", self.edit_themes_button)
        font_layout = self._create_layout_in_groupbox("Editor Font", layout)
        self.font_family_combo = QFontComboBox()
        self.font_size_spinbox = QSpinBox()
        self.font_size_spinbox.setRange(6, 72)
        font_layout.addRow("Font Family:", self.font_family_combo)
        font_layout.addRow("Font Size:", self.font_size_spinbox)
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

    def _open_theme_editor_dialog(self):
        if not self.theme_editor_dialog_instance:
            self.theme_editor_dialog_instance = ThemeEditorDialog(self)
            self.theme_editor_dialog_instance.custom_themes_changed.connect(self._repopulate_theme_combo)
        self.theme_editor_dialog_instance.exec()

    def _create_editor_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
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
        self.indent_style_combo = QComboBox()
        self.indent_style_combo.addItems(["Spaces", "Tabs"])
        self.indent_width_spinbox = QSpinBox()
        self.indent_width_spinbox.setRange(1, 16)
        indent_layout.addRow("Indent Using:", self.indent_style_combo)
        indent_layout.addRow("Indent/Tab Width:", self.indent_width_spinbox)
        file_layout = self._create_layout_in_groupbox("File Handling", layout)
        self.auto_save_checkbox = QCheckBox("Enable auto-save")
        self.auto_save_delay_spinbox = QSpinBox()
        self.auto_save_delay_spinbox.setRange(1, 60); self.auto_save_delay_spinbox.setSuffix(" seconds")
        self.max_recent_files_spinbox = QSpinBox()
        self.max_recent_files_spinbox.setRange(1, 50)
        file_layout.addRow(self.auto_save_checkbox)
        file_layout.addRow("Auto-Save Delay:", self.auto_save_delay_spinbox)
        file_layout.addRow("Max Recent Files:", self.max_recent_files_spinbox)
        layout.addStretch()
        self.tab_widget.addTab(tab, qta.icon('fa5s.edit'), "Editor")

    def _create_run_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(15)
        run_layout = self._create_layout_in_groupbox("Execution Environment", layout)
        run_layout.setRowWrapPolicy(QFormLayout.RowWrapPolicy.WrapAllRows)
        path_layout = QHBoxLayout()
        self.python_path_edit = QLineEdit()
        browse_button = QPushButton("Browse..."); browse_button.clicked.connect(self._browse_for_python)
        path_layout.addWidget(self.python_path_edit, 1); path_layout.addWidget(browse_button)
        run_layout.addRow("Python Interpreter Path:", path_layout)
        info = QLabel("This interpreter is used for running scripts (F5) and code analysis.")
        info.setWordWrap(True); info.setStyleSheet("font-size: 9pt; color: grey;")
        run_layout.addRow(info)
        layout.addStretch()
        self.tab_widget.addTab(tab, qta.icon('fa5s.play'), "Run")

    def _browse_for_python(self):
        filter_str = "Executables (*.exe)" if sys.platform == "win32" else "All Files (*)"
        if path := QFileDialog.getOpenFileName(self, "Select Python Interpreter", "", filter_str)[0]:
            self.python_path_edit.setText(path)

    def _create_system_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(15)
        system_layout = self._create_layout_in_groupbox("System Integration", layout)
        system_layout.setRowWrapPolicy(QFormLayout.RowWrapPolicy.WrapAllRows)
        self.run_in_background_checkbox = QCheckBox("Launch at startup and run in background")
        if sys.platform != "win32":
            self.run_in_background_checkbox.setEnabled(False)
            self.run_in_background_checkbox.setToolTip("This feature is only available on Windows.")
        info = QLabel("Adds a tray icon that starts with Windows, allowing PuffinPyEditor to open faster.")
        info.setWordWrap(True); info.setStyleSheet("font-size: 9pt; color: grey;")
        system_layout.addRow(self.run_in_background_checkbox); system_layout.addRow(info)
        layout.addStretch()
        self.tab_widget.addTab(tab, qta.icon('fa5s.desktop'), "System")

    def _manage_startup_shortcut(self, create: bool):
        if not (shortcut_path := get_startup_shortcut_path()): return
        try:
            if create:
                if not getattr(sys, 'frozen', False):
                    QMessageBox.warning(self, "Developer Mode", "Startup feature only works in a packaged application.")
                    self.run_in_background_checkbox.setChecked(False); return
                install_dir = os.path.dirname(sys.executable)
                target_path = os.path.join(install_dir, "PuffinPyTray.exe")
                if not os.path.exists(target_path):
                    QMessageBox.warning(self, "File Not Found", f"Could not find PuffinPyTray.exe in {install_dir}")
                    self.run_in_background_checkbox.setChecked(False); return
                with winshell.shortcut(shortcut_path) as s:
                    s.path, s.description, s.working_directory = target_path, "PuffinPyEditor Background App", install_dir
                log.info(f"Created startup shortcut: {shortcut_path}")
            elif os.path.exists(shortcut_path):
                os.remove(shortcut_path)
                log.info(f"Removed startup shortcut: {shortcut_path}")
        except Exception as e:
            log.error(f"Failed to manage startup shortcut: {e}")
            QMessageBox.critical(self, "Error", f"Could not modify startup shortcut.\n{e}")
            self.run_in_background_checkbox.setChecked(not create)

    def _create_source_control_tab(self):
        tab = QWidget(); top_layout = QVBoxLayout(tab); top_layout.setSpacing(15)
        gh_form_layout = self._create_layout_in_groupbox("GitHub Account", top_layout)
        gh_form_layout.setRowWrapPolicy(QFormLayout.RowWrapPolicy.WrapAllRows)
        auth_widget = QWidget(); auth_layout = QHBoxLayout(auth_widget); auth_layout.setContentsMargins(0,0,0,0)
        self.auth_status_label = QLabel("Not logged in.")
        self.auth_button = QPushButton("Login to GitHub"); self.logout_button = QPushButton("Logout"); self.logout_button.hide()
        auth_layout.addWidget(self.auth_status_label, 1); auth_layout.addWidget(self.auth_button); auth_layout.addWidget(self.logout_button)
        gh_form_layout.addRow("Status:", auth_widget)
        git_form_layout = self._create_layout_in_groupbox("Local Git Configuration", top_layout)
        self.git_user_name_edit = QLineEdit(); self.git_user_name_edit.setPlaceholderText("Name for commits")
        self.git_user_email_edit = QLineEdit(); self.git_user_email_edit.setPlaceholderText("Email for commits")
        branch_fix_button = QPushButton("Set Default to 'main' Globally"); branch_btn_layout = QHBoxLayout()
        branch_btn_layout.setContentsMargins(0,0,0,0); branch_btn_layout.addWidget(branch_fix_button); branch_btn_layout.addStretch()
        git_form_layout.addRow("Author Name:", self.git_user_name_edit)
        git_form_layout.addRow("Author Email:", self.git_user_email_edit)
        git_form_layout.addRow("Default Branch:", branch_btn_layout)
        build_form_layout = self._create_layout_in_groupbox("Build Tools", top_layout)
        nsis_path_layout = QHBoxLayout()
        self.nsis_path_edit = QLineEdit(); self.nsis_path_edit.setPlaceholderText("e.g., C:\\Program Files (x86)\\NSIS\\makensis.exe")
        browse_nsis_button = QPushButton("Browse..."); browse_nsis_button.clicked.connect(self._browse_for_nsis)
        nsis_path_layout.addWidget(self.nsis_path_edit, 1); nsis_path_layout.addWidget(browse_nsis_button)
        build_form_layout.addRow("NSIS `makensis.exe` Path:", nsis_path_layout)
        self.cleanup_build_checkbox = QCheckBox("Automatically clean up temporary build files")
        self.cleanup_build_checkbox.setToolTip("Deletes the 'build/' folder after a successful installer creation.")
        build_form_layout.addRow("", self.cleanup_build_checkbox)
        update_group = QGroupBox("Plugin Distribution & Update Repositories"); update_layout = QVBoxLayout(update_group)
        splitter = QSplitter(Qt.Orientation.Horizontal); update_layout.addWidget(splitter, 1)
        left_pane, right_pane = self._create_repo_management_widgets()
        splitter.addWidget(left_pane); splitter.addWidget(right_pane); splitter.setSizes([250, 400])
        top_layout.addWidget(update_group, 1)
        self.tab_widget.addTab(tab, qta.icon('fa5b.git-alt'), "Source Control")
        self.auth_button.clicked.connect(self.github_manager.start_device_flow)
        self.logout_button.clicked.connect(self._logout_github)
        branch_fix_button.clicked.connect(self.git_manager.set_default_branch_to_main)

    def _browse_for_nsis(self):
        if path := QFileDialog.getOpenFileName(self, "Select makensis.exe", "", "Executable (makensis.exe)")[0]:
            self.nsis_path_edit.setText(path)

    def _create_repo_management_widgets(self) -> tuple[QWidget, QWidget]:
        left_pane, right_pane = QWidget(), QWidget(); left_layout = QVBoxLayout(left_pane)
        self.right_pane_layout = QVBoxLayout(right_pane); self.repo_list_widget = QListWidget()
        repo_btn_layout = QHBoxLayout(); create_repo_btn, add_repo_btn, remove_repo_btn = QPushButton("Create..."), QPushButton("Add..."), QPushButton("Remove")
        repo_btn_layout.addStretch(); repo_btn_layout.addWidget(create_repo_btn); repo_btn_layout.addWidget(add_repo_btn); repo_btn_layout.addWidget(remove_repo_btn)
        left_layout.addWidget(self.repo_list_widget); left_layout.addLayout(repo_btn_layout)
        self.repo_form_widget = QWidget(); repo_form_layout = QFormLayout(self.repo_form_widget)
        self.repo_name_edit, self.repo_owner_edit, self.repo_repo_edit = QLineEdit(), QLineEdit(), QLineEdit()
        self.repo_active_checkbox = QCheckBox("Set as Primary (for updates & publishing)")
        repo_form_layout.addRow("Friendly Name:", self.repo_name_edit)
        repo_form_layout.addRow("Owner (e.g., 'Stelliro'):", self.repo_owner_edit)
        repo_form_layout.addRow("Repository (e.g., 'PuffinPyEditor'):", self.repo_repo_edit)
        repo_form_layout.addRow("", self.repo_active_checkbox)
        self.repo_placeholder_label = QLabel("\nSelect or add a repository to configure it.")
        self.repo_placeholder_label.setAlignment(Qt.AlignmentFlag.AlignCenter); self.repo_placeholder_label.setStyleSheet("color: grey;")
        self.right_pane_layout.addWidget(self.repo_placeholder_label, 1); self.right_pane_layout.addWidget(self.repo_form_widget)
        create_repo_btn.clicked.connect(self._action_create_repo); add_repo_btn.clicked.connect(self._action_add_repo)
        remove_repo_btn.clicked.connect(self._action_remove_repo); self.repo_list_widget.currentItemChanged.connect(self._on_repo_selection_changed)
        self.repo_active_checkbox.toggled.connect(self._on_active_checkbox_toggled)
        return left_pane, right_pane

    def _action_create_repo(self):
        if not (name := QInputDialog.getText(self, "Create New Repository", "Enter a name for the new repository:")[0]): return
        desc = QInputDialog.getText(self, "Create New Repository", "Description (optional):")[0]
        is_private = QMessageBox.question(self, "Visibility", "Make this repository private?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.No) == QMessageBox.StandardButton.Yes
        self.github_manager.create_repo(name, desc, is_private)
        QMessageBox.information(self, "In Progress", f"Attempting to create '{name}' on GitHub...")

    def _populate_git_config_fields(self, name: str, email: str):
        log.debug(f"Populating Git config: Name='{name}', Email='{email}'")
        self.original_git_config = {'name': name, 'email': email}
        self.git_user_name_edit.setText(name); self.git_user_email_edit.setText(email)

    def _handle_git_success(self, message: str, data: dict):
        if "Default branch" in message: QMessageBox.information(self, "Success", message)

    def _logout_github(self):
        self.github_manager.logout(); self._update_auth_status()

    def _update_auth_status(self):
        user, is_logged_in = self.github_manager.get_authenticated_user(), False
        if user: is_logged_in = True
        self.auth_status_label.setText(f"Logged in as: <b>{user}</b>" if is_logged_in else "Not logged in.")
        self.auth_button.setVisible(not is_logged_in); self.logout_button.setVisible(is_logged_in)

    def _on_device_code_ready(self, data: dict):
        self.auth_dialog = AuthDialog(data['user_code'], data['verification_uri'], self)
        self.auth_dialog.show()
        self.github_manager.poll_for_token(data['device_code'], data['interval'], data['expires_in'])

    def _on_auth_successful(self, username: str):
        if self.auth_dialog: self.auth_dialog.accept()
        QMessageBox.information(self, "Success", f"Successfully logged in as {username}.")
        self._update_auth_status()
        if not self.git_user_name_edit.text(): self.git_user_name_edit.setText(username)
        if not self.git_user_email_edit.text(): self.git_user_email_edit.setPlaceholderText(f"e.g., {username}@users.noreply.github.com")

    def _on_auth_failed(self, error: str):
        if self.auth_dialog: self.auth_dialog.reject()
        QMessageBox.critical(self, "Authentication Failed", error); self._update_auth_status()

    def _on_auth_polling_lapsed(self):
        if self.auth_dialog: self.auth_dialog.reject()
        QMessageBox.warning(self, "Login Expired", "The login code has expired. Please try again."); self._update_auth_status()

    def _on_repo_selection_changed(self, current: QListWidgetItem, previous: QListWidgetItem):
        if previous: self._save_repo_form_to_staged()
        if not current: self._clear_repo_form()
        else: self._load_staged_to_repo_form(current.data(Qt.ItemDataRole.UserRole))

    def _on_active_checkbox_toggled(self, checked: bool):
        if not self.current_repo_id_in_form: return
        self.staged_active_repo_id = self.current_repo_id_in_form if checked else None
        self._populate_repo_list(select_repo_id=self.current_repo_id_in_form)
        self._on_ui_setting_changed()

    def _save_repo_form_to_staged(self):
        if not self.current_repo_id_in_form: return
        if repo := next((r for r in self.staged_repos if r.get("id") == self.current_repo_id_in_form), None):
            repo.update({'name': self.repo_name_edit.text().strip(), 'owner': self.repo_owner_edit.text().strip(), 'repo': self.repo_repo_edit.text().strip()})

    def _load_staged_to_repo_form(self, repo_id: str):
        if not (repo_data := next((r for r in self.staged_repos if r.get("id") == repo_id), None)):
            self._clear_repo_form(); return
        self.current_repo_id_in_form = repo_id
        for w in [self.repo_name_edit, self.repo_owner_edit, self.repo_repo_edit, self.repo_active_checkbox]: w.blockSignals(True)
        self.repo_name_edit.setText(repo_data.get("name", "")); self.repo_owner_edit.setText(repo_data.get("owner", ""))
        self.repo_repo_edit.setText(repo_data.get("repo", "")); self.repo_active_checkbox.setChecked(self.staged_active_repo_id == repo_id)
        for w in [self.repo_name_edit, self.repo_owner_edit, self.repo_repo_edit, self.repo_active_checkbox]: w.blockSignals(False)
        self.repo_placeholder_label.hide(); self.repo_form_widget.show()

    def _action_add_repo(self):
        self._save_repo_form_to_staged()
        new_id = str(uuid.uuid4())
        self.staged_repos.append({"id": new_id, "name": "New Repository", "owner": "", "repo": ""})
        self._populate_repo_list(select_repo_id=new_id)
        self.repo_name_edit.setFocus(); self.repo_name_edit.selectAll()
        self._on_ui_setting_changed()

    def _action_remove_repo(self):
        if not (item := self.repo_list_widget.currentItem()): return
        repo_id = item.data(Qt.ItemDataRole.UserRole)
        repo = next((r for r in self.staged_repos if r.get("id") == repo_id), None)
        repo_name = f"'{repo.get('owner')}/{repo.get('repo')}'" if repo else f"'{item.text()}'"
        if QMessageBox.question(self, "Confirm Remove", f"Remove {repo_name} from this list? This does not delete it from GitHub.", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.Cancel) == QMessageBox.StandardButton.Yes:
            self.staged_repos = [r for r in self.staged_repos if r.get("id") != repo_id]
            if self.staged_active_repo_id == repo_id: self.staged_active_repo_id = None
            self._populate_repo_list(); self._on_ui_setting_changed()

    def _populate_repo_list(self, select_repo_id: Optional[str] = None):
        self.repo_list_widget.blockSignals(True); self.repo_list_widget.clear(); item_to_select = None
        for repo in sorted(self.staged_repos, key=lambda r: r.get('name', '').lower()):
            item = QListWidgetItem(repo.get("name")); item.setData(Qt.ItemDataRole.UserRole, repo.get("id"))
            if repo.get("id") == self.staged_active_repo_id: item.setIcon(qta.icon('fa5s.star', color='gold'))
            self.repo_list_widget.addItem(item)
            if repo.get("id") == select_repo_id: item_to_select = item
        self.repo_list_widget.blockSignals(False)
        if item_to_select: self.repo_list_widget.setCurrentItem(item_to_select)
        else: self._clear_repo_form()

    def _clear_repo_form(self):
        self.current_repo_id_in_form = None
        for w in [self.repo_name_edit, self.repo_owner_edit, self.repo_repo_edit]: w.clear()
        self.repo_active_checkbox.setChecked(False); self.repo_placeholder_label.show(); self.repo_form_widget.hide()

    def _create_plugins_tab(self):
        tab_container = QWidget(); layout = QVBoxLayout(tab_container)
        plugins_tabs = QTabWidget()
        plugins_tabs.addTab(self._create_plugins_manage_tab(), qta.icon('fa5s.tasks'), "Manage")
        plugins_tabs.addTab(self._create_plugins_install_tab(), qta.icon('fa5s.plus-circle'), "Install / Uninstall")
        plugins_tabs.addTab(self._create_plugins_options_tab(), qta.icon('fa5s.cogs'), "Options")
        layout.addWidget(plugins_tabs)
        self.tab_widget.addTab(tab_container, qta.icon('fa5s.puzzle-piece'), "Plugins")
    
    def _populate_all_plugin_lists(self):
        self._populate_manage_plugins_list()
        self._populate_install_plugins_list()
        self._populate_options_plugins_list()

    # --- Plugin Management Tab ---
    def _create_plugins_manage_tab(self) -> QWidget:
        widget = QWidget(); layout = QVBoxLayout(widget); layout.setSpacing(10)
        self.manage_plugins_list = QListWidget()
        self.manage_plugins_list.itemChanged.connect(self._on_plugin_enabled_changed)
        layout.addWidget(self.manage_plugins_list)
        buttons_layout = QHBoxLayout()
        reload_button = QPushButton("Reload Selected"); reload_button.setIcon(qta.icon('fa5s.sync-alt'))
        reload_all_button = QPushButton("Reload All Plugins"); reload_all_button.setIcon(qta.icon('fa5s.sync-alt'))
        buttons_layout.addStretch()
        buttons_layout.addWidget(reload_button)
        buttons_layout.addWidget(reload_all_button)
        layout.addLayout(buttons_layout)
        reload_button.clicked.connect(self._reload_selected_plugin)
        reload_all_button.clicked.connect(self._reload_all_plugins)
        return widget

    def _populate_manage_plugins_list(self):
        self.manage_plugins_list.blockSignals(True); self.manage_plugins_list.clear()
        for plugin in sorted(self.plugin_manager.get_all_plugins(), key=lambda p: p.name.lower()):
            item = QListWidgetItem(f"{plugin.name} v{plugin.version}"); item.setData(Qt.ItemDataRole.UserRole, plugin.id)
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            if plugin.is_core: item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsUserCheckable)
            item.setCheckState(Qt.CheckState.Checked if plugin.enabled else Qt.CheckState.Unchecked)
            item.setToolTip(f"ID: {plugin.id}\nSource: {plugin.source_type}\nStatus: {plugin.status_reason}")
            self.manage_plugins_list.addItem(item)
        self.manage_plugins_list.blockSignals(False)
    
    def _on_plugin_enabled_changed(self, item: QListWidgetItem):
        plugin_id = item.data(Qt.ItemDataRole.UserRole)
        is_enabled = item.checkState() == Qt.CheckState.Checked
        if is_enabled: self.plugin_manager.enable_plugin(plugin_id)
        else: self.plugin_manager.disable_plugin(plugin_id)
        self.restart_needed = True
        QMessageBox.information(self, "Reload Recommended", f"Plugin '{item.text()}' state changed. A restart or reload is recommended.")
        self._populate_all_plugin_lists()

    def _reload_selected_plugin(self):
        if not (item := self.manage_plugins_list.currentItem()): return
        plugin_id = item.data(Qt.ItemDataRole.UserRole)
        self.plugin_manager.reload_plugin(plugin_id)
        QMessageBox.information(self, "Success", f"Plugin '{item.text()}' reloaded.")
        self._populate_all_plugin_lists()
    
    def _reload_all_plugins(self):
        self.plugin_manager.discover_and_load_plugins()
        QMessageBox.information(self, "Success", "All plugins have been reloaded.")
        self._populate_all_plugin_lists()

    # --- Plugin Install/Uninstall Tab ---
    def _create_plugins_install_tab(self) -> QWidget:
        widget = QWidget(); layout = QVBoxLayout(widget)
        splitter = QSplitter(Qt.Orientation.Vertical)
        
        remote_group = QGroupBox("Find & Install New Plugins")
        remote_layout = QVBoxLayout(remote_group)
        repo_layout = QHBoxLayout()
        repo_layout.addWidget(QLabel("Plugin Distro Repo:"))
        self.plugins_repo_edit = QLineEdit(); self.plugins_repo_edit.setPlaceholderText("user/repository")
        self.fetch_plugins_button = QPushButton("Fetch"); self.fetch_plugins_button.setIcon(qta.icon('fa5s.cloud-download-alt'))
        repo_layout.addWidget(self.plugins_repo_edit, 1); repo_layout.addWidget(self.fetch_plugins_button)
        remote_layout.addLayout(repo_layout)
        self.remote_plugins_list = QListWidget()
        remote_layout.addWidget(self.remote_plugins_list)
        remote_buttons_layout = QHBoxLayout()
        self.install_remote_button = QPushButton("Install Selected"); self.install_remote_button.setIcon(qta.icon('fa5s.download'))
        self.install_remote_button.setEnabled(False)
        install_file_button = QPushButton("Install from File..."); install_file_button.setIcon(qta.icon('fa5s.file-archive'))
        remote_buttons_layout.addStretch()
        remote_buttons_layout.addWidget(self.install_remote_button); remote_buttons_layout.addWidget(install_file_button)
        remote_layout.addLayout(remote_buttons_layout)
        splitter.addWidget(remote_group)

        installed_group = QGroupBox("Installed Plugins")
        installed_layout = QVBoxLayout(installed_group)
        self.installed_plugins_list = QListWidget()
        self.uninstall_plugin_button = QPushButton("Uninstall Selected"); self.uninstall_plugin_button.setIcon(qta.icon('fa5s.trash-alt', color='crimson'))
        self.uninstall_plugin_button.setEnabled(False)
        installed_layout.addWidget(self.installed_plugins_list)
        installed_layout.addWidget(self.uninstall_plugin_button, 0, Qt.AlignmentFlag.AlignRight)
        splitter.addWidget(installed_group)
        
        splitter.setSizes([350, 250])
        layout.addWidget(splitter)
        
        self.fetch_plugins_button.clicked.connect(self._fetch_remote_plugins)
        install_file_button.clicked.connect(self._install_plugin_from_file)
        self.install_remote_button.clicked.connect(self._install_selected_remote_plugin)
        self.uninstall_plugin_button.clicked.connect(self._uninstall_selected_plugin)
        self.installed_plugins_list.currentItemChanged.connect(self._on_installed_plugin_selected)
        self.remote_plugins_list.currentItemChanged.connect(self._on_remote_plugin_selected)
        return widget

    def _populate_install_plugins_list(self):
        self.installed_plugins_list.clear()
        for plugin in sorted(self.plugin_manager.get_all_plugins(), key=lambda p: p.name.lower()):
            item_text = f"{plugin.name} v{plugin.version}{' (Core)' if plugin.is_core else ''}"
            list_item = QListWidgetItem(item_text); list_item.setData(Qt.ItemDataRole.UserRole, plugin)
            if plugin.is_core: list_item.setForeground(QColor("grey"))
            self.installed_plugins_list.addItem(list_item)
    
    def _on_installed_plugin_selected(self, item: QListWidgetItem):
        is_core = item.data(Qt.ItemDataRole.UserRole).is_core if item else True
        self.uninstall_plugin_button.setEnabled(not is_core)
        self.uninstall_plugin_button.setToolTip("Core plugins cannot be uninstalled." if is_core else "Uninstall selected plugin.")

    def _on_remote_plugin_selected(self, item: QListWidgetItem):
        can_install = item is not None and bool(item.flags() & Qt.ItemFlag.ItemIsEnabled)
        self.install_remote_button.setEnabled(can_install)

    def _fetch_remote_plugins(self):
        if not (repo_path := self.plugins_repo_edit.text().strip()) or '/' not in repo_path:
            QMessageBox.warning(self, "Invalid Repo", "Enter a valid GitHub repo (user/repo)."); return
        self.remote_plugins_list.clear(); self.remote_plugins_list.addItem("Fetching...")
        self.fetch_plugins_button.setEnabled(False); self.install_remote_button.setEnabled(False)
        self.github_manager.fetch_plugin_index(repo_path)

    def _on_plugin_index_ready(self, plugin_list: list):
        self.fetch_plugins_button.setEnabled(True); self.remote_plugins_list.clear()
        installed_ids = {p.id for p in self.plugin_manager.get_all_plugins()}
        for info in plugin_list:
            is_installed = info.get('id') in installed_ids
            item = QListWidgetItem(f"{info.get('name', 'N/A')} v{info.get('version', 'N/A')}{' (Installed)' if is_installed else ''}")
            item.setToolTip(info.get("description", "No description.")); item.setData(Qt.ItemDataRole.UserRole, info)
            if is_installed: item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEnabled); item.setForeground(QColor("grey"))
            self.remote_plugins_list.addItem(item)

    def _install_selected_remote_plugin(self):
        if item := self.remote_plugins_list.currentItem():
            self._install_plugin_from_url(item.data(Qt.ItemDataRole.UserRole).get("download_url"))

    def _install_plugin_from_url(self, url: str):
        if not url: QMessageBox.critical(self, "Error", "Plugin has no download URL."); return
        try:
            with requests.get(url, stream=True, timeout=30) as r, tempfile.NamedTemporaryFile(delete=False, suffix=".zip") as tmp:
                r.raise_for_status()
                for chunk in r.iter_content(8192): tmp.write(chunk)
                zip_path = tmp.name
            success, msg = self.plugin_manager.install_plugin_from_zip(zip_path)
            QMessageBox.information(self, "Success" if success else "Failed", msg)
            if success: self.restart_needed = True; self._populate_all_plugin_lists(); self._fetch_remote_plugins()
        except requests.RequestException as e: QMessageBox.critical(self, "Download Failed", f"Could not download: {e}")
        finally:
            if 'zip_path' in locals() and os.path.exists(zip_path): os.remove(zip_path)

    def _install_plugin_from_file(self):
        if not (filepath := QFileDialog.getOpenFileName(self, "Select Plugin Archive", "", "ZIP Files (*.zip)")[0]): return
        success, message = self.plugin_manager.install_plugin_from_zip(filepath)
        QMessageBox.information(self, "Success" if success else "Failed", message)
        if success: self.restart_needed = True; self._populate_all_plugin_lists()

    def _uninstall_selected_plugin(self):
        if not (item := self.installed_plugins_list.currentItem()): return
        plugin = item.data(Qt.ItemDataRole.UserRole)
        if plugin.is_core: QMessageBox.information(self, "Core Plugin", "Core plugins cannot be uninstalled."); return
        if QMessageBox.question(self, "Confirm Uninstall", f"Uninstall '{plugin.name}'?") == QMessageBox.StandardButton.Yes:
            success, message = self.plugin_manager.uninstall_plugin(plugin.id)
            QMessageBox.information(self, "Success" if success else "Failed", message)
            if success: self.restart_needed = True; self._populate_all_plugin_lists()

    # --- Plugin Options Tab ---
    def _create_plugins_options_tab(self) -> QWidget:
        widget = QWidget(); layout = QHBoxLayout(widget)
        splitter = QSplitter(Qt.Orientation.Horizontal)
        self.options_plugins_list = QListWidget()
        self.options_stack = QStackedWidget()
        
        # Placeholder widget for when no options are available
        self.no_options_label = QLabel("Select a plugin to see its options.\nNot all plugins are configurable.")
        self.no_options_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.no_options_label.setStyleSheet("color: grey;")
        self.options_stack.addWidget(self.no_options_label)
        
        splitter.addWidget(self.options_plugins_list)
        splitter.addWidget(self.options_stack)
        splitter.setSizes([200, 450])
        layout.addWidget(splitter)

        self.options_plugins_list.currentItemChanged.connect(self._on_options_plugin_selected)
        return widget

    def _populate_options_plugins_list(self):
        self.options_plugins_list.clear()
        self.options_stack.blockSignals(True)
        # Clear old option widgets, keeping the placeholder
        while self.options_stack.count() > 1:
            self.options_stack.removeWidget(self.options_stack.widget(1))

        plugins_with_options = []
        for plugin in self.plugin_manager.get_all_plugins():
            if plugin.instance and hasattr(plugin.instance, 'get_options_widget'):
                plugins_with_options.append(plugin)
        
        plugins_with_options.sort(key=lambda p: p.name.lower())

        for plugin in plugins_with_options:
            item = QListWidgetItem(plugin.name)
            options_widget = plugin.instance.get_options_widget()
            if options_widget:
                idx = self.options_stack.addWidget(options_widget)
                item.setData(Qt.ItemDataRole.UserRole, idx) # Store stack index
                self.options_plugins_list.addItem(item)
        
        self.options_stack.blockSignals(False)
        self.options_stack.setCurrentIndex(0)

    def _on_options_plugin_selected(self, item: QListWidgetItem):
        if item:
            stack_index = item.data(Qt.ItemDataRole.UserRole)
            self.options_stack.setCurrentIndex(stack_index)
        else:
            self.options_stack.setCurrentIndex(0) # Show placeholder
```

### File: `/ui/theme_editor_dialog.py`

#### Linter Issues Found:
```

- L17 (E501) No message available

- L20 (E501) No message available

- L63 (E501) No message available

- L71 (E501) No message available

- L101 (E501) No message available

- L171 (E501) No message available

- L300 (E501) No message available

- L358 (W292) No message available

```


```python
# PuffinPyEditor/ui/theme_editor_dialog.py
import re
import datetime
import copy
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QGridLayout,
                             QWidget, QLabel, QLineEdit, QPushButton,
                             QDialogButtonBox, QScrollArea, QMessageBox,
                             QColorDialog, QListWidget, QListWidgetItem,
                             QSplitter, QFrame, QGroupBox)
from PyQt6.QtGui import QColor, QFont, QPixmap, QIcon
from PyQt6.QtCore import Qt, pyqtSignal, QSize
from utils.logger import log
from app_core.theme_manager import theme_manager


class ColorPickerButton(QPushButton):
    """A custom button that displays a color swatch and opens a color picker."""
    color_changed = pyqtSignal(str, QColor)

    def __init__(self, key_name: str, initial_color=QColor("black"), parent=None):
        super().__init__(parent)
        self.key_name = key_name
        self._color = QColor(initial_color)
        self.setFixedSize(QSize(130, 28))
        self.setIconSize(QSize(20, 20))
        self._update_swatch()
        self.clicked.connect(self._pick_color)

    def _update_swatch(self):
        pixmap = QPixmap(self.iconSize())
        pixmap.fill(self._color)
        self.setIcon(QIcon(pixmap))
        self.setText(self._color.name().upper())

    def set_color(self, new_color: QColor, from_picker=False):
        new_color = QColor(new_color)
        if self._color != new_color:
            self._color = new_color
            self._update_swatch()
            if from_picker:
                self.color_changed.emit(self.key_name, self._color)

    def get_color(self) -> QColor:
        return self._color

    def _pick_color(self):
        dialog = QColorDialog(self._color, self)
        if dialog.exec():
            self.set_color(dialog.currentColor(), from_picker=True)


class ThemeEditorDialog(QDialog):
    """A dialog for creating, editing, and deleting UI themes."""
    custom_themes_changed = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        log.info("ThemeEditorDialog initializing...")
        self.setWindowTitle("Theme Customizer")
        self.setMinimumSize(QSize(950, 700))
        self.setModal(True)
        self.COLOR_GROUPS = {
            "Window & General": ["window.background", "sidebar.background", "accent"],
            "Editor": ["editor.background", "editor.foreground",
                       "editor.lineHighlightBackground"],
            "Editor Gutter": ["editorGutter.background",
                              "editorGutter.foreground"],
            "Editor Matching": ["editor.matchingBracketBackground",
                                "editor.matchingBracketForeground"],
            "Controls": ["button.background", "button.foreground",
                         "input.background", "input.foreground", "input.border"],
            "Bars & Menus": ["statusbar.background", "statusbar.foreground",
                             "menu.background", "menu.foreground"],
            "Editor Tabs": ["tab.activeBackground", "tab.inactiveBackground",
                            "tab.activeForeground", "tab.inactiveForeground"],
            "Scrollbar": ["scrollbar.background", "scrollbar.handle",
                          "scrollbar.handleHover", "scrollbar.handlePressed"],
            "Syntax Highlighting": [
                "syntax.keyword", "syntax.operator", "syntax.brace",
                "syntax.decorator", "syntax.self", "syntax.className",
                "syntax.functionName", "syntax.comment", "syntax.string",
                "syntax.docstring", "syntax.number"
            ]
        }
        self.current_theme_id = None
        self.is_custom_theme = False
        self.color_widgets = {}
        self.unsaved_changes = False
        self._setup_ui()
        self._repopulate_theme_list()
        self._update_ui_state()
        log.info("ThemeEditorDialog initialized successfully.")

    def _setup_ui(self):
        self.main_layout = QVBoxLayout(self)
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        self.main_layout.addWidget(self.splitter, 1)
        self._create_left_pane()
        self._create_right_pane()
        self.splitter.setSizes([240, 710])
        self.button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        self.button_box.rejected.connect(self.reject)
        self.main_layout.addWidget(self.button_box)

    def _create_left_pane(self):
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.addWidget(QLabel("<b>Available Themes:</b>"))
        self.theme_list_widget = QListWidget()
        self.theme_list_widget.setAlternatingRowColors(True)
        self.theme_list_widget.currentItemChanged.connect(
            self._on_theme_selection_changed
        )
        layout.addWidget(self.theme_list_widget, 1)
        actions_layout = QHBoxLayout()
        self.duplicate_button = QPushButton("Duplicate")
        self.delete_button = QPushButton("Delete")
        self.duplicate_button.clicked.connect(self._action_duplicate_theme)
        self.delete_button.clicked.connect(self._action_delete_theme)
        actions_layout.addWidget(self.duplicate_button)
        actions_layout.addWidget(self.delete_button)
        layout.addLayout(actions_layout)
        self.splitter.addWidget(container)

    def _create_right_pane(self):
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(10, 5, 5, 5)
        form_layout = QGridLayout()
        form_layout.addWidget(QLabel("<b>Theme Name:</b>"), 0, 0)
        self.name_edit = QLineEdit()
        self.name_edit.textChanged.connect(self._mark_unsaved_changes)
        form_layout.addWidget(self.name_edit, 0, 1)
        self.info_label = QLabel()
        self.info_label.setStyleSheet("font-style: italic; color: grey;")
        form_layout.addWidget(self.info_label, 1, 1)
        form_layout.setColumnStretch(1, 1)
        layout.addLayout(form_layout)
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        self.scroll_content = QWidget()
        self.v_scroll_layout = QVBoxLayout(self.scroll_content)
        self.v_scroll_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        scroll_area.setWidget(self.scroll_content)
        layout.addWidget(scroll_area, 1)
        actions_layout = QHBoxLayout()
        self.reset_button = QPushButton("Reset Changes")
        self.update_button = QPushButton("Update Custom Theme")
        self.reset_button.clicked.connect(self._load_theme_to_editor)
        self.update_button.clicked.connect(self._action_save)
        actions_layout.addWidget(self.reset_button)
        actions_layout.addStretch()
        actions_layout.addWidget(self.update_button)
        layout.addLayout(actions_layout)
        self.splitter.addWidget(container)

    def _repopulate_theme_list(self, select_theme_id=None):
        self.theme_list_widget.blockSignals(True)
        self.theme_list_widget.clear()
        all_themes = theme_manager.get_available_themes_for_ui()
        target_row = 0
        current_selection = (select_theme_id or self.current_theme_id or
                             theme_manager.current_theme_id)
        for i, (theme_id, name) in enumerate(all_themes.items()):
            item = QListWidgetItem(name)
            item.setData(Qt.ItemDataRole.UserRole, theme_id)
            theme_data = theme_manager.get_theme_data_by_id(theme_id)
            if theme_data and theme_data.get("is_custom"):
                item.setFont(QFont(self.font().family(), -1, QFont.Weight.Bold))
            self.theme_list_widget.addItem(item)
            if theme_id == current_selection:
                target_row = i
        self.theme_list_widget.setCurrentRow(target_row)
        self.theme_list_widget.blockSignals(False)
        self._on_theme_selection_changed(
            self.theme_list_widget.currentItem(), None
        )

    def _on_theme_selection_changed(self, current, previous):
        if not current:
            self._clear_editor()
            return

        if self.unsaved_changes and current is not previous:
            reply = QMessageBox.question(
                self, "Unsaved Changes",
                "Discard changes to the previous theme?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.No:
                self.theme_list_widget.blockSignals(True)
                if previous:
                    self.theme_list_widget.setCurrentItem(previous)
                self.theme_list_widget.blockSignals(False)
                return

        new_theme_id = current.data(Qt.ItemDataRole.UserRole)
        if new_theme_id != self.current_theme_id:
            self.current_theme_id = new_theme_id
            self._load_theme_to_editor()

    def _load_theme_to_editor(self):
        theme_data = theme_manager.get_theme_data_by_id(self.current_theme_id)
        if not theme_data or "colors" not in theme_data:
            self._clear_editor()
            return

        self._clear_layout(self.v_scroll_layout)
        self.color_widgets.clear()

        self.is_custom_theme = theme_data.get("is_custom", False)
        self.name_edit.setText(theme_data.get("name", ""))
        self.name_edit.setReadOnly(not self.is_custom_theme)
        self.info_label.setText(f"Author: {theme_data.get('author', 'N/A')}")

        all_color_keys = theme_data["colors"].keys()
        sorted_keys = sorted(all_color_keys)

        for group_name, prefixes in self.COLOR_GROUPS.items():
            group_keys = [k for k in sorted_keys if
                          any(k.startswith(p) for p in prefixes)]
            if not group_keys:
                continue

            group_box = QGroupBox(group_name)
            grid = QGridLayout(group_box)
            grid.setSpacing(5)
            row, col = 0, 0
            for key in group_keys:
                color_val = QColor(theme_data["colors"][key])
                picker = ColorPickerButton(key, color_val)
                picker.setEnabled(self.is_custom_theme)
                picker.color_changed.connect(self._mark_unsaved_changes)
                self.color_widgets[key] = picker
                grid.addWidget(QLabel(f"{key.split('.')[-1]}:"), row, col)
                grid.addWidget(picker, row, col + 1)
                col += 2
                if col >= 4:
                    col = 0
                    row += 1
            self.v_scroll_layout.addWidget(group_box)

        self.v_scroll_layout.addStretch()
        self.unsaved_changes = False
        self._update_ui_state()

    def _action_duplicate_theme(self):
        if not self.current_theme_id:
            return
        original_theme = copy.deepcopy(
            theme_manager.get_theme_data_by_id(self.current_theme_id)
        )
        if not original_theme:
            return

        new_name = f"{original_theme.get('name', 'New Theme')} (Copy)"
        safe_name = re.sub(r'[^a-z0-9_]', '', new_name.lower())
        timestamp = int(datetime.datetime.now().timestamp())
        new_id = f"custom_{safe_name}_{timestamp}"

        original_theme['name'] = new_name
        original_theme['author'] = "PuffinPy User"
        original_theme['is_custom'] = True

        theme_manager.add_or_update_custom_theme(new_id, original_theme)
        self.custom_themes_changed.emit()
        self._repopulate_theme_list(select_theme_id=new_id)

    def _action_delete_theme(self):
        if not self.current_theme_id or not self.is_custom_theme:
            return
        theme_data = theme_manager.get_theme_data_by_id(self.current_theme_id)
        theme_name = theme_data.get('name', self.current_theme_id)
        reply = QMessageBox.question(
            self, "Confirm Delete",
            f"Are you sure you want to delete the theme '{theme_name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            theme_manager.delete_custom_theme(self.current_theme_id)
            self.custom_themes_changed.emit()
            if self.current_theme_id == theme_manager.current_theme_id:
                theme_manager.set_theme("puffin_dark")
            self._repopulate_theme_list(select_theme_id="puffin_dark")

    def _action_save(self):
        if not self.is_custom_theme or not self.unsaved_changes:
            return
        theme_data = copy.deepcopy(
            theme_manager.get_theme_data_by_id(self.current_theme_id)
        )
        theme_data['name'] = self.name_edit.text()
        for key, widget in self.color_widgets.items():
            theme_data['colors'][key] = widget.get_color().name()

        theme_manager.add_or_update_custom_theme(self.current_theme_id, theme_data)
        self.custom_themes_changed.emit()
        self.unsaved_changes = False
        self._update_ui_state()
        if self.current_theme_id == theme_manager.current_theme_id:
            theme_manager.set_theme(self.current_theme_id)
        QMessageBox.information(
            self, "Success", f"Theme '{theme_data['name']}' has been updated."
        )

    def _mark_unsaved_changes(self, *args):
        if self.is_custom_theme:
            self.unsaved_changes = True
            self._update_ui_state()

    def _update_ui_state(self):
        has_selection = self.current_theme_id is not None
        can_edit = self.is_custom_theme
        self.name_edit.setEnabled(can_edit)
        self.reset_button.setEnabled(can_edit and self.unsaved_changes)
        self.update_button.setEnabled(can_edit and self.unsaved_changes)
        self.delete_button.setEnabled(can_edit)
        self.duplicate_button.setEnabled(has_selection)
        for widget in self.color_widgets.values():
            widget.setEnabled(can_edit)

    def _clear_layout(self, layout):
        if layout is None:
            return
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
            else:
                sub_layout = item.layout()
                if sub_layout is not None:
                    self._clear_layout(sub_layout)

    def _clear_editor(self):
        self._clear_layout(self.v_scroll_layout)
        self.name_edit.clear()
        self.info_label.clear()
        self.current_theme_id = None
        self.is_custom_theme = False
        self.unsaved_changes = False
        self._update_ui_state()

    def reject(self):
        if self.unsaved_changes:
            reply = QMessageBox.question(
                self, "Unsaved Changes", "Discard changes and close?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.Yes:
                super().reject()
        else:
            super().reject()
```

### File: `/utils/__init__.py`

```python

```

### File: `/utils/helpers.py`

#### Linter Issues Found:
```

- L71 (E501) No message available

- L78 (W292) No message available

```


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

#### Linter Issues Found:
```

- L7 (E501) No message available

- L65 (E501) No message available

- L66 (E501) No message available

- L220 (E501) No message available

- L225 (E501) No message available

- L290 (W292) No message available

```


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

#### Linter Issues Found:
```

- L24 (E501) No message available

- L35 (E501) No message available

- L47 (E127) No message available

- L86 (W292) No message available

```


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

#### Linter Issues Found:
```

- L33 (E501) No message available

- L39 (W292) No message available

```


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

#### Linter Issues Found:
```

- L66 (E501) No message available

- L88 (E501) No message available

- L148 (W292) No message available

```


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

#### Linter Issues Found:
```

- L7 (E501) No message available

- L78 (E501) No message available

- L89 (W292) No message available

```


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

#### Linter Issues Found:
```

- L57 (E501) No message available

- L62 (E501) No message available

- L76 (W292) No message available

```


```python
# PuffinPyEditor/main.py
import sys
import traceback
# *** FIX: Import the 'os' module to get the current directory ***
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
    # Also print to stderr for visibility if the log file is not accessible
    print(f"FATAL ERROR:\n{tb_text}", file=sys.stderr)
    # Call the original excepthook to ensure standard exit behavior
    sys.__excepthook__(exc_type, exc_value, exc_tb)


def main():
    # Set the fallback hook immediately. It will be replaced by a better one
    # if the application initializes correctly and debug tools are loaded.
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

    # Import MainWindow inside main() to prevent circular dependency
    from ui.main_window import MainWindow

    # Separate initialization from execution for clarity and stability.
    try:
        main_window = MainWindow(file_handler, theme_manager, debug_mode=DEBUG_MODE)
        log.info("MainWindow instance created successfully.")
    except Exception:
        # The enhanced exception hook will now properly catch this
        # because we are not swallowing the exception.
        log.critical("A fatal error occurred during MainWindow initialization.")
        # Re-raising the exception ensures it gets passed to the excepthook.
        raise

    # *** FIX: Set a project root to prevent the window from collapsing ***
    project_path = os.getcwd()
    main_window.set_project_root(project_path)

    main_window.show()
    log.info("MainWindow shown. Entering main event loop.")
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
```

### File: `/requirements.txt`

```text
flake8
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

#### Linter Issues Found:
```

- L10 (E501) No message available

- L112 (E501) No message available

- L138 (W292) No message available

```


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

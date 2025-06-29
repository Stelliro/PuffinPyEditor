# Project Export: PuffinPyEditor
## Export Timestamp: 2025-06-28T06:27:36.948074
---



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

### File: `/app_core/plugin_api.py`

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

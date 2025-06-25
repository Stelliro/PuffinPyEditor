# PuffinPyEditor/app_core/completion_manager.py
import os
import sys
import shutil
from typing import Dict, List, Any, Optional
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
    2. The python.exe from the current virtual environment (if running from source).
    3. A python.exe bundled alongside the main PuffinPyEditor.exe.
    4. The first 'python' found on the system's PATH.

    Returns:
        The path to a suitable Python executable, or an empty string if none found.
    """
    # 1. Prioritize user-defined path from settings
    user_path = settings_manager.get("python_interpreter_path")
    if user_path and os.path.exists(user_path) and "PuffinPyEditor.exe" not in user_path:
        log.info(f"Jedi: Using user-defined interpreter: {user_path}")
        return user_path

    # 2. When running from source, sys.executable is the venv python.
    # When frozen, sys.executable is PuffinPyEditor.exe, which we must avoid.
    if not getattr(sys, 'frozen', False):
        log.info(f"Jedi: Running from source, using sys.executable: {sys.executable}")
        return sys.executable

    # 3. If the application is frozen (bundled with PyInstaller)
    if getattr(sys, 'frozen', False):
        # Look for 'python.exe' in the same directory as our main executable.
        frozen_dir = os.path.dirname(sys.executable)
        local_python_path = os.path.join(frozen_dir, "python.exe")
        if os.path.exists(local_python_path):
            log.info(f"Jedi: Found local python.exe in frozen app dir: {local_python_path}")
            return local_python_path

    # 4. As a last resort, search the system's PATH.
    system_python = shutil.which("python")
    if system_python:
        log.warning(f"Jedi: Falling back to system python on PATH: {system_python}")
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
                log.error("JediWorker could not be initialized: No valid Python interpreter found.")
                self.project = None
                return

            if project_path and os.path.isdir(project_path):
                self.project = jedi.Project(path=project_path, environment_path=python_executable)
                log.info(f"Jedi context set to project: {project_path} with interpreter: {python_executable}")
            else:
                # Fallback to a default project if no path is given
                self.project = jedi.get_default_project(sys_path=[os.path.dirname(python_executable)])
                log.info(f"Jedi context set to default environment with interpreter: {python_executable}")

        except Exception as e:
            log.error(f"Failed to initialize Jedi project: {e}", exc_info=True)
            self.project = None

    def get_completions(self, source: str, line: int, col: int, filepath: str):
        """Generates code completions."""
        if not self.project:
            self.completions_ready.emit([])
            return
        try:
            script = jedi.Script(code=source, path=filepath, project=self.project)
            completions = script.complete(line=line, column=col)
            completion_data = [{
                'name': c.name, 'type': c.type,
                'description': c.description, 'docstring': c.docstring(raw=True)
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
            script = jedi.Script(code=source, path=filepath, project=self.project)
            definitions = script.goto(line=line, column=col)
            if definitions:
                d = definitions[0]
                log.info(f"Jedi found definition for '{d.name}' at {d.module_path}:{d.line}:{d.column}")
                self.definition_ready.emit(str(d.module_path), d.line, d.column)
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
            script = jedi.Script(code=source, path=filepath, project=self.project)
            signatures = script.get_signatures(line=line, column=col)
            self.signature_ready.emit(signatures[0] if signatures else None)
        except Exception as e:
            log.error(f"Error getting Jedi signature: {e}", exc_info=False)
            self.signature_ready.emit(None)


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

    def request_completions(self, source: str, line: int, col: int, filepath: str):
        self._completions_requested.emit(source, line, col, filepath)

    def request_definition(self, source: str, line: int, col: int, filepath: str):
        self._definition_requested.emit(source, line, col, filepath)

    def request_signature(self, source: str, line: int, col: int, filepath: str):
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

            # Escape HTML characters in the docstring to prevent rendering issues
            doc_html = docstring.replace('&', '&').replace('<', '<').replace('>', '>')
            doc_html = f"<pre style='white-space: pre-wrap; margin: 0; padding: 0; font-family: inherit;'>{doc_html}</pre>"

            tooltip_html = f"""
                <div style='background-color: {bg}; color: {fg};
                            font-family: Consolas, "Courier New", monospace; font-size: 10pt;
                            padding: 8px; border-radius: 4px; border: 1px solid {border};'>
                    <b style='color: {accent};'>{header}</b>
            """
            if docstring:
                tooltip_html += f"""
                    <div style='border-top: 1px solid {border}; margin-top: 6px;
                                padding-top: 6px; color: {doc_fg};'>
                        {doc_html}
                    </div>
                """
            tooltip_html += "</div>"
            self.hover_tip_ready.emit(tooltip_html.strip())
        except Exception as e:
            log.error(f"Error formatting signature tooltip: {e}", exc_info=False)
            self.hover_tip_ready.emit("")

    def shutdown(self):
        """Gracefully shuts down the Jedi worker thread."""
        if self.thread and self.thread.isRunning():
            log.info("Shutting down CompletionManager thread.")
            # Disconnect signals to prevent any more work from being sent
            try:
                self._completions_requested.disconnect(self.worker.get_completions)
                self._definition_requested.disconnect(self.worker.get_definition)
                self._signature_requested.disconnect(self.worker.get_signature)
                self._project_path_changed.disconnect(self.worker.set_project)
            except TypeError:
                pass  # Signals may already be disconnected

            self.thread.quit()
            if not self.thread.wait(3000):  # Wait 3 seconds
                log.warning("CompletionManager thread did not shut down gracefully. Terminating.")
                self.thread.terminate()
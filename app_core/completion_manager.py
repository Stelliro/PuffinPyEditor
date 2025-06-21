# PuffinPyEditor/app_core/completion_manager.py
import os
import sys
from PyQt6.QtCore import QObject, QThread, pyqtSignal, Qt

import jedi
from utils.logger import log
from app_core.settings_manager import settings_manager
from app_core.theme_manager import theme_manager


class JediWorker(QObject):
    completions_ready = pyqtSignal(list)
    definition_ready = pyqtSignal(str, int, int)
    signature_ready = pyqtSignal(object)

    def __init__(self):
        super().__init__()
        self.project = None

    def set_project(self, project_path: str):
        try:
            python_executable = settings_manager.get("python_interpreter_path") or sys.executable

            if project_path and os.path.isdir(project_path):
                self.project = jedi.Project(path=project_path, environment_path=python_executable)
                log.info(f"JediWorker context set to project: {project_path}")
            else:
                self.project = jedi.get_default_project(sys.executable)
                log.info(f"JediWorker context set to default system environment.")
        except Exception as e:
            log.error(f"Failed to initialize Jedi project: {e}", exc_info=True)
            self.project = None

    def get_completions(self, source: str, line: int, col: int, filepath: str):
        try:
            if not self.project:
                self.completions_ready.emit([])
                return

            script = jedi.Script(code=source, path=filepath, project=self.project)
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
        try:
            if not self.project:
                self.definition_ready.emit(None, -1, -1)
                return

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
        try:
            if not self.project:
                self.signature_ready.emit(None)
                return

            script = jedi.Script(code=source, path=filepath, project=self.project)
            signatures = script.get_signatures(line=line, column=col)
            if signatures:
                self.signature_ready.emit(signatures[0])
            else:
                self.signature_ready.emit(None)
        except Exception as e:
            log.error(f"Error getting Jedi signature: {e}", exc_info=False)
            self.signature_ready.emit(None)


class CompletionManager(QObject):
    completions_available = pyqtSignal(list)
    definition_found = pyqtSignal(str, int, int)
    hover_tip_ready = pyqtSignal(str)

    _completions_requested = pyqtSignal(str, int, int, str)
    _definition_requested = pyqtSignal(str, int, int, str)
    _signature_requested = pyqtSignal(str, int, int, str)
    _project_path_changed = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.thread = QThread()
        self.worker = JediWorker()
        self.worker.moveToThread(self.thread)

        self._completions_requested.connect(self.worker.get_completions)
        self._definition_requested.connect(self.worker.get_definition)
        self._signature_requested.connect(self.worker.get_signature)
        self._project_path_changed.connect(self.worker.set_project)

        self.worker.completions_ready.connect(self.completions_available)
        self.worker.definition_ready.connect(self.definition_found)
        self.worker.signature_ready.connect(self._format_signature_for_tooltip)

        self.thread.finished.connect(self.worker.deleteLater)
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

    def _format_signature_for_tooltip(self, signature):
        if not signature:
            self.hover_tip_ready.emit("")
            return

        try:
            colors = theme_manager.current_theme_data.get('colors', {})
            bg = colors.get('menu.background', '#2b2b2b')
            fg = colors.get('menu.foreground', '#a9b7c6')
            accent = colors.get('syntax.functionName', '#88c0d0')
            doc_fg = colors.get('syntax.comment', '#88929b')
            border = colors.get('input.border', '#555')

            params_str = ', '.join(p.description for p in signature.params)
            header = f"def {signature.name}({params_str})"
            docstring = signature.docstring(raw=True).strip()

            tooltip_html = f"""
                <div style='font-family: Consolas, "Courier New", monospace; font-size: 10pt; background-color: {bg}; color: {fg}; padding: 8px; border-radius: 4px; border: 1px solid {border};'>
                    <b style='color: {accent};'>{header}</b>
            """
            if docstring:
                doc_html = docstring.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
                doc_html = f"<pre style='white-space: pre-wrap; margin: 0; padding: 0; font-family: inherit;'>{doc_html}</pre>"
                tooltip_html += f"""
                    <div style='border-top: 1px solid {border}; margin-top: 6px; padding-top: 6px; color: {doc_fg};'>
                        {doc_html}
                    </div>
                """
            tooltip_html += "</div>"
            self.hover_tip_ready.emit(tooltip_html.strip())
        except Exception as e:
            log.error(f"Error formatting signature tooltip: {e}")
            self.hover_tip_ready.emit("")

    def shutdown(self):
        if self.thread.isRunning():
            log.info("Shutting down CompletionManager thread.")
            self.thread.quit()
            self.thread.wait(3000)

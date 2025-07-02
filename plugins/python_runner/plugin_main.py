# PuffinPyEditor/plugins/python_runner/plugin_main.py
import os
from PyQt6.QtWidgets import QMessageBox
from PyQt6.QtCore import Qt, QObject
from app_core.puffin_api import PuffinPluginAPI
from .output_panel import OutputPanel
from .code_runner import CodeRunner

class PythonRunnerPlugin(QObject):
    def __init__(self, puffin_api: PuffinPluginAPI):
        super().__init__()
        from ui.editor_widget import EditorWidget
        self.EditorWidgetClass = EditorWidget
        self.api = puffin_api
        self.main_window = self.api.get_main_window()
        self.code_runner = CodeRunner(self)
        self.output_panel = OutputPanel(self.main_window)
        self._setup_ui()
        self._connect_signals()

    def _setup_ui(self):
        self.api.register_dock_panel(self.output_panel, "Output", Qt.DockWidgetArea.BottomDockWidgetArea, 'fa5s.terminal')
        self.run_action = self.api.add_menu_action("run", "Run Script", self._run_script, "F5", 'fa5s.play')
        self.stop_action = self.api.add_menu_action("run", "Stop Script", self.code_runner.stop_script, "Ctrl+F5", 'fa5s.stop-circle')
        self.stop_action.setEnabled(False)
        self.api.add_toolbar_action(self.run_action)
        self.api.add_toolbar_action(self.stop_action)

    def _connect_signals(self):
        self.code_runner.output_received.connect(self.output_panel.append_output)
        self.code_runner.error_received.connect(lambda text: self.output_panel.append_output(text, is_error=True))
        self.code_runner.process_finished.connect(self._on_run_finished)
        self.main_window.theme_changed_signal.connect(self.output_panel.update_theme)

    def _run_script(self):
        editor = self.main_window.tab_widget.currentWidget()
        if not isinstance(editor, self.EditorWidgetClass): return
        filepath = self.main_window.editor_tabs_data.get(editor, {}).get('filepath')
        if not filepath:
            if QMessageBox.question(self.main_window, "Save Required", "File must be saved.", QMessageBox.StandardButton.Save | QMessageBox.StandardButton.Cancel) == QMessageBox.StandardButton.Save:
                if not (filepath := self.main_window._action_save_as()): return
            else: return
        elif hash(editor.get_text()) != self.main_window.editor_tabs_data[editor]['original_hash']:
            self.main_window._action_save_file()

        if filepath and os.path.exists(filepath):
            self.output_panel.clear_output()
            self.run_action.setEnabled(False); self.stop_action.setEnabled(True)
            self.code_runner.run_script(filepath)

    def _on_run_finished(self, exit_code):
        self.api.show_status_message(f"Process finished with exit code {exit_code}", 4000)
        self.run_action.setEnabled(True); self.stop_action.setEnabled(False)

def initialize(puffin_api: PuffinPluginAPI):
    return PythonRunnerPlugin(puffin_api)
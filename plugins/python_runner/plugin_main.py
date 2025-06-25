# PuffinPyEditor/plugins/python_runner/plugin_main.py
import os
from PyQt6.QtWidgets import QMessageBox
from PyQt6.QtCore import Qt
from ui.editor_widget import EditorWidget
from app_core.code_runner import CodeRunner # Use the core runner
from output_panel import OutputPanel


class PythonRunnerPlugin:
    def __init__(self, main_window):
        self.api = main_window.puffin_api
        self.main_window = self.api.get_main_window()
        # Use the centralized code runner from the core application
        self.code_runner = CodeRunner()
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
        if not isinstance(editor, EditorWidget): return
        filepath = self.main_window.editor_tabs_data.get(editor, {}).get('filepath')
        if not filepath:
            if QMessageBox.question(self.main_window, "Save Required", "File must be saved to be executed.",
                                    QMessageBox.StandardButton.Save | QMessageBox.StandardButton.Cancel) == QMessageBox.StandardButton.Save:
                # Use the main window's save_as action which returns a boolean
                if not self.main_window._action_save_as(): return
                filepath = self.main_window.editor_tabs_data.get(editor, {}).get('filepath')
            else:
                return
        # If the file is modified (dirty), save it before running.
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
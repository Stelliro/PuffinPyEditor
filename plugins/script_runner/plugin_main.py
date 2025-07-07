# PuffinPyEditor/plugins/script_runner/plugin_main.py
import os
import sys
import shutil
import platform
from PyQt6.QtWidgets import QMessageBox
from PyQt6.QtCore import QObject, QProcess, QTimer
from app_core.puffin_api import PuffinPluginAPI
from .output_panel import OutputPanel
from .code_runner import _find_python_interpreter
from utils.logger import log


class ScriptRunnerPlugin(QObject):
    def __init__(self, puffin_api: PuffinPluginAPI):
        super().__init__()
        self.api = puffin_api
        self.main_window = self.api.get_main_window()
        self.output_panel = OutputPanel(self.main_window)
        self.process = None
        self._current_task_info = {}

        self.RUN_CONFIG = {
            '.py': {'handler': self._run_python_script, 'menu_text': 'Run Python Script', 'shortcut': 'F5',
                    'icon': 'mdi.language-python'},
            '.js': {'handler': self._run_node_script, 'menu_text': 'Run JS File', 'shortcut': 'Ctrl+F5',
                    'icon': 'mdi.language-javascript'},
            '.cpp': {'handler': self._compile_run_cpp, 'menu_text': 'Compile & Run C++', 'shortcut': 'F6',
                     'icon': 'mdi.language-cpp'},
            '.c': {'handler': self._compile_run_cpp, 'menu_text': 'Compile & Run C', 'shortcut': 'F6',
                   'icon': 'mdi.language-cpp'},
            '.cs': {'handler': self._compile_run_csharp, 'menu_text': 'Compile & Run C#', 'shortcut': 'F7',
                    'icon': 'mdi.language-csharp'},
        }
        self.run_actions = {}
        self._setup_ui()
        self._connect_signals()

    def _setup_ui(self):
        self.api.add_dock_panel(
            widget=self.output_panel,
            title="Output",
            area_str="bottom",
            icon_name='mdi.console-line'
        )
        for config in self.RUN_CONFIG.values():
            action = self.api.add_menu_action("run", config['menu_text'], config['handler'], config['shortcut'],
                                              config['icon'])
            action.setEnabled(False)
            self.run_actions[config['menu_text']] = action

        self.stop_action = self.api.add_menu_action("run", "Stop Script", self.stop_script, "Ctrl+F2",
                                                    'mdi.stop-circle-outline')
        self.stop_action.setEnabled(False)

        # Add only the Python run/stop actions to the main toolbar for prominence
        py_action = self.run_actions['Run Python Script']
        self.api.add_toolbar_action(py_action)
        self.api.add_toolbar_action(self.stop_action)

    def _connect_signals(self):
        self.main_window.tab_widget.currentChanged.connect(self._on_tab_changed)
        QTimer.singleShot(0, lambda: self._on_tab_changed(self.main_window.tab_widget.currentIndex()))
        self.main_window.theme_changed_signal.connect(self.output_panel.update_theme)

    def _on_tab_changed(self, index):
        from ui.editor_widget import EditorWidget
        active_ext = None
        if index != -1:
            if widget := self.main_window.tab_widget.widget(index):
                if isinstance(widget, EditorWidget):
                    if data := self.main_window.editor_tabs_data.get(widget):
                        if filepath := data.get('filepath'):
                            _, active_ext = os.path.splitext(filepath)

        for ext, config in self.RUN_CONFIG.items():
            action = self.run_actions.get(config['menu_text'])
            if action:
                action.setEnabled(ext == active_ext)

    def stop_script(self):
        if self.process and self.process.state() != QProcess.ProcessState.NotRunning:
            self.output_panel.append_output("[Runner] Terminating process...\n", is_error=True)
            self.process.terminate()
            if not self.process.waitForFinished(1000):
                self.process.kill()
                self.output_panel.append_output("[Runner] Process killed.\n", is_error=True)
        else:
            self._on_run_finished(-1)

    def _get_current_filepath(self):
        from ui.editor_widget import EditorWidget
        editor = self.main_window.tab_widget.currentWidget()
        if not isinstance(editor, EditorWidget):
            return None

        filepath = self.main_window.editor_tabs_data.get(editor, {}).get('filepath')
        if not filepath:
            self.api.show_message("info", "Save File", "Please save the file before running.")
            return None

        if self.main_window._is_editor_modified(editor):
            self.main_window._action_save_file()

        return filepath
        
    def run_specific_script(self, filepath: str):
        """Runs a script from a given path, bypassing the active tab."""
        ext = os.path.splitext(filepath)[1].lower()
        for config_ext, config in self.RUN_CONFIG.items():
            if ext == config_ext:
                # Call the handler with the specific filepath
                config['handler'](filepath=filepath)
                return
        self.api.show_message("warning", "Unsupported File Type", f"No run configuration for '{ext}' files.")

    def _run_python_script(self, filepath: str = None):
        filepath = filepath or self._get_current_filepath()
        if not filepath: return
        if not (interpreter_path := _find_python_interpreter()):
            self.api.show_message("critical", "Python Not Found", "Could not find a Python interpreter.")
            return

        self._current_task_info = {'name': 'Python Script'}
        self._start_process(interpreter_path, [filepath])

    def _run_node_script(self, filepath: str = None):
        filepath = filepath or self._get_current_filepath()
        if not filepath: return
        if not (node_path := shutil.which("node")):
            self.api.show_message("critical", "Node.js Not Found", "Could not find 'node' on your system PATH.")
            return

        self._current_task_info = {'name': 'Node.js Script'}
        self._start_process(node_path, [filepath])

    def _compile_run_cpp(self, filepath: str = None):
        source_path = filepath or self._get_current_filepath()
        if not source_path: return
        compiler_path = shutil.which("g++") or shutil.which("cl")
        if not compiler_path:
            self.api.show_message("critical", "Compiler Not Found", "No C++ compiler (g++ or cl.exe) found.")
            return

        source_dir = os.path.dirname(source_path)
        base_name = os.path.splitext(os.path.basename(source_path))[0]
        exe_path = os.path.join(source_dir, base_name + (".exe" if platform.system() == "Windows" else ""))

        if "g++" in os.path.basename(compiler_path):
            args = [source_path, "-o", exe_path, "-std=c++17", "-Wall"]
        else:  # cl.exe
            args = [source_path, f"/Fe:{exe_path}", "/EHsc"]

        self._current_task_info = {'name': 'C++ Compilation', 'type': 'compile', 'runner_path': exe_path}
        self._start_process(compiler_path, args)

    def _compile_run_csharp(self, filepath: str = None):
        source_path = filepath or self._get_current_filepath()
        if not source_path: return
        if not (compiler_path := shutil.which("csc")):
            self.api.show_message("critical", "C# Compiler Not Found", "C# compiler (csc.exe) not found.")
            return

        source_dir = os.path.dirname(source_path)
        base_name = os.path.splitext(os.path.basename(source_path))[0]
        exe_path = os.path.join(source_dir, f"{base_name}.exe")

        args = [f"/out:{exe_path}", source_path]
        self._current_task_info = {'name': 'C# Compilation', 'type': 'compile', 'runner_path': exe_path}
        self._start_process(compiler_path, args)

    def _start_process(self, program, args):
        if self.process and self.process.state() != QProcess.ProcessState.NotRunning:
            self.output_panel.append_output("[Runner] A process is already running.", is_error=True)
            return

        self.output_panel.clear_output()
        self.output_panel.append_output(f"[{self._current_task_info.get('name', 'Process')}] Starting...")
        self.output_panel.append_output(f"> {os.path.basename(program)} {' '.join(args)}\n")

        self.process = QProcess()
        self.process.readyReadStandardOutput.connect(self._handle_stdout)
        self.process.readyReadStandardError.connect(self._handle_stderr)
        self.process.finished.connect(self._handle_finished)
        self.process.setWorkingDirectory(os.path.dirname(args[0]))

        self.stop_action.setEnabled(True)
        self.process.start(program, args)

    def _handle_stdout(self):
        if self.process: self.output_panel.append_output(
            self.process.readAllStandardOutput().data().decode(errors='replace'))

    def _handle_stderr(self):
        if self.process: self.output_panel.append_output(
            self.process.readAllStandardError().data().decode(errors='replace'), is_error=True)

    def _handle_finished(self, exit_code, exit_status):
        task_name = self._current_task_info.get('name', 'Process')
        task_type = self._current_task_info.get('type')

        if task_type == 'compile':
            if exit_code == 0:
                self.output_panel.append_output(f"\n[{task_name}] Compilation successful.")
                runner_path = self._current_task_info.get('runner_path')
                self._current_task_info = {'name': f"{task_name.split(' ')[0]} Execution", 'type': 'run',
                                           'runner_path': runner_path}
                self._start_process(runner_path, [])
            else:
                self.output_panel.append_output(f"\n[{task_name}] Compilation failed.", is_error=True)
                self._on_run_finished(exit_code)
        else:  # Standard run or second step of compile-run
            self.output_panel.append_output(f"\n[{task_name}] Finished with exit code {exit_code}.")
            runner_path = self._current_task_info.get('runner_path')
            if runner_path and os.path.exists(runner_path) and not filepath.endswith('.py'):
                try:
                    os.remove(runner_path)
                except OSError as e:
                    self.output_panel.append_output(f"Could not remove temporary file: {e}", is_error=True)
            self._on_run_finished(exit_code)

    def _on_run_finished(self, exit_code):
        self.stop_action.setEnabled(False)
        self.process = None
        self._current_task_info = {}
        # Re-evaluate which run button should be active
        self._on_tab_changed(self.main_window.tab_widget.currentIndex())


def initialize(puffin_api: PuffinPluginAPI):
    return ScriptRunnerPlugin(puffin_api)
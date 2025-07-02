# PuffinPyEditor/plugins/cpp_tools/plugin_main.py
import os
import sys
import shutil
import platform
from PyQt6.QtWidgets import QMessageBox
from PyQt6.QtCore import QObject, QProcess
from app_core.puffin_api import PuffinPluginAPI
from utils.logger import log
from .cpp_syntax_highlighter import CppSyntaxHighlighter

class CppToolsPlugin(QObject):
    def __init__(self, puffin_api: PuffinPluginAPI):
        super().__init__()
        from ui.editor_widget import EditorWidget
        self.EditorWidgetClass = EditorWidget

        self.api = puffin_api
        self.main_window = self.api.get_main_window()
        self.compiler_process = None
        self._current_step = None
        self._output_exe_path = None

        # Corrected assignment to fix SyntaxError
        self.output_panel = self._get_output_panel()
        if not self.output_panel:
            log.error("C++ Tools: Could not find Output Panel. This plugin needs Python Runner.")
            return

        self._setup_highlighter()
        self._setup_ui()
        self._connect_signals()

    def _get_output_panel(self):
        runner_plugin = self.api.get_plugin_instance("python_runner")
        return getattr(runner_plugin, 'output_panel', None)

    def _setup_highlighter(self):
        extensions = ['.cpp', '.hpp', '.c', '.h', '.cxx', '.hxx']
        for ext in extensions: self.api.register_highlighter(ext, CppSyntaxHighlighter)
        log.info(f"C++ Tools: Registered highlighter for {', '.join(extensions)} files.")

    def _setup_ui(self):
        self.run_cpp_action = self.api.add_menu_action("run", "Compile & Run C++ File", self._compile_and_run_script,
                                                       "F6", "mdi.language-cpp")
        self.run_cpp_action.setEnabled(False)

    def _connect_signals(self):
        self.main_window.tab_widget.currentChanged.connect(self._on_tab_changed)
        self._on_tab_changed(self.main_window.tab_widget.currentIndex())

    def _on_tab_changed(self, index):
        widget = self.main_window.tab_widget.widget(index) if index != -1 else None
        is_cpp = isinstance(widget, self.EditorWidgetClass) and (
            d := self.main_window.editor_tabs_data.get(widget)) and (
                     fp := d.get('filepath', '')) and fp.lower().endswith(('.cpp', '.c', '.cxx'))
        self.run_cpp_action.setEnabled(is_cpp)

    def _find_compiler(self):
        if shutil.which("g++"): return "g++"
        if platform.system() == "Windows" and shutil.which("cl"): return "cl"
        return None

    def _compile_and_run_script(self):
        if self.compiler_process and self.compiler_process.state() != QProcess.ProcessState.NotRunning: return
        compiler = self._find_compiler()
        if not compiler:
            self.api.show_message("critical", "Compiler Not Found",
                                  "No C++ compiler (g++ or cl.exe) found on your system PATH.")
            return
        widget, data = self.main_window.tab_widget.currentWidget(), self.main_window.editor_tabs_data.get(
            self.main_window.tab_widget.currentWidget(), {})
        source_path = data.get('filepath')
        if not source_path: self.api.show_message("info", "Save File", "Please save the file before compiling."); return
        if self.main_window._is_editor_modified(widget): self.main_window._action_save_file()

        self.output_panel.clear_output()
        self.output_panel.append_output(f"[{compiler}] Found compiler at: {shutil.which(compiler)}")
        source_dir, base_name = os.path.dirname(source_path), os.path.splitext(os.path.basename(source_path))[0]
        self._output_exe_path = os.path.join(source_dir, base_name + (".exe" if platform.system() == "Windows" else ""))

        if compiler == "g++":
            cmd_args = [source_path, "-o", self._output_exe_path, "-std=c++17", "-Wall"]
        else:
            cmd_args = [source_path, f"/Fe:{self._output_exe_path}", "/EHsc"]

        self._current_step = "COMPILE"
        self._start_process(compiler, cmd_args)

    def _start_process(self, program, args):
        self.compiler_process = QProcess()
        self.compiler_process.readyReadStandardOutput.connect(self._handle_stdout)
        self.compiler_process.readyReadStandardError.connect(self._handle_stderr)
        self.compiler_process.finished.connect(self._handle_finished)
        self.output_panel.append_output(f"\n> {program} {' '.join(args)}\n")
        self.run_cpp_action.setEnabled(False)
        self.compiler_process.start(program, args)

    def _handle_stdout(self):
        if self.compiler_process: self.output_panel.append_output(
            self.compiler_process.readAllStandardOutput().data().decode())

    def _handle_stderr(self):
        if self.compiler_process: self.output_panel.append_output(
            self.compiler_process.readAllStandardError().data().decode(), is_error=True)

    def _handle_finished(self, exit_code, exit_status):
        step, self._current_step = self._current_step, None
        if step == "COMPILE":
            if exit_code == 0:
                self.output_panel.append_output("\n[PuffinPy-CPP] Compilation successful.")
                self._current_step = "RUN"
                self._start_process(self._output_exe_path, [])
            else:
                self.output_panel.append_output(f"\n[PuffinPy-CPP] Compilation failed with exit code {exit_code}.",
                                                is_error=True)
                self.run_cpp_action.setEnabled(True)
        elif step == "RUN":
            self.output_panel.append_output(f"\n[PuffinPy-CPP] Execution finished with exit code {exit_code}.")
            if self._output_exe_path and os.path.exists(self._output_exe_path):
                try:
                    os.remove(self._output_exe_path)
                except OSError as e:
                    self.output_panel.append_output(f"Could not remove temporary executable: {e}", is_error=True)
            self._output_exe_path = None
            self.run_cpp_action.setEnabled(True)


def initialize(puffin_api: PuffinPluginAPI):
    """Entry point for PuffinPyEditor to load the plugin."""
    try:
        return CppToolsPlugin(puffin_api)
    except Exception as e:
        log.error(f"Failed to initialize C++ Tools Plugin: {e}", exc_info=True)
        return None
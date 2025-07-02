# PuffinPyEditor/plugins/csharp_tools/plugin_main.py
import os, sys, shutil, platform
from PyQt6.QtWidgets import QMessageBox
from PyQt6.QtCore import QObject, QProcess
from app_core.puffin_api import PuffinPluginAPI
from utils.logger import log
from .csharp_syntax_highlighter import CSharpSyntaxHighlighter

class CSharpToolsPlugin(QObject):
    def __init__(self, puffin_api: PuffinPluginAPI):
        super().__init__()
        from ui.editor_widget import EditorWidget
        self.EditorWidgetClass = EditorWidget

        self.api = puffin_api
        self.main_window = self.api.get_main_window()
        self.process = None
        self._current_step = None
        self._output_exe_path = None

        self.output_panel = self._get_output_panel()
        if not self.output_panel:
            log.error("C# Tools: Could not find Output Panel. This plugin depends on Python Runner.")
            return

        self._setup_highlighter()
        self._setup_ui()
        self._connect_signals()

    def _get_output_panel(self):
        runner_plugin = self.api.get_plugin_instance("python_runner")
        return getattr(runner_plugin, 'output_panel', None)

    def _setup_highlighter(self):
        self.api.register_highlighter('.cs', CSharpSyntaxHighlighter)
        log.info("C# Tools: Registered highlighter for .cs files.")

    def _setup_ui(self):
        self.run_cs_action = self.api.add_menu_action(
            menu_name="run",
            text="Compile & Run C# File",
            callback=self._compile_and_run_script,
            shortcut="F7",  # New shortcut
            icon_name="mdi.language-csharp"
        )
        self.run_cs_action.setEnabled(False)

    def _connect_signals(self):
        self.main_window.tab_widget.currentChanged.connect(self._on_tab_changed)
        self._on_tab_changed(self.main_window.tab_widget.currentIndex())

    def _on_tab_changed(self, index):
        is_cs_file = False
        if index != -1:
            widget = self.main_window.tab_widget.widget(index)
            # MODIFIED: Use deferred class
            if isinstance(widget, self.EditorWidgetClass) and (data := self.main_window.editor_tabs_data.get(widget)):
                filepath = data.get('filepath', '')
                if filepath and filepath.lower().endswith('.cs'):
                    is_cs_file = True
        self.run_cs_action.setEnabled(is_cs_file)

    def _find_compiler(self):
        # The C# compiler on Windows is typically csc.exe. It needs to be in PATH.
        return shutil.which("csc")

    def _compile_and_run_script(self):
        if self.process and self.process.state() != QProcess.ProcessState.NotRunning:
            return

        compiler = self._find_compiler()
        if not compiler:
            self.api.show_message("critical", "Compiler Not Found",
                                  "C# compiler (csc.exe) not found on your system PATH.\n"
                                  "Please ensure the .NET SDK is installed and its bin folder is in your PATH.")
            return

        editor = self.main_window.tab_widget.currentWidget()
        source_path = self.main_window.editor_tabs_data.get(editor, {}).get('filepath')
        if not source_path:
            return

        if self.main_window._is_editor_modified(editor):
            self.main_window._action_save_file()

        self.output_panel.clear_output()
        self.output_panel.append_output(f"[C#] Using compiler: {compiler}")

        base_name = os.path.splitext(os.path.basename(source_path))[0]
        self._output_exe_path = os.path.join(os.path.dirname(source_path), f"{base_name}.exe")

        command_args = [f"/out:{self._output_exe_path}", source_path]

        self._current_step = "COMPILE"
        self._start_process(compiler, command_args)

    def _start_process(self, program, args):
        self.process = QProcess()
        self.process.readyReadStandardOutput.connect(self._handle_stdout)
        self.process.readyReadStandardError.connect(self._handle_stderr)
        self.process.finished.connect(self._handle_finished)

        cmd_string = f"{program} {' '.join(args)}"
        self.output_panel.append_output(f"\n> {cmd_string}\n")
        self.run_cs_action.setEnabled(False)
        self.process.start(program, args)

    def _handle_stdout(self):
        if self.process:
            self.output_panel.append_output(self.process.readAllStandardOutput().data().decode(errors='replace'))

    def _handle_stderr(self):
        if self.process:
            self.output_panel.append_output(self.process.readAllStandardError().data().decode(), is_error=True)

    def _handle_finished(self, exit_code, exit_status):
        if self._current_step == "COMPILE":
            if exit_code == 0:
                self.output_panel.append_output("\n[C#] Compilation successful.")
                self._current_step = "RUN"
                self._start_process(self._output_exe_path, [])
            else:
                self.output_panel.append_output(f"\n[C#] Compilation failed.", is_error=True)
                self.run_cs_action.setEnabled(True)
        elif self._current_step == "RUN":
            self.output_panel.append_output(f"\n[C#] Execution finished.")
            if self._output_exe_path and os.path.exists(self._output_exe_path):
                try:
                    os.remove(self._output_exe_path)
                except OSError as e:
                    self.output_panel.append_output(f"Could not remove temp exe: {e}", is_error=True)
            self.run_cs_action.setEnabled(True)
        self._current_step = None


def initialize(puffin_api: PuffinPluginAPI):
    return CSharpToolsPlugin(puffin_api)
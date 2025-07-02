# /plugins/javascript_tools/plugin_main.py
import os
import shutil
from PyQt6.QtCore import QObject, QProcess
from app_core.puffin_api import PuffinPluginAPI
from utils.logger import log
# This import was pointing to the wrong file. I've corrected it!
from .javascript_syntax_highlighter import JavaScriptSyntaxHighlighter

class JavaScriptToolsPlugin(QObject):
    # The constructor now correctly accepts the puffin_api object.
    def __init__(self, puffin_api: PuffinPluginAPI):
        super().__init__()
        from ui.editor_widget import EditorWidget
        self.EditorWidgetClass = EditorWidget

        # This now correctly stores the API object.
        self.api = puffin_api
        self.main_window = self.api.get_main_window()
        self.runner_process = None
        self.output_panel = None

        self._setup_highlighter()
        self._setup_ui()
        self._connect_signals()

    def _setup_highlighter(self):
        """Register our JS highlighter with the core application for .js files."""
        self.api.register_highlighter('.js', JavaScriptSyntaxHighlighter)
        log.info("JavaScript Tools: Registered '.js' file highlighter.")

    def _setup_ui(self):
        """Add a 'Run JS File' action to the 'Run' menu."""
        self.run_js_action = self.api.add_menu_action(
            menu_name="run",
            text="Run JS File",
            callback=self._run_script,
            shortcut="Ctrl+F5",
            icon_name="fa5b.js-square"
        )
        self.run_js_action.setEnabled(False)
        self.run_js_action.setToolTip("Run the current JavaScript file using Node.js")

    def _connect_signals(self):
        """Connect to the main window's tab switching to enable/disable our action."""
        self.main_window.tab_widget.currentChanged.connect(self._on_tab_changed)
        self._on_tab_changed(self.main_window.tab_widget.currentIndex())

    def _on_tab_changed(self, index):
        """Enable or disable the run action based on the active file's extension."""
        from ui.editor_widget import EditorWidget
        is_js_file = False
        if index != -1:
            widget = self.main_window.tab_widget.widget(index)
            if isinstance(widget, EditorWidget):
                if (editor_data := self.main_window.editor_tabs_data.get(widget)):
                    filepath = editor_data.get('filepath', '')
                    if filepath and filepath.lower().endswith('.js'):
                        is_js_file = True

        self.run_js_action.setEnabled(is_js_file)

    def _run_script(self):
        """Execute the currently active JavaScript file."""
        current_widget = self.main_window.tab_widget.currentWidget()
        editor_data = self.main_window.editor_tabs_data.get(current_widget, {})
        filepath = editor_data.get('filepath')

        if not filepath:
            self.api.show_message("info", "Save File", "Please save the file before running.")
            return

        node_path = shutil.which("node")
        if not node_path:
            self.api.show_message("critical", "Node.js Not Found",
                                  "Could not find 'node' on your system PATH. Please install Node.js to run JavaScript files.")
            return

        if self.output_panel is None:
            runner_plugin = self.api.get_plugin_instance("python_runner")
            if not runner_plugin:
                self.api.show_message("critical", "Dependency Missing",
                                      "The Python Runner plugin, which provides the Output panel, is not loaded.")
                return
            self.output_panel = runner_plugin.output_panel

        if self.main_window._is_editor_modified(current_widget):
            self.main_window._action_save_file()

        self.output_panel.clear_output()
        self.output_panel.append_output(f"[NodeJS Runner] Executing: {os.path.basename(filepath)}...\n")

        self.runner_process = QProcess()
        self.runner_process.readyReadStandardOutput.connect(self._handle_stdout)
        self.runner_process.readyReadStandardError.connect(self._handle_stderr)
        self.runner_process.finished.connect(self._handle_finished)

        script_dir = os.path.dirname(filepath)
        self.runner_process.setWorkingDirectory(script_dir)
        self.runner_process.start(node_path, [filepath])

    def _handle_stdout(self):
        data = self.runner_process.readAllStandardOutput().data().decode(errors='replace')
        self.output_panel.append_output(data)

    def _handle_stderr(self):
        data = self.runner_process.readAllStandardError().data().decode(errors='replace')
        self.output_panel.append_output(data, is_error=True)

    def _handle_finished(self, exit_code, exit_status):
        self.output_panel.append_output(f"\n[NodeJS Runner] Process finished with exit code {exit_code}.")
        self.runner_process = None

# Corrected the signature here to match the others.
def initialize(puffin_api: PuffinPluginAPI):
    """Entry point for PuffinPyEditor to load the plugin."""
    return JavaScriptToolsPlugin(puffin_api)
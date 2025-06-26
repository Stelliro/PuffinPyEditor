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
            self.problems_panel, "Problems", Qt.DockWidgetArea.BottomDockWidgetArea, "fa5s.bug"
        )

    def _connect_signals(self):
        self.linter_manager.lint_results_ready.connect(self._update_problems)
        self.linter_manager.error_occurred.connect(
            lambda err: self.problems_panel.show_info_message(f"Linter Error: {err}"))
        self.problems_panel.problem_selected.connect(self.main_window._goto_definition_result)

    def _update_problems(self, problems: list):
        editor = self.main_window.tab_widget.currentWidget()
        if not isinstance(editor, EditorWidget):
            return

        filepath = self.main_window.editor_tabs_data.get(editor, {}).get('filepath')
        if filepath:
            self.problems_panel.update_problems({filepath: problems})


def initialize(main_window):
    return LinterUIPlugin(main_window)
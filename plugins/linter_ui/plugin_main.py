# PuffinPyEditor/plugins/linter_ui/plugin_main.py
from PyQt6.QtCore import Qt
from .problems_panel import ProblemsPanel

class LinterUIPlugin:
    def __init__(self, puffin_api):
        from ui.editor_widget import EditorWidget
        self.EditorWidgetClass = EditorWidget

        self.api = puffin_api
        self.main_window = self.api.get_main_window()
        self.linter_manager = self.api.get_manager("linter")
        self.problems_panel = ProblemsPanel(self.main_window)
        self._setup_ui()
        self._connect_signals()

    def _setup_ui(self):
        self.api.register_dock_panel(
            self.problems_panel, "Problems",
            Qt.DockWidgetArea.BottomDockWidgetArea, "fa5s.bug"
        )

    def _connect_signals(self):
        self.linter_manager.lint_results_ready.connect(self._update_problems)
        self.linter_manager.error_occurred.connect(
            lambda err: self.problems_panel.show_info_message(
                f"Linter Error: {err}")
        )
        self.problems_panel.problem_selected.connect(
            self.main_window._goto_definition_result)

    def _update_problems(self, problems: list):
        editor = self.main_window.tab_widget.currentWidget()
        if not isinstance(editor, self.EditorWidgetClass):
            return

        filepath = self.main_window.editor_tabs_data.get(
            editor, {}).get('filepath')
        if filepath:
            self.problems_panel.update_problems({filepath: problems})

def initialize(puffin_api):
    return LinterUIPlugin(puffin_api)
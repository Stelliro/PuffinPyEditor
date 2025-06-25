# PuffinPyEditor/plugins/source_control_ui/plugin_main.py
from PyQt6.QtCore import Qt
from project_source_control_panel import ProjectSourceControlPanel

class SourceControlUIPlugin:
    def __init__(self, main_window):
        self.api = main_window.puffin_api
        project_manager = self.api.get_manager("project"); git_manager = self.api.get_manager("git")
        self.source_control_panel = ProjectSourceControlPanel(project_manager, git_manager, main_window)
        self._setup_ui(); self._connect_signals()

    def _setup_ui(self):
        self.api.register_dock_panel(self.source_control_panel, "Source Control", Qt.DockWidgetArea.BottomDockWidgetArea, "fa5b.git-alt")

    def _connect_signals(self):
        main_window = self.api.get_main_window()
        # Refresh the panel when the active project changes or a git operation succeeds
        main_window.project_tabs.currentChanged.connect(self.source_control_panel.refresh_all_projects)
        main_window.theme_changed_signal.connect(self.source_control_panel.update_icons)
        self.api.get_manager("git").git_success.connect(self.source_control_panel.refresh_all_projects)

def initialize(main_window): return SourceControlUIPlugin(main_window)
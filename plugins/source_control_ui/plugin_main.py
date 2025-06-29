# PuffinPyEditor/plugins/source_control_ui/plugin_main.py
from PyQt6.QtCore import Qt
from .project_source_control_panel import ProjectSourceControlPanel


class SourceControlUIPlugin:
    def __init__(self, puffin_api):
        self.api = puffin_api
        project_manager = self.api.get_manager("project")
        git_manager = self.api.get_manager("git")
        main_window = self.api.get_main_window()

        self.source_control_panel = ProjectSourceControlPanel(
            project_manager, git_manager, main_window)
        self._setup_ui()
        self._connect_signals()

    def _setup_ui(self):
        self.api.register_dock_panel(
            self.source_control_panel, "Source Control",
            Qt.DockWidgetArea.BottomDockWidgetArea, "fa5b.git-alt"
        )

    def _connect_signals(self):
        main_window = self.api.get_main_window()
        plugin_manager = self.api.get_manager("plugin")

        # Get the project_explorer plugin instance, which is now a dependency
        project_explorer_plugin = plugin_manager.plugins.get('project_explorer').instance

        if project_explorer_plugin and hasattr(project_explorer_plugin, 'project_tabs'):
            # Connect to the project_tabs widget from the other plugin
            project_explorer_plugin.project_tabs.currentChanged.connect(
                self.source_control_panel.refresh_all_projects)
            self.api.log_info("SourceControlUI connected to ProjectExplorer's tabs.")
        else:
            self.api.log_warning("SourceControlUI: Could not find Project Explorer plugin to connect signals.")

        # Connect to other core signals
        main_window.theme_changed_signal.connect(self.source_control_panel.update_icons)
        self.api.get_manager("git").git_success.connect(
            self.source_control_panel.refresh_all_projects)
        self.api.get_manager("github").operation_success.connect(
            self.source_control_panel.refresh_all_projects)


def initialize(puffin_api):
    return SourceControlUIPlugin(puffin_api)
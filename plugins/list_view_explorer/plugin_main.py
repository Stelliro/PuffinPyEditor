# PuffinPyEditor/plugins/list_view_explorer/plugin_main.py
from PyQt6.QtWidgets import QWidget, QVBoxLayout
from PyQt6.QtCore import Qt
from app_core.puffin_api import PuffinPluginAPI
from utils.logger import log
from .list_view_widget import FileSystemListView

class ListViewExplorerPlugin:
    """
    Initializes and manages a single, unified file system view
    that can display multiple project folders as top-level items.
    """
    def __init__(self, puffin_api: PuffinPluginAPI):
        self.api = puffin_api
        self.main_window = self.api.get_main_window()
        self.project_manager = self.api.get_manager("project")
        
        # This is the single, unified tree view for all projects.
        self.view = FileSystemListView(self.api)

        # Register the view as a dockable panel.
        self.dock_widget = self.api.register_dock_panel(
            self.view, "Explorer",
            Qt.DockWidgetArea.LeftDockWidgetArea, "fa5s.compass"
        )
        if self.dock_widget:
            self.dock_widget.setProperty("plugin_instance", self)

        # --- Signal Connections ---
        # When projects are opened or closed, tell our single view to refresh.
        self.project_manager.projects_changed.connect(self.view.refresh)
        
        # When the user clicks an item in the tree, update the app's active project.
        self.view.tree_widget.currentItemChanged.connect(self._on_active_project_changed)

        # Perform the initial population of the tree.
        self.view.refresh()
        log.info("Unified List View Explorer initialized.")

    def _on_active_project_changed(self, current_item, previous_item):
        """
        Determines the root project of the selected item and sets it
        as the application's active project.
        """
        if not current_item:
            return

        # Traverse up the tree to find the top-level project item
        root_item = current_item
        while root_item.parent():
            root_item = root_item.parent()
        
        # Get the path from the root item and set it as active
        data = root_item.data(0, Qt.ItemDataRole.UserRole)
        if data and (path := data.get('path')):
            self.project_manager.set_active_project(path)

    def shutdown(self):
        """Cleans up resources when the plugin is unloaded."""
        if self.dock_widget:
            self.main_window.removeDockWidget(self.dock_widget)
            self.dock_widget.deleteLater()
        log.info("List View Explorer shut down.")


def initialize(puffin_api: PuffinPluginAPI):
    return ListViewExplorerPlugin(puffin_api)
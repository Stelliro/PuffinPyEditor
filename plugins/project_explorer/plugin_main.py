# PuffinPyEditor/plugins/project_explorer/plugin_main.py
import os
from PyQt6.QtWidgets import (QDockWidget, QTabWidget, QWidget, QVBoxLayout, QMenu, QStackedWidget)
from PyQt6.QtCore import Qt, pyqtSignal, QModelIndex
from .project_explorer_panel import FileTreeViewWidget, FullPathRole, IsDirRole


class NoProjectViewWidget(FileTreeViewWidget):
    """A specialized tree view for the 'no project open' view."""
    folder_open_requested = pyqtSignal(str)

    def _on_item_double_clicked(self, index: QModelIndex):
        if not index.isValid(): return
        path = index.data(FullPathRole)
        is_dir = index.data(IsDirRole) is True
        if path:
            if is_dir:
                self.folder_open_requested.emit(path)
            else:
                self.file_open_requested.emit(path)


class ProjectExplorerPlugin:
    def __init__(self, puffin_api):
        self.api = puffin_api
        self.main_window = self.api.get_main_window()
        self.project_manager = self.api.get_manager("project")
        self.file_handler = self.api.get_manager("file_handler")
        self.theme_manager = self.api.get_manager("theme")
        self._setup_ui()

    def _setup_ui(self):
        container = QWidget();
        container_layout = QVBoxLayout(container);
        container_layout.setContentsMargins(0, 0, 0, 0)
        self.stacked_widget = QStackedWidget();
        container_layout.addWidget(self.stacked_widget)

        self.no_project_view = NoProjectViewWidget(self.file_handler, self.theme_manager, self.main_window)
        self.project_tabs = QTabWidget();
        self.project_tabs.setDocumentMode(True);
        self.project_tabs.setTabsClosable(True);
        self.project_tabs.setMovable(True)

        self.stacked_widget.addWidget(self.no_project_view)
        self.stacked_widget.addWidget(self.project_tabs)

        self.file_tree_dock = QDockWidget("Project Explorer", self.main_window)
        self.file_tree_dock.setObjectName("ProjectExplorerDock");
        self.file_tree_dock.setWidget(container)
        self.main_window.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.file_tree_dock)

        toggle_action = self.file_tree_dock.toggleViewAction();
        toggle_action.setShortcut("Ctrl+Shift+E")
        if hasattr(self.main_window, 'view_menu'): self.main_window.view_menu.addAction(toggle_action)

        self._connect_signals()
        self.refresh_project_views()
        if not self.project_manager.get_open_projects(): self.file_tree_dock.close()

    def _connect_signals(self):
        self.project_tabs.tabCloseRequested.connect(self._action_close_project_by_index)
        self.project_tabs.currentChanged.connect(self._on_project_tab_changed)
        self.no_project_view.folder_open_requested.connect(self._on_no_project_folder_activated)
        self.main_window.theme_changed_signal.connect(self.update_all_themes)

    def update_all_themes(self, theme_id: str):
        self.no_project_view.update_theme()
        for i in range(self.project_tabs.count()):
            if isinstance(widget := self.project_tabs.widget(i), FileTreeViewWidget): widget.update_theme()

    def refresh_project_views(self):
        open_projects = self.project_manager.get_open_projects()
        if not open_projects:
            self.stacked_widget.setCurrentWidget(self.no_project_view)
            self.no_project_view.set_project_root(None)
            return

        self.stacked_widget.setCurrentWidget(self.project_tabs)
        active_project = self.project_manager.get_active_project_path()
        self.project_tabs.blockSignals(True)

        current_trees = {w.project_root_path: w for i in range(self.project_tabs.count()) if
                         isinstance(w := self.project_tabs.widget(i), FileTreeViewWidget)}
        self.project_tabs.clear()

        active_index = -1
        for i, path in enumerate(open_projects):
            tree = current_trees.get(path)
            if not tree:
                tree = FileTreeViewWidget(self.file_handler, self.theme_manager, self.main_window)
                tree.file_open_requested.connect(self.main_window._action_open_file)
                tree.file_to_open_created.connect(self.main_window._add_new_tab)
            tree.set_project_root(path)  # This is now a fast and synchronous call.

            tab_index = self.project_tabs.addTab(tree, os.path.basename(path).upper())
            self.project_tabs.setTabToolTip(tab_index, path)
            if path == active_project: active_index = i

        if active_index != -1: self.project_tabs.setCurrentIndex(active_index)
        self.project_tabs.blockSignals(False)
        self._on_project_tab_changed(self.project_tabs.currentIndex())

    def _on_no_project_folder_activated(self, path: str):
        if path and os.path.isdir(path):
            self.project_manager.open_project(path)
            self.main_window._broadcast_project_change()

    def _on_project_tab_changed(self, index: int):
        path = self.project_tabs.tabToolTip(index) if index != -1 else None
        self.project_manager.set_active_project(path)
        if self.main_window: self.main_window._update_window_title()

    def _action_close_project_by_index(self, index: int):
        if 0 <= index < self.project_tabs.count():
            path = self.project_tabs.tabToolTip(index)
            self.project_manager.close_project(path)
            self.main_window._broadcast_project_change()


def initialize(puffin_api):
    return ProjectExplorerPlugin(puffin_api)
# PuffinPyEditor/app_core/puffin_api.py
from typing import Callable, Optional
from PyQt6.QtWidgets import QDockWidget, QTabWidget, QWidget, QMenu, QMessageBox
from PyQt6.QtGui import QAction
from PyQt6.QtCore import Qt
import qtawesome as qta
from utils.logger import log


class PuffinPluginAPI:
    """A stable API for plugins to interact with the MainWindow."""

    def __init__(self, main_window):
        self._main_window = main_window
        # Attributes to manage the shared bottom dock area
        self._bottom_dock_widget: Optional[QDockWidget] = None
        self._bottom_tab_widget: Optional[QTabWidget] = None
        log.info("PuffinPluginAPI initialized.")

    def get_main_window(self):
        return self._main_window

    def get_manager(self, manager_name: str) -> Optional[object]:
        manager_map = {
            "settings": self._main_window.settings, "theme": self._main_window.theme_manager,
            "project": self._main_window.project_manager, "completion": self._main_window.completion_manager,
            "github": self._main_window.github_manager, "git": self._main_window.git_manager,
            "file_handler": self._main_window.file_handler, "linter": self._main_window.linter_manager,
            "update": self._main_window.update_manager,
            "plugin": self._main_window.plugin_manager
        }
        manager = manager_map.get(manager_name.lower())
        if not manager: log.warning(f"Plugin requested unknown manager: '{manager_name}'")
        return manager

    def get_menu(self, menu_name: str) -> QMenu:
        name_map = {"file": self._main_window.file_menu, "edit": self._main_window.edit_menu,
                    "view": self._main_window.view_menu, "go": self._main_window.go_menu,
                    "run": self._main_window.run_menu, "tools": self._main_window.tools_menu,
                    "help": self._main_window.help_menu}
        # Allow plugins to get the core debug menu if it exists
        if hasattr(self._main_window, 'debug_menu'):
            name_map['debug'] = self._main_window.debug_menu

        if menu_name.lower() in name_map: return name_map[menu_name.lower()]

        # Check for menus created by other plugins
        for action in self._main_window.menuBar().actions():
            if isinstance(action.menu(), QMenu) and action.text().replace('&', '').lower() == menu_name.lower():
                return action.menu()

        log.info(f"Creating new top-level menu for plugin: '{menu_name}'")
        return self._main_window.menuBar().addMenu(f"&{menu_name.capitalize()}")

    def add_menu_action(self, menu_name: str, text: str, callback: Callable, shortcut: Optional[str] = None,
                        icon_name: Optional[str] = None):
        menu = self.get_menu(menu_name)
        action = menu.addAction(qta.icon(icon_name), text) if icon_name else menu.addAction(text)
        if shortcut: action.setShortcut(shortcut)
        action.triggered.connect(callback)
        log.info(f"Added action '{text}' to menu '{menu_name}'.")
        return action

    def add_toolbar_action(self, action: QAction):
        self._main_window.main_toolbar.addAction(action)
        log.info(f"Added action '{action.text()}' to main toolbar.")

    def register_dock_panel(self, panel_widget: QWidget, title: str, area: Qt.DockWidgetArea, icon_name: str = None):
        if area == Qt.DockWidgetArea.BottomDockWidgetArea:
            if self._bottom_tab_widget is None:
                log.info("Creating shared bottom dock area for plugins.")
                self._bottom_dock_widget = QDockWidget("Info Panels", self._main_window)
                self._bottom_dock_widget.setObjectName("SharedBottomDock")
                self._bottom_tab_widget = QTabWidget()
                self._bottom_tab_widget.setDocumentMode(True)
                self._bottom_dock_widget.setWidget(self._bottom_tab_widget)
                self._main_window.addDockWidget(area, self._bottom_dock_widget)
                self._main_window.view_menu.addSeparator()
                self._main_window.view_menu.addAction(self._bottom_dock_widget.toggleViewAction())

            icon = qta.icon(icon_name) if icon_name else None
            self._bottom_tab_widget.addTab(panel_widget, icon, title)
        else:
            dock = QDockWidget(title, self._main_window)
            dock.setWidget(panel_widget)
            self._main_window.addDockWidget(area, dock)
            self._main_window.view_menu.addSeparator()
            self._main_window.view_menu.addAction(dock.toggleViewAction())
        log.info(f"Registered panel '{title}'")
    
    def register_file_opener(self, extension: str, handler_func: Callable):
        """
        Registers a function to handle opening files with a specific extension.
        The handler function will receive the full filepath as its only argument.

        Args:
            extension: The file extension to handle (e.g., '.md', '.csv').
            handler_func: The function to call when a file with this extension is opened.
        """
        if not extension.startswith('.'):
            extension = '.' + extension
        self._main_window.file_open_handlers[extension.lower()] = handler_func
        log.info(f"Registered custom opener for '{extension}' files.")

    def show_message(self, level: str, title: str, text: str):
        level_map = {'info': QMessageBox.Icon.Information, 'warning': QMessageBox.Icon.Warning,
                     'critical': QMessageBox.Icon.Critical}
        QMessageBox(level_map.get(level, QMessageBox.Icon.NoIcon), title, text, parent=self._main_window).exec()

    def show_status_message(self, text: str, timeout_ms: int = 3000):
        self._main_window.statusBar().showMessage(text, timeout_ms)

    def log_info(self, message: str):
        """Logs an informational message."""
        log.info(f"[Plugin] {message}")

    def log_warning(self, message: str):
        """Logs a warning message."""
        log.warning(f"[Plugin] {message}")

    def log_error(self, message: str):
        """Logs an error message."""
        log.error(f"[Plugin] {message}")
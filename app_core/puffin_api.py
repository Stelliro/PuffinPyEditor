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
        self._bottom_dock_widget: Optional[QDockWidget] = None
        self._bottom_tab_widget: Optional[QTabWidget] = None
        log.info("PuffinPluginAPI initialized.")

    def get_main_window(self):
        """Returns the main application window instance."""
        return self._main_window

    def get_manager(self, manager_name: str) -> Optional[object]:
        """
        Gets a core application manager instance by name.
        This uses if/elif to avoid creating a large dictionary and eagerly
        evaluating all manager attributes on every call.
        """
        name = manager_name.lower()
        if name == "settings":
            return self._main_window.settings
        elif name == "theme":
            return self._main_window.theme_manager
        elif name == "project":
            return self._main_window.project_manager
        elif name == "completion":
            return self._main_window.completion_manager
        elif name == "github":
            return self._main_window.github_manager
        elif name == "git":
            return self._main_window.git_manager
        elif name == "file_handler":
            return self._main_window.file_handler
        elif name == "linter":
            return self._main_window.linter_manager
        elif name == "update":
            return self._main_window.update_manager
        elif name == "plugin":
            return self._main_window.plugin_manager

        log.warning(f"Plugin requested unknown manager: '{manager_name}'")
        return None

    def get_menu(self, menu_name: str) -> Optional[QMenu]:
        """Gets a QMenu by name. Does not create new menus."""
        return getattr(self._main_window, f"{menu_name}_menu", None)

    def add_menu_action(self, menu_name: str, text: str, callback: Callable,
                        shortcut: Optional[str] = None, icon_name: Optional[str] = None) -> QAction:
        """Adds an action to a menu, creating the menu in a standard order if it doesn't exist."""
        menu = self.get_menu(menu_name)
        if not menu:
            log.info(f"Menu '{menu_name}' not found. Creating it dynamically.")
            menu_bar = self._main_window.menuBar()

            # Define the standard order of menus
            standard_order = ["file", "edit", "view", "go", "run", "tools", "help"]

            # Find the correct action to insert the new menu before
            insert_before_action = None
            current_menu_index = standard_order.index(menu_name) if menu_name in standard_order else -1

            if current_menu_index != -1:
                # Find the next menu in the standard order that already exists
                for next_menu_name in standard_order[current_menu_index + 1:]:
                    if next_menu := self.get_menu(next_menu_name):
                        insert_before_action = next_menu.menuAction()
                        break

            new_menu = QMenu(f"&{menu_name.capitalize()}", self._main_window)

            if insert_before_action:
                menu_bar.insertMenu(insert_before_action, new_menu)
            else:
                # If no subsequent menu is found (e.g., adding a new last menu), just add it
                menu_bar.addMenu(new_menu)

            menu = new_menu
            setattr(self._main_window, f"{menu_name}_menu", menu)
            log.info(f"Dynamically created and inserted menu '{menu_name}'.")

        icon = qta.icon(icon_name) if icon_name else None
        action = QAction(icon, text, self._main_window)
        if icon_name:
            action.setData(icon_name)
        if shortcut:
            action.setShortcut(shortcut)
        action.triggered.connect(callback)
        menu.addAction(action)
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
        log.info(f"[Plugin] {message}")

    def log_warning(self, message: str):
        log.warning(f"[Plugin] {message}")

    def log_error(self, message: str):
        log.error(f"[Plugin] {message}")
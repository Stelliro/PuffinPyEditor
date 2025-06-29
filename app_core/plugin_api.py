# PuffinPyEditor/app_core/plugin_api.py
from utils.logger import log


class PluginAPI:
    """A dedicated, safe API for plugins to interact with the editor."""

    def __init__(self, main_window):
        self._main_window = main_window
        self.log = log  # Expose the logger safely

    def get_main_window(self):
        """Provides access to the main application window."""
        return self._main_window

    def add_menu_item(self, menu_name: str, item_name: str, callback):
        """Adds a new item to a specified top-level menu."""
        # In a real Qt/Tkinter app, you would find the menu and add the action.
        log.info(f"API: Adding '{item_name}' to menu '{menu_name}'.")
        # self._main_window.menuBar().findChild(QMenu, menu_name).addAction(...)

    def get_current_editor_text(self) -> str:
        """Returns the full text of the currently active editor tab."""
        # return self._main_window.tab_widget.currentWidget().toPlainText()
        log.info("API: Getting current editor text.")
        return "Example text from the current editor."

    def set_current_editor_text(self, text: str):
        """Sets the full text of the currently active editor tab."""
        # self._main_window.tab_widget.currentWidget().setPlainText(text)
        log.info("API: Setting current editor text.")
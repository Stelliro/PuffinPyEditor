# PuffinPyEditor/plugins/terminal/plugin_main.py
from PyQt6.QtCore import Qt
from utils.logger import log
from .terminal_widget import TerminalWidget

class TerminalPlugin:
    def __init__(self, puffin_api):
        self.api = puffin_api
        self.terminal_widget = None

        self._setup_ui()
        log.info("Integrated Terminal plugin initialized.")

    def _setup_ui(self):
        """Creates and registers the terminal panel and menu action."""
        # Create an instance of our terminal widget
        self.terminal_widget = TerminalWidget(self.api)
        
        # Register it as a dockable panel at the bottom of the window
        dock = self.api.register_dock_panel(
            self.terminal_widget, 
            "Terminal", 
            Qt.DockWidgetArea.BottomDockWidgetArea, 
            "fa5s.terminal"
        )
        
        # Add a menu item to the "View" menu to toggle the terminal's visibility
        if dock:
            self.api.add_menu_action(
                menu_name="view",
                text="Terminal",
                callback=dock.toggleViewAction().trigger,
                icon_name="fa5s.terminal"
            )

    def shutdown(self):
        """Called by the plugin manager to clean up resources."""
        if self.terminal_widget:
            self.terminal_widget.stop_process()
        log.info("Integrated Terminal plugin shut down.")


def initialize(puffin_api):
    """Entry point for PuffinPyEditor to load the plugin."""
    try:
        return TerminalPlugin(puffin_api)
    except Exception as e:
        log.error(f"Failed to initialize Terminal Plugin: {e}", exc_info=True)
        return None
# PuffinPyEditor/core_debug_tools/debug_framework/plugin_main.py
from utils.logger import log
from .api import PuffinDebugAPI
from .debug_window import DebugWindow


class DebugFrameworkPlugin:
    def __init__(self, main_window):
        self.main_window = main_window
        self.puffin_api = main_window.puffin_api
        self.debug_window = None

        log.info("Initializing Debug Tools Framework...")

        # Create the 'Debug' menu if it doesn't exist
        if not hasattr(self.main_window, 'debug_menu'):
            self.main_window.debug_menu = self.main_window.menuBar().addMenu("&Debug")

        # Create the Debug API and attach it to the main window
        self.main_window.debug_api = PuffinDebugAPI(self)

        # Add the main action to show the debugger window
        self.main_window.debug_api.puffin_api = self.puffin_api  # Cross-reference
        self.puffin_api.add_menu_action(
            menu_name="debug",
            text="Show Debugger",
            callback=self.show_debugger_window,
            icon_name="fa5s.bug"
        )
        log.info("Debug Framework initialized and attached to MainWindow.")

    def show_debugger_window(self):
        """Shows the main debugger window, creating it if necessary."""
        if self.debug_window is None or not self.debug_window.isVisible():
            # Pass the PuffinAPI to the debug window so it can pass it to tools
            self.debug_window = DebugWindow(self.puffin_api, self.main_window)
            # Re-register any tools that might have been registered before window was shown
            for name, widget_class in self.main_window.debug_api.registered_tools.items():
                self.debug_window.add_tool_tab(name, widget_class)

        self.debug_window.show()
        self.debug_window.raise_()
        self.debug_window.activateWindow()

    def add_tool_tab(self, tool_name: str, widget_class: type):
        """Callback for the DebugAPI to add a tab to our window."""
        if self.debug_window:
            self.debug_window.add_tool_tab(tool_name, widget_class)
        else:
            # Window not created yet, API will handle queuing it
            pass


def initialize(main_window):
    """Entry point for the Debug Framework plugin."""
    return DebugFrameworkPlugin(main_window)
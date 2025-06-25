# PuffinPyEditor/core_debug_tools/debug_framework/plugin_main.py
from .api import PuffinDebugAPI  # CORRECTED IMPORT: Use relative import
from .debug_window import DebugWindow
from utils.logger import log


class DebugFrameworkPlugin:
    def __init__(self, main_window):
        self.main_window = main_window
        self.puffin_api = main_window.puffin_api
        self.debug_window = None

        log.info("Initializing Debug Framework Plugin.")
        self._setup_api_and_menu()

    def _setup_api_and_menu(self):
        """Creates the Debug menu and attaches the debug API."""
        if hasattr(self.main_window, 'debug_api'):
            log.warning("Debug API already exists. Skipping setup.")
            return

        self.debug_window = DebugWindow(self.puffin_api, self.main_window)

        # Attach the specialized debug API to the main window for other debug tools
        self.main_window.debug_api = PuffinDebugAPI(self.debug_window)

        # Create the main "Debug" menu using the core API
        # Store the menu on the main window so other plugins can add to it.
        self.main_window.debug_menu = self.puffin_api.get_menu("debug")

        self.puffin_api.add_menu_action(
            menu_name="debug",
            text="Show Debugger Window",
            callback=self.show_debug_window,
            icon_name="fa5s.cogs"
        )
        self.main_window.debug_menu.addSeparator()

    def show_debug_window(self):
        """Shows the main debugger window."""
        if self.debug_window:
            self.debug_window.show()
            self.debug_window.raise_()
            self.debug_window.activateWindow()


def initialize(main_window):
    """Entry point for the Debug Framework plugin."""
    return DebugFrameworkPlugin(main_window)
# PuffinPyEditor/plugins/terminal/plugin_main.py
from PyQt6.QtCore import Qt
from utils.logger import log
from .terminal_widget import TerminalWidget
from app_core.puffin_api import PuffinPluginAPI


class TerminalPlugin:
    def __init__(self, puffin_api: PuffinPluginAPI):
        self.api = puffin_api
        self.terminal_widget = None

        self._setup_ui()
        log.info("Integrated Terminal plugin initialized.")

    def _setup_ui(self):
        """Creates and registers the terminal panel and menu action."""
        self.terminal_widget = TerminalWidget(self.api)

        dock = self.api.add_dock_panel(
            area_str="bottom",
            widget=self.terminal_widget,
            title="Terminal",
            icon_name="mdi.console"
        )

        if dock:
            self.api.add_menu_action(
                menu_name="view",
                text="Terminal",
                callback=dock.toggleViewAction().trigger,
                icon_name="mdi.console"
            )

    def shutdown(self):
        """
        Called by the plugin manager or main window to ensure the terminal's
        underlying shell process is terminated correctly.
        """
        if self.terminal_widget:
            self.terminal_widget.stop_process()
            log.info("Terminal process stopped on shutdown request.")


def initialize(puffin_api: PuffinPluginAPI):
    """Entry point for PuffinPyEditor to load the plugin."""
    try:
        return TerminalPlugin(puffin_api)
    except Exception as e:
        log.error(f"Failed to initialize Terminal Plugin: {e}", exc_info=True)
        return None
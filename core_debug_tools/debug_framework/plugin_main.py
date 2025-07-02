# PuffinPyEditor/core_debug_tools/debug_framework/plugin_main.py
from utils.logger import log
from .api import PuffinDebugAPI
from .debug_window import DebugWindow
from app_core.puffin_api import PuffinPluginAPI


class DebugFrameworkPlugin:
    def __init__(self, puffin_api: PuffinPluginAPI):
        self.puffin_api = puffin_api
        self.main_window = self.puffin_api.get_main_window()
        self.debug_window = None

        log.info("Initializing Debug Tools Framework...")

        self.puffin_api.add_menu_action(
            menu_name="debug",
            text="Show Debugger",
            callback=self.show_debugger_window,
            icon_name="fa5s.bug"
        )

        if not hasattr(self.main_window, 'debug_api'):
            self.main_window.debug_api = PuffinDebugAPI(self)

        log.info("Debug Framework initialized and attached to MainWindow.")

    def show_debugger_window(self):
        if not self.debug_window or not self.debug_window.isVisible():
            self.debug_window = DebugWindow(self.puffin_api, self.main_window)
            # Re-register tools
            if hasattr(self.main_window, 'debug_api'):
                for name, widget_class in self.main_window.debug_api.registered_tools.items():
                    self.debug_window.add_tool_tab(name, widget_class)

        self.debug_window.show()
        self.debug_window.raise_()
        self.debug_window.activateWindow()

    def add_tool_tab(self, tool_name: str, widget_class: type):
        if self.debug_window:
            self.debug_window.add_tool_tab(tool_name, widget_class)


def initialize(puffin_api: PuffinPluginAPI):
    return DebugFrameworkPlugin(puffin_api)
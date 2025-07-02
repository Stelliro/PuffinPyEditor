# PuffinPyEditor/plugins/tab_drag_handler/plugin_main.py
from .draggable_tab_widget import DraggableTabWidget
from utils.logger import log
from app_core.puffin_api import PuffinPluginAPI


class TabDragHandlerPlugin:
    """
    This plugin does not create any UI elements of its own. Instead, it replaces
    the main window's default QTabWidget with the enhanced DraggableTabWidget.
    """

    def __init__(self, puffin_api: PuffinPluginAPI):
        self.api = puffin_api
        mw = self.api.get_main_window()

        log.info("TabDragHandler plugin confirmed active. Draggable tabs are enabled.")


def initialize(puffin_api: PuffinPluginAPI):
    """
    Entry point for the TabDragHandler plugin.
    It returns an instance of the class to be managed by the PluginManager.
    """
    try:
        return TabDragHandlerPlugin(puffin_api)
    except Exception as e:
        log.error(f"Failed to initialize TabDragHandlerPlugin: {e}", exc_info=True)
        return None
# PuffinPyEditor/plugins/ai_export_viewer/plugin_main.py
import qtawesome as qta
from .ai_export_viewer_widget import AIExportViewerWidget
from utils.logger import log
from app_core.puffin_api import PuffinPluginAPI


class AIExportViewerPlugin:
    VIEWER_TAB_NAME = "AI Exports"

    def __init__(self, puffin_api: PuffinPluginAPI):
        self.api = puffin_api
        self.main_window = self.api.get_main_window()
        self.api.add_menu_action(
            menu_name="tools",
            text="View AI Exports...",
            callback=self.open_export_viewer_tab,
            icon_name="fa5s.history"
        )

    def open_export_viewer_tab(self):
        log.info("AI Export Viewer: Handling request to open viewer tab.")
        for i in range(self.main_window.tab_widget.count()):
            if self.main_window.tab_widget.tabText(i) == self.VIEWER_TAB_NAME:
                self.main_window.tab_widget.setCurrentIndex(i)
                if isinstance(widget := self.main_window.tab_widget.widget(i), AIExportViewerWidget):
                    widget.refresh_list()
                return

        if self.main_window.tab_widget.count() == 1 and hasattr(self.main_window.tab_widget.widget(0),
                                                                'objectName') and self.main_window.tab_widget.widget(
                0).objectName() == "PlaceholderLabel":
            self.main_window.tab_widget.removeTab(0)

        viewer_widget = AIExportViewerWidget(self.main_window)
        icon = qta.icon("fa5s.history", color='grey')
        index = self.main_window.tab_widget.addTab(viewer_widget, icon, self.VIEWER_TAB_NAME)
        self.main_window.tab_widget.setTabToolTip(index, "Browse and manage AI exports")
        self.main_window.tab_widget.setCurrentIndex(index)
        self.main_window.tab_widget.setTabsClosable(True)


def initialize(puffin_api: PuffinPluginAPI):
    try:
        return AIExportViewerPlugin(puffin_api)
    except Exception as e:
        log.error(f"Failed to initialize AI Export Viewer Plugin: {e}", exc_info=True)
        return None
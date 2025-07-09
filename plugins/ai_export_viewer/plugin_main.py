# /plugins/ai_export_viewer/plugin_main.py
from app_core.puffin_api import PuffinPluginAPI
from .ai_export_viewer_widget import AIExportViewerWidget
from utils.logger import log


class AIExportViewerPlugin:
    """Plugin to view AI-generated export files."""

    def __init__(self, puffin_api: PuffinPluginAPI):
        self.api = puffin_api
        self.main_window = self.api.get_main_window()
        self.viewer_widget = None

        self.api.add_menu_action(
            menu_name="tools",
            text="View AI Exports",
            callback=self.open_viewer_tab,
            icon_name="fa5s.robot"
        )
        log.info("AI Export Viewer plugin initialized and menu action added.")

    def open_viewer_tab(self):
        """Opens a new tab containing the AI Export Viewer widget."""
        self.viewer_widget = AIExportViewerWidget(
            theme_manager=self.api.get_manager("theme"),
            parent=self.main_window
        )

        for i in range(self.main_window.tab_widget.count()):
            if isinstance(self.main_window.tab_widget.widget(i), AIExportViewerWidget):
                self.main_window.tab_widget.setCurrentIndex(i)
                return

        index = self.main_window.tab_widget.addTab(self.viewer_widget, "AI Exports")
        self.main_window.tab_widget.setCurrentIndex(index)
        self.main_window.tab_widget.setTabsClosable(True)


def initialize(puffin_api: PuffinPluginAPI):
    """Entry point for PuffinPyEditor to load the plugin."""
    try:
        return AIExportViewerPlugin(puffin_api)
    except Exception as e:
        log.error(f"Failed to initialize AI Export Viewer: {e}", exc_info=True)
        return None
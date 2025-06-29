# PuffinPyEditor/plugins/ai_export_viewer/plugin_main.py
import qtawesome as qta
from .ai_export_viewer_widget import AIExportViewerWidget
from utils.logger import log


class AIExportViewerPlugin:
    """
    Manages the lifecycle and functionality of the AI Export Viewer.
    Opens the viewer in a persistent tab instead of a modal dialog.
    """
    VIEWER_TAB_NAME = "AI Exports"

    def __init__(self, main_window):
        self.api = main_window.puffin_api
        self.main_window = self.api.get_main_window()
        self.api.add_menu_action(
            menu_name="tools",
            text="View AI Exports...",
            callback=self.open_export_viewer_tab,
            icon_name="fa5s.history"
        )

    def open_export_viewer_tab(self):
        """
        Opens the AI Export Viewer in a new tab, or focuses it if already open.
        """
        log.info("AI Export Viewer: Handling request to open viewer tab.")

        # Check if the viewer tab is already open
        for i in range(self.main_window.tab_widget.count()):
            tab_text = self.main_window.tab_widget.tabText(i)
            if tab_text == self.VIEWER_TAB_NAME:
                self.main_window.tab_widget.setCurrentIndex(i)
                widget = self.main_window.tab_widget.widget(i)
                if isinstance(widget, AIExportViewerWidget):
                    widget.refresh_list()
                return

        # If a placeholder "Welcome" tab exists, remove it
        if self.main_window.tab_widget.count() == 1:
            current_widget = self.main_window.tab_widget.widget(0)
            is_placeholder = (hasattr(current_widget, 'objectName') and
                              current_widget.objectName() == "PlaceholderLabel")
            if is_placeholder:
                self.main_window.tab_widget.removeTab(0)

        # Create the viewer widget and add it to a new tab
        viewer_widget = AIExportViewerWidget(self.main_window)
        icon = qta.icon("fa5s.history", color='grey')
        index = self.main_window.tab_widget.addTab(
            viewer_widget, icon, self.VIEWER_TAB_NAME
        )
        self.main_window.tab_widget.setTabToolTip(
            index, "Browse and manage AI exports")
        self.main_window.tab_widget.setCurrentIndex(index)
        self.main_window.tab_widget.setTabsClosable(True)


def initialize(main_window):
    """
    Entry point function for PuffinPyEditor to load the plugin.
    """
    try:
        plugin_instance = AIExportViewerPlugin(main_window)
        log.info("AI Export Viewer Plugin initialized successfully.")
        return plugin_instance
    except Exception as e:
        log.error(
            f"Failed to initialize AI Export Viewer Plugin: {e}", exc_info=True
        )
        return None
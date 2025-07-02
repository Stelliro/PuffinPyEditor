# /plugins/markdown_viewer/plugin_main.py
import os
from .markdown_editor_widget import MarkdownEditorWidget
from utils.logger import log
from app_core.puffin_api import PuffinPluginAPI


class MarkdownPlugin:
    """
    Manages the lifecycle and functionality of the Markdown Editor plugin.
    This version uses the file opener hook to handle .md files.
    """

    def __init__(self, puffin_api: PuffinPluginAPI):
        # The API object is passed in.
        self.api = puffin_api
        # We get the actual main window widget from the API.
        self.main_window = self.api.get_main_window()

        # Register this plugin as the handler for .md files
        self.api.register_file_opener('.md', self.open_markdown_file)
        log.info("Markdown Editor: Registered as handler for .md files.")

    def open_markdown_file(self, filepath: str):
        """
        Callback function to open a .md file in the custom editor.
        This is called by MainWindow when a .md file is opened.
        """
        log.info(f"Markdown Editor: Handling request to open '{filepath}'.")

        # Check if this file is already open in a viewer
        for i in range(self.main_window.tab_widget.count()):
            widget = self.main_window.tab_widget.widget(i)
            if (isinstance(widget, MarkdownEditorWidget) and
                    widget.filepath == filepath):
                self.main_window.tab_widget.setCurrentIndex(i)
                return

        # If a placeholder "Welcome" tab exists, remove it
        if self.main_window.tab_widget.count() == 1:
            current_widget = self.main_window.tab_widget.widget(0)
            is_placeholder = (hasattr(current_widget, 'objectName') and
                              current_widget.objectName() == "PlaceholderLabel")
            if is_placeholder:
                self.main_window.tab_widget.removeTab(0)

        # Now, `self.main_window` is a proper QWidget, so it's a valid parent.
        editor = MarkdownEditorWidget(self.main_window)
        editor.load_file(filepath)
        # Connect editor's signal to the main window's handler
        editor.content_changed.connect(self.main_window._on_content_changed)

        tab_name = os.path.basename(filepath)
        index = self.main_window.tab_widget.addTab(editor, tab_name)
        self.main_window.tab_widget.setTabToolTip(index, filepath)
        self.main_window.tab_widget.setCurrentIndex(index)
        self.main_window.tab_widget.setTabsClosable(True)


def initialize(puffin_api: PuffinPluginAPI):
    """
    Entry point function for PuffinPyEditor to load the plugin.
    """
    try:
        # Pass the API object to the plugin's constructor
        plugin_instance = MarkdownPlugin(puffin_api)
        log.info("Markdown Editor Plugin initialized successfully.")
        return plugin_instance
    except Exception as e:
        log.error(
            f"Failed to initialize Markdown Editor Plugin: {e}", exc_info=True
        )
        return None
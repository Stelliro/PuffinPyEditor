# /plugins/markdown_viewer/plugin_main.py
import os
from .markdown_editor_widget import MarkdownEditorWidget
from utils.logger import log
from app_core.puffin_api import PuffinPluginAPI


class MarkdownPlugin:
    """
    Manages the lifecycle and functionality of the Markdown Editor plugin.
    Provides a dual-pane editor with live preview for Markdown files.
    """

    def __init__(self, puffin_api: PuffinPluginAPI):
        self.api = puffin_api
        self.main_window = self.api.get_main_window()
        self.completion_manager = self.api.get_manager("completion")
        self.instances = {}  # Track open editor instances

        # Register our custom editor widget as the handler for .md files
        self.api.register_file_opener('.md', self.open_markdown_editor)
        log.info("Markdown Editor: Registered dual-pane handler for .md files.")

    def open_markdown_editor(self, filepath: str):
        """
        Callback to open a .md file in our custom MarkdownEditorWidget.
        It creates a new tab with the dual-pane editor or focuses an existing one.
        """
        # If file is already open, just switch to its tab
        if filepath in self.instances:
            widget = self.instances[filepath]
            if widget:
                index = self.main_window.tab_widget.indexOf(widget)
                if index != -1:
                    self.main_window.tab_widget.setCurrentIndex(index)
                    return

        # Remove placeholder if this is the first real tab
        if self.main_window.tab_widget.count() == 1:
            if current_widget := self.main_window.tab_widget.widget(0):
                if current_widget.objectName() == "PlaceholderLabel":
                    self.main_window.tab_widget.removeTab(0)

        log.info(f"Markdown Editor: Creating new dual-pane view for '{filepath}'.")

        editor = MarkdownEditorWidget(
            puffin_api=self.api,
            completion_manager=self.completion_manager,
            parent=self.main_window
        )
        editor.load_file(filepath)
        editor.content_changed.connect(lambda: self.main_window._on_content_changed(editor))

        # Add the widget to a new tab
        tab_name = os.path.basename(filepath)
        index = self.main_window.tab_widget.addTab(editor, tab_name)
        self.main_window.tab_widget.setTabToolTip(index, filepath)
        self.main_window.tab_widget.setCurrentIndex(index)
        self.main_window.tab_widget.setTabsClosable(True)

        # Store instance for tracking and to prevent duplicates
        self.instances[filepath] = editor
        editor.destroyed.connect(lambda: self.instances.pop(filepath, None))


def initialize(puffin_api: PuffinPluginAPI):
    """Entry point for PuffinPyEditor to load the plugin."""
    try:
        plugin_instance = MarkdownPlugin(puffin_api)
        log.info("Markdown Editor Plugin (dual-pane) initialized successfully.")
        return plugin_instance
    except Exception as e:
        log.error(f"Failed to initialize Markdown Editor Plugin: {e}", exc_info=True)
        return None
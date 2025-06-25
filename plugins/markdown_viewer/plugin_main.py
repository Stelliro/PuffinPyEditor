# /plugins/markdown_viewer/plugin_main.py
import os
from utils.logger import log
from markdown_editor_widget import MarkdownEditorWidget

class MarkdownPlugin:
    """
    Manages the lifecycle and functionality of the Markdown Editor plugin.
    This version automatically opens .md files in the custom editor.
    """
    def __init__(self, main_window):
        self.main_window = main_window
        self.original_open_file_func = None

    def activate(self):
        """
        Activates the plugin by patching the main window's file opening method
        to handle .md files with the custom editor.
        """
        # Store the original function and replace it with our patched version
        self.original_open_file_func = self.main_window._action_open_file
        self.main_window._action_open_file = self._patched_open_file
        log.info("Markdown Editor: Patched MainWindow._action_open_file to handle .md files.")

    def _patched_open_file(self, filepath, content=None):
        """
        Our replacement function. It checks the file extension and either
        opens the Markdown editor or calls the original function.
        """
        if filepath and filepath.lower().endswith('.md'):
            log.info(f"Markdown Editor: Intercepted request to open '{filepath}'.")
            self._create_markdown_editor_tab(filepath=filepath)
        else:
            # For any other file type, call the original function
            if self.original_open_file_func:
                self.original_open_file_func(filepath, content)

    def _create_markdown_editor_tab(self, filepath):
        """Creates and adds a new MarkdownEditorWidget tab."""
        # Check if this file is already open in a viewer
        for i in range(self.main_window.tab_widget.count()):
            widget = self.main_window.tab_widget.widget(i)
            if isinstance(widget, MarkdownEditorWidget) and widget.filepath == filepath:
                self.main_window.tab_widget.setCurrentIndex(i)
                return

        # If placeholder tab exists, remove it
        if self.main_window.tab_widget.count() == 1:
             current_widget = self.main_window.tab_widget.widget(0)
             if hasattr(current_widget, 'objectName') and current_widget.objectName() == "PlaceholderLabel":
                  self.main_window.tab_widget.removeTab(0)

        editor = MarkdownEditorWidget(self.main_window)
        editor.load_file(filepath)
        # Connect the editor's content changed signal to the main window's handler
        editor.content_changed.connect(self.main_window._on_content_changed)

        tab_name = os.path.basename(filepath)
        index = self.main_window.tab_widget.addTab(editor, tab_name)
        self.main_window.tab_widget.setTabToolTip(index, filepath)
        self.main_window.tab_widget.setCurrentIndex(index)
        self.main_window.tab_widget.setTabsClosable(True)

def initialize(main_window):
    """
    Entry point function for PuffinPyEditor to load the plugin.
    """
    try:
        plugin_instance = MarkdownPlugin(main_window)
        plugin_instance.activate()
        log.info("Markdown Editor Plugin initialized successfully.")
        return plugin_instance
    except Exception as e:
        log.error(f"Failed to initialize Markdown Editor Plugin: {e}", exc_info=True)
        return None
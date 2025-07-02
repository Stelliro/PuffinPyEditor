# /plugins/html_tools/plugin_main.py
import os
import tempfile
from PyQt6.QtGui import QDesktopServices
from PyQt6.QtCore import QObject, QUrl
from PyQt6.QtWidgets import QApplication

from utils.logger import log
from .html_syntax_highlighter import HtmlSyntaxHighlighter
from app_core.puffin_api import PuffinPluginAPI # I've added this for proper type hinting!

# I'm keeping this global variable for the temporary file logic.
_temp_preview_file = None


def cleanup_temp_file():
    """Function to clean up the temp file on application exit."""
    global _temp_preview_file
    if _temp_preview_file and os.path.exists(_temp_preview_file):
        try:
            os.remove(_temp_preview_file)
            log.info(f"Cleaned up temporary HTML file: {_temp_preview_file}")
        except OSError:
            pass


class HtmlToolsPlugin(QObject):
    # The constructor now correctly accepts the puffin_api object.
    def __init__(self, puffin_api: PuffinPluginAPI):
        super().__init__()
        # This deferred import is a good pattern to prevent circular dependencies.
        from ui.editor_widget import EditorWidget
        self.EditorWidgetClass = EditorWidget

        # We now correctly store the passed-in API object.
        self.api = puffin_api
        self.main_window = self.api.get_main_window()

        self._setup_highlighter()
        self._setup_ui()
        self._connect_signals()

    def _setup_highlighter(self):
        """Register the HtmlSyntaxHighlighter for HTML files."""
        self.api.register_highlighter('.html', HtmlSyntaxHighlighter)
        self.api.register_highlighter('.htm', HtmlSyntaxHighlighter)
        log.info("HTML Tools: Registered highlighter for .html and .htm files.")

    def _setup_ui(self):
        self.run_html_action = self.api.add_menu_action(
            menu_name="run",
            text="View in Browser",
            callback=self._preview_in_browser,
            shortcut="F8",
            icon_name="mdi.web"
        )
        self.run_html_action.setEnabled(False)

    def _connect_signals(self):
        self.main_window.tab_widget.currentChanged.connect(self._on_tab_changed)
        self._on_tab_changed(self.main_window.tab_widget.currentIndex())
        QApplication.instance().aboutToQuit.connect(cleanup_temp_file)

    def _on_tab_changed(self, index):
        is_html_file = False
        if index != -1:
            widget = self.main_window.tab_widget.widget(index)
            if isinstance(widget, self.EditorWidgetClass):
                filepath = self.main_window.editor_tabs_data.get(widget, {}).get('filepath', '')
                if filepath and filepath.lower().endswith(('.html', '.htm')):
                    is_html_file = True

        self.run_html_action.setEnabled(is_html_file)

    def _preview_in_browser(self):
        """Writes the current content to a temp file and opens it in the browser."""
        global _temp_preview_file
        editor = self.main_window.tab_widget.currentWidget()
        if not isinstance(editor, self.EditorWidgetClass):
            return

        html_content = editor.get_text()

        try:
            if not _temp_preview_file or not os.path.exists(os.path.dirname(_temp_preview_file)):
                with tempfile.NamedTemporaryFile(mode='w', suffix=".html", delete=False, encoding='utf-8') as tf:
                    _temp_preview_file = tf.name

            with open(_temp_preview_file, 'w', encoding='utf-8') as tf:
                tf.write(html_content)

            log.info(f"Previewing HTML content in temporary file: {_temp_preview_file}")
            QDesktopServices.openUrl(QUrl.fromLocalFile(_temp_preview_file))

        except Exception as e:
            self.api.show_message("error", "Preview Failed", f"Could not create temporary file for preview:\n{e}")


# The initialize function now correctly takes puffin_api.
def initialize(puffin_api: PuffinPluginAPI):
    """Entry point for the HTML Tools plugin."""
    return HtmlToolsPlugin(puffin_api)
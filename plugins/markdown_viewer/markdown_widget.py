# /plugins/markdown_viewer/markdown_widget.py
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTextBrowser
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt
from markdown import markdown
from app_core.theme_manager import theme_manager
from app_core.settings_manager import settings_manager
from utils.logger import log

class MarkdownViewerWidget(QWidget):
    """
    A widget that displays rendered Markdown content.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.filepath = None

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)

        self.browser = QTextBrowser()
        self.browser.setOpenExternalLinks(True)
        self.layout.addWidget(self.browser)

        self.update_theme()

    def load_markdown_file(self, filepath: str):
        """Reads a .md file and renders its content."""
        self.filepath = filepath
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                md_text = f.read()
            # Convert Markdown to HTML
            html = markdown(md_text, extensions=['fenced_code', 'tables'])
            self.browser.setHtml(html)
        except FileNotFoundError:
            self.browser.setHtml(f"<h1>Error</h1><p>File not found: {filepath}</p>")
        except Exception as e:
            log.error(f"Error reading or rendering Markdown file {filepath}: {e}")
            self.browser.setHtml(f"<h1>Error</h1><p>Could not render file: {e}</p>")

    def set_markdown_content(self, md_text: str):
        """Sets the content from a string directly."""
        html = markdown(md_text, extensions=['fenced_code', 'tables'])
        self.browser.setHtml(html)

    def update_theme(self):
        """Applies colors and fonts from the current theme."""
        colors = theme_manager.current_theme_data.get('colors', {})
        font_family = settings_manager.get("font_family", "Consolas")
        font_size = settings_manager.get("font_size", 11)

        # Base styles
        bg_color = colors.get('editor.background', '#2b2b2b')
        fg_color = colors.get('editor.foreground', '#a9b7c6')
        accent_color = colors.get('accent', '#88c0d0')
        line_highlight_bg = colors.get('editor.lineHighlightBackground', '#323232')
        comment_color = colors.get('syntax.comment', '#808080')
        string_color = colors.get('syntax.string', '#6A8759')

        style_sheet = f"""
        QTextBrowser {{
            background-color: {bg_color};
            color: {fg_color};
            border: none;
            padding: 10px;
        }}
        h1, h2, h3, h4, h5, h6 {{
            color: {accent_color};
            border-bottom: 1px solid {line_highlight_bg};
            padding-bottom: 4px;
            margin-top: 15px;
        }}
        a {{
            color: {string_color};
            text-decoration: none;
        }}
        a:hover {{
            text-decoration: underline;
        }}
        p, li {{
            font-size: {font_size}pt;
        }}
        pre {{
            background-color: {line_highlight_bg};
            border: 1px solid {colors.get('input.border', '#555')};
            border-radius: 4px;
            padding: 10px;
            font-family: "{font_family}";
        }}
        code {{
            background-color: {line_highlight_bg};
            font-family: "{font_family}";
            border-radius: 2px;
            padding: 2px 4px;
        }}
        blockquote {{
            color: {comment_color};
            border-left: 3px solid {accent_color};
            padding-left: 10px;
            margin-left: 5px;
        }}
        """
        self.browser.document().setDefaultStyleSheet(style_sheet)
        self.browser.document().setDefaultFont(QFont(font_family, font_size))
        # We have to reload the content for the stylesheet to apply
        self.browser.reload()
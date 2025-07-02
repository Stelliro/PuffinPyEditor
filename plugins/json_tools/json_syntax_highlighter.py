# PuffinPyEditor/plugins/json_tools/json_syntax_highlighter.py
from PyQt6.QtGui import QSyntaxHighlighter, QTextCharFormat, QColor, QFont
from PyQt6.QtCore import QRegularExpression
from app_core.theme_manager import theme_manager
from utils.logger import log


class JsonSyntaxHighlighter(QSyntaxHighlighter):
    """A syntax highlighter for JSON files."""

    def __init__(self, parent_document):
        super().__init__(parent_document)
        self.highlighting_rules = []
        self.initialize_formats_and_rules()
        log.info("JsonSyntaxHighlighter initialized.")

    def initialize_formats_and_rules(self):
        """Initializes formats and rules based on the current theme."""
        colors = theme_manager.current_theme_data.get("colors", {})

        def get_color(key: str, fallback: str) -> QColor:
            return QColor(colors.get(f"syntax.{key}", fallback))

        # Format for keys (strings before a colon)
        key_format = QTextCharFormat()
        key_format.setForeground(get_color("className", "#dbbc7f"))

        # Format for string values
        string_format = QTextCharFormat()
        string_format.setForeground(get_color("string", "#a7c080"))

        # Format for numbers
        number_format = QTextCharFormat()
        number_format.setForeground(get_color("number", "#d699b6"))

        # Format for keywords (true, false, null)
        keyword_format = QTextCharFormat()
        keyword_format.setForeground(get_color("keyword", "#e67e80"))
        keyword_format.setFontWeight(QFont.Weight.Bold)

        # Format for operators/braces
        brace_format = QTextCharFormat()
        brace_format.setForeground(get_color("brace", "#d3c6aa"))

        # MODIFIED: Reordered rules for correct application.
        # The last rule applied to a character wins, so we apply the general
        # string format first, then overwrite keys with the more specific key format.
        self.highlighting_rules = [
            # Braces and brackets
            (QRegularExpression(r'[\{\}\[\]]'), brace_format),
            # Keywords: true, false, null
            (QRegularExpression(r'\b(true|false|null)\b'), keyword_format),
            # Numbers
            (QRegularExpression(r'\b-?(?:0|[1-9]\d*)(?:\.\d+)?(?:[eE][+-]?\d+)?\b'), number_format),
            # All strings get the generic string format first.
            (QRegularExpression(r'"[^"\\]*(\\.[^"\\]*)*"'), string_format),
            # Then, re-apply the more specific 'key' format over the top for keys.
            (QRegularExpression(r'"[^"\\]*(\\.[^"\\]*)*"(?=\s*:)'), key_format),
        ]

    def highlightBlock(self, text: str):
        """Highlights a single block of text."""
        for pattern, fmt in self.highlighting_rules:
            iterator = pattern.globalMatch(text)
            while iterator.hasNext():
                match = iterator.next()
                self.setFormat(match.capturedStart(), match.capturedLength(), fmt)

    def rehighlight_document(self):
        """Forces a re-highlight of the entire document on theme change."""
        self.initialize_formats_and_rules()
        super().rehighlight()
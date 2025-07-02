# PuffinPyEditor/plugins/html_tools/html_syntax_highlighter.py
from PyQt6.QtGui import QSyntaxHighlighter, QTextCharFormat, QColor, QFont
from PyQt6.QtCore import QRegularExpression
from app_core.theme_manager import theme_manager
from utils.logger import log


class HtmlSyntaxHighlighter(QSyntaxHighlighter):
    """A syntax highlighter for HTML code."""

    def __init__(self, parent_document):
        super().__init__(parent_document)
        self.rules = []
        self.multiline_comment_format = QTextCharFormat()
        self.initialize_formats_and_rules()
        log.info("HtmlSyntaxHighlighter initialized.")

    def initialize_formats_and_rules(self):
        formats = {}
        colors = theme_manager.current_theme_data.get("colors", {})

        def get_color(key, fallback):
            return QColor(colors.get(f"syntax.{key}", fallback))

        # Format for tags like <p>, <div>
        tag_format = QTextCharFormat()
        tag_format.setForeground(get_color("keyword", "#e67e80"))

        # Format for attributes like href, class
        attribute_format = QTextCharFormat()
        attribute_format.setForeground(get_color("className", "#dbbc7f"))
        attribute_format.setFontItalic(True)

        # Format for attribute values like "styles.css"
        value_format = QTextCharFormat()
        value_format.setForeground(get_color("string", "#a7c080"))

        # Format for HTML comments <!-- ... -->
        comment_format = QTextCharFormat()
        comment_format.setForeground(get_color("comment", "#5f6c6d"))
        comment_format.setFontItalic(True)
        self.multiline_comment_format = comment_format

        # Format for DOCTYPE
        doctype_format = QTextCharFormat()
        doctype_format.setForeground(get_color("decorator", "#dbbc7f"))

        self.rules = [
            # Tags: <tag>, </tag>, <tag/>
            (QRegularExpression(r"</?([a-zA-Z0-9_-]+)"), tag_format),
            # Attributes: href=, class=
            (QRegularExpression(r'\b([a-zA-Z_-]+)(?=\s*=)'), attribute_format),
            # Attribute values in quotes
            (QRegularExpression(r'"[^"]*"'), value_format),
            (QRegularExpression(r"'[^']*'"), value_format),
            # DOCTYPE
            (QRegularExpression(r'<!DOCTYPE[^>]*>'), doctype_format),
        ]

        self.comment_start_expression = QRegularExpression(r"<!--")
        self.comment_end_expression = QRegularExpression(r"-->")

    def highlightBlock(self, text: str):
        # Apply single-line rules first
        for pattern, fmt in self.rules:
            iterator = pattern.globalMatch(text)
            while iterator.hasNext():
                match = iterator.next()
                self.setFormat(match.capturedStart(), match.capturedLength(), fmt)

        # Handle multiline comments
        self.setCurrentBlockState(0)
        start_index = 0
        if self.previousBlockState() != 1:
            match = self.comment_start_expression.match(text)
            start_index = match.capturedStart() if match.hasMatch() else -1

        while start_index >= 0:
            end_match = self.comment_end_expression.match(text, start_index)
            end_index = end_match.capturedStart() if end_match.hasMatch() else -1

            if end_index == -1:
                self.setCurrentBlockState(1)
                comment_len = len(text) - start_index
            else:
                comment_len = end_index - start_index + end_match.capturedLength()

            self.setFormat(start_index, comment_len, self.multiline_comment_format)

            next_match = self.comment_start_expression.match(text, start_index + comment_len)
            start_index = next_match.capturedStart() if next_match.hasMatch() else -1

    def rehighlight_document(self):
        self.initialize_formats_and_rules()
        super().rehighlight()
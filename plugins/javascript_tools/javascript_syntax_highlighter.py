# PuffinPyEditor/plugins/javascript_tools/javascript_syntax_highlighter.py
from typing import Dict, List, Tuple
from PyQt6.QtGui import QSyntaxHighlighter, QTextCharFormat, QColor, QFont
from PyQt6.QtCore import QRegularExpression
from app_core.theme_manager import theme_manager
from utils.logger import log


class JavaScriptSyntaxHighlighter(QSyntaxHighlighter):
    """A syntax highlighter for JavaScript code."""

    def __init__(self, parent_document):
        super().__init__(parent_document)
        self.highlighting_rules: List[Tuple[QRegularExpression, QTextCharFormat]] = []
        self.multiline_comment_format = QTextCharFormat()

        self.initialize_formats_and_rules()
        log.info("JavaScriptSyntaxHighlighter initialized.")

    def initialize_formats_and_rules(self):
        """Initializes all text formats based on the current theme and sets up regex rules."""
        formats: Dict[str, QTextCharFormat] = {}
        colors = theme_manager.current_theme_data.get("colors", {})

        def get_color(key: str, fallback: str) -> QColor:
            # Re-use existing python syntax colors for simplicity
            return QColor(colors.get(f"syntax.{key}", fallback))

        formats["keyword"] = QTextCharFormat()
        formats["keyword"].setForeground(get_color("keyword", "#e67e80"))
        formats["keyword"].setFontWeight(QFont.Weight.Bold)

        formats["operator"] = QTextCharFormat()
        formats["operator"].setForeground(get_color("operator", "#d3c6aa"))

        formats["brace"] = QTextCharFormat()
        formats["brace"].setForeground(get_color("brace", "d3c6aa"))

        formats["className"] = QTextCharFormat()
        formats["className"].setForeground(get_color("className", "#dbbc7f"))
        formats["className"].setFontWeight(QFont.Weight.Bold)

        formats["functionName"] = QTextCharFormat()
        formats["functionName"].setForeground(get_color("functionName", "#83c092"))

        formats["comment"] = QTextCharFormat()
        formats["comment"].setForeground(get_color("comment", "#5f6c6d"))
        formats["comment"].setFontItalic(True)
        self.multiline_comment_format = formats["comment"]

        formats["string"] = QTextCharFormat()
        formats["string"].setForeground(get_color("string", "#a7c080"))

        formats["number"] = QTextCharFormat()
        formats["number"].setForeground(get_color("number", "#d699b6"))

        # Build Rule List
        self.highlighting_rules = []

        keywords = [
            r'\bfunction\b', r'\bclass\b', r'\blet\b', r'\bconst\b', r'\bvar\b',
            r'\bif\b', r'\belse\b', r'\bfor\b', r'\bwhile\b', r'\breturn\b',
            r'\bswitch\b', r'\bcase\b', r'\bdefault\b', r'\bnew\b', r'\bthis\b',
            r'\btry\b', r'\bcatch\b', r'\bfinally\b', r'\bthrow\b', r'\btypeof\b',
            r'\bimport\b', r'\bexport\b', r'\bfrom\b', r'\basync\b', r'\bawait\b',
            r'\btrue\b', r'\bfalse\b', r'\bnull\b', r'\bundefined\b'
        ]
        self.highlighting_rules += [(QRegularExpression(p), formats["keyword"]) for p in keywords]

        self.highlighting_rules.extend([
            (QRegularExpression(r'\b[A-Z][A-Za-z0-9_]*'), formats["className"]),
            (QRegularExpression(r'[a-z_][A-Za-z0-9_]*(?=\s*=\s*function|\s*=\s*\(|\s*\()'), formats["functionName"]),
            (QRegularExpression(r'[=><!~?&|+\-*/^%]+'), formats["operator"]),
            (QRegularExpression(r'\{|\}|\(|\)|\[|\]'), formats["brace"]),
            (QRegularExpression(r'\b[0-9]+(\.[0-9]+)?\b'), formats["number"]),
            (QRegularExpression(r'"[^"\\]*(\\.[^"\\]*)*"'), formats["string"]),
            (QRegularExpression(r"'[^'\\]*(\\.[^'\\]*)*'"), formats["string"]),
            (QRegularExpression(r"`[^`\\]*(\\.[^`\\]*)*`"), formats["string"]),  # Template literals
            (QRegularExpression(r'//.*'), formats["comment"]),
        ])

        # For multiline comments /* ... */
        self.comment_start_expression = QRegularExpression(r"/\*")
        self.comment_end_expression = QRegularExpression(r"\*/")

    def highlightBlock(self, text: str):
        """Highlights a single block of text, handling multiline comments."""
        # Apply single-line rules
        for pattern, fmt in self.highlighting_rules:
            iterator = pattern.globalMatch(text)
            while iterator.hasNext():
                match = iterator.next()
                self.setFormat(match.capturedStart(), match.capturedLength(), fmt)

        # Handle multiline comments
        self.setCurrentBlockState(0)
        start_index = 0
        if self.previousBlockState() != 1:
            start_index = self.comment_start_expression.match(text).capturedStart()

        while start_index >= 0:
            end_index = self.comment_end_expression.match(text, start_index).capturedStart()
            if end_index == -1:
                self.setCurrentBlockState(1)
                comment_len = len(text) - start_index
            else:
                comment_len = end_index - start_index + 2
            
            self.setFormat(start_index, comment_len, self.multiline_comment_format)
            start_index = self.comment_start_expression.match(text, start_index + comment_len).capturedStart()

    def rehighlight_document(self):
        """Forces a re-highlight of the entire document, usually on theme change."""
        self.initialize_formats_and_rules()
        super().rehighlight()
# PuffinPyEditor/plugins/basic_highlighters/javascript_syntax_highlighter.py
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
        self.formats: Dict[str, QTextCharFormat] = {}
        colors = theme_manager.current_theme_data.get("colors", {})

        def get_color(key: str, fallback: str) -> QColor:
            # Re-use existing python syntax colors for simplicity
            return QColor(colors.get(f"syntax.{key}", fallback))

        self.formats["keyword"] = QTextCharFormat()
        self.formats["keyword"].setForeground(get_color("keyword", "#e67e80"))
        self.formats["keyword"].setFontWeight(QFont.Weight.Bold)

        self.formats["operator"] = QTextCharFormat()
        self.formats["operator"].setForeground(get_color("operator", "#d3c6aa"))

        self.formats["brace"] = QTextCharFormat()
        self.formats["brace"].setForeground(get_color("brace", "d3c6aa"))

        self.formats["className"] = QTextCharFormat()
        self.formats["className"].setForeground(get_color("className", "#dbbc7f"))
        self.formats["className"].setFontWeight(QFont.Weight.Bold)

        self.formats["functionName"] = QTextCharFormat()
        self.formats["functionName"].setForeground(get_color("functionName", "#83c092"))

        self.formats["comment"] = QTextCharFormat()
        self.formats["comment"].setForeground(get_color("comment", "#5f6c6d"))
        self.formats["comment"].setFontItalic(True)
        self.multiline_comment_format = self.formats["comment"]

        self.formats["string"] = QTextCharFormat()
        self.formats["string"].setForeground(get_color("string", "#a7c080"))

        self.formats["number"] = QTextCharFormat()
        self.formats["number"].setForeground(get_color("number", "#d699b6"))

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
        self.highlighting_rules += [(QRegularExpression(p), self.formats["keyword"]) for p in keywords]

        self.highlighting_rules.extend([
            (QRegularExpression(r'\b[A-Z][A-Za-z0-9_]*'), self.formats["className"]),
            (QRegularExpression(r'[a-z_][A-Za-z0-9_]*(?=\s*=\s*function|\s*=\s*\(|\s*\()'), self.formats["functionName"]),
            (QRegularExpression(r'[=><!~?&|+\-*/^%]+'), self.formats["operator"]),
            (QRegularExpression(r'\{|\}|\(|\)|\[|\]'), self.formats["brace"]),
            (QRegularExpression(r'\b[0-9]+(\.[0-9]+)?\b'), self.formats["number"]),
            (QRegularExpression(r'"[^"\\]*(\\.[^"\\]*)*"'), self.formats["string"]),
            (QRegularExpression(r"'[^'\\]*(\\.[^'\\]*)*'"), self.formats["string"]),
            (QRegularExpression(r"`[^`\\]*(\\.[^`\\]*)*`"), self.formats["string"]),  # Template literals
            (QRegularExpression(r'//.*'), self.formats["comment"]),
        ])

        # For multiline comments /* ... */
        self.comment_start_expression = QRegularExpression(r"/\*")
        self.comment_end_expression = QRegularExpression(r"\*/")

    def highlightBlock(self, text: str):
        # Apply single-line rules first
        for pattern, fmt in self.highlighting_rules:
            iterator = pattern.globalMatch(text)
            while iterator.hasNext():
                match = iterator.next()
                self.setFormat(match.capturedStart(), match.capturedLength(), fmt)

        self.setCurrentBlockState(0)

        in_multiline_comment = self.previousBlockState() == 1
        start_index = 0

        if in_multiline_comment:
            end_match = self.comment_end_expression.match(text, 0)
            if end_match.hasMatch():
                length = end_match.capturedEnd()
                self.setFormat(0, length, self.multiline_comment_format)
                start_index = length
            else:
                self.setCurrentBlockState(1)
                self.setFormat(0, len(text), self.multiline_comment_format)
                return

        search_index = start_index
        while search_index >= 0 and search_index < len(text):
            start_match = self.comment_start_expression.match(text, search_index)
            if not start_match.hasMatch():
                break

            start_pos = start_match.capturedStart()
            end_match = self.comment_end_expression.match(text, start_pos + start_match.capturedLength())
            if end_match.hasMatch():
                length = end_match.capturedEnd() - start_pos
                self.setFormat(start_pos, length, self.multiline_comment_format)
                search_index = end_match.capturedEnd()
            else:
                self.setCurrentBlockState(1)
                self.setFormat(start_pos, len(text) - start_pos, self.multiline_comment_format)
                return

    def rehighlight_document(self):
        """Forces a re-highlight of the entire document, usually on theme change."""
        self.initialize_formats_and_rules()
        super().rehighlight()
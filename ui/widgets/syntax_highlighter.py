# PuffinPyEditor/ui/widgets/syntax_highlighter.py
from typing import Dict, List, Tuple
from PyQt6.QtGui import QSyntaxHighlighter, QTextCharFormat, QColor, QFont
from PyQt6.QtCore import QRegularExpression
from app_core.theme_manager import theme_manager
from utils.logger import log


class PythonSyntaxHighlighter(QSyntaxHighlighter):
    """
    A syntax highlighter for Python code that dynamically styles based on the
    current theme from the ThemeManager.
    """
    def __init__(self, parent_document):
        super().__init__(parent_document)
        self.highlighting_rules: List[Tuple[QRegularExpression, QTextCharFormat]] = []
        self.multiline_string_format = QTextCharFormat()

        self.initialize_formats_and_rules()
        log.info("PythonSyntaxHighlighter initialized.")

    def initialize_formats_and_rules(self):
        """
        Initializes all text formats based on the current theme and sets up
        the regular expression rules for highlighting.
        """
        formats: Dict[str, QTextCharFormat] = {}
        colors = theme_manager.current_theme_data.get("colors", {})

        def get_color(key: str, fallback: str) -> QColor:
            return QColor(colors.get(f"syntax.{key}", fallback))

        formats["keyword"] = QTextCharFormat()
        formats["keyword"].setForeground(get_color("keyword", "#e67e80"))
        formats["keyword"].setFontWeight(QFont.Weight.Bold)

        formats["self"] = QTextCharFormat()
        formats["self"].setForeground(get_color("self", "#e67e80"))
        formats["self"].setFontItalic(True)

        formats["operator"] = QTextCharFormat()
        formats["operator"].setForeground(get_color("operator", "#d3c6aa"))

        formats["brace"] = QTextCharFormat()
        formats["brace"].setForeground(get_color("brace", "#d3c6aa"))

        formats["decorator"] = QTextCharFormat()
        formats["decorator"].setForeground(get_color("decorator", "#dbbc7f"))
        formats["decorator"].setFontItalic(True)

        formats["className"] = QTextCharFormat()
        formats["className"].setForeground(get_color("className", "#dbbc7f"))
        formats["className"].setFontWeight(QFont.Weight.Bold)

        formats["functionName"] = QTextCharFormat()
        formats["functionName"].setForeground(
            get_color("functionName", "#83c092")
        )

        formats["comment"] = QTextCharFormat()
        formats["comment"].setForeground(get_color("comment", "#5f6c6d"))
        formats["comment"].setFontItalic(True)

        formats["string"] = QTextCharFormat()
        formats["string"].setForeground(get_color("string", "#a7c080"))

        formats["docstring"] = QTextCharFormat()
        formats["docstring"].setForeground(get_color("docstring", "#5f6c6d"))
        formats["docstring"].setFontItalic(True)
        self.multiline_string_format = formats["docstring"]

        formats["number"] = QTextCharFormat()
        formats["number"].setForeground(get_color("number", "#d699b6"))

        self.highlighting_rules = []

        keywords = [
            r'\bdef\b', r'\bclass\b', r'\bif\b', r'\belif\b', r'\belse\b',
            r'\bfor\b', r'\bwhile\b', r'\breturn\b', r'\byield\b', r'\bpass\b',
            r'\bcontinue\b', r'\bbreak\b', r'\bimport\b', r'\bfrom\b',
            r'\bas\b', r'\btry\b', r'\bexcept\b', r'\bfinally\b', r'\braise\b',
            r'\bwith\b', r'\bassert\b', r'\bdel\b', r'\bglobal\b',
            r'\bnonlocal\b', r'\bin\b', r'\bis\b', r'\blambda\b', r'\bnot\b',
            r'\bor\b', r'\band\b', r'\bTrue\b', r'\bFalse\b', r'\bNone\b',
            r'\basync\b', r'\bawait\b'
        ]
        self.highlighting_rules += [
            (QRegularExpression(p), formats["keyword"]) for p in keywords
        ]

        self.highlighting_rules.extend([
            (QRegularExpression(r'\bself\b'), formats["self"]),
            (QRegularExpression(r'@[A-Za-z0-9_]+'), formats["decorator"]),
            (QRegularExpression(r'\b[A-Z][A-Za-z0-9_]*'), formats["className"]),
            (QRegularExpression(r'\b[a-z_][A-Za-z0-9_]*(?=\()'),
             formats["functionName"]),
            (QRegularExpression(r'[+\-*/%=<>!&|^~]'), formats["operator"]),
            (QRegularExpression(r'[{}()\[\]]'), formats["brace"]),
            (QRegularExpression(r'\b[0-9]+\b'), formats["number"]),
            (QRegularExpression(r'"[^"\\]*(\\.[^"\\]*)*"'), formats["string"]),
            (QRegularExpression(r"'[^'\\]*(\\.[^'\\]*)*'"), formats["string"]),
            (QRegularExpression(r'#.*'), formats["comment"]),
        ])

        self.tri_single_quote_start = QRegularExpression(r"'''")
        self.tri_double_quote_start = QRegularExpression(r'"""')

    def highlightBlock(self, text: str):
        """Highlights a single block of text."""
        for pattern, fmt in self.highlighting_rules:
            iterator = pattern.globalMatch(text)
            while iterator.hasNext():
                match = iterator.next()
                self.setFormat(match.capturedStart(), match.capturedLength(), fmt)

        self.setCurrentBlockState(0)
        in_multiline = self.previousBlockState() == 1

        start_index = 0
        if in_multiline:
            start_index = self._apply_multiline_format(
                text, self.tri_double_quote_start, 1, 0
            )
            if start_index == -1:
                return

        self._apply_multiline_format(
            text, self.tri_double_quote_start, 1, start_index
        )
        self._apply_multiline_format(
            text, self.tri_single_quote_start, 1, start_index
        )

    def _apply_multiline_format(
        self, text, delimiter_re, state, start_index
    ):
        """Helper to apply formatting for multi-line strings."""
        match = delimiter_re.match(text, start_index)
        while match.hasMatch():
            end_match = delimiter_re.match(text, match.capturedEnd())
            if end_match.hasMatch():
                length = end_match.capturedEnd() - match.capturedStart()
                self.setFormat(
                    match.capturedStart(), length, self.multiline_string_format
                )
                match = delimiter_re.match(text, end_match.capturedEnd())
            else:
                self.setCurrentBlockState(state)
                length = len(text) - match.capturedStart()
                self.setFormat(
                    match.capturedStart(), length, self.multiline_string_format
                )
                return -1
        return match.capturedEnd()

    def rehighlight_document(self):
        """Forces a re-highlight of the entire document."""
        log.info("Re-highlighting entire document for syntax.")
        self.initialize_formats_and_rules()
        super().rehighlight()
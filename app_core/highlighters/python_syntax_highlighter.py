# PuffinPyEditor/app_core/highlighters/python_syntax_highlighter.py
from typing import Dict, List, Tuple, TYPE_CHECKING
from PyQt6.QtGui import QSyntaxHighlighter, QTextCharFormat, QColor, QFont
from PyQt6.QtCore import QRegularExpression
from utils.logger import log

if TYPE_CHECKING:
    from app_core.theme_manager import ThemeManager


class PythonSyntaxHighlighter(QSyntaxHighlighter):
    """
    A syntax highlighter for Python code that dynamically styles based on the
    current theme from the ThemeManager.
    """

    def __init__(self, parent_document, theme_manager: "ThemeManager"):
        super().__init__(parent_document)
        self.theme_manager = theme_manager
        self.highlighting_rules: List[Tuple[QRegularExpression, QTextCharFormat]] = []
        self.multiline_string_format = QTextCharFormat()

        self.initialize_formats_and_rules()
        log.info("PythonSyntaxHighlighter initialized from app_core.")

    def initialize_formats_and_rules(self):
        """
        Initializes all text formats based on the current theme and sets up
        the regular expression rules for highlighting.
        """
        formats: Dict[str, QTextCharFormat] = {}
        colors = self.theme_manager.current_theme_data.get("colors", {})

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
        # 1. Apply all single-line rules
        for pattern, fmt in self.highlighting_rules:
            iterator = pattern.globalMatch(text)
            while iterator.hasNext():
                match = iterator.next()
                self.setFormat(match.capturedStart(), match.capturedLength(), fmt)

        # 2. Handle multi-line strings with explicit state management
        # State 0: Normal, State 1: In """, State 2: In '''
        NORMAL_STATE = 0
        IN_TRIPLE_DOUBLE = 1
        IN_TRIPLE_SINGLE = 2

        self.setCurrentBlockState(NORMAL_STATE)

        start_index = 0
        previous_state = self.previousBlockState()

        if previous_state == IN_TRIPLE_DOUBLE:
            delimiter = self.tri_double_quote_start
            end_match = delimiter.match(text, 0)
            if end_match.hasMatch():
                length = end_match.capturedEnd()
                self.setFormat(0, length, self.multiline_string_format)
                start_index = length
            else:
                self.setCurrentBlockState(IN_TRIPLE_DOUBLE)
                self.setFormat(0, len(text), self.multiline_string_format)
                return

        elif previous_state == IN_TRIPLE_SINGLE:
            delimiter = self.tri_single_quote_start
            end_match = delimiter.match(text, 0)
            if end_match.hasMatch():
                length = end_match.capturedEnd()
                self.setFormat(0, length, self.multiline_string_format)
                start_index = length
            else:
                self.setCurrentBlockState(IN_TRIPLE_SINGLE)
                self.setFormat(0, len(text), self.multiline_string_format)
                return

        # 3. Find new multi-line strings in the rest of the block
        delimiters = [
            (self.tri_double_quote_start, IN_TRIPLE_DOUBLE),
            (self.tri_single_quote_start, IN_TRIPLE_SINGLE)
        ]

        while start_index < len(text):
            # Find the next occurring delimiter of any type with grace and simplicity.
            next_match, next_state_to_set, next_delimiter_re = None, None, None
            first_pos = float('inf')

            for delimiter_re, state_to_set in delimiters:
                match = delimiter_re.match(text, start_index)
                if match.hasMatch() and match.capturedStart() < first_pos:
                    first_pos = match.capturedStart()
                    next_match = match
                    next_state_to_set = state_to_set
                    next_delimiter_re = delimiter_re

            if not next_match:
                break  # No more delimiters found in the remaining text.

            start_pos = next_match.capturedStart()
            # Re-use the found delimiter regex to find its partner
            end_match = next_delimiter_re.match(text, start_pos + next_match.capturedLength())

            if end_match.hasMatch():
                # A complete story, with a beginning and an end.
                length = end_match.capturedEnd() - start_pos
                self.setFormat(start_pos, length, self.multiline_string_format)
                start_index = end_match.capturedEnd()
            else:
                # A story left unfinished...
                self.setCurrentBlockState(next_state_to_set)
                self.setFormat(start_pos, len(text) - start_pos, self.multiline_string_format)
                return

    def rehighlight(self):
        """Forces a re-highlight of the entire document."""
        log.info("Re-highlighting entire document for Python syntax.")
        self.initialize_formats_and_rules()
        super().rehighlight()
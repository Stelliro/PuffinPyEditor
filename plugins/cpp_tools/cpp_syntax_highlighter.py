# PuffinPyEditor/plugins/cpp_tools/cpp_syntax_highlighter.py
from typing import Dict, List, Tuple
from PyQt6.QtGui import QSyntaxHighlighter, QTextCharFormat, QColor, QFont
from PyQt6.QtCore import QRegularExpression
from app_core.theme_manager import theme_manager
from utils.logger import log


class CppSyntaxHighlighter(QSyntaxHighlighter):
    """A syntax highlighter for C and C++ code."""

    def __init__(self, parent_document):
        super().__init__(parent_document)
        self.highlighting_rules: List[Tuple[QRegularExpression, QTextCharFormat]] = []
        self.multiline_comment_format = QTextCharFormat()

        self.initialize_formats_and_rules()
        log.info("CppSyntaxHighlighter initialized.")

    def initialize_formats_and_rules(self):
        """Initializes all text formats and regular expression rules."""
        formats: Dict[str, QTextCharFormat] = {}
        colors = theme_manager.current_theme_data.get("colors", {})

        def get_color(key: str, fallback: str) -> QColor:
            # Re-use existing python syntax colors for simplicity and consistency
            return QColor(colors.get(f"syntax.{key}", fallback))

        formats["keyword"] = QTextCharFormat()
        formats["keyword"].setForeground(get_color("keyword", "#e67e80"))
        formats["keyword"].setFontWeight(QFont.Weight.Bold)

        formats["preprocessor"] = QTextCharFormat()
        formats["preprocessor"].setForeground(get_color("decorator", "#dbbc7f"))
        formats["preprocessor"].setFontWeight(QFont.Weight.Medium)

        formats["operator"] = QTextCharFormat()
        formats["operator"].setForeground(get_color("operator", "#d3c6aa"))

        formats["brace"] = QTextCharFormat()
        formats["brace"].setForeground(get_color("brace", "d3c6aa"))

        formats["className"] = QTextCharFormat()
        formats["className"].setForeground(get_color("className", "#dbbc7f"))

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
            r'\bchar\b', r'\bclass\b', r'\bconst\b', r'\bdouble\b', r'\benum\b',
            r'\bexplicit\b', r'\bfloat\b', r'\bfriend\b', r'\binline\b',
            r'\bint\b', r'\blong\b', r'\bnamespace\b', r'\boperator\b',
            r'\bprivate\b', r'\bprotected\b', r'\bpublic\b', r'\bshort\b',
            r'\bsigned\b', r'\bstatic\b', r'\bstruct\b', r'\btemplate\b',
            r'\btypedef\b', r'\btypename\b', r'\bunion\b', r'\bunsigned\b',
            r'\bvirtual\b', r'\bvoid\b', r'\bvolatile\b', r'\bwchar_t\b',
            # Control flow
            r'\bif\b', r'\belse\b', r'\bfor\b', r'\bwhile\b', r'\bdo\b',
            r'\bbreak\b', r'\bcontinue\b', r'\breturn\b', r'\bgoto\b',
            r'\bswitch\b', r'\bcase\b', r'\bdefault\b',
            # C++ specific
            r'\bnew\b', r'\bdelete\b', r'\bthis\b', r'\bthrow\b', r'\btry\b',
            r'\bcatch\b', r'\bexplicit\b', r'\bexport\b', r'\btrue\b',
            r'\bfalse\b', r'\bnullptr\b', r'\busing\b',
            # Newer keywords
            r'\bnoexcept\b', r'\bstatic_assert\b', r'\bdecltype\b', r'\bauto\b'
        ]
        self.highlighting_rules += [(QRegularExpression(p), formats["keyword"]) for p in keywords]

        self.highlighting_rules.extend([
            (QRegularExpression(r'^\s*#.*'), formats["preprocessor"]),
            (QRegularExpression(r'\b[A-Z][A-Za-z0-9_]*'), formats["className"]),
            (QRegularExpression(r'\b[a-zA-Z_][a-zA-Z0-9_]*(?=\s*\()'), formats["functionName"]),
            (QRegularExpression(r'[=><!~?&|+\-*/^%:]+'), formats["operator"]),
            (QRegularExpression(r'\{|\}|\(|\)|\[|\]'), formats["brace"]),
            (QRegularExpression(r'\b[0-9]+[fLu]?\b'), formats["number"]),
            (QRegularExpression(r'"[^"\\]*(\\.[^"\\]*)*"'), formats["string"]),
            (QRegularExpression(r"'\\?.'"), formats["string"]),  # Char literal
            (QRegularExpression(r'//.*'), formats["comment"]),
        ])

        self.comment_start_expression = QRegularExpression(r"/\*")
        self.comment_end_expression = QRegularExpression(r"\*/")

    def highlightBlock(self, text: str):
        """Highlights a single block of text, handling multiline comments."""
        for pattern, fmt in self.highlighting_rules:
            iterator = pattern.globalMatch(text)
            while iterator.hasNext():
                match = iterator.next()
                self.setFormat(match.capturedStart(), match.capturedLength(), fmt)

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
        """Forces a re-highlight of the entire document, usually on theme change."""
        self.initialize_formats_and_rules()
        super().rehighlight()
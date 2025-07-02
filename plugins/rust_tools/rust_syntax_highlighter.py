# PuffinPyEditor/plugins/rust_tools/rust_syntax_highlighter.py
from typing import Dict, List, Tuple
from PyQt6.QtGui import QSyntaxHighlighter, QTextCharFormat, QColor, QFont
from PyQt6.QtCore import QRegularExpression
from app_core.theme_manager import theme_manager
from utils.logger import log


class RustSyntaxHighlighter(QSyntaxHighlighter):
    """A syntax highlighter for Rust code."""

    def __init__(self, parent_document):
        super().__init__(parent_document)
        self.highlighting_rules: List[Tuple[QRegularExpression, QTextCharFormat]] = []
        self.multiline_comment_format = QTextCharFormat()
        self.initialize_formats_and_rules()
        log.info("RustSyntaxHighlighter initialized.")

    def initialize_formats_and_rules(self):
        """Initializes all text formats and regular expression rules based on the theme."""
        formats: Dict[str, QTextCharFormat] = {}
        colors = theme_manager.current_theme_data.get("colors", {})

        def get_color(key: str, fallback: str) -> QColor:
            return QColor(colors.get(f"syntax.{key}", fallback))

        # Basic formats from Python highlighter for consistency
        formats["keyword"] = QTextCharFormat()
        formats["keyword"].setForeground(get_color("keyword", "#e67e80"))
        formats["keyword"].setFontWeight(QFont.Weight.Bold)

        formats["special"] = QTextCharFormat()
        formats["special"].setForeground(get_color("self", "#e67e80"))
        formats["special"].setFontItalic(True)

        formats["attribute"] = QTextCharFormat()
        formats["attribute"].setForeground(get_color("decorator", "#dbbc7f"))

        formats["macro"] = QTextCharFormat()
        formats["macro"].setForeground(get_color("decorator", "#dbbc7f"))

        formats["type"] = QTextCharFormat()
        formats["type"].setForeground(get_color("className", "#dbbc7f"))

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

        # Build Rule List for Rust
        self.highlighting_rules = []

        keywords = [
            r'\b(as|break|const|continue|crate|else|enum|extern|false|fn|for|if|impl|in|let|loop|match|mod|move|mut|pub|ref|return|static|struct|super|trait|true|type|unsafe|use|where|while|async|await|dyn)\b'
        ]
        self.highlighting_rules += [(QRegularExpression(p), formats["keyword"]) for p in keywords]

        # Special keywords like self
        special_keywords = [r'\b(self|Self)\b']
        self.highlighting_rules += [(QRegularExpression(p), formats["special"]) for p in special_keywords]

        self.highlighting_rules.extend([
            # Attributes: #[...]
            (QRegularExpression(r"#\!\[[^\]]+\]|#\[[^\]]+\]"), formats["attribute"]),
            # Macros: println!(), vec![]
            (QRegularExpression(r"\b([a-zA-Z0-9_]+)!\b"), formats["macro"]),
            # Types (PascalCase)
            (QRegularExpression(r'\b[A-Z][a-zA-Z0-9_]*\b'), formats["type"]),
            # Function definitions
            (QRegularExpression(r'\b(fn)\s+([a-zA-Z_][a-zA-Z0-9_]*)'), self._format_function_definition),
            # Lifetimes: 'a
            (QRegularExpression(r"'\w+"), formats["special"]),
            # Strings
            (QRegularExpression(r'"[^"\\]*(\\.[^"\\]*)*"'), formats["string"]),
            # Numbers
            (QRegularExpression(r'\b[0-9]+(_[0-9]+)*\.?[0-9]*\b'), formats["number"]),
            # Comments
            (QRegularExpression(r'//.*'), formats["comment"]),
        ])

        self.comment_start_expression = QRegularExpression(r"/\*")
        self.comment_end_expression = QRegularExpression(r"\*/")

    def _format_function_definition(self, match):
        """Custom formatter to style `fn` as keyword and name as functionName."""
        # 'fn' keyword
        self.setFormat(match.capturedStart(1), match.capturedLength(1), self.highlighting_rules[0][1])
        # function name
        self.setFormat(match.capturedStart(2), match.capturedLength(2), next(
            fmt for _, fmt in self.highlighting_rules if fmt.fontItalic() == False and fmt.foreground() == QColor(
                theme_manager.current_theme_data.get('colors').get('syntax.functionName'))))

    def highlightBlock(self, text: str):
        # Apply custom formatters first
        self._format_function_definition(self.highlighting_rules[2][0].match(text))

        for pattern, fmt in self.highlighting_rules:
            if callable(fmt): continue

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
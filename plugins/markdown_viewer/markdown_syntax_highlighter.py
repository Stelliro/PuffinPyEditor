# /plugins/markdown_viewer/markdown_syntax_highlighter.py
from PyQt6.QtGui import QSyntaxHighlighter, QTextCharFormat, QColor, QFont
from PyQt6.QtCore import QRegularExpression
from app_core.theme_manager import theme_manager

class MarkdownSyntaxHighlighter(QSyntaxHighlighter):
    """
    A syntax highlighter that provides a rich, WYSIWYG-like experience
    for editing Markdown source by visually styling the syntax.
    """
    def __init__(self, parent_document):
        super().__init__(parent_document)
        self.formats = {}
        self.initialize_formats_and_rules()

    def initialize_formats_and_rules(self):
        colors = theme_manager.current_theme_data.get("colors", {})
        editor_bg = QColor(colors.get('editor.background', '#2b2b2b'))

        self.formats['marker'] = QTextCharFormat()
        self.formats['marker'].setForeground(editor_bg.lighter(130))
        self.formats['marker'].setFontWeight(QFont.Weight.Bold)

        self.formats['h1'] = QTextCharFormat()
        self.formats['h1'].setFontPointSize(20)
        self.formats['h1'].setFontWeight(QFont.Weight.Bold)
        self.formats['h1'].setForeground(QColor(colors.get('accent', '#88c0d0')))

        self.formats['h2'] = QTextCharFormat()
        self.formats['h2'].setFontPointSize(18)
        self.formats['h2'].setFontWeight(QFont.Weight.Bold)

        self.formats['h3'] = QTextCharFormat()
        self.formats['h3'].setFontPointSize(16)
        self.formats['h3'].setFontWeight(QFont.Weight.Bold)

        self.formats['bold'] = QTextCharFormat()
        self.formats['bold'].setFontWeight(QFont.Weight.Bold)

        self.formats['italic'] = QTextCharFormat()
        self.formats['italic'].setFontItalic(True)

        self.formats['strikethrough'] = QTextCharFormat()
        self.formats['strikethrough'].setFontStrikeOut(True)

        self.formats['code_block'] = QTextCharFormat()
        self.formats['code_block'].setBackground(QColor(colors.get('editor.lineHighlightBackground', '#323232')))
        self.formats['code_block'].setFontFamily("Consolas")

        self.formats['inline_code'] = QTextCharFormat()
        self.formats['inline_code'].setBackground(QColor(colors.get('editor.lineHighlightBackground', '#323232')))
        self.formats['inline_code'].setForeground(QColor(colors.get('syntax.string', '#a7c080')))
        self.formats['inline_code'].setFontFamily("Consolas")

        self.rules = [
            (QRegularExpression(r"^(#{1,3})\s"), self._format_heading),
            (QRegularExpression(r"(\*\*)([^\*]+)(\*\*)"), self._format_inline('bold')),
            (QRegularExpression(r"(\*)([^\*]+)(\*)"), self._format_inline('italic')),
            (QRegularExpression(r"(`)([^`]+)(`)"), self._format_inline('inline_code')),
            (QRegularExpression(r"(~~)([^~]+)(~~)"), self._format_inline('strikethrough')),
        ]
        self.code_block_delimiter = QRegularExpression(r"^```")

    def _format_heading(self, match):
        marker = match.captured(1)
        level = len(marker)
        self.setFormat(match.capturedStart(1), len(marker), self.formats['marker'])
        self.setFormat(match.capturedEnd(1), self.currentBlock().length(), self.formats[f'h{level}'])

    def _format_inline(self, fmt_name):
        def formatter(match):
            self.setFormat(match.capturedStart(1), len(match.captured(1)), self.formats['marker'])
            self.setFormat(match.capturedStart(3), len(match.captured(3)), self.formats['marker'])
            self.setFormat(match.capturedStart(2), len(match.captured(2)), self.formats[fmt_name])
        return formatter

    def highlightBlock(self, text: str):
        if self.code_block_delimiter.match(text).hasMatch() or self.previousBlockState() == 1:
            self.setFormat(0, len(text), self.formats['code_block'])
            in_code_block = True

            if self.code_block_delimiter.match(text).hasMatch() and self.previousBlockState() == 1:
                in_code_block = False

            self.setCurrentBlockState(1 if in_code_block else 0)
            return

        for pattern, formatter in self.rules:
            iterator = pattern.globalMatch(text)
            while iterator.hasNext():
                formatter(iterator.next())

    def rehighlight_document(self):
        self.initialize_formats_and_rules()
        super().rehighlight()
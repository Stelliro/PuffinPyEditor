# /plugins/markdown_viewer/markdown_syntax_highlighter.py
from PyQt6.QtGui import QSyntaxHighlighter, QTextCharFormat, QColor, QFont
from PyQt6.QtCore import QRegularExpression, Qt
from app_core.theme_manager import theme_manager


class MarkdownSyntaxHighlighter(QSyntaxHighlighter):
    """
    A syntax highlighter that provides a rich, WYSIWYG-like experience
    for editing Markdown source by visually styling the syntax.
    Includes auto-correction for low-contrast text on colored backgrounds.
    """

    def __init__(self, parent_document):
        super().__init__(parent_document)
        self.formats = {}
        self.rules = []
        self.default_fg = QColor(
            theme_manager.current_theme_data.get("colors", {}).get(
                "editor.foreground", "#ffffff"
            )
        )
        self.initialize_formats_and_rules()

    def _get_high_contrast_color(self, fg_color: QColor, bg_color: QColor) -> QColor:
        """
        Checks if a foreground color has enough contrast against a background.
        If not, it returns black or white, whichever is more readable.
        """
        CONTRAST_THRESHOLD = 80
        fg_lightness = fg_color.lightness()
        bg_lightness = bg_color.lightness()

        if abs(fg_lightness - bg_lightness) < CONTRAST_THRESHOLD:
            return QColor(Qt.GlobalColor.white) if bg_lightness < 128 else QColor(Qt.GlobalColor.black)

        return fg_color

    def initialize_formats_and_rules(self):
        """Initializes text formats and regular expression rules for highlighting."""
        colors = theme_manager.current_theme_data.get("colors", {})
        editor_bg = QColor(colors.get('editor.background', '#2b2b2b'))
        accent = QColor(colors.get('accent', '#88c0d0'))
        comment_color = QColor(colors.get('syntax.comment', '#808080'))

        self.formats['marker'] = QTextCharFormat()
        self.formats['marker'].setForeground(editor_bg.lighter(150))
        self.formats['marker'].setFontWeight(QFont.Weight.Bold)

        self.formats['blockquote'] = QTextCharFormat()
        self.formats['blockquote'].setForeground(comment_color)
        self.formats['blockquote'].setFontItalic(True)

        self.formats['hr'] = QTextCharFormat()
        self.formats['hr'].setForeground(editor_bg.lighter(130))
        self.formats['hr'].setFontWeight(QFont.Weight.Bold)

        base_heading_format = QTextCharFormat()
        base_heading_format.setFontWeight(QFont.Weight.Bold)
        base_heading_format.setForeground(accent)
        self.formats['h1'] = QTextCharFormat(base_heading_format);
        self.formats['h1'].setFontPointSize(22)
        self.formats['h2'] = QTextCharFormat(base_heading_format);
        self.formats['h2'].setFontPointSize(20)
        self.formats['h3'] = QTextCharFormat(base_heading_format);
        self.formats['h3'].setFontPointSize(18)
        self.formats['h4'] = QTextCharFormat(base_heading_format);
        self.formats['h4'].setFontPointSize(16)
        self.formats['h5'] = QTextCharFormat(base_heading_format);
        self.formats['h5'].setFontPointSize(14)
        self.formats['h6'] = QTextCharFormat(base_heading_format);
        self.formats['h6'].setFontPointSize(12)

        self.formats['bold'] = QTextCharFormat();
        self.formats['bold'].setFontWeight(QFont.Weight.Bold)
        self.formats['italic'] = QTextCharFormat();
        self.formats['italic'].setFontItalic(True)
        self.formats['strikethrough'] = QTextCharFormat();
        self.formats['strikethrough'].setFontStrikeOut(True)

        # --- Code Formats (with contrast correction) ---
        code_block_bg_color = QColor(colors.get('editor.lineHighlightBackground', '#323232'))

        self.formats['code_block'] = QTextCharFormat()
        self.formats['code_block'].setBackground(code_block_bg_color)
        self.formats['code_block'].setFontFamily("Consolas")

        self.formats['inline_code'] = QTextCharFormat()
        original_inline_code_fg = QColor(colors.get('syntax.string', '#a7c080'))

        final_inline_code_fg = self._get_high_contrast_color(original_inline_code_fg, code_block_bg_color)

        self.formats['inline_code'].setBackground(code_block_bg_color)
        self.formats['inline_code'].setForeground(final_inline_code_fg)
        self.formats['inline_code'].setFontFamily("Consolas")

        self.rules = [
            (QRegularExpression(r"^(#{1,6})\s"), self._format_heading),
            (QRegularExpression(r"^>+\s?"), self._format_simple('blockquote')),
            (QRegularExpression(r"^[-_*]{3,}\s*$"), self._format_simple('hr')),
            (QRegularExpression(r"^(\s*[\*\-\+]\s)"), self._format_marker_only()),
            (QRegularExpression(r"^(\s*[0-9]+\.\s)"), self._format_marker_only()),
            (QRegularExpression(r"(\*\*)(\S.*?\S)(\*\*)"), self._format_inline('bold')),
            (QRegularExpression(r"(\*)(\S.*?\S)(\*)"), self._format_inline('italic')),
            (QRegularExpression(r"(__)(\S.*?\S)(__)"), self._format_inline('bold')),
            (QRegularExpression(r"(_)(\S.*?\S)(_)"), self._format_inline('italic')),
            (QRegularExpression(r"(~~)([^~]+)(~~)"), self._format_inline('strikethrough')),
            (QRegularExpression(r"(`)([^`]+)(`)"), self._format_inline('inline_code')),
        ]
        self.code_block_delimiter = QRegularExpression(r"^```")

    def _format_simple(self, fmt_name):
        def formatter(match):
            self.setFormat(match.capturedStart(0), match.capturedLength(0), self.formats[fmt_name])

        return formatter

    def _format_marker_only(self):
        def formatter(match):
            self.setFormat(match.capturedStart(1), match.capturedLength(1), self.formats['marker'])

        return formatter

    def _format_heading(self, match):
        marker = match.captured(1)
        level = len(marker)
        self.setFormat(match.capturedStart(1), len(marker), self.formats['marker'])
        content_start = match.capturedEnd(1)
        self.setFormat(content_start, self.currentBlock().length() - content_start, self.formats[f'h{level}'])

    def _format_inline(self, fmt_name):
        def formatter(match):
            self.setFormat(match.capturedStart(2), len(match.captured(2)), self.formats[fmt_name])

            self.setFormat(match.capturedStart(1), len(match.captured(1)), self.formats['marker'])
            self.setFormat(match.capturedStart(3), len(match.captured(3)), self.formats['marker'])

            if fmt_name == 'inline_code':
                code_bg_color = self.formats['inline_code'].background().color()
                original_marker_fg = self.formats['marker'].foreground().color()

                corrected_marker_fg = self._get_high_contrast_color(original_marker_fg, code_bg_color)

                marker_with_bg_format = QTextCharFormat()
                marker_with_bg_format.setBackground(code_bg_color)
                marker_with_bg_format.setForeground(corrected_marker_fg)
                marker_with_bg_format.setFontWeight(self.formats['marker'].fontWeight())

                self.setFormat(match.capturedStart(1), len(match.captured(1)), marker_with_bg_format)
                self.setFormat(match.capturedStart(3), len(match.captured(3)), marker_with_bg_format)

        return formatter

    def highlightBlock(self, text: str):
        is_in_code_block = self.previousBlockState() == 1
        is_delimiter = self.code_block_delimiter.match(text).hasMatch()

        if is_delimiter:
            self.setCurrentBlockState(0 if is_in_code_block else 1)
            is_in_code_block = True
        elif is_in_code_block:
            self.setCurrentBlockState(1)
        else:
            self.setCurrentBlockState(0)

        if is_in_code_block:
            code_bg = self.formats['code_block'].background().color()
            corrected_fg = self._get_high_contrast_color(self.default_fg, code_bg)

            block_format = QTextCharFormat(self.formats['code_block'])
            block_format.setForeground(corrected_fg)
            self.setFormat(0, len(text), block_format)

            if is_delimiter:
                self.setFormat(0, 3, self.formats['marker'])
            return

        for pattern, formatter in self.rules:
            iterator = pattern.globalMatch(text)
            while iterator.hasNext():
                match = iterator.next()
                formatter(match)

    def rehighlight_document(self):
        """Force a re-highlight of the entire document, e.g., on theme change."""
        self.default_fg = QColor(
            theme_manager.current_theme_data.get("colors", {}).get(
                "editor.foreground", "#ffffff"
            )
        )
        self.initialize_formats_and_rules()
        super().rehighlight()
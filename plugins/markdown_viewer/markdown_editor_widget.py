# /plugins/markdown_viewer/markdown_editor_widget.py
import qtawesome as qta
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTextBrowser,
                             QPlainTextEdit, QSplitter, QMenu, QLineEdit,
                             QToolButton, QFrame)
from PyQt6.QtGui import (QFont, QTextCursor, QMouseEvent, QPainter, QColor,
                         QKeySequence, QAction)
from PyQt6.QtCore import QTimer, pyqtSignal, Qt, QSize
from markdown import markdown

from app_core.theme_manager import theme_manager
from app_core.settings_manager import settings_manager
from utils.logger import log
from .markdown_syntax_highlighter import MarkdownSyntaxHighlighter


# =============================================================================
# Floating Formatting Toolbar
# =============================================================================
class MarkdownFormattingToolbar(QWidget):
    """A floating, horizontal toolbar for rich text formatting."""
    format_bold_requested = pyqtSignal()
    format_italic_requested = pyqtSignal()
    format_strikethrough_requested = pyqtSignal()
    format_inline_code_requested = pyqtSignal()
    heading_level_requested = pyqtSignal(int)
    code_block_requested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(
            Qt.WindowType.ToolTip | Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self.frame = QFrame(self)
        self.frame.setObjectName("FormattingToolbarFrame")

        self.layout = QHBoxLayout(self.frame)
        self.layout.setContentsMargins(4, 4, 4, 4)
        self.layout.setSpacing(2)

        self._add_tool_button("fa5s.bold", "Bold (Ctrl+B)",
                              self.format_bold_requested)
        self._add_tool_button("fa5s.italic", "Italic (Ctrl+I)",
                              self.format_italic_requested)
        self._add_tool_button("fa5s.strikethrough", "Strikethrough",
                              self.format_strikethrough_requested)
        self._add_tool_button("fa5s.code", "Inline Code",
                              self.format_inline_code_requested)
        self._add_separator()
        self._create_heading_menu()
        self._add_separator()
        self._add_tool_button(
            "fa5s.file-code", "Insert Code Block", self.code_block_requested
        )

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(self.frame)
        self.update_theme()

    def _add_tool_button(self, icon_name, tooltip, signal_to_emit):
        button = QToolButton()
        button.setIcon(qta.icon(icon_name, color='white'))
        button.setToolTip(tooltip)
        button.clicked.connect(signal_to_emit.emit)
        self.layout.addWidget(button)

    def _add_separator(self):
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.VLine)
        sep.setFrameShadow(QFrame.Shadow.Sunken)
        self.layout.addWidget(sep)

    def _create_heading_menu(self):
        heading_button = QToolButton()
        heading_button.setIcon(qta.icon("fa5s.heading", color='white'))
        heading_button.setToolTip("Apply Heading")
        heading_button.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        heading_menu = QMenu(self)
        for i in range(1, 7):
            action = QAction(f"Heading {i}", self)
            action.triggered.connect(
                lambda _, level=i: self.heading_level_requested.emit(level))
            heading_menu.addAction(action)
        heading_button.setMenu(heading_menu)
        self.layout.addWidget(heading_button)

    def update_theme(self):
        colors = theme_manager.current_theme_data.get('colors', {})
        menu_bg = colors.get('menu.background', '#3a4145')
        border_color = colors.get('input.border', '#555555')
        self.frame.setStyleSheet(f"""
            #FormattingToolbarFrame {{
                background-color: {menu_bg};
                border: 1px solid {border_color};
                border-radius: 6px;
            }}
            QToolButton {{
                background-color: transparent; border: none; padding: 5px;
                border-radius: 4px;
            }}
            QToolButton:hover {{
                background-color: {colors.get('accent', '#88c0d0')};
            }}
            QFrame[frameShape="5"] {{ color: {border_color}; }}
        """)

    def show_at(self, pos):
        self.move(pos)
        self.show()
        self.activateWindow()
        self.setFocus()

    def focusOutEvent(self, event):
        self.hide()
        super().focusOutEvent(event)


class LineNumberArea(QWidget):
    def __init__(self, editor):
        super().__init__(editor)
        self.source_editor = editor

    def sizeHint(self):
        return QSize(self.source_editor.line_number_area_width(), 0)

    def paintEvent(self, event):
        self.source_editor.line_number_area_paint_event(event)


class InteractiveTextBrowser(QTextBrowser):
    source_focus_requested = pyqtSignal(str)

    def mouseDoubleClickEvent(self, event: QMouseEvent):
        cursor = self.cursorForPosition(event.pos())
        cursor.select(QTextCursor.SelectionType.BlockUnderCursor)
        if (clicked_text := cursor.selectedText().strip()):
            self.source_focus_requested.emit(clicked_text)
        super().mouseDoubleClickEvent(event)


class MarkdownSourceEditor(QPlainTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.line_number_area = LineNumberArea(self)
        self.blockCountChanged.connect(self.update_line_number_area_width)
        self.updateRequest.connect(self.update_line_number_area)
        self.update_line_number_area_width(0)
        self.formatting_toolbar = MarkdownFormattingToolbar(self)
        self.formatting_toolbar.format_bold_requested.connect(self._format_bold)
        self.formatting_toolbar.format_italic_requested.connect(
            self._format_italic)
        self.formatting_toolbar.format_strikethrough_requested.connect(
            self._format_strikethrough)
        self.formatting_toolbar.format_inline_code_requested.connect(
            self._format_inline_code)
        self.formatting_toolbar.heading_level_requested.connect(
            self._format_heading)
        self.formatting_toolbar.code_block_requested.connect(
            self._insert_code_block)

    def line_number_area_width(self):
        digits = len(str(max(1, self.blockCount())))
        return 10 + self.fontMetrics().horizontalAdvance('9') * digits

    def update_line_number_area_width(self, _):
        self.setViewportMargins(self.line_number_area_width(), 0, 0, 0)

    def update_line_number_area(self, rect, dy):
        if dy:
            self.line_number_area.scroll(0, dy)
        else:
            self.line_number_area.update(0, rect.y(),
                                         self.line_number_area.width(),
                                         rect.height())
        if rect.contains(self.viewport().rect()):
            self.update_line_number_area_width(0)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        cr = self.contentsRect()
        self.line_number_area.setGeometry(
            cr.left(), cr.top(), self.line_number_area_width(), cr.height())

    def line_number_area_paint_event(self, event):
        painter = QPainter(self.line_number_area)
        colors = theme_manager.current_theme_data.get('colors', {})
        gutter_bg = colors.get('editorGutter.background', '#f0f0f0')
        painter.fillRect(event.rect(), QColor(gutter_bg))

        block = self.firstVisibleBlock()
        block_geo = self.blockBoundingGeometry(block)
        top = block_geo.translated(self.contentOffset()).top()
        bottom = top + self.blockBoundingRect(block).height()

        current_line_num = self.textCursor().blockNumber()
        block_number = block.blockNumber()
        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                number = str(block_number + 1)
                is_current = block_number == current_line_num
                pen_color = colors.get(
                    'editor.foreground' if is_current else
                    'editorGutter.foreground'
                )
                painter.setPen(QColor(pen_color))
                painter.drawText(
                    0, int(top), self.line_number_area.width() - 5,
                    self.fontMetrics().height(),
                    Qt.AlignmentFlag.AlignRight, number
                )
            block = block.next()
            top = bottom
            bottom = top + self.blockBoundingRect(block).height()
            block_number += 1

    def contextMenuEvent(self, event):
        self.formatting_toolbar.show_at(event.globalPos())

    def keyPressEvent(self, event):
        if event.matches(QKeySequence.StandardKey.Bold):
            self._format_bold()
        elif event.matches(QKeySequence.StandardKey.Italic):
            self._format_italic()
        else:
            super().keyPressEvent(event)

    def _wrap_selection(self, prefix, suffix=None):
        suffix = suffix or prefix
        cursor = self.textCursor()
        if not cursor.hasSelection():
            cursor.insertText(f"{prefix}text{suffix}")
            cursor.movePosition(QTextCursor.MoveOperation.Left, n=len(suffix))
            cursor.movePosition(QTextCursor.MoveOperation.Left,
                                QTextCursor.MoveMode.KeepAnchor, n=4)
        else:
            text = cursor.selectedText()
            cursor.insertText(f"{prefix}{text}{suffix}")
        self.setTextCursor(cursor)

    def _format_bold(self):
        self._wrap_selection("**")

    def _format_italic(self):
        self._wrap_selection("*")

    def _format_strikethrough(self):
        self._wrap_selection("~~")

    def _format_inline_code(self):
        self._wrap_selection("`")

    def _format_heading(self, level):
        cursor = self.textCursor()
        cursor.beginEditBlock()
        cursor.movePosition(QTextCursor.MoveOperation.StartOfBlock)
        cursor.insertText(f'{"#" * level} ')
        cursor.endEditBlock()

    def _insert_code_block(self):
        cursor = self.textCursor()
        cursor.beginEditBlock()
        cursor.insertText("\n```python\n\n```\n")
        cursor.movePosition(QTextCursor.MoveOperation.Up, n=2)
        cursor.endEditBlock()
        self.setTextCursor(cursor)


class MarkdownEditorWidget(QWidget):
    content_changed = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.filepath = None
        self.original_hash = 0
        self.is_syncing_scroll = False
        self._setup_ui()
        self._connect_signals()
        self.update_theme()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        self.search_bar = QWidget()
        search_layout = QHBoxLayout(self.search_bar)
        search_layout.setContentsMargins(5, 2, 5, 2)
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Find...")
        self.prev_button = QToolButton()
        self.prev_button.setIcon(qta.icon('fa5s.arrow-up'))
        self.next_button = QToolButton()
        self.next_button.setIcon(qta.icon('fa5s.arrow-down'))
        self.close_search_button = QToolButton()
        self.close_search_button.setIcon(qta.icon('fa5s.times'))
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(self.prev_button)
        search_layout.addWidget(self.next_button)
        search_layout.addWidget(self.close_search_button)
        layout.addWidget(self.search_bar)
        self.search_bar.hide()
        splitter = QSplitter(self)
        layout.addWidget(splitter)
        self.editor = MarkdownSourceEditor()
        self.editor_scrollbar = self.editor.verticalScrollBar()
        self.highlighter = MarkdownSyntaxHighlighter(self.editor.document())
        self.viewer = InteractiveTextBrowser()
        self.viewer.setOpenExternalLinks(True)
        self.viewer_scrollbar = self.viewer.verticalScrollBar()
        splitter.addWidget(self.editor)
        splitter.addWidget(self.viewer)
        splitter.setSizes([self.width() // 2, self.width() // 2])

    def _connect_signals(self):
        self.update_timer = QTimer(self)
        self.update_timer.setSingleShot(True)
        self.update_timer.setInterval(300)
        self.update_timer.timeout.connect(self._render_preview)
        self.editor.textChanged.connect(self.update_timer.start)
        self.editor.textChanged.connect(self.content_changed.emit)
        self.editor_scrollbar.valueChanged.connect(self._sync_viewer_scroll)
        self.viewer_scrollbar.valueChanged.connect(self._sync_editor_scroll)
        self.viewer.source_focus_requested.connect(self._focus_source_text)
        self.search_input.returnPressed.connect(self.next_button.click)
        self.next_button.clicked.connect(lambda: self._find_text())
        self.prev_button.clicked.connect(
            lambda: self._find_text(backwards=True))
        self.close_search_button.clicked.connect(self.search_bar.hide)

    def keyPressEvent(self, event):
        if event.matches(QKeySequence.StandardKey.Find):
            self.search_bar.show()
            self.search_input.setFocus()
            self.search_input.selectAll()
        elif event.key() == Qt.Key.Key_Escape and self.search_bar.isVisible():
            self.search_bar.hide()
        else:
            self.editor.keyPressEvent(event)
            super().keyPressEvent(event)

    def _find_text(self, backwards=False):
        query = self.search_input.text()
        if not query:
            return
        flags = QTextCursor.FindFlag(0)
        if self.editor.find(
                query, flags | QTextCursor.FindFlag.FindCaseSensitively):
            flags |= QTextCursor.FindFlag.FindCaseSensitively
        if backwards:
            flags |= QTextCursor.FindFlag.FindBackward
        self.editor.find(query, flags)

    def _focus_source_text(self, text_to_find: str):
        if self.editor.find(text_to_find):
            self.editor.setFocus()
        elif self.editor.find(text_to_find.splitlines()[0]):
            self.editor.setFocus()

    def _sync_viewer_scroll(self, value):
        if self.is_syncing_scroll:
            return
        self.is_syncing_scroll = True
        editor_max = self.editor_scrollbar.maximum()
        scroll_ratio = value / editor_max if editor_max > 0 else 0
        self.viewer_scrollbar.setValue(
            int(self.viewer_scrollbar.maximum() * scroll_ratio))
        self.is_syncing_scroll = False

    def _sync_editor_scroll(self, value):
        if self.is_syncing_scroll:
            return
        self.is_syncing_scroll = True
        viewer_max = self.viewer_scrollbar.maximum()
        scroll_ratio = value / viewer_max if viewer_max > 0 else 0
        self.editor_scrollbar.setValue(
            int(self.editor_scrollbar.maximum() * scroll_ratio))
        self.is_syncing_scroll = False

    def load_file(self, filepath: str):
        self.filepath = filepath
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            self.original_hash = hash(content)
            self.editor.setPlainText(content)
        except Exception as e:
            log.error(f"Error loading Markdown file {filepath}: {e}")
            self.editor.setPlainText(f"# Error loading file\n\n{e}")

    def get_content(self) -> str:
        return self.editor.toPlainText()

    def _render_preview(self):
        scroll_max = self.viewer_scrollbar.maximum()
        old_pos_percent = (self.viewer_scrollbar.value() / scroll_max
                           if scroll_max > 0 else 0)
        raw_text = self.editor.toPlainText()
        html = markdown(raw_text,
                        extensions=['fenced_code', 'tables', 'extra',
                                    'sane_lists'])
        self.viewer.setHtml(html)

        def restore_scroll():
            new_max = self.viewer_scrollbar.maximum()
            self.viewer_scrollbar.setValue(int(new_max * old_pos_percent))

        QTimer.singleShot(0, restore_scroll)

    def update_theme(self):
        colors = theme_manager.current_theme_data.get('colors', {})
        font_family = settings_manager.get("font_family", "Consolas")
        font_size = settings_manager.get("font_size", 11)
        font = QFont(font_family, font_size)
        self.editor.setFont(font)
        self.editor.update_line_number_area_width(0)
        editor_bg = colors.get('editor.background', '#2b2b2b')
        editor_fg = colors.get('editor.foreground', '#a9b7c6')
        self.editor.setStyleSheet(
            f"background-color: {editor_bg}; color: {editor_fg}; "
            f"border: none; padding: 0px;")
        self.highlighter.rehighlight_document()
        if self.editor.formatting_toolbar:
            self.editor.formatting_toolbar.update_theme()
        viewer_bg = colors.get('window.background', '#2f383e')
        accent_color = colors.get('accent', '#88c0d0')
        line_highlight_bg = colors.get(
            'editor.lineHighlightBackground', '#323232')
        comment_color = colors.get('syntax.comment', '#808080')
        string_color = colors.get('syntax.string', '#6A8759')
        style_sheet = f"""
            h1, h2, h3, h4, h5, h6 {{
                color: {accent_color};
                border-bottom: 1px solid {line_highlight_bg};
                padding-bottom: 4px; margin-top: 15px;
            }}
            a {{ color: {string_color}; text-decoration: none; }}
            a:hover {{ text-decoration: underline; }}
            p, li {{ font-size: {font_size}pt; }}
            pre {{
                background-color: {editor_bg};
                border: 1px solid {colors.get('input.border', '#555')};
                border-radius: 4px; padding: 10px;
                font-family: "{font_family}";
            }}
            code {{
                background-color: {line_highlight_bg};
                font-family: "{font_family}";
                border-radius: 2px; padding: 2px 4px;
            }}
            blockquote {{
                color: {comment_color};
                border-left: 3px solid {accent_color};
                padding-left: 10px; margin-left: 5px;
            }}
            table {{ border-collapse: collapse; }}
            th, td {{
                border: 1px solid {colors.get('input.border', '#555')};
                padding: 6px;
            }}
            th {{ background-color: {line_highlight_bg}; }}"""
        self.viewer.document().setDefaultStyleSheet(style_sheet)
        default_font = QFont(
            settings_manager.get("font_family", "Arial"), font_size
        )
        self.viewer.document().setDefaultFont(default_font)
        self.viewer.setStyleSheet(
            f"background-color: {viewer_bg}; border:none;")
        self._render_preview()
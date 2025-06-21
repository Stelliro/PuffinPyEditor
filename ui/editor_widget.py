# PuffinPyEditor/ui/editor_widget.py
import re
from PyQt6.QtWidgets import QPlainTextEdit, QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QMenu, QToolTip
from PyQt6.QtGui import (QFont, QColor, QPainter, QPaintEvent, QFontMetrics,
                         QKeyEvent, QTextCursor, QTextBlockFormat, QAction, QCursor, QTextDocument, QPalette, QPen)
from PyQt6.QtCore import Qt, QRect, pyqtSignal, QTimer
from utils.logger import log
from app_core.settings_manager import settings_manager
from app_core.completion_manager import CompletionManager
from app_core.theme_manager import theme_manager
from .line_number_area import LineNumberArea
from .widgets.syntax_highlighter import PythonSyntaxHighlighter


class CustomPlainTextEdit(QPlainTextEdit):
    cursor_position_changed_signal = pyqtSignal(int, int)
    definition_requested_from_menu = pyqtSignal()

    def __init__(self, editor_widget_ref, parent=None):
        super().__init__(parent)
        self.editor_widget_ref = editor_widget_ref
        self.setMouseTracking(True)
        self.hover_timer = QTimer(self)
        self.hover_timer.setSingleShot(True)
        self.hover_timer.setInterval(600)
        self.hover_timer.timeout.connect(self._request_hover_tip)
        self.cursorPositionChanged.connect(self._on_cursor_position_changed)

    def contextMenuEvent(self, event):
        menu = self.createStandardContextMenu()
        menu.addSeparator()
        goto_def_action = QAction("Go to Definition", self)
        goto_def_action.setShortcut("F12")
        goto_def_action.triggered.connect(self.definition_requested_from_menu.emit)
        menu.addAction(goto_def_action)
        menu.exec(event.globalPos())

    def mouseMoveEvent(self, event):
        self.hover_timer.start()
        QToolTip.hideText()
        super().mouseMoveEvent(event)

    def _request_hover_tip(self):
        cursor = self.cursorForPosition(self.viewport().mapFromGlobal(QCursor.pos()))
        self.editor_widget_ref.request_signature(cursor.blockNumber() + 1, cursor.columnNumber())

    def _on_cursor_position_changed(self):
        cursor = self.textCursor()
        self.cursor_position_changed_signal.emit(cursor.blockNumber() + 1, cursor.columnNumber() + 1)
        self.hover_timer.stop()
        QToolTip.hideText()

    def paintEvent(self, event: QPaintEvent):
        super().paintEvent(event)
        self._paint_indentation_guides()

    def _paint_indentation_guides(self):
        if not settings_manager.get("show_indentation_guides"):
            return

        painter = QPainter(self.viewport())
        colors = theme_manager.current_theme_data.get('colors', {})
        guide_color = QColor(colors.get('input.border', '#555555'))
        pen = QPen(guide_color)
        pen.setStyle(Qt.PenStyle.DotLine)
        painter.setPen(pen)

        indent_width = settings_manager.get("indent_width", 4)
        char_width = self.fontMetrics().horizontalAdvance(' ')
        offset = self.contentOffset()

        block = self.firstVisibleBlock()

        while block.isValid():
            geom = self.blockBoundingGeometry(block).translated(offset)
            if geom.bottom() < 0:
                block = block.next()
                continue
            if geom.top() > self.viewport().height():
                break

            text = block.text()
            leading_spaces = len(text) - len(text.lstrip(' '))

            for i in range(1, (leading_spaces // indent_width) + 2):
                x = geom.left() + (i * indent_width * char_width)
                if x > geom.left():
                    painter.drawLine(int(x), int(geom.top()), int(x), int(geom.bottom()))

            block = block.next()


class EditorWidget(QWidget):
    content_possibly_changed = pyqtSignal()
    cursor_position_display_updated = pyqtSignal(int, int)

    def __init__(self, completion_manager: CompletionManager, parent=None):
        super().__init__(parent)
        self.filepath = None
        self.completion_manager = completion_manager
        self.completion_manager.hover_tip_ready.connect(self._display_tooltip)

        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

        self.text_area = CustomPlainTextEdit(self)
        self.text_area.definition_requested_from_menu.connect(self.request_definition_from_context)

        self.line_number_area = LineNumberArea(self)
        self.layout.addWidget(self.line_number_area)
        self.layout.addWidget(self.text_area)

        self.highlighter = PythonSyntaxHighlighter(self.text_area.document())

        self.text_area.blockCountChanged.connect(self._update_line_number_area_width)
        self.text_area.updateRequest.connect(self._update_line_number_area)
        self.text_area.cursor_position_changed_signal.connect(self.cursor_position_display_updated.emit)
        self.text_area.textChanged.connect(self.content_possibly_changed.emit)

        self.update_editor_settings()
        self._update_line_number_area_width()

    def set_filepath(self, filepath: str | None):
        self.filepath = filepath

    def request_definition_from_context(self):
        if not self.filepath: return
        cursor = self.text_area.textCursor()
        self.completion_manager.request_definition(self.get_text(), cursor.blockNumber() + 1, cursor.columnNumber(),
                                                   self.filepath)

    def request_signature(self, line: int, col: int):
        if not self.filepath: return
        self.completion_manager.request_signature(self.get_text(), line, col, self.filepath)

    def _display_tooltip(self, html_content: str):
        if html_content:
            QToolTip.showText(QCursor.pos(), html_content, self.text_area.viewport())

    def get_text(self) -> str:
        return self.text_area.toPlainText()

    def set_text(self, text: str):
        self.text_area.setPlainText(text)
        self.update_editor_settings()

    def find_next(self, query: str, flags: QTextDocument.FindFlag):
        found = self.text_area.find(query, flags)
        if not found:
            cursor = self.text_area.textCursor()
            cursor.movePosition(QTextCursor.MoveOperation.Start)
            self.text_area.setTextCursor(cursor)
            self.text_area.find(query, flags)

    def replace_current(self, query: str, replace_text: str, flags: QTextDocument.FindFlag):
        cursor = self.text_area.textCursor()
        if cursor.hasSelection():
            text = cursor.selectedText()
            is_match = (text == query) if (flags & QTextDocument.FindFlag.FindCaseSensitively) else (
                    text.lower() == query.lower())
            if is_match:
                cursor.insertText(replace_text)
        self.find_next(query, flags)

    def replace_all(self, query: str, replace_text: str, flags: QTextDocument.FindFlag) -> int:
        count = 0
        self.text_area.moveCursor(QTextCursor.MoveOperation.Start)
        while self.text_area.find(query, flags):
            self.text_area.textCursor().insertText(replace_text)
            count += 1
        return count

    def line_number_area_width(self):
        count = max(1, self.text_area.blockCount())
        digits = len(str(count))
        space = 30 + self.fontMetrics().horizontalAdvance('9') * digits
        return space

    def _update_line_number_area_width(self, newBlockCount=0):
        self.line_number_area.setFixedWidth(self.line_number_area_width())

    def _update_line_number_area(self, rect, dy):
        if dy:
            self.line_number_area.scroll(0, dy)
        else:
            self.line_number_area.update(0, rect.y(), self.line_number_area.width(), rect.height())

    def line_number_area_paint_event(self, event):
        painter = QPainter(self.line_number_area)

        colors = theme_manager.current_theme_data.get('colors', {})
        bg_color = QColor(colors.get('editorGutter.background', '#f0f0f0'))
        fg_color = QColor(colors.get('editorGutter.foreground', '#888888'))
        current_line_fg_color = QColor(colors.get('editor.foreground', '#111111'))

        painter.fillRect(event.rect(), bg_color)

        block = self.text_area.firstVisibleBlock()
        block_number = block.blockNumber()
        top = int(self.text_area.blockBoundingGeometry(block).translated(self.text_area.contentOffset()).top())
        bottom = top + int(self.text_area.blockBoundingRect(block).height())

        current_line_number = self.text_area.textCursor().blockNumber()

        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                number = str(block_number + 1)

                if block_number == current_line_number:
                    painter.setPen(current_line_fg_color)
                else:
                    painter.setPen(fg_color)
                painter.drawText(0, top, self.line_number_area.width() - 8, self.fontMetrics().height(),
                                 Qt.AlignmentFlag.AlignRight, number)

            block = block.next()
            top = bottom
            bottom = top + int(self.text_area.blockBoundingRect(block).height())
            block_number += 1

    def goto_line_and_column(self, line: int, col: int):
        if line <= 0: return
        block = self.text_area.document().findBlockByNumber(line - 1)
        if not block.isValid(): return

        cursor = QTextCursor(block)
        cursor.movePosition(QTextCursor.MoveOperation.Right, mode=QTextCursor.MoveMode.MoveAnchor, n=max(0, col - 1))

        self.text_area.setTextCursor(cursor)
        self.text_area.setFocus()

    def update_editor_settings(self):
        """Applies settings from SettingsManager to the editor."""
        font = QFont(settings_manager.get("font_family"), settings_manager.get("font_size"))
        self.text_area.setFont(font)
        self.line_number_area.setFont(font)

        # CORRECTED ENUM: Use QPlainTextEdit's enum, not QTextEdit's
        wrap_mode = QPlainTextEdit.LineWrapMode.WidgetWidth if settings_manager.get(
            "word_wrap") else QPlainTextEdit.LineWrapMode.NoWrap
        self.text_area.setLineWrapMode(wrap_mode)

        self.line_number_area.setVisible(settings_manager.get("show_line_numbers", True))

        self.text_area.viewport().update()
        log.debug("Editor settings applied.")
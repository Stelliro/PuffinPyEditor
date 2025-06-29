# PuffinPyEditor/ui/editor_widget.py
from PyQt6.QtWidgets import (QWidget, QPlainTextEdit, QHBoxLayout,
                             QTextEdit)
from PyQt6.QtCore import pyqtSignal, QRect, Qt
from PyQt6.QtGui import QTextCursor, QFont, QPainter, QColor, QTextFormat, QTextDocument

# Import necessary components
from .line_number_area import LineNumberArea
from .widgets.breakpoint_area import BreakpointArea
from .widgets.syntax_highlighter import PythonSyntaxHighlighter
from app_core.settings_manager import settings_manager
from app_core.theme_manager import theme_manager


class EditorWidget(QWidget):
    """
    A full-featured code editor widget composed of a text area, line number
    gutter, and breakpoint area.
    """
    content_possibly_changed = pyqtSignal()
    cursor_position_display_updated = pyqtSignal(int, int)

    def __init__(self, completion_manager=None, parent=None):
        super().__init__(parent)
        self.filepath = None
        self.breakpoints = set()
        self._completion_manager = completion_manager
        self.theme_manager = theme_manager
        self.main_layout = QHBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        self.text_area = QPlainTextEdit()
        self.line_number_area = LineNumberArea(self)
        self.breakpoint_area = BreakpointArea(self)
        self.highlighter = PythonSyntaxHighlighter(self.text_area.document())
        self.main_layout.addWidget(self.breakpoint_area)
        self.main_layout.addWidget(self.line_number_area)
        self.main_layout.addWidget(self.text_area)
        self.text_area.blockCountChanged.connect(self.update_line_number_area_width)
        self.text_area.updateRequest.connect(self.update_line_number_area)
        self.text_area.cursorPositionChanged.connect(self._on_cursor_pos_changed)
        self.text_area.textChanged.connect(self.content_possibly_changed)
        self.breakpoint_area.breakpoint_toggled.connect(self._toggle_breakpoint)
        self.update_editor_settings()
        self.update_line_number_area_width()

    def line_number_area_width(self):
        digits = len(str(max(1, self.text_area.blockCount())))
        space = 10 + self.fontMetrics().horizontalAdvance('9') * digits
        return space

    def update_line_number_area_width(self, new_block_count=0):
        self.line_number_area.setFixedWidth(self.line_number_area_width())

    def update_line_number_area(self, rect: QRect, dy: int):
        if dy:
            self.line_number_area.scroll(0, dy)
            self.breakpoint_area.scroll(0, dy)
        else:
            self.line_number_area.update(0, rect.y(), self.line_number_area.width(), rect.height())
            self.breakpoint_area.update(0, rect.y(), self.breakpoint_area.width(), rect.height())
        if rect.contains(self.text_area.viewport().rect()):
            self.update_line_number_area_width()

    def _toggle_breakpoint(self, line_num):
        if line_num in self.breakpoints: self.breakpoints.remove(line_num)
        else: self.breakpoints.add(line_num)
        self.breakpoint_area.update()

    def get_cursor_position(self) -> tuple[int, int]:
        cursor = self.text_area.textCursor()
        return cursor.blockNumber() + 1, cursor.columnNumber()

    def _on_cursor_pos_changed(self):
        line, col = self.get_cursor_position()
        self.cursor_position_display_updated.emit(line, col + 1)

    def get_text(self) -> str: return self.text_area.toPlainText()
    def set_text(self, text: str): self.text_area.setPlainText(text)
    def set_filepath(self, filepath: str | None): self.filepath = filepath

    def goto_line_and_column(self, line: int, col: int):
        cursor = QTextCursor(self.text_area.document().findBlockByNumber(line - 1))
        cursor.movePosition(QTextCursor.MoveOperation.Right, n=col)
        self.text_area.setTextCursor(cursor)
        self.text_area.setFocus()

    def find_next(self, query: str, flags: QTextDocument.FindFlag) -> bool:
        return self.text_area.find(query, flags)

    def replace_current(self, query: str, replace_text: str, flags: QTextDocument.FindFlag) -> bool:
        cursor = self.text_area.textCursor()
        if not cursor.hasSelection(): return False
        selected_text = cursor.selectedText()
        match_ok = (selected_text.lower() == query.lower() if
                    QTextDocument.FindFlag.FindCaseSensitively not in flags
                    else selected_text == query)
        if match_ok:
            cursor.insertText(replace_text)
            return True
        return False

    def replace_all(self, query: str, replace_text: str, flags: QTextDocument.FindFlag) -> int:
        count = 0
        self.text_area.moveCursor(QTextCursor.MoveOperation.Start)
        while self.text_area.find(query, flags):
            self.text_area.textCursor().insertText(replace_text)
            count += 1
        return count

    def update_editor_settings(self):
        font = QFont(settings_manager.get("font_family"), settings_manager.get("font_size"))
        self.text_area.setFont(font)
        self.line_number_area.setFont(font)
        self.breakpoint_area.setFont(font)
        self.text_area.setTabStopDistance(self.fontMetrics().horizontalAdvance(' ') * settings_manager.get("indent_width"))
        self.update_theme()

    def update_theme(self):
        colors = self.theme_manager.current_theme_data.get("colors", {})
        stylesheet = f"""
        QPlainTextEdit {{
            background-color: {colors.get('editor.background', '#1e1e1e')};
            color: {colors.get('editor.foreground', '#d4d4d4')};
            border: none;
            selection-background-color: {colors.get('editor.selectionBackground', '#264f78')};
        }}"""
        self.text_area.setStyleSheet(stylesheet)
        if self.highlighter: self.highlighter.rehighlight_document()
        self.line_number_area.update(); self.breakpoint_area.update()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        cr = self.text_area.contentsRect()
        self.line_number_area.setFixedHeight(cr.height())
        self.breakpoint_area.setFixedHeight(cr.height())
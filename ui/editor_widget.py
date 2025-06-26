# PuffinPyEditor/ui/editor_widget.py
from PyQt6.QtWidgets import (QPlainTextEdit, QWidget, QHBoxLayout, QTextEdit,
                             QToolTip, QFrame, QVBoxLayout)
from PyQt6.QtGui import (QFont, QColor, QPainter, QPaintEvent, QFontMetrics,
                         QKeyEvent, QTextCursor, QAction, QCursor, QTextDocument,
                         QPen, QTextFormat)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from utils.logger import log
from app_core.settings_manager import settings_manager
from app_core.completion_manager import CompletionManager
from app_core.theme_manager import theme_manager
from .line_number_area import LineNumberArea
from .widgets.breakpoint_area import BreakpointArea
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
        self.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)

    def keyPressEvent(self, event: QKeyEvent) -> None:
        if event.key() == Qt.Key.Key_Print:
            event.ignore()
            log.debug("Print Screen key ignored in editor to allow OS handling.")
            return

        is_shift = event.modifiers() & Qt.KeyboardModifier.ShiftModifier
        key = event.key()

        if key == Qt.Key.Key_Tab or key == Qt.Key.Key_Backtab:
            cursor = self.textCursor()
            if cursor.hasSelection():
                self._indent_selection(indent=not is_shift)
            elif not is_shift:
                self._insert_indentation()
            return

        super().keyPressEvent(event)

    def _insert_indentation(self):
        cursor = self.textCursor()
        style = settings_manager.get("indent_style")
        width = settings_manager.get("indent_width")
        cursor.insertText(" " * width if style == "spaces" else "\t")

    def _indent_selection(self, indent: bool = True):
        cursor = self.textCursor()
        start, end = cursor.selectionStart(), cursor.selectionEnd()

        cursor.setPosition(start)
        start_block = cursor.blockNumber()
        cursor.setPosition(end)
        end_block = cursor.blockNumber() if cursor.columnNumber() != 0 or end == start else cursor.blockNumber() - 1

        cursor.beginEditBlock()
        width = settings_manager.get("indent_width")
        indent_str = " " * width if settings_manager.get("indent_style") == "spaces" else "\t"

        for i in range(start_block, end_block + 1):
            cursor.setPosition(self.document().findBlockByNumber(i).position())
            if indent:
                cursor.insertText(indent_str)
            else:
                block_text = cursor.block().text()
                if block_text.startswith("\t"):
                    cursor.deleteChar()
                else:
                    leading_spaces = len(block_text) - len(block_text.lstrip(' '))
                    for _ in range(min(leading_spaces, width)):
                        cursor.deleteChar()
        cursor.endEditBlock()

        new_start_cursor = self.textCursor()
        new_start_cursor.setPosition(start)
        new_start_cursor.setPosition(end, QTextCursor.MoveMode.KeepAnchor)
        self.setTextCursor(new_start_cursor)

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
        self.editor_widget_ref._update_dynamic_highlights()

    def paintEvent(self, event: QPaintEvent):
        super().paintEvent(event)
        self.editor_widget_ref.paint_indentation_guides(self)


class EditorWidget(QFrame):
    content_possibly_changed = pyqtSignal()
    cursor_position_display_updated = pyqtSignal(int, int)

    def __init__(self, completion_manager: CompletionManager, parent=None):
        super().__init__(parent)
        self.setObjectName("EditorWidgetFrame")
        self.filepath = None
        self.completion_manager = completion_manager
        self.theme_manager = theme_manager
        self.breakpoints = set()
        self.completion_manager.hover_tip_ready.connect(self._display_tooltip)

        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        editor_area_widget = QWidget()
        self.layout = QHBoxLayout(editor_area_widget)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

        self.text_area = CustomPlainTextEdit(self)
        self.text_area.definition_requested_from_menu.connect(self.request_definition_from_context)

        self.breakpoint_area = BreakpointArea(self)
        self.line_number_area = LineNumberArea(self)
        self.layout.addWidget(self.breakpoint_area)
        self.layout.addWidget(self.line_number_area)
        self.layout.addWidget(self.text_area)
        
        self.main_layout.addWidget(editor_area_widget, 1)

        self.highlighter = PythonSyntaxHighlighter(self.text_area.document())

        self.text_area.blockCountChanged.connect(self._update_gutter_areas)
        self.text_area.updateRequest.connect(self._update_gutter_areas)
        self.text_area.cursor_position_changed_signal.connect(self.cursor_position_display_updated.emit)
        self.text_area.textChanged.connect(self.content_possibly_changed.emit)

        self.update_editor_settings()
        self._update_gutter_areas()

    def toggle_breakpoint(self, line_number):
        if line_number in self.breakpoints:
            self.breakpoints.remove(line_number)
        else:
            self.breakpoints.add(line_number)
        self._update_dynamic_highlights()
        self.breakpoint_area.update()

    def _update_dynamic_highlights(self):
        selections = []
        colors = self.theme_manager.current_theme_data.get('colors', {})
        current_line_color = QColor(colors.get('editor.lineHighlightBackground', '#ffffff'))

        selection = QTextEdit.ExtraSelection()
        selection.format.setBackground(current_line_color)
        selection.format.setProperty(QTextFormat.Property.FullWidthSelection, True)
        selection.cursor = self.text_area.textCursor()
        selections.append(selection)

        breakpoint_color = QColor(colors.get('accent', '#ff0000'))
        breakpoint_color.setAlpha(65)

        for line_num in self.breakpoints:
            bp_selection = QTextEdit.ExtraSelection()
            bp_selection.format.setBackground(breakpoint_color)
            bp_selection.format.setProperty(QTextFormat.Property.FullWidthSelection, True)
            block = self.text_area.document().findBlockByNumber(line_num - 1)
            if block.isValid():
                bp_selection.cursor = QTextCursor(block)
                selections.append(bp_selection)

        self.text_area.setExtraSelections(selections)

    def paint_indentation_guides(self, text_area):
        if not settings_manager.get("show_indentation_guides"):
            return

        painter = QPainter(text_area.viewport())
        colors = self.theme_manager.current_theme_data.get('colors', {})
        guide_color = QColor(colors.get('input.border', '#555555'))
        pen = QPen(guide_color)
        pen.setStyle(Qt.PenStyle.DotLine)
        painter.setPen(pen)

        tab_width_setting = settings_manager.get("indent_width", 4)
        char_width = text_area.fontMetrics().horizontalAdvance(' ')
        tab_width_pixels = tab_width_setting * char_width

        if tab_width_pixels <= 0:
            return

        offset = text_area.contentOffset()
        block = text_area.firstVisibleBlock()

        while block.isValid() and block.isVisible():
            geom = text_area.blockBoundingGeometry(block).translated(offset)
            if geom.bottom() < 0:
                block = block.next()
                continue
            if geom.top() > text_area.viewport().height():
                break

            text = block.text()
            leading_spaces = len(text) - len(text.lstrip(' '))

            indent_level = 0
            if settings_manager.get("indent_style") == "tabs":
                indent_level = text.count('\t') + (leading_spaces // tab_width_setting)
            else:
                indent_level = leading_spaces // tab_width_setting

            for i in range(1, indent_level + 1):
                x = geom.left() + (i * tab_width_pixels)
                painter.drawLine(int(x), int(geom.top()), int(x), int(geom.bottom()))

            block = block.next()

    def set_filepath(self, filepath: str | None):
        self.filepath = filepath

    def request_definition_from_context(self):
        if not self.filepath:
            return
        cursor = self.text_area.textCursor()
        self.completion_manager.request_definition(
            self.get_text(), cursor.blockNumber() + 1, cursor.columnNumber(), self.filepath
        )

    def request_signature(self, line: int, col: int):
        if not self.filepath:
            return
        self.completion_manager.request_signature(self.get_text(), line, col, self.filepath)

    def _display_tooltip(self, html_content: str):
        if html_content:
            QToolTip.showText(QCursor.pos(), html_content, self.text_area.viewport())

    def get_text(self) -> str:
        return self.text_area.toPlainText()

    def set_text(self, text: str):
        self.text_area.setPlainText(text)
        self.update_editor_settings()

    def find_next(self, query: str, flags: QTextDocument.FindFlag) -> bool:
        found = self.text_area.find(query, flags)
        if not found:
            cursor = self.text_area.textCursor()
            cursor.movePosition(QTextCursor.MoveOperation.Start)
            self.text_area.setTextCursor(cursor)
            return self.text_area.find(query, flags)
        return True

    def replace_current(self, query: str, replace_text: str, flags: QTextDocument.FindFlag) -> bool:
        cursor = self.text_area.textCursor()
        if cursor.hasSelection():
            cursor.insertText(replace_text)
            self.find_next(query, flags)
            return True
        return False

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
        space = 20 + self.fontMetrics().horizontalAdvance('9') * digits
        return space

    def _update_gutter_areas(self, rect=None, dy=None):
        if rect and dy is not None:
            self.line_number_area.scroll(0, dy)
            self.breakpoint_area.scroll(0, dy)
        else:
            self.line_number_area.update()
            self.breakpoint_area.update()

        self.line_number_area.setFixedWidth(self.line_number_area_width())

    def line_number_area_paint_event(self, event):
        painter = QPainter(self.line_number_area)

        colors = self.theme_manager.current_theme_data.get('colors', {})
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
                painter.setPen(current_line_fg_color if block_number == current_line_number else fg_color)
                painter.drawText(0, top, self.line_number_area.width() - 8, self.fontMetrics().height(),
                                 Qt.AlignmentFlag.AlignRight, number)

            block = block.next()
            top = bottom
            bottom = top + int(self.text_area.blockBoundingRect(block).height())
            block_number += 1

    def goto_line_and_column(self, line: int, col: int):
        if line <= 0:
            return
        block = self.text_area.document().findBlockByNumber(line - 1)
        if not block.isValid():
            return

        cursor = QTextCursor(block)
        cursor.movePosition(QTextCursor.MoveOperation.Right, mode=QTextCursor.MoveMode.MoveAnchor, n=max(0, col - 1))

        self.text_area.setTextCursor(cursor)
        self.text_area.setFocus()

    def update_editor_settings(self):
        """Applies settings from SettingsManager to the editor."""
        font = QFont(settings_manager.get("font_family"), settings_manager.get("font_size"))
        self.text_area.setFont(font)
        self.line_number_area.setFont(font)
        self.breakpoint_area.setFont(font)

        metrics = QFontMetrics(font)
        tab_width = settings_manager.get("indent_width")
        self.text_area.setTabStopDistance(tab_width * metrics.horizontalAdvance(' '))

        self._update_dynamic_highlights()
        self.text_area.viewport().update()
        log.debug("Editor settings applied.")
# /ui/editor_widget.py
from PyQt6.QtWidgets import (QWidget, QPlainTextEdit, QHBoxLayout, QVBoxLayout,
                             QTextEdit)
from PyQt6.QtCore import pyqtSignal, QRect, Qt, QSize
from PyQt6.QtGui import (QTextCursor, QFont, QPainter, QColor, QTextFormat,
                         QTextDocument, QSyntaxHighlighter, QKeySequence)  # Added QKeySequence

from .widgets.breakpoint_area import BreakpointArea
from .widgets.find_panel import FindPanel
from app_core.settings_manager import settings_manager
from app_core.theme_manager import theme_manager
from utils.logger import log


class LineNumberArea(QWidget):
    """
    A simple widget that acts as a canvas for the EditorWidget to paint
    line numbers onto.
    """

    def __init__(self, editor_widget: 'EditorWidget'):
        super().__init__(editor_widget)
        self.editor = editor_widget

    def sizeHint(self) -> QSize:
        """Determines the required width of the widget."""
        return QSize(self.editor.calculate_line_number_area_width(), 0)

    def paintEvent(self, event) -> None:
        """Delegates the paint event to the parent editor widget."""
        self.editor.line_number_area_paint_event(event)


# --- FIX START: Corrected the CodeTextEdit implementation ---
# This class had a logical bug where `self.parent()` did not reliably point to the
# EditorWidget due to Qt's layout parenting rules. This can cause instability.
# The fix is to give it a direct reference to the editor it belongs to.
class CodeTextEdit(QPlainTextEdit):
    """A QPlainTextEdit that correctly forwards key presses to its owner EditorWidget."""

    # This is the new constructor! It takes an explicit reference to the EditorWidget.
    def __init__(self, editor: 'EditorWidget'):
        # We still pass the editor as the parent to super() for proper
        # Qt object ownership and automatic cleanup. It's good practice!
        super().__init__(editor)
        # We store our own direct, stable reference to the "logical" parent, the EditorWidget.
        # This avoids any ambiguity from layout reparenting.
        self._editor_widget = editor

    def keyPressEvent(self, event):
        # We now use our stable _editor_widget reference to forward the event.
        # This ensures the key press is always sent to the correct handler in EditorWidget.
        if self._editor_widget.keyPressEvent(event):
            # If the EditorWidget handled it (e.g., for Ctrl+F), we stop processing.
            return

        # If the EditorWidget didn't handle the key, we let the QPlainTextEdit
        # process it as usual (e.g., for typing text).
        super().keyPressEvent(event)


# --- FIX END ---


class EditorWidget(QWidget):
    """
    A full-featured code editor widget. It composes a text area with line
    number and breakpoint sidebars (gutters). The painting logic for the
    gutters is handled within this class for stability.
    """
    content_possibly_changed = pyqtSignal()
    cursor_position_display_updated = pyqtSignal(int, int)
    # This new signal allows us to send status messages up to the main window
    # without creating a hard dependency. It's good practice!
    status_message_requested = pyqtSignal(str, int)

    def __init__(self, completion_manager=None, parent=None):
        super().__init__(parent)
        self.filepath: str | None = None
        self.breakpoints: set[int] = set()
        self._completion_manager = completion_manager
        self.theme_manager = theme_manager
        self.highlighter: QSyntaxHighlighter | None = None

        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        # --- The Find Panel is now created here! ---
        self.find_panel = FindPanel(self)
        self.find_panel.close_requested.connect(self.hide_find_panel)
        # We pass its status message request up to our own signal.
        self.find_panel.status_message_requested.connect(self.status_message_requested.emit)
        self.main_layout.addWidget(self.find_panel)
        self.find_panel.hide()  # It starts hidden, of course.

        editor_area_container = QWidget()
        editor_hbox = QHBoxLayout(editor_area_container)
        editor_hbox.setContentsMargins(0, 0, 0, 0)
        editor_hbox.setSpacing(0)

        self.breakpoint_area = BreakpointArea(self)
        self.line_number_area = LineNumberArea(self)
        # Here we instantiate our new, more robust CodeTextEdit class.
        self.text_area = CodeTextEdit(self)

        editor_hbox.addWidget(self.breakpoint_area)
        editor_hbox.addWidget(self.line_number_area)
        editor_hbox.addWidget(self.text_area, 1)

        self.main_layout.addWidget(editor_area_container)

        self._connect_signals()
        self.update_editor_settings()

    def _connect_signals(self):
        self.text_area.blockCountChanged.connect(self._update_gutter_widths)
        self.text_area.updateRequest.connect(self._on_editor_viewport_changed)
        self.text_area.cursorPositionChanged.connect(self._on_cursor_position_changed)
        self.text_area.textChanged.connect(self.content_possibly_changed)
        self.breakpoint_area.breakpoint_toggled.connect(self._toggle_breakpoint)

    def keyPressEvent(self, event) -> bool:
        # The editor widget itself now handles the Ctrl+F shortcut.
        if event.matches(QKeySequence.StandardKey.Find):
            if self.find_panel.isVisible():
                self.hide_find_panel()
            else:
                self.show_find_panel()
            return True  # We've handled the event!
        return False  # Let the CodeTextEdit handle other keys.

    def show_find_panel(self):
        """Makes the Find Panel visible and connects it to this editor."""
        self.find_panel.connect_editor(self)
        self.find_panel.show()
        self.find_panel.focus_find_input()

    def hide_find_panel(self):
        """Hides the Find Panel and returns focus to the text area."""
        self.find_panel.hide()
        self.text_area.setFocus()

    def set_highlighter(self, highlighter_class):
        if self.highlighter:
            self.highlighter.setDocument(None)
        if highlighter_class:
            self.highlighter = highlighter_class(self.text_area.document())
        else:
            self.highlighter = None

    def calculate_line_number_area_width(self) -> int:
        digits = len(str(max(1, self.text_area.blockCount())))
        space = 10 + self.fontMetrics().horizontalAdvance('9') * digits
        return space

    def _update_gutter_widths(self):
        width = self.calculate_line_number_area_width()
        self.line_number_area.setFixedWidth(width)

    def _on_editor_viewport_changed(self, rect: QRect, dy: int):
        if dy:
            self.line_number_area.scroll(0, dy)
            self.breakpoint_area.scroll(0, dy)
        else:
            self.line_number_area.update()
            self.breakpoint_area.update()
        self.highlight_current_line()

    def line_number_area_paint_event(self, event: 'QPaintEvent') -> None:
        try:
            painter = QPainter(self.line_number_area)
        except Exception as e:
            log.error(f"Could not create QPainter for line numbers: {e}")
            return

        colors = self.theme_manager.current_theme_data.get('colors', {})
        bg_color = QColor(colors.get('editorGutter.background', '#2c313a'))
        border_color = QColor(colors.get('input.border', '#555555'))

        painter.fillRect(event.rect(), bg_color)
        painter.setPen(border_color)
        painter.drawLine(event.rect().topRight(), event.rect().bottomRight())

        content_offset = self.text_area.contentOffset()
        current_line = self.text_area.textCursor().blockNumber()

        block = self.text_area.firstVisibleBlock()
        while block.isValid() and (block_top := self.text_area.blockBoundingGeometry(block).translated(
                content_offset).top()) <= event.rect().bottom():
            if block.isVisible():
                line_number_str = str(block.blockNumber() + 1)
                is_current = (block.blockNumber() == current_line)

                font = self.text_area.font()
                font.setBold(is_current)
                painter.setFont(font)

                color_key = 'editorLineNumber.activeForeground' if is_current else 'editorLineNumber.foreground'
                painter.setPen(QColor(colors.get(color_key, '#d0d0d0')))

                paint_rect = QRect(0, int(block_top), self.line_number_area.width(), self.fontMetrics().height())
                painter.drawText(paint_rect.adjusted(0, 0, -8, 0), Qt.AlignmentFlag.AlignRight, line_number_str)
            block = block.next()

    def _toggle_breakpoint(self, line_num: int):
        if line_num in self.breakpoints:
            self.breakpoints.remove(line_num)
        else:
            self.breakpoints.add(line_num)
        self.breakpoint_area.update()

    def get_cursor_position(self) -> tuple[int, int]:
        cursor = self.text_area.textCursor()
        return cursor.blockNumber(), cursor.columnNumber()

    def _on_cursor_position_changed(self):
        line, col = self.get_cursor_position()
        self.cursor_position_display_updated.emit(line, col)
        self.highlight_current_line()

    def highlight_current_line(self):
        selections = []
        if not self.text_area.isReadOnly():
            selection = QTextEdit.ExtraSelection()
            colors = self.theme_manager.current_theme_data.get('colors', {})
            line_color_hex = colors.get('editor.lineHighlightBackground')
            if line_color_hex:
                selection.format.setBackground(QColor(line_color_hex))
                selection.format.setProperty(QTextFormat.Property.FullWidthSelection, True)
                selection.cursor = self.text_area.textCursor()
                selection.cursor.clearSelection()
                selections.append(selection)
        self.text_area.setExtraSelections(selections)

    def get_text(self) -> str:
        return self.text_area.toPlainText()

    def set_text(self, text: str):
        self.text_area.setPlainText(text);
        self._on_cursor_position_changed()

    def set_filepath(self, filepath: str | None):
        self.filepath = filepath;
        self.breakpoint_area.setVisible(bool(filepath and filepath.lower().endswith('.py')))

    def goto_line_and_column(self, line: int, col: int):
        cursor = QTextCursor(self.text_area.document().findBlockByNumber(line - 1))
        cursor.movePosition(QTextCursor.MoveOperation.Right, n=col)
        self.text_area.setTextCursor(cursor);
        self.text_area.setFocus()

    def find_next(self, query: str, flags: QTextDocument.FindFlag) -> bool:
        return self.text_area.find(query, flags)

    def replace_current(self, query, replace, flags) -> bool:
        cursor = self.text_area.textCursor()
        if not cursor.hasSelection(): return False
        if (cursor.selectedText() == query) if (flags & QTextDocument.FindFlag.FindCaseSensitively) else (
                cursor.selectedText().lower() == query.lower()):
            cursor.insertText(replace);
            return True
        return False

    def replace_all(self, query, replace, flags) -> int:
        count = 0;
        self.text_area.moveCursor(QTextCursor.MoveOperation.Start)
        while self.text_area.find(query, flags): self.text_area.textCursor().insertText(replace); count += 1
        return count

    def update_editor_settings(self):
        font = QFont(settings_manager.get("font_family"), settings_manager.get("font_size"))
        self.text_area.setFont(font);
        self.line_number_area.setFont(font);
        self.breakpoint_area.setFont(font)
        # --- FIX: Use the text_area's font metrics for tab width calculation ---
        # This ensures the tab stop is calculated based on the actual font being used
        # in the editor, preventing potential miscalculations and rendering errors.
        self.text_area.setTabStopDistance(
            self.text_area.fontMetrics().horizontalAdvance(' ') * settings_manager.get("indent_width"))
        self.line_number_area.setVisible(settings_manager.get("show_line_numbers", True))
        self.update_theme()
        self._update_gutter_widths()

    def update_theme(self):
        colors = self.theme_manager.current_theme_data.get("colors", {})
        stylesheet = f"""QPlainTextEdit {{ background-color: {colors.get('editor.background', '#1e1e1e')}; color: {colors.get('editor.foreground', '#d4d4d4')}; border: none; selection-background-color: {colors.get('editor.selectionBackground', '#264f78')}; }}"""
        self.text_area.setStyleSheet(stylesheet)
        if self.highlighter: self.highlighter.rehighlight()
        self.breakpoint_area.update();
        self.line_number_area.update();
        self.highlight_current_line()
        # I also need to make sure the find panel gets the theme update!
        self.find_panel.update_theme()
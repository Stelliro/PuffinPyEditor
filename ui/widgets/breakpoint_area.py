# PuffinPyEditor/ui/widgets/breakpoint_area.py
from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QMouseEvent, QPainter, QColor
from PyQt6.QtCore import QSize, pyqtSignal, Qt

from utils.logger import log


class BreakpointArea(QWidget):
    """
    A gutter widget that displays and handles breakpoint toggling with a
    clear hover effect.
    """
    breakpoint_toggled = pyqtSignal(int)

    def __init__(self, editor_widget: 'EditorWidget'):
        super().__init__(editor_widget)
        self.editor = editor_widget
        self.setMouseTracking(True)
        self.hovered_line = -1

    def sizeHint(self) -> QSize:
        return QSize(self.minimumSizeHint().width(), 0)

    def minimumSizeHint(self) -> QSize:
        return QSize(20, 0)

    def enterEvent(self, event):
        self.update()  # Redraw to show potential hover
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.hovered_line = -1
        self.update()  # Redraw to remove hover
        super().leaveEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent):
        """Calculates which line number is under the cursor."""
        try:
            # Use the editor's cursorForPosition method, which is the most reliable way
            # to determine the block (line) at a specific y-coordinate.
            cursor = self.editor.text_area.cursorForPosition(event.pos())
            line_num = -1
            if cursor.block().isValid():
                line_num = cursor.block().blockNumber() + 1

            if line_num != self.hovered_line:
                self.hovered_line = line_num
                self.update()
        except Exception as e:
            log.error(f"Error in BreakpointArea mouseMoveEvent: {e}", exc_info=False)
        super().mouseMoveEvent(event)

    def mousePressEvent(self, event: QMouseEvent) -> None:
        """Toggles the breakpoint on the hovered line."""
        if event.button() == Qt.MouseButton.LeftButton and self.hovered_line != -1:
            self.breakpoint_toggled.emit(self.hovered_line)
        super().mousePressEvent(event)

    def paintEvent(self, event) -> None:
        """Paints the breakpoints and hover indicators."""
        try:
            painter = QPainter(self)
        except Exception as e:
            log.error(f"Could not create QPainter for breakpoints: {e}")
            return

        colors = self.editor.theme_manager.current_theme_data.get('colors', {})
        bg_color = QColor(colors.get('editorGutter.background', '#2c313a'))
        breakpoint_color = QColor(colors.get('editor.breakpoint.color', 'crimson'))

        # A more visible hover color
        hover_base_color = QColor(colors.get('editorGutter.foreground', '#888888'))
        hover_color = QColor(hover_base_color)
        hover_color.setAlpha(128)  # semi-transparent

        painter.fillRect(event.rect(), bg_color)

        # Get editor state
        text_area = self.editor.text_area
        content_offset = text_area.contentOffset()

        # Iterate through visible blocks to draw markers
        block = text_area.firstVisibleBlock()
        while block.isValid():
            block_top = text_area.blockBoundingGeometry(block).translated(content_offset).top()

            # Stop if we've drawn past the visible area
            if block_top > event.rect().bottom():
                break

            if block.isVisible():
                line_num = block.blockNumber() + 1
                radius = 5  # Larger radius for better visibility
                center_x = self.width() / 2
                # Center the dot vertically within the line's bounding rect
                center_y = block_top + (text_area.blockBoundingRect(block).height() / 2)

                painter.setPen(Qt.PenStyle.NoPen)

                if line_num in self.editor.breakpoints:
                    painter.setBrush(breakpoint_color)
                    painter.drawEllipse(int(center_x - radius), int(center_y - radius), int(radius * 2),
                                        int(radius * 2))
                elif line_num == self.hovered_line:
                    # Draw a hollow circle for the hover indicator
                    painter.setBrush(hover_color)
                    painter.drawEllipse(int(center_x - radius), int(center_y - radius), int(radius * 2),
                                        int(radius * 2))

            block = block.next()
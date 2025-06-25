# PuffinPyEditor/ui/widgets/breakpoint_area.py
from typing import Optional
from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QPainter, QColor, QCursor, QPaintEvent, QMouseEvent, QEnterEvent
from PyQt6.QtCore import Qt, QSize


class BreakpointArea(QWidget):
    """
    A QWidget that displays breakpoints and allows users to toggle them.
    It sits to the left of the line number area.
    """
    def __init__(self, editor: 'EditorWidget'):
        super().__init__(editor)
        self.editor_widget = editor
        self.hovered_line_number: int = -1
        self.setMouseTracking(True)

    def sizeHint(self) -> QSize:
        """Provides the default size for this widget."""
        return QSize(20, 0)

    def enterEvent(self, event: QEnterEvent):
        """Change cursor to a pointing hand when mouse enters."""
        self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        super().enterEvent(event)

    def leaveEvent(self, event: QEnterEvent):
        """Change cursor back and clear hover marker when mouse leaves."""
        self.unsetCursor()
        if self.hovered_line_number != -1:
            self.hovered_line_number = -1
            self.update()  # Trigger a repaint to remove the ghost marker
        super().leaveEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent):
        """Detect which line is being hovered over and trigger a repaint."""
        text_area = self.editor_widget.text_area
        cursor = text_area.cursorForPosition(event.pos())
        current_hovered_line = cursor.blockNumber() + 1

        if current_hovered_line != self.hovered_line_number:
            self.hovered_line_number = current_hovered_line
            self.update()  # Trigger a repaint to show/move the ghost marker
        super().mouseMoveEvent(event)

    def mousePressEvent(self, event: QMouseEvent):
        """Handle toggling breakpoints on a left-click."""
        if event.button() == Qt.MouseButton.LeftButton and self.hovered_line_number > 0:
            self.editor_widget.toggle_breakpoint(self.hovered_line_number)
        super().mousePressEvent(event)

    def paintEvent(self, event: QPaintEvent):
        """Paints the breakpoints and the hover marker."""
        painter = QPainter(self)
        colors = self.editor_widget.theme_manager.current_theme_data.get('colors', {})
        
        # Define colors from the theme
        bg_color = QColor(colors.get('editorGutter.background', '#f0f0f0'))
        breakpoint_color = QColor(colors.get('accent', '#ff0000'))
        hover_marker_color = QColor(breakpoint_color)
        hover_marker_color.setAlpha(90)  # Make it semi-transparent

        painter.fillRect(event.rect(), bg_color)

        text_area = self.editor_widget.text_area
        block = text_area.firstVisibleBlock()
        block_number = block.blockNumber()
        
        # Get geometry info once
        top = int(text_area.blockBoundingGeometry(block).translated(text_area.contentOffset()).top())
        bottom = top + int(text_area.blockBoundingRect(block).height())
        line_height = text_area.fontMetrics().height()
        circle_radius = 4
        y_offset = (line_height - circle_radius * 2) // 2

        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                line_num = block_number + 1
                center_x = self.width() // 2
                center_y = top + y_offset + circle_radius

                # Draw permanent breakpoint
                if line_num in self.editor_widget.breakpoints:
                    painter.setBrush(breakpoint_color)
                    painter.setPen(Qt.PenStyle.NoPen)
                    painter.drawEllipse(center_x - circle_radius, center_y - circle_radius,
                                        circle_radius * 2, circle_radius * 2)
                # Draw hover marker if it's this line and no breakpoint exists
                elif line_num == self.hovered_line_number:
                    painter.setBrush(hover_marker_color)
                    painter.setPen(Qt.PenStyle.NoPen)
                    painter.drawEllipse(center_x - circle_radius, center_y - circle_radius,
                                        circle_radius * 2, circle_radius * 2)

            block = block.next()
            if not block.isValid():
                break
            top = bottom
            bottom = top + int(text_area.blockBoundingRect(block).height())
            block_number += 1
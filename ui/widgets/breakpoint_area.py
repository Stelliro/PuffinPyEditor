# PuffinPyEditor/ui/widgets/breakpoint_area.py
from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QMouseEvent, QPainter, QColor
from PyQt6.QtCore import QSize, pyqtSignal, Qt


class BreakpointArea(QWidget):
    """A widget that displays and handles breakpoint toggling with a hover effect."""
    breakpoint_toggled = pyqtSignal(int)

    def __init__(self, editor_widget):
        super().__init__(editor_widget)
        self.editor_widget = editor_widget
        
        # [NEW] Enable mouse tracking to get hover events
        self.setMouseTracking(True)
        # [NEW] Variable to store the line number currently being hovered over
        self.hovered_line = -1

    def sizeHint(self) -> QSize:
        return QSize(self.minimumSizeHint().width(), 0)

    def minimumSizeHint(self) -> QSize:
        return QSize(20, 0)

    # [NEW] Track when the mouse enters the widget
    def enterEvent(self, event):
        self.update() # Trigger a repaint
        super().enterEvent(event)

    # [NEW] Clear hover state when the mouse leaves
    def leaveEvent(self, event):
        self.hovered_line = -1
        self.update()
        super().leaveEvent(event)

    # [NEW] Detect which line is being hovered over
    def mouseMoveEvent(self, event: QMouseEvent):
        text_area = self.editor_widget.text_area
        cursor = text_area.cursorForPosition(event.pos())
        line_num = cursor.block().blockNumber() + 1
        
        # If the hovered line has changed, update the state and trigger a repaint
        if line_num != self.hovered_line:
            self.hovered_line = line_num
            self.update()
        
        super().mouseMoveEvent(event)

    # [MODIFIED] paintEvent now includes logic to draw the hover indicator
    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        colors = self.editor_widget.theme_manager.current_theme_data['colors']
        
        # Define colors
        bg_color = QColor(colors.get('editorGutter.background', '#2c313a'))
        breakpoint_color = QColor(colors.get('editor.breakpoint.color', 'crimson'))
        hover_color = QColor(colors.get('editorGutter.foreground', '#888888'))
        hover_color.setAlpha(128) # Make it semi-transparent

        painter.fillRect(event.rect(), bg_color)
        
        text_area = self.editor_widget.text_area
        offset = text_area.contentOffset()
        block = text_area.firstVisibleBlock()
        
        while block.isValid() and block.isVisible():
            geom = text_area.blockBoundingGeometry(block).translated(offset)
            line_num = block.blockNumber() + 1
            
            radius = 4
            dot_x = self.width() // 2 - radius
            dot_y = int(geom.top() + (geom.height() - radius * 2) / 2)

            # --- Main Drawing Logic ---
            if line_num in self.editor_widget.breakpoints:
                # If there's a breakpoint, draw the solid red dot
                painter.setBrush(breakpoint_color)
                painter.setPen(Qt.PenStyle.NoPen)
                painter.drawEllipse(dot_x, dot_y, radius * 2, radius * 2)
            elif line_num == self.hovered_line:
                # Otherwise, if we are hovering here, draw the "ghost" dot
                painter.setBrush(hover_color)
                painter.setPen(Qt.PenStyle.NoPen)
                painter.drawEllipse(dot_x, dot_y, radius * 2, radius * 2)
            
            if geom.top() > self.height():
                break
            
            block = block.next()

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            # The hover line is always the correct line to toggle
            if self.hovered_line != -1:
                self.breakpoint_toggled.emit(self.hovered_line)
        super().mousePressEvent(event)
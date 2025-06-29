# PuffinPyEditor/ui/line_number_area.py
from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QPainter, QColor
from PyQt6.QtCore import QSize, Qt


class LineNumberArea(QWidget):
    """
    An interactive widget that displays line numbers with pixel-perfect alignment
    by querying the editor's text block geometry directly.
    """

    def __init__(self, editor_widget):
        super().__init__(editor_widget)
        self.editor_widget = editor_widget

    def sizeHint(self) -> QSize:
        """Determines the required width of the widget based on line count."""
        return QSize(self.editor_widget.line_number_area_width(), 0)

    def paintEvent(self, event) -> None:
        """
        Paints the line numbers with perfect alignment by using the exact
        geometry of the text blocks from the editor.
        """
        painter = QPainter(self)
        colors = self.editor_widget.theme_manager.current_theme_data['colors']
        text_area = self.editor_widget.text_area

        # 1. Fill the background
        bg_color = QColor(colors.get('editorGutter.background', '#2c313a'))
        painter.fillRect(event.rect(), bg_color)

        # 2. Get the geometry of the first visible line to start drawing
        block = text_area.firstVisibleBlock()
        block_number = block.blockNumber()
        offset = text_area.contentOffset()

        current_line = text_area.textCursor().blockNumber()

        # 3. Iterate through all visible blocks (lines)
        while block.isValid() and block.isVisible():
            # Get the exact geometry for this specific line
            geom = text_area.blockBoundingGeometry(block).translated(offset)

            # Check if this line is within the area that needs to be repainted
            if geom.bottom() >= event.rect().top() and geom.top() <= event.rect().bottom():
                number = str(block_number + 1)

                # Set color: bright for the current line, faded for others
                is_current = (block_number == current_line)
                pen_color_name = 'editorLineNumber.activeForeground' if is_current else 'editorLineNumber.foreground'
                pen_color = QColor(colors.get(pen_color_name, '#d0d0d0'))
                painter.setPen(pen_color)

                # 4. Draw the number using the block's exact geometry. This is the key.
                painter.drawText(
                    0,
                    int(geom.top()),
                    self.width() - 8,  # 8px right-side padding
                    int(geom.height()),
                    Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter,
                    number
                )

            # Stop drawing if we are past the visible viewport
            if geom.top() > self.height():
                break

            block = block.next()
            block_number += 1
# PuffinPyEditor/ui/line_number_area.py
from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QPainter, QColor, QFontMetrics
from PyQt6.QtCore import Qt, QSize
from utils.logger import log

class LineNumberArea(QWidget):
    def __init__(self, editor):
        super().__init__(editor)
        self.editor_widget = editor

    def sizeHint(self) -> QSize:
        return QSize(self.editor_widget.line_number_area_width(), 0)

    def paintEvent(self, event) -> None:
        self.editor_widget.line_number_area_paint_event(event)
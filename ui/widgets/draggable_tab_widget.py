# PuffinPyEditor/ui/widgets/draggable_tab_widget.py [MODIFIED]
import os
from PyQt6.QtWidgets import (QTabWidget, QTabBar, QMainWindow, QWidget,
                             QApplication)
from PyQt6.QtCore import Qt, pyqtSignal, QPoint, QMimeData, QByteArray
from PyQt6.QtGui import QMouseEvent, QDrag
from utils.logger import log

# Custom MIME type to identify our widget drags
WIDGET_REFERENCE_MIME_TYPE = "application/x-puffin-widget-reference"


class FloatingTabWindow(QMainWindow):
    """A QMainWindow to host a detached tab. It now knows how to be dragged."""

    def __init__(self, main_window_ref, widget, tab_text, tooltip_text, icon):
        super().__init__()
        self.main_window_ref = main_window_ref
        self.hosted_widget = widget
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)

        self.setWindowTitle(f"{tab_text} - PuffinPyEditor")
        self.setCentralWidget(self.hosted_widget)
        if icon:
            self.setWindowIcon(icon)

        self.resize(800, 600)
        self.setToolTip(tooltip_text)
        self.drag_start_pos = None

    def closeEvent(self, event):
        self.main_window_ref._close_widget_safely(self.hosted_widget, event)

    def mousePressEvent(self, event: QMouseEvent):
        # We start a drag if the left button is pressed on the window frame (title bar).
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_start_pos = event.globalPosition().toPoint()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent):
        if not (event.buttons() & Qt.MouseButton.LeftButton) or not self.drag_start_pos:
            return super().mouseMoveEvent(event)

        # Check if the mouse has moved far enough to be considered a drag
        if (
                event.globalPosition().toPoint() - self.drag_start_pos).manhattanLength() < QApplication.startDragDistance():
            return super().mouseMoveEvent(event)

        log.info(f"Initiating drag for widget ID: {id(self.hosted_widget)}")
        drag = QDrag(self)
        mime_data = QMimeData()
        widget_id_bytes = QByteArray(str(id(self.hosted_widget)).encode())
        mime_data.setData(WIDGET_REFERENCE_MIME_TYPE, widget_id_bytes)
        drag.setMimeData(mime_data)

        # Hide the window while dragging. If the drag is cancelled, we'll show it again.
        self.hide()

        # The exec() call blocks until the drag is finished.
        result = drag.exec(Qt.DropAction.MoveAction)

        if result == Qt.DropAction.IgnoreAction:
            # Drop was cancelled or unsuccessful, show the window again.
            log.debug("Tab drag cancelled, showing floating window again.")
            self.show()

        self.drag_start_pos = None


class DraggableTabBar(QTabBar):
    """A QTabBar that detects dragging out and accepts drops from floating windows."""
    tab_dragged_out = pyqtSignal(int, QPoint)
    tab_reinserted = pyqtSignal(QWidget, int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.drag_start_pos = None
        self.setAcceptDrops(True)

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_start_pos = event.pos()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent):
        if not (event.buttons() & Qt.MouseButton.LeftButton) or self.drag_start_pos is None:
            return super().mouseMoveEvent(event)

        if (event.pos() - self.drag_start_pos).manhattanLength() < QApplication.startDragDistance():
            return super().mouseMoveEvent(event)

        # If drag moves outside the tab bar, initiate a drag-out
        if not self.rect().contains(event.pos()):
            tab_index = self.tabAt(self.drag_start_pos)
            if tab_index > -1:
                self.tab_dragged_out.emit(tab_index, event.globalPosition().toPoint())
                self.drag_start_pos = None

    def dragEnterEvent(self, event):
        if event.mimeData().hasFormat(WIDGET_REFERENCE_MIME_TYPE):
            event.acceptProposedAction()
        else:
            super().dragEnterEvent(event)

    def dropEvent(self, event):
        if not event.mimeData().hasFormat(WIDGET_REFERENCE_MIME_TYPE):
            return super().dropEvent(event)

        widget_id_bytes = event.mimeData().data(WIDGET_REFERENCE_MIME_TYPE)
        widget_id_str = widget_id_bytes.data().decode()

        # Find the widget instance from the main window's tracking dict
        main_window = self.parentWidget().main_window_ref
        widget_to_reinsert = None
        for widget, data in main_window.editor_tabs_data.items():
            if str(id(widget)) == widget_id_str:
                widget_to_reinsert = widget
                break

        if widget_to_reinsert:
            drop_index = self.tabAt(event.position().toPoint())
            log.info(f"Dropping widget ID {widget_id_str} at tab index {drop_index}")
            self.tab_reinserted.emit(widget_to_reinsert, drop_index)
            event.acceptProposedAction()
        else:
            log.warning(f"Could not find widget with ID {widget_id_str} to re-insert.")
            event.ignore()


class DraggableTabWidget(QTabWidget):
    """A QTabWidget that uses a DraggableTabBar to allow detaching and re-attaching tabs."""

    def __init__(self, main_window_ref, parent=None):
        super().__init__(parent)
        self.main_window_ref = main_window_ref
        tab_bar = DraggableTabBar(self)
        self.setTabBar(tab_bar)
        tab_bar.tab_dragged_out.connect(self._handle_tab_drag_out)
        tab_bar.tab_reinserted.connect(self._handle_tab_reinsert)

    def _handle_tab_drag_out(self, index: int, global_pos: QPoint):
        log.info(f"Detaching tab at index {index}.")
        widget = self.widget(index)
        widget_data = self.main_window_ref.editor_tabs_data.get(widget)
        if not widget or not widget_data:
            log.warning("Could not detach tab: widget or its data not found.")
            return

        tab_text, tooltip, icon = self.tabText(index), self.tabToolTip(index), self.tabIcon(index)
        self.removeTab(index)

        floating_window = FloatingTabWindow(self.main_window_ref, widget, tab_text, tooltip, icon)
        floating_window.move(global_pos)
        floating_window.show()

    def _handle_tab_reinsert(self, widget: QWidget, index: int):
        log.info(f"Re-inserting widget into tab bar at index: {index}")
        floating_window = widget.window()
        if not isinstance(floating_window, FloatingTabWindow):
            return

        widget_data = self.main_window_ref.editor_tabs_data.get(widget, {})
        tab_text = os.path.basename(widget_data.get('filepath')) if widget_data.get('filepath') else "Untitled"
        tooltip = widget_data.get('filepath', "Unsaved file")
        icon = floating_window.windowIcon()

        widget.setParent(self)

        if index < 0:
            index = self.count()

        self.insertTab(index, widget, icon, tab_text)
        self.setTabToolTip(index, tooltip)
        self.setCurrentWidget(widget)

        floating_window.setCentralWidget(None)
        floating_window.close()
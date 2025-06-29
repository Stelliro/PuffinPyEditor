# PuffinPyEditor/plugins/tab_drag_handler/draggable_tab_widget.py
from PyQt6.QtWidgets import (QTabWidget, QTabBar, QMainWindow, QWidget,
                             QApplication)
from PyQt6.QtCore import Qt, pyqtSignal, QPoint, QMimeData, QByteArray
from PyQt6.QtGui import QMouseEvent, QDrag
from utils.logger import log

# [NEW] Define a custom MIME type to identify our widget drags
WIDGET_REFERENCE_MIME_TYPE = "application/x-puffin-widget-reference"


class FloatingTabWindow(QMainWindow):
    """
    A QMainWindow to host a detached tab. It now knows how to be dragged.
    """
    def __init__(self, main_window_ref, widget, tab_text, tooltip_text, icon):
        super().__init__()
        self.main_window_ref = main_window_ref
        self.hosted_widget = widget

        self.setWindowTitle(f"{tab_text} - PuffinPyEditor")
        self.setCentralWidget(self.hosted_widget)
        if icon:
            self.setWindowIcon(icon)

        self.resize(800, 600)
        self.setToolTip(tooltip_text)

        # [NEW] Attribute to handle starting a drag operation
        self.drag_start_pos = None

    # [MODIFIED] closeEvent now delegates to the main window's generic closer
    def closeEvent(self, event):
        self.main_window_ref._close_widget_safely(self.hosted_widget, event)

    # [NEW] mousePressEvent to initiate a potential drag
    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            # We only start a drag if the click is on the window frame (title bar)
            # A simple way to approximate this is to check if the click is outside
            # the bounds of the central widget.
            if not self.centralWidget().geometry().contains(event.pos()):
                self.drag_start_pos = event.pos()
        super().mousePressEvent(event)

    # [NEW] mouseMoveEvent to perform the drag
    def mouseMoveEvent(self, event: QMouseEvent):
        if not (event.buttons() & Qt.MouseButton.LeftButton) or not self.drag_start_pos:
            return super().mouseMoveEvent(event)

        manhattan_len = (event.pos() - self.drag_start_pos).manhattanLength()
        if manhattan_len < QApplication.startDragDistance():
            return super().mouseMoveEvent(event)

        log.info(f"Initiating drag for widget ID: {id(self.hosted_widget)}")
        drag = QDrag(self)
        mime_data = QMimeData()

        # Create a reference to the widget using its memory ID. This is how
        # the receiving tab bar will know which widget is being dragged.
        widget_id_bytes = QByteArray(str(id(self.hosted_widget)).encode())
        mime_data.setData(WIDGET_REFERENCE_MIME_TYPE, widget_id_bytes)
        drag.setMimeData(mime_data)

        # The drag has started, hide the window. If the drag is cancelled,
        # we'll show it again.
        self.hide()
        # The 'exec()' call blocks until the drag is finished (dropped or cancelled).
        if drag.exec(Qt.DropAction.MoveAction) == Qt.DropAction.IgnoreAction:
            # If the drop was cancelled (or unsuccessful), show the window again.
            log.debug("Tab drag cancelled, showing floating window again.")
            self.show()

        self.drag_start_pos = None


class DraggableTabBar(QTabBar):
    """
    A QTabBar that detects dragging out and now also accepts drops from
    floating windows.
    """
    tab_dragged_out = pyqtSignal(int, QPoint)
    # [NEW] Signal to re-insert a dropped widget. We pass a widget reference.
    tab_reinserted = pyqtSignal(QWidget, int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.drag_start_pos = None
        self.setAcceptDrops(True)  # [MODIFIED] Explicitly accept drops

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_start_pos = event.pos()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent):
        if not (event.buttons() & Qt.MouseButton.LeftButton) or self.drag_start_pos is None:
            return super().mouseMoveEvent(event)

        manhattan_len = (event.pos() - self.drag_start_pos).manhattanLength()
        if manhattan_len < QApplication.startDragDistance():
            return super().mouseMoveEvent(event)

        if self.rect().contains(event.pos()):
            return super().mouseMoveEvent(event)

        tab_index = self.tabAt(self.drag_start_pos)
        if tab_index > -1:
            self.tab_dragged_out.emit(tab_index, event.globalPosition().toPoint())
            self.drag_start_pos = None

    # [NEW] dragEnterEvent to check if we can accept the drop
    def dragEnterEvent(self, event):
        if event.mimeData().hasFormat(WIDGET_REFERENCE_MIME_TYPE):
            event.acceptProposedAction()
        else:
            super().dragEnterEvent(event)

    # [NEW] dropEvent to handle the actual re-insertion
    def dropEvent(self, event):
        if not event.mimeData().hasFormat(WIDGET_REFERENCE_MIME_TYPE):
            return super().dropEvent(event)

        # Get the widget ID from the drag's MIME data
        widget_id_bytes = event.mimeData().data(WIDGET_REFERENCE_MIME_TYPE)
        widget_id_str = widget_id_bytes.data().decode()

        # Find the actual widget instance from the main window's tracking dict
        main_window = self.parentWidget().main_window_ref
        widget_to_reinsert = None
        for widget, data in main_window.editor_tabs_data.items():
            if str(id(widget)) == widget_id_str:
                widget_to_reinsert = widget
                break

        if widget_to_reinsert:
            # Determine the insertion index based on drop position
            drop_index = self.tabAt(event.position().toPoint())
            log.info(f"Dropping widget ID {widget_id_str} at tab index {drop_index}")

            # Emit signal for the parent TabWidget to handle the logic
            self.tab_reinserted.emit(widget_to_reinsert, drop_index)
            event.acceptProposedAction()
        else:
            log.warning(f"Could not find widget with ID {widget_id_str} to re-insert.")
            event.ignore()


class DraggableTabWidget(QTabWidget):
    """
    A QTabWidget that uses a DraggableTabBar to allow detaching and
    re-attaching tabs.
    """
    def __init__(self, main_window_ref, parent=None):
        super().__init__(parent)
        self.main_window_ref = main_window_ref
        
        tab_bar = DraggableTabBar(self)
        self.setTabBar(tab_bar)

        tab_bar.tab_dragged_out.connect(self._handle_tab_drag_out)
        # [NEW] Connect the re-insertion signal
        tab_bar.tab_reinserted.connect(self._handle_tab_reinsert)

    def _handle_tab_drag_out(self, index: int, global_pos: QPoint):
        log.info(f"Detaching tab at index {index}.")

        widget = self.widget(index)
        widget_data = self.main_window_ref.editor_tabs_data.get(widget)
        if not widget or not widget_data:
            log.warning("Could not detach tab: widget or its data not found.")
            return

        # Preserve info before removing the tab
        tab_text = self.tabText(index)
        tooltip = self.tabToolTip(index)
        icon = self.tabIcon(index)
        
        self.removeTab(index)
        
        floating_window = FloatingTabWindow(
            self.main_window_ref, widget, tab_text, tooltip, icon
        )
        floating_window.move(global_pos)
        floating_window.show()

    def _handle_tab_reinsert(self, widget: QWidget, index: int):
        """Re-integrates a widget from a floating window back into this tab bar."""
        log.info(f"Re-inserting widget into tab bar at index: {index}")

        # Find the floating window that holds this widget
        floating_window = widget.window()
        if not isinstance(floating_window, FloatingTabWindow):
            log.error("Re-insert failed: could not find floating parent window.")
            # If something went wrong, ensure the hidden window is shown again.
            if floating_window and hasattr(floating_window, "show"):
                floating_window.show()
            return
            
        widget_data = self.main_window_ref.editor_tabs_data.get(widget, {})
        
        # Prepare for re-insertion
        tab_text = os.path.basename(widget_data.get('filepath')) if widget_data.get('filepath') else "Untitled"
        tooltip = widget_data.get('filepath', "Unsaved file")
        icon = floating_window.windowIcon()
        
        # Reparent the widget back to the tab widget before inserting
        widget.setParent(self)

        if index < 0:  # If dropped on an empty area, append to the end
            index = self.count()

        # Insert tab, set tooltip, and make it active
        self.insertTab(index, widget, icon, tab_text)
        self.setTabToolTip(index, tooltip)
        self.setCurrentWidget(widget)
        
        # Cleanly close the now-empty floating window.
        # Set its central widget to None to prevent it from being
        # garbage-collected with the window.
        floating_window.setCentralWidget(None)
        floating_window.close()
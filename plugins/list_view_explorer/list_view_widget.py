# PuffinPyEditor/plugins/list_view_explorer/list_view_widget.py
import os
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QTreeWidget, QTreeWidgetItem, QInputDialog, QMessageBox,
                             QProxyStyle, QStyle, QApplication, QAbstractItemView)
from PyQt6.QtGui import QPainter, QColor, QPolygonF, QPen, QDrag, QKeyEvent
from PyQt6.QtCore import Qt, QFileInfo, QPointF, QMimeData
import qtawesome as qta

from app_core.puffin_api import PuffinPluginAPI
from utils.logger import log
from .icon_provider import CustomFileIconProvider
from .context_menu import show_project_context_menu

TREE_ITEM_MIME_TYPE = "application/x-puffin-tree-item"


class CustomTreeStyle(QProxyStyle):
    def drawPrimitive(self, element, option, painter, widget=None):
        if element == QStyle.PrimitiveElement.PE_IndicatorBranch:
            # THE FIX: Save the painter's state to prevent leaks.
            painter.save()

            painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

            original_pen = painter.pen()
            if hasattr(widget, 'theme_manager'):
                colors = widget.theme_manager.current_theme_data.get('colors', {})
                line_color = QColor(colors.get('accent', '#5f6c6d'))
                original_pen.setColor(line_color)

            painter.setPen(original_pen)

            r = option.rect
            mid_x = r.x() + r.width() / 2
            mid_y = r.y() + r.height() / 2

            if option.state & QStyle.StateFlag.State_Sibling:
                painter.drawLine(int(mid_x), r.top(), int(mid_x), r.bottom())
            else:
                painter.drawLine(int(mid_x), r.top(), int(mid_x), int(mid_y))

            if option.state & QStyle.StateFlag.State_Item:
                is_folder = bool(option.state & QStyle.StateFlag.State_Children)
                branch_pen = QPen(original_pen)

                if is_folder:
                    branch_pen.setWidth(2)
                else:
                    branch_pen.setWidth(1)
                painter.setPen(branch_pen)

                offset = 4
                painter.drawLine(QPointF(mid_x, mid_y - offset), QPointF(r.right(), mid_y))

                painter.setPen(original_pen)

                if is_folder:
                    indicator_size = 3.5
                    pen_width = 1.5
                    indicator_pen = QPen(original_pen)
                    indicator_pen.setWidthF(pen_width)
                    indicator_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
                    painter.setPen(indicator_pen)

                    if option.state & QStyle.StateFlag.State_Open:
                        painter.drawLine(QPointF(mid_x - indicator_size, mid_y - indicator_size / 2),
                                         QPointF(mid_x, mid_y + indicator_size / 2))
                        painter.drawLine(QPointF(mid_x, mid_y + indicator_size / 2),
                                         QPointF(mid_x + indicator_size, mid_y - indicator_size / 2))
                    else:
                        painter.drawLine(QPointF(mid_x - indicator_size / 2, mid_y - indicator_size),
                                         QPointF(mid_x + indicator_size / 2, mid_y))
                        painter.drawLine(QPointF(mid_x + indicator_size / 2, mid_y),
                                         QPointF(mid_x - indicator_size / 2, mid_y + indicator_size))

            # THE FIX: Restore the painter's state to prevent side effects.
            painter.restore()
            return

        super().drawPrimitive(element, option, painter, widget)


class StyledTreeView(QTreeWidget):
    def __init__(self, puffin_api, parent_view, parent=None):
        super().__init__(parent)
        self.puffin_api = puffin_api
        self.parent_view = parent_view
        self.theme_manager = puffin_api.get_manager("theme")
        self.file_handler = puffin_api.get_manager("file_handler")
        self.setStyle(CustomTreeStyle(self.style()))

        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.setDropIndicatorShown(True)
        self.setDragDropMode(QAbstractItemView.DragDropMode.InternalMove)

        # To manage highlighting the item being dragged over
        self.drag_over_item = None

    def startDrag(self, supportedActions):
        item = self.currentItem()
        if not item: return

        path = item.data(0, Qt.ItemDataRole.UserRole).get('path')
        if not path: return

        mime_data = QMimeData()
        mime_data.setData(TREE_ITEM_MIME_TYPE, path.encode('utf-8'))

        drag = QDrag(self)
        drag.setMimeData(mime_data)
        drag.exec(Qt.DropAction.MoveAction)

    def dragEnterEvent(self, event):
        if event.mimeData().hasFormat(TREE_ITEM_MIME_TYPE):
            event.acceptProposedAction()
        else:
            super().dragEnterEvent(event)

    def dragMoveEvent(self, event):
        # Reset background of the previously hovered item
        if self.drag_over_item:
            self.drag_over_item.setBackground(0, QColor(Qt.GlobalColor.transparent))
            self.drag_over_item = None

        item = self.itemAt(event.position().toPoint())

        # Check if the drop target is a valid directory
        if item and item.data(0, Qt.ItemDataRole.UserRole).get('is_dir'):
            if not event.mimeData().hasFormat(TREE_ITEM_MIME_TYPE):
                event.ignore()
                return

            source_path = event.mimeData().data(TREE_ITEM_MIME_TYPE).data().decode('utf-8')
            target_path = item.data(0, Qt.ItemDataRole.UserRole).get('path')

            # Prevent dropping on itself or into its own children
            is_invalid_move = (os.path.normpath(source_path) == os.path.normpath(target_path) or
                               (os.path.isdir(source_path) and
                                os.path.normpath(target_path).startswith(os.path.normpath(source_path) + os.sep)))

            if not is_invalid_move:
                self.drag_over_item = item
                colors = self.theme_manager.current_theme_data.get('colors', {})
                selection_color = QColor(colors.get('editor.selectionBackground', '#264f78'))
                selection_color.setAlpha(128)  # Make it semi-transparent
                self.drag_over_item.setBackground(0, selection_color)

        event.acceptProposedAction()

    def dragLeaveEvent(self, event):
        if self.drag_over_item:
            self.drag_over_item.setBackground(0, QColor(Qt.GlobalColor.transparent))
            self.drag_over_item = None
        super().dragLeaveEvent(event)

    def dropEvent(self, event):
        # Clear any drop-target highlighting
        if self.drag_over_item:
            self.drag_over_item.setBackground(0, QColor(Qt.GlobalColor.transparent))
            self.drag_over_item = None

        source_path = event.mimeData().data(TREE_ITEM_MIME_TYPE).data().decode('utf-8')

        target_item = self.itemAt(event.position().toPoint())
        if not target_item:
            event.ignore()
            return

        target_data = target_item.data(0, Qt.ItemDataRole.UserRole)
        target_path = target_data.get('path')
        dest_dir = target_path if target_data.get('is_dir') else os.path.dirname(target_path)

        if not source_path or not dest_dir: event.ignore(); return
        if os.path.normpath(source_path) == os.path.normpath(dest_dir): event.ignore(); return
        if os.path.isdir(source_path) and dest_dir.startswith(os.path.normpath(source_path)):
            QMessageBox.warning(self, "Invalid Move", "Cannot move a folder into itself or a subfolder.")
            event.ignore();
            return

        success, result_msg = self.file_handler.move_item(source_path, dest_dir)
        if success:
            log.info(f"Successfully moved '{source_path}' to '{dest_dir}'")
            self.parent_view.refresh()
        else:
            QMessageBox.critical(self, "Move Failed", result_msg)

        event.acceptProposedAction()

    def keyPressEvent(self, event: QKeyEvent):
        """Handle key presses, specifically the Delete key."""
        if event.key() == Qt.Key.Key_Delete:
            if item := self.currentItem():
                if data := item.data(0, Qt.ItemDataRole.UserRole):
                    if path := data.get('path'):
                        # Call the parent's delete action method
                        self.parent_view._action_delete(path)
                        event.accept()
                        return
        super().keyPressEvent(event)


class FileSystemListView(QWidget):
    def __init__(self, puffin_api: PuffinPluginAPI, parent: None = None):
        super().__init__(parent)
        self.api = puffin_api

        self.project_manager = self.api.get_manager("project")
        self.file_handler = self.api.get_manager("file_handler")
        self.icon_provider = CustomFileIconProvider(self.api)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.tree_widget = StyledTreeView(self.api, self)

        self.tree_widget.setHeaderHidden(True)
        self.tree_widget.setAlternatingRowColors(True)
        self.tree_widget.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.tree_widget.setIndentation(15)
        layout.addWidget(self.tree_widget)

        self.tree_widget.itemExpanded.connect(self.on_item_expanded)
        self.tree_widget.itemCollapsed.connect(self.on_item_collapsed)
        self.tree_widget.itemClicked.connect(self.on_item_clicked)
        self.tree_widget.itemDoubleClicked.connect(self.on_item_double_clicked)
        self.tree_widget.customContextMenuRequested.connect(self.show_context_menu)
        QApplication.instance().focusChanged.connect(self._handle_focus_change)

    def _handle_focus_change(self, old_widget, new_widget):
        if not self.tree_widget.isAncestorOf(new_widget) and new_widget != self.tree_widget:
            self.tree_widget.clearSelection()

    def on_item_clicked(self, item, column):
        data = item.data(0, Qt.ItemDataRole.UserRole)
        if data and data.get('is_dir'):
            item.setExpanded(not item.isExpanded())

    def on_item_double_clicked(self, item, column):
        data = item.data(0, Qt.ItemDataRole.UserRole)
        if not data or data.get('is_dir'): return

        path = data.get('path')
        if path:
            self.api.get_main_window()._action_open_file(path)

    # MODIFIED: Refresh now preserves the expansion state.
    def refresh(self):
        """Intelligently refreshes the tree, preserving expansion state."""
        expanded_paths = set()
        for i in range(self.tree_widget.topLevelItemCount()):
            self._get_expanded_children(self.tree_widget.topLevelItem(i), expanded_paths)

        self.tree_widget.clear()

        open_projects = self.project_manager.get_open_projects()
        if not open_projects:
            return

        for project_path in open_projects:
            project_name = os.path.basename(project_path)
            root_item = QTreeWidgetItem(self.tree_widget)
            root_item.setText(0, project_name)
            root_item.setToolTip(0, project_path)
            root_item.setIcon(0, qta.icon('fa5s.folder-open',
                                          color=self.api.get_manager("theme").current_theme_data.get('colors', {}).get(
                                              'accent')))
            root_item.setData(0, Qt.ItemDataRole.UserRole, {'path': project_path, 'is_dir': True, 'is_root': True})
            root_item.addChild(QTreeWidgetItem())  # Dummy for expander

        self._set_expanded_children(self.tree_widget.invisibleRootItem(), expanded_paths)

    def _get_expanded_children(self, item, expanded_set):
        """Recursively finds all expanded items and adds their paths to a set."""
        if item.isExpanded():
            path = item.data(0, Qt.ItemDataRole.UserRole).get('path')
            if path:
                expanded_set.add(path)
            for i in range(item.childCount()):
                self._get_expanded_children(item.child(i), expanded_set)

    def _set_expanded_children(self, parent_item, expanded_set):
        """Recursively expands items if their path is in the provided set."""
        for i in range(parent_item.childCount()):
            child = parent_item.child(i)
            path = child.data(0, Qt.ItemDataRole.UserRole).get('path')
            if path in expanded_set:
                child.setExpanded(True)
                # This ensures sub-folders are populated if they were previously expanded
                self.on_item_expanded(child)

    # NEW: Smartly inserts a new item without a full, jarring refresh.
    def _update_tree_with_new_item(self, full_path: str):
        """Inserts a new item into the tree without a full refresh."""
        parent_dir = os.path.dirname(full_path)

        search_root = self.tree_widget.invisibleRootItem()
        parent_item = self._find_item_by_path(search_root, parent_dir)

        if not parent_item:
            self.refresh();
            return

        parent_item.setExpanded(True)
        self._populate_node(parent_item, parent_dir)

        newly_created_item = self._find_item_by_path(parent_item, full_path)
        if newly_created_item:
            self.tree_widget.setCurrentItem(newly_created_item)

    def _find_item_by_path(self, parent_item, path_to_find):
        for i in range(parent_item.childCount()):
            child = parent_item.child(i)
            child_data = child.data(0, Qt.ItemDataRole.UserRole)
            if not child_data: continue

            child_path = child_data.get('path')
            if child_path and os.path.normpath(child_path) == os.path.normpath(path_to_find):
                return child

            if child.isExpanded():
                found = self._find_item_by_path(child, path_to_find)
                if found:
                    return found
        return None

    def _populate_node(self, parent_item, path):
        if not os.path.isdir(path): return

        parent_item.takeChildren()

        try:
            entries = sorted(os.scandir(path), key=lambda e: (not e.is_dir(), e.name.lower()))
            for entry in entries:
                if entry.name.startswith(('.', '__')): continue

                item = QTreeWidgetItem(parent_item)
                item.setText(0, entry.name)
                item.setIcon(0, self.icon_provider.icon(QFileInfo(entry.path)))
                item.setData(0, Qt.ItemDataRole.UserRole, {'path': entry.path, 'is_dir': entry.is_dir()})

                if entry.is_dir():
                    item.addChild(QTreeWidgetItem())
        except OSError as e:
            log.warning(f"Could not scan directory: {path} - {e}")

    def on_item_expanded(self, item):
        path = item.data(0, Qt.ItemDataRole.UserRole).get('path')
        if path and item.childCount() == 1 and not item.child(0).text(0):
            self._populate_node(item, path)

    def on_item_collapsed(self, item):
        if not item.data(0, Qt.ItemDataRole.UserRole).get('is_root', False):
            item.takeChildren()
            item.addChild(QTreeWidgetItem())

    def show_context_menu(self, position):
        item = self.tree_widget.itemAt(position)
        if not item: return

        data = item.data(0, Qt.ItemDataRole.UserRole)
        path = data.get('path')
        is_dir = data.get('is_dir')
        if path:
            show_project_context_menu(self, position, path, is_dir)

    def _action_new_file(self, target_dir: str):
        file_name, ok = QInputDialog.getText(self, "New File", "Enter file name:")
        if ok and file_name:
            full_path = os.path.join(target_dir, file_name)
            success, message = self.file_handler.create_file(full_path)
            if not success:
                QMessageBox.warning(self, "Error", message)
            else:
                self._update_tree_with_new_item(full_path)

    def _action_new_folder(self, target_dir: str):
        folder_name, ok = QInputDialog.getText(self, "New Folder", "Enter folder name:")
        if ok and folder_name:
            full_path = os.path.join(target_dir, folder_name)
            success, message = self.file_handler.create_folder(full_path)
            if not success:
                QMessageBox.warning(self, "Error", message)
            else:
                self._update_tree_with_new_item(full_path)

    def _action_rename(self, old_path: str):
        """Handles renaming a file or folder."""
        item_name = os.path.basename(old_path)
        new_name, ok = QInputDialog.getText(self, f"Rename '{item_name}'", "New name:", text=item_name)
        if ok and new_name:
            success, result_or_msg = self.file_handler.rename_item(old_path, new_name)
            if success:
                self.refresh()
            else:
                QMessageBox.critical(self, "Rename Failed", result_or_msg)

    def _action_delete(self, path_to_delete: str):
        """Shows a confirmation and deletes the selected file or folder."""
        if not path_to_delete:
            return

        item_name = os.path.basename(path_to_delete)
        is_dir = os.path.isdir(path_to_delete)
        item_type = "folder" if is_dir else "file"

        warning_message = f"Are you sure you want to permanently delete this {item_type}?\n\n'{item_name}'"

        try:
            if is_dir and os.listdir(path_to_delete):
                warning_message += "\n\n<b>Warning: The folder is not empty.</b>"
        except OSError:
            pass  # Ignore if we can't list dir contents

        reply = QMessageBox.question(
            self, f"Confirm Delete", warning_message,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            success, message = self.file_handler.delete_item(path_to_delete)
            if success:
                self.refresh()
            else:
                QMessageBox.critical(self, "Deletion Failed", message)

    def _action_duplicate(self, path: str):
        """Handles duplicating a file or folder."""
        item_name = os.path.basename(path)
        reply = QMessageBox.question(
            self, "Confirm Duplicate",
            f"Create a copy of '{item_name}' in the same directory?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            success, message = self.file_handler.duplicate_item(path)
            if success:
                self.refresh()
            else:
                QMessageBox.critical(self, "Duplicate Failed", message)
# PuffinPyEditor/ui/explorer/list_view_widget.py
import os
import sys
from typing import List, Optional
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QTreeWidget, QTreeWidgetItem, QInputDialog, QMessageBox,
                             QProxyStyle, QStyle, QApplication, QAbstractItemView, QToolButton,
                             QHBoxLayout, QTreeWidgetItemIterator, QHeaderView, QFrame)
from PyQt6.QtGui import (QPainter, QColor, QPen, QDrag, QKeyEvent, QIcon, QPaintEvent, QDragEnterEvent, QDropEvent,
                         QDragMoveEvent, QMouseEvent, QAction)
from PyQt6.QtCore import (Qt, QFileInfo, QMimeData, QRect, QFileSystemWatcher, QTimer, QPoint, QPointF,
                          QUrl, QItemSelection, QItemSelectionModel) # Corrected: QItemSelectionModel moved here
from functools import partial
import qtawesome as qta

from app_core.puffin_api import PuffinPluginAPI
from utils.logger import log
from app_core.settings_manager import settings_manager
from ..explorer.icon_provider import CustomFileIconProvider
from ..explorer.context_menu import show_project_context_menu
from ..explorer.helpers import get_git_statuses_for_root

TREE_ITEM_MIME_TYPE = "application/x-puffin-tree-item"


class NoDrawProxyStyle(QProxyStyle):
    """A proxy style to prevent drawing the default expand/collapse arrows."""

    def drawPrimitive(self, element: QStyle.PrimitiveElement, option, painter, widget=None):
        if element == QStyle.PrimitiveElement.PE_IndicatorBranch:
            return
        super().drawPrimitive(element, option, painter, widget)


class StyledTreeView(QTreeWidget):
    """A QTreeWidget with custom branch and indentation guide painting."""

    def __init__(self, puffin_api: PuffinPluginAPI, parent_view: 'FileSystemListView', parent: QWidget = None):
        super().__init__(parent)
        self.puffin_api = puffin_api
        self.parent_view = parent_view
        self.theme_manager = puffin_api.get_manager("theme")
        self.file_handler = puffin_api.get_manager("file_handler")

        self.setStyle(NoDrawProxyStyle(self.style()))
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.setDropIndicatorShown(True)
        self.setDragDropMode(QAbstractItemView.DragDropMode.DragDrop)
        self.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.setExpandsOnDoubleClick(False)


    def supportedDropActions(self) -> Qt.DropAction:
        return Qt.DropAction.CopyAction | Qt.DropAction.MoveAction

    def mimeData(self, items: List[QTreeWidgetItem]) -> Optional[QMimeData]:
        if not items:
            return None

        if len(items) > 1:
            return None

        item = items[0]
        data = item.data(0, Qt.ItemDataRole.UserRole)
        path = data.get('path') if data else None
        if not path:
            return None

        mime = QMimeData()
        mime.setData(TREE_ITEM_MIME_TYPE, path.encode('utf-8'))
        mime.setUrls([QUrl.fromLocalFile(path)])
        return mime

    def paintEvent(self, event: QPaintEvent):
        super().paintEvent(event)
        if self.topLevelItemCount() == 0:
            return

        painter = QPainter(self.viewport())
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        colors = self.theme_manager.current_theme_data.get('colors', {})
        pen = QPen(QColor(colors.get('accent', '#83c092')), 1)
        painter.setPen(pen)
        painter.drawLine(8, 0, 8, self.viewport().height())

    def drawBranches(self, painter: QPainter, rect: QRect, index: 'QModelIndex'):
        item = self.itemFromIndex(index)
        if not item or not item.parent() or item.parent() == self.invisibleRootItem():
            return

        colors = self.theme_manager.current_theme_data.get('colors', {})
        accent_color = QColor(colors.get('accent', '#83c092'))
        indent = self.indentation()
        half_indent = indent / 2.0
        ROOT_ITEM_OFFSET = 14

        painter.save()
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        depth = -1
        temp_item = item
        while temp_item.parent() and temp_item.parent() != self.invisibleRootItem():
            depth += 1
            temp_item = temp_item.parent()

        if depth < 0:
            painter.restore()
            return

        painter.setPen(QPen(accent_color, 1))
        for i in range(depth):
            ancestor = item
            for _ in range(depth - i):
                ancestor = ancestor.parent()
            if ancestor.parent() and ancestor.parent().indexOfChild(ancestor) < ancestor.parent().childCount() - 1:
                line_x = ROOT_ITEM_OFFSET + (i * indent) + half_indent
                painter.drawLine(QPointF(line_x, rect.top()), QPointF(line_x, rect.bottom()))

        item_is_folder = item.childCount() > 0 or (item.childCount() == 1 and not item.child(0).text(0))
        item_is_last_child = item.parent().indexOfChild(item) == item.parent().childCount() - 1
        expander_x = ROOT_ITEM_OFFSET + (depth * indent) + (indent * 0.25)
        parent_guide_x = (ROOT_ITEM_OFFSET + ((depth - 1) * indent) + half_indent) if depth > 0 else ROOT_ITEM_OFFSET
        center_y = rect.center().y()
        diagonal_start_y = rect.center().y() - 4.0

        if depth > 0:
            end_y = diagonal_start_y if item_is_last_child else rect.bottom()
            painter.drawLine(QPointF(parent_guide_x, rect.top()), QPointF(parent_guide_x, end_y))

        painter.setPen(QPen(accent_color, 2.0 if item_is_folder else 1.0))
        painter.drawLine(QPointF(parent_guide_x, diagonal_start_y), QPointF(expander_x, center_y))

        if item_is_folder:
            painter.setPen(QPen(accent_color, 1.2))
            self._draw_expander_at(painter, QPointF(expander_x, center_y), item.isExpanded())
        painter.restore()

    def _draw_expander_at(self, painter: QPainter, pos: QPointF, is_open: bool):
        arrow_size = 3.5
        p1 = pos + QPointF(-arrow_size / 2, -arrow_size)
        p2 = pos + QPointF(arrow_size / 2, 0)
        p3 = pos + QPointF(-arrow_size / 2, arrow_size)
        painter.save()
        painter.translate(pos)
        painter.rotate(90 if is_open else 0)
        painter.translate(-pos)
        painter.drawLine(p1, p2)
        painter.drawLine(p2, p3)
        painter.restore()

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasFormat(TREE_ITEM_MIME_TYPE):
            event.acceptProposedAction()
        else:
            super().dragEnterEvent(event)

    def dragMoveEvent(self, event: QDragMoveEvent):
        if not event.mimeData().hasFormat(TREE_ITEM_MIME_TYPE):
            event.ignore()
            return

        target_item = self.itemAt(event.position().toPoint())
        if not target_item:
            event.ignore()
            return

        source_path = event.mimeData().data(TREE_ITEM_MIME_TYPE).data().decode('utf-8')
        target_data = target_item.data(0, Qt.ItemDataRole.UserRole)
        target_path = target_data.get('path') if target_data else None

        if not target_path or os.path.normpath(source_path) == os.path.normpath(target_path):
            event.ignore()
            return
        
        dest_dir = target_path if target_data.get('is_dir') else os.path.dirname(target_path)

        if os.path.isdir(source_path) and os.path.normpath(dest_dir).startswith(os.path.normpath(source_path) + os.sep):
            event.ignore()
            return
            
        event.acceptProposedAction()


    def dropEvent(self, event: QDropEvent):
        if not event.mimeData().hasFormat(TREE_ITEM_MIME_TYPE):
            event.ignore()
            return

        source_path = event.mimeData().data(TREE_ITEM_MIME_TYPE).data().decode('utf-8')
        target_item = self.itemAt(event.position().toPoint())
        if not target_item:
            event.ignore()
            return

        target_data = target_item.data(0, Qt.ItemDataRole.UserRole)
        target_path = target_data.get('path') if target_data else None
        if not target_path:
            event.ignore()
            return

        dest_dir = target_path if target_data.get('is_dir') else os.path.dirname(target_path)
        is_copy = (event.modifiers() & Qt.KeyboardModifier.ControlModifier) == Qt.KeyboardModifier.ControlModifier
        
        operation = self.file_handler.copy_item_to_dest if is_copy else self.file_handler.move_item
        success, new_path = self.parent_view._perform_file_operation(operation, source_path, dest_dir, return_result=True)
        
        if success:
            log.info("Drag-and-drop operation successful, refreshing tree view.")
            self.parent_view.refresh()
            QTimer.singleShot(150, lambda p=new_path: self.parent_view._select_and_scroll_to_path(p))
            
        event.acceptProposedAction()


    def keyPressEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key.Key_Delete:
            selected_items = self.selectedItems()
            if selected_items:
                paths = [item.data(0, Qt.ItemDataRole.UserRole)['path'] for item in selected_items if item.data(0, Qt.ItemDataRole.UserRole)]
                if paths:
                    self.parent_view._action_delete(paths)
                    event.accept()
                    return
        super().keyPressEvent(event)
    
    def mousePressEvent(self, event: QMouseEvent):
        super().mousePressEvent(event)
        
        if event.button() == Qt.MouseButton.LeftButton:
            item = self.itemAt(event.pos())
            if not item:
                self.clearSelection()
                return

            modifiers = QApplication.keyboardModifiers()
            if modifiers & Qt.KeyboardModifier.ShiftModifier:
                if current_item := self.currentItem():
                    selection_model = self.selectionModel()
                    selection_model.select(QItemSelection(self.indexFromItem(item), self.indexFromItem(current_item)), QItemSelectionModel.SelectionFlag.Select | QItemSelectionModel.SelectionFlag.Rows)
            else:
                # Toggle expansion on single click
                if (data := item.data(0, Qt.ItemDataRole.UserRole)) and data.get('is_dir'):
                    item.setExpanded(not item.isExpanded())

    def mouseDoubleClickEvent(self, event: QMouseEvent):
        item = self.itemAt(event.pos())
        if item and (data := item.data(0, Qt.ItemDataRole.UserRole)) and data.get('is_dir'):
            # If it's a directory, we consume the event to prevent toggling again,
            # as mousePressEvent already handled it.
            event.accept()
            return
        # For files, let the default or connected slots handle it
        super().mouseDoubleClickEvent(event)


class FileSystemListView(QWidget):
    def __init__(self, puffin_api: PuffinPluginAPI, parent: QWidget = None):
        super().__init__(parent)
        self.api = puffin_api
        self.project_manager = self.api.get_manager("project")
        self.file_handler = self.api.get_manager("file_handler")
        self.theme_manager = self.api.get_manager("theme")
        self.icon_provider = CustomFileIconProvider(self.api)
        self.git_statuses = {}
        self.fs_watcher = QFileSystemWatcher(self)
        self.watched_paths = set()
        self._refresh_timer = QTimer(self)
        self._refresh_timer.setSingleShot(True)
        self._refresh_timer.setInterval(300)
        self._is_programmatic_change = False
        self._setup_ui()
        self._connect_signals()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        toolbar_frame = QFrame()
        toolbar_frame.setObjectName("ExplorerToolbar")
        toolbar_layout = QHBoxLayout(toolbar_frame)
        toolbar_layout.setContentsMargins(5, 2, 5, 2)
        toolbar_layout.setSpacing(5)
        self.expand_button = QToolButton()
        self.expand_button.setIcon(qta.icon('mdi.arrow-expand-all', color='gray'))
        self.expand_button.setToolTip("Expand All")
        self.expand_button.setAutoRaise(True)
        self.collapse_button = QToolButton()
        self.collapse_button.setIcon(qta.icon('mdi.arrow-collapse-all', color='gray'))
        self.collapse_button.setToolTip("Collapse All")
        self.collapse_button.setAutoRaise(True)
        self.refresh_button = QToolButton()
        self.refresh_button.setIcon(qta.icon('mdi.refresh', color='gray'))
        self.refresh_button.setToolTip("Refresh")
        self.refresh_button.setAutoRaise(True)
        toolbar_layout.addStretch()
        toolbar_layout.addWidget(self.expand_button)
        toolbar_layout.addWidget(self.collapse_button)
        toolbar_layout.addWidget(self.refresh_button)
        layout.addWidget(toolbar_frame)
        self.tree_widget = StyledTreeView(self.api, self)
        self.tree_widget.setHeaderLabels(["Project / File", ""])
        header = self.tree_widget.header()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)
        header.resizeSection(1, 60)
        self.tree_widget.setAlternatingRowColors(True)
        self.tree_widget.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.tree_widget.setIndentation(14)
        layout.addWidget(self.tree_widget)

    def _connect_signals(self):
        self.expand_button.clicked.connect(self.expand_all)
        self.collapse_button.clicked.connect(self.collapse_all)
        self.refresh_button.clicked.connect(self.refresh)
        self.tree_widget.itemExpanded.connect(self.on_item_expanded)
        self.tree_widget.itemCollapsed.connect(self.on_item_collapsed)
        self.tree_widget.itemDoubleClicked.connect(self.on_item_double_clicked)
        self.tree_widget.customContextMenuRequested.connect(self.show_context_menu)
        self.fs_watcher.directoryChanged.connect(self._schedule_refresh)
        self.fs_watcher.fileChanged.connect(self._schedule_refresh)
        self._refresh_timer.timeout.connect(self.refresh)
        if git_manager := self.api.get_manager("git"):
            git_manager.git_success.connect(self.refresh)
        self.file_handler.item_created.connect(self._on_item_created)
        self.file_handler.item_renamed.connect(self._on_item_renamed)
        self.file_handler.item_deleted.connect(self._on_item_deleted)

    def _action_new_file(self, target_dir: str):
        file_name, ok = QInputDialog.getText(self, "New File", "Enter file name:")
        if ok and file_name:
            self._perform_file_operation(self.file_handler.create_file, os.path.join(target_dir, file_name))

    def _action_new_folder(self, target_dir: str):
        folder_name, ok = QInputDialog.getText(self, "New Folder", "Enter folder name:")
        if ok and folder_name:
            self._perform_file_operation(self.file_handler.create_folder, os.path.join(target_dir, folder_name))

    def _action_rename(self, path: str):
        old_name = os.path.basename(path)
        new_name, ok = QInputDialog.getText(self, f"Rename '{old_name}'", "Enter new name:", text=old_name)
        if ok and new_name and new_name != old_name:
            self._perform_file_operation(self.file_handler.rename_item, path, new_name)

    def _action_delete(self, paths: List[str] or str):
        if isinstance(paths, str): paths = [paths]
        if not paths: return
        names = ", ".join([f"'{os.path.basename(p)}'" for p in paths])
        reply = QMessageBox.question(self, "Confirm Delete", f"Are you sure you want to delete {names}?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            for path in paths:
                self._perform_file_operation(self.file_handler.delete_item, path)

    def _action_duplicate(self, path: str):
        self._perform_file_operation(self.file_handler.duplicate_item, path)

    def _action_remove_boms(self, path: str):
        self.file_handler.remove_boms_in_path(path)

    def _perform_file_operation(self, operation_func, *args, return_result=False):
        try:
            success, message_or_data = operation_func(*args)
            if not success:
                QMessageBox.warning(self, "Operation Failed", message_or_data)
            if return_result:
                return success, message_or_data
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An unexpected error occurred: {e}")
            if return_result:
                return False, None

    def expand_all(self):
        self._is_programmatic_change = True
        self.tree_widget.expandAll()
        self._is_programmatic_change = False
        self._save_expanded_state_to_settings()

    def collapse_all(self):
        self._is_programmatic_change = True
        self.tree_widget.collapseAll()
        self._is_programmatic_change = False
        self._save_expanded_state_to_settings()

    def get_expanded_paths(self):
        expanded = set()
        iterator = QTreeWidgetItemIterator(self.tree_widget, QTreeWidgetItemIterator.IteratorFlag.All)
        while (item := iterator.value()):
            if item.isExpanded() and (data := item.data(0, Qt.ItemDataRole.UserRole)) and (path := data.get('path')):
                expanded.add(os.path.normpath(path))
            iterator += 1
        return list(expanded)
    
    def _save_expanded_state_to_settings(self):
        settings_manager.set("explorer_expanded_paths", self.get_expanded_paths())

    def _on_item_created(self, item_type: str, path: str):
        log.debug(f"Created {item_type}: {path}, refreshing.")
        self.refresh()
        QTimer.singleShot(150, lambda: self._select_and_scroll_to_path(path))
        if item_type == "file":
            self.api.get_main_window()._action_open_file(path)

    def _on_item_renamed(self, item_type: str, old: str, new: str):
        self.api.get_main_window()._on_file_renamed(old, new)
        self.refresh()
        QTimer.singleShot(100, lambda: self._select_and_scroll_to_path(new))

    def _on_item_deleted(self, item_type: str, path: str):
        self.refresh()
        QTimer.singleShot(150, lambda: self._select_and_scroll_to_path(os.path.dirname(path)))

    def on_item_double_clicked(self, item: QTreeWidgetItem, col: int):
        if (data := item.data(0, Qt.ItemDataRole.UserRole)) and not data.get('is_dir') and (path := data.get('path')) and os.path.isfile(path):
            self.api.get_main_window()._action_open_file(path)
            
    def _schedule_refresh(self, path: str):
        if not self._is_programmatic_change:
            log.debug(f"FS event at {path}. Refresh scheduled.")
            self._refresh_timer.start()

    def _move_project(self, path: str, direction: str):
        to_top = (direction == 'up')
        if QApplication.keyboardModifiers() & Qt.KeyboardModifier.ShiftModifier:
            self.project_manager.move_project_to_end(path, to_top)
        else:
            self.project_manager.move_project(path, direction)

    def refresh(self):
        log.info("Refreshing file explorer.")
        expanded_paths = set(os.path.normpath(p) for p in settings_manager.get("explorer_expanded_paths", []))
        is_first_load = not self.tree_widget.topLevelItemCount() > 0
        selected_paths = {os.path.normpath(item.data(0, Qt.ItemDataRole.UserRole)['path']) for item in self.tree_widget.selectedItems() if item.data(0, Qt.ItemDataRole.UserRole)}
        
        self.tree_widget.blockSignals(True)
        self._is_programmatic_change = True

        if self.watched_paths:
            self.fs_watcher.removePaths(list(self.watched_paths))
        self.watched_paths.clear()
        self.tree_widget.clear()
        
        open_projects = self.project_manager.get_open_projects()
        get_git_statuses_for_root.cache_clear()
        self.git_statuses = {p: get_git_statuses_for_root(p) for p in open_projects}
        self.flat_git_status = {k: v for d in self.git_statuses.values() for k, v in d.items()}
        items_to_reselect = []

        def build_tree_level(parent_item, path):
            try:
                self._add_to_watcher(path)
                for entry in sorted(os.scandir(path), key=lambda e: (not e.is_dir(), e.name.lower())):
                    if entry.name.startswith(('.', '__pycache__', 'venv')):
                        continue
                    norm_path = os.path.normpath(entry.path)
                    child = QTreeWidgetItem(parent_item, [entry.name])
                    child.setFirstColumnSpanned(True)
                    child.setIcon(0, self.icon_provider.icon(QFileInfo(entry.path)))
                    child.setData(0, Qt.ItemDataRole.UserRole, {'path': norm_path, 'is_dir': entry.is_dir()})
                    if norm_path in selected_paths:
                        items_to_reselect.append(child)
                    
                    if status := self.flat_git_status.get(norm_path):
                        colors = self.theme_manager.current_theme_data.get('colors', {})
                        color_map = {'??': 'git.added', 'M': 'git.modified', 'A': 'git.added', 'D': 'git.deleted', '!!': 'syntax.comment'}
                        for code, color_key in color_map.items():
                            if code in status and (color_val := colors.get(color_key)):
                                child.setForeground(0, QColor(color_val))
                                break

                    if entry.is_dir():
                        if norm_path in expanded_paths:
                            child.setExpanded(True)
                            build_tree_level(child, norm_path)
                        else:
                            child.addChild(QTreeWidgetItem([""]))
            except OSError as e:
                log.warning(f"Scan dir error: {e}")

        for proj in open_projects:
            norm_proj = os.path.normpath(proj)
            item = QTreeWidgetItem(self.tree_widget, [os.path.basename(norm_proj)])
            item.setToolTip(0, norm_proj)
            item.setIcon(0, qta.icon('mdi.folder-open-outline', color=self.theme_manager.current_theme_data.get('colors', {}).get('accent')))
            item.setData(0, Qt.ItemDataRole.UserRole, {'path': norm_proj, 'is_dir': True, 'is_root': True})
            if is_first_load or norm_proj in expanded_paths:
                item.setExpanded(True)
            controls_widget = QWidget()
            controls_layout = QHBoxLayout(controls_widget)
            controls_layout.setContentsMargins(0, 0, 0, 0)
            controls_layout.setSpacing(0)
            up_btn = QToolButton(icon=qta.icon('mdi.arrow-up-bold-box-outline'), toolTip="Move project up")
            down_btn = QToolButton(icon=qta.icon('mdi.arrow-down-bold-box-outline'), toolTip="Move project down")
            up_btn.clicked.connect(partial(self._move_project, norm_proj, 'up'))
            down_btn.clicked.connect(partial(self._move_project, norm_proj, 'down'))
            for btn in (up_btn, down_btn):
                btn.setAutoRaise(True)
            controls_layout.addStretch()
            controls_layout.addWidget(up_btn)
            controls_layout.addWidget(down_btn)
            self.tree_widget.setItemWidget(item, 1, controls_widget)
            build_tree_level(item, norm_proj)
            
        if items_to_reselect:
            self.tree_widget.clearSelection()
            for item in items_to_reselect:
                item.setSelected(True)
            if items_to_reselect:
                self.tree_widget.scrollToItem(items_to_reselect[0])
        elif self.tree_widget.topLevelItemCount() > 0:
            current = self.tree_widget.currentItem()
            if not current or not current.isSelected():
                self.tree_widget.setCurrentItem(self.tree_widget.topLevelItem(0))

        self.tree_widget.blockSignals(False)
        self._is_programmatic_change = False

    def _add_to_watcher(self, path):
        if path and path not in self.watched_paths:
            self.fs_watcher.addPath(path)
            self.watched_paths.add(path)

    def _find_item_by_path(self, parent_item, path_to_find):
        iterator = QTreeWidgetItemIterator(parent_item)
        while (item := iterator.value()):
            if (data := item.data(0, Qt.ItemDataRole.UserRole)) and os.path.normpath(data.get('path', '')) == path_to_find:
                return item
            iterator += 1
        return None
        
    def _select_and_scroll_to_path(self, path: str):
        if path and (item := self._find_item_by_path(self.tree_widget.invisibleRootItem(), os.path.normpath(path))):
            try:
                self.tree_widget.scrollToItem(item, QAbstractItemView.ScrollHint.PositionAtCenter)
                self.tree_widget.setCurrentItem(item)
            except RuntimeError as e:
                log.warning(f"Scroll failed (ignored): {e}")

    def on_item_expanded(self, item: QTreeWidgetItem):
        if self._is_programmatic_change:
            return
        data = item.data(0, Qt.ItemDataRole.UserRole)
        if data and data.get('is_dir') and item.childCount() == 1 and not item.child(0).text(0):
            self._is_programmatic_change = True
            item.takeChildren()
            self._populate_node(item)
            self._is_programmatic_change = False
        self._save_expanded_state_to_settings()

    def on_item_collapsed(self, item: QTreeWidgetItem):
        if not self._is_programmatic_change:
            self._save_expanded_state_to_settings()

    def _populate_node(self, parent_item):
        path = (data := parent_item.data(0, Qt.ItemDataRole.UserRole)) and data.get('path')
        if not path or not os.path.isdir(path):
            return
        try:
            for entry in sorted(os.scandir(path), key=lambda e: (not e.is_dir(), e.name.lower())):
                if entry.name.startswith(('.', '__pycache__', 'venv')):
                    continue
                child = QTreeWidgetItem(parent_item, [entry.name])
                child.setFirstColumnSpanned(True)
                child.setIcon(0, self.icon_provider.icon(QFileInfo(entry.path)))
                child.setData(0, Qt.ItemDataRole.UserRole, {'path': os.path.normpath(entry.path), 'is_dir': entry.is_dir()})
                if status := self.flat_git_status.get(os.path.normpath(entry.path)):
                    colors, color_map = self.theme_manager.current_theme_data.get('colors', {}), {'??': 'git.added', 'M': 'git.modified', 'A': 'git.added', 'D': 'git.deleted', '!!': 'syntax.comment'}
                    for code, color_key in color_map.items():
                        if code in status and (color := colors.get(color_key)):
                            child.setForeground(0, QColor(color))
                            break
                if entry.is_dir():
                    child.addChild(QTreeWidgetItem([""]))
        except OSError:
            pass

    def show_context_menu(self, position: QPoint):
        item = self.tree_widget.itemAt(position)
        path, is_dir = self.project_manager.get_active_project_path(), True
        if item and (data := item.data(0, Qt.ItemDataRole.UserRole)):
            path, is_dir = data.get('path'), data.get('is_dir')
        if path:
            show_project_context_menu(self, self.tree_widget.mapToGlobal(position), path, is_dir, self.project_manager)
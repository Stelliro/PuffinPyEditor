# PuffinPyEditor/ui/explorer/list_view_widget.py
import os
import sys
# MODIFIED: Added imports for typing and more Qt modules for drag-and-drop
from typing import List, Optional
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QTreeWidget, QTreeWidgetItem, QInputDialog, QMessageBox,
                             QProxyStyle, QStyle, QApplication, QAbstractItemView, QToolButton,
                             QHBoxLayout, QTreeWidgetItemIterator)
from PyQt6.QtGui import (QPainter, QColor, QPen, QDrag, QKeyEvent, QIcon, QPaintEvent, QDragEnterEvent, QDropEvent, QDragMoveEvent)
from PyQt6.QtCore import (Qt, QFileInfo, QMimeData, QRect, QFileSystemWatcher, QTimer, QPoint, QPointF,
                          QUrl)
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

    def drawPrimitive(self, element, option, painter, widget=None):
        if element == QStyle.PrimitiveElement.PE_IndicatorBranch:
            return  # Skip drawing the default branch indicator
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

    def supportedDropActions(self) -> Qt.DropAction:
        """Specifies that we support both copy and move actions."""
        return Qt.DropAction.CopyAction | Qt.DropAction.MoveAction

    def mimeData(self, items: List[QTreeWidgetItem]) -> Optional[QMimeData]:
        """Creates the MIME data for a drag operation."""
        if not items:
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
        """
        Custom paint event to draw a root guide line before other painting.
        """
        super().paintEvent(event)
        if self.topLevelItemCount() == 0:
            return

        # Draw the main root vertical line
        painter = QPainter(self.viewport())
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        colors = self.theme_manager.current_theme_data.get('colors', {})
        pen = QPen(QColor(colors.get('accent', '#83c092')), 1)
        painter.setPen(pen)
        painter.drawLine(8, 0, 8, self.viewport().height())

    def drawBranches(self, painter: QPainter, rect: QRect, index: 'QModelIndex'):
        """
        Overrides the default branch drawing to create custom guide lines.
        """
        item = self.itemFromIndex(index)
        if not item or not item.parent() or item.parent() == self.invisibleRootItem():
            return  # Don't draw for top-level items or invalid items

        # --- Configuration & Theme Colors ---
        colors = self.theme_manager.current_theme_data.get('colors', {})
        accent_color = QColor(colors.get('accent', '#83c092'))
        indent = self.indentation()
        half_indent = indent / 2.0
        # The base offset for the first level of indentation
        ROOT_ITEM_OFFSET = 14

        painter.save()
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # --- Calculate item depth ---
        depth = -1
        temp_item = item
        while temp_item.parent() and temp_item.parent() != self.invisibleRootItem():
            depth += 1
            temp_item = temp_item.parent()
        if depth < 0:
            painter.restore()
            return

        # --- Draw Vertical Ancestor Guides ---
        # This loop walks up the tree to see if parent folders have siblings
        # below them. If so, a vertical line is needed.
        painter.setPen(QPen(accent_color, 1))
        for i in range(depth):
            ancestor = item
            for _ in range(depth - i):
                ancestor = ancestor.parent()
            # If the ancestor is not the last child, draw a vertical line
            if ancestor.parent() and ancestor.parent().indexOfChild(ancestor) < ancestor.parent().childCount() - 1:
                line_x = ROOT_ITEM_OFFSET + (i * indent) + half_indent
                painter.drawLine(QPointF(line_x, rect.top()), QPointF(line_x, rect.bottom()))

        # --- Draw Horizontal Connector Guide ---
        item_is_folder = item.childCount() > 0 or (item.childCount() == 1 and not item.child(0).text(0))
        item_is_last_child = item.parent().indexOfChild(item) == item.parent().childCount() - 1

        # The X position of the expander icon and the parent's vertical guide line
        expander_x = ROOT_ITEM_OFFSET + (depth * indent) + (indent * 0.25)
        parent_guide_x = (ROOT_ITEM_OFFSET + ((depth - 1) * indent) + half_indent) if depth > 0 else ROOT_ITEM_OFFSET

        center_y = rect.center().y()
        diagonal_start_y = rect.center().y() - 4.0

        # Draw the short vertical line segment from the parent guide
        if depth > 0:
            end_y = diagonal_start_y if item_is_last_child else rect.bottom()
            painter.drawLine(QPointF(parent_guide_x, rect.top()), QPointF(parent_guide_x, end_y))

        # Draw the diagonal connector
        painter.setPen(QPen(accent_color, 2.0 if item_is_folder else 1.0))
        painter.drawLine(QPointF(parent_guide_x, diagonal_start_y), QPointF(expander_x, center_y))

        # --- Draw Expander Icon ---
        if item_is_folder:
            painter.setPen(QPen(accent_color, 1.2))
            self._draw_expander_at(painter, QPointF(expander_x, center_y), item.isExpanded())

        painter.restore()

    def _draw_expander_at(self, painter: QPainter, pos: QPointF, is_open: bool):
        """Draws a custom > or v arrow for expanding/collapsing."""
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
        """Accepts drags if they contain our custom MIME type."""
        if event.mimeData().hasFormat(TREE_ITEM_MIME_TYPE):
            event.acceptProposedAction()
        else:
            super().dragEnterEvent(event)

    def dragMoveEvent(self, event: QDragMoveEvent):
        """Determines if a drop is allowed at the current cursor position."""
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

        if not target_path:
            event.ignore()
            return
            
        if os.path.normpath(source_path) == os.path.normpath(target_path):
            event.ignore()
            return

        dest_dir = target_path if target_data.get('is_dir') else os.path.dirname(target_path)

        if os.path.isdir(source_path) and os.path.normpath(dest_dir).startswith(os.path.normpath(source_path) + os.sep):
            event.ignore()
            return

        event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent):
        """Handles the drop of an item."""
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

        is_copy = (event.keyboardModifiers() & Qt.KeyboardModifier.ControlModifier) == Qt.KeyboardModifier.ControlModifier
        
        operation = self.file_handler.copy_item_to_dest if is_copy else self.file_handler.move_item
        
        # MODIFIED: Call the file operation and then explicitly refresh the UI.
        success, new_path = self.parent_view._perform_file_operation(operation, source_path, dest_dir, return_result=True)
        if success:
            log.info("Drag-and-drop operation successful, refreshing tree view.")
            self.parent_view.refresh()
            # After refreshing, try to select the newly moved/copied item
            QTimer.singleShot(150, lambda p=new_path: self.parent_view._select_and_scroll_to_path(p))
            
        event.acceptProposedAction()

    def keyPressEvent(self, event: QKeyEvent):
        """Handles key presses, like the Delete key."""
        if event.key() == Qt.Key.Key_Delete:
            item = self.currentItem()
            if item and (data := item.data(0, Qt.ItemDataRole.UserRole)) and (path := data.get('path')):
                self.parent_view._action_delete(path)
                event.accept()
                return

        super().keyPressEvent(event)


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
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)

        toolbar_layout = QHBoxLayout()
        self.expand_button = QToolButton()
        self.expand_button.setIcon(qta.icon('mdi.arrow-expand-all', color='gray'))
        self.expand_button.setToolTip("Expand All")

        self.collapse_button = QToolButton()
        self.collapse_button.setIcon(qta.icon('mdi.arrow-collapse-all', color='gray'))
        self.collapse_button.setToolTip("Collapse All")

        self.refresh_button = QToolButton()
        self.refresh_button.setIcon(qta.icon('mdi.refresh', color='gray'))
        self.refresh_button.setToolTip("Refresh")

        toolbar_layout.addStretch()
        toolbar_layout.addWidget(self.expand_button)
        toolbar_layout.addWidget(self.collapse_button)
        toolbar_layout.addWidget(self.refresh_button)
        layout.addLayout(toolbar_layout)

        self.tree_widget = StyledTreeView(self.api, self)
        self.tree_widget.setHeaderLabels(["Project / File", ""])
        header = self.tree_widget.header()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)
        header.resizeSection(1, 60) # Width for reorder buttons

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

    def expand_all(self):
        self._is_programmatic_change = True
        self.tree_widget.expandAll()
        self._is_programmatic_change = False
        self._save_expanded_state_to_settings()

    def collapse_all(self):
        self._is_programmatic_change = True
        self.tree_widget.collapseAll()
        # Ensure project roots stay visible
        for i in range(self.tree_widget.topLevelItemCount()):
            item = self.tree_widget.topLevelItem(i)
            if item:
                self.tree_widget.expandItem(item)
        self._is_programmatic_change = False
        self._save_expanded_state_to_settings()

    def get_expanded_paths(self):
        expanded_set = set()
        iterator = QTreeWidgetItemIterator(self.tree_widget, QTreeWidgetItemIterator.IteratorFlag.All)
        while iterator.value():
            item = iterator.value()
            if item.isExpanded():
                data = item.data(0, Qt.ItemDataRole.UserRole)
                if data and (path := data.get('path')):
                    expanded_set.add(os.path.normpath(path))
            iterator += 1
        return list(expanded_set)

    def _save_expanded_state_to_settings(self):
        """Persists the current expanded paths to the settings file."""
        settings_manager.set("explorer_expanded_paths", self.get_expanded_paths())

    def _on_item_created(self, item_type: str, path: str):
        log.debug(f"Item created, refreshing explorer for: {path}")
        self.refresh()
        QTimer.singleShot(150, lambda: self._select_and_scroll_to_path(path))
        if item_type == "file":
            self.api.get_main_window()._action_open_file(path)

    def _on_item_renamed(self, item_type: str, old_path: str, new_path: str):
        self.api.get_main_window()._on_file_renamed(old_path, new_path)
        log.debug(f"Item renamed, refreshing explorer for: {new_path}")
        self.refresh()
        QTimer.singleShot(100, lambda: self._select_and_scroll_to_path(new_path))

    def _on_item_deleted(self, item_type: str, path: str):
        parent_path = os.path.dirname(path)
        log.debug(f"Item deleted, refreshing explorer and selecting parent: {parent_path}")
        self.refresh()
        QTimer.singleShot(150, lambda: self._select_and_scroll_to_path(parent_path))

    def on_item_double_clicked(self, item: QTreeWidgetItem, column: int):
        data = item.data(0, Qt.ItemDataRole.UserRole)
        if data and not data.get('is_dir'):
            path = data.get('path')
            if path and os.path.isfile(path):
                self.api.get_main_window()._action_open_file(path)

    def _schedule_refresh(self, path: str):
        if not self._is_programmatic_change:
            log.debug(f"External FS event for: {path}. Scheduling refresh.")
            self._refresh_timer.start()

    def _move_project(self, path: str, direction: str):
        modifiers = QApplication.keyboardModifiers()
        is_shift_pressed = modifiers == Qt.KeyboardModifier.ShiftModifier

        if is_shift_pressed:
            self.project_manager.move_project_to_end(path, to_top=(direction == 'up'))
        else:
            self.project_manager.move_project(path, direction)

    def refresh(self):
        log.info("Refreshing file explorer view.")

        expanded_paths = set(os.path.normpath(p) for p in self.get_expanded_paths())
        if not expanded_paths:
            persisted_paths = settings_manager.get("explorer_expanded_paths", [])
            expanded_paths.update(os.path.normpath(p) for p in persisted_paths)

        current_item = self.tree_widget.currentItem()
        current_path = os.path.normpath(
            current_item.data(0, Qt.ItemDataRole.UserRole)['path']) if current_item and current_item.data(0,
                                                                                                          Qt.ItemDataRole.UserRole) else None

        self._is_programmatic_change = True
        self.tree_widget.blockSignals(True)

        if self.watched_paths:
            self.fs_watcher.removePaths(list(self.watched_paths))
        self.watched_paths.clear()
        self.tree_widget.clear()

        open_projects = self.project_manager.get_open_projects()
        get_git_statuses_for_root.cache_clear()
        self.git_statuses = {p: get_git_statuses_for_root(p) for p in open_projects}
        self.flat_git_status = {k: v for d in self.git_statuses.values() for k, v in d.items()}

        def build_tree_level(parent_item, path):
            try:
                self._add_to_watcher(path)
                entries = sorted(os.scandir(path), key=lambda e: (not e.is_dir(), e.name.lower()))
                for entry in entries:
                    if entry.name.startswith(('.', '__pycache__')) or entry.name == 'venv':
                        continue

                    norm_entry_path = os.path.normpath(entry.path)
                    child_item = QTreeWidgetItem(parent_item, [entry.name])
                    child_item.setIcon(0, self.icon_provider.icon(QFileInfo(entry.path)))
                    child_item.setData(0, Qt.ItemDataRole.UserRole, {'path': norm_entry_path, 'is_dir': entry.is_dir()})

                    status = self.flat_git_status.get(norm_entry_path)
                    if status:
                        colors = self.theme_manager.current_theme_data.get('colors', {})
                        color_map = {
                            '??': colors.get('git.added', '#a7c080'),
                            'M': colors.get('git.modified', '#dbbc7f'),
                            'A': colors.get('git.added', '#a7c080'),
                            'D': colors.get('git.deleted', '#e67e80'),
                            '!!': colors.get('syntax.comment', '#5f6c6d')}
                        for code, color in color_map.items():
                            if code in status:
                                child_item.setForeground(0, QColor(color))
                                break

                    if entry.is_dir():
                        if norm_entry_path in expanded_paths:
                            child_item.setExpanded(True)
                            build_tree_level(child_item, norm_entry_path)
                        else:
                            child_item.addChild(QTreeWidgetItem([""]))  # Placeholder
            except OSError as e:
                log.warning(f"Failed to scan directory {path}: {e}")

        # Start build from roots
        for proj_path in open_projects:
            norm_path = os.path.normpath(proj_path)
            item = QTreeWidgetItem(self.tree_widget, [os.path.basename(norm_path)])
            item.setToolTip(0, norm_path)
            colors = self.theme_manager.current_theme_data.get('colors', {})
            item.setIcon(0, qta.icon('mdi.folder-open-outline', color=colors.get('accent')))
            item.setData(0, Qt.ItemDataRole.UserRole, {'path': norm_path, 'is_dir': True, 'is_root': True})
            item.setExpanded(True)

            # Add reorder controls for project root items
            controls_widget = QWidget()
            controls_layout = QHBoxLayout(controls_widget)
            controls_layout.setContentsMargins(0, 0, 0, 0)
            controls_layout.setSpacing(2)
            up_button = QToolButton(icon=qta.icon('mdi.arrow-up-bold-box-outline'), toolTip="Move project up")
            down_button = QToolButton(icon=qta.icon('mdi.arrow-down-bold-box-outline'), toolTip="Move project down")
            up_button.clicked.connect(partial(self._move_project, norm_path, 'up'))
            down_button.clicked.connect(partial(self._move_project, norm_path, 'down'))
            for btn in [up_button, down_button]: btn.setAutoRaise(True)
            controls_layout.addStretch()
            controls_layout.addWidget(up_button)
            controls_layout.addWidget(down_button)
            self.tree_widget.setItemWidget(item, 1, controls_widget)

            build_tree_level(item, norm_path)

        self.tree_widget.blockSignals(False)
        self._is_programmatic_change = False

        if current_path:
            self._select_and_scroll_to_path(current_path)
        elif self.tree_widget.topLevelItemCount() > 0:
            self.tree_widget.setCurrentItem(self.tree_widget.topLevelItem(0))

    def _add_to_watcher(self, path):
        if path and path not in self.watched_paths:
            self.fs_watcher.addPath(path)
            self.watched_paths.add(path)

    def _find_item_by_path(self, parent_item, path_to_find):
        """Recursively search for a QTreeWidgetItem by its path data."""
        iterator = QTreeWidgetItemIterator(parent_item)
        while iterator.value():
            item = iterator.value()
            data = item.data(0, Qt.ItemDataRole.UserRole)
            if data and os.path.normpath(data.get('path', '')) == path_to_find:
                return item
            iterator += 1
        return None

    def _select_and_scroll_to_path(self, path):
        if not path: return
        item_to_select = self._find_item_by_path(self.tree_widget.invisibleRootItem(), os.path.normpath(path))
        if item_to_select:
            self.tree_widget.setCurrentItem(item_to_select)
            self.tree_widget.scrollToItem(item_to_select, QAbstractItemView.ScrollHint.PositionAtCenter)

    def on_item_expanded(self, item: QTreeWidgetItem):
        if self._is_programmatic_change: return
        # User-driven expansion: lazy-load children
        data = item.data(0, Qt.ItemDataRole.UserRole)
        if data and data.get('is_dir') and item.childCount() == 1 and item.child(0).text(0) == "":
            self._is_programmatic_change = True
            item.takeChildren()
            self._populate_node(item)
            self._is_programmatic_change = False
        self._save_expanded_state_to_settings()

    def on_item_collapsed(self, item: QTreeWidgetItem):
        if self._is_programmatic_change: return
        self._save_expanded_state_to_settings()

    def _populate_node(self, parent_item):
        """Populates a single node. Called for lazy loading."""
        data = parent_item.data(0, Qt.ItemDataRole.UserRole)
        path = data.get('path')
        if not (data and path and os.path.isdir(path)):
            return

        try:
            entries = sorted(os.scandir(path), key=lambda e: (not e.is_dir(), e.name.lower()))
            for entry in entries:
                if entry.name.startswith(('.', '__pycache__')) or entry.name == 'venv':
                    continue
                child_item = QTreeWidgetItem(parent_item, [entry.name])
                child_item.setIcon(0, self.icon_provider.icon(QFileInfo(entry.path)))
                child_item.setData(0, Qt.ItemDataRole.UserRole,
                                   {'path': os.path.normpath(entry.path), 'is_dir': entry.is_dir()})

                status = self.flat_git_status.get(os.path.normpath(entry.path))
                if status:
                    colors = self.theme_manager.current_theme_data.get('colors', {})
                    color_map = {
                        '??': colors.get('git.added', '#a7c080'),
                        'M': colors.get('git.modified', '#dbbc7f'),
                        'A': colors.get('git.added', '#a7c080'),
                        'D': colors.get('git.deleted', '#e67e80'),
                        '!!': colors.get('syntax.comment', '#5f6c6d')}
                    for code, color in color_map.items():
                        if code in status:
                            child_item.setForeground(0, QColor(color))
                            break

                if entry.is_dir():
                    child_item.addChild(QTreeWidgetItem([""]))  # Placeholder
        except OSError:
            pass

    def show_context_menu(self, position: QPoint):
        item = self.tree_widget.itemAt(position)
        path = self.project_manager.get_active_project_path()  # Default path
        is_dir = True

        if item and (data := item.data(0, Qt.ItemDataRole.UserRole)):
            path = data.get('path')
            is_dir = data.get('is_dir')

        if not path: return
        show_project_context_menu(self, position, path, is_dir, self.project_manager)

    def _perform_file_operation(self, operation, *args, return_result=False):
        self._is_programmatic_change = True
        success, message = False, "Operation cancelled by user."
        try:
            result = operation(*args)
            success, message = result if isinstance(result, tuple) else (result, None)
            if not success and message:
                QMessageBox.critical(self, "Operation Failed", message)
        finally:
            QTimer.singleShot(200, lambda: setattr(self, '_is_programmatic_change', False))
        
        if return_result:
            return success, message

    def _action_new_file(self, target_dir: str):
        filename, ok = QInputDialog.getText(self, "New File", "Enter file name:")
        if ok and filename:
            self._perform_file_operation(self.file_handler.create_file, os.path.join(target_dir, filename))

    def _action_new_folder(self, target_dir: str):
        foldername, ok = QInputDialog.getText(self, "New Folder", "Enter folder name:")
        if ok and foldername:
            self._perform_file_operation(self.file_handler.create_folder, os.path.join(target_dir, foldername))

    def _action_rename(self, old_path: str):
        basename = os.path.basename(old_path)
        new_name, ok = QInputDialog.getText(self, f"Rename '{basename}'", "New name:", text=basename)
        if ok and new_name and new_name != basename:
            self._perform_file_operation(self.file_handler.rename_item, old_path, new_name)

    def _action_delete(self, path_to_delete: str):
        if not path_to_delete: return
        basename = os.path.basename(path_to_delete)
        is_dir = os.path.isdir(path_to_delete)
        item_type = "folder" if is_dir else "file"
        message = f"Are you sure you want to permanently delete this {item_type}?\n\n'{basename}'"
        try:
            if is_dir and any(os.scandir(path_to_delete)):
                message += "\n\n<b>Warning: The folder is not empty.</b>"
        except OSError:
            pass
        reply = QMessageBox.question(self, f"Confirm Delete", message,
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                     QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            self._perform_file_operation(self.file_handler.delete_item, path_to_delete)

    def _action_duplicate(self, path: str):
        self._perform_file_operation(self.file_handler.duplicate_item, path)
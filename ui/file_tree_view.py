# PuffinPyEditor/ui/file_tree_view.py
import os
from functools import partial
from PyQt6.QtWidgets import QTreeView, QMessageBox, QMenu, QInputDialog
from PyQt6.QtGui import QFileSystemModel
from PyQt6.QtCore import QDir, Qt, pyqtSignal, QModelIndex, QPoint
import qtawesome as qta
from utils.logger import log
from app_core.file_handler import FileHandler


class FileTreeViewWidget(QTreeView):
    file_open_requested = pyqtSignal(str)
    file_to_open_created = pyqtSignal(str)

    def __init__(self, file_handler: FileHandler, parent=None):
        super().__init__(parent)
        log.info("FileTreeViewWidget initializing with drag-drop and context menu.")
        self.file_handler = file_handler
        self.file_system_model = QFileSystemModel()
        self.setModel(self.file_system_model)

        # === Appearance & Core Behavior ===
        self.setAnimated(True)
        self.setIndentation(15)
        self.setSortingEnabled(True)
        self.sortByColumn(0, Qt.SortOrder.AscendingOrder)
        self.setHeaderHidden(True)
        for i in range(1, self.model().columnCount()):
            self.setColumnHidden(i, True)

        # === Context Menu & Drag/Drop Setup ===
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self._show_context_menu)
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.setDropIndicatorShown(True)
        self.setDragDropMode(self.DragDropMode.InternalMove)

        # === Signals ===
        self.doubleClicked.connect(self._on_item_double_clicked)

    def set_project_root(self, path: str | None):
        if path and QDir(path).exists():
            log.info(f"Setting FileTreeViewWidget root to: {path}")
            self.file_system_model.setRootPath(path)
            self.setRootIndex(self.file_system_model.index(path))
        else:
            self.file_system_model.setRootPath("")

    def _on_item_double_clicked(self, index: QModelIndex):
        if not index.isValid() or self.file_system_model.isDir(index):
            return
        file_path = self.file_system_model.filePath(index)
        log.info(f"File open requested: {file_path}")
        self.file_open_requested.emit(file_path)

    def _show_context_menu(self, position: QPoint):
        index = self.indexAt(position)
        menu = QMenu()
        clicked_path = self.file_system_model.filePath(index) if index.isValid() else self.file_system_model.rootPath()
        if not clicked_path:
            return

        target_dir = clicked_path if os.path.isdir(clicked_path) else os.path.dirname(clicked_path)

        menu.addAction(qta.icon('fa5s.file-alt'), "New File...", partial(self._action_new_file, target_dir))
        menu.addAction(qta.icon('fa5s.folder-plus'), "New Folder...", partial(self._action_new_folder, target_dir))

        if index.isValid():
            menu.addSeparator()
            menu.addAction("Rename...", partial(self._action_rename, clicked_path))
            menu.addAction(qta.icon('fa5s.trash-alt', color='crimson'), "Delete",
                           partial(self._action_delete, clicked_path))
            menu.addSeparator()
            menu.addAction("Copy Path", partial(self.file_handler.copy_path_to_clipboard, clicked_path))
            menu.addAction("Reveal in File Explorer", partial(self.file_handler.reveal_in_explorer, clicked_path))

        menu.exec(self.viewport().mapToGlobal(position))

    def _action_new_file(self, base_path: str):
        name, ok = QInputDialog.getText(self, "New File", "Enter file name:")
        if ok and name:
            new_path = os.path.join(base_path, name)
            success, error = self.file_handler.create_file(new_path)
            if success:
                self.file_to_open_created.emit(new_path)
            else:
                QMessageBox.warning(self, "Error", error)

    def _action_new_folder(self, base_path: str):
        name, ok = QInputDialog.getText(self, "New Folder", "Enter folder name:")
        if ok and name:
            success, error = self.file_handler.create_folder(os.path.join(base_path, name))
            if not success:
                QMessageBox.warning(self, "Error", error)

    def _action_rename(self, path: str):
        new_name, ok = QInputDialog.getText(self, "Rename", "Enter new name:", text=os.path.basename(path))
        if ok and new_name and new_name != os.path.basename(path):
            success, result = self.file_handler.rename_item(path, new_name)
            if not success:
                QMessageBox.warning(self, "Error", result)

    def _action_delete(self, path: str):
        item_name = os.path.basename(path)
        is_dir = os.path.isdir(path)
        reply = QMessageBox.question(self, "Confirm Delete",
                                     f"Are you sure you want to permanently delete '{item_name}'?" +
                                     ("\nThis will delete the folder and ALL its contents!" if is_dir else ""),
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.Cancel,
                                     QMessageBox.StandardButton.Cancel
                                     )
        if reply == QMessageBox.StandardButton.Yes:
            success, error = self.file_handler.delete_item(path)
            if not success:
                QMessageBox.warning(self, "Error", error)
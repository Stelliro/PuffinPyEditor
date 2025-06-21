# PuffinPyEditor/ui/favorites_view.py
import os
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QListWidget, QListWidgetItem, QMenu, QMessageBox, QStyle)
from PyQt6.QtGui import QAction
from PyQt6.QtCore import Qt, pyqtSignal, QPoint
from app_core.settings_manager import settings_manager
from utils.logger import log


class FavoritesViewWidget(QWidget):
    file_open_requested = pyqtSignal(str)
    open_project_requested = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.favorites_list = QListWidget()
        self.favorites_list.itemDoubleClicked.connect(self._on_item_double_clicked)
        self.favorites_list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.favorites_list.customContextMenuRequested.connect(self._show_context_menu)
        self.main_layout.addWidget(self.favorites_list)
        self.load_favorites()

    def load_favorites(self):
        self.favorites_list.clear()
        fav_paths = settings_manager.get("favorites", [])
        for path in fav_paths:
            if not path: continue
            base_name = os.path.basename(path)
            if not base_name: base_name = path
            item = QListWidgetItem(base_name)
            item.setToolTip(path)
            item.setData(Qt.ItemDataRole.UserRole, path)
            if os.path.isdir(path):
                item.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_DirIcon))
            else:
                item.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_FileIcon))
            self.favorites_list.addItem(item)
        log.info(f"Loaded {len(fav_paths)} favorites into the favorites view.")

    def add_favorite(self, path: str):
        favs = list(settings_manager.get("favorites", []))
        if path in favs:
            QMessageBox.information(self, "Already a Favorite", f"'{os.path.basename(path)}' is already a favorite.")
            return
        favs.append(path)
        settings_manager.set("favorites", favs)
        self.load_favorites()

    def remove_favorite(self, path: str):
        favs = settings_manager.get("favorites", [])
        if path in favs:
            favs.remove(path)
            settings_manager.set("favorites", favs)
            self.load_favorites()

    def _on_item_double_clicked(self, item: QListWidgetItem):
        path = item.data(Qt.ItemDataRole.UserRole)
        if not path: return
        if os.path.isdir(path):
            self.open_project_requested.emit(path)
        else:
            self.file_open_requested.emit(path)

    def _show_context_menu(self, pos: QPoint):
        item = self.favorites_list.itemAt(pos)
        if not item: return
        path = item.data(Qt.ItemDataRole.UserRole)
        menu = QMenu()
        open_as_project_action = menu.addAction("Open as Project") if os.path.isdir(path) else None
        remove_action = menu.addAction("Remove from Favorites")
        action = menu.exec(self.favorites_list.mapToGlobal(pos))
        if action == remove_action:
            self.remove_favorite(path)
        elif action == open_as_project_action:
            self.open_project_requested.emit(path)
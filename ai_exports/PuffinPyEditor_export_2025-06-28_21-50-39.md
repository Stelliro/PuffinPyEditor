# Project Export: PuffinPyEditor
## Export Timestamp: 2025-06-28T21:50:39.084682
---



---

## Project Files

Here is the project context you need to work with.
## File Tree
```
/PuffinPyEditor
 └── plugins
     └── project_explorer
         ├── plugin.json
         ├── plugin_main.py
         └── project_explorer_panel.py

```
## File Contents
### File: `/plugins/project_explorer/plugin.json`

```json
{
    "id": "project_explorer",
    "name": "Project Explorer",
    "author": "PuffinPy Team",
    "version": "1.0.0",
    "description": "Provides a dockable file tree view for open projects.",
    "entry_point": "plugin_main.py"
}
```

### File: `/plugins/project_explorer/plugin_main.py`

#### Linter Issues Found:
```

- L38 (E501) No message available

- L65 (E501) No message available

- L76 (E501) No message available

- L78 (E501) No message available

- L79 (E501) No message available

- L98 (E501) No message available

- L106 (E501) No message available

- L107 (E501) No message available

- L108 (E501) No message available

- L110 (E501) No message available

- L116 (E701) No message available

- L118 (E701) No message available

- L131 (E701) No message available

- L135 (E501) No message available

- L139 (E501) No message available

- L145 (E501) No message available

- L157 (E701) No message available

- L160 (E701) No message available

- L167 (E501) No message available

- L190 (W292) No message available

```


```python
# PuffinPyEditor/plugins/project_explorer/plugin_main.py
import os
import sys
from functools import partial
from PyQt6.QtWidgets import (QDockWidget, QTabWidget, QToolButton, QWidget,
                             QVBoxLayout, QListWidget, QPushButton,
                             QListWidgetItem, QMenu, QStackedWidget)
from PyQt6.QtCore import Qt, QPoint
import qtawesome as qta

from .project_explorer_panel import FileTreeViewWidget
from app_core.settings_manager import settings_manager


class ProjectExplorerPlugin:
    """Manages the Project Explorer dock widget and its contents."""

    def __init__(self, puffin_api):
        self.api = puffin_api
        self.main_window = self.api.get_main_window()
        self.project_manager = self.api.get_manager("project")
        self.file_handler = self.api.get_manager("file_handler")
        self.theme_manager = self.api.get_manager("theme")

        # --- Create main container and stacked widget ---
        container = QWidget()
        container.setMinimumWidth(250)  # Set a sensible minimum width
        self.layout = QVBoxLayout(container)
        self.layout.setContentsMargins(5, 5, 5, 5)
        self.layout.setSpacing(5)
        self.stacked_widget = QStackedWidget()

        # --- View 1: No Project Open ---
        self.no_project_view = QWidget()
        no_project_layout = QVBoxLayout(self.no_project_view)
        no_project_layout.setContentsMargins(0, 0, 0, 0)
        self.favorites_list = QListWidget()
        self.favorites_list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.open_project_button = QPushButton("Open a Folder...")
        self.open_project_button.setIcon(qta.icon('fa5s.folder-open'))
        no_project_layout.addWidget(self.favorites_list)
        no_project_layout.addWidget(self.open_project_button)

        # --- View 2: Projects Open ---
        self.project_tabs = QTabWidget()
        self.project_tabs.setDocumentMode(True)
        self.project_tabs.setTabsClosable(True)
        self.project_tabs.setMovable(True)
        add_button = QToolButton()
        add_button.setIcon(qta.icon('fa5s.folder-plus'))
        add_button.setAutoRaise(True)
        add_button.setToolTip("Open Another Folder")
        add_button.clicked.connect(self.main_window._action_open_folder)
        self.project_tabs.setCornerWidget(add_button, Qt.Corner.TopRightCorner)

        self.stacked_widget.addWidget(self.no_project_view)
        self.stacked_widget.addWidget(self.project_tabs)
        self.layout.addWidget(self.stacked_widget)

        # --- Create and register the dock widget ---
        self.file_tree_dock = QDockWidget("Project Explorer", self.main_window)
        self.file_tree_dock.setObjectName("ProjectExplorerDock")
        self.file_tree_dock.setWidget(container)
        self.api.add_menu_action(
            "view", "Project Explorer", self.file_tree_dock.toggleViewAction().trigger,
            "Ctrl+Shift+E"
        )
        self.main_window.addDockWidget(
            Qt.DockWidgetArea.LeftDockWidgetArea, self.file_tree_dock
        )

        self._connect_signals()
        self.refresh_project_views()

    def _connect_signals(self):
        self.project_tabs.tabCloseRequested.connect(self._action_close_project_by_index)
        self.project_tabs.currentChanged.connect(self._on_project_tab_changed)
        self.favorites_list.itemDoubleClicked.connect(self._on_favorite_activated)
        self.favorites_list.customContextMenuRequested.connect(self._show_favorites_menu)
        self.open_project_button.clicked.connect(
            lambda: self.main_window._action_open_folder()
        )

    def refresh_project_views(self):
        """Re-creates the project tabs and updates favorites list."""
        self._populate_favorites()
        open_projects = self.project_manager.get_open_projects()

        if not open_projects:
            self.stacked_widget.setCurrentWidget(self.no_project_view)
            self.file_tree_dock.setVisible(True)  # Keep visible as requested
            self._on_project_tab_changed(-1)
            return

        self.stacked_widget.setCurrentWidget(self.project_tabs)
        active_project = self.project_manager.get_active_project_path()
        self.project_tabs.blockSignals(True)
        current_trees = {self.project_tabs.tabToolTip(i): self.project_tabs.widget(i)
                         for i in range(self.project_tabs.count())}
        self.project_tabs.clear()

        active_index = -1
        for i, path in enumerate(open_projects):
            tree = current_trees.get(path)
            if not tree:
                tree = FileTreeViewWidget(self.file_handler, self.theme_manager, self.main_window)
                tree.file_open_requested.connect(self.main_window._action_open_file)
                tree.file_to_open_created.connect(lambda p: self.main_window._add_new_tab(filepath=p))
                tree.favorites_updated.connect(self._populate_favorites)
                self.main_window.theme_changed_signal.connect(tree.update_theme)

            tree.set_project_root(path)

            tab_index = self.project_tabs.addTab(tree, os.path.basename(path))
            self.project_tabs.setTabToolTip(tab_index, path)
            if path == active_project: active_index = i

        if active_index != -1: self.project_tabs.setCurrentIndex(active_index)
        self.project_tabs.blockSignals(False)
        self._on_project_tab_changed(self.project_tabs.currentIndex())

    def _populate_favorites(self):
        self.favorites_list.clear()
        try:
            # Add default system drives
            if sys.platform == "win32":
                from ctypes import windll
                drives = []
                bitmask = windll.kernel32.GetLogicalDrives()
                for letter in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
                    if bitmask & 1: drives.append(f"{letter}:\\")
                    bitmask >>= 1
                for drive in drives:
                    if os.path.exists(drive):
                        item = QListWidgetItem(qta.icon('fa5s.hdd'), f"Drive ({drive})")
                        item.setData(Qt.ItemDataRole.UserRole, drive)
                        self.favorites_list.addItem(item)
        except Exception as e:
            self.api.log_warning(f"Could not get system drives for favorites list: {e}")

        # Add user-defined favorites
        favorites = settings_manager.get("favorites", [])
        for fav_path in sorted(favorites):
            if os.path.exists(fav_path):
                item = QListWidgetItem(qta.icon('fa5s.star', color='gold'), os.path.basename(fav_path))
                item.setToolTip(fav_path)
                item.setData(Qt.ItemDataRole.UserRole, fav_path)
                self.favorites_list.addItem(item)

    def _on_favorite_activated(self, item: QListWidgetItem):
        path = item.data(Qt.ItemDataRole.UserRole)
        if path and os.path.isdir(path):
            self.main_window._action_open_folder(path)

    def _show_favorites_menu(self, pos: QPoint):
        item = self.favorites_list.itemAt(pos)
        if not item: return

        path = item.data(Qt.ItemDataRole.UserRole)
        if path is None: return

        menu = QMenu()
        menu.addAction(qta.icon('fa5s.folder-open'), "Open as Project",
                       partial(self.main_window._action_open_folder, path))
        is_user_favorite = path in settings_manager.get("favorites", [])
        if is_user_favorite:
            menu.addAction(qta.icon('fa5s.trash-alt'), "Remove from Favorites", partial(self._remove_favorite, path))
        menu.exec(self.favorites_list.mapToGlobal(pos))

    def _remove_favorite(self, path: str):
        favorites = settings_manager.get("favorites", [])
        if path in favorites:
            favorites.remove(path)
            settings_manager.set("favorites", favorites)
            self._populate_favorites()

    def _on_project_tab_changed(self, index: int):
        path = self.project_tabs.tabToolTip(index) if index != -1 else None
        self.project_manager.set_active_project(path)
        self.main_window._update_window_title()

    def _action_close_project_by_index(self, index: int):
        if 0 <= index < self.project_tabs.count():
            path = self.project_tabs.tabToolTip(index)
            self.project_manager.close_project(path)
            self.refresh_project_views()


def initialize(puffin_api):
    return ProjectExplorerPlugin(puffin_api)
```

### File: `/plugins/project_explorer/project_explorer_panel.py`

#### Linter Issues Found:
```

- L6 (E501) No message available

- L7 (E501) No message available

- L9 (F401) No message available

- L9 (F401) No message available

- L9 (E501) No message available

- L25 (E501) No message available

- L26 (E501) No message available

- L27 (E501) No message available

- L28 (E501) No message available

- L29 (E501) No message available

- L30 (E501) No message available

- L31 (E501) No message available

- L32 (E501) No message available

- L44 (E501) No message available

- L45 (E501) No message available

- L46 (E501) No message available

- L47 (E501) No message available

- L48 (E501) No message available

- L49 (E501) No message available

- L54 (E501) No message available

- L56 (E501) No message available

- L61 (E501) No message available

- L87 (E501) No message available

- L89 (E501) No message available

- L90 (E501) No message available

- L97 (E703) No message available

- L99 (E703) No message available

- L100 (E703) No message available

- L103 (E703) No message available

- L105 (E703) No message available

- L107 (E703) No message available

- L114 (E501) No message available

- L116 (E501) No message available

- L126 (E703) No message available

- L127 (E703) No message available

- L129 (E703) No message available

- L130 (E703) No message available

- L133 (E703) No message available

- L136 (E501) No message available

- L136 (E703) No message available

- L139 (E501) No message available

- L139 (E703) No message available

- L141 (E703) No message available

- L144 (E501) No message available

- L146 (E703) No message available

- L148 (E703) No message available

- L154 (E703) No message available

- L155 (E703) No message available

- L157 (E701) No message available

- L157 (E702) No message available

- L161 (E501) No message available

- L166 (E501) No message available

- L170 (E501) No message available

- L172 (E501) No message available

- L173 (E501) No message available

- L176 (E501) No message available

- L177 (E501) No message available

- L189 (E501) No message available

- L199 (E703) No message available

- L200 (E703) No message available

- L205 (E501) No message available

- L206 (E501) No message available

- L210 (E501) No message available

- L211 (E501) No message available

- L218 (E701) No message available

- L218 (E501) No message available

- L229 (E501) No message available

- L230 (E703) No message available

- L235 (E501) No message available

- L239 (E501) No message available

- L240 (E701) No message available

- L241 (E501) No message available

- L245 (E501) No message available

- L250 (E501) No message available

- L255 (E501) No message available

- L256 (E501) No message available

- L260 (E501) No message available

- L261 (E501) No message available

- L265 (E501) No message available

- L266 (E501) No message available

- L268 (E501) No message available

- L269 (E501) No message available

- L271 (E501) No message available

- L272 (E501) No message available

- L276 (E501) No message available

- L277 (E501) No message available

- L284 (E501) No message available

- L285 (E501) No message available

- L286 (E701) No message available

- L290 (E501) No message available

- L291 (E129) No message available

- L293 (E701) No message available

- L298 (E501) No message available

- L299 (E501) No message available

- L300 (E501) No message available

- L302 (E701) No message available

- L306 (E701) No message available

- L310 (E701) No message available

- L319 (W292) No message available

```


```python
# PuffinPyEditor/plugins/project_explorer/project_explorer_panel.py
import os
from functools import partial

# PyQt6 imports
from PyQt6.QtGui import (QFileSystemModel, QPainter, QPen, QColor, QPainterPath)
from PyQt6.QtWidgets import (QTreeView, QMenu, QInputDialog, QWidget, QVBoxLayout,
                             QFileIconProvider, QMessageBox)
from PyQt6.QtCore import (QDir, Qt, pyqtSignal, QModelIndex, QPoint, QRect, QPointF, QRectF, QTimer)

# Third-party imports
import qtawesome as qta

# Local imports
from app_core.file_handler import FileHandler
from app_core.theme_manager import ThemeManager


class CustomFileIconProvider(QFileIconProvider):
    def __init__(self, theme_manager):
        super().__init__()
        self.theme_manager = theme_manager
        self.project_root_path = None
        self._icon_map = {
            ".py": "mdi.language-python", ".js": "mdi.language-javascript", ".ts": "mdi.language-typescript",
            ".java": "mdi.language-java", ".cs": "mdi.language-csharp", ".cpp": "mdi.language-cpp",
            ".hpp": "mdi.language-cpp", ".h": "mdi.language-cpp", ".rs": "mdi.language-rust",
            ".html": "mdi.language-html5", ".css": "mdi.language-css3", ".scss": "mdi.language-css3",
            ".json": "mdi.code-json", ".md": "mdi.markdown", ".yaml": "mdi.yaml", ".yml": "mdi.yaml",
            ".xml": "mdi.xml", ".gitignore": "mdi.git", ".git": "mdi.git", "Dockerfile": "mdi.docker",
            ".dockerignore": "mdi.docker", ".txt": "mdi.file-document-outline", ".log": "mdi.file-document-outline",
            "__pycache__": "fa5s.archive", "venv": "fa5s.box-open", ".venv": "fa5s.box-open",
            "dist": "fa5s.box-open", "node_modules": "mdi.folder-npm-outline",
        }

    def set_project_root_path(self, path: str):
        self.project_root_path = path

    def icon(self, fileInfo):
        colors = self.theme_manager.current_theme_data.get('colors', {})
        base_color = colors.get('icon.foreground', '#d0d0d0')
        accent_color = colors.get('accent', '#be5046')
        color_palette = {
            ".py": "#4B8BBE", ".js": "#F7DF1E", ".ts": "#3178C6", ".java": "#B07219", ".cs": "#68217A",
            ".cpp": "#689AD6", ".hpp": "#689AD6", ".h": "mdi.language-cpp", ".rs": "#DEA584", ".html": "#E34F26",
            ".css": "#1572B6", ".scss": "#1572B6", ".json": "#FBC02D", ".md": "#90A4AE", ".yaml": "#A0A0A0",
            ".yml": "#A0A0A0", ".xml": "#009900", ".gitignore": "#F44336", ".git": "#F44336",
            "Dockerfile": "#2496ED", ".dockerignore": "#2496ED", "__pycache__": "#546E7A",
            "venv": "#546E7A", ".venv": "#546E7A", "dist": "#546E7A", "node_modules": "#CB3837",
        }
        file_name = fileInfo.fileName()
        file_path = fileInfo.filePath()
        if file_path == self.project_root_path and fileInfo.isDir():
            return qta.icon('mdi.folder-home-outline', color=accent_color, scale_factor=1.1)
        if file_name in self._icon_map:
            return qta.icon(self._icon_map[file_name], color=color_palette.get(file_name, base_color))
        if fileInfo.isDir():
            return qta.icon('mdi.folder-outline', color=base_color)
        _, ext = os.path.splitext(file_name)
        if ext in self._icon_map:
            return qta.icon(self._icon_map[ext], color=color_palette.get(ext, base_color))
        return qta.icon('mdi.file-outline', color=base_color)


class FileTree(QTreeView):
    def __init__(self, model, theme_manager, parent=None):
        super().__init__(parent)
        self.setModel(model)
        self.theme_manager = theme_manager
        self.setAnimated(True)
        self.setIndentation(20)
        self.setSortingEnabled(True)
        self.sortByColumn(0, Qt.SortOrder.AscendingOrder)
        self.setHeaderHidden(True)
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.setDropIndicatorShown(True)
        self.setDragDropMode(self.DragDropMode.InternalMove)
        self.setRootIsDecorated(False)
        for i in range(1, self.model().columnCount()):
            self.setColumnHidden(i, True)

    def paintEvent(self, event):
        painter = QPainter(self.viewport())
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        colors = self.theme_manager.current_theme_data.get('colors', {})
        bus_color = QColor(colors.get('tree.indentationGuides.stroke', '#5c6370'))
        trace_color = QColor(colors.get('tree.trace.color', '#be5046'))
        shadow_color = QColor(colors.get('tree.trace.shadow', bus_color.lighter(120)))
        model, indent, offset = self.model(), self.indentation(), self.header().offset()
        bus_width, trace_thickness, node_chip_size = 1.0, 1.2, 4.0
        shadow_offset, kink_size = QPointF(1.0, 1.0), 5.0
        current_index = self.indexAt(QPoint(0, 0))
        while current_index.isValid():
            rect = self.visualRect(current_index)
            if not rect.isValid() or rect.height() == 0:
                current_index = self.indexBelow(current_index);
                continue
            depth = self._get_depth(current_index);
            y_connect = rect.center().y();
            stem_x = offset + (indent * depth) + (indent // 2)
            opacity = max(0.4, 1.0 - depth * 0.15)
            faded_bus_color = QColor(bus_color);
            faded_bus_color.setAlphaF(opacity * 0.7)
            faded_trace_color = QColor(trace_color);
            faded_trace_color.setAlphaF(opacity)
            faded_shadow_color = QColor(shadow_color);
            faded_shadow_color.setAlphaF(opacity * 0.4)
            painter.setPen(QPen(faded_bus_color, bus_width))
            ancestor_index = current_index.parent()
            for i in range(depth):
                if self._has_siblings_below(ancestor_index):
                    parent_bus_x = offset + (indent * i) + (indent // 2)
                    painter.drawLine(QPointF(parent_bus_x, rect.top()), QPointF(parent_bus_x, rect.bottom()))
                ancestor_index = ancestor_index.parent()
            painter.drawLine(QPointF(stem_x, rect.top()), QPointF(stem_x, rect.bottom()))

            # Correctly define points for the schematic trace
            start_p = QPointF(stem_x, y_connect)
            end_p = QPointF(rect.left() - 6, y_connect)
            kink_dir = -1 if current_index.row() % 2 == 0 else 1
            p1, p2 = start_p, QPointF(start_p.x() + kink_size, start_p.y())
            p3 = QPointF(p2.x() + kink_size, p2.y() + kink_size * kink_dir)
            p4, p5 = QPointF(end_p.x() - kink_size, p3.y()), end_p

            trace_path = QPainterPath();
            trace_path.moveTo(p1);
            trace_path.lineTo(p2)
            trace_path.lineTo(p3);
            trace_path.lineTo(p4);
            trace_path.lineTo(p5)

            shadow_path = QPainterPath(trace_path);
            shadow_path.translate(shadow_offset)
            painter.setPen(
                QPen(faded_shadow_color, trace_thickness * 1.5, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin));
            painter.drawPath(shadow_path)
            painter.setPen(
                QPen(faded_trace_color, trace_thickness, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin));
            painter.drawPath(trace_path)
            painter.setPen(Qt.PenStyle.NoPen);
            painter.setBrush(faded_bus_color)
            painter.drawRect(
                QRectF(stem_x - node_chip_size / 2, y_connect - node_chip_size / 2, node_chip_size, node_chip_size))
            if model.hasChildren(current_index):
                char = "−" if self.isExpanded(current_index) else "+";
                char_rect = QRectF(end_p.x() - 8, y_connect - 8, 16, 16)
                painter.setPen(faded_trace_color);
                painter.drawText(char_rect, Qt.AlignmentFlag.AlignCenter, char)
            current_index = self.indexBelow(current_index)
        super().paintEvent(event)

    def _get_depth(self, index: QModelIndex) -> int:
        depth = 0;
        p = index.parent();
        root = self.rootIndex()
        while p.isValid() and p != root: depth += 1; p = p.parent()
        return depth

    def _has_siblings_below(self, index: QModelIndex) -> bool:
        return index.isValid() and index.row() < self.model().rowCount(index.parent()) - 1

    def update_theme(self, colors):
        self.setStyleSheet(f"""
            QTreeView {{
                background-color: transparent; color: {colors.get('sidebar.foreground', '#d0d0d0')};
                border: none; outline: 0px; font-size: 9.5pt;
            }}
            QTreeView::item {{ padding: 4px 5px; border-radius: 4px; }}
            QTreeView::item:hover {{ background-color: {colors.get('list.hoverBackground', '#3a4149')}; }}
            QTreeView::item:selected:active {{
                background-color: {colors.get('list.activeSelectionBackground', '#4a5160')};
                color: {colors.get('list.activeSelectionForeground', '#ffffff')};
            }}
            QTreeView::item:selected:!active {{
                background-color: {colors.get('list.inactiveSelectionBackground', '#3a4149')};
                color: {colors.get('list.inactiveSelectionForeground', '#d0d0d0')};
            }}
            QTreeView::branch {{ background: transparent; }}
        """)
        self.viewport().update()


class FileTreeViewWidget(QWidget):
    file_open_requested = pyqtSignal(str)
    file_to_open_created = pyqtSignal(str)
    favorites_updated = pyqtSignal()

    def __init__(self, file_handler: FileHandler, theme_manager: ThemeManager, parent=None):
        super().__init__(parent)
        self.file_handler = file_handler
        self.theme_manager = theme_manager
        self.project_root_path = None
        self._setup_ui()
        self._connect_signals()
        self.update_theme()

    def _setup_ui(self):
        layout = QVBoxLayout(self);
        layout.setContentsMargins(0, 0, 0, 0);
        layout.setSpacing(0)
        self.file_system_model = QFileSystemModel()
        self.icon_provider = CustomFileIconProvider(self.theme_manager)
        self.file_system_model.setIconProvider(self.icon_provider)
        self.file_system_model.setFilter(QDir.Filter.AllDirs | QDir.Filter.NoDotAndDotDot | QDir.Filter.AllEntries)
        self.tree_view = FileTree(self.file_system_model, self.theme_manager, self)
        layout.addWidget(self.tree_view)

    def _connect_signals(self):
        self.tree_view.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.tree_view.customContextMenuRequested.connect(self._show_context_menu)
        self.tree_view.doubleClicked.connect(self._on_item_double_clicked)

    def update_theme(self):
        colors = self.theme_manager.current_theme_data.get('colors', {})
        self.tree_view.update_theme(colors)
        self.icon_provider = CustomFileIconProvider(self.theme_manager)
        if self.project_root_path: self.icon_provider.set_project_root_path(self.project_root_path)
        self.file_system_model.setIconProvider(self.icon_provider)
        self.tree_view.viewport().update()

    def set_project_root(self, path: str | None):
        if path and QDir(path).exists():
            self.project_root_path = path
            self.icon_provider.set_project_root_path(self.project_root_path)
            root_index = self.file_system_model.setRootPath(path)
            self.tree_view.setRootIndex(root_index)
        else:
            self.project_root_path, self.icon_provider.project_root_path = None, None
            self.file_system_model.setRootPath("");
            self.tree_view.setRootIndex(QModelIndex())

    def _on_item_double_clicked(self, index: QModelIndex):
        if index.isValid() and not self.file_system_model.isDir(index):
            self.file_open_requested.emit(self.file_system_model.filePath(index))

    def _show_context_menu(self, position: QPoint):
        index = self.tree_view.indexAt(position)
        clicked_path = self.file_system_model.filePath(index) if index.isValid() else self.project_root_path
        if not clicked_path: return
        target_dir = clicked_path if not index.isValid() or self.file_system_model.isDir(index) else os.path.dirname(
            clicked_path)

        menu = QMenu()
        menu.addAction(qta.icon('mdi.file-plus-outline'), "New File...", partial(self._action_new_file, target_dir))
        menu.addAction(qta.icon('mdi.folder-plus-outline'), "New Folder...",
                       partial(self._action_new_folder, target_dir))

        paste_action = menu.addAction(qta.icon('mdi.content-paste'), "Paste")
        paste_action.setEnabled(self.file_handler.get_clipboard_status() is not None)
        paste_action.triggered.connect(partial(self._action_paste, target_dir))

        if index.isValid():
            menu.addSeparator()
            menu.addAction(qta.icon('mdi.content-cut'), "Cut", partial(self.file_handler.cut_item, clicked_path))
            menu.addAction(qta.icon('mdi.content-copy'), "Copy", partial(self.file_handler.copy_item, clicked_path))
            menu.addAction(qta.icon('mdi.content-duplicate'), "Duplicate",
                           partial(self._action_duplicate, clicked_path))
            menu.addSeparator()
            menu.addAction(qta.icon('mdi.pencil-outline'), "Rename...", partial(self._action_rename, clicked_path))
            menu.addAction(qta.icon('mdi.trash-can-outline', color='crimson'), "Delete",
                           partial(self._action_delete, clicked_path))
            menu.addSeparator()
            if os.path.isdir(clicked_path):
                fav_action = menu.addAction(qta.icon('mdi.star-outline'), "Add to Favorites")
                fav_action.triggered.connect(partial(self._action_add_to_favorites, clicked_path))
            menu.addSeparator()
            menu.addAction(qta.icon('mdi.folder-search-outline'), "Reveal in File Explorer",
                           partial(self.file_handler.reveal_in_explorer, clicked_path))
            if os.path.isfile(clicked_path):
                menu.addAction(qta.icon('mdi.open-in-new'), "Open in Default App",
                               partial(self.file_handler.open_with_default_app, clicked_path))
        menu.exec(self.tree_view.viewport().mapToGlobal(position))

    def _action_new_file(self, base_path: str):
        if (name := QInputDialog.getText(self, "New File", "Enter file name:")[0]):
            success, error = self.file_handler.create_file(os.path.join(base_path, name))
            if success:
                self.file_to_open_created.emit(os.path.join(base_path, name))
            else:
                QMessageBox.warning(self, "Error", error)

    def _action_new_folder(self, base_path: str):
        if (name := QInputDialog.getText(self, "New Folder", "Enter folder name:")[0]):
            success, error = self.file_handler.create_folder(os.path.join(base_path, name))
            if not success: QMessageBox.warning(self, "Error", error)

    def _action_rename(self, path: str):
        current_name = os.path.basename(path)
        if (new_name := QInputDialog.getText(self, "Rename", "Enter new name:", text=current_name)[
            0]) and new_name != current_name:
            success, result = self.file_handler.rename_item(path, new_name)
            if not success: QMessageBox.warning(self, "Error", result)

    def _action_delete(self, path: str):
        is_dir = os.path.isdir(path)
        if QMessageBox.question(self, "Confirm Delete",
                                f"Are you sure you want to permanently delete this {'folder' if is_dir else 'file'}?\n\n'{os.path.basename(path)}'",
                                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.Cancel,
                                QMessageBox.StandardButton.Cancel) == QMessageBox.StandardButton.Yes:
            success, error = self.file_handler.delete_item(path)
            if not success: QMessageBox.warning(self, "Error", error)

    def _action_duplicate(self, path: str):
        success, error = self.file_handler.duplicate_item(path)
        if not success: QMessageBox.warning(self, "Error", error)

    def _action_paste(self, dest_dir: str):
        success, error = self.file_handler.paste_item(dest_dir)
        if not success: QMessageBox.warning(self, "Error", error)

    def _action_add_to_favorites(self, path: str):
        from app_core.settings_manager import settings_manager
        favorites = settings_manager.get("favorites", [])
        norm_path = os.path.normpath(path)
        if norm_path not in favorites:
            favorites.append(norm_path)
            settings_manager.set("favorites", favorites)
            self.favorites_updated.emit()
```

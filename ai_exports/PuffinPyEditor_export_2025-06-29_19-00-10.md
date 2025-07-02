# Project Export: PuffinPyEditor
## Export Timestamp: 2025-06-29T19:00:10.811313
---

## Golden Rules
1. Only edit and add features, the only features should stay unless asked to be removed, or may be completely redundant.
2. any scripts over 1000 lines, please write in a new response.
3. multiple scripts together exceeding 2000 lines together need to be separated into smaller responses, (example: these scripts have 2340 lines together I'm going to separate it into 2 messages that way i dont lose formatting and dont accidentally remove any features)
4. Do not remove any code that is unrelated to the fix, only remove code if it is being substituted or is not needed anymore.

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

- L3 (F401) No message available

- L3 (E501) No message available

- L13 (E701) No message available

- L33 (E703) No message available

- L34 (E703) No message available

- L36 (E703) No message available

- L39 (E501) No message available

- L40 (E703) No message available

- L41 (E703) No message available

- L42 (E703) No message available

- L49 (E703) No message available

- L51 (E501) No message available

- L53 (E703) No message available

- L55 (E701) No message available

- L55 (E501) No message available

- L59 (E701) No message available

- L59 (E501) No message available

- L62 (E501) No message available

- L64 (E501) No message available

- L70 (E501) No message available

- L70 (E701) No message available

- L83 (E501) No message available

- L84 (E501) No message available

- L91 (E501) No message available

- L92 (E501) No message available

- L93 (E501) No message available

- L94 (E501) No message available

- L96 (E501) No message available

- L98 (E701) No message available

- L100 (E701) No message available

- L112 (E701) No message available

- L122 (W292) No message available

```


```python
# PuffinPyEditor/plugins/project_explorer/plugin_main.py
import os
from PyQt6.QtWidgets import (QDockWidget, QTabWidget, QWidget, QVBoxLayout, QMenu, QStackedWidget)
from PyQt6.QtCore import Qt, pyqtSignal, QModelIndex
from .project_explorer_panel import FileTreeViewWidget, FullPathRole, IsDirRole


class NoProjectViewWidget(FileTreeViewWidget):
    """A specialized tree view for the 'no project open' view."""
    folder_open_requested = pyqtSignal(str)

    def _on_item_double_clicked(self, index: QModelIndex):
        if not index.isValid(): return
        path = index.data(FullPathRole)
        is_dir = index.data(IsDirRole) is True
        if path:
            if is_dir:
                self.folder_open_requested.emit(path)
            else:
                self.file_open_requested.emit(path)


class ProjectExplorerPlugin:
    def __init__(self, puffin_api):
        self.api = puffin_api
        self.main_window = self.api.get_main_window()
        self.project_manager = self.api.get_manager("project")
        self.file_handler = self.api.get_manager("file_handler")
        self.theme_manager = self.api.get_manager("theme")
        self._setup_ui()

    def _setup_ui(self):
        container = QWidget();
        container_layout = QVBoxLayout(container);
        container_layout.setContentsMargins(0, 0, 0, 0)
        self.stacked_widget = QStackedWidget();
        container_layout.addWidget(self.stacked_widget)

        self.no_project_view = NoProjectViewWidget(self.file_handler, self.theme_manager, self.main_window)
        self.project_tabs = QTabWidget();
        self.project_tabs.setDocumentMode(True);
        self.project_tabs.setTabsClosable(True);
        self.project_tabs.setMovable(True)

        self.stacked_widget.addWidget(self.no_project_view)
        self.stacked_widget.addWidget(self.project_tabs)

        self.file_tree_dock = QDockWidget("Project Explorer", self.main_window)
        self.file_tree_dock.setObjectName("ProjectExplorerDock");
        self.file_tree_dock.setWidget(container)
        self.main_window.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.file_tree_dock)

        toggle_action = self.file_tree_dock.toggleViewAction();
        toggle_action.setShortcut("Ctrl+Shift+E")
        if hasattr(self.main_window, 'view_menu'): self.main_window.view_menu.addAction(toggle_action)

        self._connect_signals()
        self.refresh_project_views()
        if not self.project_manager.get_open_projects(): self.file_tree_dock.close()

    def _connect_signals(self):
        self.project_tabs.tabCloseRequested.connect(self._action_close_project_by_index)
        self.project_tabs.currentChanged.connect(self._on_project_tab_changed)
        self.no_project_view.folder_open_requested.connect(self._on_no_project_folder_activated)
        self.main_window.theme_changed_signal.connect(self.update_all_themes)

    def update_all_themes(self, theme_id: str):
        self.no_project_view.update_theme()
        for i in range(self.project_tabs.count()):
            if isinstance(widget := self.project_tabs.widget(i), FileTreeViewWidget): widget.update_theme()

    def refresh_project_views(self):
        open_projects = self.project_manager.get_open_projects()
        if not open_projects:
            self.stacked_widget.setCurrentWidget(self.no_project_view)
            self.no_project_view.set_project_root(None)
            return

        self.stacked_widget.setCurrentWidget(self.project_tabs)
        active_project = self.project_manager.get_active_project_path()
        self.project_tabs.blockSignals(True)

        current_trees = {w.project_root_path: w for i in range(self.project_tabs.count()) if
                         isinstance(w := self.project_tabs.widget(i), FileTreeViewWidget)}
        self.project_tabs.clear()

        active_index = -1
        for i, path in enumerate(open_projects):
            tree = current_trees.get(path)
            if not tree:
                tree = FileTreeViewWidget(self.file_handler, self.theme_manager, self.main_window)
                tree.file_open_requested.connect(self.main_window._action_open_file)
                tree.file_to_open_created.connect(self.main_window._add_new_tab)
            tree.set_project_root(path)  # This is now a fast and synchronous call.

            tab_index = self.project_tabs.addTab(tree, os.path.basename(path).upper())
            self.project_tabs.setTabToolTip(tab_index, path)
            if path == active_project: active_index = i

        if active_index != -1: self.project_tabs.setCurrentIndex(active_index)
        self.project_tabs.blockSignals(False)
        self._on_project_tab_changed(self.project_tabs.currentIndex())

    def _on_no_project_folder_activated(self, path: str):
        if path and os.path.isdir(path):
            self.project_manager.open_project(path)
            self.main_window._broadcast_project_change()

    def _on_project_tab_changed(self, index: int):
        path = self.project_tabs.tabToolTip(index) if index != -1 else None
        self.project_manager.set_active_project(path)
        if self.main_window: self.main_window._update_window_title()

    def _action_close_project_by_index(self, index: int):
        if 0 <= index < self.project_tabs.count():
            path = self.project_tabs.tabToolTip(index)
            self.project_manager.close_project(path)
            self.main_window._broadcast_project_change()


def initialize(puffin_api):
    return ProjectExplorerPlugin(puffin_api)
```

### File: `/plugins/project_explorer/project_explorer_panel.py`

#### Linter Issues Found:
```

- L4 (W291) No message available

- L6 (F401) No message available

- L6 (W291) No message available

- L7 (W291) No message available

- L9 (F401) No message available

- L9 (W291) No message available

- L10 (E128) No message available

- L12 (F401) No message available

- L20 (E302) No message available

- L25 (E501) No message available

- L26 (E501) No message available

- L27 (E501) No message available

- L28 (E501) No message available

- L29 (E501) No message available

- L30 (E501) No message available

- L33 (E501) No message available

- L43 (E702) No message available

- L44 (W293) No message available

- L52 (W293) No message available

- L55 (E302) No message available

- L66 (E501) No message available

- L69 (W293) No message available

- L73 (W293) No message available

- L76 (E501) No message available

- L78 (W293) No message available

- L82 (E702) No message available

- L87 (W293) No message available

- L92 (E702) No message available

- L92 (E501) No message available

- L93 (W293) No message available

- L97 (E501) No message available

- L98 (W293) No message available

- L102 (E501) No message available

- L104 (E702) No message available

- L104 (E702) No message available

- L105 (E501) No message available

- L108 (W293) No message available

- L109 (E501) No message available

- L111 (E702) No message available

- L111 (E501) No message available

- L112 (E501) No message available

- L113 (E501) No message available

- L114 (E702) No message available

- L114 (E501) No message available

- L115 (W293) No message available

- L116 (E501) No message available

- L118 (E501) No message available

- L119 (E225) No message available

- L119 (E501) No message available

- L120 (E225) No message available

- L120 (E702) No message available

- L120 (E702) No message available

- L120 (E501) No message available

- L121 (W293) No message available

- L122 (E501) No message available

- L123 (E501) No message available

- L125 (E225) No message available

- L125 (E501) No message available

- L125 (E702) No message available

- L126 (W293) No message available

- L127 (E225) No message available

- L127 (E501) No message available

- L129 (E225) No message available

- L129 (E702) No message available

- L129 (E501) No message available

- L129 (E231) No message available

- L129 (E231) No message available

- L129 (E231) No message available

- L130 (E225) No message available

- L130 (E231) No message available

- L130 (E501) No message available

- L130 (E702) No message available

- L130 (E702) No message available

- L130 (E702) No message available

- L130 (E702) No message available

- L130 (E231) No message available

- L130 (E231) No message available

- L131 (W293) No message available

- L135 (E702) No message available

- L135 (E501) No message available

- L136 (E501) No message available

- L138 (W293) No message available

- L139 (E701) No message available

- L140 (E501) No message available

- L141 (E702) No message available

- L141 (E501) No message available

- L141 (E702) No message available

- L141 (E227) No message available

- L142 (W293) No message available

- L143 (E501) No message available

- L144 (E225) No message available

- L145 (E225) No message available

- L146 (E225) No message available

- L147 (E501) No message available

- L149 (E302) No message available

- L151 (E702) No message available

- L151 (E702) No message available

- L151 (E501) No message available

- L151 (E231) No message available

- L151 (E702) No message available

- L151 (E702) No message available

- L151 (E702) No message available

- L151 (E702) No message available

- L151 (E702) No message available

- L152 (E702) No message available

- L152 (E501) No message available

- L152 (E702) No message available

- L152 (E702) No message available

- L154 (W293) No message available

- L156 (F841) No message available

- L156 (E501) No message available

- L157 (E501) No message available

- L157 (E702) No message available

- L158 (W293) No message available

- L164 (E702) No message available

- L164 (E501) No message available

- L164 (E702) No message available

- L165 (E501) No message available

- L166 (E702) No message available

- L169 (E302) No message available

- L170 (E231) No message available

- L170 (E231) No message available

- L171 (W293) No message available

- L173 (E702) No message available

- L173 (E231) No message available

- L173 (E225) No message available

- L173 (E501) No message available

- L173 (E231) No message available

- L173 (E702) No message available

- L173 (E231) No message available

- L173 (E225) No message available

- L173 (E702) No message available

- L173 (E231) No message available

- L173 (E702) No message available

- L173 (E231) No message available

- L174 (W293) No message available

- L176 (E702) No message available

- L177 (E702) No message available

- L177 (E501) No message available

- L177 (E702) No message available

- L177 (E702) No message available

- L177 (E702) No message available

- L178 (W293) No message available

- L181 (E501) No message available

- L181 (E702) No message available

- L183 (W293) No message available

- L185 (E501) No message available

- L185 (E702) No message available

- L186 (W293) No message available

- L188 (E701) No message available

- L188 (E501) No message available

- L189 (E501) No message available

- L190 (E701) No message available

- L190 (E501) No message available

- L192 (W293) No message available

- L194 (E225) No message available

- L195 (E225) No message available

- L196 (E701) No message available

- L196 (E501) No message available

- L196 (E231) No message available

- L196 (E231) No message available

- L198 (E301) No message available

- L199 (E701) No message available

- L199 (E501) No message available

- L200 (E701) No message available

- L200 (E501) No message available

- L201 (W293) No message available

- L203 (E702) No message available

- L204 (E701) No message available

- L206 (E501) No message available

- L206 (E702) No message available

- L206 (E702) No message available

- L206 (E702) No message available

- L207 (W293) No message available

- L208 (E501) No message available

- L211 (E701) No message available

- L213 (E225) No message available

- L213 (E702) No message available

- L213 (E231) No message available

- L213 (E501) No message available

- L213 (E702) No message available

- L213 (E231) No message available

- L213 (E231) No message available

- L213 (E702) No message available

- L213 (E231) No message available

- L213 (E225) No message available

- L213 (E702) No message available

- L213 (E231) No message available

- L213 (E702) No message available

- L213 (E231) No message available

- L213 (E702) No message available

- L213 (E231) No message available

- L213 (E702) No message available

- L213 (E231) No message available

- L214 (W293) No message available

- L215 (E701) No message available

- L215 (E231) No message available

- L215 (E702) No message available

- L215 (E501) No message available

- L215 (E225) No message available

- L215 (E231) No message available

- L215 (E231) No message available

- L215 (E702) No message available

- L215 (E702) No message available

- L216 (E701) No message available

- L216 (E231) No message available

- L216 (E702) No message available

- L216 (E501) No message available

- L216 (E225) No message available

- L216 (E231) No message available

- L216 (E231) No message available

- L216 (E702) No message available

- L217 (W293) No message available

- L218 (E702) No message available

- L218 (E501) No message available

- L218 (E702) No message available

- L223 (E701) No message available

- L223 (E501) No message available

- L224 (E701) No message available

- L224 (E501) No message available

- L226 (E231) No message available

- L226 (E231) No message available

- L226 (E231) No message available

- L226 (E225) No message available

- L226 (E702) No message available

- L226 (E231) No message available

- L226 (E501) No message available

- L226 (E702) No message available

- L226 (E231) No message available

- L226 (E231) No message available

- L226 (E702) No message available

- L226 (E231) No message available

- L226 (E231) No message available

- L226 (E702) No message available

- L226 (E231) No message available

- L226 (E702) No message available

- L226 (E231) No message available

- L226 (E227) No message available

- L226 (E702) No message available

- L226 (E231) No message available

- L227 (W293) No message available

- L229 (E701) No message available

- L230 (E701) No message available

- L230 (E501) No message available

- L232 (E231) No message available

- L232 (E501) No message available

- L232 (E702) No message available

- L235 (E225) No message available

- L235 (E702) No message available

- L235 (E231) No message available

- L235 (E225) No message available

- L235 (E501) No message available

- L236 (E701) No message available

- L238 (E225) No message available

- L238 (E702) No message available

- L238 (E231) No message available

- L238 (E231) No message available

- L238 (E501) No message available

- L238 (E231) No message available

- L238 (E231) No message available

- L238 (E231) No message available

- L238 (E702) No message available

- L238 (E231) No message available

- L238 (E231) No message available

- L238 (E231) No message available

- L238 (E231) No message available

- L238 (E231) No message available

- L239 (E225) No message available

- L239 (E501) No message available

- L240 (E702) No message available

- L240 (E231) No message available

- L240 (E501) No message available

- L240 (E231) No message available

- L240 (E231) No message available

- L240 (E702) No message available

- L240 (E231) No message available

- L240 (E231) No message available

- L240 (E231) No message available

- L240 (E231) No message available

- L242 (W293) No message available

- L243 (E231) No message available

- L243 (E231) No message available

- L244 (E225) No message available

- L244 (E275) No message available

- L244 (E702) No message available

- L244 (E231) No message available

- L244 (E231) No message available

- L244 (E225) No message available

- L244 (E501) No message available

- L244 (E231) No message available

- L244 (E231) No message available

- L246 (E225) No message available

- L246 (E231) No message available

- L246 (E702) No message available

- L246 (E231) No message available

- L246 (E225) No message available

- L246 (E501) No message available

- L246 (E702) No message available

- L246 (E231) No message available

- L246 (E231) No message available

- L246 (E225) No message available

- L247 (E701) No message available

- L248 (E701) No message available

- L248 (E231) No message available

- L248 (E231) No message available

- L250 (E231) No message available

- L251 (E225) No message available

- L251 (E702) No message available

- L251 (E231) No message available

- L251 (E231) No message available

- L251 (E225) No message available

- L251 (E231) No message available

- L251 (E501) No message available

- L251 (E231) No message available

- L251 (E231) No message available

- L252 (E225) No message available

- L253 (E231) No message available

- L253 (E225) No message available

- L253 (E231) No message available

- L254 (E701) No message available

- L254 (E231) No message available

- L254 (E231) No message available

- L255 (W293) No message available

- L256 (E231) No message available

- L257 (E225) No message available

- L257 (E275) No message available

- L258 (E702) No message available

- L258 (E231) No message available

- L258 (E501) No message available

- L258 (E702) No message available

- L258 (E231) No message available

- L258 (E702) No message available

- L258 (E231) No message available

- L258 (E702) No message available

- L258 (E231) No message available

- L258 (E227) No message available

- L258 (E702) No message available

- L258 (E231) No message available

- L259 (E225) No message available

- L260 (E231) No message available

- L260 (E225) No message available

- L261 (E701) No message available

- L261 (E231) No message available

- L261 (E231) No message available

- L261 (W292) No message available

```


```python
# PuffinPyEditor/plugins/project_explorer/project_explorer_panel.py
import os
from functools import partial
from PyQt6.QtGui import (QPainter, QPen, QColor, QPainterPath, QFont, 
                         QStandardItemModel, QStandardItem, QMouseEvent)
from PyQt6.QtWidgets import (QTreeView, QMenu, QInputDialog, QWidget, 
                             QVBoxLayout, QFileIconProvider, QMessageBox, 
                             QStyledItemDelegate, QStyleOptionViewItem)
from PyQt6.QtCore import (Qt, pyqtSignal, QModelIndex, QPoint, QRect, 
                        QPointF, QSize, QFileSystemWatcher)
import qtawesome as qta
from app_core.file_handler import FileHandler
from app_core.theme_manager import ThemeManager
from utils.logger import log

# --- Custom Model Data Roles ---
FullPathRole = Qt.ItemDataRole.UserRole + 1
IsDirRole = Qt.ItemDataRole.UserRole + 2

class CustomFileIconProvider:
    def __init__(self, theme_manager: ThemeManager):
        super().__init__()
        self.theme_manager = theme_manager
        self._icon_map = {
            ".py": "mdi.language-python", ".js": "mdi.language-javascript", ".ts": "mdi.language-typescript",
            ".java": "mdi.language-java", ".cs": "mdi.language-csharp", ".cpp": "mdi.language-cpp",
            ".hpp": "mdi.language-cpp", ".h": "mdi.language-cpp", ".rs": "mdi.language-rust",
            ".html": "mdi.language-html5", ".css": "mdi.language-css3", ".scss": "mdi.language-css3",
            ".json": "mdi.code-json", ".md": "mdi.markdown", ".yaml": "mdi.yaml", ".yml": "mdi.yaml",
            ".xml": "mdi.xml", ".gitignore": "mdi.git", ".git": "mdi.git", "Dockerfile": "mdi.docker",
            ".dockerignore": "mdi.docker", ".txt": "mdi.file-document-outline",
            ".log": "mdi.file-document-outline", "__pycache__": "fa5s.archive",
            "venv": "fa5s.box-open", ".venv": "fa5s.box-open", "dist": "fa5s.box-open",
            "node_modules": "mdi.folder-npm-outline"
        }

    def get_icon(self, file_path: str):
        theme_colors = self.theme_manager.current_theme_data.get('colors', {})
        icon_colors = theme_colors.get('icon.colors', {})
        global_fallback = theme_colors.get('icon.foreground', '#C0C5CE')
        file_fallback = icon_colors.get("default_file", global_fallback)
        folder_fallback = icon_colors.get("default_folder", global_fallback)
        is_dir = os.path.isdir(file_path); name = os.path.basename(file_path)
        
        if is_dir:
            icon_name = self._icon_map.get(name, 'mdi.folder-outline')
            color = icon_colors.get(name, folder_fallback)
        else:
            _, ext = os.path.splitext(name)
            icon_name = self._icon_map.get(ext, 'mdi.file-outline')
            color = icon_colors.get(ext, file_fallback)
            
        return qta.icon(icon_name, color=color)

class TreeViewDelegate(QStyledItemDelegate):
    def __init__(self, tree_view, theme_manager):
        super().__init__(tree_view)
        self.tree = tree_view
        self.theme_manager = theme_manager

    def sizeHint(self, option, index):
        size = super().sizeHint(option, index)
        size.setHeight(size.height() + 12)
        return size

    def paint(self, painter: QPainter, option: QStyleOptionViewItem, index: QModelIndex):
        painter.save()
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        is_folder = index.data(IsDirRole) is True
        colors = self.theme_manager.current_theme_data.get('colors', {})
        accent_color = QColor(colors.get('accent', '#83c092'))
        
        p3 = self._paint_branch_lines(painter, option, index, accent_color)
        if index.data(Qt.ItemDataRole.DisplayRole) != "(empty)":
            self._paint_final_segment(painter, index, p3, is_folder, accent_color)
        self._paint_content(painter, option, index, p3, accent_color)
        
        painter.restore()

    def _get_depth(self, index: QModelIndex) -> int:
        depth = 0; p = index.parent()
        while p.isValid() and p != self.tree.rootIndex():
            depth += 1
            p = p.parent()
        return depth
        
    def _paint_branch_lines(self, painter, option, index, trace_color: QColor):
        indent, depth = self.tree.indentation(), self._get_depth(index)
        rect, y_center = option.rect, option.rect.center().y()
        opacity = max(0.4, 1.0 - depth * 0.15)
        faded_trace_color = QColor(trace_color); faded_trace_color.setAlphaF(opacity)
        
        for k in range(depth):
            bus_x = k * indent + indent / 2
            painter.setPen(QPen(faded_trace_color, 1.2))
            painter.drawLine(QPointF(bus_x, rect.top()), QPointF(bus_x, rect.bottom()))
            
        p3 = QPointF(depth * indent + indent, y_center + 6.0)
        if depth > 0:
            x_bus_line = (depth - 1) * indent + indent / 2
            p1, p2 = QPointF(x_bus_line, y_center), QPointF(x_bus_line + 6.0, y_center)
            p3 = QPointF(p2.x() + 6.0, y_center + 6.0)
            path = QPainterPath(p1); path.lineTo(p2); path.lineTo(p3)
            painter.setPen(QPen(faded_trace_color, 1.2, cap=Qt.PenCapStyle.RoundCap, join=Qt.PenJoinStyle.RoundJoin))
            painter.drawPath(path)
        return p3
    
    def _paint_final_segment(self, painter, index, start_pos, is_folder, trace_color: QColor):
        depth = self._get_depth(index)
        faded_trace_color = QColor(trace_color); faded_trace_color.setAlphaF(max(0.4, 1.0-depth*0.15))
        end_x = (depth * self.tree.indentation() + self.tree.indentation()) + self.tree.iconSize().width() / 2
        pen = QPen(faded_trace_color, 3.5 if is_folder else 1.2, cap=Qt.PenCapStyle.FlatCap if is_folder else Qt.PenCapStyle.RoundCap)
        painter.setPen(pen); painter.drawLine(start_pos, QPointF(end_x, start_pos.y()))
    
    def _paint_content(self, painter, option, index, conn_point, trace_color: QColor):
        colors = self.theme_manager.current_theme_data.get('colors', {})
        is_selected, depth = option.state & self.tree.style().StateFlag.State_Selected, self._get_depth(index)
        content_start_x=(depth * self.tree.indentation()) + self.tree.indentation()
        content_rect=QRect(option.rect); content_rect.setLeft(content_start_x); content_rect.moveTop(int(conn_point.y() - option.rect.height() / 2))
        
        icon, text = index.data(Qt.ItemDataRole.DecorationRole), index.data(Qt.ItemDataRole.DisplayRole)
        icon_size, icon_rect, text_rect = self.tree.iconSize(), QRect(), QRect(content_rect)
        if icon:
            icon_rect=QRect(content_rect.left()+4, content_rect.center().y()-icon_size.height()//2, icon_size.width(), icon_size.height()); text_rect.setLeft(icon_rect.right() + 4)
            
        text_bounding_rect=painter.fontMetrics().boundingRect(text_rect, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, text)
        if is_selected:
            highlight_area=text_bounding_rect.united(icon_rect); highlight_area.adjust(-4,-2,4,2)
            hcolor=QColor(colors.get('list.activeSelectionBackground','#be5046')); hcolor.setAlphaF(0.35); painter.setBrush(hcolor); painter.setPen(Qt.PenStyle.NoPen); painter.drawRoundedRect(highlight_area,3.0,3.0)
            
        if index.model().hasChildren(index):
            exp_rect = self.get_expander_rect(option, index)
            exp_char = "▼" if self.tree.isExpanded(index) else "▶"
            faded_trace_color = QColor(trace_color); faded_trace_color.setAlphaF(max(0.4, 1.0-depth * 0.15))
            painter.setPen(option.palette.highlightedText().color() if is_selected else faded_trace_color)
            painter.drawText(exp_rect, Qt.AlignmentFlag.AlignCenter, exp_char)
            
        if icon: icon.paint(painter, icon_rect)
        text_color = index.data(Qt.ItemDataRole.ForegroundRole) or (option.palette.highlightedText().color() if is_selected else option.palette.text().color())
        painter.setPen(text_color); painter.setFont(index.data(Qt.ItemDataRole.FontRole) or painter.font()); painter.drawText(text_bounding_rect, Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignVCenter, text)
    
    def get_expander_rect(self, option: QStyleOptionViewItem, index: QModelIndex) -> QRect:
        depth=self._get_depth(index)
        content_start_x=(depth*self.tree.indentation())+self.tree.indentation()
        expander_x_pos=content_start_x-self.tree.indentation()
        return QRect(int(expander_x_pos + 2), int(option.rect.center().y() - 8), 12, 16)

class FileTree(QTreeView):
    def __init__(self, model, theme_manager, parent=None):
        super().__init__(parent); self.setModel(model); self.setItemDelegate(TreeViewDelegate(self,theme_manager)); self.setAnimated(True); self.setIndentation(15); self.setIconSize(QSize(16, 16)); self.setSortingEnabled(True); self.sortByColumn(0, Qt.SortOrder.AscendingOrder)
        self.setHeaderHidden(True); self.setDragDropMode(self.DragDropMode.InternalMove); self.setRootIsDecorated(False); self.drawBranches = False
        self.setExpandsOnDoubleClick(False)
    
    def update_theme(self, colors):
        fg, sfg = colors.get('editor.foreground', '#d0d0d0'), colors.get('list.activeSelectionForeground', '#ffffff')
        self.setStyleSheet(f"""QTreeView{{background:transparent;border:none;outline:0;}} QTreeView::item{{color:{fg};background-color:transparent;border:0;}} QTreeView::item:selected{{background-color:transparent;}} QTreeView::branch{{image:none;background:transparent;}}"""); self.viewport().update()
    
    def mousePressEvent(self, event: QMouseEvent):
        index = self.indexAt(event.pos())
        if index.isValid() and self.model().hasChildren(index):
            delegate = self.itemDelegate()
            if hasattr(delegate, 'get_expander_rect'):
                option = QStyleOptionViewItem(); self.initViewItemOption(option); option.rect = self.visualRect(index)
                if delegate.get_expander_rect(option, index).contains(event.pos()):
                    self.setExpanded(index, not self.isExpanded(index)); return
        super().mousePressEvent(event)

class FileTreeViewWidget(QWidget):
    file_open_requested,file_to_open_created = pyqtSignal(str),pyqtSignal(str)
    
    def __init__(self, file_handler, theme_manager, parent=None):
        super().__init__(parent); self.file_handler,self.theme_manager=file_handler,theme_manager;self.project_root_path=None;self._setup_ui();self._connect_signals()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self); layout.setContentsMargins(0, 0, 0, 0)
        self.item_model = QStandardItemModel(); self.tree_view = FileTree(self.item_model, self.theme_manager, self); self.icon_provider = CustomFileIconProvider(self.theme_manager); self.fs_watcher = QFileSystemWatcher(self); layout.addWidget(self.tree_view)
    
    def _connect_signals(self):
        self.tree_view.doubleClicked.connect(self._on_item_double_clicked)
        self.tree_view.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu); self.tree_view.customContextMenuRequested.connect(self._show_context_menu)
        self.fs_watcher.directoryChanged.connect(self._on_directory_changed)
    
    def update_theme(self):
        self.tree_view.update_theme(self.theme_manager.current_theme_data.get('colors', {})); self._populate_tree()
    
    def set_project_root(self, path):
        if self.fs_watcher.directories(): self.fs_watcher.removePaths(self.fs_watcher.directories())
        self.project_root_path = os.path.normpath(path) if path and os.path.isdir(path) else None
        if self.project_root_path: self.fs_watcher.addPath(self.project_root_path)
        self._populate_tree()
    
    def get_expanded_paths(self):
        expanded_paths=set()
        root=QModelIndex()
        for r in range(self.item_model.rowCount(root)): self._check_expansion(self.item_model.index(r,0,root), expanded_paths)
        return expanded_paths
    def _check_expansion(self, index, expanded_set):
        if self.tree_view.isExpanded(index): expanded_set.add(index.data(FullPathRole))
        for r in range(self.item_model.rowCount(index)): self._check_expansion(self.item_model.index(r, 0, index), expanded_set)
        
    def _populate_tree(self):
        expanded_paths = self.get_expanded_paths(); self.item_model.clear()
        if not self.project_root_path: return
        self.tree_view.setUpdatesEnabled(False)
        root_item = self._create_tree_item(os.path.basename(self.project_root_path), self.project_root_path, True); self.item_model.appendRow(root_item); path_map = {self.project_root_path: root_item}; ignore = {'.git', '__pycache__', 'venv', '.venv', 'node_modules', 'dist', 'build'}
        
        for dirpath, dirnames, filenames in os.walk(self.project_root_path, topdown=True):
            dirnames[:] = [d for d in dirnames if d not in ignore]
            parent_item = path_map.get(dirpath)
            if not parent_item: continue
            if not dirnames and not filenames:
                empty=QStandardItem("(empty)");empty.setFlags(Qt.ItemFlag.NoItemFlags);empty.setData(QColor('gray'),Qt.ItemDataRole.ForegroundRole);font=QFont();font.setItalic(True);empty.setFont(font);parent_item.appendRow(empty);continue
            
            for name in sorted(dirnames): fp = os.path.join(dirpath,name); dir_item=self._create_tree_item(name,fp,True); parent_item.appendRow(dir_item); path_map[fp] = dir_item
            for name in sorted(filenames): fp = os.path.join(dirpath,name); file_item=self._create_tree_item(name,fp,False); parent_item.appendRow(file_item)
            
        self._restore_expanded_state(QModelIndex(), expanded_paths); self.tree_view.expand(self.item_model.index(0, 0)); self.tree_view.setUpdatesEnabled(True)

    def _restore_expanded_state(self, parent_index, expanded_paths):
        for r in range(self.item_model.rowCount(parent_index)):
            index = self.item_model.index(r, 0, parent_index)
            if index.data(FullPathRole) in expanded_paths: self.tree_view.expand(index)
            if self.item_model.hasChildren(index): self._restore_expanded_state(index, expanded_paths)

    def _create_tree_item(self,name,path,is_dir): item=QStandardItem(name);item.setEditable(False);item.setData(path,FullPathRole);item.setData(is_dir,IsDirRole);item.setIcon(self.icon_provider.get_icon(path));item.setFlags(Qt.ItemFlag.ItemIsEnabled|Qt.ItemFlag.ItemIsSelectable);return item
    
    def _on_item_double_clicked(self, index):
        if not index.isValid() or index.data(IsDirRole): return
        if path := index.data(FullPathRole): self.file_open_requested.emit(path)

    def _on_directory_changed(self,path): log.info(f"Directory change detected: '{path}'. Refreshing tree."); self._populate_tree()

    def _show_context_menu(self, position):
        index=self.tree_view.indexAt(position);path=self.project_root_path if not index.isValid() else index.data(FullPathRole)
        if not path: return
        target_dir = path if os.path.isdir(path) else os.path.dirname(path)
        menu=QMenu(self);menu.addAction(qta.icon('mdi.file-plus-outline'),"New File...",partial(self._create_item_dialog,target_dir,True));menu.addAction(qta.icon('mdi.folder-plus-outline'),"New Folder...",partial(self._create_item_dialog,target_dir,False))
        if index.isValid() and index.data(Qt.ItemDataRole.DisplayRole)!="(empty)":
            menu.addSeparator(); menu.addAction(qta.icon('mdi.pencil-outline'),"Rename...",partial(self._action_rename,path)); menu.addAction(qta.icon('mdi.trash-can-outline','crimson'),"Delete",partial(self._action_delete,path))
        menu.exec(self.tree_view.viewport().mapToGlobal(position))
    
    def _create_item_dialog(self,base_path,is_file):
        item_type="File"if is_file else"Folder";name,ok=QInputDialog.getText(self,f"New {item_type}",f"Enter {item_type.lower()} name:")
        if ok and name:
            path=os.path.join(base_path,name);handler=self.file_handler.create_file if is_file else self.file_handler.create_folder;success,err=handler(path)
            if success and is_file: self.file_to_open_created.emit(path)
            elif not success: QMessageBox.warning(self,"Error",err)

    def _action_rename(self,path):
        old_name=os.path.basename(path);new_name,ok=QInputDialog.getText(self,"Rename",f"Enter new name for '{old_name}':",text=old_name)
        if ok and new_name and new_name!=old_name:
            success,res=self.file_handler.rename_item(path,new_name)
            if not success: QMessageBox.warning(self,"Error",res)
            
    def _action_delete(self,path):
        thing="folder"if os.path.isdir(path)else"file"
        msg = QMessageBox(self);msg.setText(f"Permanently delete this {thing}?");msg.setInformativeText(f"'{os.path.basename(path)}'");msg.setIcon(QMessageBox.Icon.Warning);msg.setStandardButtons(QMessageBox.StandardButton.Yes|QMessageBox.StandardButton.Cancel);msg.setDefaultButton(QMessageBox.StandardButton.Cancel)
        if msg.exec()==QMessageBox.StandardButton.Yes:
            success,error=self.file_handler.delete_item(path)
            if not success: QMessageBox.warning(self,"Error",error)
```

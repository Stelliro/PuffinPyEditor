# PuffinPyEditor/plugins/project_explorer/project_explorer_panel.py
import os
from functools import partial
from PyQt6.QtGui import (QPainter, QPen, QColor, QPainterPath, QFont, QStandardItemModel, QStandardItem)
from PyQt6.QtWidgets import (QTreeView, QMenu, QInputDialog, QWidget, QVBoxLayout, QFileIconProvider, QMessageBox, QStyledItemDelegate, QStyleOptionViewItem)
from PyQt6.QtCore import (Qt, pyqtSignal, QModelIndex, QPoint, QRect, QPointF, QSize)
import qtawesome as qta
from app_core.file_handler import FileHandler
from app_core.theme_manager import ThemeManager

# Custom roles to store data in our model items
FullPathRole = Qt.ItemDataRole.UserRole + 1
IsDirRole = Qt.ItemDataRole.UserRole + 2

class CustomFileIconProvider:
    """Provides file-specific icons and colors based on the current theme."""
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
        super().__init__(tree_view); self.tree, self.theme_manager = tree_view, theme_manager
    def sizeHint(self, option, index): s=super().sizeHint(option, index);s.setHeight(s.height()+10);return s
    def paint(self, painter, option, index):
        painter.save();painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        is_folder = index.data(IsDirRole) is True
        p3 = self._paint_branch_lines(painter, option, index)
        if index.data(Qt.ItemDataRole.DisplayRole)!="(empty)":self._paint_final_segment(painter,index,p3,is_folder)
        self._paint_content(painter, option, index, p3);painter.restore()
    def _get_depth(self,i):d=0;p=i.parent();
        while p.isValid() and p!=self.tree.rootIndex():d+=1;p=p.parent();
        return d
    def _paint_branch_lines(self,painter,option,index):
        colors=self.theme_manager.current_theme_data.get('colors',{});trace_color=QColor(colors.get('tree.trace.color','#be5046'));indent,depth=self.tree.indentation(),self._get_depth(index);rect,y_center=option.rect,option.rect.center().y();opacity=max(0.4,1.0-depth*0.15);faded_trace_color=QColor(trace_color);faded_trace_color.setAlphaF(opacity)
        for k in range(depth):bus_x=k*indent+indent/2;painter.setPen(QPen(faded_trace_color,1.2));painter.drawLine(QPointF(bus_x,rect.top()),QPointF(bus_x,rect.bottom()))
        p3=QPointF(depth*indent+indent,y_center+6.0)
        if depth>0:
            x_bus_line=(depth-1)*indent+indent/2;p1=QPointF(x_bus_line,y_center);p2=QPointF(p1.x()+6.0,y_center);p3=QPointF(p2.x()+6.0,y_center+6.0)
            path=QPainterPath(p1);path.lineTo(p2);path.lineTo(p3);painter.setPen(QPen(faded_trace_color,1.2,cap=Qt.PenCapStyle.RoundCap,join=Qt.PenJoinStyle.RoundJoin));painter.drawPath(path)
        return p3
    def _paint_final_segment(self,painter,index,start_pos,is_folder):
        colors,depth=self.theme_manager.current_theme_data.get('colors',{}),self._get_depth(index);trace_color=QColor(colors.get('tree.trace.color','#be5046'));faded_trace_color=QColor(trace_color);faded_trace_color.setAlphaF(max(0.4,1.0-depth*0.15))
        end_x=(depth*self.tree.indentation()+self.tree.indentation())+self.tree.iconSize().width()/2
        pen=QPen(faded_trace_color,3.5 if is_folder else 1.2,cap=Qt.PenCapStyle.FlatCap if is_folder else Qt.PenCapStyle.RoundCap);painter.setPen(pen);painter.drawLine(start_pos,QPointF(end_x,start_pos.y()))
    def _paint_content(self,painter,option,index,conn_point):
        colors,is_selected,depth=self.theme_manager.current_theme_data.get('colors',{}),option.state&self.tree.style().StateFlag.State_Selected,self._get_depth(index)
        content_rect=QRect(option.rect);content_rect.setLeft(depth*self.tree.indentation()+self.tree.indentation());content_rect.moveTop(int(conn_point.y()-option.rect.height()/2))
        icon,text=index.data(Qt.ItemDataRole.DecorationRole),index.data(Qt.ItemDataRole.DisplayRole);text_rect=QRect(content_rect)
        if icon:
            icon_rect=QRect(content_rect.left()+4,content_rect.center().y()-self.tree.iconSize().height()//2,self.tree.iconSize().width(),self.tree.iconSize().height())
            text_rect.setLeft(icon_rect.right()+4);icon.paint(painter,icon_rect)
        if is_selected:
            hcolor=QColor(colors.get('list.activeSelectionBackground','#be5046'));hcolor.setAlphaF(0.35);painter.setBrush(hcolor);painter.setPen(Qt.PenStyle.NoPen);painter.drawRoundedRect(text_rect.adjusted(-2,-1,2,1),3.0,3.0)
        if index.model().hasChildren(index):
            exp_char="▼"if self.tree.isExpanded(index)else"▶";exp_rect=QRect(int((depth*self.tree.indentation()+self.tree.indentation()/2)-6),int(option.rect.center().y()-8),12,16)
            painter.setPen(option.palette.highlightedText().color()if is_selected else QColor(colors.get('tree.trace.color','#be5046')));painter.drawText(exp_rect,Qt.AlignmentFlag.AlignCenter,exp_char)
        text_color=index.data(Qt.ItemDataRole.ForegroundRole)or(option.palette.highlightedText().color()if is_selected else option.palette.text().color());painter.setPen(text_color);painter.setFont(index.data(Qt.ItemDataRole.FontRole)or painter.font());painter.drawText(text_rect,Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignVCenter,text)

class FileTree(QTreeView):
    def __init__(self, model, theme_manager, parent=None):
        super().__init__(parent); self.setModel(model); self.setItemDelegate(TreeViewDelegate(self, theme_manager)); self.setAnimated(True); self.setIndentation(15); self.setIconSize(QSize(16,16)); self.setSortingEnabled(True); self.sortByColumn(0, Qt.SortOrder.AscendingOrder)
        self.setHeaderHidden(True); self.setDragDropMode(self.DragDropMode.InternalMove); self.setRootIsDecorated(False); self.drawBranches=False

    def update_theme(self, colors):
        fg = colors.get('editor.foreground', '#d0d0d0')
        sel_fg = colors.get('list.activeSelectionForeground', '#ffffff')
        # --- FIX: Explicitly hide the default branch indicators ---
        self.setStyleSheet(f"""
            QTreeView {{
                background: transparent;
                border: none;
                outline: 0;
            }}
            QTreeView::item {{
                color: {fg};
                background: transparent;
            }}
            QTreeView::item:selected {{
                color: {sel_fg};
                background: transparent;
            }}
            QTreeView::branch {{
                image: none;
                background: transparent;
            }}
        """)
        self.viewport().update()

class FileTreeViewWidget(QWidget):
    file_open_requested=pyqtSignal(str); file_to_open_created=pyqtSignal(str)
    def __init__(self,file_handler,theme_manager,parent=None):
        super().__init__(parent);self.file_handler,self.theme_manager=file_handler,theme_manager;self.project_root_path=None;self._setup_ui();self._connect_signals()
    def _setup_ui(self):
        layout=QVBoxLayout(self);layout.setContentsMargins(0,0,0,0)
        self.item_model=QStandardItemModel();self.tree_view=FileTree(self.item_model,self.theme_manager,self);self.icon_provider=CustomFileIconProvider(self.theme_manager);layout.addWidget(self.tree_view)
    def _connect_signals(self):
        self.tree_view.doubleClicked.connect(self._on_item_double_clicked);self.tree_view.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu);self.tree_view.customContextMenuRequested.connect(self._show_context_menu)
    def update_theme(self):self.tree_view.update_theme(self.theme_manager.current_theme_data.get('colors',{}));self._populate_tree()
    def set_project_root(self,path):self.project_root_path=os.path.normpath(path) if path and os.path.isdir(path)else None;self._populate_tree()
    def _populate_tree(self):
        self.item_model.clear()
        if not self.project_root_path: return
        self.tree_view.setUpdatesEnabled(False)
        root_item = self._create_tree_item(os.path.basename(self.project_root_path),self.project_root_path,True)
        self.item_model.appendRow(root_item)
        path_map={self.project_root_path:root_item}
        ignore={'.git','__pycache__','venv','.venv','node_modules','dist','build'}
        for dirpath,dirnames,filenames in os.walk(self.project_root_path,topdown=True):
            dirnames[:]=[d for d in dirnames if d not in ignore]
            parent_item=path_map.get(dirpath)
            if not parent_item:continue
            if not dirnames and not filenames:
                empty_item=QStandardItem("(empty)");empty_item.setFlags(Qt.ItemFlag.NoItemFlags)
                empty_item.setData(QColor('gray'),Qt.ItemDataRole.ForegroundRole);font=QFont();font.setItalic(True);empty_item.setFont(font);parent_item.appendRow(empty_item);continue
            for name in sorted(dirnames):full_path=os.path.join(dirpath,name);dir_item=self._create_tree_item(name,full_path,True);parent_item.appendRow(dir_item);path_map[full_path]=dir_item
            for name in sorted(filenames):full_path=os.path.join(dirpath,name);file_item=self._create_tree_item(name,full_path,False);parent_item.appendRow(file_item)
        self.tree_view.expand(self.item_model.index(0,0));self.tree_view.setUpdatesEnabled(True)
    def _create_tree_item(self,name,path,is_dir):
        item=QStandardItem(name);item.setEditable(False)
        item.setData(path,FullPathRole);item.setData(is_dir,IsDirRole);item.setIcon(self.icon_provider.get_icon(path))
        item.setFlags(Qt.ItemFlag.ItemIsEnabled|Qt.ItemFlag.ItemIsSelectable);return item
    def _on_item_double_clicked(self,index):
        if not index.isValid():return
        if index.data(IsDirRole):self.tree_view.setExpanded(index,not self.tree_view.isExpanded(index))
        elif path:=index.data(FullPathRole):self.file_open_requested.emit(path)
    def _show_context_menu(self,position):
        index=self.tree_view.indexAt(position);path=self.project_root_path if not index.isValid()else index.data(FullPathRole)
        if not path:return
        target_dir=path if os.path.isdir(path)else os.path.dirname(path)
        menu=QMenu(self);menu.addAction(qta.icon('mdi.file-plus-outline'),"New File...",partial(self._create_item_dialog,target_dir,True));menu.addAction(qta.icon('mdi.folder-plus-outline'),"New Folder...",partial(self._create_item_dialog,target_dir,False))
        if index.isValid()and index.data(Qt.ItemDataRole.DisplayRole)!="(empty)":
            menu.addSeparator();menu.addAction(qta.icon('mdi.pencil-outline'),"Rename...",partial(self._action_rename,path));menu.addAction(qta.icon('mdi.trash-can-outline','crimson'),"Delete",partial(self._action_delete,path))
        menu.exec(self.tree_view.viewport().mapToGlobal(position))
    def _create_item_dialog(self,base_path,is_file):
        item_type="File"if is_file else"Folder";name,ok=QInputDialog.getText(self,f"New {item_type}",f"Enter {item_type.lower()} name:")
        if ok and name:
            path=os.path.join(base_path,name);handler=self.file_handler.create_file if is_file else self.file_handler.create_folder;success,err=handler(path)
            if success:self._populate_tree()
                if is_file:self.file_to_open_created.emit(path)
            else:QMessageBox.warning(self,"Error",err)
    def _action_rename(self,path):
        old_name=os.path.basename(path);new_name,ok=QInputDialog.getText(self,"Rename",f"Enter new name for '{old_name}':",text=old_name)
        if ok and new_name and new_name!=old_name:
            success,res=self.file_handler.rename_item(path,new_name)
            if not success:QMessageBox.warning(self,"Error",res)
            else:self._populate_tree()
    def _action_delete(self,path):
        thing="folder"if os.path.isdir(path)else"file"
        if QMessageBox.question(self,"Confirm Delete",f"Permanently delete this {thing}?\n\n'{os.path.basename(path)}'",QMessageBox.StandardButton.Yes|QMessageBox.StandardButton.Cancel)==QMessageBox.StandardButton.Yes:
            success,error=self.file_handler.delete_item(path)
            if not success:QMessageBox.warning(self,"Error",error)
            else:self._populate_tree()
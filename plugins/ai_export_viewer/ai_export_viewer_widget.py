# PuffinPyEditor/plugins/ai_export_viewer/ai_export_viewer_widget.py
import os
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QListWidget, QListWidgetItem,
    QTextEdit, QPushButton, QMessageBox, QSplitter, QFrame
)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt
from markdown import markdown
import qtawesome as qta
from utils.helpers import get_base_path
from utils.logger import log
from app_core.theme_manager import theme_manager
from app_core.settings_manager import settings_manager


class AIExportViewerWidget(QWidget):
    """
    A widget that displays a list of past AI exports and their content,
    designed to be embedded in a tab.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.export_dir = os.path.join(get_base_path(), "ai_exports")
        self._ensure_export_dir_exists()

        self.setObjectName("AIExportViewerWidget")
        self._setup_ui()
        self._connect_signals()
        self.update_theme()
        self.refresh_list()

    def _setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Toolbar
        toolbar = QFrame()
        toolbar.setObjectName("ExportViewerToolbar")
        toolbar_layout = QHBoxLayout(toolbar)
        toolbar_layout.setContentsMargins(5, 5, 5, 5)

        self.refresh_button = QPushButton(qta.icon('fa5s.sync-alt'), "Refresh")
        self.delete_button = QPushButton(qta.icon('fa5s.trash-alt'), "Delete")
        toolbar_layout.addWidget(self.refresh_button)
        toolbar_layout.addWidget(self.delete_button)
        toolbar_layout.addStretch()
        main_layout.addWidget(toolbar)

        # Main content area
        splitter = QSplitter(Qt.Orientation.Horizontal)
        main_layout.addWidget(splitter)

        # Left pane for the list of exports
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)
        self.export_list_widget = QListWidget()
        self.export_list_widget.setAlternatingRowColors(True)
        left_layout.addWidget(self.export_list_widget)
        splitter.addWidget(left_widget)

        # Right pane for viewing the content of an export
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)
        self.content_view = QTextEdit()
        self.content_view.setReadOnly(True)
        right_layout.addWidget(self.content_view)
        splitter.addWidget(right_widget)

        splitter.setSizes([250, 550])

    def _connect_signals(self):
        self.export_list_widget.currentItemChanged.connect(
            self._on_export_selected
        )
        self.refresh_button.clicked.connect(self.refresh_list)
        self.delete_button.clicked.connect(self._delete_selected_export)

    def _ensure_export_dir_exists(self):
        try:
            os.makedirs(self.export_dir, exist_ok=True)
        except OSError as e:
            log.error(f"Could not create export directory: {e}", exc_info=True)

    def refresh_list(self):
        self.export_list_widget.clear()
        self.content_view.clear()
        self.delete_button.setEnabled(False)
        try:
            files = [
                f for f in os.listdir(self.export_dir)
                if f.endswith('.md') and
                os.path.isfile(os.path.join(self.export_dir, f))
            ]
            files.sort(reverse=True)  # Show newest first

            if not files:
                self.export_list_widget.addItem("No exports found.")
                self.export_list_widget.setEnabled(False)
                return

            self.export_list_widget.setEnabled(True)
            for filename in files:
                path = os.path.join(self.export_dir, filename)
                item = QListWidgetItem(filename)
                item.setData(Qt.ItemDataRole.UserRole, path)
                self.export_list_widget.addItem(item)
            if self.export_list_widget.count() > 0:
                self.export_list_widget.setCurrentRow(0)

        except OSError as e:
            log.error(f"Error reading export directory {self.export_dir}: {e}")
            self.export_list_widget.addItem("Error reading directory.")
            self.export_list_widget.setEnabled(False)

    def _on_export_selected(self, current: QListWidgetItem, _):
        if not current or not current.data(Qt.ItemDataRole.UserRole):
            self.content_view.clear()
            self.delete_button.setEnabled(False)
            return

        self.delete_button.setEnabled(True)
        filepath = current.data(Qt.ItemDataRole.UserRole)
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            html = markdown(content, extensions=['fenced_code', 'tables',
                                                  'extra', 'sane_lists'])
            self.content_view.setHtml(html)
        except Exception as e:
            error_message = f"Error reading file:\n{filepath}\n\n{str(e)}"
            self.content_view.setText(error_message)
            log.error(f"Failed to read export file {filepath}: {e}")

    def _delete_selected_export(self):
        current_item = self.export_list_widget.currentItem()
        if not current_item:
            return

        filepath = current_item.data(Qt.ItemDataRole.UserRole)
        filename = os.path.basename(filepath)
        reply = QMessageBox.question(
            self, "Confirm Deletion",
            f"Are you sure you want to permanently delete this export?\n\n{filename}",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            try:
                os.remove(filepath)
                log.info(f"Deleted AI export file: {filepath}")
                self.refresh_list()
            except OSError as e:
                log.error(f"Failed to delete file {filepath}: {e}")
                QMessageBox.critical(
                    self, "Deletion Failed", f"Could not delete file:\n{e}"
                )

    def update_theme(self):
        """Applies colors and fonts from the current theme."""
        colors = theme_manager.current_theme_data.get('colors', {})
        font_family = settings_manager.get("font_family", "Consolas")
        font_size = settings_manager.get("font_size", 11)

        bg_color = colors.get('editor.background', '#2b2b2b')
        fg_color = colors.get('editor.foreground', '#a9b7c6')
        accent = colors.get('accent', '#88c0d0')
        line_bg = colors.get('editor.lineHighlightBackground', '#323232')
        comment = colors.get('syntax.comment', '#808080')
        string = colors.get('syntax.string', '#6A8759')
        toolbar_bg = colors.get('sidebar.background', '#3c3f41')
        border = colors.get('input.border', '#555')

        self.setStyleSheet(f"""
            AIExportViewerWidget {{ background-color: {bg_color}; }}
            #ExportViewerToolbar {{
                background-color: {toolbar_bg};
                border-bottom: 1px solid {border};
            }}
            QListWidget {{ background-color: {bg_color}; border: none; }}
        """)

        md_style = f"""
            h1,h2,h3,h4,h5,h6 {{
                color:{accent}; border-bottom:1px solid {line_bg};
                padding-bottom:4px; margin-top:15px;
            }}
            a {{ color:{string}; text-decoration:none; }}
            a:hover {{ text-decoration:underline; }}
            p,li {{ font-size:{font_size}pt; }}
            pre,code {{
                background-color:{line_bg}; border:1px solid {border};
                border-radius:4px; padding:10px; font-family:"{font_family}";
            }}
            code {{ padding:2px 4px; border:none; }}
            blockquote {{
                color:{comment}; border-left:3px solid {accent};
                padding-left:10px; margin-left:5px;
            }}
            table{{border-collapse:collapse;}}
            th,td{{border:1px solid {border}; padding:6px;}}
            th{{background-color:{line_bg};}}
        """
        self.content_view.document().setDefaultStyleSheet(md_style)
        font = QFont(settings_manager.get("font_family", "Arial"), font_size)
        self.content_view.document().setDefaultFont(font)
        self.content_view.setStyleSheet(
            f"background-color: {bg_color}; border:none; padding:10px;")

        if item := self.export_list_widget.currentItem():
            self._on_export_selected(item, None)
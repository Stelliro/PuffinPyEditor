# /plugins/markdown_viewer/markdown_editor_widget.py
import qtawesome as qta
from typing import TYPE_CHECKING
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTextBrowser,
                             QSplitter, QMenu, QToolButton, QFrame, QPlainTextEdit)
from PyQt6.QtGui import (QFont, QTextCursor, QAction)
from PyQt6.QtCore import QTimer, pyqtSignal, Qt
from markdown import markdown

from app_core.puffin_api import PuffinPluginAPI
from app_core.settings_manager import settings_manager
from ui.editor_widget import HighlightManager
from .markdown_syntax_highlighter import MarkdownSyntaxHighlighter
from utils.logger import log

if TYPE_CHECKING:
    from app_core.theme_manager import ThemeManager

class MarkdownFormattingToolbar(QWidget):
    # This class seems fine, no changes needed.
    format_bold_requested = pyqtSignal()
    format_italic_requested = pyqtSignal()
    format_strikethrough_requested = pyqtSignal()
    format_inline_code_requested = pyqtSignal()
    heading_level_requested = pyqtSignal(int)
    code_block_requested = pyqtSignal()
    def __init__(self, theme_manager: "ThemeManager", parent=None):
        super().__init__(parent)
        self.theme_manager = theme_manager
        self.setWindowFlags(Qt.WindowType.ToolTip | Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.frame = QFrame(self)
        self.frame.setObjectName("FormattingToolbarFrame")
        layout = QHBoxLayout(self.frame)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(2)
        self._add_tool_button("fa5s.bold", "Bold (Ctrl+B)", self.format_bold_requested)
        self._add_tool_button("fa5s.italic", "Italic (Ctrl+I)", self.format_italic_requested)
        self._add_tool_button("fa5s.strikethrough", "Strikethrough", self.format_strikethrough_requested)
        self._add_tool_button("fa5s.code", "Inline Code", self.format_inline_code_requested)
        layout.addWidget(self._create_separator())
        self._create_heading_menu()
        layout.addWidget(self._create_separator())
        self._add_tool_button("fa5s.file-code", "Insert Code Block", self.code_block_requested)
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(self.frame)
        self.update_theme()
    def _add_tool_button(self, icon_name, tooltip, signal_to_emit):
        button = QToolButton()
        button.setIcon(qta.icon(icon_name, color='white'))
        button.setToolTip(tooltip)
        button.clicked.connect(signal_to_emit.emit)
        self.frame.layout().addWidget(button)
    def _create_separator(self):
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.VLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        return separator
    def _create_heading_menu(self):
        button = QToolButton()
        button.setIcon(qta.icon("fa5s.heading", color='white'))
        button.setToolTip("Apply Heading")
        button.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        menu = QMenu(self)
        for i in range(1, 7):
            action = QAction(f"Heading {i}", self)
            action.triggered.connect(lambda _, level=i: self.heading_level_requested.emit(level))
            menu.addAction(action)
        button.setMenu(menu)
        self.frame.layout().addWidget(button)
    def update_theme(self):
        colors = self.theme_manager.current_theme_data.get('colors', {})
        bg, border, accent = colors.get('menu.background', '#3a4145'), colors.get('input.border', '#555555'), colors.get('accent', '#88c0d0')
        self.setStyleSheet(f"""#FormattingToolbarFrame {{ background-color: {bg}; border: 1px solid {border}; border-radius: 6px; }} QToolButton {{ background: transparent; border: none; padding: 5px; border-radius: 4px; }} QToolButton:hover {{ background-color: {accent}; }} QFrame[frameShape="5"] {{ color: {border}; }}""")
    def show_at(self, global_pos):
        self.move(global_pos)
        self.show()
        self.activateWindow()
    def focusOutEvent(self, event):
        self.hide()
        super().focusOutEvent(event)


class MarkdownEditorWidget(QWidget):
    content_changed = pyqtSignal()
    def __init__(self, puffin_api: PuffinPluginAPI, theme_manager: "ThemeManager", parent=None):
        super().__init__(parent)
        from ui.editor_widget import EditorWidget
        self.EditorWidgetClass = EditorWidget
        self.api = puffin_api
        self.theme_manager = theme_manager
        self.highlight_manager = HighlightManager()
        self.filepath = None
        self.original_hash = 0
        self.is_syncing_scroll = False
        self.formatting_toolbar = MarkdownFormattingToolbar(self.theme_manager, self)
        self._setup_ui()
        self._connect_signals()
        self.update_theme()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        self.editor_widget = self.EditorWidgetClass(self.api, self.api.get_manager("completion"), self.highlight_manager, self.theme_manager, self)
        self.editor_widget.text_area.setLineWrapMode(QPlainTextEdit.LineWrapMode.WidgetWidth)
        # THE FIX: Pass the theme_manager instance to the highlighter's constructor.
        self.highlighter = MarkdownSyntaxHighlighter(self.editor_widget.text_area.document(), self.theme_manager)
        self.viewer = QTextBrowser()
        self.viewer.setOpenExternalLinks(True)
        splitter = QSplitter(self)
        splitter.addWidget(self.editor_widget)
        splitter.addWidget(self.viewer)
        splitter.setSizes([self.width() // 2, self.width() // 2])
        layout.addWidget(splitter)

    def _connect_signals(self):
        self.update_timer = QTimer(self)
        self.update_timer.setSingleShot(True)
        self.update_timer.setInterval(250)
        self.update_timer.timeout.connect(self._render_preview)
        text_area = self.editor_widget.text_area
        text_area.textChanged.connect(self.update_timer.start)
        text_area.textChanged.connect(self.content_changed.emit)
        self.formatting_toolbar.format_bold_requested.connect(lambda: self._wrap_selection("**"))
        self.formatting_toolbar.format_italic_requested.connect(lambda: self._wrap_selection("*"))
        self.formatting_toolbar.format_strikethrough_requested.connect(lambda: self._wrap_selection("~~"))
        self.formatting_toolbar.format_inline_code_requested.connect(lambda: self._wrap_selection("`"))
        self.formatting_toolbar.heading_level_requested.connect(self._format_heading)
        self.formatting_toolbar.code_block_requested.connect(self._insert_code_block)
        editor_scroll = text_area.verticalScrollBar()
        viewer_scroll = self.viewer.verticalScrollBar()
        editor_scroll.valueChanged.connect(self._sync_scroll_from_editor)
        viewer_scroll.valueChanged.connect(self._sync_scroll_from_viewer)

    def contextMenuEvent(self, event):
        # We need to find the correct text_area widget within the editor_widget child
        if self.editor_widget.text_area.rect().contains(event.pos()):
            self.formatting_toolbar.show_at(event.globalPos())
        super().contextMenuEvent(event)
    def _wrap_selection(self, prefix, suffix=None):
        suffix = suffix or prefix
        cursor = self.editor_widget.text_area.textCursor()
        if not cursor.hasSelection():
            cursor.insertText(f"{prefix}text{suffix}")
            cursor.movePosition(QTextCursor.MoveOperation.Left, n=len(suffix))
            cursor.movePosition(QTextCursor.MoveOperation.Left, QTextCursor.MoveMode.KeepAnchor, n=4)
        else:
            selected_text = cursor.selectedText()
            cursor.insertText(f"{prefix}{selected_text}{suffix}")
        self.editor_widget.text_area.setTextCursor(cursor)
    def _format_heading(self, level):
        cursor = self.editor_widget.text_area.textCursor()
        cursor.beginEditBlock()
        cursor.movePosition(QTextCursor.MoveOperation.StartOfBlock)
        cursor.insertText(f'{"#" * level} ')
        cursor.endEditBlock()
    def _insert_code_block(self):
        cursor = self.editor_widget.text_area.textCursor()
        cursor.beginEditBlock()
        cursor.insertText("\n```python\n\n```\n")
        cursor.movePosition(QTextCursor.MoveOperation.Up, n=2)
        cursor.endEditBlock()
        self.editor_widget.text_area.setTextCursor(cursor)
    def _sync_scroll_factory(self, source_bar, target_bar):
        def sync_scroll(value):
            if self.is_syncing_scroll: return
            self.is_syncing_scroll = True
            source_max = source_bar.maximum() or 1
            ratio = value / source_max
            target_bar.setValue(int(target_bar.maximum() * ratio))
            self.is_syncing_scroll = False
        return sync_scroll
    @property
    def _sync_scroll_from_editor(self):
        return self._sync_scroll_factory(self.editor_widget.text_area.verticalScrollBar(), self.viewer.verticalScrollBar())
    @property
    def _sync_scroll_from_viewer(self):
        return self._sync_scroll_factory(self.viewer.verticalScrollBar(), self.editor_widget.text_area.verticalScrollBar())
    def load_file(self, filepath: str):
        self.filepath = filepath
        self.editor_widget.set_filepath(filepath)
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            self.editor_widget.set_text(content)
            self.original_hash = hash(content)
            log.info(f"Markdown Editor: Successfully loaded '{filepath}'.")
        except Exception as e:
            log.error(f"Failed to load markdown file {filepath}: {e}")
            self.editor_widget.set_text(f"# Error\n\nCould not load file: {e}")

    def get_content(self) -> str:
        return self.editor_widget.get_text()

    def _render_preview(self):
        viewer_scroll = self.viewer.verticalScrollBar()
        scroll_max = viewer_scroll.maximum() or 1
        old_pos_ratio = viewer_scroll.value() / scroll_max
        md_text = self.get_content()
        html = markdown(md_text, extensions=['fenced_code', 'tables', 'extra', 'sane_lists'])
        self.viewer.setHtml(html)
        QTimer.singleShot(0, lambda: viewer_scroll.setValue(int(viewer_scroll.maximum() * old_pos_ratio)))
    
    def update_theme(self):
        colors = self.theme_manager.current_theme_data.get('colors', {})
        font_family = settings_manager.get("font_family", "Arial")
        code_font_family = settings_manager.get("font_family", "Consolas")
        font_size = settings_manager.get("font_size", 11)
        bg = colors.get('editor.background', '#2b2b2b')
        string = colors.get('syntax.string', '#6A8759')
        accent = colors.get('accent', '#88c0d0')
        line_highlight_bg = colors.get('editor.lineHighlightBackground', '#323232')
        border = colors.get('input.border', '#555')
        comment = colors.get('syntax.comment', '#808080')
        
        style_sheet = f""" h1, h2, h3, h4, h5, h6 {{ color: {accent}; border-bottom: 1px solid {line_highlight_bg}; padding-bottom: 4px; margin-top: 15px; }} a {{ color: {string}; text-decoration: none; }} a:hover {{ text-decoration: underline; }} p, li {{ font-size: {font_size}pt; }} pre {{ background-color: {line_highlight_bg}; border: 1px solid {border}; border-radius: 4px; padding: 10px; font-family: "{code_font_family}"; }} code {{ background-color: {line_highlight_bg}; font-family: "{code_font_family}"; border-radius: 3px; padding: 2px 4px; }} blockquote {{ color: {comment}; border-left: 3px solid {accent}; padding-left: 15px; margin-left: 5px; font-style: italic; }} table {{ border-collapse: collapse; margin: 1em 0; }} th, td {{ border: 1px solid {border}; padding: 8px; }} th {{ background-color: {line_highlight_bg}; font-weight: bold; }} """
        doc = self.viewer.document()
        doc.setDefaultStyleSheet(style_sheet)
        doc.setDefaultFont(QFont(font_family, font_size))
        self.viewer.setStyleSheet(f"background-color: {bg}; border: none; padding: 10px;")
        
        # Ensure editor widget and highlighter also get updated
        self.editor_widget.update_theme()
        if self.highlighter:
            self.highlighter.rehighlight()

        self.formatting_toolbar.update_theme()
        self._render_preview()
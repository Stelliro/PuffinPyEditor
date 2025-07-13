# /ui/editor_widget.py
"""
PuffinPyEditor - Advanced Editor Widget
"""
from __future__ import annotations
from typing import Optional, Set, Dict, List, Tuple, TYPE_CHECKING
import re
import os
from math import cos, sin

from PyQt6.QtWidgets import (QWidget, QPlainTextEdit, QTextEdit, QHBoxLayout, QVBoxLayout, QSplitter, QApplication)
from PyQt6.QtGui import (QPainter, QColor, QFont, QPaintEvent, QTextFormat,
                         QTextBlockFormat, QPen, QTextCursor, QMouseEvent, QFontMetrics,
                         QKeyEvent, QTextDocument, QKeySequence, QWheelEvent, QPolygonF, QSyntaxHighlighter)
from PyQt6.QtCore import (Qt, QSize, QRect, QRectF, QPointF, QEvent, pyqtSignal,
                          QObject, QTimer, QPoint)
import qtawesome as qta
from app_core.settings_manager import settings_manager
from .widgets.find_panel import FindPanel
from utils.logger import log

if TYPE_CHECKING:
    from app_core.theme_manager import ThemeManager
    from app_core.completion_manager import CompletionManager
    from app_core.puffin_api import PuffinPluginAPI


class HighlightManager(QObject):
    """Manages custom line highlights from multiple sources (e.g., linter, user)."""
    highlights_changed = pyqtSignal()

    def __init__(self):
        super().__init__()
        self._highlights: Dict[str, Dict[int, QColor]] = {}

    def add_highlight(self, source_id: str, line_number: int, color: QColor):
        if source_id not in self._highlights: self._highlights[source_id] = {}
        self._highlights[source_id][line_number] = color
        self.highlights_changed.emit()

    def clear_highlights(self, source_id: str):
        if source_id in self._highlights:
            self._highlights.pop(source_id, None)
            self.highlights_changed.emit()

    def get_all_highlights(self) -> Dict[int, QColor]:
        combined = {}
        for source in self._highlights.values(): combined.update(source)
        return combined


class GutterWidget(QWidget):
    """The widget responsible for drawing the line number gutter."""
    RULER_WIDTH = 4

    def __init__(self, editor: 'CodeEditor'):
        super().__init__(editor.container)
        self.editor = editor
        self.setMouseTracking(True)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.hovered_line = -1

    def sizeHint(self) -> QSize:
        return QSize(self.editor.calculate_gutter_width(), 0)

    def paintEvent(self, event: QPaintEvent):
        self.editor.paint_gutter_event(event, self)

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self.editor.handle_gutter_left_click(event.pos())

    def mouseMoveEvent(self, event: QMouseEvent):
        block = self.editor.cursorForPosition(event.pos()).block()
        line_num = block.blockNumber() if block.isValid() else -1
        if line_num != self.hovered_line:
            self.hovered_line = line_num
            self.update()
        super().mouseMoveEvent(event)

    def leaveEvent(self, event: QEvent):
        self.hovered_line = -1
        self.update()
        super().leaveEvent(event)


class MiniMapWidget(QWidget):
    def __init__(self, editor: 'CodeEditor'):
        super().__init__(editor.container)
        self.editor = editor
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setMinimumWidth(80)
        self.editor.verticalScrollBar().valueChanged.connect(self.update)
        self.editor.document().blockCountChanged.connect(self.update)

    def paintEvent(self, event: QPaintEvent):
        painter, colors = QPainter(self), self.editor.container.theme_manager.current_theme_data.get('colors', {})
        painter.fillRect(self.rect(), QColor(colors.get('editorGutter.background', '#16161e')))
        doc, v_scroll = self.editor.document(), self.editor.verticalScrollBar()
        if doc.blockCount() == 0: return
        line_height_map, total_content_height = 2.0, doc.blockCount() * 2.0
        scale = min(1.0, self.height() / total_content_height if total_content_height > 0 else 1.0)
        scroll_proportion = v_scroll.value() / (v_scroll.maximum() or 1)
        scroll_offset = -(total_content_height - self.height()) * scroll_proportion if total_content_height > self.height() else 0
        painter.setPen(QColor(colors.get('editor.foreground', '#c0caf5')))
        for i in range(doc.blockCount()):
            block = doc.findBlockByNumber(i); text = block.text().lstrip()
            if not text: continue
            y = scroll_offset + (i * line_height_map * scale)
            if y > self.height(): break
            x = (len(block.text()) - len(text)) * 1.5; width = len(text) * 0.8
            painter.drawRect(QRectF(x, y, width, max(1.0, line_height_map * scale)))
        first_visible = self.editor.firstVisibleBlock().blockNumber()
        visible_blocks = self.editor.viewport().height() // self.editor.fontMetrics().height() if self.editor.fontMetrics().height() > 0 else 0
        viewport_y = scroll_offset + (first_visible * line_height_map * scale)
        viewport_h = max(1.0, visible_blocks * line_height_map * scale)
        viewport_rect = QRectF(0, viewport_y, self.width() - 1, viewport_h)
        painter.fillRect(viewport_rect, QColor(colors.get('editorGutter.ruler.color', '#41a6b530')))
        painter.setPen(QPen(QColor(colors.get('editorGutter.ruler.color', '#41a6b5')), 1)); painter.drawRect(viewport_rect)

    def mousePressEvent(self, e: QMouseEvent): self._scroll_from_mouse(e.position())
    def mouseMoveEvent(self, e: QMouseEvent):
        if e.buttons() & Qt.MouseButton.LeftButton: self._scroll_from_mouse(e.position())
    def _scroll_from_mouse(self, pos: QPointF):
        v_scroll = self.editor.verticalScrollBar()
        v_scroll.setValue(int((pos.y() / self.height()) * v_scroll.maximum()) if self.height() > 0 else 0)


class CodeOutlineMinimap(MiniMapWidget):
    LANG_PATTERNS = {
        'python': [(re.compile(r"^\s*class\s+(\w+)"), 'class', 1), (re.compile(r"^\s*def\s+(_?[a-zA-Z0-9_]+)"), 'def', 1)],
        'javascript': [(re.compile(r"^\s*class\s+(\w+)"), 'class', 1), (re.compile(r"^\s*function\s*\*?\s*(\w*)"), 'def', 1), (re.compile(r"^\s*(?:const|let|var)\s+([\w$]+)\s*=\s*(?:async\s*)?\("), 'def', 1)],
        'csharp': [(re.compile(r"^\s*(?:public|private|protected|internal)?\s*(?:sealed|abstract)?\s*class\s+(\w+)"), 'class', 1), (re.compile(r"^\s*(?:public|private|protected|internal)?\s*struct\s+(\w+)"), 'class', 1), (re.compile(r"^\s*(?:public|private|protected|internal)?\s*(?:static|virtual|override|async|unsafe)?\s*[\w<>\[\],]+\s+([\w]+)\s*\("), 'def', 1)],
        'cpp': [(re.compile(r"^\s*class\s+(\w+)"), 'class', 1), (re.compile(r"^\s*struct\s+(\w+)"), 'class', 1), (re.compile(r"^\w[\w\s\*&<>,:]*?([\w_]+)\s*\([^;]*\)\s*\{?$"), 'def', 1)],
        'rust': [(re.compile(r"^\s*struct\s+(\w+)"), 'class', 1), (re.compile(r"^\s*enum\s+(\w+)"), 'class', 1), (re.compile(r"^\s*(?:pub\s)?(?:async\s)?fn\s+(\w+)"), 'def', 1)]}
    LANG_MAP = {'.py': 'python', '.pyw': 'python', '.js': 'javascript', '.ts': 'javascript', '.cs': 'csharp', '.c': 'cpp', '.cpp': 'cpp', '.h': 'cpp', '.hpp': 'cpp', '.rs': 'rust'}
    def __init__(self, editor: 'CodeEditor', language_ext: str):
        super().__init__(editor); self.setMouseTracking(True); self.clickable_regions, self.hovered_region_index = [], -1
        self.patterns = self.LANG_PATTERNS.get(self.LANG_MAP.get(language_ext, ''), [])
        self._load_icons()
    def _load_icons(self):
        self.class_icon, self.def_icon = qta.icon('fa5s.cubes', color="#E5C07B"), qta.icon('fa5s.cube', color="#61AFEF")
    def _get_indent(self, text: str): return len(text) - len(text.lstrip())
    def _precompute_structure(self) -> List[Tuple[int, int, str, str]]:
        structure, doc = [], self.editor.document()
        if not self.patterns: return structure
        for i in range(doc.blockCount()):
            text = doc.findBlockByNumber(i).text()
            if not text.strip(): continue
            for pattern, item_type, name_group_idx in self.patterns:
                if match := pattern.match(text):
                    if name := match.group(name_group_idx): structure.append((i, self._get_indent(text), item_type, name)); break
        return structure
    def _format_name(self, name: str): return name.lstrip('_').replace('_', ' ').title()
    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            for i, (region_rect, line_num) in enumerate(self.clickable_regions):
                if region_rect.contains(event.position()):
                    cursor = QTextCursor(self.editor.document().findBlockByNumber(line_num)); self.editor.setTextCursor(cursor); self.editor.centerCursor(); return
            v_scroll = self.editor.verticalScrollBar(); v_scroll.setValue(int((event.position().y() / self.height()) * v_scroll.maximum())) if self.height() > 0 else None
    def mouseMoveEvent(self, event: QMouseEvent):
        new_hover_index = next((i for i, (rr, _) in enumerate(self.clickable_regions) if rr.contains(event.position())), -1)
        if new_hover_index != self.hovered_region_index: self.hovered_region_index = new_hover_index; self.update()
        super().mouseMoveEvent(event)
    def leaveEvent(self, event: QEvent):
        if self.hovered_region_index != -1: self.hovered_region_index = -1; self.update()
        super().leaveEvent(event)
    def paintEvent(self, event: QPaintEvent):
        painter = QPainter(self); painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        colors = self.editor.container.theme_manager.current_theme_data.get('colors', {})
        painter.fillRect(self.rect(), QColor(colors.get('editorGutter.background', '#16161e')))
        structure = self._precompute_structure()
        if not structure: super().paintEvent(event); return
        self._draw_structure_items(painter, colors, structure); self._draw_viewport_indicator(painter, colors)
    def _draw_structure_items(self, painter, colors, structure):
        self.clickable_regions.clear(); row_height, icon_size, class_indent, def_indent = 24, 14, 10, 25
        class_color, func_color, label_font = QColor(colors.get('syntax.className')), QColor(colors.get('syntax.functionName')), self.editor.font(); label_font.setPointSizeF(label_font.pointSizeF() * 0.9); painter.setFont(label_font)
        font_metrics, v_scroll = painter.fontMetrics(), self.editor.verticalScrollBar()
        total_content_height = len(structure) * row_height; scrollable_height = max(0, total_content_height - self.height())
        scroll_offset = -scrollable_height * (v_scroll.value() / (v_scroll.maximum() or 1))
        for i, (line_num, indent, item_type, name) in enumerate(structure):
            y_pos = i * row_height + scroll_offset
            if y_pos + row_height < 0 or y_pos > self.height(): continue
            item_rect = QRectF(0, y_pos, self.width(), row_height); self.clickable_regions.append((item_rect, line_num))
            if i == self.hovered_region_index: painter.fillRect(item_rect, QColor(colors.get('editor.lineHighlightBackground')).lighter(110))
            icon, indent_x = (self.class_icon, class_indent) if item_type == "class" else (self.def_icon, def_indent)
            icon.paint(painter, QRect(indent_x, int(y_pos + (row_height - icon_size) / 2), icon_size, icon_size))
            painter.setPen(class_color if item_type == "class" else func_color)
            text_x = indent_x + icon_size + 5
            painter.drawText(QPointF(text_x, y_pos + (row_height - font_metrics.height()) / 2 + font_metrics.ascent()), font_metrics.elidedText(self._format_name(name), Qt.TextElideMode.ElideRight, self.width() - text_x - 5))
    def _draw_viewport_indicator(self, painter, colors):
        doc = self.editor.document(); total_doc_lines = doc.blockCount()
        if total_doc_lines == 0: return
        first_visible = self.editor.firstVisibleBlock().blockNumber()
        visible_lines = self.editor.viewport().height() // self.editor.fontMetrics().height() if self.editor.fontMetrics().height() > 0 else 0
        indicator_y = (first_visible / total_doc_lines) * self.height(); indicator_h = max(3.0, (visible_lines / total_doc_lines) * self.height())
        viewport_rect = QRectF(0, indicator_y, self.width() - 1, indicator_h)
        painter.fillRect(viewport_rect, QColor(colors.get('editorGutter.ruler.color', '#41a6b530')))
        painter.setPen(QPen(QColor(colors.get('editorGutter.ruler.color', '#41a6b5')), 1)); painter.drawRect(viewport_rect)


class CodeEditor(QPlainTextEdit):
    def __init__(self, parent_container: 'EditorWidget'):
        super().__init__(parent_container)
        self.container = parent_container
        self.highlight_manager = self.container.highlight_manager
        self.multi_selection_source_id = f"multi_select_{id(self)}"
        self.highlight_manager.highlights_changed.connect(self.viewport().update)
        self.cursorPositionChanged.connect(self.update_extra_selections)

    def keyPressEvent(self, event: QKeyEvent):
        if event.modifiers() & Qt.KeyboardModifier.ControlModifier and event.key() == Qt.Key.Key_Slash: self._toggle_comment(); event.accept(); return
        if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter): self._auto_indent(); event.accept(); return
        if event.matches(QKeySequence.StandardKey.Find): self.container.toggle_find_panel(); event.accept(); return
        if event.key() == Qt.Key.Key_Escape:
            if self.highlight_manager._highlights.get(self.multi_selection_source_id):
                self.highlight_manager.clear_highlights(self.multi_selection_source_id)
                self.setFocus(); event.accept(); return
        super().keyPressEvent(event)

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton and QApplication.keyboardModifiers() & Qt.KeyboardModifier.ControlModifier:
            self.handle_multi_select_click(event)
            event.accept()
        else:
            self.highlight_manager.clear_highlights(self.multi_selection_source_id)
            super().mousePressEvent(event)
    
    def handle_multi_select_click(self, event: QMouseEvent):
        cursor = self.cursorForPosition(event.pos())
        selections = self.highlight_manager._highlights.get(self.multi_selection_source_id, {})
        color_hex = self.container.theme_manager.current_theme_data.get('colors', {}).get('editor.userHighlightBackground', '#83c0924D')
        selection_color = QColor(color_hex)
        line_num = cursor.blockNumber() + 1
        if line_num in selections: del selections[line_num]
        else: selections[line_num] = selection_color
        self.highlight_manager._highlights[self.multi_selection_source_id] = selections
        self.highlight_manager.highlights_changed.emit()

    def paintEvent(self, event: QPaintEvent):
        painter, event_rect = QPainter(self.viewport()), event.rect()
        all_highlights = self.highlight_manager.get_all_highlights()
        for line_num, color in all_highlights.items():
            block = self.document().findBlockByNumber(line_num - 1)
            if block.isValid() and block.isVisible():
                block_rect = self.blockBoundingGeometry(block).translated(self.contentOffset())
                if block_rect.intersects(event_rect):
                    full_width_rect = QRectF(self.viewport().rect().left(), block_rect.top(), self.viewport().rect().width(), block_rect.height())
                    painter.fillRect(full_width_rect, color)
        super().paintEvent(event); self.paint_indentation_guides(event)

    def handle_gutter_left_click(self, pos: QPointF):
        block = self.cursorForPosition(pos).block()
        if not block.isValid(): return
        line_num = block.blockNumber() + 1
        source_id, source_highlights = "user_breakpoint", self.highlight_manager._highlights.get("user_breakpoint", {})
        if line_num in source_highlights: del source_highlights[line_num]
        else: source_highlights[line_num] = QColor(self.container.theme_manager.current_theme_data.get('colors', {}).get('editor.breakpoint.color', '#dc143c'))
        self.highlight_manager._highlights[source_id] = source_highlights
        self.highlight_manager.highlights_changed.emit()

    def update_extra_selections(self):
        selections = []
        if self.hasFocus():
            selection = QTextEdit.ExtraSelection(); selection.format.setBackground(QColor(self.container.theme_manager.current_theme_data.get('colors', {}).get('editor.lineHighlightBackground', '#222436')))
            selection.format.setProperty(QTextFormat.Property.FullWidthSelection, True); selection.cursor = self.textCursor(); selection.cursor.clearSelection(); selections.append(selection)
        self.setExtraSelections(selections); self.container.gutter_widget.update()

    def calculate_gutter_width(self) -> int:
        if not self.container.settings.get("show_line_numbers", True): return 0
        return GutterWidget.RULER_WIDTH + self.fontMetrics().horizontalAdvance('9' * len(str(max(1, self.blockCount())))) + 15

    def paint_gutter_event(self, event: QPaintEvent, gutter: GutterWidget):
        painter = QPainter(gutter)
        colors = self.container.theme_manager.current_theme_data.get('colors', {})
        # CORRECTED: Added fallback values to all QColor lookups.
        painter.fillRect(event.rect(), QColor(colors.get('editorGutter.background', '#2f383e')))
        block = self.firstVisibleBlock()
        if not block.isValid(): return
        highlights, top = self.highlight_manager.get_all_highlights(), int(self.blockBoundingGeometry(block).translated(self.contentOffset()).top())
        block_num = block.blockNumber()
        
        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and top + int(self.blockBoundingRect(block).height()) >= event.rect().top():
                is_current = self.textCursor().blockNumber() == block_num
                is_hovered = block_num == gutter.hovered_line
                block_height = int(self.blockBoundingRect(block).height())
                if color := highlights.get(block_num + 1):
                    painter.fillRect(QRect(0, top, gutter.width(), block_height), color)
                elif is_hovered:
                    painter.fillRect(QRect(0, top, gutter.width(), block_height), QColor(colors.get('editorGutter.hoverBackground', '#ffffff1a')))
                
                if is_current and self.hasFocus():
                    # CORRECTED: Safely get the ruler color with a fallback.
                    ruler_color_str = colors.get('editorGutter.ruler.color', colors.get('accent'))
                    painter.fillRect(QRectF(0, top, gutter.RULER_WIDTH, block_height), QColor(ruler_color_str))

                active_fg = QColor(colors.get('editorLineNumber.activeForeground', '#d3c6aa'))
                default_fg = QColor(colors.get('editorLineNumber.foreground', '#5f6c6d'))
                painter.setPen(active_fg if is_current and self.hasFocus() else default_fg)
                painter.setFont(self.font())
                painter.drawText(QRect(gutter.RULER_WIDTH, top, gutter.width() - gutter.RULER_WIDTH - 5, block_height), Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter, str(block_num + 1))
            
            top += int(self.blockBoundingRect(block).height())
            block, block_num = block.next(), block_num + 1

    def paint_indentation_guides(self, event: QPaintEvent):
        painter = QPainter(self.viewport()); pen = QPen(QColor(self.container.theme_manager.current_theme_data.get('colors', {}).get('editorIndentGuide.background', '#3b4261'))); pen.setStyle(Qt.PenStyle.DotLine); painter.setPen(pen)
        indent_width = self.container.settings.get("indent_width", 4)
        if indent_width <= 0: return
        tab_width, offset = self.fontMetrics().horizontalAdvance(' ') * indent_width, self.contentOffset()
        block = self.firstVisibleBlock()
        while block.isValid() and block.isVisible():
            geom, indent_level = self.blockBoundingGeometry(block), len(block.text()) - len(block.text().lstrip(' '))
            for i in range(1, (indent_level // indent_width) + 1):
                if (x := i * tab_width + offset.x() - 1) > 0: painter.drawLine(int(x), int(geom.top() + offset.y()), int(x), int(geom.bottom() + offset.y()))
            block = block.next()

    def _auto_indent(self):
        cursor = self.textCursor(); indentation = (t := cursor.block().text())[:len(t) - len(t.lstrip())]
        cursor.insertBlock(); cursor.insertText(indentation)
        
    def _toggle_comment(self):
        cursor = self.textCursor(); start_pos, end_pos = cursor.selectionStart(), cursor.selectionEnd()
        doc = self.document(); start_block, end_block = doc.findBlock(start_pos), doc.findBlock(end_pos)
        if cursor.position() == end_pos and cursor.columnNumber() == 0 and start_pos != end_pos: end_block = end_block.previous()
        
        blocks_to_process = []
        block = start_block
        while block.isValid() and block.position() <= end_block.position():
            blocks_to_process.append(block); block = block.next()
            
        comment_char = self.container.get_comment_char()
        are_all_commented = all(b.text().lstrip().startswith(comment_char) for b in blocks_to_process if b.text().strip())
        
        cursor.beginEditBlock()
        for block in blocks_to_process:
            bc, text = QTextCursor(block), block.text()
            if are_all_commented:
                if (index := text.find(f'{comment_char} ')) != -1: bc.setPosition(block.position() + index); bc.setPosition(block.position() + index + len(comment_char) + 1, QTextCursor.MoveMode.KeepAnchor)
                elif (index := text.find(comment_char)) != -1: bc.setPosition(block.position() + index); bc.setPosition(block.position() + index + len(comment_char), QTextCursor.MoveMode.KeepAnchor)
                else: continue
                bc.removeSelectedText()
            else:
                bc.movePosition(QTextCursor.MoveOperation.StartOfLine); bc.insertText(f'{comment_char} ')
        cursor.endEditBlock()


class EditorWidget(QWidget):
    content_possibly_changed, cursor_position_display_updated, status_message_requested = pyqtSignal(), pyqtSignal(int, int), pyqtSignal(str, int)
    def __init__(self, puffin_api: 'PuffinPluginAPI', completion_manager: 'CompletionManager', highlight_manager: HighlightManager, theme_manager: 'ThemeManager', parent: Optional[QWidget] = None):
        super().__init__(parent); self.puffin_api, self.completion_manager, self.theme_manager, self.settings, self.highlight_manager = puffin_api, completion_manager, theme_manager, settings_manager, highlight_manager
        self.filepath: Optional[str] = None; self.highlighter: Optional[QSyntaxHighlighter] = None
        self.find_panel, self.text_area = FindPanel(self.theme_manager, self), CodeEditor(self)
        self.find_panel.hide(); self.gutter_widget, self.minimap_widget = GutterWidget(self.text_area), self._create_minimap()
        self._setup_layout(); self._connect_signals(); self.apply_styles_and_settings()

    def _create_minimap(self) -> MiniMapWidget:
        file_ext = os.path.splitext(self.filepath or '')[1].lower()
        if file_ext in {'.py', '.js', '.ts', '.cs', '.cpp', '.h', '.hpp', '.rs'}: return CodeOutlineMinimap(self.text_area, language_ext=file_ext)
        return MiniMapWidget(self.text_area)

    def _setup_layout(self):
        self.content_splitter = QSplitter(Qt.Orientation.Horizontal, self)
        editor_area_widget = QWidget(); editor_layout = QHBoxLayout(editor_area_widget)
        editor_layout.setContentsMargins(0, 0, 0, 0); editor_layout.setSpacing(0)
        editor_layout.addWidget(self.gutter_widget); editor_layout.addWidget(self.text_area, 1)
        self.content_splitter.addWidget(editor_area_widget); self.content_splitter.addWidget(self.minimap_widget)
        self.content_splitter.setSizes([800, 150]); self.content_splitter.setHandleWidth(4)
        self.main_layout = QVBoxLayout(self); self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0); self.main_layout.addWidget(self.find_panel)
        self.main_layout.addWidget(self.content_splitter, 1)

    def _connect_signals(self):
        self.text_area.blockCountChanged.connect(self._update_widget_geometries)
        self.text_area.updateRequest.connect(self._on_update_request)
        self.text_area.cursorPositionChanged.connect(self._on_cursor_position_changed)
        self.text_area.textChanged.connect(self.content_possibly_changed.emit)
        self.find_panel.close_requested.connect(self.hide_find_panel)
        self.find_panel.status_message_requested.connect(self.status_message_requested)

    def _on_update_request(self, rect: QRect, dy: int):
        if dy: self.gutter_widget.scroll(0, dy)
        else: self.gutter_widget.update(0, rect.y(), self.gutter_widget.width(), rect.height())
        if rect.contains(self.text_area.viewport().rect()): self._update_widget_geometries()

    def _update_widget_geometries(self): self.gutter_widget.setFixedWidth(self.text_area.calculate_gutter_width())
    def _on_cursor_position_changed(self): self.cursor_position_display_updated.emit(*self.get_cursor_position())
    def apply_styles_and_settings(self):
        font = QFont(self.settings.get("font_family"), self.settings.get("font_size")); self.text_area.setFont(font)
        self.text_area.setTabStopDistance(self.fontMetrics().horizontalAdvance(' ') * self.settings.get("indent_width", 4))
        self.update_theme()
    def update_theme(self):
        colors = self.theme_manager.current_theme_data.get("colors", {}); stylesheet = f"QPlainTextEdit {{ background-color: {colors.get('editor.background')}; color: {colors.get('editor.foreground')}; border: none; selection-background-color: {colors.get('editor.selectionBackground')}; }} QSplitter::handle {{ background-color: {colors.get('editorGutter.background')}; }} QSplitter::handle:hover {{ background-color: {colors.get('accent')}; }}"
        self.text_area.setStyleSheet(stylesheet); self.content_splitter.setStyleSheet(stylesheet)
        if hasattr(self.minimap_widget, '_load_icons'): self.minimap_widget._load_icons()
        if self.highlighter: self.highlighter.rehighlight()
        self._update_widget_geometries(); self.gutter_widget.update(); self.minimap_widget.update()
    def set_filepath(self, fp: Optional[str]):
        self.filepath = fp; new_minimap = self._create_minimap()
        if new_minimap.__class__ != self.minimap_widget.__class__: self.content_splitter.replaceWidget(1, new_minimap); self.minimap_widget.deleteLater(); self.minimap_widget = new_minimap
    def get_cursor_position(self) -> tuple[int, int]: c = self.text_area.textCursor(); return c.blockNumber() + 1, c.columnNumber()
    def goto_line_and_column(self, line: int, col: int):
        cursor = QTextCursor(self.document().findBlockByNumber(line - 1)); cursor.movePosition(QTextCursor.MoveOperation.Right, QTextCursor.MoveMode.MoveAnchor, col)
        self.text_area.setTextCursor(cursor); self.text_area.setFocus()
    def set_text(self, text: str): self.text_area.setPlainText(text)
    def get_text(self) -> str: return self.text_area.toPlainText()
    def set_highlighter(self, h_class):
        if self.highlighter: self.highlighter.setDocument(None)
        if h_class: self.highlighter = h_class(self.text_area.document(), self.theme_manager)
    def toggle_find_panel(self):
        if self.find_panel.isVisible(): self.hide_find_panel()
        else: self.show_find_panel()
    def show_find_panel(self): self.find_panel.show(); self.find_panel.connect_editor(self)
    def hide_find_panel(self): self.find_panel.hide(); self.text_area.setFocus()
    def get_comment_char(self) -> str: return self.puffin_api.get_main_window().COMMENT_MAP.get(os.path.splitext(self.filepath or "")[1].lower(), '#')
    def find_next(self, query: str, flags: QTextDocument.FindFlag) -> bool: return self.text_area.find(query, flags)
    def replace_current(self, query: str, replace: str, flags: QTextDocument.FindFlag) -> bool:
        c = self.text_area.textCursor()
        if c.hasSelection() and c.selectedText() == query: c.insertText(replace); return True
        if self.find_next(query, flags): self.text_area.textCursor().insertText(replace); return True
        return False
    def replace_all(self, query: str, replace: str, flags: QTextDocument.FindFlag) -> int:
        count, cursor = 0, self.text_area.textCursor(); cursor.beginEditBlock()
        cursor.movePosition(QTextCursor.MoveOperation.Start); self.text_area.setTextCursor(cursor)
        while self.find_next(query, flags): self.text_area.textCursor().insertText(replace); count += 1
        cursor.endEditBlock(); return count
    def document(self): return self.text_area.document()
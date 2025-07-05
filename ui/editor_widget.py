# /ui/editor_widget.py
"""
PuffinPyEditor - Advanced Editor Widget
(Version 8.7 - The Final Typo)
"""
from __future__ import annotations
from typing import Optional, Set, Dict, List, Tuple
import re
import os
from math import cos, sin

from PyQt6.QtWidgets import (QWidget, QPlainTextEdit, QTextEdit, QHBoxLayout, QVBoxLayout, QSplitter)
from PyQt6.QtGui import (QPainter, QColor, QFont, QPaintEvent, QTextFormat,
                         QTextBlockFormat, QPen, QTextCursor, QMouseEvent, QFontMetrics,
                         QKeyEvent, QTextDocument, QKeySequence, QWheelEvent, QPolygonF)
from PyQt6.QtCore import (Qt, QSize, QRect, QRectF, QPointF, QEvent, pyqtSignal,
                          QObject)
import qtawesome as qta
from app_core.settings_manager import settings_manager
from app_core.theme_manager import theme_manager
from .widgets.find_panel import FindPanel
from utils.logger import log


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
            del self._highlights[source_id]
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
        """Determines the required width of the gutter."""
        return QSize(self.editor.calculate_gutter_width(), 0)

    def paintEvent(self, event: QPaintEvent):
        """Delegates painting to the main editor component."""
        self.editor.paint_gutter_event(event, self)

    def mousePressEvent(self, event: QMouseEvent):
        """Handles clicks for toggling breakpoints/highlights."""
        if event.button() == Qt.MouseButton.LeftButton:
            self.editor.handle_gutter_left_click(event.pos())

    def mouseMoveEvent(self, event: QMouseEvent):
        """Tracks the hovered line to provide visual feedback."""
        block = self.editor.cursorForPosition(event.pos()).block()
        line_num = block.blockNumber() if block.isValid() else -1
        if line_num != self.hovered_line:
            self.hovered_line = line_num
            self.update()
        super().mouseMoveEvent(event)

    def leaveEvent(self, event: QEvent):
        """Resets the hover state when the mouse leaves the gutter."""
        self.hovered_line = -1
        self.update()
        super().leaveEvent(event)


class MiniMapWidget(QWidget):
    """A widget that displays a high-level, shrunken overview of the code text."""

    def __init__(self, editor: 'CodeEditor'):
        super().__init__(editor.container)
        self.editor = editor
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setMinimumWidth(80)
        self.editor.verticalScrollBar().valueChanged.connect(self.update)
        self.editor.document().blockCountChanged.connect(self.update)

    def paintEvent(self, event: QPaintEvent):
        painter = QPainter(self)
        colors = self.editor.container.theme_manager.current_theme_data.get('colors', {})
        painter.fillRect(self.rect(), QColor(colors.get('editorGutter.background', '#16161e')))
        doc = self.editor.document()
        if doc.blockCount() == 0: return
        line_height_map = 2.0
        total_content_height = doc.blockCount() * line_height_map
        scale = min(1.0, self.height() / total_content_height if total_content_height > 0 else 1.0)
        v_scroll = self.editor.verticalScrollBar()
        scroll_proportion = v_scroll.value() / v_scroll.maximum() if v_scroll.maximum() > 0 else 0
        scroll_offset = -(
                    total_content_height - self.height()) * scroll_proportion if total_content_height > self.height() else 0
        painter.setPen(QColor(colors.get('editor.foreground', '#c0caf5')))
        for i in range(doc.blockCount()):
            block = doc.findBlockByNumber(i)
            text = block.text().lstrip()
            if not text: continue
            y = scroll_offset + (i * line_height_map * scale)
            if y > self.height(): break
            x = (len(block.text()) - len(text)) * 1.5
            width = len(text) * 0.8
            painter.drawRect(QRectF(x, y, width, max(1.0, line_height_map * scale)))
        first_visible = self.editor.firstVisibleBlock().blockNumber()
        try:
            visible_blocks = self.editor.viewport().height() // self.editor.fontMetrics().height()
        except ZeroDivisionError:
            visible_blocks = 0
        viewport_y = scroll_offset + (first_visible * line_height_map * scale)
        viewport_h = max(1.0, visible_blocks * line_height_map * scale)
        viewport_rect = QRectF(0, viewport_y, self.width() - 1, viewport_h)
        painter.fillRect(viewport_rect, QColor(colors.get('editorGutter.ruler.color', '#41a6b530')))
        painter.setPen(QPen(QColor(colors.get('editorGutter.ruler.color', '#41a6b5')), 1))
        painter.drawRect(viewport_rect)

    def mousePressEvent(self, e: QMouseEvent):
        self._scroll_from_mouse(e.position())

    def mouseMoveEvent(self, e: QMouseEvent):
        if e.buttons() & Qt.MouseButton.LeftButton:
            self._scroll_from_mouse(e.position())

    def _scroll_from_mouse(self, pos: QPointF):
        v_scroll = self.editor.verticalScrollBar()
        proportion = pos.y() / self.height()
        v_scroll.setValue(int(proportion * v_scroll.maximum()))


class CodeOutlineMinimap(MiniMapWidget):
    """A specialized minimap that shows a clickable code outline for various languages."""
    LANG_PATTERNS = {
        'python': [
            (re.compile(r"^\s*class\s+(\w+)"), 'class', 1),
            (re.compile(r"^\s*def\s+(_?[a-zA-Z0-9_]+)"), 'def', 1),
        ],
        'javascript': [
            (re.compile(r"^\s*class\s+(\w+)"), 'class', 1),
            (re.compile(r"^\s*function\s*\*?\s*(\w*)"), 'def', 1),
            (re.compile(r"^\s*(?:const|let|var)\s+([\w$]+)\s*=\s*(?:async\s*)?\("), 'def', 1),
        ],
        'csharp': [
            (re.compile(r"^\s*(?:public|private|protected|internal)?\s*(?:sealed|abstract)?\s*class\s+(\w+)"), 'class', 1),
            (re.compile(r"^\s*(?:public|private|protected|internal)?\s*struct\s+(\w+)"), 'class', 1),
            (re.compile(r"^\s*(?:public|private|protected|internal)?\s*(?:static|virtual|override|async|unsafe)?\s*[\w<>\[\],]+\s+([\w]+)\s*\("), 'def', 1),
        ],
        'cpp': [
            (re.compile(r"^\s*class\s+(\w+)"), 'class', 1),
            (re.compile(r"^\s*struct\s+(\w+)"), 'class', 1),
            (re.compile(r"^\w[\w\s\*&<>,:]*?([\w_]+)\s*\([^;]*\)\s*\{?$"), 'def', 1),
        ],
        'rust': [
            (re.compile(r"^\s*struct\s+(\w+)"), 'class', 1),
            (re.compile(r"^\s*enum\s+(\w+)"), 'class', 1),
            (re.compile(r"^\s*(?:pub\s)?(?:async\s)?fn\s+(\w+)"), 'def', 1),
        ]
    }
    LANG_MAP = {
        '.py': 'python', '.pyw': 'python',
        '.js': 'javascript', '.ts': 'javascript',
        '.cs': 'csharp',
        '.c': 'cpp', '.cpp': 'cpp', '.h': 'cpp', '.hpp': 'cpp',
        '.rs': 'rust'
    }

    def __init__(self, editor: 'CodeEditor', language_ext: str):
        super().__init__(editor)
        self.setMouseTracking(True)
        self.clickable_regions: List[Tuple[QRectF, int]] = []
        self.hovered_region_index = -1
        lang_name = self.LANG_MAP.get(language_ext)
        self.patterns = self.LANG_PATTERNS.get(lang_name, [])
        self._load_icons()

    def _load_icons(self):
        """Pre-load icons to avoid doing so in the paint loop."""
        class_icon_color = "#E5C07B"
        def_icon_color = "#61AFEF"
        self.class_icon = qta.icon('fa5s.cubes', color=class_icon_color)
        self.def_icon = qta.icon('fa5s.cube', color=def_icon_color)

    def _get_indent(self, text: str) -> int:
        return len(text) - len(text.lstrip())

    def _precompute_structure(self) -> List[Tuple[int, int, str, str]]:
        structure = []
        doc = self.editor.document()
        if not self.patterns:
            return structure
        for i in range(doc.blockCount()):
            text = doc.findBlockByNumber(i).text()
            if not text.strip():
                continue
            for pattern, item_type, name_group_idx in self.patterns:
                match = pattern.match(text)
                if match:
                    name = match.group(name_group_idx)
                    if name:
                        structure.append((i, self._get_indent(text), item_type, name))
                        break
        return structure

    def _format_name(self, name: str) -> str:
        return name.lstrip('_').replace('_', ' ').title()

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            for i, (region_rect, line_num) in enumerate(self.clickable_regions):
                if region_rect.contains(event.position()):
                    cursor = QTextCursor(self.editor.document().findBlockByNumber(line_num))
                    self.editor.setTextCursor(cursor)
                    self.editor.centerCursor()
                    return
            v_scroll = self.editor.verticalScrollBar()
            if self.height() > 0:
                proportion = event.position().y() / self.height()
                v_scroll.setValue(int(proportion * v_scroll.maximum()))

    def mouseMoveEvent(self, event: QMouseEvent):
        new_hover_index = -1
        for i, (region_rect, _) in enumerate(self.clickable_regions):
            if region_rect.contains(event.position()):
                new_hover_index = i
                break
        if new_hover_index != self.hovered_region_index:
            self.hovered_region_index = new_hover_index
            self.update()
        super().mouseMoveEvent(event)

    def leaveEvent(self, event: QEvent):
        if self.hovered_region_index != -1:
            self.hovered_region_index = -1
            self.update()
        super().leaveEvent(event)

    def paintEvent(self, event: QPaintEvent):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        colors = self.editor.container.theme_manager.current_theme_data.get('colors', {})
        painter.fillRect(self.rect(), QColor(colors.get('editorGutter.background', '#16161e')))
        structure = self._precompute_structure()
        if not structure:
            return super().paintEvent(event)
        self._draw_structure_items(painter, colors, structure)
        self._draw_viewport_indicator(painter, colors)

    def _draw_structure_items(self, painter, colors, structure):
        self.clickable_regions.clear()
        row_height, icon_size = 24, 14
        class_indent, def_indent = 10, 25
        class_color = QColor(colors.get('syntax.className', '#dbbc7f'))
        func_color = QColor(colors.get('syntax.functionName', '#83c092'))
        label_font = self.editor.font()
        label_font.setPointSizeF(label_font.pointSizeF() * 0.9)
        painter.setFont(label_font)
        font_metrics = painter.fontMetrics()
        v_scroll = self.editor.verticalScrollBar()
        total_content_height = len(structure) * row_height
        scrollable_height = max(0, total_content_height - self.height())
        scroll_proportion = v_scroll.value() / (v_scroll.maximum() or 1)
        scroll_offset = -scrollable_height * scroll_proportion
        for i, (line_num, indent, item_type, name) in enumerate(structure):
            y_pos = i * row_height + scroll_offset
            if y_pos + row_height < 0 or y_pos > self.height():
                continue
            item_rect = QRectF(0, y_pos, self.width(), row_height)
            self.clickable_regions.append((item_rect, line_num))
            if i == self.hovered_region_index:
                hover_color = QColor(colors.get('editor.lineHighlightBackground', '#323232'))
                painter.fillRect(item_rect, hover_color.lighter(110))
            icon = self.class_icon if item_type == "class" else self.def_icon
            indent_x = class_indent if item_type == "class" else def_indent
            icon_y = y_pos + (row_height - icon_size) / 2
            icon.paint(painter, QRect(indent_x, int(icon_y), icon_size, icon_size))
            painter.setPen(class_color if item_type == "class" else func_color)
            text_x = indent_x + icon_size + 5
            available_width = self.width() - text_x - 5
            elided_name = font_metrics.elidedText(self._format_name(name), Qt.TextElideMode.ElideRight, available_width)
            text_y = y_pos + (row_height - font_metrics.height()) / 2 + font_metrics.ascent()
            painter.drawText(QPointF(text_x, text_y), elided_name)

    def _draw_viewport_indicator(self, painter, colors):
        doc = self.editor.document()
        total_doc_lines = doc.blockCount()
        if total_doc_lines == 0:
            return
        first_visible_line = self.editor.firstVisibleBlock().blockNumber()
        try:
            visible_line_count = self.editor.viewport().height() // self.editor.fontMetrics().height()
        except ZeroDivisionError:
            visible_line_count = 0
        start_proportion = first_visible_line / total_doc_lines
        visible_proportion = visible_line_count / total_doc_lines
        indicator_y = start_proportion * self.height()
        indicator_h = max(3.0, visible_proportion * self.height())
        viewport_rect = QRectF(0, indicator_y, self.width() - 1, indicator_h)
        painter.fillRect(viewport_rect, QColor(colors.get('editorGutter.ruler.color', '#41a6b530')))
        painter.setPen(QPen(QColor(colors.get('editorGutter.ruler.color', '#41a6b5')), 1))
        painter.drawRect(viewport_rect)


class CodeEditor(QPlainTextEdit):
    def __init__(self, parent_container: 'EditorWidget'):
        super().__init__(parent_container)
        self.container = parent_container
        self.highlight_manager = self.container.highlight_manager
        self.highlight_manager.highlights_changed.connect(self.viewport().update)
        self.cursorPositionChanged.connect(self.update_extra_selections)

    def keyPressEvent(self, event: QKeyEvent):
        if event.modifiers() & Qt.KeyboardModifier.ControlModifier and event.key() == Qt.Key.Key_Slash:
            self._toggle_comment()
            event.accept()
            return
        if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            self._auto_indent()
            event.accept()
            return
        if event.matches(QKeySequence.StandardKey.Find):
            self.container.toggle_find_panel()
            event.accept()
            return
        super().keyPressEvent(event)

    def paintEvent(self, event: QPaintEvent):
        painter = QPainter(self.viewport())
        event_rect_f = QRectF(event.rect())
        for line_num, color in self.highlight_manager.get_all_highlights().items():
            block = self.document().findBlockByNumber(line_num - 1)
            if block.isValid() and block.isVisible():
                block_rect = self.blockBoundingGeometry(block).translated(self.contentOffset())
                if block_rect.intersects(event_rect_f):
                    painter.fillRect(block_rect, color)
        super().paintEvent(event)
        self.paint_indentation_guides(event)

    def handle_gutter_left_click(self, pos: QPointF):
        block = self.cursorForPosition(pos).block()
        if not block.isValid(): return
        line_num = block.blockNumber() + 1
        source_id = "user_breakpoint"
        source_highlights = self.highlight_manager._highlights.get(source_id, {})
        if line_num in source_highlights:
            del source_highlights[line_num]
        else:
            colors = self.container.theme_manager.current_theme_data.get('colors', {})
            color = QColor(colors.get('editor.breakpoint.color', '#dc143c'))
            source_highlights[line_num] = color
        self.highlight_manager._highlights[source_id] = source_highlights
        self.highlight_manager.highlights_changed.emit()

    def update_extra_selections(self):
        selections = []
        if self.hasFocus():
            selection = QTextEdit.ExtraSelection()
            colors = self.container.theme_manager.current_theme_data.get('colors', {})
            selection.format.setBackground(QColor(colors.get('editor.lineHighlightBackground', '#222436')))
            selection.format.setProperty(QTextFormat.Property.FullWidthSelection, True)
            selection.cursor = self.textCursor()
            selection.cursor.clearSelection()
            selections.append(selection)
        self.setExtraSelections(selections)
        self.container.gutter_widget.update()

    def calculate_gutter_width(self) -> int:
        if not self.container.settings.get("show_line_numbers", True): return 0
        digits = len(str(max(1, self.blockCount())))
        return GutterWidget.RULER_WIDTH + self.fontMetrics().horizontalAdvance('9' * digits) + 15

    def paint_gutter_event(self, event: QPaintEvent, gutter: GutterWidget):
        painter = QPainter(gutter)
        colors = self.container.theme_manager.current_theme_data.get('colors', {})
        gutter_bg = QColor(colors.get('editorGutter.background', '#16161e'))
        ruler_color = QColor(colors.get('editorGutter.ruler.color', colors.get('accent', '#88c0d0')))
        hover_bg = QColor(colors.get('editorGutter.hoverBackground', '#ffffff1a'))
        default_fg = QColor(colors.get('editorLineNumber.foreground', '#545c7e'))
        active_fg = QColor(colors.get('editorLineNumber.activeForeground', '#a9b1d6'))
        painter.fillRect(event.rect(), gutter_bg)
        block = self.firstVisibleBlock()
        if not block.isValid(): return
        highlights = self.highlight_manager.get_all_highlights()
        top = int(self.blockBoundingGeometry(block).translated(self.contentOffset()).top())
        block_num = block.blockNumber()
        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and top + int(self.blockBoundingRect(block).height()) >= event.rect().top():
                is_current = self.textCursor().blockNumber() == block_num
                is_hovered = block_num == gutter.hovered_line
                block_height = int(self.blockBoundingRect(block).height())
                if (color := highlights.get(block_num + 1)):
                    painter.fillRect(QRect(0, top, gutter.width(), block_height), color)
                elif is_hovered:
                    painter.fillRect(QRect(0, top, gutter.width(), block_height), hover_bg)
                if is_current and self.hasFocus():
                    painter.fillRect(QRectF(0, top, gutter.RULER_WIDTH, block_height), ruler_color)
                line_text = str(block_num + 1)
                pen_color = active_fg if is_current and self.hasFocus() else default_fg
                painter.setPen(pen_color)
                painter.setFont(self.font())
                painter.drawText(QRect(gutter.RULER_WIDTH, top, gutter.width() - gutter.RULER_WIDTH - 5, block_height),
                                 Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter, line_text)
            top += int(self.blockBoundingRect(block).height())
            block = block.next()
            block_num += 1

    def paint_indentation_guides(self, event: QPaintEvent):
        painter = QPainter(self.viewport())
        colors = self.container.theme_manager.current_theme_data.get('colors', {})
        pen = QPen(QColor(colors.get('editorIndentGuide.background', '#3b4261')))
        pen.setStyle(Qt.PenStyle.DotLine)
        painter.setPen(pen)
        indent_width = self.container.settings.get("indent_width", 4)
        if indent_width <= 0: return
        tab_width = self.fontMetrics().horizontalAdvance(' ') * indent_width
        offset = self.contentOffset()
        block = self.firstVisibleBlock()
        while block.isValid() and block.isVisible():
            geom = self.blockBoundingGeometry(block)
            indent_level = len(block.text()) - len(block.text().lstrip(' '))
            for i in range(1, (indent_level // indent_width) + 1):
                x = (i * tab_width) + offset.x() - 1
                if x > 0: painter.drawLine(int(x), int(geom.top() + offset.y()), int(x),
                                           int(geom.bottom() + offset.y()))
            block = block.next()

    def _auto_indent(self):
        cursor = self.textCursor()
        current_block = cursor.block()
        text = current_block.text()
        indentation = text[:len(text) - len(text.lstrip())]
        cursor.insertBlock()
        cursor.insertText(indentation)

    def _toggle_comment(self):
        cursor = self.textCursor()
        start, end = cursor.selectionStart(), cursor.selectionEnd()
        start_block, end_block = self.document().findBlock(start), self.document().findBlock(end)
        if cursor.position() == end and cursor.columnNumber() == 0 and start != end:
            end_block = end_block.previous()
        blocks_to_process = []
        block = start_block
        while True:
            blocks_to_process.append(block)
            if not block.isValid() or block == end_block: break
            block = block.next()
        comment_char = self.container.get_comment_char()
        are_all_commented = all(
            b.text().lstrip().startswith(comment_char) for b in blocks_to_process if b.text().strip())
        cursor.beginEditBlock()
        for block in blocks_to_process:
            block_cursor = QTextCursor(block)
            text = block.text()
            if are_all_commented:
                if text.lstrip().startswith(f'{comment_char} '):
                    index = text.find(f'{comment_char} ')
                    length = len(comment_char) + 1
                elif text.lstrip().startswith(comment_char):
                    index = text.find(comment_char)
                    length = len(comment_char)
                else:
                    continue
                block_cursor.setPosition(index)
                block_cursor.setPosition(index + length, QTextCursor.MoveMode.KeepAnchor)
                block_cursor.removeSelectedText()
            else:
                block_cursor.movePosition(QTextCursor.MoveOperation.StartOfLine)
                block_cursor.insertText(f'{comment_char} ')
        cursor.endEditBlock()


class EditorWidget(QWidget):
    content_possibly_changed = pyqtSignal()
    cursor_position_display_updated = pyqtSignal(int, int)
    status_message_requested = pyqtSignal(str, int)

    def __init__(self, puffin_api, completion_manager, highlight_manager: HighlightManager, parent=None):
        super().__init__(parent)
        self.puffin_api = puffin_api
        self.theme_manager = theme_manager
        self.settings = settings_manager
        self.highlight_manager = highlight_manager
        self.filepath: Optional[str] = None
        self.highlighter: Optional[QSyntaxHighlighter] = None
        self.find_panel = FindPanel(self)
        self.find_panel.hide()
        self.text_area = CodeEditor(self)
        self.gutter_widget = GutterWidget(self.text_area)
        self.minimap_widget = self._create_minimap()
        self._setup_layout()
        self._connect_signals()
        self.apply_styles_and_settings()

    def _create_minimap(self) -> MiniMapWidget:
        outline_extensions = {'.py', '.js', '.ts', '.cs', '.cpp', '.h', '.hpp', '.rs'}
        file_ext = os.path.splitext(self.filepath or '')[1].lower()
        if file_ext in outline_extensions:
            log.info(f"Creating Code Outline minimap for {file_ext} file.")
            return CodeOutlineMinimap(self.text_area, language_ext=file_ext)
        else:
            log.info("Creating default text minimap.")
            return MiniMapWidget(self.text_area)

    def _setup_layout(self):
        self.content_splitter = QSplitter(Qt.Orientation.Horizontal, self)
        
        editor_area_widget = QWidget()
        editor_layout = QHBoxLayout(editor_area_widget)
        editor_layout.setContentsMargins(0, 0, 0, 0)
        editor_layout.setSpacing(0)
        editor_layout.addWidget(self.gutter_widget)
        editor_layout.addWidget(self.text_area, 1)
        
        self.content_splitter.addWidget(editor_area_widget)
        self.content_splitter.addWidget(self.minimap_widget)
        self.content_splitter.setSizes([800, 150])
        self.content_splitter.setHandleWidth(4)
        
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        self.main_layout.addWidget(self.find_panel)
        # THE FIX: Give the content_splitter a stretch factor so it takes priority
        self.main_layout.addWidget(self.content_splitter, 1)

    def _connect_signals(self):
        self.text_area.blockCountChanged.connect(self._update_widget_geometries)
        self.text_area.updateRequest.connect(self._on_update_request)
        self.text_area.cursorPositionChanged.connect(self._on_cursor_position_changed)
        self.text_area.textChanged.connect(self.content_possibly_changed.emit)
        self.find_panel.close_requested.connect(self.hide_find_panel)
        self.find_panel.status_message_requested.connect(self.status_message_requested)

    def _on_update_request(self, rect: QRect, dy: int):
        if dy:
            self.gutter_widget.scroll(0, dy)
        else:
            self.gutter_widget.update(0, rect.y(), self.gutter_widget.width(), rect.height())
        if rect.contains(self.text_area.viewport().rect()):
            self._update_widget_geometries()

    def _update_widget_geometries(self):
        width = self.text_area.calculate_gutter_width()
        self.gutter_widget.setFixedWidth(width)

    def _on_cursor_position_changed(self):
        self.cursor_position_display_updated.emit(*self.get_cursor_position())

    def apply_styles_and_settings(self):
        font = QFont(self.settings.get("font_family"), self.settings.get("font_size"))
        self.text_area.setFont(font)
        indent_width = self.settings.get("indent_width", 4)
        tab_stop_dist = self.fontMetrics().horizontalAdvance(' ') * indent_width
        self.text_area.setTabStopDistance(tab_stop_dist)
        self.update_theme()

    def update_theme(self):
        colors = self.theme_manager.current_theme_data.get("colors", {})
        stylesheet = f"""
            QPlainTextEdit {{
                background-color: {colors.get('editor.background', '#1a1b26')};
                color: {colors.get('editor.foreground', '#c0caf5')};
                border: none;
                selection-background-color: {colors.get('editor.selectionBackground', '#2e3c60')};
            }}
            QSplitter::handle {{
                background-color: {colors.get('editorGutter.background', '#16161e')};
            }}
            QSplitter::handle:hover {{
                background-color: {colors.get('accent', '#88c0d0')};
            }}
        """
        self.text_area.setStyleSheet(stylesheet)
        self.content_splitter.setStyleSheet(stylesheet)
        if hasattr(self.minimap_widget, '_load_icons'): self.minimap_widget._load_icons()
        if self.highlighter:
            self.highlighter.rehighlight()
        self._update_widget_geometries()
        self.gutter_widget.update()
        self.minimap_widget.update()

    def set_filepath(self, filepath: Optional[str]):
        self.filepath = filepath
        new_minimap = self._create_minimap()
        if new_minimap.__class__ != self.minimap_widget.__class__:
            self.content_splitter.replaceWidget(1, new_minimap)
            self.minimap_widget.deleteLater()
            self.minimap_widget = new_minimap

    def get_cursor_position(self) -> tuple[int, int]:
        cursor = self.text_area.textCursor()
        return cursor.blockNumber() + 1, cursor.columnNumber()

    def goto_line_and_column(self, line: int, column: int):
        cursor = QTextCursor(self.document().findBlockByNumber(line - 1))
        cursor.movePosition(QTextCursor.MoveOperation.Right, QTextCursor.MoveMode.MoveAnchor, column)
        self.text_area.setTextCursor(cursor)
        self.text_area.setFocus()

    def set_text(self, text: str):
        self.text_area.setPlainText(text)

    def get_text(self) -> str:
        return self.text_area.toPlainText()

    def set_highlighter(self, highlighter_class):
        if self.highlighter:
            self.highlighter.setDocument(None)
        if highlighter_class:
            self.highlighter = highlighter_class(self.text_area.document())

    def toggle_find_panel(self):
        if self.find_panel.isVisible():
            self.hide_find_panel()
        else:
            self.show_find_panel()

    def show_find_panel(self):
        self.find_panel.show()
        self.find_panel.connect_editor(self)

    def hide_find_panel(self):
        self.find_panel.hide()
        self.text_area.setFocus()

    def get_comment_char(self) -> str:
        from ui.main_window import MainWindow
        if self.filepath:
            ext = os.path.splitext(self.filepath)[1].lower()
            return MainWindow.COMMENT_MAP.get(ext, '#')
        return '#'

    def find_next(self, query: str, flags: QTextDocument.FindFlag) -> bool:
        return self.text_area.find(query, flags)

    def replace_current(self, query: str, replace_text: str, flags: QTextDocument.FindFlag) -> bool:
        cursor = self.text_area.textCursor()
        if cursor.hasSelection() and cursor.selectedText() == query:
            cursor.insertText(replace_text)
            return True
        elif self.find_next(query, flags):
            self.text_area.textCursor().insertText(replace_text)
            return True
        return False

    def replace_all(self, query: str, replace_text: str, flags: QTextDocument.FindFlag) -> int:
        count = 0
        cursor = self.text_area.textCursor()
        cursor.beginEditBlock()
        cursor.movePosition(QTextCursor.MoveOperation.Start)
        self.text_area.setTextCursor(cursor)
        while self.find_next(query, flags):
            self.text_area.textCursor().insertText(replace_text)
            count += 1
        cursor.endEditBlock()
        return count

    def document(self):
        return self.text_area.document()
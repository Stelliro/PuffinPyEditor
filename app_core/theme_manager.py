# PuffinPyEditor/app_core/theme_manager.py
import os
import json
import base64
import shutil
from typing import Dict, Any, Optional
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QColor

from app_core.settings_manager import settings_manager
from utils.logger import log, get_app_data_path
from utils.helpers import get_base_path

SVG_ARROW_PATHS = {'up': "M4 10 L8 6 L12 10", 'down': "M4 6 L8 10 L12 6"}
APP_BASE_PATH = get_base_path()
APP_DATA_ROOT = get_app_data_path()
CUSTOM_THEMES_FILE_PATH = os.path.join(APP_DATA_ROOT, "custom_themes.json")
DEFAULT_CUSTOM_THEMES_FILE_PATH = os.path.join(APP_BASE_PATH, "assets", "themes", "custom_themes.json")

BUILT_IN_THEMES = {
    "puffin_dark": {
        "name": "Puffin Dark", "author": "PuffinPy", "type": "dark", "is_custom": False,
        "colors": {
            "window.background": "#2f383e", "sidebar.background": "#2a3338",
            "editor.background": "#272e33", "editor.foreground": "#d3c6aa",
            "editorGutter.background": "#2f383e", "editorGutter.foreground": "#5f6c6d",
            "editor.lineHighlightBackground": "#3a4145",
            "editor.matchingBracketBackground": "#545e62", "editor.matchingBracketForeground": "#d3c6aa",
            "menu.background": "#3a4145", "menu.foreground": "#d3c6aa",
            "statusbar.background": "#282f34", "statusbar.foreground": "#d3c6aa",
            "tab.activeBackground": "#272e33", "tab.inactiveBackground": "#2f383e",
            "tab.activeForeground": "#d3c6aa", "tab.inactiveForeground": "#5f6c6d",
            "button.background": "#424d53", "button.foreground": "#d3c6aa",
            "input.background": "#3a4145", "input.foreground": "#d3c6aa", "input.border": "#5f6c6d",
            "scrollbar.background": "#2f383e", "scrollbar.handle": "#424d53",
            "scrollbar.handleHover": "#545e62", "scrollbar.handlePressed": "#545e62",
            "accent": "#83c092",
            "syntax.keyword": "#e67e80", "syntax.operator": "#d3c6aa", "syntax.brace": "#d3c6aa",
            "syntax.decorator": "#dbbc7f", "syntax.self": "#e67e80",
            "syntax.className": "#dbbc7f", "syntax.functionName": "#83c092",
            "syntax.comment": "#5f6c6d", "syntax.string": "#a7c080",
            "syntax.docstring": "#5f6c6d", "syntax.number": "#d699b6",
            "tree.indentationGuides.stroke": "#5f6c6d", "tree.trace.color": "#83c092",

            # --- Icon Colors for Project Explorer ---
            "icon.foreground": "#d3c6aa",  # Final fallback for icons
            "icon.colors": {
                "default_folder": "#79b8f2",
                "default_file": "#d3c6aa",
                ".py": "#3572A5", ".js": "#f7df1e", ".ts": "#3178c6", ".html": "#e34f26",
                ".css": "#1572b6", ".json": "#fbc02d", ".md": "#90a4ae", ".gitignore": "#f44336",
                "__pycache__": "#546e7a", "venv": "#8BC34A", ".venv": "#8BC34A",
                "node_modules": "#cb3837", "dist": "#FFCA28"
            }
        }
    },
    "puffin_light": {
        "name": "Puffin Light", "author": "PuffinPy", "type": "light", "is_custom": False,
        "colors": {
            "window.background": "#f5f5f5", "sidebar.background": "#ECECEC",
            "editor.background": "#ffffff", "editor.foreground": "#000000",
            "editorGutter.background": "#f5f5f5", "editorGutter.foreground": "#505050",
            "editor.lineHighlightBackground": "#e0e8f0",
            "editor.matchingBracketBackground": "#c0c8d0", "editor.matchingBracketForeground": "#000000",
            "menu.background": "#e0e0e0", "menu.foreground": "#000000",
            "statusbar.background": "#007acc", "statusbar.foreground": "#ffffff",
            "tab.activeBackground": "#ffffff", "tab.inactiveBackground": "#f5f5f5",
            "tab.activeForeground": "#000000", "tab.inactiveForeground": "#555555",
            "button.background": "#E0E0E0", "button.foreground": "#000000",
            "input.background": "#ffffff", "input.foreground": "#000000", "input.border": "#D0D0D0",
            "scrollbar.background": "#f0f0f0", "scrollbar.handle": "#cccccc",
            "scrollbar.handleHover": "#bbbbbb", "scrollbar.handlePressed": "#aaaaaa",
            "accent": "#007ACC",
            "syntax.keyword": "#0000ff", "syntax.operator": "#000000", "syntax.brace": "#a00050",
            "syntax.decorator": "#267f99", "syntax.self": "#800080", "syntax.className": "#267f99",
            "syntax.functionName": "#795e26", "syntax.comment": "#008000", "syntax.string": "#a31515",
            "syntax.docstring": "#a31515", "syntax.number": "#098658",
            "tree.indentationGuides.stroke": "#D0D0D0", "tree.trace.color": "#007ACC",

            # --- Icon Colors for Project Explorer ---
            "icon.foreground": "#2f383e",  # Final fallback for icons
            "icon.colors": {
                "default_folder": "#0366d6", "default_file": "#2f383e",
                ".py": "#3572A5", ".js": "#f7df1e", ".ts": "#3178c6", ".html": "#e34f26",
                ".css": "#1572b6", ".json": "#fbc02d", ".md": "#586069", ".gitignore": "#d73a49",
                "__pycache__": "#b0bec5", "venv": "#22863a", ".venv": "#22863a",
                "node_modules": "#cb3837", "dist": "#FFCA28"
            }
        }
    }
}


def get_arrow_svg_uri(direction: str, color: str) -> str:
    path_data = SVG_ARROW_PATHS.get(direction, "")
    if not path_data: return ""
    svg_content = f'<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 16 16"><path fill="{color}" d="{path_data}" /></svg>'
    b64_content = base64.b64encode(svg_content.encode('utf-8')).decode('utf-8')
    return f"data:image/svg+xml;base64,{b64_content}"


class ThemeManager:
    def __init__(self):
        self.all_themes_data: Dict[str, Dict] = {}
        self.current_theme_id: str = "puffin_dark"
        self.current_theme_data: Dict[str, Any] = {}
        self.reload_themes()
        log.info(f"ThemeManager initialized. Current theme: '{self.current_theme_id}'")

    def reload_themes(self):
        self.all_themes_data = self._load_all_themes()
        last_theme_id = settings_manager.get("last_theme_id", "puffin_dark")
        if last_theme_id not in self.all_themes_data:
            last_theme_id = "puffin_dark"
            settings_manager.set("last_theme_id", last_theme_id)
        self.current_theme_id = last_theme_id
        self.current_theme_data = self.all_themes_data.get(self.current_theme_id, {})

    def _load_all_themes(self) -> Dict[str, Dict]:
        all_themes = BUILT_IN_THEMES.copy()
        if not os.path.exists(CUSTOM_THEMES_FILE_PATH) and os.path.exists(DEFAULT_CUSTOM_THEMES_FILE_PATH):
            try:
                os.makedirs(os.path.dirname(CUSTOM_THEMES_FILE_PATH), exist_ok=True)
                shutil.copy2(DEFAULT_CUSTOM_THEMES_FILE_PATH, CUSTOM_THEMES_FILE_PATH)
            except Exception as e:
                log.error(f"Failed to copy default custom themes: {e}")
        if os.path.exists(CUSTOM_THEMES_FILE_PATH):
            try:
                with open(CUSTOM_THEMES_FILE_PATH, 'r', encoding='utf-8') as f:
                    custom_themes_data = json.load(f)
                    for theme_data in custom_themes_data.values():
                        theme_data['is_custom'] = True
                    all_themes.update(custom_themes_data)
            except Exception as e:
                log.error(f"Error loading user custom themes: {e}")
        return all_themes

    def get_available_themes_for_ui(self) -> Dict[str, str]:
        return {tid: d.get("name", tid) for tid, d in
                sorted(self.all_themes_data.items(), key=lambda i: i[1].get("name", i[0]).lower())}

    def set_theme(self, theme_id: str, app_instance: Optional[QApplication] = None):
        if theme_id not in self.all_themes_data: theme_id = "puffin_dark"
        self.current_theme_id = theme_id
        self.current_theme_data = self.all_themes_data.get(theme_id, {})
        settings_manager.set("last_theme_id", theme_id)
        self.apply_theme_to_app(app_instance or QApplication.instance())
        log.info(f"Theme set to '{self.current_theme_data.get('name', 'Unknown')}'")

    def apply_theme_to_app(self, app: Optional[QApplication]):
        if not app or not self.current_theme_data: return
        # ... (The lengthy stylesheet generation can remain as-is)
        colors = self.current_theme_data.get("colors", {})

        def c(key: str, fallback: str) -> str: return colors.get(key, fallback)

        def adjust_color(hex_str: str, factor: int) -> str:
            color = QColor(hex_str);
            return color.lighter(factor).name() if factor > 100 else color.darker(factor).name()

        accent, win_bg, btn_bg, btn_fg = c('accent', '#83c092'), c('window.background', '#2f383e'), c(
            'button.background', '#424d53'), c('button.foreground', '#d3c6aa')
        input_bg, input_fg, input_border, sidebar_bg = c('input.background', '#3a4145'), c('input.foreground',
                                                                                           '#d3c6aa'), c('input.border',
                                                                                                         '#5f6c6d'), c(
            'sidebar.background', '#2a3338')
        combo_arrow, spin_up, spin_down = get_arrow_svg_uri('down', input_fg), get_arrow_svg_uri('up',
                                                                                                 input_fg), get_arrow_svg_uri(
            'down', input_fg)
        stylesheet = f"""QWidget{{background-color:{win_bg};color:{input_fg};border:none;}}QMainWindow,QDialog{{background-color:{win_bg};}}QPushButton{{background-color:{btn_bg};color:{btn_fg};border:1px solid {input_border};border-radius:4px;padding:6px 12px;min-width:80px;}}QPushButton:hover{{background-color:{adjust_color(btn_bg, 115)};border-color:{accent};}}QPushButton:pressed{{background-color:{adjust_color(btn_bg, 95)};}}QPushButton:disabled{{background-color:{adjust_color(btn_bg, 105)};color:{c('editorGutter.foreground', '#888')};border-color:{adjust_color(input_border, 110)};}}QSplitter::handle{{background-color:{sidebar_bg};width:1px;image:none;}}QSplitter::handle:hover{{background-color:{accent};}}QMenuBar{{background-color:{adjust_color(win_bg, 105)};border-bottom:1px solid {input_border};}}QMenuBar::item{{padding:6px 12px;}}QMenuBar::item:selected{{background-color:{accent};color:{c('button.foreground', '#000')};}}QMenu{{background-color:{c('menu.background', '#3a4145')};border:1px solid {input_border};padding:4px;}}QMenu::item{{padding:6px 24px;}}QMenu::item:selected{{background-color:{accent};color:{c('button.foreground', '#000')};}}QTabWidget::pane{{border:none;}}QTabBar::tab{{background:transparent;color:{c('tab.inactiveForeground', '#5f6c6d')};padding:8px 15px;border:none;border-bottom:2px solid transparent;}}QTabBar::tab:hover{{background:{adjust_color(win_bg, 110)};}}QTabBar::tab:selected{{color:{c('tab.activeForeground', '#d3c6aa')};border-bottom:2px solid {accent};}}QToolButton{{background:transparent;border:none;border-radius:4px;padding:4px;}}QToolButton:hover{{background-color:{adjust_color(btn_bg, 120)};}}QAbstractItemView{{background-color:{sidebar_bg};outline:0;}}QTreeView,QListWidget,QTableWidget,QTreeWidget{{alternate-background-color:{adjust_color(sidebar_bg, 103)};}}QTreeView::item:hover,QListWidget::item:hover{{background-color:{adjust_color(sidebar_bg, 120)};}}QTreeView::item:selected,QListWidget::item:selected{{background-color:{accent};color:{c('button.foreground', '#000')};}}QHeaderView::section{{background-color:{adjust_color(sidebar_bg, 110)};padding:4px;border:1px solid {win_bg};}}QDockWidget::title{{background-color:{adjust_color(win_bg, 105)};text-align:left;padding:5px;border-bottom:1px solid {input_border};}}QGroupBox{{font-weight:bold;border:1px solid {input_border};border-radius:4px;margin-top:10px;}}QGroupBox::title{{subcontrol-origin:margin;subcontrol-position:top left;padding:0 5px 0 5px;left:10px;background-color:{win_bg};}}QLineEdit,QTextEdit,QPlainTextEdit,QAbstractSpinBox,QComboBox{{background-color:{input_bg};border:1px solid {input_border};border-radius:4px;padding:5px;}}QLineEdit:focus,QAbstractSpinBox:focus,QComboBox:focus,QTextEdit:focus,QPlainTextEdit:focus{{border:1px solid {accent};}}QComboBox::drop-down{{subcontrol-origin:padding;subcontrol-position:top right;width:20px;border-left:1px solid {input_border};}}QComboBox::down-arrow{{image:url({combo_arrow});width:8px;height:8px;}}QSpinBox{{padding-right:22px;}}QSpinBox::up-button,QSpinBox::down-button{{subcontrol-origin:border;width:22px;background-color:transparent;border-left:1px solid {input_border};}}QSpinBox::up-button:hover,QSpinBox::down-button:hover{{background-color:{adjust_color(input_bg, 120)};}}QSpinBox::up-button{{subcontrol-position:top right;}}QSpinBox::down-button{{subcontrol-position:bottom right;}}QSpinBox::up-arrow{{image:url({spin_up});width:8px;height:8px;}}QSpinBox::down-arrow{{image:url({spin_down});width:8px;height:8px;}}QStatusBar{{background-color:{c('statusbar.background', '#282f34')};border-top:1px solid {input_border};color:{c('statusbar.foreground', '#d3c6aa')};}}QScrollBar:vertical{{width:10px;}}QScrollBar:horizontal{{height:10px;}}QScrollBar::handle{{background:{c('scrollbar.handle', '#424d53')};border-radius:5px;min-height:20px;}}QScrollBar::handle:hover{{background:{c('scrollbar.handleHover', '#545e62')};}}QScrollBar::add-line,QScrollBar::sub-line{{height:0px;width:0px;}}QScrollBar::add-page,QScrollBar::sub-page{{background:none;}}"""
        app.setStyleSheet(stylesheet)


theme_manager = ThemeManager()
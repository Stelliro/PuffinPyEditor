# PuffinPyEditor/app_core/theme_manager.py
import os
import json
import base64
import shutil
from typing import Dict, Any, Optional
from PyQt6.QtGui import QColor

from app_core.settings_manager import settings_manager
from utils.logger import log, get_app_data_path
from utils.helpers import get_base_path

SVG_ARROW_PATHS = {'up': "M4 10 L8 6 L12 10", 'down': "M4 6 L8 10 L12 6"}

APP_BASE_PATH = get_base_path()
APP_DATA_ROOT = get_app_data_path()
CUSTOM_THEMES_FILE_PATH = os.path.join(APP_DATA_ROOT, "custom_themes.json")
DEFAULT_CUSTOM_THEMES_FILE_PATH = os.path.join(APP_BASE_PATH, "assets", "themes", "custom_themes.json")
ICON_COLORS_FILE_PATH = os.path.join(APP_DATA_ROOT, "icon_colors.json")
DEFAULT_ICON_COLORS_FILE_PATH = os.path.join(APP_BASE_PATH, "assets", "themes", "icon_colors.json")

BUILT_IN_THEMES = {
    "puffin_dark": {
        "name": "Puffin Dark", "author": "PuffinPy", "type": "dark", "is_custom": False,
        "colors": {
            "window.background": "#2f383e", "sidebar.background": "#2a3338", "editor.background": "#272e33",
            "editor.foreground": "#d3c6aa", "editor.selectionBackground": "#264f78",
            "editor.lineHighlightBackground": "#3a4145", "editor.matchingBracketBackground": "#545e62",
            "editor.matchingBracketForeground": "#d3c6aa",
            "editor.userHighlightBackground": "#83c0924D",
            "editor.breakpoint.color": "#dc143c",
            "editorGutter.background": "#2f383e", "editorGutter.foreground": "#5f6c6d",
            "editorGutter.hoverBackground": "#83c0921a",
            "editorLineNumber.foreground": "#5f6c6d", "editorLineNumber.activeForeground": "#d3c6aa",
            "gutter.activeLineNumberForeground": "#d3c6aa",
            "menu.background": "#3a4145", "menu.foreground": "#d3c6aa", "statusbar.background": "#282f34",
            "statusbar.foreground": "#d3c6aa", "tab.activeBackground": "#272e33",
            "tab.inactiveBackground": "#2f383e", "tab.activeForeground": "#d3c6aa",
            "tab.inactiveForeground": "#5f6c6d", "button.background": "#424d53",
            "button.foreground": "#d3c6aa", "input.background": "#3a4145", "input.foreground": "#d3c6aa",
            "input.border": "#5f6c6d", "scrollbar.background": "#2f383e", "scrollbar.handle": "#424d53",
            "scrollbar.handleHover": "#545e62", "scrollbar.handlePressed": "#545e62",
            "accent": "#83c092", "syntax.keyword": "#e67e80", "syntax.operator": "#d3c6aa",
            "syntax.brace": "#d3c6aa", "syntax.decorator": "#dbbc7f", "syntax.self": "#e67e80",
            "syntax.className": "#dbbc7f", "syntax.functionName": "#83c092", "syntax.comment": "#5f6c6d",
            "syntax.string": "#a7c080", "syntax.docstring": "#5f6c6d", "syntax.number": "#d699b6",
            "tree.indentationGuides.stroke": "#5f6c6d", "tree.trace.color": "#83c092",
            "git.added": "#a7c080", "git.modified": "#dbbc7f", "git.deleted": "#e67e80",
            "git.status.foreground": "#87ceeb"
        }
    },
    "puffin_light": {
        "name": "Puffin Light", "author": "PuffinPy", "type": "light", "is_custom": False,
        "colors": {
            "window.background": "#f5f5f5", "sidebar.background": "#ECECEC", "editor.background": "#ffffff",
            "editor.foreground": "#000000", "editor.selectionBackground": "#add6ff",
            "editor.lineHighlightBackground": "#e0e8f0", "editor.matchingBracketBackground": "#c0c8d0",
            "editor.matchingBracketForeground": "#000000",
            "editor.userHighlightBackground": "#007acc4D",
            "editor.breakpoint.color": "#ff0000",
            "editorGutter.background": "#f5f5f5", "editorGutter.foreground": "#505050",
            "editorGutter.hoverBackground": "#007acc1a",
            "editorLineNumber.foreground": "#9e9e9e", "editorLineNumber.activeForeground": "#000000",
            "gutter.activeLineNumberForeground": "#000000",
            "menu.background": "#e0e0e0", "menu.foreground": "#000000", "statusbar.background": "#007acc",
            "statusbar.foreground": "#ffffff", "tab.activeBackground": "#ffffff",
            "tab.inactiveBackground": "#f5f5f5", "tab.activeForeground": "#000000",
            "tab.inactiveForeground": "#555555", "button.background": "#E0E0E0",
            "button.foreground": "#000000", "input.background": "#ffffff", "input.foreground": "#000000",
            "input.border": "#D0D0D0", "scrollbar.background": "#f0f0f0", "scrollbar.handle": "#cccccc",
            "scrollbar.handleHover": "#bbbbbb", "scrollbar.handlePressed": "#aaaaaa",
            "accent": "#007ACC", "syntax.keyword": "#0000ff", "syntax.operator": "#000000",
            "syntax.brace": "#a00050", "syntax.decorator": "#267f99", "syntax.self": "#800080",
            "syntax.className": "#267f99", "syntax.functionName": "#795e26", "syntax.comment": "#008000",
            "syntax.string": "#a31515", "syntax.docstring": "#a31515", "syntax.number": "#098658",
            "tree.indentationGuides.stroke": "#D0D0D0", "tree.trace.color": "#007ACC",
            "git.added": "#28a745", "git.modified": "#f1e05a", "git.deleted": "#d73a49",
            "git.status.foreground": "#007ACC"
        }
    }
}


def get_arrow_svg_uri(direction: str, color: str) -> str:
    path_data = SVG_ARROW_PATHS.get(direction, "");
    if not path_data: return ""
    svg_content = f'<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 16 16"><path fill="{color}" d="{path_data}" /></svg>'
    b64_content = base64.b64encode(svg_content.encode('utf-8')).decode('utf-8');
    return f"data:image/svg+xml;base64,{b64_content}"


class ThemeManager:
    def __init__(self):
        self.all_themes_data: Dict[str, Dict] = {}
        self.icon_colors: Dict[str, str] = {}
        self.current_theme_id: str = "puffin_dark"
        self.current_theme_data: Dict[str, Any] = {}
        self.reload_themes()
        log.info(f"ThemeManager initialized. Current theme: '{self.current_theme_id}'")

    def reload_themes(self):
        self.icon_colors = self._load_icon_colors()
        self.all_themes_data = self._load_all_themes()
        last_theme_id = settings_manager.get("last_theme_id", "puffin_dark")
        if last_theme_id not in self.all_themes_data:
            last_theme_id = "puffin_dark"
            settings_manager.set("last_theme_id", last_theme_id)
        self.current_theme_id = last_theme_id
        # We don't call set_theme here anymore to avoid circular dependencies
        self.current_theme_data = self.all_themes_data.get(self.current_theme_id, {})
        if 'colors' in self.current_theme_data:
            self.current_theme_data['colors']['icon.colors'] = self.icon_colors

    def _load_icon_colors(self) -> Dict[str, str]:
        """Loads default and user icon colors, with user settings overriding defaults."""
        colors = {}
        if not os.path.exists(ICON_COLORS_FILE_PATH) and os.path.exists(DEFAULT_ICON_COLORS_FILE_PATH):
            try:
                os.makedirs(os.path.dirname(ICON_COLORS_FILE_PATH), exist_ok=True)
                shutil.copy2(DEFAULT_ICON_COLORS_FILE_PATH, ICON_COLORS_FILE_PATH)
                log.info(f"Copied default icon colors to {ICON_COLORS_FILE_PATH}")
            except Exception as e:
                log.error(f"Failed to copy default icon colors: {e}")

        try:
            with open(DEFAULT_ICON_COLORS_FILE_PATH, 'r', encoding='utf-8') as f:
                colors.update(json.load(f))
            if os.path.exists(ICON_COLORS_FILE_PATH):
                with open(ICON_COLORS_FILE_PATH, 'r', encoding='utf-8') as f:
                    colors.update(json.load(f))
        except (IOError, json.JSONDecodeError) as e:
            log.error(f"Could not load icon color schemes: {e}")

        return colors

    def _load_all_themes(self) -> Dict[str, Dict]:
        all_themes = BUILT_IN_THEMES.copy()
        custom_themes_path = os.path.join(get_app_data_path(), "custom_themes.json")
        default_custom_themes_path = os.path.join(get_base_path(), "assets", "themes", "custom_themes.json")

        if not os.path.exists(custom_themes_path) and os.path.exists(default_custom_themes_path):
            try:
                os.makedirs(os.path.dirname(custom_themes_path), exist_ok=True)
                shutil.copy2(default_custom_themes_path, custom_themes_path)
            except Exception as e:
                log.error(f"Failed to copy default custom themes: {e}")

        if os.path.exists(custom_themes_path):
            try:
                with open(custom_themes_path, 'r', encoding='utf-8') as f:
                    custom_themes = json.load(f)
                    for theme in custom_themes.values():
                        theme['is_custom'] = True
                    all_themes.update(custom_themes)
            except Exception as e:
                log.error(f"Error loading custom themes: {e}")
        return all_themes

    def get_available_themes_for_ui(self) -> Dict[str, str]:
        return {tid: d.get("name", tid) for tid, d in
                sorted(self.all_themes_data.items(), key=lambda i: i[1].get("name", i[0]).lower())}

    def set_theme(self, theme_id: str, app_instance: Optional['QApplication'] = None):
        if theme_id not in self.all_themes_data:
            theme_id = "puffin_dark"
        self.current_theme_id = theme_id
        self.current_theme_data = self.all_themes_data.get(theme_id, {})

        if 'colors' not in self.current_theme_data:
            log.warning(f"Theme '{theme_id}' is missing the 'colors' dictionary. UI may not render correctly.")
        else:
            self.current_theme_data['colors']['icon.colors'] = self.icon_colors

        settings_manager.set("last_theme_id", theme_id)
        # Import moved here to avoid circular dependency
        from PyQt6.QtWidgets import QApplication
        self.apply_theme_to_app(app_instance or QApplication.instance())
        log.info(f"Theme set to '{self.current_theme_data.get('name', 'Unknown')}'")

    def add_or_update_custom_theme(self, theme_id: str, theme_data: dict):
        custom_themes_path = os.path.join(get_app_data_path(), "custom_themes.json")
        try:
            custom_themes = {}
            if os.path.exists(custom_themes_path):
                with open(custom_themes_path, 'r', encoding='utf-8') as f:
                    custom_themes = json.load(f)
            custom_themes[theme_id] = theme_data
            with open(custom_themes_path, 'w', encoding='utf-8') as f:
                json.dump(custom_themes, f, indent=4)
            self.reload_themes()
        except (IOError, json.JSONDecodeError) as e:
            log.error(f"Failed to save custom theme '{theme_id}': {e}")

    def delete_custom_theme(self, theme_id: str):
        custom_themes_path = os.path.join(get_app_data_path(), "custom_themes.json")
        try:
            custom_themes = {}
            if os.path.exists(custom_themes_path):
                with open(custom_themes_path, 'r', encoding='utf-8') as f:
                    custom_themes = json.load(f)
            if theme_id in custom_themes:
                del custom_themes[theme_id]
                with open(custom_themes_path, 'w', encoding='utf-8') as f:
                    json.dump(custom_themes, f, indent=4)
                self.reload_themes()
        except (IOError, json.JSONDecodeError) as e:
            log.error(f"Failed to delete custom theme '{theme_id}': {e}")

    def apply_theme_to_app(self, app: Optional['QApplication']):
        if not app or not self.current_theme_data: return
        colors = self.current_theme_data.get("colors", {})

        def c(key: str, fb: str) -> str: return colors.get(key, fb)

        def adj(h: str, f: int) -> str:
            c_obj = QColor(h)
            is_light_theme = self.current_theme_data.get('type', 'dark') == 'light'
            return c_obj.darker(f).name() if f > 100 and is_light_theme else c_obj.lighter(f).name()

        ac, wb, bb, bf, ib, igf, ibd, sb = (
            c('accent', '#83c092'), c('window.background', '#2f383e'),
            c('button.background', '#424d53'), c('button.foreground', '#d3c6aa'),
            c('input.background', '#3a4145'), c('editor.foreground', '#d3c6aa'),
            c('input.border', '#5f6c6d'), c('sidebar.background', '#2a3338')
        )

        arrow_color = c('editor.foreground', '#d3c6aa')
        combo_arrow, spin_up, spin_down = (
            get_arrow_svg_uri('down', arrow_color),
            get_arrow_svg_uri('up', arrow_color),
            get_arrow_svg_uri('down', arrow_color)
        )

        stylesheet = f"""
            QWidget {{ background-color: {wb}; color: {igf}; border: none; }}
            QMainWindow, QDialog {{ background-color: {wb}; }}
            QSplitter::handle {{ background-color: {sb}; width: 1px; image: none; }}
            QSplitter::handle:hover {{ background-color: {ac}; }}

            /* Buttons */
            QPushButton {{
                background-color: {bb}; color: {bf}; border: 1px solid {ibd};
                border-radius: 4px; padding: 6px 12px; min-width: 80px;
            }}
            QPushButton:hover {{ background-color: {adj(bb, 115)}; border-color: {ac}; }}
            QPushButton:pressed {{ background-color: {adj(bb, 95)}; }}
            QPushButton:disabled {{
                background-color: {adj(bb, 105)}; color: {c('editorGutter.foreground', '#888')};
                border-color: {adj(ibd, 110)};
            }}
            QToolButton {{ background: transparent; border: none; border-radius: 4px; padding: 4px; }}
            QToolButton:hover {{ background-color: {adj(bb, 120)}; }}

            /* Menus and Bars */
            QMenuBar {{ background-color: {adj(wb, 105)}; border-bottom: 1px solid {ibd}; }}
            QMenuBar::item {{ padding: 6px 12px; }}
            QMenuBar::item:selected {{ background-color: {ac}; color: {c('button.foreground', '#000')}; }}
            QMenu {{ background-color: {c('menu.background', '#3a4145')}; border: 1px solid {ibd}; padding: 4px; }}
            QMenu::item {{ padding: 6px 24px; }}
            QMenu::item:selected {{ background-color: {ac}; color: {c('button.foreground', '#000')}; }}
            QStatusBar {{
                background-color: {c('statusbar.background', '#282f34')}; border-top: 1px solid {ibd};
                color: {c('statusbar.foreground', '#d3c6aa')};
            }}

            /* THEME: Signature Tab Bar Styling */
            QTabWidget::pane {{ border: none; }}
            QTabBar::tab {{
                background: transparent; color: {c('tab.inactiveForeground', '#5f6c6d')};
                padding: 8px 15px; border: none; border-bottom: 2px solid transparent;
            }}
            QTabBar::tab:hover {{ background: {adj(wb, 110)}; }}
            QTabBar::tab:selected {{ color: {c('tab.activeForeground', '#d3c6aa')}; border-bottom: 2px solid {ac}; }}
            /* Specific style for editor tabs to blend the bottom border */
            QTabWidget#MainTabWidget > QTabBar::tab:selected {{ border-bottom-color: {c('editor.background', '#272e33')}; }}

            /* THEME: Signature Toolbar Styling */
            QFrame#ExplorerToolbar {{
                background-color: {c('sidebar.background', '#2a3338')};
                border-bottom: 1px solid {c('input.border', '#5f6c6d')};
            }}

            /* Inputs */
            QLineEdit, QTextEdit, QPlainTextEdit, QAbstractSpinBox, QComboBox {{
                background-color: {ib}; border: 1px solid {ibd}; border-radius: 4px; padding: 5px;
            }}
            QLineEdit:focus, QAbstractSpinBox:focus, QComboBox:focus, QTextEdit:focus, QPlainTextEdit:focus {{
                border: 1px solid {ac};
            }}

            /* Combo & Spin Box Arrows */
            QComboBox::drop-down {{
                subcontrol-origin: padding; subcontrol-position: top right;
                width: 20px; border-left: 1px solid {ibd};
            }}
            QComboBox::down-arrow {{ image: url({combo_arrow}); width: 8px; height: 8px; }}
            QSpinBox {{ padding-right: 22px; }}
            QSpinBox::up-button, QSpinBox::down-button {{
                subcontrol-origin: border; width: 22px; background-color: transparent;
                border-left: 1px solid {ibd};
            }}
            QSpinBox::up-button:hover, QSpinBox::down-button:hover {{ background-color: {adj(ib, 120)}; }}
            QSpinBox::up-button {{ subcontrol-position: top right; }}
            QSpinBox::down-button {{ subcontrol-position: bottom right; }}
            QSpinBox::up-arrow {{ image: url({spin_up}); width: 8px; height: 8px; }}
            QSpinBox::down-arrow {{ image: url({spin_down}); width: 8px; height: 8px; }}

            /* Item Views */
            QAbstractItemView {{ background-color: {sb}; outline: 0; }}
            QTreeView, QListWidget, QTableWidget, QTreeWidget {{ alternate-background-color: {adj(sb, 103)}; }}
            QTreeView::item:hover, QListWidget::item:hover {{ background-color: {adj(sb, 120)}; }}
            QTreeView::item:selected {{ background-color: {ac}; color: {c('button.foreground', '#000')}; }}
            QHeaderView::section {{ background-color: {adj(sb, 110)}; padding: 4px; border: 1px solid {wb}; }}
            QDockWidget::title {{
                background-color: {adj(wb, 105)}; text-align: left; padding: 5px;
                border-bottom: 1px solid {ibd};
            }}
            QGroupBox {{
                font-weight: bold; border: 1px solid {adj(ibd, 115)};
                border-radius: 6px; margin-top: 1em;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin; left: 10px; padding: 0 4px;
                color: {ac}; background-color: {wb};
            }}

            /* Scrollbar */
            QScrollBar:vertical {{ width: 10px; }}
            QScrollBar:horizontal {{ height: 10px; }}
            QScrollBar::handle {{ background: {c('scrollbar.handle', '#424d53')}; border-radius: 5px; min-height: 20px; }}
            QScrollBar::handle:hover {{ background: {c('scrollbar.handleHover', '#545e62')}; }}
            QScrollBar::add-line, QScrollBar::sub-line {{ height: 0px; width: 0px; }}
            QScrollBar::add-page, QScrollBar::sub-page {{ background: none; }}
        """
        app.setStyleSheet(stylesheet)
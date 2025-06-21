# PuffinPyEditor/app_core/theme_manager.py
import os
import json
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QColor, QFont
from utils.logger import log
from app_core.settings_manager import settings_manager

CUSTOM_THEMES_FILE_PATH = os.path.join("assets", "themes", "custom_themes.json")
BUILT_IN_THEMES = {
    "puffin_dark": {
        "name": "Puffin Dark", "author": "PuffinPy", "type": "dark",
        "font_suggestion": {"family": ["Fira Code", "Consolas"], "size": 12},
        "colors": {"window.background": "#2f383e", "sidebar.background": "#2a3338", "editor.background": "#272e33",
                   "editor.foreground": "#d3c6aa", "editorGutter.background": "#2f383e",
                   "editorGutter.foreground": "#5f6c6d", "editor.lineHighlightBackground": "#3a4145",
                   "editor.matchingBracketBackground": "#545e62", "editor.matchingBracketForeground": "#d3c6aa",
                   "menu.background": "#3a4145", "menu.foreground": "#d3c6aa", "statusbar.background": "#282f34",
                   "statusbar.foreground": "#d3c6aa", "tab.activeBackground": "#272e33",
                   "tab.inactiveBackground": "#2f383e", "tab.activeForeground": "#d3c6aa",
                   "tab.inactiveForeground": "#5f6c6d", "button.background": "#424d53", "button.foreground": "#d3c6aa",
                   "input.background": "#3a4145", "input.foreground": "#d3c6aa", "input.border": "#282f34",
                   "scrollbar.background": "#2f383e", "scrollbar.handle": "#424d53", "scrollbar.handleHover": "#545e62",
                   "scrollbar.handlePressed": "#545e62", "accent": "#83c092", "syntax.keyword": "#e67e80",
                   "syntax.operator": "#d3c6aa", "syntax.brace": "#d3c6aa", "syntax.decorator": "#dbbc7f",
                   "syntax.self": "#e67e80", "syntax.className": "#dbbc7f", "syntax.functionName": "#83c092",
                   "syntax.comment": "#5f6c6d", "syntax.string": "#a7c080", "syntax.docstring": "#5f6c6d",
                   "syntax.number": "#d699b6"}
    },
    "puffin_light": {
        "name": "Puffin Light", "author": "PuffinPy", "type": "light",
        "font_suggestion": {"family": ["Consolas", "Fira Code"], "size": 11},
        "colors": {"window.background": "#f5f5f5", "sidebar.background": "#ECECEC", "editor.background": "#ffffff",
                   "editor.foreground": "#000000", "editorGutter.background": "#f5f5f5",
                   "editorGutter.foreground": "#505050", "editor.lineHighlightBackground": "#e0e8f0",
                   "editor.matchingBracketBackground": "#c0c8d0", "editor.matchingBracketForeground": "#000000",
                   "menu.background": "#e0e0e0", "menu.foreground": "#000000", "statusbar.background": "#007acc",
                   "statusbar.foreground": "#ffffff", "tab.activeBackground": "#ffffff",
                   "tab.inactiveBackground": "#f5f5f5", "tab.activeForeground": "#000000",
                   "tab.inactiveForeground": "#555555", "button.background": "#E0E0E0", "button.foreground": "#000000",
                   "input.background": "#ffffff", "input.foreground": "#000000", "input.border": "#D0D0D0",
                   "scrollbar.background": "#f0f0f0", "scrollbar.handle": "#cccccc", "scrollbar.handleHover": "#bbbbbb",
                   "scrollbar.handlePressed": "#aaaaaa", "accent": "#007ACC", "syntax.keyword": "#0000ff",
                   "syntax.operator": "#000000", "syntax.brace": "#a00050", "syntax.decorator": "#267f99",
                   "syntax.self": "#800080", "syntax.className": "#267f99", "syntax.functionName": "#795e26",
                   "syntax.comment": "#008000", "syntax.string": "#a31515", "syntax.docstring": "#a31515",
                   "syntax.number": "#098658"}
    }
}


class ThemeManager:
    def __init__(self):
        self.reload_themes()
        last_theme_id = settings_manager.get("last_theme_id", "puffin_dark")
        if last_theme_id not in self.all_themes_data:
            last_theme_id = "puffin_dark"
            settings_manager.set("last_theme_id", last_theme_id)
        self.current_theme_id = last_theme_id
        self.current_theme_data = self.all_themes_data.get(self.current_theme_id)
        log.info(f"ThemeManager initialized. Current theme: '{self.current_theme_id}'")

    def reload_themes(self):
        self.all_themes_data = self._load_all_themes()
        last_theme_id = settings_manager.get("last_theme_id", "puffin_dark")
        if last_theme_id not in self.all_themes_data:
            last_theme_id = "puffin_dark";
            settings_manager.set("last_theme_id", last_theme_id)
        self.current_theme_id = last_theme_id
        self.current_theme_data = self.all_themes_data.get(self.current_theme_id)

    def _load_all_themes(self):
        all_themes = BUILT_IN_THEMES.copy()
        if os.path.exists(CUSTOM_THEMES_FILE_PATH):
            try:
                with open(CUSTOM_THEMES_FILE_PATH, 'r', encoding='utf-8') as f:
                    all_themes.update(json.load(f))
            except Exception as e:
                log.error(f"Error loading custom themes: {e}")
        return all_themes

    def get_available_themes_for_ui(self):
        return {tid: d.get("name", tid) for tid, d in
                sorted(self.all_themes_data.items(), key=lambda i: i[1].get("name", i[0]).lower())}

    def set_theme(self, theme_id: str, app_instance=None):
        if theme_id not in self.all_themes_data: return
        self.current_theme_id, self.current_theme_data = theme_id, self.all_themes_data[theme_id]
        settings_manager.set("last_theme_id", theme_id)
        self.apply_theme_to_app(app_instance or QApplication.instance())
        log.info(f"Theme set to '{self.current_theme_data.get('name')}'")

    def apply_theme_to_app(self, app_instance=None):
        app = app_instance or QApplication.instance();
        colors = self.current_theme_data.get("colors", {});

        def c(key, fallback):
            return colors.get(key, fallback)

        def adjust_color(hex_str, factor):
            color = QColor(hex_str);
            return color.lighter(factor) if factor > 100 else color.darker(factor)

        accent = c('accent', '#83c092')
        win_bg = c('window.background', '#2f383e')
        input_border = c('input.border', '#5f6c6d')
        input_fg = c('input.foreground', '#d3c6aa')

        stylesheet = f"""
            QWidget {{ background-color: {win_bg}; color: {input_fg}; border: none; }}
            QMainWindow, QDialog {{ background-color: {win_bg}; }}
            QSplitter::handle {{ background-color: {c('sidebar.background', '#2a3338')}; width: 1px; image: none; }}
            QSplitter::handle:hover {{ background-color: {accent}; }}
            QMenuBar {{ background-color: {adjust_color(win_bg, 105).name()}; border-bottom: 1px solid {c('input.border', '#282f34')}; }}
            QMenuBar::item {{ padding: 6px 12px; }}
            QMenuBar::item:selected {{ background-color: {accent}; color: #000; }}
            QMenu {{ background-color: {adjust_color(win_bg, 110).name()}; border: 1px solid {c('input.border', '#282f34')}; padding: 4px; }}
            QMenu::item {{ padding: 6px 24px; }}
            QMenu::item:selected {{ background-color: {accent}; color: #000; }}
            QTabWidget::pane {{ border: none; }}
            QTabBar::tab {{
                background: transparent; color: {c('tab.inactiveForeground', '#5f6c6d')};
                padding: 8px 15px; border: none; border-bottom: 2px solid transparent;
            }}
            QTabBar::tab:hover {{ background: {adjust_color(win_bg, 110).name()}; }}
            QTabBar::tab:selected {{ color: {c('tab.activeForeground', '#d3c6aa')}; border-bottom: 2px solid {accent}; }}
            QToolButton {{ background: transparent; border-radius: 4px; padding: 4px; }}
            QToolButton:hover {{ background-color: {adjust_color(c('button.background', '#424d53'), 120).name()}; }}
            QAbstractItemView {{ background-color: {c('sidebar.background', '#2a3338')}; outline: 0; }}
            QTreeView, QListWidget, QTableWidget, QTreeWidget {{ alternate-background-color: {adjust_color(c('sidebar.background', '#2a3338'), 103).name()}; }}
            QTreeView::item:hover, QListWidget::item:hover, QTableWidget::item:hover, QTreeWidget::item:hover {{ background-color: {adjust_color(win_bg, 120).name()}; }}
            QTreeView::item:selected, QListWidget::item:selected, QTableWidget::item:selected, QTreeWidget::item:selected {{ background-color: {accent}; color: #000; }}
            QHeaderView::section {{ background-color: {adjust_color(c('sidebar.background', '#2a3338'), 110).name()}; padding: 4px; border: 1px solid {win_bg}; }}
            QDockWidget {{ titlebar-close-icon: url(none); titlebar-normal-icon: url(none); }}
            QDockWidget::title {{ background-color: {adjust_color(win_bg, 105).name()}; text-align: left; padding: 5px; border-bottom: 1px solid {input_border}; }}

            QLineEdit, QTextEdit, QPlainTextEdit, QAbstractSpinBox, QComboBox {{
                background-color: {c('input.background', '#3a4145')};
                border: 1px solid {input_border};
                border-radius: 4px;
                padding: 5px;
            }}
            QLineEdit:focus, QAbstractSpinBox:focus, QComboBox:focus, QTextEdit:focus, QPlainTextEdit:focus {{
                border: 1px solid {accent};
            }}

            QComboBox {{ padding-right: 20px; }}
            QComboBox::drop-down {{
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 20px;
                border-left: 1px solid {input_border};
            }}
            QComboBox::down-arrow {{
                width: 0; height: 0;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 6px solid {input_fg};
                margin: 0 auto;
            }}
            QComboBox::down-arrow:on, QComboBox::down-arrow:hover {{
                border-top-color: {accent};
            }}

            QSpinBox {{ padding-right: 22px; }}
            QSpinBox::up-button, QSpinBox::down-button {{
                subcontrol-origin: border;
                width: 22px;
                background-color: transparent;
                border-left: 1px solid {input_border};
            }}
            QSpinBox::up-button:hover, QSpinBox::down-button:hover {{
                background-color: {adjust_color(c('input.background', '#3a4145'), 120).name()};
            }}
            QSpinBox::up-button {{
                subcontrol-position: top right;
            }}
            QSpinBox::down-button {{
                subcontrol-position: bottom right;
            }}
            QSpinBox::up-arrow {{
                width: 0; height: 0;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-bottom: 6px solid {input_fg};
            }}
            QSpinBox::down-arrow {{
                width: 0; height: 0;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 6px solid {input_fg};
            }}
            QSpinBox::up-arrow:hover, QSpinBox::up-arrow:pressed {{
                border-bottom-color: {accent};
            }}
            QSpinBox::down-arrow:hover, QSpinBox::down-arrow:pressed {{
                border-top-color: {accent};
            }}

            QStatusBar {{ background-color: {adjust_color(win_bg, 105).name()}; border-top: 1px solid {input_border}; }}
            QScrollBar:vertical {{ width: 10px; }} QScrollBar:horizontal {{ height: 10px; }}
            QScrollBar::handle {{ background: {c('scrollbar.handle', '#424d53')}; border-radius: 5px; }}
            QScrollBar::handle:hover {{ background: {c('scrollbar.handleHover', '#545e62')}; }}
            QScrollBar::add-line, QScrollBar::sub-line {{ height: 0px; }}
            QScrollBar::add-page, QScrollBar::sub-page {{ background: none; }}
        """

        forced_styles = """
            QPushButton {
                background-color: #0078d4;
                color: white;
                border: 1px solid #005a9e;
                padding: 6px 12px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #0089f0;
            }
            QPushButton:pressed {
                background-color: #006ac1;
            }
            QPushButton:disabled {
                background-color: #5a5a5a;
                color: #999999;
                border: 1px solid #4a4a4a;
            }
            QCheckBox {
                spacing: 8px;
            }
            QCheckBox::indicator {
                width: 14px;
                height: 14px;
                border-radius: 3px;
                border: 1px solid #999999;
            }
            QCheckBox::indicator:unchecked {
                background-color: #555555;
            }
            QCheckBox::indicator:checked {
                background-color: #0078d4;
                border: 1px solid #005a9e;
            }
            QCheckBox::indicator:hover {
                border: 1px solid #00aaff;
            }
        """

        final_stylesheet = stylesheet + forced_styles

        try:
            app.setStyleSheet(final_stylesheet)
        except Exception as e:
            log.error(f"Failed to apply stylesheet: {e}", exc_info=True)


theme_manager = ThemeManager()
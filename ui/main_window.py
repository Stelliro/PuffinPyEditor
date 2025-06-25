# PuffinPyEditor/ui/main_window.py
import os
import sys
from typing import Optional
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QStatusBar, QSplitter,
                             QTabWidget, QMessageBox, QApplication, QFileDialog, QLabel,
                             QToolButton, QToolBar,
                             QSizePolicy, QMenu)
from PyQt6.QtGui import QAction, QKeySequence, QColor, QFont, QActionGroup, QKeyEvent
from PyQt6.QtCore import Qt, QSize, QTimer, pyqtSignal

import qtawesome as qta

# Core component imports
from utils.logger import log
from utils import versioning
from app_core.settings_manager import settings_manager
from app_core.theme_manager import theme_manager
from app_core.file_handler import FileHandler
from app_core.project_manager import ProjectManager
from app_core.linter_manager import LinterManager
from app_core.plugin_manager import PluginManager
from app_core.completion_manager import CompletionManager
from app_core.update_manager import UpdateManager
from app_core.source_control_manager import SourceControlManager
from app_core.github_manager import GitHubManager
from app_core.puffin_api import PuffinPluginAPI

# UI component imports
from .file_tree_view import FileTreeViewWidget
from .editor_widget import EditorWidget
from .dialogs.preferences_dialog import PreferencesDialog


class MainWindow(QMainWindow):
    untitled_file_counter = 0
    _is_app_closing = False
    theme_changed_signal = pyqtSignal(str)

    def __init__(self, debug_mode: bool = False):
        super().__init__()
        self.debug_mode = debug_mode
        log.info(f"PuffinPyEditor v{versioning.APP_VERSION} starting... (Debug: {self.debug_mode})")

        self._initialize_managers()
        self.puffin_api = PuffinPluginAPI(self)
        log.info("Core API initialized.")

        self.setWindowTitle(f"PuffinPyEditor - v{versioning.APP_VERSION}")
        self._load_window_geometry()
        self._create_core_widgets()
        self._create_core_actions()
        self._create_core_menu()
        self._create_toolbar()
        self._create_layout()
        self._create_statusbar()

        self._load_core_debug_tools()

        self.plugin_manager.discover_and_load_plugins()
        self._connect_plugin_signals()

        self._connect_signals()
        self._apply_theme_and_icons(self.settings.get("last_theme_id"))
        self._initialize_project_views()
        self._update_window_title()
        self._update_editor_actions_state()

        log.info("MainWindow initialized successfully.")

    def _load_core_debug_tools(self):
        """Loads special core debug tools if the application is in debug mode."""
        if not self.debug_mode:
            return

        log.info("Loading core debug tools...")
        try:
            # --- DEFINITIVE FIX V3 ---
            # Step 1: Initialize the framework first to ensure debug_api exists.
            from core_debug_tools.debug_framework.plugin_main import initialize as init_framework
            self.debug_framework_instance = init_framework(self)

            # Step 2: Now that the framework and its menu exist, load other debug tools.
            from core_debug_tools.live_log_viewer.plugin_main import initialize as init_log_viewer
            self.live_log_viewer_instance = init_log_viewer(self)
            # --- END FIX ---

        except Exception as e:
            log.error(f"Failed to load core debug tools: {e}", exc_info=True)
            QMessageBox.critical(
                self, "Debug Tools Failed",
                "Could not initialize the core debugging tools. "
                f"Check logs for details.\n\nError: {e}"
            )

    # ... (The rest of the file from here on is correct and remains unchanged.) ...
    def _initialize_managers(self):
        self.settings = settings_manager
        self.theme_manager = theme_manager
        self.project_manager = ProjectManager()
        self.completion_manager = CompletionManager(self)
        self.github_manager = GitHubManager(self)
        self.git_manager = SourceControlManager(self)
        self.file_handler = FileHandler(self)
        self.linter_manager = LinterManager(self)
        self.update_manager = UpdateManager(self)
        self.plugin_manager = PluginManager(self)
        self.preferences_dialog_instance: Optional[PreferencesDialog] = None
        self.actions: dict[str, QAction] = {}
        self.editor_tabs_data: dict[EditorWidget, dict] = {}
        self.lint_timer = QTimer(self)
        self.lint_timer.setSingleShot(True)
        self.lint_timer.setInterval(1500)
        self.auto_save_timer = QTimer(self)
        self.auto_save_timer.setSingleShot(True)

    def _load_window_geometry(self):
        size = self.settings.get("window_size", [1600, 1000])
        pos = self.settings.get("window_position")
        self.resize(QSize(size[0], size[1]))
        if pos: self.move(pos[0], pos[1])

    def _create_core_widgets(self):
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.tab_widget = QTabWidget()
        self.project_tabs = QTabWidget()

        for tab_widget, action in [(self.tab_widget, self._add_new_tab), (self.project_tabs, self._action_open_folder)]:
            button = QToolButton()
            button.setIcon(qta.icon('fa5s.plus'))
            button.setAutoRaise(True)
            button.clicked.connect(action)
            tab_widget.setCornerWidget(button, Qt.Corner.TopRightCorner)
            tab_widget.setDocumentMode(True)
            tab_widget.setTabsClosable(True)
            tab_widget.setMovable(True)

        self.project_sidebar_container = QWidget()
        sb_layout = QVBoxLayout(self.project_sidebar_container)
        sb_layout.setContentsMargins(0, 0, 0, 0)
        sb_layout.addWidget(self.project_tabs)

    def _create_core_actions(self):
        actions_map = {
            "new_file": ("&New File", self._add_new_tab, "Ctrl+N", 'fa5s.file'),
            "open_file": ("&Open File...", self._action_open_file_dialog, "Ctrl+O", 'fa5s.folder-open'),
            "open_folder": ("Open &Folder...", self._action_open_folder, None, None),
            "close_project": ("&Close Project", self._action_close_project, None, None),
            "save": ("&Save", self._action_save_file, "Ctrl+S", 'fa5s.save'),
            "save_as": ("Save &As...", self._action_save_as, "Ctrl+Shift+S", None),
            "save_all": ("Save A&ll", self._action_save_all, "Ctrl+Alt+S", None),
            "preferences": ("&Preferences...", self._action_open_preferences, "Ctrl+,", None),
            "exit": ("E&xit", self.close, "Ctrl+Q", None),
        }
        for key, (text, cb, sc, icon) in actions_map.items():
            action = QAction(text, self)
            if icon: action.setData(icon)
            action.triggered.connect(cb)
            if sc: action.setShortcut(QKeySequence(sc))
            self.actions[key] = action

    def _create_core_menu(self):
        menu_bar = self.menuBar()
        self.file_menu = menu_bar.addMenu("&File")
        self.edit_menu = menu_bar.addMenu("&Edit")
        self.view_menu = menu_bar.addMenu("&View")
        self.go_menu = menu_bar.addMenu("&Go")
        self.run_menu = menu_bar.addMenu("&Run")
        self.tools_menu = menu_bar.addMenu("&Tools")
        self.help_menu = menu_bar.addMenu("&Help")

        self.file_menu.addActions([self.actions[k] for k in ["new_file", "open_file"]])
        self.recent_files_menu = self.file_menu.addMenu("Open &Recent")
        self._update_recent_files_menu()
        self.file_menu.addSeparator()
        self.file_menu.addActions([self.actions[k] for k in ["open_folder", "close_project"]])
        self.file_menu.addSeparator()
        self.file_menu.addActions([self.actions[k] for k in ["save", "save_as", "save_all"]])
        self.file_menu.addSeparator()
        self.file_menu.addActions([self.actions[k] for k in ["preferences", "exit"]])

        self.theme_menu = self.view_menu.addMenu("&Themes")

    def _create_toolbar(self):
        self.main_toolbar = QToolBar("Main Toolbar")
        self.main_toolbar.setIconSize(QSize(18, 18))
        self.addToolBar(self.main_toolbar)
        self.main_toolbar.addActions([self.actions[k] for k in ["new_file", "open_file", "save"]])
        self.main_toolbar.addSeparator()
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self.main_toolbar.addWidget(spacer)

    def _create_layout(self):
        layout = QHBoxLayout(self.central_widget)
        layout.setContentsMargins(5, 5, 5, 5)
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        self.splitter.addWidget(self.project_sidebar_container)
        self.splitter.addWidget(self.tab_widget)
        layout.addWidget(self.splitter)
        self.splitter.setSizes(self.settings.get("splitter_sizes", [250, 950]))
        self.splitter.setHandleWidth(5)

    def _create_statusbar(self):
        self.setStatusBar(QStatusBar(self))
        self.cursor_label = QLabel(" Ln 1, Col 1 ")
        self.statusBar().addPermanentWidget(self.cursor_label)

    def _connect_plugin_signals(self):
        log.info("Connecting inter-plugin signals...")
        sc_ui_plugin = self.plugin_manager.loaded_plugins.get('source_control_ui', {}).get('instance')
        github_tools_plugin = self.plugin_manager.loaded_plugins.get('github_tools', {}).get('instance')

        if sc_ui_plugin and github_tools_plugin:
            log.info("Connecting Source Control UI -> GitHub Tools.")
            sc_panel = sc_ui_plugin.source_control_panel
            sc_panel.create_release_requested.connect(github_tools_plugin._create_release)
            sc_panel.publish_repo_requested.connect(github_tools_plugin._publish_repo)
            sc_panel.link_to_remote_requested.connect(github_tools_plugin._link_repo)
            sc_panel.change_visibility_requested.connect(github_tools_plugin._change_visibility)
        else:
            if not sc_ui_plugin: log.warning("Could not connect signals: 'source_control_ui' plugin not loaded.")
            if not github_tools_plugin: log.warning("Could not connect signals: 'github_tools' plugin not loaded.")

    def _connect_signals(self):
        self.project_tabs.currentChanged.connect(self._on_project_tab_changed)
        self.project_tabs.tabCloseRequested.connect(self._action_close_project_by_index)
        self.tab_widget.currentChanged.connect(self._on_tab_changed)
        self.tab_widget.tabCloseRequested.connect(self._action_close_tab_by_index)
        self.splitter.splitterMoved.connect(lambda: self.settings.set("splitter_sizes", self.splitter.sizes(), False))
        self.auto_save_timer.timeout.connect(self._auto_save_current_tab)
        self.lint_timer.timeout.connect(self._trigger_file_linter)
        self.completion_manager.definition_found.connect(self._goto_definition_result)

    def _apply_theme_and_icons(self, theme_id: str):
        self.theme_manager.set_theme(theme_id, QApplication.instance())
        self.theme_changed_signal.emit(theme_id)
        accent_color = self.theme_manager.current_theme_data['colors'].get('accent', 'silver')
        icon_color = "#000000" if QColor(accent_color).lightnessF() > 0.6 else "#FFFFFF"
        qta.set_defaults(color=accent_color, color_active=icon_color)

        # This safe list includes actions created by the MainWindow itself.
        # It's safer than iterating through all children.
        actions_with_icons = list(self.actions.values())

        for action in actions_with_icons:
            icon_name = action.data()
            if isinstance(icon_name, str) and icon_name:
                action.setIcon(qta.icon(icon_name))

        # Re-apply icons for any toolbar actions that might have been added by plugins.
        # This is also safe because plugins use the API to add actions which sets string data.
        for action in self.main_toolbar.actions():
            icon_name = action.data()
            if isinstance(icon_name, str) and icon_name:
                action.setIcon(qta.icon(icon_name))

        self._rebuild_theme_menu()
        for i in range(self.tab_widget.count()):
            if isinstance(widget := self.tab_widget.widget(i), EditorWidget):
                widget.highlighter.rehighlight_document()

    def _rebuild_theme_menu(self):
        self.theme_menu.clear()
        group = QActionGroup(self)
        group.setExclusive(True)
        for theme_id, name in self.theme_manager.get_available_themes_for_ui().items():
            action = QAction(name, self, checkable=True,
                             triggered=lambda _, t_id=theme_id: self._on_theme_selected(t_id))
            action.setData(theme_id)
            action.setChecked(theme_id == self.theme_manager.current_theme_id)
            group.addAction(action)
            self.theme_menu.addAction(action)

    def _initialize_project_views(self):
        active_project = self.project_manager.get_active_project_path()
        self.project_tabs.blockSignals(True)
        self.project_tabs.clear()
        open_projects = self.project_manager.get_open_projects()
        self.project_sidebar_container.setVisible(len(open_projects) > 0)
        active_index = 0
        for i, path in enumerate(open_projects):
            tree = FileTreeViewWidget(self.file_handler, self)
            tree.file_open_requested.connect(self._action_open_file)
            tree.file_to_open_created.connect(self._add_new_tab)
            tree.set_project_root(path)
            tab_index = self.project_tabs.addTab(tree, os.path.basename(path))
            self.project_tabs.setTabToolTip(tab_index, path)
            if path == active_project: active_index = i
        self.project_tabs.setCurrentIndex(active_index)
        self.project_tabs.blockSignals(False)
        self._on_project_tab_changed(active_index if open_projects else -1)
        if self.tab_widget.count() == 0: self._add_new_tab(is_placeholder=True)

    def _add_new_tab(self, filepath: Optional[str] = None, content: str = "", is_placeholder: bool = False):
        if self.tab_widget.count() == 1 and isinstance(self.tab_widget.widget(0), QLabel):
            self.tab_widget.removeTab(0)

        if is_placeholder:
            placeholder = QLabel("\n\n\tOpen a file or project to get started.",
                                 alignment=Qt.AlignmentFlag.AlignCenter)
            placeholder.setObjectName("PlaceholderLabel")
            self.tab_widget.addTab(placeholder, "Welcome")
            self.tab_widget.setTabsClosable(False)
            self._update_editor_actions_state()
            return

        self.tab_widget.setTabsClosable(True)
        editor = EditorWidget(self.completion_manager, self)
        editor.set_filepath(filepath)
        editor.set_text(content)
        editor.cursor_position_display_updated.connect(
            lambda line, col: self.cursor_label.setText(f" Ln {line}, Col {col} "))
        editor.content_possibly_changed.connect(self._on_content_changed)
        if not filepath: self.untitled_file_counter += 1
        name = os.path.basename(filepath) if filepath else f"Untitled-{self.untitled_file_counter}"
        index = self.tab_widget.addTab(editor, name)
        self.tab_widget.setTabToolTip(index, filepath or f"Unsaved {name}")
        self.editor_tabs_data[editor] = {'filepath': filepath, 'original_hash': hash(content)}
        self.tab_widget.setCurrentWidget(editor)
        editor.text_area.setFocus()
        self._update_editor_actions_state()
        self._on_content_changed()

    def _action_open_preferences(self):
        if not self.preferences_dialog_instance:
            self.preferences_dialog_instance = PreferencesDialog(self.git_manager, self.github_manager,
                                                                 self.plugin_manager, self)
            self.preferences_dialog_instance.theme_changed_signal.connect(self._on_theme_selected)
            self.preferences_dialog_instance.settings_changed_for_editor_refresh.connect(
                self._on_editor_settings_changed)
        self.preferences_dialog_instance.show()
        self.preferences_dialog_instance.raise_()
        self.preferences_dialog_instance.activateWindow()

    def _on_theme_selected(self, theme_id: str):
        self._apply_theme_and_icons(theme_id)

    def _on_tab_changed(self, index: int):
        self._update_window_title()
        self._update_editor_actions_state()
        self._trigger_file_linter()

    def _on_content_changed(self):
        self._update_window_title()
        self.lint_timer.start()
        if settings_manager.get("auto_save_enabled"): self.auto_save_timer.start(
            settings_manager.get("auto_save_delay_seconds") * 1000)

    def _on_project_tab_changed(self, index: int):
        path = self.project_tabs.tabToolTip(index) if index != -1 else None
        self.project_manager.set_active_project(path)
        self.completion_manager.update_project_path(path)
        if sc_ui_plugin := self.plugin_manager.loaded_plugins.get('source_control_ui', {}).get('instance'):
            sc_panel = sc_ui_plugin.source_control_panel
            if sc_panel:
                sc_panel.refresh_all_projects()
        self._update_window_title()

    def _update_window_title(self):
        title_parts = [f"PuffinPyEditor - v{versioning.APP_VERSION}"]
        if p_path := self.project_manager.get_active_project_path():
            title_parts.insert(0, f"[{os.path.basename(p_path)}]")

        if isinstance(editor := self.tab_widget.currentWidget(), EditorWidget) and editor in self.editor_tabs_data:
            idx = self.tab_widget.indexOf(editor)
            tab_text = self.tab_widget.tabText(idx).strip().replace(' ●', '')
            is_dirty = hash(editor.get_text()) != self.editor_tabs_data[editor]['original_hash']
            display_text = f"{tab_text}{' ●' if is_dirty else ''}"
            if self.tab_widget.tabText(idx) != display_text:
                self.tab_widget.setTabText(idx, display_text)
            filepath = self.editor_tabs_data[editor].get('filepath')
            title_parts.insert(0, os.path.basename(filepath) if filepath else tab_text)

        self.setWindowTitle(" - ".join(title_parts))

    def _update_recent_files_menu(self):
        self.recent_files_menu.clear()
        if not (recent_files := self.settings.get("recent_files", [])):
            self.recent_files_menu.addAction(QAction("No Recent Files", self, enabled=False))
            return
        for fp in recent_files:
            action = QAction(os.path.basename(fp), self, triggered=self._action_open_recent_file)
            action.setData(fp)
            action.setToolTip(fp)
            self.recent_files_menu.addAction(action)

    def _trigger_file_linter(self):
        editor = self.tab_widget.currentWidget()
        if isinstance(editor, EditorWidget):
            if filepath := self.editor_tabs_data.get(editor, {}).get('filepath'):
                self.linter_manager.lint_file(filepath)

    def _action_open_recent_file(self):
        if isinstance(action := self.sender(), QAction):
            if filepath := action.data(): self._action_open_file(filepath)

    def _action_open_folder(self):
        if path := QFileDialog.getExistingDirectory(self, "Open Folder"):
            self.project_manager.open_project(path)
            self._initialize_project_views()

    def _action_close_project_by_index(self, index: int):
        if not (0 <= index < self.project_tabs.count()): return
        path = self.project_tabs.tabToolTip(index)
        self.project_manager.close_project(path)
        self._initialize_project_views()

    def _action_close_project(self):
        self._action_close_project_by_index(self.project_tabs.currentIndex())

    def _action_open_file_dialog(self):
        filepath, content, error = self.file_handler.open_file_dialog()
        if error:
            QMessageBox.critical(self, "Error Opening File", error)
        elif filepath:
            self._action_open_file(filepath, content)

    def _action_open_file(self, filepath: str, content: Optional[str] = None):
        norm_path = os.path.normpath(filepath)
        for i in range(self.tab_widget.count()):
            if isinstance(editor := self.tab_widget.widget(i), EditorWidget) and self.editor_tabs_data.get(editor,
                                                                                                           {}).get(
                    'filepath') == norm_path:
                self.tab_widget.setCurrentIndex(i)
                return

        if content is None:
            try:
                with open(norm_path, 'r', encoding='utf-8', errors='replace') as f:
                    content = f.read()
                self.file_handler._add_to_recent_files(norm_path)
            except Exception as e:
                QMessageBox.critical(self, "Error Opening File", f"Could not read file: {e}")
                return

        self._add_new_tab(norm_path, content)

    def _action_save_file(self, widget: Optional[EditorWidget] = None) -> bool:
        editor = widget or self.tab_widget.currentWidget()
        if not isinstance(editor, EditorWidget): return False
        if not (filepath := self.editor_tabs_data.get(editor, {}).get('filepath')):
            return self._action_save_as()
        if saved_path := self.file_handler.save_file_content(filepath, editor.get_text()):
            self._update_tab_info(editor, saved_path)
            return True
        return False

    def _action_save_as(self) -> bool:
        editor = self.tab_widget.currentWidget()
        if not isinstance(editor, EditorWidget): return False
        current_path = self.editor_tabs_data.get(editor, {}).get('filepath')
        if new_path := self.file_handler.save_file_content(current_path, editor.get_text(), save_as=True):
            self._update_tab_info(editor, new_path)
            return True
        return False

    def _action_save_all(self):
        for i in range(self.tab_widget.count()):
            if isinstance(e := self.tab_widget.widget(i), EditorWidget) and e in self.editor_tabs_data and hash(
                    e.get_text()) != self.editor_tabs_data[e]['original_hash']:
                if fp := self.editor_tabs_data[e].get('filepath'):
                    if self.file_handler.save_file_content(fp, e.get_text()):
                        self._update_tab_info(e, fp)
        self._update_window_title()

    def _action_close_tab_by_index(self, index: int):
        widget = self.tab_widget.widget(index)
        if not isinstance(widget, EditorWidget):
            self.tab_widget.removeTab(index)
            if self.tab_widget.count() == 0 and not self._is_app_closing:
                self._add_new_tab(is_placeholder=True)
            return

        if hash(widget.get_text()) != self.editor_tabs_data.get(widget, {})['original_hash']:
            reply = QMessageBox.question(self, "Unsaved Changes", f"Save '{self.tab_widget.tabText(index)}'?",
                                         QMessageBox.StandardButton.Save | QMessageBox.StandardButton.Discard | QMessageBox.StandardButton.Cancel)
            if reply == QMessageBox.StandardButton.Cancel: return
            if reply == QMessageBox.StandardButton.Save and not self._action_save_file(widget=widget): return

        self.editor_tabs_data.pop(widget, None)
        self.tab_widget.removeTab(index)
        if self.tab_widget.count() == 0 and not self._is_app_closing:
            self._add_new_tab(is_placeholder=True)

    def keyPressEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key.Key_Print:
            event.ignore()
            return
        super().keyPressEvent(event)

    def closeEvent(self, event):
        if self._is_app_closing:
            event.accept()
            return

        unsaved = [self.tab_widget.tabText(i) for i in range(self.tab_widget.count()) if
                   isinstance(e := self.tab_widget.widget(i), EditorWidget) and hash(e.get_text()) !=
                   self.editor_tabs_data[e]['original_hash']]

        if unsaved and QMessageBox.question(self, "Unsaved Changes", "You have unsaved changes. Save before exiting?",
                                            QMessageBox.StandardButton.SaveAll | QMessageBox.StandardButton.Discard | QMessageBox.StandardButton.Cancel) == QMessageBox.StandardButton.SaveAll:
            self._action_save_all()

        log.info("Starting graceful shutdown...")
        self._is_app_closing = True
        self.completion_manager.shutdown()
        self.git_manager.shutdown()
        self.github_manager.shutdown()
        self.linter_manager.shutdown()
        self.project_manager.save_session()
        self._save_window_geometry()
        self.settings.save()
        log.info("PuffinPyEditor closing clean.")
        event.accept()

    def _auto_save_current_tab(self):
        if isinstance(editor := self.tab_widget.currentWidget(), EditorWidget):
            if (filepath := self.editor_tabs_data[editor].get('filepath')) and hash(editor.get_text()) != \
                    self.editor_tabs_data[editor]['original_hash']:
                self.statusBar().showMessage(f"Auto-saving {os.path.basename(filepath)}...", 1500)
                self._action_save_file()

    def _update_tab_info(self, editor: EditorWidget, path: str):
        if not path: return
        norm_path = os.path.normpath(path)
        editor.set_filepath(norm_path)
        self.editor_tabs_data[editor].update({'filepath': norm_path, 'original_hash': hash(editor.get_text())})
        if (idx := self.tab_widget.indexOf(editor)) != -1:
            self.tab_widget.setTabText(idx, os.path.basename(norm_path))
            self.tab_widget.setTabToolTip(idx, norm_path)
        self.statusBar().showMessage(f"Saved: {norm_path}", 3000)
        self._update_window_title()
        self._trigger_file_linter()

    def _update_editor_actions_state(self):
        is_editor = isinstance(self.tab_widget.currentWidget(), EditorWidget)
        for key in ["save", "save_as", "save_all"]:
            self.actions[key].setEnabled(is_editor)

    def _on_editor_settings_changed(self):
        for i in range(self.tab_widget.count()):
            if isinstance(editor := self.tab_widget.widget(i), EditorWidget):
                editor.update_editor_settings()

    def _goto_definition_result(self, filepath: str, line: int, col: int):
        if not filepath:
            self.statusBar().showMessage("Definition not found", 3000)
            return

        norm_path = os.path.normpath(filepath)
        for i in range(self.tab_widget.count()):
            if isinstance(e := self.tab_widget.widget(i), EditorWidget) and self.editor_tabs_data.get(e, {}).get(
                    'filepath') == norm_path:
                self.tab_widget.setCurrentIndex(i)
                e.goto_line_and_column(line, col)
                return

        self._action_open_file(norm_path)
        QApplication.processEvents()  # Allow the new tab to be created
        if isinstance(e := self.tab_widget.currentWidget(), EditorWidget) and self.editor_tabs_data.get(e, {}).get(
                'filepath') == norm_path:
            e.goto_line_and_column(line, col)

    def _save_window_geometry(self):
        self.settings.set("window_size", [self.size().width(), self.size().height()], False)
        self.settings.set("window_position", [self.pos().x(), self.pos().y()], False)
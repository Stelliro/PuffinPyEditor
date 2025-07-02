# /ui/main_window.py
import os
import sys
from functools import partial
from typing import Optional
from PyQt6.QtGui import (QKeySequence, QAction, QCloseEvent, QDesktopServices, QIcon, QActionGroup)
from PyQt6.QtWidgets import (QMessageBox, QMenu, QWidget, QVBoxLayout, QHBoxLayout,
                             QMainWindow, QStatusBar, QTabWidget, QLabel, QToolButton,
                             QToolBar, QSizePolicy, QApplication, QFileDialog, QDockWidget)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer, QSize, QUrl

import qtawesome as qta
from utils.logger import log
from utils import versioning
from app_core.file_handler import FileHandler
from app_core.theme_manager import theme_manager
from app_core.settings_manager import settings_manager
from app_core.project_manager import ProjectManager
from app_core.linter_manager import LinterManager
from app_core.plugin_manager import PluginManager
from app_core.completion_manager import CompletionManager
from app_core.update_manager import UpdateManager
from app_core.source_control_manager import SourceControlManager
from app_core.github_manager import GitHubManager
from app_core.puffin_api import PuffinPluginAPI
from .editor_widget import EditorWidget
from .preferences_dialog import PreferencesDialog
from .widgets.syntax_highlighter import PythonSyntaxHighlighter
from plugins.tab_drag_handler.draggable_tab_widget import DraggableTabWidget


class MainWindow(QMainWindow):
    untitled_file_counter = 0
    _is_app_closing = False
    theme_changed_signal = pyqtSignal(str)

    def __init__(self, file_handler, theme_manager, debug_mode=False, parent=None):
        super().__init__(parent)
        self.file_handler = file_handler;
        self.file_handler.parent_window = self
        self.theme_manager = theme_manager;
        self.debug_mode = debug_mode
        self.preferences_dialog = None
        self._bottom_tab_widget: Optional[QTabWidget] = None
        self._bottom_dock_widget: Optional[QDockWidget] = None

        self._initialize_managers()
        self.puffin_api = PuffinPluginAPI(self)

        self.setWindowTitle(f"PuffinPyEditor - v{versioning.APP_VERSION}")
        self._load_window_geometry()
        self._create_core_widgets()
        self._create_core_actions()
        self._create_core_menu()
        self._create_toolbar()
        self._create_layout()
        self._create_statusbar()

        plugins_to_ignore = []
        if self.debug_mode:
            try:
                from core_debug_tools.enhanced_exceptions.plugin_main import initialize as init_eh
                self.eh_instance = init_eh(self.puffin_api, sys.excepthook)
                plugins_to_ignore.append('enhanced_exceptions')
            except Exception as e:
                log.error(f"Failed to load core exception handler: {e}", exc_info=True)

        self.plugin_manager = PluginManager(self)
        self.plugin_manager.discover_and_load_plugins(ignore_list=plugins_to_ignore)

        self._connect_signals()
        self._apply_theme_and_icons(self.settings.get("last_theme_id"))
        QTimer.singleShot(0, self._post_init_setup)
        log.info("MainWindow __init__ has completed.")

    def _initialize_managers(self):
        self.settings = settings_manager
        self.project_manager = ProjectManager()
        self.completion_manager = CompletionManager(self)
        self.github_manager = GitHubManager(self)
        self.git_manager = SourceControlManager(self)
        self.linter_manager = LinterManager(self)
        self.update_manager = UpdateManager(self)
        self.actions = {}
        self.editor_tabs_data = {}
        self.file_open_handlers = {}
        self.lint_timer = QTimer(self);
        self.lint_timer.setSingleShot(True);
        self.lint_timer.setInterval(1500)
        self.auto_save_timer = QTimer(self);
        self.auto_save_timer.setSingleShot(True)

    def _load_window_geometry(self):
        size, pos = self.settings.get("window_size", [1600, 1000]), self.settings.get("window_position")
        self.resize(QSize(size[0], size[1]));
        if pos: self.move(pos[0], pos[1])

    def _create_core_widgets(self):
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.tab_widget = DraggableTabWidget(self)
        button = QToolButton();
        button.setIcon(qta.icon('fa5s.plus'));
        button.setAutoRaise(True)
        button.clicked.connect(lambda: self._add_new_tab())
        self.tab_widget.setCornerWidget(button, Qt.Corner.TopRightCorner)
        self.tab_widget.setDocumentMode(True);
        self.tab_widget.setTabsClosable(True);
        self.tab_widget.setMovable(True)

    def _create_core_actions(self):
        actions_map = {
            "new_file": ("&New File", self._add_new_tab, "Ctrl+N", 'fa5s.file'),
            "open_file": ("&Open File...", self._action_open_file_dialog, "Ctrl+O", 'fa5s.folder-open'),
            "open_folder": ("Open &Folder...", self._action_open_folder, "Ctrl+Shift+O", 'fa5s.folder'),
            "close_project": ("&Close Project", self._action_close_project, None, None),
            "save": ("&Save", self._action_save_file, "Ctrl+S", 'fa5s.save'),
            "save_as": ("Save &As...", self._action_save_as, "Ctrl+Shift+S", None),
            "save_all": ("Save A&ll", self._action_save_all, "Ctrl+Alt+S", None),
            "preferences": ("&Preferences...", self._action_open_preferences, "Ctrl+,", 'fa5s.cog'),
            "exit": ("E&xit", self.close, "Ctrl+Q", None),
        }
        for key, (text, cb, sc, icon) in actions_map.items():
            action = QAction(text, self)
            if icon: action.setData(icon)
            if sc: action.setShortcut(QKeySequence(sc))
            action.triggered.connect(cb);
            self.actions[key] = action

    def _create_core_menu(self):
        mb = self.menuBar()
        self.file_menu, self.edit_menu, self.view_menu = mb.addMenu("&File"), mb.addMenu("&Edit"), mb.addMenu("&View")
        self.run_menu, self.tools_menu, self.help_menu = mb.addMenu("&Run"), mb.addMenu("&Tools"), mb.addMenu("&Help")

        self.file_menu.addActions([self.actions[k] for k in ["new_file", "open_file"]])
        self.recent_files_menu = self.file_menu.addMenu("Open &Recent")
        self.file_menu.addSeparator();
        self.file_menu.addActions([self.actions[k] for k in ["open_folder", "close_project"]])
        self.file_menu.addSeparator();
        self.file_menu.addActions([self.actions[k] for k in ["save", "save_as", "save_all"]])
        self.file_menu.addSeparator();
        self.file_menu.addAction(self.actions["preferences"]);
        self.file_menu.addSeparator()
        self.file_menu.addAction(self.actions["exit"])
        self.theme_menu = self.view_menu.addMenu("&Themes")
        self.help_menu.addAction("About PuffinPyEditor", self._show_about_dialog);
        self.help_menu.addAction("View on GitHub", self._open_github_link)

    def _create_toolbar(self):
        self.main_toolbar = QToolBar("Main Toolbar");
        self.main_toolbar.setIconSize(QSize(18, 18));
        self.addToolBar(self.main_toolbar)
        self.main_toolbar.addActions([self.actions[k] for k in ["new_file", "open_file", "save"]])
        spacer = QWidget();
        spacer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred);
        self.main_toolbar.addWidget(spacer)
        self.main_toolbar.addAction(self.actions["preferences"])

    def _create_layout(self):
        layout = QHBoxLayout(self.central_widget)
        layout.setContentsMargins(0, 0, 0, 0);
        layout.addWidget(self.tab_widget)

    def _create_statusbar(self):
        self.setStatusBar(QStatusBar(self));
        self.cursor_label = QLabel(" Ln 1, Col 1 ");
        self.statusBar().addPermanentWidget(self.cursor_label)

    def _connect_signals(self):
        self.tab_widget.currentChanged.connect(self._on_tab_changed)
        self.tab_widget.tabCloseRequested.connect(self._action_close_tab_by_index)
        self.lint_timer.timeout.connect(self._trigger_file_linter)
        self.completion_manager.definition_found.connect(self._goto_definition_result)
        self.auto_save_timer.timeout.connect(self._auto_save_current_tab)

    def _apply_theme_and_icons(self, theme_id: str):
        self.theme_manager.set_theme(theme_id, QApplication.instance());
        self.theme_changed_signal.emit(theme_id)
        for action in self.actions.values():
            if icon_name := action.data(): action.setIcon(qta.icon(icon_name))
        self._rebuild_theme_menu()
        for i in range(self.tab_widget.count()):
            if hasattr(widget := self.tab_widget.widget(i), 'update_theme'): widget.update_theme()
        if hasattr(self, 'project_manager'): self.project_manager.projects_changed.emit()

    def _rebuild_theme_menu(self):
        self.theme_menu.clear();
        group = QActionGroup(self);
        group.setExclusive(True)
        for theme_id, name in self.theme_manager.get_available_themes_for_ui().items():
            action = QAction(name, self, checkable=True,
                             triggered=lambda _, t_id=theme_id: self._on_theme_selected(t_id))
            action.setData(theme_id);
            action.setChecked(theme_id == self.theme_manager.current_theme_id)
            group.addAction(action);
            self.theme_menu.addAction(action)

    def _post_init_setup(self):
        self._update_recent_files_menu();
        self._update_window_title()
        if self.tab_widget.count() == 0: self._add_new_tab(is_placeholder=True)

    def add_dock_panel(self, panel_widget: QWidget, title: str, area: Qt.DockWidgetArea,
                       icon_name: Optional[str] = None):
        if area == Qt.DockWidgetArea.BottomDockWidgetArea:
            if self._bottom_tab_widget is None:
                log.info("Creating shared bottom dock area.");
                self._bottom_dock_widget = QDockWidget("Info Panels", self)
                self._bottom_dock_widget.setObjectName("SharedBottomDock");
                self._bottom_tab_widget = QTabWidget()
                self._bottom_tab_widget.setDocumentMode(True);
                self._bottom_dock_widget.setWidget(self._bottom_tab_widget)
                self.addDockWidget(area, self._bottom_dock_widget)
                if self.view_menu: self.view_menu.addSeparator(); self.view_menu.addAction(
                    self._bottom_dock_widget.toggleViewAction())
            icon = qta.icon(icon_name) if icon_name else QIcon();
            self._bottom_tab_widget.addTab(panel_widget, icon, title)
        else:
            dock = QDockWidget(title, self);
            dock.setWidget(panel_widget)
            if icon_name: dock.setWindowIcon(qta.icon(icon_name))
            self.addDockWidget(area, dock)
            if self.view_menu: self.view_menu.addSeparator(); self.view_menu.addAction(dock.toggleViewAction())

    def _add_new_tab(self, filepath=None, content="", is_placeholder=False):
        if not is_placeholder and self.tab_widget.count() == 1 and isinstance(self.tab_widget.widget(0), QLabel):
            self.tab_widget.removeTab(0)

        if is_placeholder:
            placeholder = QLabel("Open a file...", alignment=Qt.AlignmentFlag.AlignCenter);
            placeholder.setObjectName("PlaceholderLabel")
            self.tab_widget.addTab(placeholder, "Welcome");
            self.tab_widget.setTabsClosable(False);
            return

        try:
            self.tab_widget.setTabsClosable(True);
            editor = EditorWidget(self.completion_manager, self)
            ext = os.path.splitext(filepath or "")[1].lower()
            highlighter = self.puffin_api.highlighter_map.get(ext) or (
                PythonSyntaxHighlighter if ext == '.py' else None)
            editor.set_highlighter(highlighter);
            editor.set_filepath(filepath);
            editor.set_text(content)
            editor.cursor_position_display_updated.connect(lambda l, c: self.cursor_label.setText(f" Ln {l+1}, Col {c} "))
            editor.content_possibly_changed.connect(partial(self._on_content_changed, editor))
            # I'm connecting the new signal from the editor to the status bar here.
            editor.status_message_requested.connect(self.statusBar().showMessage)

            if filepath:
                name = os.path.basename(filepath)
            else:
                self.untitled_file_counter += 1
                name = f"Untitled-{self.untitled_file_counter}"
            index = self.tab_widget.addTab(editor, name);
            self.tab_widget.setTabToolTip(index, filepath or f"Unsaved {name}")
            self.editor_tabs_data[editor] = {'filepath': filepath, 'original_hash': hash(content)}
            self.tab_widget.setCurrentWidget(editor);
            editor.text_area.setFocus()
        except Exception as e:
            log.critical(f"CRASH during _add_new_tab: {e}", exc_info=True)
            QMessageBox.critical(self, "Fatal Error", f"Could not create editor tab:\n\n{e}")

    def _action_open_file(self, filepath: Optional[str] = None, content: Optional[str] = None):
        if not (isinstance(filepath, str) and filepath): return
        norm_path = os.path.normpath(filepath)
        for i in range(self.tab_widget.count()):
            widget = self.tab_widget.widget(i)
            if isinstance(widget, EditorWidget) and self.editor_tabs_data.get(widget, {}).get('filepath') == norm_path:
                self.tab_widget.setCurrentIndex(i);
                return

        if handler := self.file_open_handlers.get(os.path.splitext(norm_path)[1].lower()):
            handler(norm_path);
            self.file_handler._add_to_recent_files(norm_path);
            return
        if content is None:
            try:
                with open(norm_path, 'r', encoding='utf-8', errors='replace') as f:
                    content = f.read()
            except Exception as e:
                self.puffin_api.show_message("critical", "Error Opening File", f"Could not read file: {e}"); return
        self._add_new_tab(norm_path, content);
        self.file_handler._add_to_recent_files(norm_path)

    def _action_open_file_dialog(self):
        filepath, content, error = self.file_handler.open_file_dialog()
        if error:
            QMessageBox.critical(self, "Error Opening File", error)
        elif filepath:
            self._action_open_file(filepath, content)

    def _action_open_folder(self, path: Optional[str] = None):
        if not path or not isinstance(path, str):
            path = QFileDialog.getExistingDirectory(self, "Open Folder",
                                                    self.project_manager.get_active_project_path() or os.path.expanduser(
                                                        "~"))
        if path: self.project_manager.open_project(path); self.project_manager.projects_changed.emit()

    def _action_close_project(self, path: Optional[str] = None):
        if path_to_close := path if isinstance(path, str) else self.project_manager.get_active_project_path():
            self.project_manager.close_project(path_to_close);
            self.project_manager.projects_changed.emit()
        else:
            self.statusBar().showMessage("No active project to close.", 2000)

    def _on_theme_selected(self, theme_id):
        self.settings.set("last_theme_id", theme_id);
        self._apply_theme_and_icons(theme_id)

    def _on_tab_changed(self, index):
        self._update_window_title()
        widget = self.tab_widget.widget(index) if index != -1 else None
        if isinstance(widget, EditorWidget):
            line, col = widget.get_cursor_position()
            self.cursor_label.setText(f" Ln {line + 1}, Col {col + 1} ")
        else:
            self.cursor_label.setText("")

    def _is_editor_modified(self, editor: QWidget) -> bool:
        return isinstance(editor, EditorWidget) and (data := self.editor_tabs_data.get(editor)) and hash(
            editor.get_text()) != data['original_hash']

    def _on_content_changed(self, editor: EditorWidget):
        if not (isinstance(editor, EditorWidget) and self.tab_widget.isAncestorOf(editor)): return
        is_modified, index = self._is_editor_modified(editor), self.tab_widget.indexOf(editor)
        if index != -1:
            current_text = self.tab_widget.tabText(index)
            has_asterisk = current_text.endswith(' *')
            if is_modified and not has_asterisk:
                self.tab_widget.setTabText(index, current_text + ' *')
            elif not is_modified and has_asterisk:
                self.tab_widget.setTabText(index, current_text[:-2])
        self._update_window_title()
        if self.settings.get("auto_save_enabled", False): self.auto_save_timer.start(
            self.settings.get("auto_save_delay_seconds", 3) * 1000)

    def _update_window_title(self):
        base_title, project_name = "PuffinPyEditor", os.path.basename(
            self.project_manager.get_active_project_path()) if self.project_manager.is_project_open() else ""
        current_file = "";
        current_widget = self.tab_widget.currentWidget()
        if isinstance(current_widget, EditorWidget):
            filepath = self.editor_tabs_data.get(current_widget, {}).get('filepath')
            current_file = os.path.basename(filepath) if filepath else self.tab_widget.tabText(
                self.tab_widget.currentIndex()).replace(" *", "")
            if self._is_editor_modified(current_widget): current_file += " *"
        self.setWindowTitle(" - ".join(filter(None, [current_file, project_name, base_title])))

    def _action_save_file(self, editor_widget=None, save_as=False):
        current_editor = editor_widget or self.tab_widget.currentWidget()
        if not isinstance(current_editor, EditorWidget): return None
        if not (editor_data := self.editor_tabs_data.get(current_editor)): return None
        content = current_editor.get_text()
        if not self._is_editor_modified(current_editor) and not save_as and editor_data['filepath']:
            self.statusBar().showMessage("File is already saved.", 2000);
            return editor_data['filepath']
        if (filepath := self.file_handler.save_file_content(editor_data['filepath'], content, save_as)):
            editor_data.update({'filepath': filepath, 'original_hash': hash(content)});
            current_editor.set_filepath(filepath)
            if (index := self.tab_widget.indexOf(current_editor)) != -1:
                self.tab_widget.setTabText(index, os.path.basename(filepath));
                self.tab_widget.setTabToolTip(index, filepath)
            self.statusBar().showMessage(f"File saved: {os.path.basename(filepath)}", 3000)
            self._on_content_changed(current_editor);
            self.file_handler._add_to_recent_files(filepath);
            return filepath
        self.statusBar().showMessage("Save cancelled.", 2000);
        return None

    def _action_save_as(self):
        self._action_save_file(save_as=True)

    def _action_save_all(self):
        if count := sum(1 for i in range(self.tab_widget.count()) if
                        self._is_editor_modified(w := self.tab_widget.widget(i)) and self._action_save_file(w)):
            self.statusBar().showMessage(f"Saved {count} file(s).", 3000)

    def _action_close_tab_by_index(self, index):
        self._close_widget_safely(self.tab_widget.widget(index), QCloseEvent())

    def _close_widget_safely(self, widget, event):
        if not isinstance(widget, EditorWidget):
            if widget.parent() is None: widget.deleteLater()
            event.accept();
            return
        if self._is_editor_modified(widget):
            filename = self.tab_widget.tabText(self.tab_widget.indexOf(widget)).replace(" *", "")
            ret = QMessageBox.question(self, "Save Changes?", f"Save changes to {filename}?",
                                       QMessageBox.StandardButton.Save | QMessageBox.StandardButton.Discard | QMessageBox.StandardButton.Cancel)
            if ret == QMessageBox.StandardButton.Cancel or (
                    ret == QMessageBox.StandardButton.Save and not self._action_save_file(widget)):
                event.ignore();
                return
        if widget in self.editor_tabs_data: del self.editor_tabs_data[widget]
        event.accept()

    def _update_recent_files_menu(self):
        self.recent_files_menu.clear();
        recent_files = self.settings.get("recent_files", [])
        self.recent_files_menu.setEnabled(bool(recent_files))
        for i, filepath in enumerate(recent_files[:10]):
            action = QAction(f"&{i + 1} {os.path.basename(filepath)}", self)
            action.setData(filepath)
            action.setToolTip(filepath)
            action.triggered.connect(self._action_open_recent_file)
            self.recent_files_menu.addAction(action)

    def _action_open_recent_file(self):
        if action := self.sender(): self._action_open_file(action.data())

    def _trigger_file_linter(self):
        pass

    def _show_about_dialog(self):
        QMessageBox.about(self, "About", f"PuffinPyEditor v{versioning.APP_VERSION}")

    def _open_github_link(self):
        QDesktopServices.openUrl(QUrl("https://github.com/Stelliro/PuffinPyEditor"))

    def _auto_save_current_tab(self):
        if self._is_editor_modified(editor := self.tab_widget.currentWidget()): self._action_save_file(
            editor_widget=editor)

    def _on_editor_settings_changed(self):
        for i in range(self.tab_widget.count()):
            if isinstance(widget := self.tab_widget.widget(i), EditorWidget): widget.update_editor_settings()

    def _action_open_preferences(self):
        if not self.preferences_dialog or not self.preferences_dialog.isVisible():
            self.preferences_dialog = PreferencesDialog(self.git_manager, self.github_manager, self.plugin_manager,
                                                        self.puffin_api, self)
            self.preferences_dialog.settings_changed_for_editor_refresh.connect(self._on_editor_settings_changed)
            self.preferences_dialog.theme_changed_signal.connect(self._on_theme_selected)
        self.preferences_dialog.show();
        self.preferences_dialog.raise_();
        self.preferences_dialog.activateWindow()

    def _goto_definition_result(self, filepath, line, col):
        if not filepath: self.statusBar().showMessage("Definition not found", 3000); return
        norm_path = os.path.normpath(filepath)
        for i in range(self.tab_widget.count()):
            if isinstance(e := self.tab_widget.widget(i), EditorWidget) and self.editor_tabs_data.get(e, {}).get(
                    'filepath') == norm_path:
                self.tab_widget.setCurrentIndex(i);
                e.goto_line_and_column(line, col);
                return
        self._action_open_file(norm_path);
        QApplication.processEvents()
        if isinstance(e := self.tab_widget.currentWidget(), EditorWidget) and self.editor_tabs_data.get(e, {}).get(
                'filepath') == norm_path:
            e.goto_line_and_column(line, col)

    def _shutdown_managers(self):
        log.info("Shutting down core managers...")
        for manager in [self.completion_manager, self.github_manager, self.git_manager, self.linter_manager]:
            if hasattr(manager, 'shutdown'): manager.shutdown()

    def closeEvent(self, event: QCloseEvent):
        if self._is_app_closing: event.accept(); return
        self._is_app_closing = True

        while self.tab_widget.count() > 0:
            dummy_event = QCloseEvent();
            self._close_widget_safely(self.tab_widget.widget(0), dummy_event)
            if not dummy_event.isAccepted(): self._is_app_closing = False; event.ignore(); return
            if (index := self.tab_widget.indexOf(self.tab_widget.widget(0))) != -1: self.tab_widget.removeTab(index)

        self.settings.set("window_size", [self.size().width(), self.size().height()], False)
        self.settings.set("window_position", [self.pos().x(), self.pos().y()], False)
        self.project_manager.save_session();
        self.settings.save()
        self._shutdown_managers()
        log.info("PuffinPyEditor exited cleanly.")
        event.accept()
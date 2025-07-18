# /ui/main_window.py
import os, sys, re
from functools import partial
from typing import Optional
from PyQt6.QtGui import (QKeySequence, QAction, QCloseEvent, QDesktopServices, QIcon, QActionGroup, QDragEnterEvent,
                         QDropEvent)
from PyQt6.QtWidgets import (QMessageBox, QMenu, QWidget, QVBoxLayout, QHBoxLayout, QMainWindow, QStatusBar, QTabWidget, \
                             QLabel, QToolButton, QToolBar, QSizePolicy, QApplication, QFileDialog, QDockWidget, QComboBox)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer, QSize, QUrl, QEvent

import qtawesome as qta
from utils.logger import log
from utils import versioning, helpers
from app_core.file_handler import FileHandler
from app_core.settings_manager import settings_manager
from app_core.project_manager import ProjectManager
from app_core.linter_manager import LinterManager
from app_core.plugin_manager import PluginManager
from app_core.completion_manager import CompletionManager
from app_core.update_manager import UpdateManager
from app_core.source_control_manager import SourceControlManager
from app_core.github_manager import GitHubManager
from app_core.puffin_api import PuffinPluginAPI
from .preferences_dialog import PreferencesDialog
from .widgets.draggable_tab_widget import DraggableTabWidget
from .explorer.list_view_widget import FileSystemListView
from .widgets.problems_panel import ProblemsPanel
from .widgets.source_control_panel import ProjectSourceControlPanel
from .editor_widget import EditorWidget, HighlightManager
from app_core.syntax_highlighters import (
    PythonSyntaxHighlighter, JsonSyntaxHighlighter, HtmlSyntaxHighlighter,
    CssSyntaxHighlighter, CppSyntaxHighlighter, CSharpSyntaxHighlighter, JavaScriptSyntaxHighlighter,
    RustSyntaxHighlighter
)


class MainWindow(QMainWindow):
    untitled_file_counter, _is_app_closing = 0, False
    theme_changed_signal = pyqtSignal(str)
    COMMENT_MAP = {'.py': '#', '.js': '//', '.ts': '//', '.cs': '//', '.java': '//', '.go': '//', '.rs': '//',
                   '.c': '//', '.cpp': '//', '.h': '//', '.hpp': '//', '.css': '/*', '.html': '<!--'}
    END_COMMENT_MAP = {'/*': '*/', '<!--': '-->'}

    def __init__(self, file_handler, theme_manager, debug_mode=False, parent=None):
        super().__init__(parent)
        self.file_handler, self.theme_manager, self.debug_mode = file_handler, theme_manager, debug_mode
        self.file_handler.parent_window = self
        self.preferences_dialog, self._bottom_tab_widget, self._bottom_dock_widget = None, None, None

        self._initialize_managers()
        self.puffin_api = PuffinPluginAPI(self)
        self.puffin_api.highlight_manager = self.highlight_manager

        # --- NEW: Encoding Map for the UI ---
        self.encoding_map = {
            "UTF-8": "utf-8",
            "UTF-8-SIG": "utf-8-sig",
            "UTF-16 LE": "utf-16le",
            "UTF-16 BE": "utf-16be",
            "Latin-1": "latin-1",
            "Windows-1252": "cp1252"
        }
        self.reverse_encoding_map = {v: k for k, v in self.encoding_map.items()}

        self._register_built_in_highlighters()

        self.plugin_manager = PluginManager(self)
        self.setWindowTitle(f"PuffinPyEditor - v{versioning.APP_VERSION}")
        self._load_window_geometry()

        self._create_core_widgets()
        self._create_core_actions()
        self._create_core_menu()
        self._create_toolbar()
        self._create_layout()
        self._create_statusbar()
        self._integrate_file_explorer()
        self._integrate_linter_ui()
        self._integrate_source_control_ui()
        self._integrate_global_drag_drop()

        if self.explorer_panel:
            self.project_manager.projects_changed.connect(self.explorer_panel.refresh)
            self.explorer_panel.tree_widget.currentItemChanged.connect(self._on_active_project_changed)
        if self.source_control_panel:
            self.theme_changed_signal.connect(self.source_control_panel.update_icons)
            self.git_manager.git_success.connect(self.source_control_panel.refresh_all_projects)
            self.github_manager.operation_success.connect(self.source_control_panel.refresh_all_projects)
            if self.explorer_panel:
                self.explorer_panel.tree_widget.currentItemChanged.connect(
                    self.source_control_panel.refresh_all_projects)

        plugins_to_ignore = []
        if self.debug_mode:
            try:
                from core_debug_tools.enhanced_exceptions.plugin_main import initialize as init_eh
                self.eh_instance = init_eh(self.puffin_api, sys.excepthook)
                plugins_to_ignore.append('enhanced_exceptions')
            except Exception as e:
                log.error(f"Failed to load core exception handler: {e}", exc_info=True)

        self.plugin_manager.discover_and_load_plugins(ignore_list=plugins_to_ignore)
        self._connect_signals()
        self._apply_theme_and_icons(self.settings.get("last_theme_id"))
        QTimer.singleShot(0, self._post_init_setup)
        log.info("MainWindow __init__ has completed.")

    def _register_built_in_highlighters(self):
        """
        Directly registers core syntax highlighters with the PuffinAPI.
        This ensures essential features are always available without relying on the plugin system.
        """
        log.info("Registering built-in syntax highlighters...")
        built_in_map = {
            '.py': PythonSyntaxHighlighter,
            '.pyw': PythonSyntaxHighlighter,
            '.json': JsonSyntaxHighlighter,
            '.html': HtmlSyntaxHighlighter,
            '.css': CssSyntaxHighlighter,
            '.js': JavaScriptSyntaxHighlighter,
            '.rs': RustSyntaxHighlighter,
            '.c': CppSyntaxHighlighter,
            '.cpp': CppSyntaxHighlighter,
            '.h': CppSyntaxHighlighter,
            '.hpp': CppSyntaxHighlighter,
            '.cs': CSharpSyntaxHighlighter,
        }
        for ext, highlighter_class in built_in_map.items():
            if highlighter_class:
                self.puffin_api.register_highlighter(ext, highlighter_class)
        log.info("Built-in highlighters registered.")

    def _initialize_managers(self):
        self.settings = settings_manager
        self.project_manager = ProjectManager()
        self.highlight_manager = HighlightManager()
        self.completion_manager = CompletionManager(self.theme_manager, self)
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
        # --- NEW: Timer for saving drafts ---
        self.draft_save_timer = QTimer(self)
        self.draft_save_timer.setSingleShot(True)
        self.draft_save_timer.setInterval(2000) # Save draft 2s after user stops typing

    def _add_new_tab(self, filepath=None, content="", encoding='utf-8', is_placeholder=False):
        if not is_placeholder and self.tab_widget.count() == 1 and isinstance(self.tab_widget.widget(0), QLabel):
            self.tab_widget.removeTab(0)
        if is_placeholder:
            placeholder = QLabel("Open a file or project...", alignment=Qt.AlignmentFlag.AlignCenter)
            placeholder.setObjectName("PlaceholderLabel")
            self.tab_widget.addTab(placeholder, "Welcome")
            self.tab_widget.setTabsClosable(False)
            return
        try:
            self.tab_widget.setTabsClosable(True)
            editor = EditorWidget(self.puffin_api, self.completion_manager, self.highlight_manager, self.theme_manager, self)
            if hc := self.puffin_api.highlighter_map.get(os.path.splitext(filepath or "")[1].lower()):
                editor.set_highlighter(hc)
            editor.set_filepath(filepath);
            editor.set_text(content)
            editor.cursor_position_display_updated.connect(lambda l, c: self.cursor_label.setText(f" Ln {l}, Col {c} "))
            editor.content_possibly_changed.connect(partial(self._on_content_changed, editor))
            editor.status_message_requested.connect(self.statusBar().showMessage)
            name = os.path.basename(filepath or f"Untitled-{self.untitled_file_counter + 1}")
            if not filepath: self.untitled_file_counter += 1
            idx = self.tab_widget.addTab(editor, name)
            self.tab_widget.setTabToolTip(idx, filepath or f"Unsaved {name}")
            self.editor_tabs_data[editor] = {'filepath': filepath, 'original_hash': hash(content), 'encoding': encoding}
            self.tab_widget.setCurrentWidget(editor)
            editor.text_area.setFocus()
        except Exception as e:
            log.critical(f"CRASH during _add_new_tab: {e}", exc_info=True)
            QMessageBox.critical(self, "Fatal Error", f"Could not create editor tab:\n\n{e}")

    def _post_init_setup(self):
        self._update_recent_files_menu()
        self._update_window_title()
        if open_files := settings_manager.get("open_files", []):
            log.info(f"Restoring {len(open_files)} open files from last session.")
            for filepath in open_files:
                if os.path.exists(filepath):
                    self._action_open_file(filepath)
                else:
                    log.warning(f"Could not restore non-existent file: {filepath}")
        if self.tab_widget.count() == 0:
            self._add_new_tab(is_placeholder=True)

    def _on_file_renamed(self, old_path, new_path):
        norm_old_path = os.path.normpath(old_path)
        for i in range(self.tab_widget.count()):
            widget = self.tab_widget.widget(i)
            if isinstance(widget, EditorWidget) and (data := self.editor_tabs_data.get(widget)) and data.get(
                    'filepath') == norm_old_path:
                data['filepath'] = new_path
                index = self.tab_widget.indexOf(widget)
                if index != -1:
                    self.tab_widget.setTabText(index, os.path.basename(new_path))
                    self.tab_widget.setTabToolTip(index, new_path)
                    data['original_hash'] = hash(widget.get_text())
                    self._on_content_changed(widget)
                break

    def _integrate_file_explorer(self):
        self.explorer_panel = FileSystemListView(self.puffin_api)
        dock = QDockWidget("Explorer", self)
        dock.setWidget(self.explorer_panel)
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, dock)
        self.view_menu.addSeparator()
        self.view_menu.addAction(dock.toggleViewAction())
        # The connection is now done in __init__ after project_manager is created
        QTimer.singleShot(100, self.explorer_panel.refresh)

    def _integrate_linter_ui(self):
        self.problems_panel = ProblemsPanel(self)
        self.add_dock_panel(self.problems_panel, "Problems", "bottom", "mdi.bug-outline")
        self.linter_manager.lint_results_ready.connect(self._update_problems_panel)
        self.linter_manager.error_occurred.connect(
            lambda err: self.problems_panel.show_info_message(f"Linter Error: {err}"))
        self.problems_panel.problem_selected.connect(self._goto_definition_result)

    def _integrate_source_control_ui(self):
        self.source_control_panel = ProjectSourceControlPanel(
            self.project_manager, self.git_manager, self.github_manager, self.puffin_api, self
        )
        self.add_dock_panel(self.source_control_panel, "Source Control", "bottom",
                            "mdi.git")

    def _integrate_global_drag_drop(self):
        self.setAcceptDrops(True)

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent):
        if event.mimeData().hasUrls():
            for url in event.mimeData().urls():
                if url.isLocalFile():
                    self._action_open_file(url.toLocalFile())
            event.acceptProposedAction()

    def _update_problems_panel(self, problems):
        if isinstance(editor := self.tab_widget.currentWidget(), EditorWidget) and (
                fp := self.editor_tabs_data.get(editor, {}).get('filepath')):
            self.problems_panel.update_problems({fp: problems})

    def _load_window_geometry(self):
        size = self.settings.get("window_size", [1600, 1000])
        pos = self.settings.get("window_position")
        self.resize(QSize(size[0], size[1]))
        if pos:
            self.move(pos[0], pos[1])

    def _create_core_widgets(self):
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.tab_widget = DraggableTabWidget(self)
        self.tab_widget.setObjectName("MainTabWidget")
        btn = QToolButton()
        btn.setIcon(qta.icon('mdi.plus'))
        btn.setAutoRaise(True)
        btn.clicked.connect(self._add_new_tab)
        self.tab_widget.setCornerWidget(btn, Qt.Corner.TopRightCorner)
        self.tab_widget.setDocumentMode(True)
        self.tab_widget.setTabsClosable(True)
        self.tab_widget.setMovable(True)

    def _create_core_actions(self):
        actions_map = {
            "new_file": ("&New File", self._add_new_tab, "Ctrl+N", 'mdi.file-outline'),
            "open_file": ("&Open File...", self._action_open_file_dialog, "Ctrl+O", 'mdi.folder-open-outline'),
            "open_folder": ("Open &Folder...", self._action_open_folder, "Ctrl+Shift+O", 'mdi.folder-outline'),
            "close_project": ("&Close Project", self._action_close_project, None, None),
            "save": ("&Save", self._action_save_file, "Ctrl+S", 'mdi.content-save-outline'),
            "save_as": ("Save &As...", self._action_save_as, "Ctrl+Shift+S", None),
            "save_all": ("Save A&ll", self._action_save_all, "Ctrl+Alt+S", None),
            "find_replace": ("&Find/Replace...", self.toggle_find_panel, "Ctrl+F", "mdi.magnify"),
            "preferences": ("&Preferences...", self._action_open_preferences, "Ctrl+,", 'mdi.cog-outline'),
            "exit": ("E&xit", self.close, "Ctrl+Q", None),
            "force_quit": ("&Force Quit", self._action_force_quit, "Ctrl+Shift+Q", 'mdi.alert-outline')
        }
        for key, props in actions_map.items():
            text, callback = props[0], props[1]
            shortcut = props[2] if len(props) > 2 else None
            icon = props[3] if len(props) > 3 else None

            action = QAction(text, self)
            action.triggered.connect(callback)
            if icon:
                action.setData(icon)
            if shortcut:
                action.setShortcut(QKeySequence(shortcut))
            self.actions[key] = action

        self.actions["find_replace"].setEnabled(False)

    def _create_core_menu(self):
        mb = self.menuBar();
        self.file_menu, self.edit_menu, self.view_menu, self.run_menu, self.tools_menu, self.help_menu = mb.addMenu(
            "&File"), mb.addMenu("&Edit"), mb.addMenu("&View"), mb.addMenu("&Run"), mb.addMenu("&Tools"), mb.addMenu(
            "&Help")
        self.file_menu.addActions([self.actions[k] for k in ["new_file", "open_file"]]);
        self.recent_files_menu = self.file_menu.addMenu("Open &Recent");
        self.file_menu.addSeparator()
        self.file_menu.addActions([self.actions[k] for k in ["open_folder", "close_project"]]);
        self.file_menu.addSeparator();
        self.file_menu.addActions([self.actions[k] for k in ["save", "save_as", "save_all"]]);
        self.file_menu.addSeparator()
        self.file_menu.addAction(self.actions["preferences"]);
        self.file_menu.addSeparator();
        self.file_menu.addActions([self.actions["exit"], self.actions["force_quit"]])
        self.edit_menu.addAction(self.actions["find_replace"]);
        self.theme_menu = self.view_menu.addMenu("&Themes");
        self.help_menu.addAction("About PuffinPyEditor", self._show_about_dialog);
        self.help_menu.addAction("View on GitHub", self._open_github_link)

    def _create_toolbar(self):
        tb = QToolBar("Main Toolbar");
        tb.setIconSize(QSize(18, 18));
        self.addToolBar(tb);
        self.main_toolbar = tb
        tb.addActions([self.actions[k] for k in ["new_file", "open_file", "save"]])
        tb.addSeparator()

        sp = QWidget();
        sp.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred);
        tb.addWidget(sp);
        
        # --- NEW Encoding Dropdown ---
        self.encoding_toolbar_label = QLabel(" Encoding: ")
        self.encoding_combo = QComboBox()
        self.encoding_combo.setToolTip("Change file encoding and re-save")
        for display_name, actual_name in self.encoding_map.items():
            self.encoding_combo.addItem(display_name, actual_name)
        
        tb.addWidget(self.encoding_toolbar_label)
        tb.addWidget(self.encoding_combo)
        tb.addSeparator()

        tb.addAction(self.actions["find_replace"])
        tb.addAction(self.actions["preferences"])

    def _create_layout(self):
        lay = QHBoxLayout(self.central_widget);
        lay.setContentsMargins(0, 0, 0, 0);
        lay.addWidget(self.tab_widget)

    def _create_statusbar(self):
        self.setStatusBar(QStatusBar(self))
        self.encoding_label = QLabel(" UTF-8 ")
        self.cursor_label = QLabel(" Ln 1, Col 1 ")
        self.statusBar().addPermanentWidget(self.encoding_label)
        self.statusBar().addPermanentWidget(self.cursor_label)

    def _connect_signals(self):
        self.tab_widget.currentChanged.connect(self._on_tab_changed);
        self.tab_widget.tabCloseRequested.connect(self._action_close_tab_by_index);
        self.lint_timer.timeout.connect(self._trigger_file_linter);
        self.completion_manager.definition_found.connect(self._goto_definition_result);
        self.auto_save_timer.timeout.connect(self._auto_save_current_tab)
        self.file_handler.recent_files_changed.connect(self._update_recent_files_menu)
        self.encoding_combo.activated.connect(self._on_encoding_changed_from_dropdown)
        # --- NEW: Connect draft save timer ---
        self.draft_save_timer.timeout.connect(self._save_current_draft)

    def _apply_theme_and_icons(self, theme_id):
        self.theme_manager.set_theme(theme_id, QApplication.instance());
        self.theme_changed_signal.emit(theme_id)
        for act in self.actions.values():
            if ico := act.data(): act.setIcon(qta.icon(ico))
        self._rebuild_theme_menu();
        [w.update_theme() for i in range(self.tab_widget.count()) if
         hasattr(w := self.tab_widget.widget(i), 'update_theme')]
        if hasattr(self, 'explorer_panel'): self.explorer_panel.refresh()

    def _rebuild_theme_menu(self):
        self.theme_menu.clear();
        group = QActionGroup(self);
        group.setExclusive(True)
        for t_id, name in self.theme_manager.get_available_themes_for_ui().items():
            act = QAction(name, self, checkable=True, triggered=lambda _, tid=t_id: self._on_theme_selected(tid));
            act.setData(t_id);
            act.setChecked(t_id == self.theme_manager.current_theme_id);
            group.addAction(act);
            self.theme_menu.addAction(act)

    def add_dock_panel(self, panel, title, area_str: str, icon_name=None):
        area_map = {
            "left": Qt.DockWidgetArea.LeftDockWidgetArea,
            "right": Qt.DockWidgetArea.RightDockWidgetArea,
            "top": Qt.DockWidgetArea.TopDockWidgetArea,
            "bottom": Qt.DockWidgetArea.BottomDockWidgetArea,
        }
        area = area_map.get(area_str.lower(), Qt.DockWidgetArea.BottomDockWidgetArea)

        if area == Qt.DockWidgetArea.BottomDockWidgetArea:
            if not self._bottom_tab_widget:
                self._bottom_dock_widget = QDockWidget("Info Panels", self)
                self._bottom_dock_widget.setObjectName("SharedBottomDock")
                self._bottom_tab_widget = QTabWidget()
                self._bottom_tab_widget.setObjectName("InfoPanelTabBar")
                self._bottom_tab_widget.setDocumentMode(True)
                self._bottom_dock_widget.setWidget(self._bottom_tab_widget)
                self.addDockWidget(area, self._bottom_dock_widget)
                if self.view_menu:
                    self.view_menu.addSeparator()
                    self.view_menu.addAction(self._bottom_dock_widget.toggleViewAction())

            icon = qta.icon(icon_name) if icon_name else QIcon()
            self._bottom_tab_widget.addTab(panel, icon, title)
            return self._bottom_dock_widget

        dock = QDockWidget(title, self);
        dock.setWidget(panel)
        if icon_name: dock.setWindowIcon(qta.icon(icon_name))
        self.addDockWidget(area, dock)
        if self.view_menu:
            self.view_menu.addSeparator()
            self.view_menu.addAction(dock.toggleViewAction())
        return dock

    def _action_open_file(self, fp=None, content=None, encoding=None):
        if not (isinstance(fp, str) and fp): return
        np = os.path.normpath(fp)
        for i in range(self.tab_widget.count()):
            if isinstance(w := self.tab_widget.widget(i), EditorWidget) and self.editor_tabs_data.get(w, {}).get(
                    'filepath') == np: self.tab_widget.setCurrentIndex(i); return
        if h := self.file_open_handlers.get(os.path.splitext(np)[1].lower()): h(
            np); self.file_handler._add_to_recent_files(np); return
        
        # --- MODIFIED: Draft Checking Logic ---
        draft_path = helpers.get_draft_path(np)
        use_draft = False
        if os.path.exists(draft_path) and os.path.getmtime(draft_path) > os.path.getmtime(np):
            reply = QMessageBox.question(
                self, "Unsaved Changes Found",
                f"It looks like you have unsaved changes for '{os.path.basename(np)}' from a previous session.\n\n"
                "Do you want to restore them?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.Yes
            )
            if reply == QMessageBox.StandardButton.Yes:
                use_draft = True
            else:
                # User chose not to restore, so we delete the draft
                os.remove(draft_path)

        if use_draft:
            log.info(f"Restoring unsaved changes from draft for: {np}")
            content, encoding = self.file_handler._read_with_encoding_detection(draft_path)
            if content is None:
                QMessageBox.warning(self, "Draft Read Error", "Could not read the draft file. Opening original.")
                content, encoding = self.file_handler._read_with_encoding_detection(np)
        elif content is None:
            content, encoding = self.file_handler._read_with_encoding_detection(np)

        if content is None:
            self.puffin_api.show_message("critical", "Error Opening File", f"Could not read file: {np}")
            return
        
        self._add_new_tab(np, content, encoding or 'utf-8')
        self.file_handler._add_to_recent_files(np)

    def _action_open_file_dialog(self):
        fp, content, encoding, err = self.file_handler.open_file_dialog()
        if err:
            QMessageBox.critical(self, "Error Opening File", err)
        elif fp:
            self._action_open_file(fp, content, encoding)

    def _action_open_folder(self, path=None):
        if not path or not isinstance(path, str): path = QFileDialog.getExistingDirectory(self, "Open Folder",
                                                                                          self.project_manager.get_active_project_path() or os.path.expanduser(
                                                                                              "~"))
        if path: self.project_manager.open_project(path)

    def _action_close_project(self, path=None):
        if path := path if isinstance(path, str) else self.project_manager.get_active_project_path():
            self.project_manager.close_project(path)
        else:
            self.statusBar().showMessage("No active project to close.", 2000)

    def _on_theme_selected(self, theme_id):
        self.settings.set("last_theme_id", theme_id);
        self._apply_theme_and_icons(theme_id)

    def _on_tab_changed(self, index):
        self._update_window_title()
        widget = self.tab_widget.widget(index) if index != -1 else None
        is_editor = False
        
        # --- UPDATED: Auto-detect and update encoding dropdown ---
        self.encoding_combo.blockSignals(True)
        if isinstance(widget, EditorWidget):
            is_editor, (line, col) = True, widget.get_cursor_position()
            self.cursor_label.setText(f" Ln {line}, Col {col} ")
            data = self.editor_tabs_data.get(widget, {})
            encoding = data.get('encoding', 'utf-8')
            encoding_display_name = self.reverse_encoding_map.get(encoding, "UTF-8")
            self.encoding_label.setText(f" {encoding_display_name} ")
            
            # Update the toolbar dropdown
            if (idx := self.encoding_combo.findData(encoding)) != -1:
                self.encoding_combo.setCurrentIndex(idx)
            
            self.encoding_combo.setEnabled(bool(data.get('filepath')))
        else:
            self.cursor_label.setText("")
            self.encoding_label.setText("")
            self.encoding_combo.setEnabled(False)
            for i in range(self.tab_widget.count()):
                if (w := self.tab_widget.widget(i)) and isinstance(w,
                                                                   EditorWidget) and w.find_panel.isVisible(): w.hide_find_panel()
        
        self.encoding_combo.blockSignals(False)
        self.actions["find_replace"].setEnabled(is_editor)

    def _is_editor_modified(self, ed):
        return isinstance(ed, EditorWidget) and (data := self.editor_tabs_data.get(ed)) and hash(ed.get_text()) != data[
            'original_hash']

    def _on_content_changed(self, editor):
        if not (isinstance(editor, EditorWidget) and self.tab_widget.isAncestorOf(editor)): return
        mod, idx = self._is_editor_modified(editor), self.tab_widget.indexOf(editor)
        if idx != -1:
            txt = self.tab_widget.tabText(idx)
            if mod and not txt.endswith(' *'):
                self.tab_widget.setTabText(idx, f'{txt} *')
            elif not mod and txt.endswith(' *'):
                self.tab_widget.setTabText(idx, txt[:-2])
        self._update_window_title()
        if self.settings.get("auto_save_enabled"): self.auto_save_timer.start(
            self.settings.get("auto_save_delay_seconds", 3) * 1000)
        
        # --- NEW: Trigger draft save on content change ---
        if mod:
            self.draft_save_timer.start()

    def _update_window_title(self):
        proj = os.path.basename(self.project_manager.get_active_project_path() or "");
        current = ""
        if isinstance(w := self.tab_widget.currentWidget(), EditorWidget):
            current = os.path.basename(self.editor_tabs_data.get(w, {}).get('filepath') or self.tab_widget.tabText(
                self.tab_widget.currentIndex()).replace(" *", ""))
            if self._is_editor_modified(w): current += " *"
        self.setWindowTitle(" - ".join(filter(None, [current, proj, "PuffinPyEditor"])))

    def _action_save_file(self, editor_widget=None, save_as=False):
        editor = editor_widget or self.tab_widget.currentWidget()
        if not (isinstance(editor, EditorWidget) and (data := self.editor_tabs_data.get(editor))):
            return None

        content = editor.get_text()
        encoding = data.get('encoding', 'utf-8')
        
        # This will either do a 'Save As...' (if filepath is missing or save_as=True) or a direct 'Save'.
        new_fp, new_encoding = self.file_handler.save_file_content(data['filepath'], content, save_as, encoding=encoding)
        
        if new_fp:
            # Delete the draft file since changes are now permanent
            draft_path = helpers.get_draft_path(new_fp)
            if os.path.exists(draft_path):
                os.remove(draft_path)
                log.info(f"Removed draft file for saved file: {new_fp}")

            self.file_handler._add_to_recent_files(new_fp)

            # --- FIX: Reassign the entire dictionary for the editor to ensure its state is fully updated.
            # This robustly handles the transition from an unsaved "Untitled" file to a saved file with a path.
            self.editor_tabs_data[editor] = {
                'filepath': new_fp,
                'original_hash': hash(content),
                'encoding': new_encoding
            }
            # --- END FIX ---
            
            editor.set_filepath(new_fp)
            
            if (idx := self.tab_widget.indexOf(editor)) != -1:
                self.tab_widget.setTabText(idx, os.path.basename(new_fp))
                self.tab_widget.setTabToolTip(idx, new_fp)
                
            self.statusBar().showMessage(f"File saved: {os.path.basename(new_fp)}", 3000)
            self._on_content_changed(editor)  # This will remove the '*' modification marker
            self._on_tab_changed(self.tab_widget.currentIndex()) # Update status bar with encoding
            return new_fp
        
        self.statusBar().showMessage("Save cancelled.", 2000)
        return None

    def _action_save_as(self):
        self._action_save_file(save_as=True)

    def _action_save_all(self):
        saved_count = 0
        for i in range(self.tab_widget.count()):
            editor = self.tab_widget.widget(i)
            if self._is_editor_modified(editor):
                if self._action_save_file(editor_widget=editor):
                    saved_count += 1
        if saved_count > 0:
            self.statusBar().showMessage(f"Saved {saved_count} file(s).", 3000)

    def _action_close_tab_by_index(self, index):
        widget_to_close = self.tab_widget.widget(index)
        if not widget_to_close:
            return

        dummy_close_event = QCloseEvent()
        self._close_widget_safely(widget_to_close, dummy_close_event)

        if dummy_close_event.isAccepted():
            if self.tab_widget.indexOf(widget_to_close) != -1:
                self.tab_widget.removeTab(self.tab_widget.indexOf(widget_to_close))
            widget_to_close.deleteLater()
            if self.tab_widget.count() == 0:
                self._add_new_tab(is_placeholder=True)

    def _close_widget_safely(self, widget, event):
        # --- MODIFIED: No more save prompt, just save a draft if needed ---
        if isinstance(widget, EditorWidget):
            if self._is_editor_modified(widget):
                self._save_draft(widget)
            if widget in self.editor_tabs_data:
                del self.editor_tabs_data[widget]

        event.accept()

    def _update_recent_files_menu(self):
        self.recent_files_menu.clear();
        recent = self.settings.get("recent_files", []);
        self.recent_files_menu.setEnabled(bool(recent))
        for i, fp in enumerate(recent[:10]):
            act = QAction(f"&{i + 1} {os.path.basename(fp)}", self);
            act.setData(fp);
            act.setToolTip(fp);
            act.triggered.connect(self._action_open_recent_file);
            self.recent_files_menu.addAction(act)

    def _action_open_recent_file(self):
        if act := self.sender(): self._action_open_file(act.data())

    def _trigger_file_linter(self):
        if (editor := self.tab_widget.currentWidget()) and (
                fp := self.editor_tabs_data.get(editor, {}).get('filepath')):
            self.linter_manager.lint_file(fp)

    def _show_about_dialog(self):
        QMessageBox.about(self, "About", f"PuffinPyEditor v{versioning.APP_VERSION}")

    def _open_github_link(self):
        QDesktopServices.openUrl(QUrl("https://github.com/Stelliro/PuffinPyEditor"))

    def _auto_save_current_tab(self):
        if self._is_editor_modified(ed := self.tab_widget.currentWidget()):
            self._action_save_file(editor_widget=ed)

    def _on_editor_settings_changed(self):
        [w.apply_styles_and_settings() for i in range(self.tab_widget.count()) if
         isinstance(w := self.tab_widget.widget(i), EditorWidget)]

    def _action_open_preferences(self):
        if not self.preferences_dialog or not self.preferences_dialog.isVisible():
            self.preferences_dialog = PreferencesDialog(self.theme_manager, self.git_manager, self.github_manager, self.plugin_manager,
                                                        self.puffin_api, self)
            self.preferences_dialog.settings_changed_for_editor_refresh.connect(self._on_editor_settings_changed);
            self.preferences_dialog.theme_changed_signal.connect(self._on_theme_selected)
        self.preferences_dialog.show();
        self.preferences_dialog.raise_();
        self.preferences_dialog.activateWindow()

    def _action_force_quit(self):
        log.warning("Force Quit triggered.");
        QApplication.instance().quit()

    def _goto_definition_result(self, fp, line, col):
        if not fp: self.statusBar().showMessage("Definition not found", 3000); return
        np = os.path.normpath(fp)
        for i in range(self.tab_widget.count()):
            if isinstance(ed := self.tab_widget.widget(i), EditorWidget) and self.editor_tabs_data.get(ed, {}).get(
                    'filepath') == np:
                self.tab_widget.setCurrentIndex(i);
                ed.goto_line_and_column(line, col);
                return
        self._action_open_file(np);
        if isinstance(cur := self.tab_widget.currentWidget(), EditorWidget):
            cur.goto_line_and_column(line, col)
        else:
            log.warning(f"Could not jump to definition. Expected editor for {np}.")

    def _shutdown_plugins(self):
        log.info("Shutting down plugins...");
        [p.instance.shutdown() for p in self.plugin_manager.get_loaded_plugins()
         if hasattr(p.instance, 'shutdown')]

    def _shutdown_managers(self):
        log.info("Shutting down core managers...");
        [m.shutdown() for m in
         [self.completion_manager, self.github_manager, self.git_manager,
          self.linter_manager] if hasattr(m, 'shutdown')]

    def closeEvent(self, e: QCloseEvent):
        if self._is_app_closing: e.accept(); return
        self._is_app_closing = True

        open_fps = []
        for i in range(self.tab_widget.count()):
            widget = self.tab_widget.widget(i)
            if isinstance(widget, EditorWidget):
                data = self.editor_tabs_data.get(widget)
                if data and (filepath := data.get('filepath')):
                    open_fps.append(filepath)
                # --- NEW: Save final drafts on close ---
                if self._is_editor_modified(widget):
                    self._save_draft(widget)

        settings_manager.set("open_files", open_fps, save_immediately=False)
        if hasattr(self, 'explorer_panel'):
            settings_manager.set("explorer_expanded_paths", self.explorer_panel.get_expanded_paths(),
                                 save_immediately=False)
        self.project_manager.save_session()
        self.settings.save()

        self._shutdown_plugins()
        self._shutdown_managers()
        log.info("PuffinPyEditor exited cleanly.")
        e.accept()

    def toggle_find_panel(self):
        if isinstance(ed := self.tab_widget.currentWidget(), EditorWidget):
            ed.toggle_find_panel()
        else:
            log.warning("Find called on non-editor widget.")

    def _on_active_project_changed(self, cur, _):
        if not cur: return
        root = cur;
        while parent := root.parent(): root = parent
        if (data := root.data(0, Qt.ItemDataRole.UserRole)) and (path := data.get('path')):
            self.project_manager.set_active_project(path)
            # Update completion manager context when active project changes
            self.completion_manager.update_project_path(path)

    def _on_item_created(self, item_type, path):
        if item_type == 'file': self._add_header_to_new_file(path)

    def _generate_header_line(self, file_path: str):
        ext = os.path.splitext(file_path)[1].lower()
        start = self.COMMENT_MAP.get(ext)
        if not start or not (root := self.project_manager.get_active_project_path()) or not file_path.startswith(
                root): return None
        end_comment = self.END_COMMENT_MAP.get(start, '')

        # Ensure project basename is part of the path if not root
        rel_path_to_proj_root = os.path.relpath(file_path, root)
        final_path_in_header = os.path.join(os.path.basename(root), rel_path_to_proj_root).replace(os.sep, '/')

        return f"{start} PuffinPyEditor/{final_path_in_header} {end_comment}\n"

    def _add_header_to_new_file(self, file_path):
        if not (header := self._generate_header_line(file_path)): return
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(header);
                log.info(f"Autopopulated header for {file_path}")
        except IOError as e:
            log.error(f"Failed to write header to {file_path}: {e}")

    def _update_file_header(self, file_path):
        if not (header := self._generate_header_line(file_path)): return
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            if not lines:
                lines.append(header)
            elif re.compile(r"^(#|//|<!--|\/\*)\s*PuffinPyEditor/.*").match(lines[0]):
                lines[0] = header
            else:
                lines.insert(0, header)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.writelines(lines);
                log.info(f"Updated header for: {file_path}")
        except Exception as e:
            log.error(f"Failed to update header for {file_path}: {e}", exc_info=True)
            
    def _on_encoding_changed_from_dropdown(self, index: int):
        editor = self.tab_widget.currentWidget()
        if not isinstance(editor, EditorWidget):
            return

        new_encoding = self.encoding_combo.itemData(index)
        data = self.editor_tabs_data.get(editor)
        if not data or new_encoding == data.get('encoding'):
            return

        reply = QMessageBox.question(
            self,
            "Change File Encoding",
            f"This will re-save the file '{os.path.basename(data.get('filepath'))}' with the new encoding '{self.encoding_combo.currentText()}'.\n\n"
            "This may alter the file content if it contains characters not supported by the new encoding. Are you sure you want to continue?",
            QMessageBox.StandardButton.Save | QMessageBox.StandardButton.Cancel,
            QMessageBox.StandardButton.Cancel
        )

        if reply == QMessageBox.StandardButton.Save:
            self._resave_with_new_encoding(editor, new_encoding)
        else:
            # Revert the dropdown to the file's actual encoding
            self._on_tab_changed(self.tab_widget.currentIndex())

    def _resave_with_new_encoding(self, editor: EditorWidget, new_encoding: str):
        data = self.editor_tabs_data.get(editor)
        if not data or not data.get('filepath'):
            return # Should not happen as dropdown is disabled for unsaved files

        content = editor.get_text()
        filepath = data['filepath']

        # Use the file_handler to save with the new encoding
        saved_path, final_encoding = self.file_handler.save_file_content(filepath, content, save_as=False, encoding=new_encoding)
        
        if saved_path:
            # Update the editor's data store with the new encoding and reset the hash
            data['encoding'] = final_encoding
            data['original_hash'] = hash(content)
            self._on_content_changed(editor) # Update modification status
            self.statusBar().showMessage(f"File saved with new encoding: {self.reverse_encoding_map.get(final_encoding, final_encoding)}", 4000)
        else:
            self.statusBar().showMessage("Failed to re-save file with new encoding.", 4000)
            self._on_tab_changed(self.tab_widget.currentIndex()) # Revert dropdown on failure

    def _save_draft(self, editor: EditorWidget):
        data = self.editor_tabs_data.get(editor)
        if not data or not data['filepath']:
            return  # Can't save a draft for an unsaved file

        draft_path = helpers.get_draft_path(data['filepath'])
        content = editor.get_text()
        encoding = data.get('encoding', 'utf-8')
        try:
            with open(draft_path, 'w', encoding=encoding) as f:
                f.write(content)
            log.info(f"Saved draft for {os.path.basename(data['filepath'])}")
        except (IOError, OSError) as e:
            log.error(f"Failed to write draft file to {draft_path}: {e}")

    def _save_current_draft(self):
        if editor := self.tab_widget.currentWidget():
            if isinstance(editor, EditorWidget) and self._is_editor_modified(editor):
                self._save_draft(editor)
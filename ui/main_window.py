# PuffinPyEditor/ui/main_window.py
import sys
import os
import subprocess
import tempfile
import shutil
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QStatusBar, QSplitter,
                             QTabWidget, QMessageBox, QApplication, QFileDialog, QMenu, QLabel, QPushButton,
                             QToolButton, QDockWidget, QProgressDialog, QDialog, QCheckBox)
from PyQt6.QtGui import QAction, QKeySequence, QIcon, QActionGroup, QColor, QFont, QTextDocument
from PyQt6.QtCore import Qt, QSize, QTimer, pyqtSignal, QObject

import qtawesome as qta
import git
from git.exc import InvalidGitRepositoryError

# Core Application Logic
from utils.logger import log
from app_core.settings_manager import settings_manager
from app_core.theme_manager import theme_manager
from app_core.file_handler import FileHandler
from app_core.project_manager import ProjectManager
from app_core.code_runner import CodeRunner
from app_core.linter_manager import LinterManager
from app_core.plugin_manager import PluginManager
from app_core.completion_manager import CompletionManager
from app_core.update_manager import UpdateManager
from app_core.source_control_manager import SourceControlManager
from app_core.github_manager import GitHubManager

# UI Widgets and Dialogs
from ui.file_tree_view import FileTreeViewWidget
from ui.editor_widget import EditorWidget
from ui.output_panel import OutputPanel
from ui.dialogs.preferences_dialog import PreferencesDialog
from ui.dialogs.search_replace_dialog import SearchReplaceDialog
from ui.dialogs.github_dialog import GitHubDialog
from ui.dialogs.new_release_dialog import NewReleaseDialog
from ui.dialogs.select_repo_dialog import SelectRepoDialog
from ui.widgets.problems_panel import ProblemsPanel
from ui.widgets.project_source_control_panel import ProjectSourceControlPanel
from ui.widgets.terminal_widget import TerminalWidget


class MainWindow(QMainWindow):
    untitled_file_counter = 0
    _is_app_closing = False

    def __init__(self):
        super().__init__()
        self.workflow_handler = None
        self._initialize_managers()
        self.setWindowTitle("PuffinPyEditor")
        self._load_window_geometry()
        self._create_widgets()
        self._create_actions()
        self._create_menu()
        self._create_layout()
        self._create_statusbar()
        self._connect_signals()
        self._apply_theme_and_icons(self.settings.get("last_theme_id"))
        self._initialize_project_views()
        self._update_window_title()
        self._update_editor_actions_state()
        log.info("MainWindow initialized successfully.")

    def _initialize_managers(self):
        self.settings = settings_manager
        self.project_manager = ProjectManager()
        self.completion_manager = CompletionManager(self)
        self.github_manager = GitHubManager(self)
        self.git_manager = SourceControlManager(self)
        self.file_handler = FileHandler(self)
        self.code_runner = CodeRunner()
        self.linter_manager = LinterManager(self)
        self.plugin_manager = PluginManager(self)
        self.update_manager = UpdateManager(self)
        self.preferences_dialog_instance = None
        self.github_dialog = None
        self.search_dialog = None
        self.actions = {}
        self.editor_tabs_data = {}
        self.lint_timer = QTimer(self)
        self.lint_timer.setSingleShot(True)
        self.lint_timer.setInterval(1500)

    def _load_window_geometry(self):
        size = self.settings.get("window_size", [1600, 1000])
        pos = self.settings.get("window_position")
        self.resize(QSize(size[0], size[1]))
        if pos: self.move(pos[0], pos[1])

    def _create_widgets(self):
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
        sb_layout.setSpacing(0)
        sb_layout.addWidget(self.project_tabs)
        self.bottom_dock = QDockWidget("Info Panels", self)
        self.bottom_dock.setObjectName("BottomDock")
        self.bottom_tabs = QTabWidget()
        self.output_panel = OutputPanel()
        self.problems_panel = ProblemsPanel(self)
        self.source_control_panel = ProjectSourceControlPanel(self.project_manager, self.git_manager, self)
        self.terminal_widget = TerminalWidget(self)
        self.bottom_tabs.addTab(self.terminal_widget, "Terminal")
        self.bottom_tabs.addTab(self.output_panel, "Output")
        self.bottom_tabs.addTab(self.problems_panel, "Problems")
        self.bottom_tabs.addTab(self.source_control_panel, "Source Control")
        self.bottom_dock.setWidget(self.bottom_tabs)
        self.addDockWidget(Qt.DockWidgetArea.BottomDockWidgetArea, self.bottom_dock)

    def _create_actions(self):
        actions_map = {
            "new_file": ("&New File", self._add_new_tab, "Ctrl+N"),
            "open_file": ("&Open File...", self._action_open_file_dialog, "Ctrl+O"),
            "open_folder": ("Open &Folder...", self._action_open_folder, None),
            "close_project": ("&Close Project", self._action_close_project, None),
            "save": ("&Save", self._action_save_file, "Ctrl+S"),
            "save_as": ("Save &As...", self._action_save_as, "Ctrl+Shift+S"),
            "save_all": ("Save A&ll", self._action_save_all, "Ctrl+Alt+S"),
            "preferences": ("&Preferences...", self._action_open_preferences, "Ctrl+,"),
            "exit": ("E&xit", self.close, "Ctrl+Q"), "find": ("&Find/Replace...", self._action_find, "Ctrl+F"),
            "goto_definition": ("&Go to Definition", self._action_goto_definition, "F12"),
            "run_script": ("Run Script", self._action_run_script, "F5"),
            "stop_script": ("Stop Script", self._action_stop_script, "Ctrl+F5"),
            "check_updates": ("Check for &Updates...", lambda: self.update_manager.check_for_updates(), None),
            "export_for_ai": ("Export Project for AI...", self._action_export_for_ai, None)
        }
        for key, (text, cb, sc) in actions_map.items():
            self.actions[key] = QAction(text, self)
            self.actions[key].triggered.connect(cb)
            if sc: self.actions[key].setShortcut(QKeySequence(sc))

    def _create_menu(self):
        mb = self.menuBar()
        fm = mb.addMenu("&File")
        em = mb.addMenu("&Edit")
        gm = mb.addMenu("&Go")
        vm = mb.addMenu("&View")
        rm = mb.addMenu("&Run")
        self.tools_menu = mb.addMenu("&Tools")
        hm = mb.addMenu("&Help")
        fm.addActions([self.actions[k] for k in ["new_file", "open_file"]])
        self.recent_files_menu = fm.addMenu("Open &Recent")
        fm.addSeparator()
        fm.addActions([self.actions[k] for k in ["open_folder", "close_project"]])
        fm.addSeparator()
        fm.addActions([self.actions[k] for k in ["save", "save_as", "save_all"]])
        fm.addSeparator()
        fm.addActions([self.actions[k] for k in ["preferences", "exit"]])
        em.addAction(self.actions["find"])
        gm.addAction(self.actions["goto_definition"])
        self.theme_menu = vm.addMenu("&Themes")
        vm.addSeparator()
        vm.addAction(self.bottom_dock.toggleViewAction())
        rm.addActions([self.actions[k] for k in ["run_script", "stop_script"]])
        self.tools_menu.addAction(self.actions["export_for_ai"])
        hm.addAction(self.actions["check_updates"])
        self.plugin_manager.discover_and_load_plugins()
        self._update_recent_files_menu()

    def _create_layout(self):
        layout = QHBoxLayout(self.central_widget)
        layout.setContentsMargins(5, 5, 5, 5)
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        self.splitter.addWidget(self.project_sidebar_container)
        self.splitter.addWidget(self.tab_widget)
        layout.addWidget(self.splitter)
        self.splitter.setSizes(self.settings.get("splitter_sizes", [250, 950]))

    def _create_statusbar(self):
        self.setStatusBar(QStatusBar(self))
        self.cursor_label = QLabel(" Ln 1, Col 1 ")
        self.statusBar().addPermanentWidget(self.cursor_label)

    def _connect_signals(self):
        self.project_tabs.currentChanged.connect(self._on_project_tab_changed)
        self.project_tabs.tabCloseRequested.connect(self._action_close_project_by_index)
        self.tab_widget.currentChanged.connect(self._on_tab_changed)
        self.tab_widget.tabCloseRequested.connect(self._action_close_tab_by_index)
        self.splitter.splitterMoved.connect(lambda: self.settings.set("splitter_sizes", self.splitter.sizes(), False))
        self.lint_timer.timeout.connect(self._execute_file_linter_check)
        self.linter_manager.lint_results_ready.connect(self._update_problems_panel_for_file)
        self.problems_panel.problem_selected.connect(self._goto_problem)
        self.completion_manager.definition_found.connect(self._goto_definition_result)
        self.source_control_panel.publish_repo_requested.connect(self._publish_project)
        self.source_control_panel.link_to_remote_requested.connect(self._action_link_to_remote)
        self.source_control_panel.create_release_requested.connect(self._action_create_release)
        self.source_control_panel.change_visibility_requested.connect(self._action_change_visibility)
        self.update_manager.update_check_finished.connect(self._handle_update_check_result)
        self.code_runner.output_received.connect(self.output_panel.append_output)
        self.code_runner.error_received.connect(lambda text: self.output_panel.append_output(text, is_error=True))
        self.git_manager.git_success.connect(self.source_control_panel.refresh_all_projects)

    def _apply_theme_and_icons(self, theme_id):
        theme_manager.set_theme(theme_id, QApplication.instance())
        accent_color = theme_manager.current_theme_data['colors'].get('accent', 'silver')
        icon_color = "#000000" if QColor(accent_color).lightnessF() > 0.6 else "#FFFFFF"
        qta.set_defaults(color=accent_color, color_active=icon_color)
        self._rebuild_theme_menu()
        self.source_control_panel.update_icons()
        icon_map = {"terminal": 'fa5s.laptop-code', "output": 'fa5s.terminal', "problems": 'fa5s.bug',
                    "source control": 'fa5b.git-alt'}
        for i in range(self.bottom_tabs.count()):
            text = self.bottom_tabs.tabText(i).lower()
            icon_name = icon_map.get(text, 'fa5s.question-circle')
            try:
                self.bottom_tabs.setTabIcon(i, qta.icon(icon_name))
            except Exception as e:
                log.warning(f"Could not set icon '{icon_name}' for tab '{text}': {e}")
        colors = theme_manager.current_theme_data.get("colors", {})
        font = QFont(self.settings.get("font_family"), self.settings.get("font_size"))
        self.terminal_widget.set_font_and_color(font, QColor(colors.get("editor.foreground", "#fff")),
                                                QColor(colors.get("editor.background", "#000")))
        self.output_panel.update_theme()
        for i in range(self.tab_widget.count()):
            if isinstance(widget := self.tab_widget.widget(i), EditorWidget): widget.highlighter.rehighlight_document()

    def _rebuild_theme_menu(self):
        self.theme_menu.clear()
        group = QActionGroup(self)
        group.setExclusive(True)
        for theme_id, name in theme_manager.get_available_themes_for_ui().items():
            action = QAction(name, self, checkable=True)
            action.setData(theme_id)
            if theme_id == theme_manager.current_theme_id: action.setChecked(True)
            action.triggered.connect(lambda checked, id=theme_id: self._on_theme_selected(id))
            group.addAction(action)
            self.theme_menu.addAction(action)

    def _initialize_project_views(self):
        active_project = self.project_manager.get_active_project_path()
        self.project_tabs.blockSignals(True)
        self.project_tabs.clear()
        open_projects = self.project_manager.get_open_projects()
        self.project_sidebar_container.setVisible(len(open_projects) > 0)
        active_index = 0
        if open_projects:
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
        self.source_control_panel.refresh_all_projects()
        if self.tab_widget.count() == 0: self._add_new_tab(is_placeholder=True)

    def _add_new_tab(self, fp=None, content="", is_placeholder=False):
        if self.tab_widget.count() == 1 and isinstance(self.tab_widget.widget(0), QLabel): self.tab_widget.removeTab(0)
        if is_placeholder:
            placeholder = QLabel("\n\n\tOpen a file or project to get started.", alignment=Qt.AlignmentFlag.AlignCenter)
            self.tab_widget.addTab(placeholder, "Welcome")
            self.tab_widget.setTabsClosable(False)
            return
        self.tab_widget.setTabsClosable(True)
        editor = EditorWidget(self.completion_manager, self)
        editor.set_filepath(fp)
        editor.set_text(content)
        editor.cursor_position_display_updated.connect(lambda l, c: self.cursor_label.setText(f" Ln {l}, Col {c} "))
        editor.content_possibly_changed.connect(self._on_content_changed)
        name = os.path.basename(fp) if fp else f"Untitled-{self.untitled_file_counter + 1}"
        if not fp: self.untitled_file_counter += 1
        index = self.tab_widget.addTab(editor, name)
        self.tab_widget.setTabToolTip(index, fp or f"Unsaved {name}")
        self.editor_tabs_data[editor] = {'filepath': fp, 'original_hash': hash(content)}
        self.tab_widget.setCurrentWidget(editor)
        editor.text_area.setFocus()

    def _action_create_release(self, project_path):
        repo_dialog = SelectRepoDialog(self.github_manager, self)
        if not repo_dialog.exec():
            repo_dialog.cleanup()
            return
        repo_config = repo_dialog.selected_repo_data
        repo_dialog.cleanup()

        release_dialog = NewReleaseDialog(self, default_tag="v1.0.0")
        if not release_dialog.exec(): return
        release_data = release_dialog.get_release_data()
        if not release_data['tag'] or not release_data['title']:
            QMessageBox.warning(self, "Invalid Input", "Tag and Title are required.")
            return

        temp_dir = tempfile.gettempdir()
        zip_filename = f"{os.path.basename(project_path)}-{release_data['tag']}.zip"
        zip_filepath = os.path.join(temp_dir, zip_filename)

        progress = QProgressDialog("Starting Release...", "Cancel", 0, 5, self)
        progress.setWindowModality(Qt.WindowModality.WindowModal)
        progress.setMinimumDuration(0)

        if self.workflow_handler: self.workflow_handler.cleanup()
        self.workflow_handler = self._create_release_workflow_handler(progress, project_path, repo_config, release_data,
                                                                      zip_filepath)
        progress.canceled.connect(self.workflow_handler.cleanup)
        progress.show()
        self.workflow_handler.start_workflow()

    def _create_release_workflow_handler(self, progress, project_path, repo_config, release_data, zip_filepath):
        handler_obj = QObject(self)

        def cleanup():
            log.info("Workflow handler cleanup called.")
            if os.path.exists(zip_filepath):
                try:
                    os.remove(zip_filepath)
                except OSError as e:
                    log.warning(f"Could not remove temp zip file: {e}")

            try:
                self.git_manager.git_success.disconnect(handle_success)
                self.git_manager.git_error.disconnect(handle_failure)
                self.github_manager.operation_success.disconnect(handle_success)
                self.github_manager.operation_failed.disconnect(handle_failure)
            except TypeError:
                log.info("Workflow signals may have already been disconnected.")

            progress.close()
            try:
                handler_obj.deleteLater()
            except RuntimeError:
                log.warning("Caught RuntimeError on deleteLater, object likely already deleted.")

            self.workflow_handler = None
            try:
                self.git_manager.git_success.connect(self.source_control_panel.refresh_all_projects)
            except (TypeError, RuntimeError):
                pass

        def handle_failure(error_message):
            QMessageBox.critical(self, "Operation Failed", str(error_message))
            cleanup()

        def handle_success(message, data):
            if progress.wasCanceled():
                cleanup()
                return

            if "Tag created" in message:
                progress.setValue(2)
                progress.setLabelText("Creating release on GitHub...")
                owner = repo_config.get('owner', {}).get('login', '')
                repo_name = repo_config.get('name', '')
                self.github_manager.create_release(owner, repo_name, release_data['tag'], release_data['title'],
                                                   release_data['notes'], release_data['prerelease'])
            elif "Release created" in message:
                progress.setValue(3)
                progress.setLabelText("Uploading release asset...")
                upload_url = data.get('release_data', {}).get('upload_url')
                if not upload_url:
                    handle_failure("GitHub did not provide an asset upload URL.")
                    return
                self.github_manager.upload_asset(upload_url, zip_filepath)
            elif "Asset uploaded" in message:
                progress.setValue(4)
                progress.setLabelText("Pushing to remote...")
                self.git_manager.push(project_path)
            elif "Push successful" in message:
                progress.setValue(5)
                QMessageBox.information(self, "Success", f"Release '{release_data['title']}' published successfully!")
                cleanup()

        def start_workflow():
            try:
                git.Repo(project_path)
            except git.exc.InvalidGitRepositoryError:
                handle_failure(f"Operation failed: '{os.path.basename(project_path)}' is not a Git repository.")
                return

            try:
                self.git_manager.git_success.disconnect(self.source_control_panel.refresh_all_projects)
            except TypeError:
                pass

            progress.setValue(0)
            progress.setLabelText("Zipping project...")
            if self.project_manager.create_project_zip(zip_filepath):
                progress.setValue(1)
                progress.setLabelText("Creating Git tag...")
                self.git_manager.create_tag(project_path, release_data['tag'], release_data['title'])
            else:
                handle_failure("Failed to create project zip archive.")

        self.git_manager.git_success.connect(handle_success)
        self.git_manager.git_error.connect(handle_failure)
        self.github_manager.operation_success.connect(handle_success)
        self.github_manager.operation_failed.connect(handle_failure)
        handler_obj.start_workflow = start_workflow
        handler_obj.cleanup = cleanup
        return handler_obj

    def _action_link_to_remote(self, local_path):
        log.info(f"Link to remote requested for local path: {local_path}")
        repo_dialog = SelectRepoDialog(self.github_manager, self)
        if repo_dialog.exec():
            repo_data = repo_dialog.selected_repo_data
            if repo_data and 'clone_url' in repo_data:
                remote_url = repo_data['clone_url']
                log.info(f"User selected remote repo '{repo_data['full_name']}' for linking.")
                self.git_manager.link_to_remote(local_path, remote_url)
            else:
                QMessageBox.warning(self, "Error", "Could not get repository details.")
        repo_dialog.cleanup()

    def _action_change_visibility(self, project_path):
        repo_dialog = SelectRepoDialog(self.github_manager, self, "Select Repository to Change Visibility")
        if not repo_dialog.exec():
            repo_dialog.cleanup()
            return

        repo_data = repo_dialog.selected_repo_data
        repo_dialog.cleanup()

        if not repo_data:
            QMessageBox.warning(self, "Error", "No repository was selected.")
            return

        is_currently_private = repo_data.get('private', False)
        new_visibility_str = "private" if not is_currently_private else "public"

        reply = QMessageBox.question(self, "Confirm Visibility Change",
                                     f"Are you sure you want to make the repository\n"
                                     f"'{repo_data['full_name']}'\n"
                                     f"<b>{new_visibility_str.upper()}</b>?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

        if reply == QMessageBox.StandardButton.No:
            return

        owner = repo_data.get('owner', {}).get('login', '')
        repo_name = repo_data.get('name', '')
        self.github_manager.update_repo_visibility(owner, repo_name, not is_currently_private)

    def _action_close_tab_by_index(self, index):
        editor = self.tab_widget.widget(index)
        if not isinstance(editor, EditorWidget):
            self.tab_widget.removeTab(index)
            return
        if hash(editor.get_text()) != self.editor_tabs_data.get(editor, {}).get('original_hash'):
            reply = QMessageBox.question(self, "Unsaved Changes", f"Save '{self.tab_widget.tabText(index)}'?",
                                         QMessageBox.StandardButton.Save | QMessageBox.StandardButton.Discard | QMessageBox.StandardButton.Cancel)
            if reply == QMessageBox.StandardButton.Cancel: return
            if reply == QMessageBox.StandardButton.Save and not self._action_save_file(): return
        if self.tab_widget.widget(index):
            del self.editor_tabs_data[editor]
            self.tab_widget.removeTab(index)
        if self.tab_widget.count() == 0 and not self._is_app_closing: self._add_new_tab(is_placeholder=True)

    def _update_tab_info(self, editor, path):
        if not path: return
        editor.set_filepath(path)
        self.editor_tabs_data[editor]['filepath'] = path
        self.editor_tabs_data[editor]['original_hash'] = hash(editor.get_text())
        idx = self.tab_widget.indexOf(editor)
        self.tab_widget.setTabText(idx, os.path.basename(path))
        self.tab_widget.setTabToolTip(idx, path)
        self.statusBar().showMessage(f"Saved: {path}", 3000)
        self._update_window_title()
        self.lint_timer.start(100)

    def _on_theme_selected(self, theme_id):
        self._apply_theme_and_icons(theme_id)

    def _on_tab_changed(self, index):
        self._update_window_title()
        self._update_editor_actions_state()
        self.lint_timer.start(1500)

    def _on_content_changed(self):
        self._update_window_title()
        self.lint_timer.start(1500)

    def _on_project_tab_changed(self, index):
        path = self.project_tabs.tabToolTip(index) if index != -1 else None
        self.project_manager.set_active_project(path)
        self.completion_manager.update_project_path(path)
        self.terminal_widget.set_working_directory(path)
        if not self._is_app_closing:
            self.terminal_widget.kill_process()
            self.terminal_widget.start_process()
        self._update_window_title()

    def _update_window_title(self):
        title = "PuffinPyEditor"
        parts = []
        if p_path := self.project_manager.get_active_project_path(): parts.append(f"[{os.path.basename(p_path)}]")
        if isinstance(editor := self.tab_widget.currentWidget(), EditorWidget):
            idx = self.tab_widget.indexOf(editor)
            tab_text = self.tab_widget.tabText(idx).strip().replace(' ●', '')
            is_dirty = hash(editor.get_text()) != self.editor_tabs_data.get(editor, {}).get('original_hash', 0)
            display_text = tab_text + (' ●' if is_dirty else '')
            if self.tab_widget.tabText(idx) != display_text: self.tab_widget.setTabText(idx, display_text)
            file_name = os.path.basename(self.editor_tabs_data[editor]['filepath']) if self.editor_tabs_data[editor][
                'filepath'] else tab_text
            parts.insert(0, file_name)
        self.setWindowTitle(" - ".join(parts) + f" - {title}" if parts else title)

    def _update_recent_files_menu(self):
        self.recent_files_menu.clear()
        recent_files = self.settings.get("recent_files", [])
        if not recent_files:
            no_files_action = QAction("No Recent Files", self)
            no_files_action.setEnabled(False)
            self.recent_files_menu.addAction(no_files_action)
            return
        for fp in recent_files:
            action = QAction(os.path.basename(fp), self)
            action.setData(fp)
            action.setToolTip(fp)
            action.triggered.connect(self._action_open_recent_file)
            self.recent_files_menu.addAction(action)

    def _action_open_recent_file(self):
        if isinstance(action := self.sender(), QAction):
            if (filepath := action.data()) and os.path.exists(filepath): self._action_open_file(filepath)

    def _action_open_folder(self):
        if path := QFileDialog.getExistingDirectory(self, "Open Folder"):
            self.project_manager.open_project(path)
            self._initialize_project_views()

    def _action_close_project_by_index(self, index):
        if not (0 <= index < self.project_tabs.count()): return
        path = self.project_tabs.tabToolTip(index)
        self.project_manager.close_project(path)
        self._initialize_project_views()

    def _action_close_project(self):
        self._action_close_project_by_index(self.project_tabs.currentIndex())

    def _action_open_file_dialog(self):
        filepath, content, _ = self.file_handler.open_file_dialog()
        if filepath: self._action_open_file(filepath, content)

    def _action_open_file(self, filepath, content=None):
        for i in range(self.tab_widget.count()):
            if self.tab_widget.tabToolTip(i) == filepath:
                self.tab_widget.setCurrentIndex(i)
                return
        if content is None:
            try:
                with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
                    content = f.read()
                self.file_handler._add_to_recent_files(filepath)
            except Exception as e:
                QMessageBox.critical(self, "Error Opening File", f"Could not open file: {e}")
                return
        self._add_new_tab(filepath, content)

    def _action_save_file(self) -> bool:
        if not isinstance(editor := self.tab_widget.currentWidget(), EditorWidget): return False
        if not (filepath := self.editor_tabs_data.get(editor, {}).get('filepath')): return self._action_save_as()
        if saved_path := self.file_handler.save_file_content(filepath, editor.get_text()):
            self._update_tab_info(editor, saved_path)
            return True
        return False

    def _action_save_as(self) -> bool:
        if not isinstance(editor := self.tab_widget.currentWidget(), EditorWidget): return False
        current_path = self.editor_tabs_data.get(editor, {}).get('filepath')
        if new_path := self.file_handler.save_file_content(current_path, editor.get_text(), save_as=True):
            self._update_tab_info(editor, new_path)
            return True
        return False

    def _action_save_all(self):
        for i in range(self.tab_widget.count()):
            if isinstance(editor := self.tab_widget.widget(i), EditorWidget) and hash(editor.get_text()) != \
                    self.editor_tabs_data[editor].get('original_hash'):
                if filepath := self.editor_tabs_data[editor].get('filepath'):
                    if self.file_handler.save_file_content(filepath, editor.get_text()): self._update_tab_info(editor,
                                                                                                               filepath)
        self._update_window_title()

    def _action_open_preferences(self):
        if self.preferences_dialog_instance is None:
            self.preferences_dialog_instance = PreferencesDialog(self.git_manager, self.github_manager, self)
            self.preferences_dialog_instance.theme_changed_signal.connect(self._on_theme_selected)
            self.preferences_dialog_instance.restart_requested.connect(self._restart_application)
            self.preferences_dialog_instance.settings_changed_for_editor_refresh.connect(
                self._on_editor_settings_changed)
        self.preferences_dialog_instance.show()
        self.preferences_dialog_instance.raise_()
        self.preferences_dialog_instance.activateWindow()

    def _on_editor_settings_changed(self):
        log.info("Applying updated editor settings to all open editors...")
        for i in range(self.tab_widget.count()):
            if isinstance(editor := self.tab_widget.widget(i), EditorWidget): editor.update_editor_settings()

    def _update_editor_actions_state(self):
        is_editor_open = isinstance(self.tab_widget.currentWidget(), EditorWidget)
        for key in ["save", "save_as", "save_all", "find", "goto_definition", "run_script", "stop_script"]:
            if key in self.actions: self.actions[key].setEnabled(is_editor_open)

    def _goto_problem(self, filepath, line, col):
        self._goto_definition_result(filepath, line, col)

    def _goto_definition_result(self, filepath, line, col):
        if not filepath:
            self.statusBar().showMessage("Definition not found", 3000)
            return
        for i in range(self.tab_widget.count()):
            if self.tab_widget.tabToolTip(i) == filepath:
                self.tab_widget.setCurrentIndex(i)
                if isinstance(editor := self.tab_widget.widget(i), EditorWidget): editor.goto_line_and_column(line, col)
                return
        self._action_open_file(filepath)
        QApplication.processEvents()
        if isinstance(editor := self.tab_widget.currentWidget(), EditorWidget) and self.tab_widget.tabToolTip(
                self.tab_widget.currentIndex()) == filepath:
            editor.goto_line_and_column(line, col)

    def _execute_file_linter_check(self):
        if isinstance(editor := self.tab_widget.currentWidget(), EditorWidget):
            if (ed := self.editor_tabs_data.get(editor)) and (fp := ed.get('filepath')) and fp.endswith('.py'):
                self.linter_manager.lint_file(fp)

    def _update_problems_panel_for_file(self, problems: list):
        if not (isinstance(editor := self.tab_widget.currentWidget(), EditorWidget) and (
                filepath := self.editor_tabs_data.get(editor, {}).get('filepath', ''))): return
        self.problems_panel.update_problems({filepath: problems})

    def _action_export_for_ai(self):
        if not (project_path := self.project_manager.get_active_project_path()):
            QMessageBox.information(self, "No Project Open", "Please open a project to export it.")
            return
        progress = QProgressDialog("Linting project for export...", "Cancel", 0, 0, self)
        progress.setWindowModality(Qt.WindowModality.WindowModal)
        progress.show()

        def on_lint_complete(problems):
            self.linter_manager.project_lint_results_ready.disconnect(on_lint_complete)
            progress.close()
            proj_name = os.path.basename(project_path)
            sugg_path = os.path.join(os.path.expanduser("~"), f"{proj_name}_ai_export.md")
            fp, _ = QFileDialog.getSaveFileName(self, "Export Project for AI", sugg_path, "Markdown Files (*.md)")
            if not fp: return
            QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
            try:
                success, message = self.project_manager.export_project_for_ai(fp, problems)
                if success:
                    QMessageBox.information(self, "Export Complete", message)
                else:
                    QMessageBox.critical(self, "Export Failed", message)
            finally:
                QApplication.restoreOverrideCursor()

        self.linter_manager.project_lint_results_ready.connect(on_lint_complete)
        self.linter_manager.lint_project(project_path)

    def _save_window_geometry(self):
        self.settings.set("window_size", [self.size().width(), self.size().height()], False)
        self.settings.set("window_position", [self.pos().x(), self.pos().y()], False)

    def _action_find(self):
        if not isinstance(editor := self.tab_widget.currentWidget(), EditorWidget): return
        if not self.search_dialog: self.search_dialog = SearchReplaceDialog(self)
        self.search_dialog.show_dialog(editor)

    def _action_goto_definition(self):
        if isinstance(editor := self.tab_widget.currentWidget(), EditorWidget): editor.request_definition_from_context()

    def _action_run_script(self):
        if isinstance(editor := self.tab_widget.currentWidget(), EditorWidget) and (
                filepath := self.editor_tabs_data.get(editor, {}).get('filepath')):
            self.output_panel.clear_output()
            self.bottom_tabs.setCurrentWidget(self.output_panel)
            self.code_runner.run_script(filepath)
        else:
            QMessageBox.warning(self, "Cannot Run", "Please save the file before running.")

    def _action_stop_script(self):
        self.code_runner.stop_script()

    def _restart_application(self):
        self.close()
        QApplication.processEvents()
        subprocess.Popen([sys.executable] + sys.argv)

    def _show_github_dialog(self):
        if self.github_dialog is None:
            self.github_dialog = GitHubDialog(self.github_manager, self.git_manager, self)
            self.github_dialog.project_cloned.connect(self._action_open_folder)
        self.github_dialog.show()

    def _publish_project(self, path):
        if not path and not (path := self.project_manager.get_active_project_path()):
            QMessageBox.warning(self, "Cannot Publish", "No project specified.")
            return

        repo_name = os.path.basename(path)
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Publish Project to GitHub")
        msg_box.setText(f"This will create a new repository named '{repo_name}' on your GitHub account.")
        msg_box.setInformativeText("Do you want to proceed?")
        private_checkbox = QCheckBox("Create as a private repository")
        msg_box.setCheckBox(private_checkbox)
        msg_box.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        msg_box.setDefaultButton(QMessageBox.StandardButton.Yes)

        reply = msg_box.exec()

        if reply == QMessageBox.StandardButton.No:
            return

        is_private = private_checkbox.isChecked()
        log.info(f"User chose to publish. Private: {is_private}")

        def on_repo_created(message, repo_data):
            self.github_manager.operation_success.disconnect(on_repo_created)
            self.github_manager.operation_failed.disconnect(on_repo_failed)
            self.statusBar().showMessage("Publishing to new repository...")
            self.git_manager.publish_repo(path, repo_data['clone_url'])

        def on_repo_failed(error_message):
            self.github_manager.operation_success.disconnect(on_repo_created)
            self.github_manager.operation_failed.disconnect(on_repo_failed)
            QMessageBox.critical(self, "GitHub Error", f"Failed to create repository on GitHub:\n{error_message}")

        self.github_manager.operation_success.connect(on_repo_created)
        self.github_manager.operation_failed.connect(on_repo_failed)
        self.github_manager.create_repo(repo_name, "Published from PuffinPyEditor", is_private)

    def _handle_update_check_result(self, info):
        self.statusBar().clearMessage()
        if error_msg := info.get("error"):
            QMessageBox.critical(self, "Update Error", f"Error: {error_msg}")
        elif info.get("update_available") is False:
            QMessageBox.information(self, "Up to Date", "You are running the latest version.")
        elif download_url := info.get("download_url"):
            if QMessageBox.question(self, "Update Available",
                                    f"New version ({info.get('latest_version')}) available. Update now?\n\n{info.get('release_notes')}",
                                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No) == QMessageBox.StandardButton.Yes: self._initiate_update(
                download_url)

    def _initiate_update(self, url):
        updater_script = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'updater.py')
        if not os.path.exists(updater_script):
            QMessageBox.critical(self, "Error", "updater.py not found!")
            return
        app_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        subprocess.Popen([sys.executable, updater_script, url, app_dir], creationflags=subprocess.DETACHED_PROCESS,
                         close_fds=True, shell=False)
        self.close()

    def closeEvent(self, event):
        if self._is_app_closing:
            event.accept()
            return
        if self.workflow_handler: self.workflow_handler.cleanup()
        self.terminal_widget.kill_process()
        self._is_app_closing = True
        unsaved_tabs = [self.tab_widget.tabText(i) for i in range(self.tab_widget.count()) if
                        isinstance(editor := self.tab_widget.widget(i), EditorWidget) and hash(editor.get_text()) !=
                        self.editor_tabs_data[editor]['original_hash']]
        if unsaved_tabs:
            reply = QMessageBox.question(self, "Unsaved Changes", "You have unsaved changes. Save before exiting?",
                                         QMessageBox.StandardButton.SaveAll | QMessageBox.StandardButton.Discard | QMessageBox.StandardButton.Cancel)
            if reply == QMessageBox.StandardButton.Cancel:
                self._is_app_closing = False
                event.ignore()
                return
            elif reply == QMessageBox.StandardButton.SaveAll:
                self._action_save_all()
        self.completion_manager.shutdown()
        self.git_manager.shutdown()
        self.github_manager.shutdown()
        self.linter_manager.shutdown()
        self.project_manager.save_session()
        self._save_window_geometry()
        self.settings.save()
        log.info("PuffinPyEditor closing clean.")
        event.accept()
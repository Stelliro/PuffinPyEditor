# PuffinPyEditor/ui/preferences_dialog.py
import uuid
import sys
import os
import tempfile
import requests
from typing import Optional, Any
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QTabWidget,
                             QWidget, QLabel, QComboBox, QSpinBox, QCheckBox,
                             QPushButton, QLineEdit, QDialogButtonBox,
                             QFontComboBox, QSplitter, QFormLayout,
                             QListWidget, QListWidgetItem, QMessageBox,
                             QGroupBox, QFileDialog, QInputDialog,
                             QStackedWidget)
from PyQt6.QtGui import QFont, QDesktopServices, QColor
from PyQt6.QtCore import Qt, QSize, pyqtSignal, QUrl

if sys.platform == "win32":
    import winshell

import qtawesome as qta
from utils.logger import log
from utils.helpers import get_startup_shortcut_path
from app_core.settings_manager import settings_manager
from app_core.theme_manager import theme_manager
from app_core.github_manager import GitHubManager
from app_core.source_control_manager import SourceControlManager
from app_core.plugin_manager import PluginManager, Plugin
from .theme_editor_dialog import ThemeEditorDialog


class AuthDialog(QDialog):
    def __init__(self, user_code: str, verification_uri: str,
                 parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setWindowTitle("GitHub Device Authorization")
        layout = QVBoxLayout(self)
        layout.addWidget(
            QLabel("Please authorize PuffinPyEditor in your browser.")
        )
        url_label = QLabel(
            f"1. Open: <a href='{verification_uri}'>{verification_uri}</a>"
        )
        url_label.setOpenExternalLinks(True)
        layout.addWidget(url_label)
        layout.addWidget(QLabel("2. Enter this one-time code:"))
        code_label = QLineEdit(user_code)
        code_label.setReadOnly(True)
        code_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        code_label.setFont(QFont("Consolas", 14, QFont.Weight.Bold))
        layout.addWidget(code_label)
        QDesktopServices.openUrl(QUrl(verification_uri))
        self.setFixedSize(self.sizeHint())


class PreferencesDialog(QDialog):
    settings_changed_for_editor_refresh = pyqtSignal()
    theme_changed_signal = pyqtSignal(str)

    def __init__(self, git_manager: SourceControlManager,
                 github_manager: GitHubManager, plugin_manager: PluginManager,
                 parent: Optional[QWidget] = None):
        super().__init__(parent)
        log.info("PreferencesDialog initializing...")
        self.setWindowTitle("Preferences")
        self.setMinimumSize(QSize(850, 700))
        self.git_manager = git_manager
        self.github_manager = github_manager
        self.plugin_manager = plugin_manager
        self.original_settings: dict[str, Any] = {}
        self.original_git_config: dict[str, str] = {}
        self.staged_repos: list[dict] = []
        self.staged_active_repo_id: Optional[str] = None
        self.current_repo_id_in_form: Optional[str] = None
        self.auth_dialog: Optional[AuthDialog] = None
        self.theme_editor_dialog_instance: Optional[ThemeEditorDialog] = None
        self.restart_needed = False
        self.is_loading = False
        self.main_layout = QVBoxLayout(self)
        self.tab_widget = QTabWidget()
        self.main_layout.addWidget(self.tab_widget)
        self._create_tabs()
        self._create_button_box()
        self._connect_global_signals()
        self._connect_ui_changed_signals()
        log.info("PreferencesDialog initialized.")

    def _create_tabs(self):
        self._create_appearance_tab()
        self._create_editor_tab()
        self._create_run_tab()
        self._create_system_tab()
        self._create_source_control_tab()
        self._create_plugins_tab()

    def _create_button_box(self):
        buttons = (QDialogButtonBox.StandardButton.Ok |
                   QDialogButtonBox.StandardButton.Cancel |
                   QDialogButtonBox.StandardButton.Apply)
        self.button_box = QDialogButtonBox(buttons)
        self.main_layout.addWidget(self.button_box)

    def _connect_global_signals(self):
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        self.button_box.button(
            QDialogButtonBox.StandardButton.Apply).clicked.connect(self.apply_settings)

        self.git_manager.git_config_ready.connect(self._populate_git_config_fields)
        self.github_manager.device_code_ready.connect(self._on_device_code_ready)
        self.github_manager.auth_successful.connect(self._on_auth_successful)
        self.github_manager.auth_failed.connect(self._on_auth_failed)
        self.github_manager.auth_polling_lapsed.connect(self._on_auth_polling_lapsed)
        self.github_manager.operation_success.connect(self._handle_github_op_success)
        self.github_manager.plugin_index_ready.connect(self._on_plugin_index_ready)
        self.git_manager.git_success.connect(self._handle_git_success)

    def _handle_github_op_success(self, message, data):
        if "Repository" in message and "created" in message:
            new_repo_id = str(uuid.uuid4())
            owner, repo_name = self.git_manager.parse_git_url(data.get("clone_url"))
            new_repo = {
                "id": new_repo_id, "name": data.get("name"), "owner": owner, "repo": repo_name
            }
            self.staged_repos.append(new_repo)
            QMessageBox.information(
                self, "Success", f"Repository '{repo_name}' created on GitHub."
            )
            self._populate_repo_list(select_repo_id=new_repo_id)
            self._on_ui_setting_changed()

    def showEvent(self, event):
        self.is_loading = True
        self._load_settings_into_dialog()
        self.git_manager.get_git_config()
        self._update_auth_status()
        self._populate_all_plugin_lists()
        self.button_box.button(QDialogButtonBox.StandardButton.Apply).setEnabled(False)
        self.restart_needed = False
        super().showEvent(event)
        self.is_loading = False

    def _load_settings_into_dialog(self):
        self.original_settings = settings_manager.settings.copy()
        self._repopulate_theme_combo()
        self.font_family_combo.setCurrentFont(QFont(settings_manager.get("font_family")))
        self.font_size_spinbox.setValue(settings_manager.get("font_size"))
        self.show_line_numbers_checkbox.setChecked(settings_manager.get("show_line_numbers"))
        self.word_wrap_checkbox.setChecked(settings_manager.get("word_wrap"))
        self.show_indent_guides_checkbox.setChecked(settings_manager.get("show_indentation_guides"))
        self.indent_style_combo.setCurrentText(settings_manager.get("indent_style").capitalize())
        self.indent_width_spinbox.setValue(settings_manager.get("indent_width"))
        self.auto_save_checkbox.setChecked(settings_manager.get("auto_save_enabled"))
        self.auto_save_delay_spinbox.setValue(settings_manager.get("auto_save_delay_seconds"))
        self.max_recent_files_spinbox.setValue(settings_manager.get("max_recent_files"))
        self.python_path_edit.setText(settings_manager.get("python_interpreter_path", sys.executable))
        self.run_in_background_checkbox.setChecked(settings_manager.get("run_in_background", False))
        self.nsis_path_edit.setText(settings_manager.get("nsis_path", ""))
        self.cleanup_build_checkbox.setChecked(settings_manager.get("cleanup_after_build", True))
        self.staged_repos = [r.copy() for r in settings_manager.get("source_control_repos", [])]
        self.staged_active_repo_id = settings_manager.get("active_update_repo_id")
        self._populate_repo_list()
        self.plugins_repo_edit.setText(settings_manager.get("plugins_distro_repo", "Stelliro/puffin-plugins"))

    def _connect_ui_changed_signals(self):
        for widget in self.findChildren((QComboBox, QSpinBox, QCheckBox, QFontComboBox, QLineEdit)):
            if isinstance(widget, QComboBox): widget.currentIndexChanged.connect(self._on_ui_setting_changed)
            elif isinstance(widget, QFontComboBox): widget.currentFontChanged.connect(self._on_ui_setting_changed)
            elif isinstance(widget, QSpinBox): widget.valueChanged.connect(self._on_ui_setting_changed)
            elif isinstance(widget, QCheckBox): widget.stateChanged.connect(self._on_ui_setting_changed)
            elif isinstance(widget, QLineEdit): widget.textChanged.connect(self._on_ui_setting_changed)

    def _on_ui_setting_changed(self, *args):
        if self.is_loading or not self.isVisible(): return
        self.button_box.button(QDialogButtonBox.StandardButton.Apply).setEnabled(True)

    def apply_settings(self):
        apply_button = self.button_box.button(QDialogButtonBox.StandardButton.Apply)
        if not apply_button.isEnabled(): return

        if sys.platform == "win32" and self.run_in_background_checkbox.isChecked() != self.original_settings.get("run_in_background", False):
            self._manage_startup_shortcut(self.run_in_background_checkbox.isChecked())
        
        new_name, new_email = self.git_user_name_edit.text().strip(), self.git_user_email_edit.text().strip()
        if new_name != self.original_git_config.get('name') or new_email != self.original_git_config.get('email'):
            self.git_manager.set_git_config(new_name, new_email)
            self.original_git_config = {'name': new_name, 'email': new_email}

        self._save_repo_form_to_staged()
        settings_to_set = {
            "last_theme_id": self.theme_combo.currentData(),
            "font_family": self.font_family_combo.currentFont().family(),
            "font_size": self.font_size_spinbox.value(),
            "show_line_numbers": self.show_line_numbers_checkbox.isChecked(),
            "word_wrap": self.word_wrap_checkbox.isChecked(),
            "show_indentation_guides": self.show_indent_guides_checkbox.isChecked(),
            "indent_style": self.indent_style_combo.currentText().lower(),
            "indent_width": self.indent_width_spinbox.value(),
            "auto_save_enabled": self.auto_save_checkbox.isChecked(),
            "auto_save_delay_seconds": self.auto_save_delay_spinbox.value(),
            "max_recent_files": self.max_recent_files_spinbox.value(),
            "python_interpreter_path": self.python_path_edit.text().strip(),
            "run_in_background": self.run_in_background_checkbox.isChecked(),
            "nsis_path": self.nsis_path_edit.text().strip(),
            "cleanup_after_build": self.cleanup_build_checkbox.isChecked(),
            "source_control_repos": self.staged_repos,
            "active_update_repo_id": self.staged_active_repo_id,
            "plugins_distro_repo": self.plugins_repo_edit.text().strip(),
        }
        for key, value in settings_to_set.items():
            settings_manager.set(key, value, save_immediately=False)
        settings_manager.save()

        self.theme_changed_signal.emit(self.theme_combo.currentData())
        self.settings_changed_for_editor_refresh.emit()
        self.original_settings = settings_manager.settings.copy()
        apply_button.setEnabled(False)

        if self.restart_needed:
            QMessageBox.information(self, "Restart Required", "Some changes require a restart of the application to take effect.")
            self.restart_needed = False
        log.info("Applied settings from Preferences dialog.")

    def accept(self):
        if self.button_box.button(QDialogButtonBox.StandardButton.Apply).isEnabled():
            self.apply_settings()
        super().accept()

    def reject(self):
        if self.auth_dialog and self.auth_dialog.isVisible(): self.auth_dialog.reject()
        if self.button_box.button(QDialogButtonBox.StandardButton.Apply).isEnabled():
            if QMessageBox.question(self, "Unsaved Changes", "Discard unsaved changes?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.No) == QMessageBox.StandardButton.No:
                return
        if self.theme_combo.currentData() != self.original_settings.get("last_theme_id"):
            self.theme_changed_signal.emit(self.original_settings.get("last_theme_id"))
        super().reject()

    def _create_layout_in_groupbox(self, title: str, parent_layout: QVBoxLayout) -> QFormLayout:
        group = QGroupBox(title)
        parent_layout.addWidget(group)
        layout = QFormLayout(group)
        return layout

    def _create_appearance_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(15)
        theme_layout = self._create_layout_in_groupbox("Theming", layout)
        self.theme_combo = QComboBox()
        self.edit_themes_button = QPushButton("Customize Themes...")
        self.edit_themes_button.clicked.connect(self._open_theme_editor_dialog)
        theme_layout.addRow("Theme:", self.theme_combo)
        theme_layout.addRow("", self.edit_themes_button)
        font_layout = self._create_layout_in_groupbox("Editor Font", layout)
        self.font_family_combo = QFontComboBox()
        self.font_size_spinbox = QSpinBox()
        self.font_size_spinbox.setRange(6, 72)
        font_layout.addRow("Font Family:", self.font_family_combo)
        font_layout.addRow("Font Size:", self.font_size_spinbox)
        layout.addStretch()
        self.tab_widget.addTab(tab, qta.icon('fa5s.palette'), "Appearance")

    def _repopulate_theme_combo(self):
        current_id = self.original_settings.get("last_theme_id", "puffin_dark")
        self.theme_combo.blockSignals(True)
        self.theme_combo.clear()
        for theme_id, name in theme_manager.get_available_themes_for_ui().items():
            self.theme_combo.addItem(name, theme_id)
        if (index := self.theme_combo.findData(current_id)) != -1: self.theme_combo.setCurrentIndex(index)
        self.theme_combo.blockSignals(False)

    def _open_theme_editor_dialog(self):
        if not self.theme_editor_dialog_instance:
            self.theme_editor_dialog_instance = ThemeEditorDialog(self)
            self.theme_editor_dialog_instance.custom_themes_changed.connect(self._repopulate_theme_combo)
        self.theme_editor_dialog_instance.exec()

    def _create_editor_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(15)
        display_layout = self._create_layout_in_groupbox("Display", layout)
        display_layout.setRowWrapPolicy(QFormLayout.RowWrapPolicy.WrapAllRows)
        self.show_line_numbers_checkbox = QCheckBox("Show line numbers")
        self.word_wrap_checkbox = QCheckBox("Enable word wrap")
        self.show_indent_guides_checkbox = QCheckBox("Show indentation guides")
        display_layout.addRow(self.show_line_numbers_checkbox)
        display_layout.addRow(self.word_wrap_checkbox)
        display_layout.addRow(self.show_indent_guides_checkbox)
        indent_layout = self._create_layout_in_groupbox("Indentation", layout)
        self.indent_style_combo = QComboBox()
        self.indent_style_combo.addItems(["Spaces", "Tabs"])
        self.indent_width_spinbox = QSpinBox()
        self.indent_width_spinbox.setRange(1, 16)
        indent_layout.addRow("Indent Using:", self.indent_style_combo)
        indent_layout.addRow("Indent/Tab Width:", self.indent_width_spinbox)
        file_layout = self._create_layout_in_groupbox("File Handling", layout)
        self.auto_save_checkbox = QCheckBox("Enable auto-save")
        self.auto_save_delay_spinbox = QSpinBox()
        self.auto_save_delay_spinbox.setRange(1, 60); self.auto_save_delay_spinbox.setSuffix(" seconds")
        self.max_recent_files_spinbox = QSpinBox()
        self.max_recent_files_spinbox.setRange(1, 50)
        file_layout.addRow(self.auto_save_checkbox)
        file_layout.addRow("Auto-Save Delay:", self.auto_save_delay_spinbox)
        file_layout.addRow("Max Recent Files:", self.max_recent_files_spinbox)
        layout.addStretch()
        self.tab_widget.addTab(tab, qta.icon('fa5s.edit'), "Editor")

    def _create_run_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(15)
        run_layout = self._create_layout_in_groupbox("Execution Environment", layout)
        run_layout.setRowWrapPolicy(QFormLayout.RowWrapPolicy.WrapAllRows)
        path_layout = QHBoxLayout()
        self.python_path_edit = QLineEdit()
        browse_button = QPushButton("Browse..."); browse_button.clicked.connect(self._browse_for_python)
        path_layout.addWidget(self.python_path_edit, 1); path_layout.addWidget(browse_button)
        run_layout.addRow("Python Interpreter Path:", path_layout)
        info = QLabel("This interpreter is used for running scripts (F5) and code analysis.")
        info.setWordWrap(True); info.setStyleSheet("font-size: 9pt; color: grey;")
        run_layout.addRow(info)
        layout.addStretch()
        self.tab_widget.addTab(tab, qta.icon('fa5s.play'), "Run")

    def _browse_for_python(self):
        filter_str = "Executables (*.exe)" if sys.platform == "win32" else "All Files (*)"
        if path := QFileDialog.getOpenFileName(self, "Select Python Interpreter", "", filter_str)[0]:
            self.python_path_edit.setText(path)

    def _create_system_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(15)
        system_layout = self._create_layout_in_groupbox("System Integration", layout)
        system_layout.setRowWrapPolicy(QFormLayout.RowWrapPolicy.WrapAllRows)
        self.run_in_background_checkbox = QCheckBox("Launch at startup and run in background")
        if sys.platform != "win32":
            self.run_in_background_checkbox.setEnabled(False)
            self.run_in_background_checkbox.setToolTip("This feature is only available on Windows.")
        info = QLabel("Adds a tray icon that starts with Windows, allowing PuffinPyEditor to open faster.")
        info.setWordWrap(True); info.setStyleSheet("font-size: 9pt; color: grey;")
        system_layout.addRow(self.run_in_background_checkbox); system_layout.addRow(info)
        layout.addStretch()
        self.tab_widget.addTab(tab, qta.icon('fa5s.desktop'), "System")

    def _manage_startup_shortcut(self, create: bool):
        if not (shortcut_path := get_startup_shortcut_path()): return
        try:
            if create:
                if not getattr(sys, 'frozen', False):
                    QMessageBox.warning(self, "Developer Mode", "Startup feature only works in a packaged application.")
                    self.run_in_background_checkbox.setChecked(False); return
                install_dir = os.path.dirname(sys.executable)
                target_path = os.path.join(install_dir, "PuffinPyTray.exe")
                if not os.path.exists(target_path):
                    QMessageBox.warning(self, "File Not Found", f"Could not find PuffinPyTray.exe in {install_dir}")
                    self.run_in_background_checkbox.setChecked(False); return
                with winshell.shortcut(shortcut_path) as s:
                    s.path, s.description, s.working_directory = target_path, "PuffinPyEditor Background App", install_dir
                log.info(f"Created startup shortcut: {shortcut_path}")
            elif os.path.exists(shortcut_path):
                os.remove(shortcut_path)
                log.info(f"Removed startup shortcut: {shortcut_path}")
        except Exception as e:
            log.error(f"Failed to manage startup shortcut: {e}")
            QMessageBox.critical(self, "Error", f"Could not modify startup shortcut.\n{e}")
            self.run_in_background_checkbox.setChecked(not create)

    def _create_source_control_tab(self):
        tab = QWidget(); top_layout = QVBoxLayout(tab); top_layout.setSpacing(15)
        gh_form_layout = self._create_layout_in_groupbox("GitHub Account", top_layout)
        gh_form_layout.setRowWrapPolicy(QFormLayout.RowWrapPolicy.WrapAllRows)
        auth_widget = QWidget(); auth_layout = QHBoxLayout(auth_widget); auth_layout.setContentsMargins(0,0,0,0)
        self.auth_status_label = QLabel("Not logged in.")
        self.auth_button = QPushButton("Login to GitHub"); self.logout_button = QPushButton("Logout"); self.logout_button.hide()
        auth_layout.addWidget(self.auth_status_label, 1); auth_layout.addWidget(self.auth_button); auth_layout.addWidget(self.logout_button)
        gh_form_layout.addRow("Status:", auth_widget)
        git_form_layout = self._create_layout_in_groupbox("Local Git Configuration", top_layout)
        self.git_user_name_edit = QLineEdit(); self.git_user_name_edit.setPlaceholderText("Name for commits")
        self.git_user_email_edit = QLineEdit(); self.git_user_email_edit.setPlaceholderText("Email for commits")
        branch_fix_button = QPushButton("Set Default to 'main' Globally"); branch_btn_layout = QHBoxLayout()
        branch_btn_layout.setContentsMargins(0,0,0,0); branch_btn_layout.addWidget(branch_fix_button); branch_btn_layout.addStretch()
        git_form_layout.addRow("Author Name:", self.git_user_name_edit)
        git_form_layout.addRow("Author Email:", self.git_user_email_edit)
        git_form_layout.addRow("Default Branch:", branch_btn_layout)
        build_form_layout = self._create_layout_in_groupbox("Build Tools", top_layout)
        nsis_path_layout = QHBoxLayout()
        self.nsis_path_edit = QLineEdit(); self.nsis_path_edit.setPlaceholderText("e.g., C:\\Program Files (x86)\\NSIS\\makensis.exe")
        browse_nsis_button = QPushButton("Browse..."); browse_nsis_button.clicked.connect(self._browse_for_nsis)
        nsis_path_layout.addWidget(self.nsis_path_edit, 1); nsis_path_layout.addWidget(browse_nsis_button)
        build_form_layout.addRow("NSIS `makensis.exe` Path:", nsis_path_layout)
        self.cleanup_build_checkbox = QCheckBox("Automatically clean up temporary build files")
        self.cleanup_build_checkbox.setToolTip("Deletes the 'build/' folder after a successful installer creation.")
        build_form_layout.addRow("", self.cleanup_build_checkbox)
        update_group = QGroupBox("Plugin Distribution & Update Repositories"); update_layout = QVBoxLayout(update_group)
        splitter = QSplitter(Qt.Orientation.Horizontal); update_layout.addWidget(splitter, 1)
        left_pane, right_pane = self._create_repo_management_widgets()
        splitter.addWidget(left_pane); splitter.addWidget(right_pane); splitter.setSizes([250, 400])
        top_layout.addWidget(update_group, 1)
        self.tab_widget.addTab(tab, qta.icon('fa5b.git-alt'), "Source Control")
        self.auth_button.clicked.connect(self.github_manager.start_device_flow)
        self.logout_button.clicked.connect(self._logout_github)
        branch_fix_button.clicked.connect(self.git_manager.set_default_branch_to_main)

    def _browse_for_nsis(self):
        if path := QFileDialog.getOpenFileName(self, "Select makensis.exe", "", "Executable (makensis.exe)")[0]:
            self.nsis_path_edit.setText(path)

    def _create_repo_management_widgets(self) -> tuple[QWidget, QWidget]:
        left_pane, right_pane = QWidget(), QWidget(); left_layout = QVBoxLayout(left_pane)
        self.right_pane_layout = QVBoxLayout(right_pane); self.repo_list_widget = QListWidget()
        repo_btn_layout = QHBoxLayout(); create_repo_btn, add_repo_btn, remove_repo_btn = QPushButton("Create..."), QPushButton("Add..."), QPushButton("Remove")
        repo_btn_layout.addStretch(); repo_btn_layout.addWidget(create_repo_btn); repo_btn_layout.addWidget(add_repo_btn); repo_btn_layout.addWidget(remove_repo_btn)
        left_layout.addWidget(self.repo_list_widget); left_layout.addLayout(repo_btn_layout)
        self.repo_form_widget = QWidget(); repo_form_layout = QFormLayout(self.repo_form_widget)
        self.repo_name_edit, self.repo_owner_edit, self.repo_repo_edit = QLineEdit(), QLineEdit(), QLineEdit()
        self.repo_active_checkbox = QCheckBox("Set as Primary (for updates & publishing)")
        repo_form_layout.addRow("Friendly Name:", self.repo_name_edit)
        repo_form_layout.addRow("Owner (e.g., 'Stelliro'):", self.repo_owner_edit)
        repo_form_layout.addRow("Repository (e.g., 'PuffinPyEditor'):", self.repo_repo_edit)
        repo_form_layout.addRow("", self.repo_active_checkbox)
        self.repo_placeholder_label = QLabel("\nSelect or add a repository to configure it.")
        self.repo_placeholder_label.setAlignment(Qt.AlignmentFlag.AlignCenter); self.repo_placeholder_label.setStyleSheet("color: grey;")
        self.right_pane_layout.addWidget(self.repo_placeholder_label, 1); self.right_pane_layout.addWidget(self.repo_form_widget)
        create_repo_btn.clicked.connect(self._action_create_repo); add_repo_btn.clicked.connect(self._action_add_repo)
        remove_repo_btn.clicked.connect(self._action_remove_repo); self.repo_list_widget.currentItemChanged.connect(self._on_repo_selection_changed)
        self.repo_active_checkbox.toggled.connect(self._on_active_checkbox_toggled)
        return left_pane, right_pane

    def _action_create_repo(self):
        if not (name := QInputDialog.getText(self, "Create New Repository", "Enter a name for the new repository:")[0]): return
        desc = QInputDialog.getText(self, "Create New Repository", "Description (optional):")[0]
        is_private = QMessageBox.question(self, "Visibility", "Make this repository private?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.No) == QMessageBox.StandardButton.Yes
        self.github_manager.create_repo(name, desc, is_private)
        QMessageBox.information(self, "In Progress", f"Attempting to create '{name}' on GitHub...")

    def _populate_git_config_fields(self, name: str, email: str):
        log.debug(f"Populating Git config: Name='{name}', Email='{email}'")
        self.original_git_config = {'name': name, 'email': email}
        self.git_user_name_edit.setText(name); self.git_user_email_edit.setText(email)

    def _handle_git_success(self, message: str, data: dict):
        if "Default branch" in message: QMessageBox.information(self, "Success", message)

    def _logout_github(self):
        self.github_manager.logout(); self._update_auth_status()

    def _update_auth_status(self):
        user, is_logged_in = self.github_manager.get_authenticated_user(), False
        if user: is_logged_in = True
        self.auth_status_label.setText(f"Logged in as: <b>{user}</b>" if is_logged_in else "Not logged in.")
        self.auth_button.setVisible(not is_logged_in); self.logout_button.setVisible(is_logged_in)

    def _on_device_code_ready(self, data: dict):
        self.auth_dialog = AuthDialog(data['user_code'], data['verification_uri'], self)
        self.auth_dialog.show()
        self.github_manager.poll_for_token(data['device_code'], data['interval'], data['expires_in'])

    def _on_auth_successful(self, username: str):
        if self.auth_dialog: self.auth_dialog.accept()
        QMessageBox.information(self, "Success", f"Successfully logged in as {username}.")
        self._update_auth_status()
        if not self.git_user_name_edit.text(): self.git_user_name_edit.setText(username)
        if not self.git_user_email_edit.text(): self.git_user_email_edit.setPlaceholderText(f"e.g., {username}@users.noreply.github.com")

    def _on_auth_failed(self, error: str):
        if self.auth_dialog: self.auth_dialog.reject()
        QMessageBox.critical(self, "Authentication Failed", error); self._update_auth_status()

    def _on_auth_polling_lapsed(self):
        if self.auth_dialog: self.auth_dialog.reject()
        QMessageBox.warning(self, "Login Expired", "The login code has expired. Please try again."); self._update_auth_status()

    def _on_repo_selection_changed(self, current: QListWidgetItem, previous: QListWidgetItem):
        if previous: self._save_repo_form_to_staged()
        if not current: self._clear_repo_form()
        else: self._load_staged_to_repo_form(current.data(Qt.ItemDataRole.UserRole))

    def _on_active_checkbox_toggled(self, checked: bool):
        if not self.current_repo_id_in_form: return
        self.staged_active_repo_id = self.current_repo_id_in_form if checked else None
        self._populate_repo_list(select_repo_id=self.current_repo_id_in_form)
        self._on_ui_setting_changed()

    def _save_repo_form_to_staged(self):
        if not self.current_repo_id_in_form: return
        if repo := next((r for r in self.staged_repos if r.get("id") == self.current_repo_id_in_form), None):
            repo.update({'name': self.repo_name_edit.text().strip(), 'owner': self.repo_owner_edit.text().strip(), 'repo': self.repo_repo_edit.text().strip()})

    def _load_staged_to_repo_form(self, repo_id: str):
        if not (repo_data := next((r for r in self.staged_repos if r.get("id") == repo_id), None)):
            self._clear_repo_form(); return
        self.current_repo_id_in_form = repo_id
        for w in [self.repo_name_edit, self.repo_owner_edit, self.repo_repo_edit, self.repo_active_checkbox]: w.blockSignals(True)
        self.repo_name_edit.setText(repo_data.get("name", "")); self.repo_owner_edit.setText(repo_data.get("owner", ""))
        self.repo_repo_edit.setText(repo_data.get("repo", "")); self.repo_active_checkbox.setChecked(self.staged_active_repo_id == repo_id)
        for w in [self.repo_name_edit, self.repo_owner_edit, self.repo_repo_edit, self.repo_active_checkbox]: w.blockSignals(False)
        self.repo_placeholder_label.hide(); self.repo_form_widget.show()

    def _action_add_repo(self):
        self._save_repo_form_to_staged()
        new_id = str(uuid.uuid4())
        self.staged_repos.append({"id": new_id, "name": "New Repository", "owner": "", "repo": ""})
        self._populate_repo_list(select_repo_id=new_id)
        self.repo_name_edit.setFocus(); self.repo_name_edit.selectAll()
        self._on_ui_setting_changed()

    def _action_remove_repo(self):
        if not (item := self.repo_list_widget.currentItem()): return
        repo_id = item.data(Qt.ItemDataRole.UserRole)
        repo = next((r for r in self.staged_repos if r.get("id") == repo_id), None)
        repo_name = f"'{repo.get('owner')}/{repo.get('repo')}'" if repo else f"'{item.text()}'"
        if QMessageBox.question(self, "Confirm Remove", f"Remove {repo_name} from this list? This does not delete it from GitHub.", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.Cancel) == QMessageBox.StandardButton.Yes:
            self.staged_repos = [r for r in self.staged_repos if r.get("id") != repo_id]
            if self.staged_active_repo_id == repo_id: self.staged_active_repo_id = None
            self._populate_repo_list(); self._on_ui_setting_changed()

    def _populate_repo_list(self, select_repo_id: Optional[str] = None):
        self.repo_list_widget.blockSignals(True); self.repo_list_widget.clear(); item_to_select = None
        for repo in sorted(self.staged_repos, key=lambda r: r.get('name', '').lower()):
            item = QListWidgetItem(repo.get("name")); item.setData(Qt.ItemDataRole.UserRole, repo.get("id"))
            if repo.get("id") == self.staged_active_repo_id: item.setIcon(qta.icon('fa5s.star', color='gold'))
            self.repo_list_widget.addItem(item)
            if repo.get("id") == select_repo_id: item_to_select = item
        self.repo_list_widget.blockSignals(False)
        if item_to_select: self.repo_list_widget.setCurrentItem(item_to_select)
        else: self._clear_repo_form()

    def _clear_repo_form(self):
        self.current_repo_id_in_form = None
        for w in [self.repo_name_edit, self.repo_owner_edit, self.repo_repo_edit]: w.clear()
        self.repo_active_checkbox.setChecked(False); self.repo_placeholder_label.show(); self.repo_form_widget.hide()

    def _create_plugins_tab(self):
        tab_container = QWidget(); layout = QVBoxLayout(tab_container)
        plugins_tabs = QTabWidget()
        plugins_tabs.addTab(self._create_plugins_manage_tab(), qta.icon('fa5s.tasks'), "Manage")
        plugins_tabs.addTab(self._create_plugins_install_tab(), qta.icon('fa5s.plus-circle'), "Install / Uninstall")
        plugins_tabs.addTab(self._create_plugins_options_tab(), qta.icon('fa5s.cogs'), "Options")
        layout.addWidget(plugins_tabs)
        self.tab_widget.addTab(tab_container, qta.icon('fa5s.puzzle-piece'), "Plugins")
    
    def _populate_all_plugin_lists(self):
        self._populate_manage_plugins_list()
        self._populate_install_plugins_list()
        self._populate_options_plugins_list()

    # --- Plugin Management Tab ---
    def _create_plugins_manage_tab(self) -> QWidget:
        widget = QWidget(); layout = QVBoxLayout(widget); layout.setSpacing(10)
        self.manage_plugins_list = QListWidget()
        self.manage_plugins_list.itemChanged.connect(self._on_plugin_enabled_changed)
        layout.addWidget(self.manage_plugins_list)
        buttons_layout = QHBoxLayout()
        reload_button = QPushButton("Reload Selected"); reload_button.setIcon(qta.icon('fa5s.sync-alt'))
        reload_all_button = QPushButton("Reload All Plugins"); reload_all_button.setIcon(qta.icon('fa5s.sync-alt'))
        buttons_layout.addStretch()
        buttons_layout.addWidget(reload_button)
        buttons_layout.addWidget(reload_all_button)
        layout.addLayout(buttons_layout)
        reload_button.clicked.connect(self._reload_selected_plugin)
        reload_all_button.clicked.connect(self._reload_all_plugins)
        return widget

    def _populate_manage_plugins_list(self):
        self.manage_plugins_list.blockSignals(True); self.manage_plugins_list.clear()
        for plugin in sorted(self.plugin_manager.get_all_plugins(), key=lambda p: p.name.lower()):
            item = QListWidgetItem(f"{plugin.name} v{plugin.version}"); item.setData(Qt.ItemDataRole.UserRole, plugin.id)
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            if plugin.is_core: item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsUserCheckable)
            item.setCheckState(Qt.CheckState.Checked if plugin.enabled else Qt.CheckState.Unchecked)
            item.setToolTip(f"ID: {plugin.id}\nSource: {plugin.source_type}\nStatus: {plugin.status_reason}")
            self.manage_plugins_list.addItem(item)
        self.manage_plugins_list.blockSignals(False)
    
    def _on_plugin_enabled_changed(self, item: QListWidgetItem):
        plugin_id = item.data(Qt.ItemDataRole.UserRole)
        is_enabled = item.checkState() == Qt.CheckState.Checked
        if is_enabled: self.plugin_manager.enable_plugin(plugin_id)
        else: self.plugin_manager.disable_plugin(plugin_id)
        self.restart_needed = True
        QMessageBox.information(self, "Reload Recommended", f"Plugin '{item.text()}' state changed. A restart or reload is recommended.")
        self._populate_all_plugin_lists()

    def _reload_selected_plugin(self):
        if not (item := self.manage_plugins_list.currentItem()): return
        plugin_id = item.data(Qt.ItemDataRole.UserRole)
        self.plugin_manager.reload_plugin(plugin_id)
        QMessageBox.information(self, "Success", f"Plugin '{item.text()}' reloaded.")
        self._populate_all_plugin_lists()
    
    def _reload_all_plugins(self):
        self.plugin_manager.discover_and_load_plugins()
        QMessageBox.information(self, "Success", "All plugins have been reloaded.")
        self._populate_all_plugin_lists()

    # --- Plugin Install/Uninstall Tab ---
    def _create_plugins_install_tab(self) -> QWidget:
        widget = QWidget(); layout = QVBoxLayout(widget)
        splitter = QSplitter(Qt.Orientation.Vertical)
        
        remote_group = QGroupBox("Find & Install New Plugins")
        remote_layout = QVBoxLayout(remote_group)
        repo_layout = QHBoxLayout()
        repo_layout.addWidget(QLabel("Plugin Distro Repo:"))
        self.plugins_repo_edit = QLineEdit(); self.plugins_repo_edit.setPlaceholderText("user/repository")
        self.fetch_plugins_button = QPushButton("Fetch"); self.fetch_plugins_button.setIcon(qta.icon('fa5s.cloud-download-alt'))
        repo_layout.addWidget(self.plugins_repo_edit, 1); repo_layout.addWidget(self.fetch_plugins_button)
        remote_layout.addLayout(repo_layout)
        self.remote_plugins_list = QListWidget()
        remote_layout.addWidget(self.remote_plugins_list)
        remote_buttons_layout = QHBoxLayout()
        self.install_remote_button = QPushButton("Install Selected"); self.install_remote_button.setIcon(qta.icon('fa5s.download'))
        self.install_remote_button.setEnabled(False)
        install_file_button = QPushButton("Install from File..."); install_file_button.setIcon(qta.icon('fa5s.file-archive'))
        remote_buttons_layout.addStretch()
        remote_buttons_layout.addWidget(self.install_remote_button); remote_buttons_layout.addWidget(install_file_button)
        remote_layout.addLayout(remote_buttons_layout)
        splitter.addWidget(remote_group)

        installed_group = QGroupBox("Installed Plugins")
        installed_layout = QVBoxLayout(installed_group)
        self.installed_plugins_list = QListWidget()
        self.uninstall_plugin_button = QPushButton("Uninstall Selected"); self.uninstall_plugin_button.setIcon(qta.icon('fa5s.trash-alt', color='crimson'))
        self.uninstall_plugin_button.setEnabled(False)
        installed_layout.addWidget(self.installed_plugins_list)
        installed_layout.addWidget(self.uninstall_plugin_button, 0, Qt.AlignmentFlag.AlignRight)
        splitter.addWidget(installed_group)
        
        splitter.setSizes([350, 250])
        layout.addWidget(splitter)
        
        self.fetch_plugins_button.clicked.connect(self._fetch_remote_plugins)
        install_file_button.clicked.connect(self._install_plugin_from_file)
        self.install_remote_button.clicked.connect(self._install_selected_remote_plugin)
        self.uninstall_plugin_button.clicked.connect(self._uninstall_selected_plugin)
        self.installed_plugins_list.currentItemChanged.connect(self._on_installed_plugin_selected)
        self.remote_plugins_list.currentItemChanged.connect(self._on_remote_plugin_selected)
        return widget

    def _populate_install_plugins_list(self):
        self.installed_plugins_list.clear()
        for plugin in sorted(self.plugin_manager.get_all_plugins(), key=lambda p: p.name.lower()):
            item_text = f"{plugin.name} v{plugin.version}{' (Core)' if plugin.is_core else ''}"
            list_item = QListWidgetItem(item_text); list_item.setData(Qt.ItemDataRole.UserRole, plugin)
            if plugin.is_core: list_item.setForeground(QColor("grey"))
            self.installed_plugins_list.addItem(list_item)
    
    def _on_installed_plugin_selected(self, item: QListWidgetItem):
        is_core = item.data(Qt.ItemDataRole.UserRole).is_core if item else True
        self.uninstall_plugin_button.setEnabled(not is_core)
        self.uninstall_plugin_button.setToolTip("Core plugins cannot be uninstalled." if is_core else "Uninstall selected plugin.")

    def _on_remote_plugin_selected(self, item: QListWidgetItem):
        can_install = item is not None and bool(item.flags() & Qt.ItemFlag.ItemIsEnabled)
        self.install_remote_button.setEnabled(can_install)

    def _fetch_remote_plugins(self):
        if not (repo_path := self.plugins_repo_edit.text().strip()) or '/' not in repo_path:
            QMessageBox.warning(self, "Invalid Repo", "Enter a valid GitHub repo (user/repo)."); return
        self.remote_plugins_list.clear(); self.remote_plugins_list.addItem("Fetching...")
        self.fetch_plugins_button.setEnabled(False); self.install_remote_button.setEnabled(False)
        self.github_manager.fetch_plugin_index(repo_path)

    def _on_plugin_index_ready(self, plugin_list: list):
        self.fetch_plugins_button.setEnabled(True); self.remote_plugins_list.clear()
        installed_ids = {p.id for p in self.plugin_manager.get_all_plugins()}
        for info in plugin_list:
            is_installed = info.get('id') in installed_ids
            item = QListWidgetItem(f"{info.get('name', 'N/A')} v{info.get('version', 'N/A')}{' (Installed)' if is_installed else ''}")
            item.setToolTip(info.get("description", "No description.")); item.setData(Qt.ItemDataRole.UserRole, info)
            if is_installed: item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEnabled); item.setForeground(QColor("grey"))
            self.remote_plugins_list.addItem(item)

    def _install_selected_remote_plugin(self):
        if item := self.remote_plugins_list.currentItem():
            self._install_plugin_from_url(item.data(Qt.ItemDataRole.UserRole).get("download_url"))

    def _install_plugin_from_url(self, url: str):
        if not url: QMessageBox.critical(self, "Error", "Plugin has no download URL."); return
        try:
            with requests.get(url, stream=True, timeout=30) as r, tempfile.NamedTemporaryFile(delete=False, suffix=".zip") as tmp:
                r.raise_for_status()
                for chunk in r.iter_content(8192): tmp.write(chunk)
                zip_path = tmp.name
            success, msg = self.plugin_manager.install_plugin_from_zip(zip_path)
            QMessageBox.information(self, "Success" if success else "Failed", msg)
            if success: self.restart_needed = True; self._populate_all_plugin_lists(); self._fetch_remote_plugins()
        except requests.RequestException as e: QMessageBox.critical(self, "Download Failed", f"Could not download: {e}")
        finally:
            if 'zip_path' in locals() and os.path.exists(zip_path): os.remove(zip_path)

    def _install_plugin_from_file(self):
        if not (filepath := QFileDialog.getOpenFileName(self, "Select Plugin Archive", "", "ZIP Files (*.zip)")[0]): return
        success, message = self.plugin_manager.install_plugin_from_zip(filepath)
        QMessageBox.information(self, "Success" if success else "Failed", message)
        if success: self.restart_needed = True; self._populate_all_plugin_lists()

    def _uninstall_selected_plugin(self):
        if not (item := self.installed_plugins_list.currentItem()): return
        plugin = item.data(Qt.ItemDataRole.UserRole)
        if plugin.is_core: QMessageBox.information(self, "Core Plugin", "Core plugins cannot be uninstalled."); return
        if QMessageBox.question(self, "Confirm Uninstall", f"Uninstall '{plugin.name}'?") == QMessageBox.StandardButton.Yes:
            success, message = self.plugin_manager.uninstall_plugin(plugin.id)
            QMessageBox.information(self, "Success" if success else "Failed", message)
            if success: self.restart_needed = True; self._populate_all_plugin_lists()

    # --- Plugin Options Tab ---
    def _create_plugins_options_tab(self) -> QWidget:
        widget = QWidget(); layout = QHBoxLayout(widget)
        splitter = QSplitter(Qt.Orientation.Horizontal)
        self.options_plugins_list = QListWidget()
        self.options_stack = QStackedWidget()
        
        # Placeholder widget for when no options are available
        self.no_options_label = QLabel("Select a plugin to see its options.\nNot all plugins are configurable.")
        self.no_options_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.no_options_label.setStyleSheet("color: grey;")
        self.options_stack.addWidget(self.no_options_label)
        
        splitter.addWidget(self.options_plugins_list)
        splitter.addWidget(self.options_stack)
        splitter.setSizes([200, 450])
        layout.addWidget(splitter)

        self.options_plugins_list.currentItemChanged.connect(self._on_options_plugin_selected)
        return widget

    def _populate_options_plugins_list(self):
        self.options_plugins_list.clear()
        self.options_stack.blockSignals(True)
        # Clear old option widgets, keeping the placeholder
        while self.options_stack.count() > 1:
            self.options_stack.removeWidget(self.options_stack.widget(1))

        plugins_with_options = []
        for plugin in self.plugin_manager.get_all_plugins():
            if plugin.instance and hasattr(plugin.instance, 'get_options_widget'):
                plugins_with_options.append(plugin)
        
        plugins_with_options.sort(key=lambda p: p.name.lower())

        for plugin in plugins_with_options:
            item = QListWidgetItem(plugin.name)
            options_widget = plugin.instance.get_options_widget()
            if options_widget:
                idx = self.options_stack.addWidget(options_widget)
                item.setData(Qt.ItemDataRole.UserRole, idx) # Store stack index
                self.options_plugins_list.addItem(item)
        
        self.options_stack.blockSignals(False)
        self.options_stack.setCurrentIndex(0)

    def _on_options_plugin_selected(self, item: QListWidgetItem):
        if item:
            stack_index = item.data(Qt.ItemDataRole.UserRole)
            self.options_stack.setCurrentIndex(stack_index)
        else:
            self.options_stack.setCurrentIndex(0) # Show placeholder
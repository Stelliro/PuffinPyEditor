# PuffinPyEditor/ui/dialogs/preferences_dialog.py
import uuid
import sys
import os
import tempfile
import requests
from typing import Optional, Any
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QTabWidget, QWidget,
                             QLabel, QComboBox, QSpinBox, QCheckBox, QPushButton, QLineEdit,
                             QDialogButtonBox, QFontComboBox, QSplitter, QFormLayout,
                             QListWidget, QListWidgetItem, QMessageBox, QGroupBox, QFileDialog,
                             QTreeWidget, QTreeWidgetItem, QHeaderView)
from PyQt6.QtGui import QFont, QDesktopServices, QColor
from PyQt6.QtCore import Qt, QSize, pyqtSignal, QUrl

if sys.platform == "win32":
    import winshell

import qtawesome as qta
from utils.logger import log
from app_core.settings_manager import settings_manager, DEFAULT_SETTINGS
from app_core.theme_manager import theme_manager
from app_core.github_manager import GitHubManager
from app_core.source_control_manager import SourceControlManager
from app_core.plugin_manager import PluginManager
from .theme_editor_dialog import ThemeEditorDialog

DEFAULT_SETTINGS["nsis_path"] = ""


def get_startup_shortcut_path() -> Optional[str]:
    if sys.platform != "win32": return None
    try:
        return os.path.join(winshell.startup(), "PuffinPyTray.lnk")
    except Exception as e:
        log.error(f"Could not get startup folder path: {e}"); return None


class AuthDialog(QDialog):
    def __init__(self, user_code: str, verification_uri: str, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setWindowTitle("GitHub Device Authorization")
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Please authorize PuffinPyEditor in your browser."))
        url_label = QLabel(f"1. Open: <a href='{verification_uri}'>{verification_uri}</a>")
        url_label.setOpenExternalLinks(True)
        layout.addWidget(url_label)
        layout.addWidget(QLabel("2. Enter this one-time code:"))
        code_label = QLineEdit(user_code);
        code_label.setReadOnly(True)
        code_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        code_label.setFont(QFont("Consolas", 14, QFont.Weight.Bold))
        layout.addWidget(code_label)
        QDesktopServices.openUrl(QUrl(verification_uri))
        self.setFixedSize(self.sizeHint())


class PreferencesDialog(QDialog):
    settings_changed_for_editor_refresh = pyqtSignal()
    theme_changed_signal = pyqtSignal(str)

    def __init__(self, git_manager: SourceControlManager, github_manager: GitHubManager,
                 plugin_manager: PluginManager, parent: Optional[QWidget] = None):
        super().__init__(parent)
        log.info("PreferencesDialog initializing...")
        self.setWindowTitle("Preferences")
        self.setMinimumSize(QSize(750, 650))
        self.git_manager, self.github_manager, self.plugin_manager = git_manager, github_manager, plugin_manager
        self.original_settings: dict[str, Any] = {};
        self.original_git_config: dict[str, str] = {}
        self.staged_repos: list[dict] = [];
        self.staged_active_repo_id: Optional[str] = None
        self.current_repo_id_in_form: Optional[str] = None;
        self.auth_dialog: Optional[AuthDialog] = None
        self.theme_editor_dialog_instance: Optional[ThemeEditorDialog] = None;
        self.restart_needed = False
        self.main_layout = QVBoxLayout(self);
        self.tab_widget = QTabWidget();
        self.main_layout.addWidget(self.tab_widget)
        self._create_tabs();
        self._create_button_box();
        self._connect_global_signals()
        log.info("PreferencesDialog initialized.")

    def _create_tabs(self):
        self._create_appearance_tab();
        self._create_editor_tab();
        self._create_run_tab()
        self._create_system_tab();
        self._create_source_control_tab();
        self._create_plugins_tab()

    def _create_button_box(self):
        self.button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel | QDialogButtonBox.StandardButton.Apply)
        self.main_layout.addWidget(self.button_box)

    def _connect_global_signals(self):
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        self.button_box.button(QDialogButtonBox.StandardButton.Apply).clicked.connect(self.apply_settings)
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
                "id": new_repo_id,
                "name": data.get("name"),
                "owner": owner,
                "repo": repo_name
            }
            self.staged_repos.append(new_repo)
            QMessageBox.information(self, "Success", f"Repository '{repo_name}' created on GitHub.")
            self._populate_repo_list(select_repo_id=new_repo_id)
            self._on_ui_setting_changed()

    def showEvent(self, event):
        self._load_settings_into_dialog();
        self.git_manager.get_git_config();
        self._update_auth_status()
        self._populate_installed_plugins_list();
        self.button_box.button(QDialogButtonBox.StandardButton.Apply).setEnabled(False)
        self.restart_needed = False;
        super().showEvent(event)

    def _load_settings_into_dialog(self):
        self.original_settings = settings_manager.settings.copy()
        self._repopulate_theme_combo();
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
        self.staged_active_repo_id = settings_manager.get("active_update_repo_id");
        self._populate_repo_list()
        self.plugins_repo_edit.setText(settings_manager.get("plugins_distro_repo", "Stelliro/puffin-plugins"))
        self._connect_ui_changed_signals()

    def _connect_ui_changed_signals(self):
        widgets_to_connect = self.findChildren((QComboBox, QSpinBox, QCheckBox, QFontComboBox, QLineEdit))
        for widget in widgets_to_connect:
            if isinstance(widget, QComboBox):
                widget.currentIndexChanged.connect(self._on_ui_setting_changed)
            elif isinstance(widget, QFontComboBox):
                widget.currentFontChanged.connect(self._on_ui_setting_changed)
            elif isinstance(widget, QSpinBox):
                widget.valueChanged.connect(self._on_ui_setting_changed)
            elif isinstance(widget, QCheckBox):
                widget.stateChanged.connect(self._on_ui_setting_changed)
            elif isinstance(widget, QLineEdit):
                widget.textChanged.connect(self._on_ui_setting_changed)

    def _on_ui_setting_changed(self, *args):
        self.button_box.button(QDialogButtonBox.StandardButton.Apply).setEnabled(True)

    def apply_settings(self):
        if not self.button_box.button(QDialogButtonBox.StandardButton.Apply).isEnabled(): return
        if sys.platform == "win32" and self.run_in_background_checkbox.isChecked() != self.original_settings.get(
                "run_in_background", False):
            self._manage_startup_shortcut(self.run_in_background_checkbox.isChecked())
        new_name, new_email = self.git_user_name_edit.text().strip(), self.git_user_email_edit.text().strip()
        if new_name != self.original_git_config.get('name') or new_email != self.original_git_config.get('email'):
            self.git_manager.set_git_config(new_name, new_email);
            self.original_git_config = {'name': new_name, 'email': new_email}
        self._save_repo_form_to_staged()
        settings_manager.set("last_theme_id", self.theme_combo.currentData(), False)
        settings_manager.set("font_family", self.font_family_combo.currentFont().family(), False)
        settings_manager.set("font_size", self.font_size_spinbox.value(), False)
        settings_manager.set("show_line_numbers", self.show_line_numbers_checkbox.isChecked(), False)
        settings_manager.set("word_wrap", self.word_wrap_checkbox.isChecked(), False)
        settings_manager.set("show_indentation_guides", self.show_indent_guides_checkbox.isChecked(), False)
        settings_manager.set("indent_style", self.indent_style_combo.currentText().lower(), False)
        settings_manager.set("indent_width", self.indent_width_spinbox.value(), False)
        settings_manager.set("auto_save_enabled", self.auto_save_checkbox.isChecked(), False)
        settings_manager.set("auto_save_delay_seconds", self.auto_save_delay_spinbox.value(), False)
        settings_manager.set("max_recent_files", self.max_recent_files_spinbox.value(), False)
        settings_manager.set("python_interpreter_path", self.python_path_edit.text().strip(), False)
        settings_manager.set("run_in_background", self.run_in_background_checkbox.isChecked(), False)
        settings_manager.set("nsis_path", self.nsis_path_edit.text().strip(), False)
        settings_manager.set("cleanup_after_build", self.cleanup_build_checkbox.isChecked(), False)
        settings_manager.set("source_control_repos", self.staged_repos, False)
        settings_manager.set("active_update_repo_id", self.staged_active_repo_id, False)
        settings_manager.set("plugins_distro_repo", self.plugins_repo_edit.text().strip(), False)
        settings_manager.save()
        self.theme_changed_signal.emit(self.theme_combo.currentData());
        self.settings_changed_for_editor_refresh.emit()
        self.original_settings = settings_manager.settings.copy()
        self.button_box.button(QDialogButtonBox.StandardButton.Apply).setEnabled(False)
        if self.restart_needed:
            QMessageBox.information(self, "Restart Required",
                                    "Some changes require a restart of the application to take effect.")
            self.restart_needed = False
        log.info("Applied settings from Preferences dialog.")

    def accept(self):
        if self.button_box.button(QDialogButtonBox.StandardButton.Apply).isEnabled(): self.apply_settings()
        super().accept()

    def reject(self):
        if self.auth_dialog and self.auth_dialog.isVisible(): self.auth_dialog.reject()
        if self.button_box.button(QDialogButtonBox.StandardButton.Apply).isEnabled():
            if QMessageBox.question(self, "Unsaved Changes", "Discard unsaved changes?",
                                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                    QMessageBox.StandardButton.No) == QMessageBox.StandardButton.No: return
        if self.theme_combo.currentData() != self.original_settings.get("last_theme_id"):
            self.theme_changed_signal.emit(self.original_settings.get("last_theme_id"))
        super().reject()

    def _create_appearance_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        theme_group = QGroupBox("Theming")
        theme_layout = QFormLayout(theme_group)
        self.theme_combo = QComboBox()
        self.edit_themes_button = QPushButton("Customize Themes...")
        self.edit_themes_button.clicked.connect(self._open_theme_editor_dialog)
        theme_layout.addRow("Theme:", self.theme_combo)
        theme_layout.addRow("", self.edit_themes_button)
        layout.addWidget(theme_group)
        
        font_group = QGroupBox("Editor Font")
        font_layout = QFormLayout(font_group)
        self.font_family_combo = QFontComboBox()
        self.font_size_spinbox = QSpinBox()
        self.font_size_spinbox.setRange(6, 72)
        font_layout.addRow("Font Family:", self.font_family_combo)
        font_layout.addRow("Font Size:", self.font_size_spinbox)
        layout.addWidget(font_group)
        
        layout.addStretch()
        self.tab_widget.addTab(tab, "Appearance")

    def _repopulate_theme_combo(self):
        current_id = settings_manager.get("last_theme_id");
        self.theme_combo.blockSignals(True);
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
        
        display_group = QGroupBox("Display")
        display_layout = QFormLayout(display_group)
        display_layout.setRowWrapPolicy(QFormLayout.RowWrapPolicy.WrapAllRows)
        self.show_line_numbers_checkbox = QCheckBox("Show line numbers")
        self.word_wrap_checkbox = QCheckBox("Enable word wrap")
        self.show_indent_guides_checkbox = QCheckBox("Show indentation guides")
        display_layout.addRow(self.show_line_numbers_checkbox)
        display_layout.addRow(self.word_wrap_checkbox)
        display_layout.addRow(self.show_indent_guides_checkbox)
        layout.addWidget(display_group)

        indent_group = QGroupBox("Indentation")
        indent_layout = QFormLayout(indent_group)
        self.indent_style_combo = QComboBox()
        self.indent_style_combo.addItems(["Spaces", "Tabs"])
        self.indent_width_spinbox = QSpinBox()
        self.indent_width_spinbox.setRange(1, 16)
        indent_layout.addRow("Indent Using:", self.indent_style_combo)
        indent_layout.addRow("Indent/Tab Width:", self.indent_width_spinbox)
        layout.addWidget(indent_group)

        file_group = QGroupBox("File Handling")
        file_layout = QFormLayout(file_group)
        self.auto_save_checkbox = QCheckBox("Enable auto-save")
        self.auto_save_delay_spinbox = QSpinBox()
        self.auto_save_delay_spinbox.setRange(1, 60)
        self.auto_save_delay_spinbox.setSuffix(" seconds")
        self.max_recent_files_spinbox = QSpinBox()
        self.max_recent_files_spinbox.setRange(1, 50)
        file_layout.addRow(self.auto_save_checkbox)
        file_layout.addRow("Auto-Save Delay:", self.auto_save_delay_spinbox)
        file_layout.addRow("Max Recent Files:", self.max_recent_files_spinbox)
        layout.addWidget(file_group)
        
        layout.addStretch()
        self.tab_widget.addTab(tab, "Editor")

    def _create_run_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        run_group = QGroupBox("Execution Environment")
        run_layout = QFormLayout(run_group)
        run_layout.setRowWrapPolicy(QFormLayout.RowWrapPolicy.WrapAllRows)
        path_layout = QHBoxLayout()
        self.python_path_edit = QLineEdit()
        browse_button = QPushButton("Browse...")
        browse_button.clicked.connect(self._browse_for_python)
        path_layout.addWidget(self.python_path_edit, 1)
        path_layout.addWidget(browse_button)
        run_layout.addRow("Python Interpreter Path:", path_layout)
        info = QLabel("This interpreter is used for running scripts (F5) and code analysis.")
        info.setWordWrap(True)
        info.setStyleSheet("font-size: 9pt; color: grey;")
        run_layout.addRow(info)
        layout.addWidget(run_group)

        layout.addStretch()
        self.tab_widget.addTab(tab, "Run")

    def _browse_for_python(self):
        filter_str = "Executables (*.exe)" if sys.platform == "win32" else "All Files (*)"
        path, _ = QFileDialog.getOpenFileName(self, "Select Python Interpreter", "", filter_str)
        if path: self.python_path_edit.setText(path)

    def _create_system_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        system_group = QGroupBox("System Integration")
        system_layout = QFormLayout(system_group)
        system_layout.setRowWrapPolicy(QFormLayout.RowWrapPolicy.WrapAllRows)
        self.run_in_background_checkbox = QCheckBox("Launch at startup and run in background")
        if sys.platform != "win32": self.run_in_background_checkbox.setEnabled(
            False); self.run_in_background_checkbox.setToolTip("This feature is only available on Windows.")
        info = QLabel("Adds a tray icon that starts with Windows, allowing PuffinPyEditor to open faster.")
        info.setWordWrap(True)
        info.setStyleSheet("font-size: 9pt; color: grey;")
        system_layout.addRow(self.run_in_background_checkbox)
        system_layout.addRow(info)
        layout.addWidget(system_group)
        
        layout.addStretch()
        self.tab_widget.addTab(tab, "System")

    def _manage_startup_shortcut(self, create: bool):
        shortcut_path = get_startup_shortcut_path()
        if not shortcut_path: return
        try:
            if create:
                if not getattr(sys, 'frozen', False): QMessageBox.warning(self, "Developer Mode",
                                                                          "Startup feature only works in a packaged application."); self.run_in_background_checkbox.setChecked(
                    False); return
                install_dir = os.path.dirname(sys.executable);
                target_path = os.path.join(install_dir, "PuffinPyTray.exe")
                if not os.path.exists(target_path): QMessageBox.warning(self, "File Not Found",
                                                                        f"Could not find PuffinPyTray.exe in {install_dir}"); self.run_in_background_checkbox.setChecked(
                    False); return
                with winshell.shortcut(shortcut_path) as shortcut:
                    shortcut.path, shortcut.description, shortcut.working_directory = target_path, "PuffinPyEditor Background App", install_dir
                log.info(f"Created startup shortcut: {shortcut_path}")
            elif os.path.exists(shortcut_path):
                os.remove(shortcut_path); log.info(f"Removed startup shortcut: {shortcut_path}")
        except Exception as e:
            log.error(f"Failed to manage startup shortcut: {e}"); QMessageBox.critical(self, "Error",
                                                                                       f"Could not modify startup shortcut.\n{e}"); self.run_in_background_checkbox.setChecked(
                False)

    def _create_source_control_tab(self):
        tab = QWidget();
        top_layout = QVBoxLayout(tab)
        gh_group = QGroupBox("GitHub Account");
        gh_form_layout = QFormLayout(gh_group);
        gh_form_layout.setRowWrapPolicy(QFormLayout.RowWrapPolicy.WrapAllRows)
        auth_widget = QWidget();
        auth_layout = QHBoxLayout(auth_widget);
        auth_layout.setContentsMargins(0, 0, 0, 0)
        self.auth_status_label = QLabel("Not logged in.");
        self.auth_button = QPushButton("Login to GitHub");
        self.logout_button = QPushButton("Logout");
        self.logout_button.hide()
        auth_layout.addWidget(self.auth_status_label, 1);
        auth_layout.addWidget(self.auth_button);
        auth_layout.addWidget(self.logout_button)
        gh_form_layout.addRow("Status:", auth_widget);
        top_layout.addWidget(gh_group)
        git_group = QGroupBox("Local Git Configuration");
        git_form_layout = QFormLayout(git_group)
        self.git_user_name_edit = QLineEdit();
        self.git_user_name_edit.setPlaceholderText("Name for commits")
        self.git_user_email_edit = QLineEdit();
        self.git_user_email_edit.setPlaceholderText("Email for commits")
        branch_fix_button = QPushButton("Set Default to 'main' Globally");
        branch_btn_layout = QHBoxLayout();
        branch_btn_layout.setContentsMargins(0, 0, 0, 0)
        branch_btn_layout.addWidget(branch_fix_button);
        branch_btn_layout.addStretch()
        git_form_layout.addRow("Author Name:", self.git_user_name_edit);
        git_form_layout.addRow("Author Email:", self.git_user_email_edit)

        git_form_layout.addRow("Default Branch:", branch_btn_layout);
        top_layout.addWidget(git_group)

        build_group = QGroupBox("Build Tools");
        build_form_layout = QFormLayout(build_group);
        nsis_path_layout = QHBoxLayout()
        self.nsis_path_edit = QLineEdit();
        self.nsis_path_edit.setPlaceholderText("e.g., C:\\Program Files (x86)\\NSIS\\makensis.exe")
        browse_nsis_button = QPushButton("Browse...");
        browse_nsis_button.clicked.connect(self._browse_for_nsis)
        nsis_path_layout.addWidget(self.nsis_path_edit, 1);
        nsis_path_layout.addWidget(browse_nsis_button)
        build_form_layout.addRow("NSIS `makensis.exe` Path:", nsis_path_layout)
        self.cleanup_build_checkbox = QCheckBox("Automatically clean up temporary build files")
        self.cleanup_build_checkbox.setToolTip("Deletes the 'build/' folder after a successful installer creation to save space.")
        build_form_layout.addRow("", self.cleanup_build_checkbox)
        top_layout.addWidget(build_group)

        update_group = QGroupBox("Plugin Distribution & Update Repositories");
        update_layout = QVBoxLayout(update_group)
        splitter = QSplitter(Qt.Orientation.Horizontal);
        update_layout.addWidget(splitter, 1)
        left_pane, right_pane = self._create_repo_management_widgets();
        splitter.addWidget(left_pane);
        splitter.addWidget(right_pane)
        splitter.setSizes([250, 400]);
        top_layout.addWidget(update_group, 1);
        self.tab_widget.addTab(tab, "Source Control")
        self.auth_button.clicked.connect(self.github_manager.start_device_flow);
        self.logout_button.clicked.connect(self._logout_github)
        branch_fix_button.clicked.connect(self.git_manager.set_default_branch_to_main)

    def _browse_for_nsis(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select makensis.exe (Command-Line Version)", "", "Executable (makensis.exe)")
        if path: self.nsis_path_edit.setText(path)

    def _create_repo_management_widgets(self) -> tuple[QWidget, QWidget]:
        left_pane, right_pane = QWidget(), QWidget();
        left_layout, self.right_pane_layout = QVBoxLayout(left_pane), QVBoxLayout(right_pane)
        self.repo_list_widget = QListWidget();
        repo_btn_layout = QHBoxLayout();
        create_repo_btn = QPushButton("Create on GitHub...")
        add_repo_btn, remove_repo_btn = QPushButton("Add Existing..."), QPushButton("Remove")
        repo_btn_layout.addStretch();
        repo_btn_layout.addWidget(create_repo_btn)
        repo_btn_layout.addWidget(add_repo_btn);
        repo_btn_layout.addWidget(remove_repo_btn)
        left_layout.addWidget(self.repo_list_widget);
        left_layout.addLayout(repo_btn_layout);
        self.repo_form_widget = QWidget()
        repo_form_layout = QFormLayout(self.repo_form_widget);
        self.repo_name_edit, self.repo_owner_edit, self.repo_repo_edit = QLineEdit(), QLineEdit(), QLineEdit()
        self.repo_active_checkbox = QCheckBox("Set as Primary (for updates & publishing)");
        repo_form_layout.addRow("Friendly Name:", self.repo_name_edit)
        repo_form_layout.addRow("Owner (e.g., 'Stelliro'):", self.repo_owner_edit);
        repo_form_layout.addRow("Repository (e.g., 'PuffinPyEditor'):", self.repo_repo_edit)
        repo_form_layout.addRow("", self.repo_active_checkbox);
        self.repo_placeholder_label = QLabel("\nSelect a repository to edit, or create a new one.")
        self.repo_placeholder_label.setAlignment(Qt.AlignmentFlag.AlignCenter);
        self.repo_placeholder_label.setStyleSheet("color: grey;")
        self.right_pane_layout.addWidget(self.repo_placeholder_label, 1);
        self.right_pane_layout.addWidget(self.repo_form_widget)
        create_repo_btn.clicked.connect(self._action_create_repo)
        add_repo_btn.clicked.connect(self._action_add_repo);
        remove_repo_btn.clicked.connect(self._action_remove_repo)
        self.repo_list_widget.currentItemChanged.connect(self._on_repo_selection_changed);
        self.repo_active_checkbox.toggled.connect(self._on_active_checkbox_toggled)
        return left_pane, right_pane

    def _action_create_repo(self):
        name, ok = QInputDialog.getText(self, "Create New Repository", "Enter a name for the new repository:")
        if not (ok and name): return
        description, _ = QInputDialog.getText(self, "Create New Repository", "Description (optional):")
        is_private = QMessageBox.question(self, "Visibility", "Make this repository private?",
                                          QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                          QMessageBox.StandardButton.No) == QMessageBox.StandardButton.Yes
        self.github_manager.create_repo(name, description, is_private)
        QMessageBox.information(self, "In Progress", f"Attempting to create '{name}' on GitHub...")

    def _populate_git_config_fields(self, name: str, email: str):
        log.debug(f"Populating Git config fields with Name: '{name}', Email: '{email}'");
        self.original_git_config = {'name': name, 'email': email}
        self.git_user_name_edit.setText(name);
        self.git_user_email_edit.setText(email)

    def _handle_git_success(self, message: str, data: dict):
        if "Default branch" in message: QMessageBox.information(self, "Success", message)

    def _logout_github(self):
        self.github_manager.logout(); self._update_auth_status()

    def _update_auth_status(self):
        user = self.github_manager.get_authenticated_user();
        is_logged_in = bool(user)
        self.auth_status_label.setText(f"Logged in as: <b>{user}</b>" if is_logged_in else "Not logged in.")
        self.auth_button.setVisible(not is_logged_in);
        self.logout_button.setVisible(is_logged_in)

    def _on_device_code_ready(self, data: dict):
        self.auth_dialog = AuthDialog(data['user_code'], data['verification_uri'], self);
        self.auth_dialog.show()
        self.github_manager.poll_for_token(data['device_code'], data['interval'], data['expires_in'])

    def _on_auth_successful(self, username: str):
        if self.auth_dialog: self.auth_dialog.accept()
        QMessageBox.information(self, "Success", f"Successfully logged in as {username}.")
        self._update_auth_status()
        if not self.git_user_name_edit.text():
            self.git_user_name_edit.setText(username)
        if not self.git_user_email_edit.text():
            self.git_user_email_edit.setPlaceholderText(f"e.g., {username}@users.noreply.github.com")

    def _on_auth_failed(self, error_message: str):
        if self.auth_dialog: self.auth_dialog.reject()
        QMessageBox.critical(self, "Authentication Failed", error_message);
        self._update_auth_status()

    def _on_auth_polling_lapsed(self):
        if self.auth_dialog: self.auth_dialog.reject()
        QMessageBox.warning(self, "Login Expired", "The login code has expired. Please try again.");
        self._update_auth_status()

    def _on_repo_selection_changed(self, current_item: Optional[QListWidgetItem],
                                   previous_item: Optional[QListWidgetItem]):
        if previous_item: self._save_repo_form_to_staged()
        if not current_item: self._clear_repo_form(); return
        self._load_staged_to_repo_form(current_item.data(Qt.ItemDataRole.UserRole))

    def _on_active_checkbox_toggled(self, checked: bool):
        if not self.current_repo_id_in_form: return
        self.staged_active_repo_id = self.current_repo_id_in_form if checked else None
        self._populate_repo_list(select_repo_id=self.current_repo_id_in_form);
        self._on_ui_setting_changed()

    def _save_repo_form_to_staged(self):
        if not self.current_repo_id_in_form: return
        repo = next((r for r in self.staged_repos if r.get("id") == self.current_repo_id_in_form), None)
        if repo: repo.update({'name': self.repo_name_edit.text().strip(), 'owner': self.repo_owner_edit.text().strip(),
                              'repo': self.repo_repo_edit.text().strip()})

    def _load_staged_to_repo_form(self, repo_id: str):
        repo_data = next((r for r in self.staged_repos if r.get("id") == repo_id), None)
        if not repo_data: self._clear_repo_form(); return
        self.current_repo_id_in_form = repo_id
        for w in [self.repo_name_edit, self.repo_owner_edit, self.repo_repo_edit,
                  self.repo_active_checkbox]: w.blockSignals(True)
        self.repo_name_edit.setText(repo_data.get("name", ""));
        self.repo_owner_edit.setText(repo_data.get("owner", ""))
        self.repo_repo_edit.setText(repo_data.get("repo", ""));
        self.repo_active_checkbox.setChecked(self.staged_active_repo_id == repo_id)
        for w in [self.repo_name_edit, self.repo_owner_edit, self.repo_repo_edit,
                  self.repo_active_checkbox]: w.blockSignals(False)
        self.repo_placeholder_label.hide();
        self.repo_form_widget.show()

    def _action_add_repo(self):
        self._save_repo_form_to_staged();
        new_id = str(uuid.uuid4())
        self.staged_repos.append({"id": new_id, "name": "New Repository", "owner": "", "repo": ""})
        self._populate_repo_list(select_repo_id=new_id);
        self.repo_name_edit.setFocus();
        self.repo_name_edit.selectAll();
        self._on_ui_setting_changed()

    def _action_remove_repo(self):
        current_item = self.repo_list_widget.currentItem()
        if not current_item: return
        repo_id = current_item.data(Qt.ItemDataRole.UserRole)
        repo = next((r for r in self.staged_repos if r.get("id") == repo_id), None)
        repo_name = f"'{repo.get('owner')}/{repo.get('repo')}'" if repo else f"'{current_item.text()}'"

        msg_box = QMessageBox(self)
        msg_box.setIcon(QMessageBox.Icon.Warning)
        msg_box.setWindowTitle("Confirm Remove")
        msg_box.setTextFormat(Qt.TextFormat.RichText)
        msg_box.setText(f"Are you sure you want to remove the repository {repo_name} "
                        "from PuffinPyEditor's list?")
        msg_box.setInformativeText("<b>This will NOT delete the repository from GitHub.</b> "
                                   "It only removes it from this application's configuration.")
        msg_box.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.Cancel)
        msg_box.setDefaultButton(QMessageBox.StandardButton.Cancel)

        if msg_box.exec() == QMessageBox.StandardButton.Yes:
            self.staged_repos = [r for r in self.staged_repos if r.get("id") != repo_id]
            if self.staged_active_repo_id == repo_id: self.staged_active_repo_id = None
            self._populate_repo_list();
            self._on_ui_setting_changed()

    def _populate_repo_list(self, select_repo_id: Optional[str] = None):
        self.repo_list_widget.blockSignals(True);
        self.repo_list_widget.clear();
        item_to_select = None
        for repo in sorted(self.staged_repos, key=lambda r: r.get('name', '').lower()):
            item = QListWidgetItem(repo.get("name"));
            item.setData(Qt.ItemDataRole.UserRole, repo.get("id"))
            if repo.get("id") == self.staged_active_repo_id: item.setIcon(qta.icon('fa5s.star', color='gold'))
            self.repo_list_widget.addItem(item)
            if repo.get("id") == select_repo_id: item_to_select = item
        self.repo_list_widget.blockSignals(False)
        if item_to_select:
            self.repo_list_widget.setCurrentItem(item_to_select)
        else:
            self._clear_repo_form()

    def _clear_repo_form(self):
        self.current_repo_id_in_form = None
        for w in [self.repo_name_edit, self.repo_owner_edit, self.repo_repo_edit]: w.clear()
        self.repo_active_checkbox.setChecked(False);
        self.repo_placeholder_label.show();
        self.repo_form_widget.hide()

    def _create_plugins_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        remote_group = QGroupBox("Install New Plugins")
        remote_layout = QVBoxLayout(remote_group)
        
        repo_layout = QHBoxLayout()
        repo_label = QLabel("Plugin Distro Repo:")
        repo_label.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        repo_layout.addWidget(repo_label)
        self.plugins_repo_edit = QLineEdit()
        self.plugins_repo_edit.setPlaceholderText("user/repository")
        self.fetch_plugins_button = QPushButton("Fetch")
        repo_layout.addWidget(self.plugins_repo_edit, 1)
        repo_layout.addWidget(self.fetch_plugins_button)
        remote_layout.addLayout(repo_layout)

        self.remote_plugins_list = QListWidget() # Changed from QTreeWidget
        remote_layout.addWidget(self.remote_plugins_list)

        remote_buttons_layout = QHBoxLayout()
        self.install_remote_button = QPushButton("Install Selected Plugin")
        self.install_remote_button.setIcon(qta.icon('fa5s.download'))
        self.install_remote_button.setEnabled(False)
        install_file_button = QPushButton("Install from File (.zip)...")
        install_file_button.setIcon(qta.icon('fa5s.file-archive'))
        remote_buttons_layout.addStretch()
        remote_buttons_layout.addWidget(self.install_remote_button)
        remote_buttons_layout.addWidget(install_file_button)
        remote_layout.addLayout(remote_buttons_layout)
        
        layout.addWidget(remote_group, 1)

        installed_group = QGroupBox("Installed Plugins")
        installed_layout = QVBoxLayout(installed_group)
        self.installed_plugins_list = QListWidget()
        self.uninstall_plugin_button = QPushButton("Uninstall Selected Plugin")
        self.uninstall_plugin_button.setIcon(qta.icon('fa5s.trash-alt', color='crimson'))
        self.uninstall_plugin_button.setEnabled(False)
        installed_layout.addWidget(self.installed_plugins_list)
        installed_layout.addWidget(self.uninstall_plugin_button, 0, Qt.AlignmentFlag.AlignRight)
        
        layout.addWidget(installed_group, 1)
        self.tab_widget.addTab(tab, "Plugins")

        self.fetch_plugins_button.clicked.connect(self._fetch_remote_plugins)
        install_file_button.clicked.connect(self._install_plugin_from_file)
        self.install_remote_button.clicked.connect(self._install_selected_remote_plugin)
        self.uninstall_plugin_button.clicked.connect(self._uninstall_selected_plugin)
        self.installed_plugins_list.currentItemChanged.connect(self._on_installed_plugin_selected)
        self.remote_plugins_list.currentItemChanged.connect(self._on_remote_plugin_selected)

    def _populate_installed_plugins_list(self):
        self.installed_plugins_list.clear();
        plugins = self.plugin_manager.get_installed_plugins()
        for plugin in plugins:
            is_core = plugin.get("is_core", False)
            name_suffix = " (Core Tool)" if is_core else ""
            item_text = f"{plugin.get('name', 'Unknown')} v{plugin.get('version', 'N/A')}{name_suffix}"
            
            list_item = QListWidgetItem(item_text);
            list_item.setToolTip(f"ID: {plugin.get('id')}\n{plugin.get('description')}")
            list_item.setData(Qt.ItemDataRole.UserRole, plugin);
            
            if is_core:
                list_item.setForeground(QColor("grey"))
                
            self.installed_plugins_list.addItem(list_item)
            
    def _on_installed_plugin_selected(self, current_item: QListWidgetItem):
        if not current_item:
            self.uninstall_plugin_button.setEnabled(False)
            return
        
        plugin_data = current_item.data(Qt.ItemDataRole.UserRole)
        is_core = plugin_data.get("is_core", False)
        self.uninstall_plugin_button.setEnabled(not is_core)
        self.uninstall_plugin_button.setToolTip(
            "Core plugins cannot be uninstalled." if is_core else "Uninstall the selected plugin."
        )

    def _on_remote_plugin_selected(self, current_item: QListWidgetItem):
        if current_item is None:
            self.install_remote_button.setEnabled(False)
            return

        # Check if the ItemIsEnabled flag is set and convert to a boolean
        can_install = bool(current_item.flags() & Qt.ItemFlag.ItemIsEnabled)
        self.install_remote_button.setEnabled(can_install)

    def _fetch_remote_plugins(self):
        repo_path = self.plugins_repo_edit.text().strip()
        if not repo_path or '/' not in repo_path: QMessageBox.warning(self, "Invalid Repo",
                                                                      "Enter a valid GitHub repo (user/repo)."); return
        self.remote_plugins_list.clear()
        self.remote_plugins_list.addItem("Fetching...");
        self.fetch_plugins_button.setEnabled(False)
        self.install_remote_button.setEnabled(False)
        self.github_manager.fetch_plugin_index(repo_path)

    def _on_plugin_index_ready(self, plugin_list: list):
        self.fetch_plugins_button.setEnabled(True);
        self.remote_plugins_list.clear()
        installed_ids = {p['id'] for p in self.plugin_manager.get_installed_plugins()}
        
        for plugin_info in plugin_list:
            name = plugin_info.get("name", "Unknown")
            version = plugin_info.get("version", "N/A")
            is_installed = plugin_info.get('id') in installed_ids
            
            item_text = f"{name} v{version}"
            if is_installed:
                item_text += " (Installed)"

            list_item = QListWidgetItem(item_text)
            list_item.setToolTip(plugin_info.get("description", "No description available."))
            list_item.setData(Qt.ItemDataRole.UserRole, plugin_info)
            
            if is_installed:
                list_item.setFlags(list_item.flags() & ~Qt.ItemFlag.ItemIsEnabled)
                list_item.setForeground(QColor("grey"))

            self.remote_plugins_list.addItem(list_item)

    def _install_selected_remote_plugin(self):
        current_item = self.remote_plugins_list.currentItem()
        if not current_item:
            return
        plugin_info = current_item.data(Qt.ItemDataRole.UserRole)
        download_url = plugin_info.get("download_url")
        self._install_plugin_from_url(download_url)

    def _install_plugin_from_url(self, url: str):
        if not url: QMessageBox.critical(self, "Error", "Plugin has no download URL."); return
        try:
            response = requests.get(url, stream=True, timeout=30);
            response.raise_for_status()
            with tempfile.NamedTemporaryFile(delete=False, suffix=".zip") as tmp_file:
                for chunk in response.iter_content(8192): tmp_file.write(chunk)
                temp_zip_path = tmp_file.name
            success, message = self.plugin_manager.install_plugin_from_zip(temp_zip_path)
            if success:
                QMessageBox.information(self, "Success",
                                        message); self.restart_needed = True; self._populate_installed_plugins_list(); self._fetch_remote_plugins()
            else:
                QMessageBox.critical(self, "Installation Failed", message)
        except requests.RequestException as e:
            QMessageBox.critical(self, "Download Failed", f"Could not download: {e}")
        finally:
            if 'temp_zip_path' in locals() and os.path.exists(temp_zip_path): os.remove(temp_zip_path)

    def _install_plugin_from_file(self):
        filepath, _ = QFileDialog.getOpenFileName(self, "Select Plugin Archive", "", "ZIP Files (*.zip)")
        if not filepath: return
        success, message = self.plugin_manager.install_plugin_from_zip(filepath)
        if success:
            QMessageBox.information(self, "Success",
                                    message); self.restart_needed = True; self._populate_installed_plugins_list()
        else:
            QMessageBox.critical(self, "Uninstall Failed", message)

    def _uninstall_selected_plugin(self):
        current_item = self.installed_plugins_list.currentItem()
        if not current_item: 
            QMessageBox.warning(self, "No Selection", "Please select a plugin to uninstall.")
            return
            
        plugin_data = current_item.data(Qt.ItemDataRole.UserRole)
        plugin_id = plugin_data.get('id')
        
        if plugin_data.get("is_core", False):
            QMessageBox.information(self, "Cannot Uninstall", "This is a core plugin and cannot be uninstalled.")
            return

        if QMessageBox.question(self, "Confirm Uninstall",
                                f"Uninstall '{current_item.text()}'?") == QMessageBox.StandardButton.Yes:
            success, message = self.plugin_manager.uninstall_plugin(plugin_id)
            if success:
                QMessageBox.information(self, "Success",
                                        message); self.restart_needed = True; self._populate_installed_plugins_list()
            else:
                QMessageBox.critical(self, "Uninstall Failed", message)
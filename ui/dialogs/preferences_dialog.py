# PuffinPyEditor/ui/dialogs/preferences_dialog.py
import uuid
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QGridLayout, QTabWidget, QWidget,
                             QLabel, QComboBox, QSpinBox, QCheckBox, QPushButton,
                             QDialogButtonBox, QFontComboBox, QSplitter, QFormLayout,
                             QListWidget, QListWidgetItem, QLineEdit, QMessageBox, QRadioButton, QFrame, QGroupBox)
from PyQt6.QtGui import QFont, QDesktopServices
from PyQt6.QtCore import Qt, QSize, pyqtSignal, QUrl

from utils.logger import log
from app_core.settings_manager import settings_manager
from app_core.theme_manager import theme_manager
from app_core.github_manager import GitHubManager
from app_core.source_control_manager import SourceControlManager
from .theme_editor_dialog import ThemeEditorDialog


class AuthDialog(QDialog):
    """A simple dialog to show the GitHub device code."""

    def __init__(self, user_code, verification_uri, parent=None):
        super().__init__(parent)
        self.setWindowTitle("GitHub Device Authorization")
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Please authorize PuffinPyEditor in your browser."))

        url_label = QLabel(f"1. Open: <b><a href='{verification_uri}'>{verification_uri}</a></b>")
        url_label.setOpenExternalLinks(True)
        layout.addWidget(url_label)

        layout.addWidget(QLabel("2. Enter this one-time code:"))

        code_label = QLineEdit(user_code)
        code_label.setReadOnly(True)
        code_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        font = QFont("Consolas", 14, QFont.Weight.Bold)
        code_label.setFont(font)
        layout.addWidget(code_label)

        QDesktopServices.openUrl(QUrl(verification_uri))
        self.setFixedSize(self.sizeHint())


class PreferencesDialog(QDialog):
    settings_changed_for_editor_refresh = pyqtSignal()
    theme_changed_signal = pyqtSignal(str)
    restart_requested = pyqtSignal()

    def __init__(self, git_manager: SourceControlManager, github_manager: GitHubManager, parent=None):
        super().__init__(parent)
        log.info("PreferencesDialog initializing...")
        self.setWindowTitle("Preferences")
        self.setMinimumSize(QSize(700, 500))

        self.git_manager = git_manager
        self.github_manager = github_manager
        self.original_settings = {}
        self.original_git_config = {}
        self.theme_editor_dialog_instance = None
        self.staged_repos = []
        self.staged_active_repo_id = None
        self.current_repo_id_in_form = None
        self.auth_dialog = None

        self.main_layout = QVBoxLayout(self)
        self.tab_widget = QTabWidget()
        self.main_layout.addWidget(self.tab_widget)

        self._create_appearance_tab()
        self._create_editor_tab()
        self._create_source_control_tab()

        self.button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel | QDialogButtonBox.StandardButton.Apply)
        self.main_layout.addWidget(self.button_box)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        self.button_box.button(QDialogButtonBox.StandardButton.Apply).clicked.connect(self.apply_settings)

        # Connect signals
        self.git_manager.git_config_ready.connect(self._populate_git_config_fields)
        self.github_manager.device_code_ready.connect(self.on_device_code_ready)
        self.github_manager.auth_successful.connect(self.on_auth_successful)
        self.github_manager.auth_failed.connect(self.on_auth_failed)
        self.github_manager.auth_polling_lapsed.connect(self.on_auth_polling_lapsed)

        log.info("PreferencesDialog initialized.")

    def showEvent(self, event):
        self.load_settings_into_dialog()
        self.git_manager.get_git_config()
        self._update_auth_status()
        super().showEvent(event)

    def load_settings_into_dialog(self):
        self.original_settings = settings_manager.settings.copy()
        self.staged_repos = [r.copy() for r in settings_manager.get("source_control_repos", [])]
        self.staged_active_repo_id = settings_manager.get("active_update_repo_id")

        self._populate_repo_list()
        self._repopulate_theme_combo()
        self.font_family_combo.setCurrentFont(QFont(settings_manager.get("font_family")))
        self.font_size_spinbox.setValue(settings_manager.get("font_size"))
        self.show_line_numbers_checkbox.setChecked(settings_manager.get("show_line_numbers"))
        self.word_wrap_checkbox.setChecked(settings_manager.get("word_wrap"))

        self.button_box.button(QDialogButtonBox.StandardButton.Apply).setEnabled(False)
        self._connect_ui_changed_signals()

    def _populate_git_config_fields(self, name, email):
        log.debug(f"Populating Git config fields with Name: '{name}', Email: '{email}'")
        self.original_git_config = {'name': name, 'email': email}
        self.git_user_name_edit.setText(name)
        self.git_user_email_edit.setText(email)
        # Connect signals after populating to avoid premature flag setting
        self.git_user_name_edit.textChanged.connect(self._on_ui_setting_changed)
        self.git_user_email_edit.textChanged.connect(self._on_ui_setting_changed)

    def _create_source_control_tab(self):
        tab = QWidget()
        main_layout = QVBoxLayout(tab)

        global_group_box = QGroupBox("Global Git & GitHub Configuration")
        global_form_layout = QFormLayout(global_group_box)

        auth_widget = QWidget()
        auth_layout = QHBoxLayout(auth_widget)
        auth_layout.setContentsMargins(0, 0, 0, 0)
        self.auth_status_label = QLabel("Not logged in.")
        self.auth_button = QPushButton("Login to GitHub")
        self.logout_button = QPushButton("Logout")
        self.logout_button.hide()
        auth_layout.addWidget(self.auth_status_label, 1)
        auth_layout.addWidget(self.auth_button)
        auth_layout.addWidget(self.logout_button)
        self.auth_button.clicked.connect(self.github_manager.start_device_flow)
        self.logout_button.clicked.connect(self._logout_github)
        global_form_layout.addRow(QLabel("GitHub Account:"), auth_widget)

        self.git_user_name_edit = QLineEdit()
        self.git_user_name_edit.setPlaceholderText("Your full name (e.g., Jane Doe)")
        git_user_name_label = QLabel("Git Author Name (for commits):")
        git_user_name_label.setToolTip("Sets 'user.name' in your Git configuration.\nThis is NOT your GitHub username.")
        global_form_layout.addRow(git_user_name_label, self.git_user_name_edit)

        self.git_user_email_edit = QLineEdit()
        self.git_user_email_edit.setPlaceholderText("Your email address (e.g., you@example.com)")
        git_user_email_label = QLabel("Git Author Email (for commits):")
        git_user_email_label.setToolTip("Sets 'user.email' in your Git configuration.\nThis is NOT your GitHub login email.")
        global_form_layout.addRow(git_user_email_label, self.git_user_email_edit)

        main_layout.addWidget(global_group_box)

        repo_group_box = QGroupBox("Application Update Repository Settings")
        repo_group_layout = QHBoxLayout(repo_group_box)
        splitter = QSplitter(Qt.Orientation.Horizontal)
        repo_group_layout.addWidget(splitter)
        main_layout.addWidget(repo_group_box, 1)

        left_pane = QWidget()
        left_layout = QVBoxLayout(left_pane)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.addWidget(QLabel("Configured Repositories:"))
        self.repo_list_widget = QListWidget()
        left_layout.addWidget(self.repo_list_widget)
        repo_button_layout = QHBoxLayout()
        add_repo_btn = QPushButton("Add")
        remove_repo_btn = QPushButton("Remove")
        repo_button_layout.addWidget(add_repo_btn)
        repo_button_layout.addWidget(remove_repo_btn)
        left_layout.addLayout(repo_button_layout)
        splitter.addWidget(left_pane)

        right_pane = QWidget()
        self.right_pane_layout = QVBoxLayout(right_pane)
        self.repo_form_widget = QWidget()
        repo_form_layout = QFormLayout(self.repo_form_widget)
        self.repo_name_edit = QLineEdit()
        self.repo_owner_edit = QLineEdit()
        self.repo_repo_edit = QLineEdit()
        self.repo_active_radio = QRadioButton("Active for checking updates")
        repo_form_layout.addRow("Friendly Name:", self.repo_name_edit)
        repo_form_layout.addRow("Owner (e.g., 'user-name'):", self.repo_owner_edit)
        repo_form_layout.addRow("Repository (e.g., 'repo-name'):", self.repo_repo_edit)
        repo_form_layout.addRow(self.repo_active_radio)
        self.repo_placeholder_label = QLabel("Select a repository to edit, or click 'Add'.")
        self.repo_placeholder_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.right_pane_layout.addWidget(self.repo_placeholder_label)
        self.right_pane_layout.addWidget(self.repo_form_widget)
        splitter.addWidget(right_pane)
        splitter.setSizes([250, 400])

        add_repo_btn.clicked.connect(self._action_add_repo)
        remove_repo_btn.clicked.connect(self._action_remove_repo)
        self.repo_list_widget.currentItemChanged.connect(self._on_repo_selection_changed)
        self.repo_active_radio.toggled.connect(self._on_active_radio_toggled)

        self.tab_widget.addTab(tab, "Source Control")

    def _logout_github(self):
        self.github_manager.logout()
        self._update_auth_status()

    def _update_auth_status(self):
        user = self.github_manager.get_authenticated_user()
        if user:
            self.auth_status_label.setText(f"Logged in as: <b>{user}</b>")
            self.auth_button.hide()
            self.logout_button.show()
        else:
            self.auth_status_label.setText("Not logged in.")
            self.auth_button.show()
            self.logout_button.hide()

    def on_device_code_ready(self, data):
        self.auth_dialog = AuthDialog(data['user_code'], data['verification_uri'], self)
        self.auth_dialog.show()
        self.github_manager.poll_for_token(data['device_code'], data['interval'], data['expires_in'])

    def on_auth_successful(self, username):
        if self.auth_dialog:
            self.auth_dialog.accept()
        QMessageBox.information(self, "Success", f"Successfully logged in as {username}.")
        self._update_auth_status()

    def on_auth_failed(self, error_message):
        if self.auth_dialog:
            self.auth_dialog.reject()
        QMessageBox.critical(self, "Authentication Failed", error_message)
        self._update_auth_status()

    def on_auth_polling_lapsed(self):
        if self.auth_dialog:
            self.auth_dialog.reject()
        QMessageBox.warning(self, "Login Expired", "The login code has expired. Please try again.")
        self._update_auth_status()

    def _on_repo_selection_changed(self, current_item, previous_item):
        if previous_item:
            self._save_form_to_staged()
        if not current_item:
            self._clear_repo_form()
            return
        self._load_staged_to_form(current_item.data(Qt.ItemDataRole.UserRole))

    def _on_active_radio_toggled(self, checked):
        if checked and self.current_repo_id_in_form:
            self.staged_active_repo_id = self.current_repo_id_in_form
            self._on_ui_setting_changed()

    def _save_form_to_staged(self):
        if not self.current_repo_id_in_form:
            return
        repo_to_update = next((r for r in self.staged_repos if r.get("id") == self.current_repo_id_in_form), None)
        if repo_to_update:
            repo_to_update['name'] = self.repo_name_edit.text().strip()
            repo_to_update['owner'] = self.repo_owner_edit.text().strip()
            repo_to_update['repo'] = self.repo_repo_edit.text().strip()

    def _load_staged_to_form(self, repo_id):
        repo_data = next((r for r in self.staged_repos if r.get("id") == repo_id), None)
        if not repo_data:
            self._clear_repo_form()
            return
        self.current_repo_id_in_form = repo_id
        for w in [self.repo_name_edit, self.repo_owner_edit, self.repo_repo_edit, self.repo_active_radio]:
            w.blockSignals(True)
        self.repo_name_edit.setText(repo_data.get("name", ""))
        self.repo_owner_edit.setText(repo_data.get("owner", ""))
        self.repo_repo_edit.setText(repo_data.get("repo", ""))
        self.repo_active_radio.setChecked(self.staged_active_repo_id == repo_id)
        self.repo_placeholder_label.hide()
        self.repo_form_widget.show()
        for w in [self.repo_name_edit, self.repo_owner_edit, self.repo_repo_edit, self.repo_active_radio]:
            w.blockSignals(False)

    def _action_add_repo(self):
        self._save_form_to_staged()
        new_id = str(uuid.uuid4())
        new_repo = {"id": new_id, "name": "New Repository"}
        self.staged_repos.append(new_repo)
        self._populate_repo_list(select_repo_id=new_id)
        self.repo_name_edit.setFocus()
        self.repo_name_edit.selectAll()
        self._on_ui_setting_changed()

    def _action_remove_repo(self):
        current_item = self.repo_list_widget.currentItem()
        if not current_item:
            return
        repo_id = current_item.data(Qt.ItemDataRole.UserRole)
        reply = QMessageBox.question(self, "Confirm Delete", f"Remove '{current_item.text()}'?")
        if reply == QMessageBox.StandardButton.Yes:
            self.staged_repos = [r for r in self.staged_repos if r.get("id") != repo_id]
            if self.staged_active_repo_id == repo_id:
                self.staged_active_repo_id = None
            self._populate_repo_list()
            self._on_ui_setting_changed()

    def _populate_repo_list(self, select_repo_id=None):
        self.repo_list_widget.blockSignals(True)
        self.repo_list_widget.clear()
        item_to_select = None
        for repo in sorted(self.staged_repos, key=lambda r: r.get('name', '').lower()):
            item = QListWidgetItem(repo.get("name"))
            item.setData(Qt.ItemDataRole.UserRole, repo.get("id"))
            self.repo_list_widget.addItem(item)
            if repo.get("id") == select_repo_id:
                item_to_select = item
        self.repo_list_widget.blockSignals(False)
        if item_to_select:
            self.repo_list_widget.setCurrentItem(item_to_select)
        else:
            self._clear_repo_form()

    def _clear_repo_form(self):
        self.current_repo_id_in_form = None
        for w in [self.repo_name_edit, self.repo_owner_edit, self.repo_repo_edit]:
            w.clear()
        self.repo_active_radio.setAutoExclusive(False)
        self.repo_active_radio.setChecked(False)
        self.repo_active_radio.setAutoExclusive(True)
        self.repo_placeholder_label.show()
        self.repo_form_widget.hide()

    def apply_settings(self):
        if not self.button_box.button(QDialogButtonBox.StandardButton.Apply).isEnabled():
            return

        new_name = self.git_user_name_edit.text().strip()
        new_email = self.git_user_email_edit.text().strip()
        if new_name != self.original_git_config.get('name') or new_email != self.original_git_config.get('email'):
            self.git_manager.set_git_config(new_name, new_email)
            self.original_git_config = {'name': new_name, 'email': new_email}

        self._save_form_to_staged()

        new_theme_id = self.theme_combo.currentData()
        if self.original_settings.get("last_theme_id") != new_theme_id:
            self.theme_changed_signal.emit(new_theme_id)

        settings_manager.set("last_theme_id", new_theme_id, False)
        settings_manager.set("font_family", self.font_family_combo.currentFont().family(), False)
        settings_manager.set("font_size", self.font_size_spinbox.value(), False)
        settings_manager.set("show_line_numbers", self.show_line_numbers_checkbox.isChecked(), False)
        settings_manager.set("word_wrap", self.word_wrap_checkbox.isChecked(), False)
        settings_manager.set("source_control_repos", self.staged_repos, False)
        settings_manager.set("active_update_repo_id", self.staged_active_repo_id, False)

        settings_manager.save()
        self.settings_changed_for_editor_refresh.emit()
        self.original_settings = settings_manager.settings.copy()
        self.button_box.button(QDialogButtonBox.StandardButton.Apply).setEnabled(False)
        log.info("Applied settings from Preferences dialog.")

    def accept(self):
        if self.button_box.button(QDialogButtonBox.StandardButton.Apply).isEnabled():
            self.apply_settings()
        super().accept()

    def reject(self):
        if self.auth_dialog and self.auth_dialog.isVisible():
            self.auth_dialog.reject()
        if self.button_box.button(QDialogButtonBox.StandardButton.Apply).isEnabled():
            reply = QMessageBox.question(self, "Unsaved Changes", "Discard unsaved changes?",
                                         QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                         QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.No:
                return
        super().reject()

    def _create_appearance_tab(self):
        tab = QWidget()
        layout = QGridLayout(tab)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.theme_combo = QComboBox()
        self.edit_themes_button = QPushButton("Customize Themes...")
        self.edit_themes_button.clicked.connect(self._open_theme_editor_dialog)
        self.font_family_combo = QFontComboBox()
        self.font_size_spinbox = QSpinBox()
        self.font_size_spinbox.setRange(6, 72)
        layout.addWidget(QLabel("Active Theme:"), 0, 0)
        layout.addWidget(self.theme_combo, 0, 1)
        layout.addWidget(self.edit_themes_button, 1, 1, alignment=Qt.AlignmentFlag.AlignRight)
        layout.addWidget(QLabel("Font Family:"), 2, 0)
        layout.addWidget(self.font_family_combo, 2, 1)
        layout.addWidget(QLabel("Font Size:"), 3, 0)
        layout.addWidget(self.font_size_spinbox, 3, 1)
        layout.setColumnStretch(1, 1)
        self.tab_widget.addTab(tab, "Appearance")

    def _create_editor_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.show_line_numbers_checkbox = QCheckBox("Show Line Numbers")
        self.word_wrap_checkbox = QCheckBox("Enable Word Wrap")
        layout.addWidget(self.show_line_numbers_checkbox)
        layout.addWidget(self.word_wrap_checkbox)
        layout.addStretch()
        self.tab_widget.addTab(tab, "Editor")

    def _connect_ui_changed_signals(self):
        for widget in self.findChildren((QComboBox, QSpinBox, QCheckBox, QLineEdit)):
            try:
                if hasattr(widget, 'currentIndexChanged'):
                    widget.currentIndexChanged.disconnect()
                if hasattr(widget, 'valueChanged'):
                    widget.valueChanged.disconnect()
                if hasattr(widget, 'stateChanged'):
                    widget.stateChanged.disconnect()
                if hasattr(widget, 'textChanged'):
                    widget.textChanged.disconnect()
            except TypeError:
                pass

        for widget in self.findChildren((QComboBox, QSpinBox, QCheckBox)):
            if hasattr(widget, 'currentIndexChanged'):
                widget.currentIndexChanged.connect(self._on_ui_setting_changed)
            elif hasattr(widget, 'valueChanged'):
                widget.valueChanged.connect(self._on_ui_setting_changed)
            elif hasattr(widget, 'stateChanged'):
                widget.stateChanged.connect(self._on_ui_setting_changed)

        for widget in [self.repo_name_edit, self.repo_owner_edit, self.repo_repo_edit]:
            widget.textChanged.connect(self._on_ui_setting_changed)

    def _on_ui_setting_changed(self, *args):
        self.button_box.button(QDialogButtonBox.StandardButton.Apply).setEnabled(True)

    def _repopulate_theme_combo(self):
        current_id = settings_manager.get("last_theme_id")
        self.theme_combo.blockSignals(True)
        self.theme_combo.clear()
        for theme_id, name in theme_manager.get_available_themes_for_ui().items():
            self.theme_combo.addItem(name, theme_id)
        index = self.theme_combo.findData(current_id)
        if index != -1:
            self.theme_combo.setCurrentIndex(index)
        self.theme_combo.blockSignals(False)

    def _open_theme_editor_dialog(self):
        if self.theme_editor_dialog_instance is None:
            self.theme_editor_dialog_instance = ThemeEditorDialog(self)
            self.theme_editor_dialog_instance.custom_themes_changed.connect(self._repopulate_theme_combo)
        self.theme_editor_dialog_instance.exec()
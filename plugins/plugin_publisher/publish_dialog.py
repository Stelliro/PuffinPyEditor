# PuffinPyEditor/plugins/plugin_publisher/publish_dialog.py
import os
import shutil
import tempfile
import json
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QFormLayout, QComboBox,
                             QTextEdit, QPushButton, QDialogButtonBox, QLabel,
                             QMessageBox, QHBoxLayout)
from PyQt6.QtGui import QFont

# --- Content for auto-initializing a distro repo ---
README_CONTENT = """# PuffinPyEditor Plugin Distribution Repository

This repository is structured to serve plugins for the PuffinPyEditor.

- `index.json`: A manifest file listing all available plugins and their download URLs.
- `zips/`: This directory contains the packaged `.zip` files for each plugin.

To publish a new version of a plugin, use the "Publish Plugin" tool inside PuffinPyEditor.
"""
GITIGNORE_CONTENT = """# Ignore common temp files
*.tmp
*.bak
*~

# Ignore local environment
venv/
.venv/
"""


class PublishDialog(QDialog):
    """A dialog to manage the process of publishing a plugin."""

    def __init__(self, api, parent):
        super().__init__(parent)
        self.api = api
        self.git_manager = api.get_manager("git")
        self.github_manager = api.get_manager("github")
        self.plugin_manager = api.get_manager("plugin")
        self.settings = api.get_manager("settings")
        self._temp_dir = None
        self._current_step = None
        self.cloned_repo_path = None
        self.setWindowTitle("Publish a Plugin")
        self.setMinimumSize(600, 450)
        self._setup_ui()
        self._connect_ui_signals()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        form_layout = QFormLayout()

        self.plugin_selector = QComboBox()
        form_layout.addRow("Plugin to Publish:", self.plugin_selector)

        repo_layout = QHBoxLayout()
        repo_layout.setContentsMargins(0, 0, 0, 0)
        self.repo_combo = QComboBox()
        self.manage_repos_button = QPushButton("Manage...")
        repo_layout.addWidget(self.repo_combo, 1)
        repo_layout.addWidget(self.manage_repos_button)
        form_layout.addRow("Target Repository:", repo_layout)

        self.commit_message = QTextEdit()
        self.commit_message.setFixedHeight(80)
        form_layout.addRow("Commit Message:", self.commit_message)
        layout.addLayout(form_layout)

        log_label = QLabel("Log:")
        layout.addWidget(log_label)

        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        self.log_output.setFont(QFont("Consolas", 9))
        self.log_output.setStyleSheet("background-color: #1E1E1E; color: #D4D4D4;")
        layout.addWidget(self.log_output, 1)

        self.button_box = QDialogButtonBox()
        self.publish_button = self.button_box.addButton("Publish", QDialogButtonBox.ButtonRole.AcceptRole)
        self.close_button = self.button_box.addButton("Close", QDialogButtonBox.ButtonRole.RejectRole)
        layout.addWidget(self.button_box)

    def _connect_ui_signals(self):
        self.publish_button.clicked.connect(self._start_publish_flow)
        self.close_button.clicked.connect(self.reject)
        self.manage_repos_button.clicked.connect(self._open_preferences)
        self.plugin_selector.currentIndexChanged.connect(self._on_plugin_selected)

    def _open_preferences(self):
        self.api.get_main_window()._action_open_preferences()

    def _set_ui_locked(self, locked: bool):
        self.publish_button.setEnabled(not locked)
        self.plugin_selector.setEnabled(not locked)
        self.repo_combo.setEnabled(not locked)
        self.commit_message.setEnabled(not locked)
        self.manage_repos_button.setEnabled(not locked)
        self.close_button.setText("Cancel" if locked else "Close")

    def _add_log(self, message, is_error=False):
        color = "#FF5555" if is_error else "#A9B7C6"
        self.log_output.append(f"<span style='color: {color};'>{message}</span>")
        self.api.log_info(f"[Plugin Publisher] {message}")

    def showEvent(self, event):
        super().showEvent(event)
        self._populate_plugins()
        self._populate_repos()
        can_publish = bool(self.repo_combo.count() > 0 and self.plugin_selector.count() > 0)
        self.publish_button.setEnabled(can_publish)
        self.publish_button.setToolTip("Select a plugin and configure your distribution repo."
                                       if not can_publish else "")
        self.log_output.clear()

    def _populate_plugins(self):
        self.plugin_selector.clear()
        installed_plugins = self.plugin_manager.get_installed_plugins()
        skippable_ids = {'plugin_creator_framework', 'plugin_publisher'}
        for plugin in installed_plugins:
            plugin_id = plugin.get("id")
            if plugin_id and plugin_id not in skippable_ids:
                display_text = f'{plugin.get("name", plugin_id)} (v{plugin.get("version", "N/A")})'
                self.plugin_selector.addItem(display_text, plugin)
        self._on_plugin_selected()

    def _populate_repos(self):
        self.repo_combo.clear()
        all_repos = self.settings.get("source_control_repos", [])
        primary_repo_id = self.settings.get("active_update_repo_id")
        primary_idx = -1
        for i, repo_config in enumerate(all_repos):
            repo_path = f"{repo_config.get('owner', '?')}/{repo_config.get('repo', '?')}"
            self.repo_combo.addItem(repo_path, repo_config)
            if repo_config.get('id') == primary_repo_id:
                primary_idx = i
        if primary_idx != -1:
            self.repo_combo.setCurrentIndex(primary_idx)

    def _on_plugin_selected(self):
        plugin_data = self.plugin_selector.currentData()
        if not plugin_data:
            return
        commit_msg = f"feat(plugin): Publish {plugin_data['name']} v{plugin_data['version']}"
        self.commit_message.setText(commit_msg)

    def _cleanup(self, success=True):
        self._set_ui_locked(False)
        self.git_manager.git_success.disconnect(self._on_git_step_success)
        self.git_manager.git_error.disconnect(self._on_publish_failed)
        if self._temp_dir and os.path.exists(self._temp_dir):
            shutil.rmtree(self._temp_dir, ignore_errors=True)
            self._add_log("Cleaned up temporary directory.")
        self._temp_dir, self.cloned_repo_path, self._current_step = None, None, None

    def _on_publish_failed(self, error_message):
        self._add_log(f"FAILED on step '{self._current_step}': {error_message}", is_error=True)
        self._cleanup(success=False)

    def _start_publish_flow(self):
        repo_data = self.repo_combo.currentData()
        self.plugin_data = self.plugin_selector.currentData()
        self.distro_repo_path = f"{repo_data.get('owner')}/{repo_data.get('repo')}"

        if not all([repo_data, self.plugin_data, self.commit_message.toPlainText()]):
            QMessageBox.warning(self, "Missing Information", "Please select a plugin, "
                                                             "a distribution repo, and provide a commit message.")
            return

        self._set_ui_locked(True)
        self.log_output.clear()
        self._add_log("Starting plugin publication process...")
        self._temp_dir = tempfile.mkdtemp(prefix="puffin-plugin-publish-")
        self.git_manager.git_success.connect(self._on_git_step_success)
        self.git_manager.git_error.connect(self._on_publish_failed)
        self._current_step = "CLONE"
        self._add_log(f"Cloning '{self.distro_repo_path}'...")
        repo_url = f"https://github.com/{self.distro_repo_path}.git"
        self.git_manager.clone_repo(repo_url, self._temp_dir)

    def _on_git_step_success(self, message: str, data: dict):
        if self._current_step == "CLONE":
            self.cloned_repo_path = data.get("path")
            self._add_log(f"Successfully cloned repository to {self.cloned_repo_path}")
            if not os.path.exists(os.path.join(self.cloned_repo_path, "index.json")):
                self._current_step = "INITIALIZE_COMMIT"
                self._add_log("Empty repository detected. Initializing structure...")
                self._initialize_distro_repo()
                self.git_manager.commit_files(self.cloned_repo_path,
                                              "ci: Initialize plugin distribution repository")
            else:
                self._package_and_commit_plugin()

        elif self._current_step == "INITIALIZE_COMMIT":
            self._add_log("Initial commit successful.")
            self._package_and_commit_plugin()

        elif self._current_step == "PUBLISH_COMMIT":
            self._add_log(f"Commit successful. {message}")
            self._current_step = "PUSH"
            self._add_log(f"Pushing changes to '{self.distro_repo_path}'...")
            self.git_manager.push(self.cloned_repo_path)

        elif self._current_step == "PUSH":
            self._add_log("Push successful!")
            self._add_log("\n--- PUBLICATION COMPLETE ---")
            self._cleanup(success=True)

    def _package_and_commit_plugin(self):
        self._current_step = "PUBLISH_COMMIT"
        try:
            self._package_plugin_and_update_index()
            self._add_log("Staging and committing plugin files...")
            self.git_manager.commit_files(self.cloned_repo_path, self.commit_message.toPlainText())
        except Exception as e:
            self._on_publish_failed(str(e))

    def _initialize_distro_repo(self):
        try:
            with open(os.path.join(self.cloned_repo_path, 'index.json'), 'w') as f:
                json.dump([], f)
            with open(os.path.join(self.cloned_repo_path, 'README.md'), 'w') as f:
                f.write(README_CONTENT)
            with open(os.path.join(self.cloned_repo_path, '.gitignore'), 'w') as f:
                f.write(GITIGNORE_CONTENT)
            os.makedirs(os.path.join(self.cloned_repo_path, 'zips'), exist_ok=True)
            with open(os.path.join(self.cloned_repo_path, 'zips', '.gitkeep'), 'w') as f:
                pass
        except Exception as e:
            self._on_publish_failed(f"Error initializing distro repo files: {e}")
            raise

    def _package_plugin_and_update_index(self):
        try:
            self._add_log(f"Packaging '{self.plugin_data['name']}' as a .zip file...")
            plugin_id = self.plugin_data['id']
            zip_filename = f"{plugin_id}.zip"
            plugin_source_path = os.path.join(self.plugin_manager.user_plugins_directory, plugin_id)
            if not os.path.exists(plugin_source_path):
                plugin_source_path = os.path.join(self.plugin_manager.built_in_plugins_dir, plugin_id)

            zips_dir_in_repo = os.path.join(self.cloned_repo_path, 'zips')
            final_zip_path = os.path.join(zips_dir_in_repo, zip_filename)
            shutil.make_archive(os.path.splitext(final_zip_path)[0], 'zip', plugin_source_path)

            self._add_log("Updating index.json...")
            index_path = os.path.join(self.cloned_repo_path, 'index.json')
            index_data = []
            if os.path.exists(index_path):
                with open(index_path, 'r', encoding='utf-8') as f:
                    index_data = json.load(f)

            rel_zip_path = os.path.join('zips', zip_filename).replace("\\", "/")
            download_url = f"https://raw.githubusercontent.com/{self.distro_repo_path}/main/{rel_zip_path}"
            new_entry = {k: self.plugin_data.get(k) for k in ('id', 'name', 'author', 'version', 'description')}
            new_entry['download_url'] = download_url

            index_data = [entry for entry in index_data if entry.get('id') != plugin_id]
            index_data.append(new_entry)

            with open(index_path, 'w', encoding='utf-8') as f:
                json.dump(index_data, f, indent=4)
        except Exception as e:
            self._add_log(f"Error during local packaging: {e}", is_error=True)
            raise
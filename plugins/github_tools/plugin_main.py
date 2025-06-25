# PuffinPyEditor/plugins/github_tools/plugin_main.py
import os
import shutil
import tempfile
import time
import git

from PyQt6.QtWidgets import QInputDialog, QMessageBox, QProgressDialog, QTextEdit
from PyQt6.QtCore import QProcess
from PyQt6.QtGui import QFont

# --- FIX: Reverted to direct imports for the plugin loader ---
from new_release_dialog import NewReleaseDialog
from select_repo_dialog import SelectRepoDialog
from github_dialog import GitHubDialog
# --- END FIX ---
from utils import versioning


class GitHubToolsPlugin:
    def __init__(self, main_window):
        self.main_window = main_window
        self.api = main_window.puffin_api
        self.project_manager = self.api.get_manager("project")
        self.git_manager = self.api.get_manager("git")
        self.github_manager = self.api.get_manager("github")
        self._release_data = {}
        self._release_id = None
        self.github_dialog = None
        self.build_process = None
        self._is_part_of_release = False
        self._current_step = None
        self.api.log_info("GitHub Tools plugin initialized.")

        self.api.add_menu_action(
            "tools", "Build Project Installer",
            self._show_build_installer_dialog,
            icon_name="fa5s.cogs"
        )

    def _get_sc_panel(self):
        sc_plugin_info = self.main_window.plugin_manager.loaded_plugins.get('source_control_ui', {})
        sc_plugin = sc_plugin_info.get('instance')
        return sc_plugin.source_control_panel if sc_plugin else None

    def _ensure_git_identity(self, project_path: str) -> bool:
        self.api.log_info("Checking Git author information...")
        user_info = self.github_manager.get_user_info()
        if not user_info:
            self.api.show_message("warning", "GitHub User Not Found",
                                  "Could not fetch your GitHub user info. Please log in.")
            return False
        try:
            repo = git.Repo(project_path)
            user_name = user_info.get('login')
            user_email = user_info.get('email') or f"{user_info.get('id')}+{user_info.get('login')}@users.noreply.github.com"
            with repo.config_writer() as config:
                config.set_value('user', 'name', user_name)
                config.set_value('user', 'email', user_email)
            self.api.log_info("Git author configured for this operation.")
            return True
        except Exception as e:
            self.api.show_message("warning", "Git Config Failed", f"Failed to set Git author info: {e}")
            return False

    def _create_release(self, project_path):
        if not self._ensure_git_identity(project_path):
            self.api.show_status_message("Release cancelled due to Git identity misconfiguration.", 5000)
            return
        try:
            repo = git.Repo(project_path)
            if not repo.remotes:
                self.api.show_message("warning", "No Remote", "This project has no remote repository.")
                return
            owner, repo_name = self.git_manager.parse_git_url(repo.remotes.origin.url)
            if not owner or not repo_name:
                self.api.show_message("critical", "Error", "Could not parse owner/repo from a valid GitHub remote.")
                return
            self._release_owner, self._release_repo_name = owner, repo_name
        except Exception as e:
            self.api.show_message("critical", "Error", f"Could not analyze repository: {e}")
            return

        dialog = NewReleaseDialog(project_path, self.git_manager, self.main_window)
        if not dialog.exec():
            self.api.show_status_message("Release cancelled.", 3000)
            return

        self._release_data = dialog.get_release_data()
        self._release_project_path = project_path

        if sc_panel := self._get_sc_panel():
            sc_panel.set_ui_locked(True, f"Creating tag '{self._release_data['tag']}'...")

        self._current_step = "CREATE_TAG"
        self.git_manager.git_success.connect(self._on_git_step_success)
        self.git_manager.git_error.connect(self._on_release_step_failed)
        self.git_manager.create_tag(self._release_project_path, self._release_data['tag'], self._release_data['title'])

    def _on_git_step_success(self, msg, data):
        self.api.log_info(f"Git success on step '{self._current_step}': {msg}")

        if self._current_step == "CREATE_TAG":
            if sc_panel := self._get_sc_panel():
                sc_panel.set_ui_locked(True, f"Pushing tag '{self._release_data['tag']}'...")
            self._current_step = "PUSH_TAG"
            self.git_manager.push_specific_tag(self._release_project_path, self._release_data['tag'])

        elif self._current_step == "PUSH_TAG":
            if sc_panel := self._get_sc_panel():
                sc_panel.set_ui_locked(True, "Creating GitHub release...")
            self.github_manager.operation_success.connect(self._on_github_release_created)
            self.github_manager.operation_failed.connect(self._on_release_step_failed)
            self._current_step = "CREATE_RELEASE"
            self.github_manager.create_release(owner=self._release_owner, repo=self._release_repo_name,
                                               tag_name=self._release_data['tag'], name=self._release_data['title'],
                                               body=self._release_data['notes'], prerelease=self._release_data['prerelease'])

        elif self._current_step == "BUMP_VERSION_COMMIT":
            if sc_panel := self._get_sc_panel():
                sc_panel.set_ui_locked(True, "Pushing final version commit...")
            self._current_step = "FINAL_PUSH"
            self.git_manager.push(self._release_project_path)

        elif self._current_step == "FINAL_PUSH":
            success_msg = f"Release '{self._release_data['tag']}' published successfully!"
            self.api.show_status_message(success_msg, 5000)
            QMessageBox.information(self.main_window, "Success", success_msg)
            self._cleanup_release_process()

    def _on_github_release_created(self, msg, data):
        if "Release created" in msg:
            self._cleanup_connections()
            self._release_info = data.get("release_data", {})
            self._release_id = self._release_info.get("id")
            self._release_upload_url = self._release_info.get("upload_url")
            if not self._release_upload_url:
                self._on_release_step_failed("GitHub did not provide an upload URL for assets.")
                return

            if self._release_data.get("build_installer"):
                self._current_step = "BUILD_ASSETS"
                self._is_part_of_release = True
                self._run_build_script(self._release_project_path)
            else:
                self._current_step = "UPLOAD_ASSETS"
                self._upload_assets()

    def _run_build_script(self, project_path):
        build_script_path = os.path.join(project_path, "installer", "build.bat")
        if not os.path.exists(build_script_path):
            self._on_release_step_failed(f"Build script not found at '{build_script_path}'.")
            return

        self.build_progress = QProgressDialog("Building Application...", "This may take a moment...", 0, 0, self.main_window)
        self.build_progress.setCancelButton(None)
        self.build_progress.show()

        self.build_output = ""
        self.build_process = QProcess()
        self.build_process.setProcessChannelMode(QProcess.ProcessChannelMode.MergedChannels)
        self.build_process.readyReadStandardOutput.connect(self._on_build_output)
        self.build_process.finished.connect(self._on_build_finished)
        self.api.log_info(f"Executing build script: {build_script_path}")

        args = ["cleanup"] if self.api.get_manager("settings").get("cleanup_after_build", True) else []
        version_str = self._release_data['tag'].lstrip('v')
        args.extend(["--version", version_str])
        if nsis_path := self.api.get_manager("settings").get("nsis_path"):
            args.extend(["--nsis-path", nsis_path])

        self.build_process.start(build_script_path, args)

    def _on_build_output(self):
        output = self.build_process.readAllStandardOutput().data().decode(errors='ignore')
        self.build_output += output
        self.api.log_info(f"[Build] {output.strip()}")

    def _on_build_finished(self, exit_code, _):
        self.build_progress.close()
        if exit_code != 0:
            error_msg = "The build script failed. See details below."
            self._show_build_error_dialog(error_msg, self.build_output)
            self._on_release_step_failed("Build script failed.")
        else:
            self.api.show_status_message("Build successful.", 3000)
            if self._is_part_of_release:
                self._current_step = "UPLOAD_ASSETS"
                self._upload_assets()

    def _show_build_error_dialog(self, summary: str, details: str):
        dialog = QMessageBox(self.main_window)
        dialog.setIcon(QMessageBox.Icon.Critical)
        dialog.setWindowTitle("Build Failed")
        dialog.setText(summary)
        text_edit = QTextEdit()
        text_edit.setReadOnly(True)
        text_edit.setFont(QFont("Consolas", 9))
        text_edit.setText(details)
        dialog.layout().addWidget(text_edit, 1, 0, 1, -1)
        dialog.exec()

    def _show_build_installer_dialog(self):
        project_path = self.project_manager.get_active_project_path()
        if not project_path:
            self.api.show_message("info", "No Project", "Please open a project to build.")
            return

        reply = QMessageBox.question(self.main_window, "Confirm Build", "This will run the project's full build. Continue?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.Cancel)
        if reply == QMessageBox.StandardButton.Yes:
            self._is_part_of_release = False
            self._release_data = {'tag': f"v{versioning.APP_VERSION}", 'build_installer': True}
            self._run_build_script(project_path)

    def _upload_assets(self):
        assets_to_upload = []
        try:
            self._temp_zip_dir = tempfile.mkdtemp()
            zip_name = f"{self._release_repo_name}-{self._release_data['tag']}.zip"
            zip_path = os.path.join(self._temp_zip_dir, zip_name)
            if self.project_manager.create_project_zip(zip_path):
                assets_to_upload.append(zip_path)
        except Exception as e:
            self.api.log_error(f"Error creating source zip: {e}")

        if self._release_data.get("build_installer"):
            dist_path = os.path.join(self._release_project_path, "dist")
            version_str = self._release_data['tag'].lstrip('v')
            installer_name = f"PuffinPyEditor_v{version_str}_Setup.exe"
            installer_path = os.path.join(dist_path, installer_name)
            
            self.api.log_info(f"Searching for installer at: {installer_path}")
            found = False
            for i in range(5):
                if os.path.exists(installer_path):
                    self.api.log_info("Installer found.")
                    assets_to_upload.append(installer_path)
                    found = True
                    break
                self.api.log_info(f"Installer not found, waiting 2 seconds... (Attempt {i+1}/5)")
                time.sleep(2)
            
            if not found:
                self._on_release_step_failed(f"Build completed, but installer not found after waiting: {installer_path}")
                return

        if not assets_to_upload:
            self.api.log_info("No assets to upload, finalizing release.")
            self._finalize_release()
            return

        self._assets_to_upload_queue = assets_to_upload
        self._upload_next_asset()

    def _upload_next_asset(self):
        if not self._assets_to_upload_queue:
            self.api.log_info("All assets uploaded. Proceeding to finalize release.")
            self._finalize_release()
            return

        asset_path = self._assets_to_upload_queue.pop(0)
        if sc_panel := self._get_sc_panel():
            sc_panel.set_ui_locked(True, f"Uploading {os.path.basename(asset_path)}...")
        self.github_manager.operation_success.connect(self._on_asset_uploaded)
        self.github_manager.operation_failed.connect(self._on_release_step_failed)
        self.github_manager.upload_asset(self._release_upload_url, asset_path)

    def _on_asset_uploaded(self, msg, _):
        if "Asset uploaded" in msg:
            self._cleanup_connections()
            self._upload_next_asset()

    def _finalize_release(self):
        self._current_step = "FINALIZE"
        if sc_panel := self._get_sc_panel():
            sc_panel.set_ui_locked(True, "Bumping version...")
        if not versioning.write_new_version(self._release_data['tag']):
            self._on_release_step_failed("Failed to write new version to VERSION.txt.")
            return
        self.main_window._update_window_title()
        self._current_step = "BUMP_VERSION_COMMIT"
        self.git_manager.git_success.connect(self._on_git_step_success)
        self.git_manager.git_error.connect(self._on_release_step_failed)
        self.git_manager.commit_files(self._release_project_path, f"ci: Release {self._release_data['tag']}")

    def _on_release_step_failed(self, error_message):
        self._cleanup_connections()
        self.api.log_error(f"Release failed at step '{self._current_step}': {error_message}")
        self.api.show_message("critical", "Release Failed",
                              f"An error occurred: {error_message}\n\nAttempting to roll back changes on GitHub...")
        tag_name = self._release_data.get('tag')
        if self._release_id:
            self.api.log_info(f"ROLLBACK: Deleting GitHub release ID {self._release_id}")
            self.github_manager.delete_release(self._release_owner, self._release_repo_name, self._release_id)
        if tag_name and self._current_step != "CREATE_TAG":
            self.api.log_info(f"ROLLBACK: Deleting remote tag '{tag_name}'")
            self.git_manager.delete_remote_tag(self._release_project_path, tag_name)
        if tag_name:
            self.api.log_info(f"ROLLBACK: Deleting local tag '{tag_name}'")
            self.git_manager.delete_tag(self._release_project_path, tag_name)

        if sc_panel := self._get_sc_panel():
            sc_panel.set_ui_locked(False, "Release failed. Rollback attempted.")
        self._cleanup_release_process()

    def _cleanup_connections(self):
        try:
            self.git_manager.git_success.disconnect()
            self.git_manager.git_error.disconnect()
            self.github_manager.operation_success.disconnect()
            self.github_manager.operation_failed.disconnect()
        except TypeError:
            pass

    def _cleanup_release_process(self):
        self.api.log_info("Cleaning up release process state.")
        self._cleanup_connections()
        self._current_step = None
        self._release_id = None
        if hasattr(self, '_assets_to_upload_queue'):
            self._assets_to_upload_queue.clear()
        if hasattr(self, 'build_process'):
            self.build_process = None
        if hasattr(self, '_temp_zip_dir') and os.path.exists(self._temp_zip_dir):
            shutil.rmtree(self._temp_zip_dir, ignore_errors=True)
            self.api.log_info(f"Cleaned up temp release directory: {self._temp_zip_dir}")
        self._is_part_of_release = False

    def _publish_repo(self, local_path):
        if not self._ensure_git_identity(local_path):
            if sc_panel := self._get_sc_panel():
                sc_panel.set_ui_locked(False, "Publish cancelled.")
            return

        repo_name, ok = QInputDialog.getText(self.main_window, "Publish to GitHub", "Repository Name:",
                                            text=os.path.basename(local_path))
        if not ok or not repo_name:
            if sc_panel := self._get_sc_panel():
                sc_panel.set_ui_locked(False, "Publish cancelled.")
            return

        description, _ = QInputDialog.getText(self.main_window, "Publish to GitHub", "Description (optional):")
        is_private = QMessageBox.question(self.main_window, "Visibility", "Make this repository private?",
                                          QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                          QMessageBox.StandardButton.No) == QMessageBox.StandardButton.Yes

        self.github_manager.operation_success.connect(lambda msg, data, path=local_path: self._on_repo_published(msg, data, path))
        self.github_manager.operation_failed.connect(lambda msg: self._get_sc_panel().set_ui_locked(False, f"Error: {msg}"))
        if sc_panel := self._get_sc_panel():
            sc_panel.set_ui_locked(True, f"Creating '{repo_name}' on GitHub...")
        self.github_manager.create_repo(repo_name, description, is_private)

    def _on_repo_published(self, msg, data, local_path):
        if "Repository" in msg and "created" in msg:
            self._cleanup_connections()
            clone_url = data.get("clone_url")
            if sc_panel := self._get_sc_panel():
                sc_panel.set_ui_locked(True, "Linking and pushing...")
            self.git_manager.publish_repo(local_path, clone_url)

    def _link_repo(self, local_path):
        dialog = SelectRepoDialog(self.github_manager, self.main_window)
        if dialog.exec() and (repo_data := dialog.selected_repo_data):
            if clone_url := repo_data.get('clone_url'):
                if sc_panel := self._get_sc_panel():
                    sc_panel.set_ui_locked(True, "Linking to remote...")
                self.git_manager.link_to_remote(local_path, clone_url)

    def _change_visibility(self, local_path):
        try:
            repo = git.Repo(local_path)
            if not repo.remotes:
                return
            owner, repo_name = self.git_manager.parse_git_url(repo.remotes.origin.url)
            if not owner or not repo_name:
                return
            is_private = QMessageBox.question(self.main_window, "Change Visibility", "Make repository private?",
                                              QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No) == QMessageBox.StandardButton.Yes
            if sc_panel := self._get_sc_panel():
                sc_panel.set_ui_locked(True, "Changing visibility...")
            self.github_manager.update_repo_visibility(owner, repo_name, is_private)
        except Exception as e:
            self.api.show_message("critical", "Error", f"Could not get repository info: {e}")

    def _show_github_dialog(self):
        if not self.github_dialog:
            self.github_dialog = GitHubDialog(self.github_manager, self.git_manager, self.main_window)
            self.github_dialog.project_cloned.connect(lambda path: self.project_manager.open_project(path))
        self.github_dialog.show()


def initialize(main_window):
    """
    Initializes the GitHub Tools plugin.
    """
    plugin = GitHubToolsPlugin(main_window)
    plugin.api.add_menu_action("tools", "GitHub Repositories...", plugin._show_github_dialog, icon_name="fa5b.github")
    return plugin
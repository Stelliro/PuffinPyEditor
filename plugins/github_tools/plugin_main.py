# PuffinPyEditor/plugins/github_tools/plugin_main.py
import os
import shutil
import tempfile
import git
import configparser
from git import Actor
from PyQt6.QtWidgets import (QInputDialog, QMessageBox, QTextEdit, QDialog,
                             QVBoxLayout, QLabel, QProgressBar, QPushButton,
                             QDialogButtonBox)
from PyQt6.QtCore import Qt, QCoreApplication, QProcess, QTimer
from PyQt6.QtGui import QFont

from app_core.puffin_api import PuffinPluginAPI
from .new_release_dialog import NewReleaseDialog
from .select_repo_dialog import SelectRepoDialog
from .github_dialog import GitHubDialog
from utils import versioning
import sys


class UploadProgressDialog(QDialog):
    """A dialog to show the real-time progress of an asset upload."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Release Progress")
        self.setMinimumWidth(600)
        self.setModal(True)
        self.setWindowFlag(Qt.WindowType.WindowCloseButtonHint, False)

        layout = QVBoxLayout(self)

        self.step_label = QLabel("Starting release...")
        font = self.step_label.font()
        font.setBold(True)
        self.step_label.setFont(font)
        layout.addWidget(self.step_label)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)
        self.progress_bar.setTextVisible(False)
        layout.addWidget(self.progress_bar)

        self.log_console = QTextEdit()
        self.log_console.setReadOnly(True)
        self.log_console.setFont(QFont("Consolas", 9))
        self.log_console.setStyleSheet("background-color: #1e1e1e; color: #d4d4d4;")
        layout.addWidget(self.log_console)

        self.button_box = QDialogButtonBox()
        self.close_button = self.button_box.addButton("Close", QDialogButtonBox.ButtonRole.RejectRole)
        self.close_button.clicked.connect(self.reject)
        self.close_button.hide()  # Hide until process is complete
        layout.addWidget(self.button_box)

    def set_step(self, step_name: str):
        self.step_label.setText(f"Step: {step_name}")

    def add_log(self, message: str, is_error: bool = False):
        color = "#FF5555" if is_error else "#D4D4D4"
        self.log_console.append(f"<span style='color:{color};'>{message}</span>")
        self.log_console.verticalScrollBar().setValue(self.log_console.verticalScrollBar().maximum())

    def show_close_button(self):
        self.close_button.show()
        self.setWindowTitle("Release Complete")


class GitHubToolsPlugin:
    def __init__(self, puffin_api: PuffinPluginAPI):
        self.api = puffin_api
        self.main_window = self.api.get_main_window()
        self.project_manager = self.api.get_manager("project")
        self.git_manager = self.api.get_manager("git")
        self.github_manager = self.api.get_manager("github")
        self.github_dialog = None
        self._release_state = {}
        self.build_process = None
        self.build_output_buffer = []
        self.progress_dialog = None

        self.api.log_info("GitHub Tools plugin initialized.")
        self.api.add_menu_action("tools", "Build Project Installer", self._show_build_installer_dialog,
                                 icon_name="fa5s.cogs")

        if sc_panel := self._get_sc_panel():
            sc_panel.create_release_requested.connect(self.show_create_release_dialog)
            sc_panel.publish_repo_requested.connect(self._publish_repo)
            sc_panel.link_to_remote_requested.connect(self._link_repo)
            sc_panel.change_visibility_requested.connect(self._change_visibility)
            self.api.log_info("GitHub Tools: Connected signals from Source Control Panel.")

    def _get_sc_panel(self):
        if hasattr(self.main_window, 'source_control_panel'): return self.main_window.source_control_panel
        return None

    def _log_to_dialog(self, message: str, is_error: bool = False):
        log_func = self.api.log_error if is_error else self.api.log_info
        log_func(f"[Release] {message}")
        if self.progress_dialog:
            self.progress_dialog.add_log(message, is_error)

    def ensure_git_identity(self, project_path: str, log_to_dialog=False) -> bool:
        """
        Ensures the local repo is configured to use an email associated with the
        logged-in GitHub account, which is required for contributions to be counted.
        It will overwrite a misconfigured local email.

        Returns True on success, False on failure.
        """
        log_func = self._log_to_dialog if log_to_dialog else self.api.log_info
        log_func("Verifying Git identity for contributions...")

        user_info = self.github_manager.get_user_info()
        if not user_info or not user_info.get('login'):
            self.api.show_message("warning", "GitHub Login Required",
                                  "You must be logged into GitHub to ensure your commits are counted as contributions.")
            return False

        # Construct the set of valid emails for this user
        valid_emails = set()
        user_name = user_info.get('login')
        public_email = user_info.get('email')
        noreply_email = f"{user_info.get('id')}+{user_name}@users.noreply.github.com"

        if public_email:
            valid_emails.add(public_email.lower())
        valid_emails.add(noreply_email.lower())

        try:
            repo = git.Repo(project_path)
            current_email = ""
            # Check for an existing email config
            try:
                with repo.config_reader() as cr:
                    current_email = cr.get_value('user', 'email', '').lower()
            except (configparser.NoSectionError, configparser.NoOptionError):
                log_func("No local or global git email is set.")
                pass  # No email is set, we can proceed to set it.

            # If the current email is not valid for contributions, overwrite it locally.
            if current_email not in valid_emails:
                log_func(f"Current git email ('{current_email}') is not valid for contributions. Updating local config.")
                with repo.config_writer() as config:
                    config.set_value('user', 'name', user_name)
                    # Prefer the noreply email for privacy and consistency
                    config.set_value('user', 'email', noreply_email)
                log_func(f"Successfully set local git identity to '{user_name} <{noreply_email}>'.")
            else:
                log_func(f"Verified Git identity is correctly set to '{current_email}'.")

            return True

        except Exception as e:
            self.api.show_message("critical", "Git Configuration Error", f"Could not verify or set Git configuration: {e}")
            return False

    def show_create_release_dialog(self, project_path: str = None):
        if not project_path: project_path = self.project_manager.get_active_project_path()
        if not project_path:
            self.api.show_message("info", "No Project Open", "Please open a project to create a release.")
            return
        self._create_release(project_path)

    def _create_release(self, project_path):
        dialog = NewReleaseDialog(project_path, self.git_manager, self.main_window)
        if not dialog.exec():
            self.api.show_status_message("Release cancelled.", 3000)
            return

        self.progress_dialog = UploadProgressDialog(self.main_window)
        self.progress_dialog.show()

        if not self.ensure_git_identity(project_path, log_to_dialog=True):
            self._on_release_step_failed("Git identity misconfiguration. Commit cannot be created.")
            return

        try:
            repo = git.Repo(project_path)
            if not repo.remotes: self._on_release_step_failed("This project has no remote repository."); return
            remote_url = repo.remotes.origin.url
            if 'github.com' not in remote_url: self._on_release_step_failed(
                "The 'origin' remote is not a GitHub repository."); return
            owner, repo_name = self.git_manager.parse_git_url(remote_url)
            if not owner or not repo_name: self._on_release_step_failed(
                "Could not parse owner/repo from remote."); return
        except Exception as e:
            self._on_release_step_failed(f"Could not analyze repository: {e}"); return

        self._release_state = {'dialog_data': dialog.get_release_data(), 'project_path': project_path, 'owner': owner,
                               'repo_name': repo_name, 'step': None}
        self._advance_release_state("CREATE_TAG")

    def _advance_release_state(self, next_step):
        self._release_state['step'] = next_step
        step = next_step
        dialog_data, project_path = self._release_state['dialog_data'], self._release_state['project_path']
        self._cleanup_all_connections()
        step_title = step.replace('_', ' ').title()
        if sc_panel := self._get_sc_panel(): sc_panel.set_ui_locked(True, f"Step: {step_title}...")
        if self.progress_dialog: self.progress_dialog.set_step(step_title)

        if step == "CREATE_TAG":
            self.git_manager.git_success.connect(self._on_release_step_succeeded)
            self.git_manager.git_error.connect(self._on_release_step_failed)
            self.git_manager.create_tag(project_path, dialog_data['tag'], dialog_data['title'])
        elif step == "PUSH_TAG":
            self.git_manager.git_success.connect(self._on_release_step_succeeded)
            self.git_manager.git_error.connect(self._on_release_step_failed)
            self.git_manager.push_specific_tag(project_path, dialog_data['tag'])
        elif step == "CREATE_RELEASE":
            self.github_manager.operation_success.connect(self._on_release_step_succeeded)
            self.github_manager.operation_failed.connect(self._on_release_step_failed)
            self.github_manager.create_github_release(
                owner=self._release_state['owner'], repo=self._release_state['repo_name'], tag_name=dialog_data['tag'],
                name=dialog_data['title'], body=dialog_data['notes'], prerelease=dialog_data['prerelease'])
        elif step == "BUILD_ASSETS":
            self._run_build_script(project_path)
        elif step == "UPLOAD_ASSETS":
            self._upload_assets()
        elif step == "BUMP_VERSION_COMMIT":
            if not versioning.write_new_version(dialog_data['tag']):
                self._on_release_step_failed("Failed to write new version to VERSION.txt.")
                return
            self.main_window._update_window_title()

            # THE FIX: Create the author object before committing.
            try:
                repo = git.Repo(project_path)
                with repo.config_reader() as cr:
                    name = cr.get_value('user', 'name')
                    email = cr.get_value('user', 'email')
                author = Actor(name, email)
            except Exception as e:
                self._on_release_step_failed(f"Could not read Git author info to create commit: {e}")
                return

            self.git_manager.git_success.connect(self._on_release_step_succeeded)
            self.git_manager.git_error.connect(self._on_release_step_failed)
            self.git_manager.commit_files(project_path, f"ci: Release {dialog_data['tag']}", author)

        elif step == "FINAL_PUSH":
            self.git_manager.git_success.connect(self._on_release_step_succeeded)
            self.git_manager.git_error.connect(self._on_release_step_failed)
            self.git_manager.push(project_path)

    def _on_release_step_succeeded(self, msg, data):
        step = self._release_state.get('step')
        self._log_to_dialog(f"SUCCESS on step '{step}': {msg}")
        if step == "CREATE_TAG":
            self._advance_release_state("PUSH_TAG")
        elif step == "PUSH_TAG":
            self._advance_release_state("CREATE_RELEASE")
        elif step == "CREATE_RELEASE":
            self._release_state['release_info'] = data.get("release_data", {})
            self._advance_release_state(
                "BUILD_ASSETS" if self._release_state['dialog_data'].get("build_installer") else "UPLOAD_ASSETS")
        elif step == "UPLOAD_ASSET":
            self._upload_next_asset()
        elif step == "BUMP_VERSION_COMMIT":
            self._advance_release_state("FINAL_PUSH")
        elif step == "FINAL_PUSH":
            self._cleanup_release_process(success=True)

    def _run_build_script(self, project_path):
        build_script_path = os.path.join(project_path, "installer", "build.py")
        if not os.path.exists(build_script_path):
            self._on_release_step_failed(f"Build script not found at '{build_script_path}'.")
            return

        self.build_output_buffer.clear()
        args = []
        if self.api.get_manager("settings").get("cleanup_after_build", True):
            args.append("--cleanup")

        version_str = self._release_state['dialog_data']['tag'].lstrip('v')
        args.extend(["--version", version_str])

        if nsis_path := self.api.get_manager("settings").get("nsis_path"):
            args.extend(["--nsis-path", nsis_path])

        self.build_process = QProcess()
        self.build_process.setProcessChannelMode(QProcess.ProcessChannelMode.MergedChannels)
        self.build_process.readyReadStandardOutput.connect(self._on_build_stdout)
        self.build_process.finished.connect(self._on_build_finished)

        self.build_process.setWorkingDirectory(project_path)
        program = sys.executable
        command_args = [build_script_path] + args
        self._log_to_dialog(f"Executing build in '{project_path}': {os.path.basename(program)} {' '.join(command_args)}")

        self.build_process.start(program, command_args)

    def _on_build_stdout(self):
        output = self.build_process.readAllStandardOutput().data().decode(errors='ignore');
        self.build_output_buffer.append(output);
        self._log_to_dialog(f"[Build] {output.strip()}")

    def _on_build_finished(self, exit_code, exit_status):
        if exit_code == 0:
            self._log_to_dialog("Build successful."); self._advance_release_state("UPLOAD_ASSETS")
        else:
            self._show_build_error_dialog("The build script failed. See details below.",
                                          "".join(self.build_output_buffer)); self._on_release_step_failed(
                f"Build script failed with exit code {exit_code}.")
        self.build_process.deleteLater();
        self.build_process = None

    def _show_build_error_dialog(self, summary: str, details: str):
        self._log_to_dialog(f"ERROR: {summary}", is_error=True);
        dialog = QMessageBox(self.main_window)
        dialog.setIcon(QMessageBox.Icon.Critical)
        dialog.setWindowTitle("Build Failed")
        dialog.setText(summary)
        dialog.layout().setColumnStretch(1, 1)
        text_edit = QTextEdit()
        text_edit.setReadOnly(True)
        text_edit.setFont(QFont("Consolas", 9))
        text_edit.setText(details)
        text_edit.setMinimumSize(600, 300)
        dialog.layout().addWidget(text_edit, 1, 0, 1, -1)
        dialog.exec()

    def _show_build_installer_dialog(self):
        project_path = self.project_manager.get_active_project_path()
        if not project_path: self.api.show_message("info", "No Project", "Please open a project."); return
        if QMessageBox.question(self.main_window, "Confirm Build", "This will run the project's full build. Continue?",
                                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.Cancel) == QMessageBox.StandardButton.Yes:
            self._release_state = {'dialog_data': {'tag': f"v{versioning.APP_VERSION}", 'build_installer': True},
                                   'project_path': project_path}
            self.progress_dialog = UploadProgressDialog(self.main_window);
            self.progress_dialog.show()
            self._run_build_script(project_path)

    def _upload_assets(self):
        assets_to_upload = []
        dialog_data = self._release_state['dialog_data']
        project_path = self._release_state['project_path']
        
        if dialog_data.get("build_installer"):
            # THE FIX: Look for the installer in the correct top-level /dist directory
            dist_path = os.path.join(project_path, "dist")
            version_str = dialog_data['tag'].lstrip('v')
            installer_name = f"PuffinPyEditor_v{version_str}_Setup.exe"
            installer_path = os.path.join(dist_path, installer_name)

            if os.path.exists(installer_path):
                assets_to_upload.append(installer_path)
            else:
                self._on_release_step_failed(
                    f"Installer not found at '{installer_path}'. Build may have failed or produced an unexpected filename.")
                return

        # --- Create source code zip ---
        repo_name = self._release_state['repo_name']
        try:
            temp_zip_dir = tempfile.mkdtemp()
            self._release_state['temp_dir'] = temp_zip_dir
            # THE FIX: Define zip_name and zip_path separately to fix UnboundLocalError
            zip_name = f"{repo_name}-{dialog_data['tag']}.zip"
            zip_path = os.path.join(temp_zip_dir, zip_name)

            if self.project_manager.create_project_zip(zip_path):
                assets_to_upload.append(zip_path)
            else:
                self._log_to_dialog("Warning: Failed to create source code zip asset.", is_error=True)
        except Exception as e:
            self._log_to_dialog(f"Error creating source zip: {e}", is_error=True)

        if not assets_to_upload:
            self._log_to_dialog("No assets to upload, moving to finalize.")
            self._advance_release_state("BUMP_VERSION_COMMIT")
            return

        self._release_state['asset_queue'] = assets_to_upload
        self._log_to_dialog(f"Found {len(assets_to_upload)} asset(s) to upload.")
        self._upload_next_asset()

    def _upload_next_asset(self):
        asset_queue = self._release_state.get('asset_queue', [])
        if not asset_queue:
            self._log_to_dialog("All assets uploaded successfully.")
            self._advance_release_state("BUMP_VERSION_COMMIT")
            return
        asset_path, upload_url = asset_queue.pop(0), self._release_state['release_info']['upload_url']
        if self.progress_dialog: self.progress_dialog.set_step(f"Uploading {os.path.basename(asset_path)}")
        self._release_state['step'] = "UPLOAD_ASSET"
        self.github_manager.operation_success.connect(self._on_release_step_succeeded)
        self.github_manager.operation_failed.connect(self._on_release_step_failed)
        self.github_manager.upload_asset(upload_url, asset_path)

    def _on_release_step_failed(self, error_message):
        step = self._release_state.get('step', 'UNKNOWN');
        failure_msg = f"An error occurred at step '{step}': {error_message}"
        self._log_to_dialog(failure_msg, is_error=True)
        if self.progress_dialog: self.progress_dialog.show_close_button();
        if step in ["BUMP_VERSION_COMMIT",
                    "FINAL_PUSH"]: failure_msg += "\n\nA local commit may have been created. You might need to undo it manually (e.g., 'git reset HEAD~1')."
        self.api.show_message("critical", "Release Failed", f"{failure_msg}\n\nAttempting to roll back...")
        tag_name, release_id = self._release_state.get('dialog_data', {}).get('tag'), self._release_state.get(
            'release_info', {}).get('id')
        if release_id: self._log_to_dialog(
            f"ROLLBACK: Deleting GitHub release ID {release_id}"); self.github_manager.delete_release(
            self._release_state['owner'], self._release_state['repo_name'], release_id)
        if tag_name and step != "CREATE_TAG": self._log_to_dialog(
            f"ROLLBACK: Deleting remote tag '{tag_name}'"); self.git_manager.delete_remote_tag(
            self._release_state['project_path'], tag_name)
        if tag_name: self._log_to_dialog(f"ROLLBACK: Deleting local tag '{tag_name}'"); self.git_manager.delete_tag(
            self._release_state['project_path'], tag_name)
        self._cleanup_release_process()

    def _cleanup_all_connections(self):
        try:
            self.git_manager.git_success.disconnect(self._on_release_step_succeeded)
            self.git_manager.git_error.disconnect(self._on_release_step_failed)
            self.github_manager.operation_success.disconnect(self._on_release_step_succeeded)
            self.github_manager.operation_failed.disconnect(self._on_release_step_failed)
        except TypeError:
            pass

    def _cleanup_release_process(self, success=False):
        self._log_to_dialog("Cleaning up release process state.")
        self._cleanup_all_connections()
        if sc_panel := self._get_sc_panel(): sc_panel.set_ui_locked(False, "Release process finished.")
        if self.progress_dialog:
            if success:
                self.progress_dialog.add_log("\n--- RELEASE COMPLETE ---")
            else:
                self.progress_dialog.add_log("\n--- RELEASE FAILED ---")
            self.progress_dialog.show_close_button()
            self.progress_dialog = None
        if temp_dir := self._release_state.get('temp_dir'):
            if os.path.exists(temp_dir): shutil.rmtree(temp_dir, ignore_errors=True); self._log_to_dialog(
                f"Cleaned temp dir: {temp_dir}")
        self._release_state = {}

    def _publish_repo(self, local_path):
        repo_name, ok = QInputDialog.getText(self.main_window, "Publish to GitHub", "Repository Name:",
                                             text=os.path.basename(local_path))
        if not ok or not repo_name:
            if sc_panel := self._get_sc_panel(): sc_panel.set_ui_locked(False, "Publish cancelled."); return
        
        if not self.ensure_git_identity(local_path):
            if sc_panel := self._get_sc_panel(): sc_panel.set_ui_locked(False, "Publish cancelled: Git identity not set.")
            return

        description, _ = QInputDialog.getText(self.main_window, "Publish to GitHub", "Description (optional):")
        is_private = QMessageBox.question(self.main_window, "Visibility", "Make this repository private?",
                                          QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                          QMessageBox.StandardButton.No) == QMessageBox.StandardButton.Yes

        def on_repo_created(msg, data, path=local_path):
            if "Repository" in msg and "created" in msg:
                self._cleanup_all_connections();
                clone_url = data.get("clone_url")
                if sc_panel := self._get_sc_panel(): sc_panel.set_ui_locked(True, "Linking and pushing...")
                self.git_manager.publish_repo(path, clone_url)

        self.github_manager.operation_success.connect(on_repo_created)
        self.github_manager.operation_failed.connect(
            lambda msg: self._get_sc_panel().set_ui_locked(False, f"Error: {msg}"))
        if sc_panel := self._get_sc_panel(): sc_panel.set_ui_locked(True, f"Creating '{repo_name}' on GitHub...")
        self.github_manager.create_repo(repo_name, description, is_private)

    def _link_repo(self, local_path):
        dialog = SelectRepoDialog(self.github_manager, self.main_window)
        if dialog.exec() and (repo_data := dialog.selected_repo_data):
            
            if not self.ensure_git_identity(local_path):
                if sc_panel := self._get_sc_panel(): sc_panel.set_ui_locked(False, "Link cancelled: Git identity not set.")
                return

            if clone_url := repo_data.get('clone_url'):
                if sc_panel := self._get_sc_panel(): sc_panel.set_ui_locked(True, "Linking to remote...")
                self.git_manager.link_to_remote(local_path, clone_url)

    def _change_visibility(self, local_path):
        try:
            repo = git.Repo(local_path);
            if not repo.remotes: return
            remote_url, (owner, repo_name) = repo.remotes.origin.url, self.git_manager.parse_git_url(remote_url)
            if not owner or not repo_name: return
            is_private = QMessageBox.question(self.main_window, "Change Visibility", "Make repository private?",
                                              QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No) == QMessageBox.StandardButton.Yes
            if sc_panel := self._get_sc_panel(): sc_panel.set_ui_locked(True, "Changing visibility...")
            self.github_manager.update_repo_visibility(owner, repo_name, is_private)
        except Exception as e:
            self.api.show_message("critical", "Error", f"Could not get repository info: {e}")

    def _show_github_dialog(self):
        if not self.github_dialog:
            self.github_dialog = GitHubDialog(self.github_manager, self.git_manager, self.main_window)
            self.github_dialog.project_cloned.connect(lambda path: self.project_manager.open_project(path))
        self.github_dialog.show()


def initialize(puffin_api: PuffinPluginAPI):
    """Initializes the GitHub Tools plugin."""
    plugin = GitHubToolsPlugin(puffin_api)
    puffin_api.add_menu_action("tools", "GitHub Repositories...", plugin._show_github_dialog, icon_name="fa5b.github")
    puffin_api.add_menu_action("tools", "New Release...", plugin.show_create_release_dialog, icon_name="fa5s.tag")
    return plugin
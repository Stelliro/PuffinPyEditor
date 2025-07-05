# PuffinPyEditor/plugins/github_tools/plugin_main.py
import os
import shutil
import tempfile
import git
from PyQt6.QtWidgets import (QInputDialog, QMessageBox, QProgressDialog,
                             QTextEdit)
from PyQt6.QtCore import Qt, QCoreApplication, QProcess
from PyQt6.QtGui import QFont

from app_core.puffin_api import PuffinPluginAPI
from .new_release_dialog import NewReleaseDialog
from .select_repo_dialog import SelectRepoDialog
from .github_dialog import GitHubDialog
from .upload_progress_dialog import UploadProgressDialog
from utils import versioning

class GitHubToolsPlugin:
    def __init__(self, puffin_api: PuffinPluginAPI):
        self.api = puffin_api
        self.main_window = self.api.get_main_window()
        self.project_manager = self.api.get_manager("project")
        self.git_manager = self.api.get_manager("git")
        self.github_manager = self.api.get_manager("github")
        self.github_dialog = None
        self._release_state = {}
        self.build_process = None # For handling the async build process
        self.build_output_buffer = []
        self.upload_dialog = None

        self.api.log_info("GitHub Tools plugin initialized.")
        self.api.add_menu_action("tools", "Build Project Installer", self._show_build_installer_dialog, icon_name="fa5s.cogs")

        if sc_panel := self._get_sc_panel():
            sc_panel.create_release_requested.connect(self.show_create_release_dialog)
            sc_panel.publish_repo_requested.connect(self._publish_repo)
            sc_panel.link_to_remote_requested.connect(self._link_repo)
            sc_panel.change_visibility_requested.connect(self._change_visibility)
            self.api.log_info("GitHub Tools: Connected signals from Source Control Panel.")

    def _get_sc_panel(self):
        """Correctly retrieves the source control panel from the main window instance."""
        if hasattr(self.main_window, 'source_control_panel'):
            return self.main_window.source_control_panel
        return None

    def _ensure_git_identity(self, project_path: str) -> bool:
        self.api.log_info("Checking Git author information...")
        user_info = self.github_manager.get_user_info()
        if not user_info:
            self.api.show_message("warning", "GitHub User Not Found",
                                  "Could not fetch GitHub user info. "
                                  "Please log in.")
            return False
        try:
            repo = git.Repo(project_path)
            user_name = user_info.get('login')
            user_email = user_info.get('email')

            if not user_email:
                user_email = (f"{user_info.get('id')}+{user_name}"
                              "@users.noreply.github.com")
                self.api.log_info(
                    "GitHub email is private. Falling back to no-reply "
                    "address. To see contributions, enable 'Keep my email "
                    "addresses private' in GitHub settings."
                )
            self.api.log_info(f"Setting git author for this operation to: "
                              f"Name='{user_name}', Email='{user_email}'")

            with repo.config_writer() as config:
                config.set_value('user', 'name', user_name)
                config.set_value('user', 'email', user_email)
            self.api.log_info("Git author configured for this operation.")
            return True
        except Exception as e:
            self.api.show_message("warning", "Git Config Failed",
                                  f"Failed to set Git author info: {e}")
            return False

    def show_create_release_dialog(self, project_path: str = None):
        """
        Public method to show the 'Create Release' dialog. Intended to be
        called from other plugins or UI elements.
        """
        if not project_path:
            project_path = self.project_manager.get_active_project_path()
        
        if not project_path:
            self.api.show_message("info", "No Project Open",
                                  "Please open a project to create a release.")
            return
        self._create_release(project_path)

    def _create_release(self, project_path):
        if not self._ensure_git_identity(project_path):
            self.api.show_status_message(
                "Release cancelled: Git identity misconfiguration.", 5000)
            return

        try:
            repo = git.Repo(project_path)
            if not repo.remotes:
                self.api.show_message("warning", "No Remote",
                                      "This project has no remote repository.")
                return
            remote_url = repo.remotes.origin.url
            if 'github.com' not in remote_url:
                self.api.show_message(
                    "warning", "Not a GitHub Remote",
                    "The 'origin' remote of this project does not appear "
                    "to be a GitHub repository."
                )
                return

            owner, repo_name = self.git_manager.parse_git_url(remote_url)
            if not owner or not repo_name:
                self.api.show_message(
                    "critical", "Error",
                    "Could not parse owner/repo from remote.")
                return
        except Exception as e:
            self.api.show_message(
                "critical", "Error", f"Could not analyze repository: {e}")
            return

        dialog = NewReleaseDialog(
            project_path, self.git_manager, self.main_window)
        if not dialog.exec():
            self.api.show_status_message("Release cancelled.", 3000)
            return

        self._release_state = {
            'dialog_data': dialog.get_release_data(),
            'project_path': project_path,
            'owner': owner,
            'repo_name': repo_name,
            'step': None
        }

        self._advance_release_state("CREATE_TAG")

    def _advance_release_state(self, next_step):
        self._release_state['step'] = next_step
        step = self._release_state['step']
        dialog_data = self._release_state['dialog_data']
        project_path = self._release_state['project_path']

        self._cleanup_all_connections()

        if sc_panel := self._get_sc_panel():
            sc_panel.set_ui_locked(
                True, f"Step: {step.replace('_', ' ').title()}...")

        if step == "CREATE_TAG":
            self.git_manager.git_success.connect(
                self._on_release_step_succeeded)
            self.git_manager.git_error.connect(self._on_release_step_failed)
            self.git_manager.create_tag(
                project_path, dialog_data['tag'], dialog_data['title'])
        elif step == "PUSH_TAG":
            self.git_manager.git_success.connect(
                self._on_release_step_succeeded)
            self.git_manager.git_error.connect(self._on_release_step_failed)
            self.git_manager.push_specific_tag(
                project_path, dialog_data['tag'])
        elif step == "CREATE_RELEASE":
            self.github_manager.operation_success.connect(
                self._on_release_step_succeeded)
            self.github_manager.operation_failed.connect(
                self._on_release_step_failed)
            self.github_manager.create_github_release(
                owner=self._release_state['owner'],
                repo=self._release_state['repo_name'],
                tag_name=dialog_data['tag'], name=dialog_data['title'],
                body=dialog_data['notes'],
                prerelease=dialog_data['prerelease'])
        elif step == "BUILD_ASSETS":
            self._run_build_script(project_path)
        elif step == "UPLOAD_ASSETS":
            self.upload_dialog = UploadProgressDialog(self.main_window)
            self.upload_dialog.show()
            self._upload_assets()
        elif step == "BUMP_VERSION_COMMIT":
            if not versioning.write_new_version(dialog_data['tag']):
                self._on_release_step_failed(
                    "Failed to write new version to VERSION.txt.")
                return
            self.main_window._update_window_title()
            self.git_manager.git_success.connect(
                self._on_release_step_succeeded)
            self.git_manager.git_error.connect(self._on_release_step_failed)
            self.git_manager.commit_files(
                project_path, f"ci: Release {dialog_data['tag']}")
        elif step == "FINAL_PUSH":
            self.git_manager.git_success.connect(
                self._on_release_step_succeeded)
            self.git_manager.git_error.connect(self._on_release_step_failed)
            self.git_manager.push(project_path)

    def _on_release_step_succeeded(self, msg, data):
        step = self._release_state.get('step')
        self.api.log_info(f"SUCCESS on step '{step}': {msg}")

        if step == "CREATE_TAG":
            self._advance_release_state("PUSH_TAG")
        elif step == "PUSH_TAG":
            self._advance_release_state("CREATE_RELEASE")
        elif step == "CREATE_RELEASE":
            self._release_state['release_info'] = data.get("release_data", {})
            if dialog_data := self._release_state.get('dialog_data'):
                if dialog_data.get("build_installer"):
                    self._advance_release_state("BUILD_ASSETS")
                else:
                    self._advance_release_state("UPLOAD_ASSETS")
        elif step == "UPLOAD_ASSET":
            if self.upload_dialog:
                self.upload_dialog.add_log(f"OK: {os.path.basename(data.get('asset_data', {}).get('name', '...'))}")
            self._upload_next_asset()
        elif step == "BUMP_VERSION_COMMIT":
            self._advance_release_state("FINAL_PUSH")
        elif step == "FINAL_PUSH":
            tag = self._release_state['dialog_data']['tag']
            success_msg = f"Release '{tag}' published successfully!"
            self.api.show_status_message(success_msg, 5000)
            QMessageBox.information(self.main_window, "Success", success_msg)
            self._cleanup_release_process()

    def _run_build_script(self, project_path):
        build_script = os.path.join(project_path, "installer", "build.bat")
        if not os.path.exists(build_script):
            self._on_release_step_failed(f"Build script not found at '{build_script}'.")
            return

        self.build_output_buffer.clear()
        
        args = [build_script]
        if self.api.get_manager("settings").get("cleanup_after_build", True):
            args.append("cleanup")
        version_str = self._release_state['dialog_data']['tag'].lstrip('v')
        args.extend(["--version", version_str])
        if nsis_path := self.api.get_manager("settings").get("nsis_path"):
            args.extend(["--nsis-path", nsis_path])

        self.build_process = QProcess()
        self.build_process.setProcessChannelMode(QProcess.ProcessChannelMode.MergedChannels)
        self.build_process.readyReadStandardOutput.connect(self._on_build_stdout)
        self.build_process.finished.connect(self._on_build_finished)
        
        program = args[0]
        arguments = args[1:]
        
        self.api.log_info(f"Executing build script with QProcess: {program} {' '.join(arguments)}")
        self.build_process.setWorkingDirectory(project_path)
        self.build_process.start(program, arguments)

    def _on_build_stdout(self):
        output = self.build_process.readAllStandardOutput().data().decode(errors='ignore')
        self.build_output_buffer.append(output)
        self.api.log_info(f"[Build] {output.strip()}")

    def _on_build_finished(self, exit_code, exit_status):
        if exit_code == 0:
            self.api.show_status_message("Build successful.", 3000)
            self._advance_release_state("UPLOAD_ASSETS")
        else:
            error_msg = "The build script failed. See details below."
            full_output = "".join(self.build_output_buffer)
            self._show_build_error_dialog(error_msg, full_output)
            self._on_release_step_failed(f"Build script failed with exit code {exit_code}.")
        
        self.build_process.deleteLater()
        self.build_process = None

    def _show_build_error_dialog(self, summary: str, details: str):
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
        if not project_path:
            self.api.show_message("info", "No Project", "Please open a project.")
            return

        reply = QMessageBox.question(self, "Confirm Build", "This will run the project's full build. Continue?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.Cancel)
        if reply == QMessageBox.StandardButton.Yes:
            self._release_state = {'dialog_data': {'tag': f"v{versioning.APP_VERSION}", 'build_installer': True},
                                   'project_path': project_path}
            self._run_build_script(project_path)

    def _upload_assets(self):
        assets_to_upload = []
        dialog_data = self._release_state['dialog_data']
        project_path = self._release_state['project_path']

        # --- Gatekeeper: Check for installer if required ---
        if dialog_data.get("build_installer"):
            dist_path = os.path.join(project_path, "dist")
            version_str = dialog_data['tag'].lstrip('v')
            installer_name = f"PuffinPyEditor_v{version_str}_Setup.exe"
            installer_path = os.path.join(dist_path, installer_name)
            
            if os.path.exists(installer_path):
                assets_to_upload.append(installer_path)
            else:
                error_msg = f"Installer not found at '{installer_path}'. A successful build did not produce the expected asset."
                self.api.log_error(error_msg)
                self._on_release_step_failed(error_msg)
                return

        # --- Proceed with other assets only if the gatekeeper passed ---
        repo_name = self._release_state['repo_name']
        try:
            temp_zip_dir = tempfile.mkdtemp()
            self._release_state['temp_dir'] = temp_zip_dir
            zip_name = f"{repo_name}-{dialog_data['tag']}.zip"
            zip_path = os.path.join(temp_zip_dir, zip_name)
            if self.project_manager.create_project_zip(zip_path):
                assets_to_upload.append(zip_path)
            else:
                self.api.log_warning("Failed to create source code zip asset.")
        except Exception as e:
            self.api.log_error(f"Error creating source zip: {e}")

        if not assets_to_upload:
            self.api.log_info("No assets to upload, moving to finalize.")
            if self.upload_dialog:
                self.upload_dialog.close()
                self.upload_dialog = None
            self._advance_release_state("BUMP_VERSION_COMMIT")
            return

        # --- Start the upload process ---
        self._release_state['asset_queue'] = assets_to_upload
        if self.upload_dialog:
             self.upload_dialog.add_log(f"Found {len(assets_to_upload)} asset(s) to upload.")
        self._upload_next_asset()

    def _upload_next_asset(self):
        asset_queue = self._release_state.get('asset_queue', [])
        if not asset_queue:
            self.api.log_info("All assets uploaded. Moving to finalize.")
            if self.upload_dialog:
                self.upload_dialog.close()
                self.upload_dialog = None
            self._advance_release_state("BUMP_VERSION_COMMIT")
            return

        asset_path = asset_queue.pop(0)
        upload_url = self._release_state.get('release_info', {}).get('upload_url')
        if sc_panel := self._get_sc_panel():
            asset_name = os.path.basename(asset_path)
            sc_panel.set_ui_locked(True, f"Uploading {asset_name}...")

        if self.upload_dialog:
            self.upload_dialog.update_progress(os.path.basename(asset_path), 0)
            self.upload_dialog.add_log(f"Starting upload of {os.path.basename(asset_path)}...")
            
        self._release_state['step'] = "UPLOAD_ASSET"
        self.github_manager.operation_success.connect(self._on_release_step_succeeded)
        self.github_manager.operation_failed.connect(self._on_release_step_failed)
        self.github_manager.upload_asset(upload_url, asset_path)

    def _on_release_step_failed(self, error_message):
        step = self._release_state.get('step', 'UNKNOWN')
        failure_msg = f"An error occurred at step '{step}': {error_message}"
        if self.upload_dialog:
            self.upload_dialog.add_log(f"ERROR: {failure_msg}")
            # Give user a moment to see the error, then close
            QCoreApplication.processEvents() # Process UI updates
            QMessageBox.critical(self.upload_dialog, "Upload Failed", "The upload process failed. See logs for details.")
            self.upload_dialog.close()
            self.upload_dialog = None

        if step in ["BUMP_VERSION_COMMIT", "FINAL_PUSH"]:
            failure_msg += "\n\nA local commit to bump the version may have been created. You might need to undo it manually (e.g., 'git reset HEAD~1')."

        self.api.log_error(f"Release failed: {failure_msg}")
        self.api.show_message("critical", "Release Failed", f"{failure_msg}\n\nAttempting to roll back...")

        tag_name = self._release_state.get('dialog_data', {}).get('tag')
        release_id = self._release_state.get('release_info', {}).get('id')

        if release_id:
            msg = f"ROLLBACK: Deleting GitHub release ID {release_id}"
            self.api.log_info(msg)
            self.github_manager.delete_release(self._release_state['owner'], self._release_state['repo_name'], release_id)
        if tag_name and step != "CREATE_TAG":
            msg = f"ROLLBACK: Deleting remote tag '{tag_name}'"
            self.api.log_info(msg)
            self.git_manager.delete_remote_tag(self._release_state['project_path'], tag_name)
        if tag_name:
            self.api.log_info(f"ROLLBACK: Deleting local tag '{tag_name}'")
            self.git_manager.delete_tag(self._release_state['project_path'], tag_name)

        self._cleanup_release_process()

    def _cleanup_all_connections(self):
        try:
            self.git_manager.git_success.disconnect(self._on_release_step_succeeded)
            self.git_manager.git_error.disconnect(self._on_release_step_failed)
            self.github_manager.operation_success.disconnect(self._on_release_step_succeeded)
            self.github_manager.operation_failed.disconnect(self._on_release_step_failed)
        except TypeError:
            pass

    def _cleanup_release_process(self):
        self.api.log_info("Cleaning up release process state.")
        self._cleanup_all_connections()

        if sc_panel := self._get_sc_panel():
            sc_panel.set_ui_locked(False, "Release process finished.")

        temp_dir = self._release_state.get('temp_dir')
        if temp_dir and os.path.exists(temp_dir):
            shutil.rmtree(temp_dir, ignore_errors=True)
            self.api.log_info(f"Cleaned temp dir: {temp_dir}")

        self._release_state = {}

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

        def on_repo_created(msg, data, path=local_path):
            if "Repository" in msg and "created" in msg:
                self._cleanup_all_connections()
                clone_url = data.get("clone_url")
                if sc_panel := self._get_sc_panel():
                    sc_panel.set_ui_locked(True, "Linking and pushing...")
                self.git_manager.publish_repo(path, clone_url)

        self.github_manager.operation_success.connect(on_repo_created)
        self.github_manager.operation_failed.connect(
            lambda msg: self._get_sc_panel().set_ui_locked(False, f"Error: {msg}"))
        if sc_panel := self._get_sc_panel():
            sc_panel.set_ui_locked(True, f"Creating '{repo_name}' on GitHub...")
        self.github_manager.create_repo(repo_name, description, is_private)

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
            remote_url = repo.remotes.origin.url
            owner, repo_name = self.git_manager.parse_git_url(remote_url)
            if not owner or not repo_name:
                return
            is_private = QMessageBox.question(self.main_window, "Change Visibility", "Make repository private?",
                                              QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                                              ) == QMessageBox.StandardButton.Yes

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


def initialize(puffin_api: PuffinPluginAPI):
    """Initializes the GitHub Tools plugin."""
    plugin = GitHubToolsPlugin(puffin_api)
    puffin_api.add_menu_action("tools", "GitHub Repositories...", plugin._show_github_dialog, icon_name="fa5b.github")
    # This action is now effectively a duplicate, but we'll leave it in the Tools menu for discoverability.
    # The main interaction point will be the button in the Source Control panel.
    puffin_api.add_menu_action("tools", "New Release...", plugin.show_create_release_dialog, icon_name="fa5s.tag")
    return plugin
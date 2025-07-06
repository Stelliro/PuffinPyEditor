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
from PyQt6.QtCore import Qt
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
        self.close_button.hide()
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
        self.progress_dialog = None
        self.api.log_info("GitHub Tools plugin initialized.")
        if sc_panel := self._get_sc_panel():
            sc_panel.create_release_requested.connect(self.show_create_release_dialog)
            sc_panel.publish_repo_requested.connect(self._publish_repo)
            sc_panel.link_to_remote_requested.connect(self._link_repo)
            sc_panel.change_visibility_requested.connect(self._change_visibility)
            self.api.log_info("GitHub Tools: Connected signals from Source Control Panel.")

    def _get_sc_panel(self):
        return getattr(self.main_window, 'source_control_panel', None)

    def _log_to_dialog(self, message: str, is_error: bool = False):
        log_func = self.api.log_error if is_error else self.api.log_info
        log_func(f"[Release] {message}")
        if self.progress_dialog:
            self.progress_dialog.add_log(message, is_error)

    def ensure_git_identity(self, project_path: str) -> bool:
        user_info = self.github_manager.get_user_info()
        if not (user_info and user_info.get('login')):
            self.api.show_message("warning", "GitHub Login Required", "You must be logged into GitHub.")
            return False
        user_name, user_id = user_info.get('login'), user_info.get('id')
        valid_emails = {f"{user_id}+{user_name}@users.noreply.github.com"}
        if public_email := user_info.get('email'):
            valid_emails.add(public_email.lower())
        try:
            repo = git.Repo(project_path)
            with repo.config_reader() as cr:
                current_email = cr.get_value('user', 'email', '').lower()
            if current_email not in valid_emails:
                with repo.config_writer() as cw:
                    cw.set_value('user', 'name', user_name)
                    cw.set_value('user', 'email', next(iter(valid_emails)))
                self.api.show_status_message("Updated local Git identity for GitHub.", 3000)
            return True
        except Exception as e:
            self.api.show_message("critical", "Git Config Error", f"Could not set Git identity: {e}")
            return False

    def show_create_release_dialog(self, project_path: str = None):
        if not project_path: project_path = self.project_manager.get_active_project_path()
        if not project_path:
            self.api.show_message("info", "No Project", "Please open a project to create a release.")
            return
        self._prepare_repository_for_release(project_path)

    def _prepare_repository_for_release(self, path: str):
        self.api.show_status_message("Verifying repository state...")
        
        try:
            repo = git.Repo(path)
            if repo.is_dirty(untracked_files=True):
                self.api.show_message("critical", "Uncommitted Changes", "Your repository has uncommitted changes or untracked files. Please commit or stash them before creating a release.")
                return
            if os.path.exists(os.path.join(repo.git_dir, 'MERGE_HEAD')):
                if self._handle_unresolved_merge(repo):
                    self.api.show_status_message("Re-checking repository state after merge abort...")
                    self._prepare_repository_for_release(path)
                return
            if not repo.remotes:
                self.api.show_message("critical", "No Remote", "This project has no remote repository configured.")
                return
            
            is_synced, fix_attempted, error = self._check_and_handle_branch_sync(repo)
            if error:
                self.api.show_message("info", "Release Cancelled", error)
                return
            if fix_attempted:
                return
            
            if is_synced:
                self.api.show_status_message("Repository is clean and ready for release.", 2000)
                self._start_release_process(path)

        except git.GitCommandError as e:
            self.api.show_message("critical", "Git Error", f"A Git command failed during pre-flight checks:\n\n{e.stderr}")
        except Exception as e:
            self.api.show_message("critical", "Repository Error", f"Could not check repository status: {e}")

    def _handle_unresolved_merge(self, repo: git.Repo) -> bool:
        msg_box = QMessageBox(self.main_window)
        msg_box.setIcon(QMessageBox.Icon.Warning)
        msg_box.setTextFormat(Qt.TextFormat.RichText)
        msg_box.setWindowTitle("Unresolved Merge")
        msg_box.setText("Your repository has an unresolved merge conflict.")
        msg_box.setInformativeText("To proceed, the merge must be aborted. This is a safe action that will revert your project to the state before the merge began.")
        abort_button = msg_box.addButton("Abort Merge and Continue", QMessageBox.ButtonRole.AcceptRole)
        cancel_button = msg_box.addButton("Cancel Release", QMessageBox.ButtonRole.RejectRole)
        msg_box.exec()

        if msg_box.clickedButton() == abort_button:
            try:
                repo.git.merge('--abort')
                return True
            except git.GitCommandError as e:
                self.api.show_message("critical", "Abort Failed", f"Could not abort merge: {e.stderr}")
        return False

    def _check_and_handle_branch_sync(self, repo: git.Repo) -> tuple[bool, bool, str]:
        self.api.show_status_message("Fetching remote status...")
        try:
            repo.remotes.origin.fetch()
        except git.GitCommandError as e:
            return False, False, f"Could not fetch from remote: {e.stderr}"

        active_branch = repo.active_branch
        tracking_branch = active_branch.tracking_branch()

        if not tracking_branch:
            return False, False, f"Local branch '{active_branch.name}' is not tracking a remote branch. Please push it to the remote first."

        ahead_commits = list(repo.iter_commits(f'{tracking_branch.name}..{active_branch.name}'))
        behind_commits = list(repo.iter_commits(f'{active_branch.name}..{tracking_branch.name}'))

        # FIX: Handle diverged state by offering to pull, just like the 'behind' state.
        if behind_commits:
            message_text = "Your local branch is behind the remote."
            if ahead_commits:
                message_text = "Your local branch has diverged from the remote (both have new changes)."
            
            reply = QMessageBox.question(self.main_window, "Branch Not Synchronized",
                                         f"{message_text}\n\nTo continue, you must pull the remote changes. This may create a merge commit.\n\nPull changes now?",
                                         QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.Yes:
                self._trigger_background_pull(repo.working_dir)
                return False, True, "" # A fix was attempted.
            else:
                return False, False, "Synchronization was cancelled by user."
        
        if ahead_commits:
            self.api.log_info(f"Branch '{active_branch.name}' is {len(ahead_commits)} commit(s) ahead, which is expected for a new release.")
        
        return True, False, "" # Synced or ahead, ready to go.

    def _trigger_background_pull(self, repo_path: str):
        self.api.show_status_message("Pulling remote changes...")
        self.git_manager.git_success.connect(lambda msg, data: self._on_preflight_pull_finished(True, msg, repo_path))
        self.git_manager.git_error.connect(lambda err: self._on_preflight_pull_finished(False, err, repo_path))
        self.git_manager.pull(repo_path)

    def _on_preflight_pull_finished(self, success: bool, message: str, repo_path: str):
        try:
            self.git_manager.git_success.disconnect()
            self.git_manager.git_error.disconnect()
        except TypeError: pass

        if success:
            self.api.get_main_window().explorer_panel.refresh()
            self._prepare_repository_for_release(repo_path)
        else:
            self.api.show_message("critical", "Pull Failed", f"Could not synchronize with remote.\n\nError: {message}")

    def _start_release_process(self, project_path: str):
        if not self.ensure_git_identity(project_path): return
        dialog = NewReleaseDialog(project_path, self.git_manager, self.main_window)
        if not dialog.exec():
            self.api.show_status_message("Release cancelled.", 3000)
            return
        
        self.progress_dialog = UploadProgressDialog(self.main_window)
        self.progress_dialog.show()
        
        try:
            repo = git.Repo(project_path)
            owner, repo_name = self.git_manager.parse_git_url(repo.remotes.origin.url)
            if not owner or not repo_name:
                self._on_release_step_failed("Could not parse owner/repo from remote URL.")
                return
        except Exception as e:
            self._on_release_step_failed(f"Could not analyze repository: {e}")
            return
            
        self._release_state = {'dialog_data': dialog.get_release_data(), 'project_path': project_path,
                               'owner': owner, 'repo_name': repo_name}
        self._advance_release_state("BUMP_VERSION_COMMIT")
        
    def _advance_release_state(self, next_step):
        self._release_state['step'] = next_step
        step_title = next_step.replace('_', ' ').title()
        self._log_to_dialog(f"Starting step: {step_title}")
        if sc_panel := self._get_sc_panel(): sc_panel.set_ui_locked(True, f"Step: {step_title}...")
        
        project_path = self._release_state['project_path']
        try:
            repo = git.Repo(project_path)
            with repo.config_reader() as cr:
                author = Actor(cr.get_value('user', 'name'), cr.get_value('user', 'email'))
        except Exception as e:
            self._on_release_step_failed(f"Could not read Git author info: {e}")
            return

        self._cleanup_connections()
        dialog_data = self._release_state['dialog_data']
        
        if next_step in ["CREATE_RELEASE", "UPLOAD_ASSET"]:
            self.github_manager.operation_success.connect(self._on_github_step_success)
            self.github_manager.operation_failed.connect(self._on_release_step_failed)
        else:
            self.git_manager.git_success.connect(self._on_git_step_success)
            self.git_manager.git_error.connect(self._on_release_step_failed)

        if next_step == "BUMP_VERSION_COMMIT":
            if not versioning.write_new_version(dialog_data['tag']):
                self._on_release_step_failed("Failed to write new version to VERSION.txt")
                return
            self.main_window._update_window_title()
            self.git_manager.commit_files(project_path, f"ci: Release {dialog_data['tag']}", author)
        elif next_step == "PUSH_MAIN_BRANCH":
            self.git_manager.push(project_path)
        elif next_step == "CREATE_TAG":
            self.git_manager.create_tag(project_path, dialog_data['tag'], dialog_data['title'], author)
        elif next_step == "PUSH_TAG":
            self.git_manager.push_specific_tag(project_path, dialog_data['tag'])
        elif next_step == "CREATE_RELEASE":
            self.github_manager.create_github_release(
                owner=self._release_state['owner'], repo=self._release_state['repo_name'],
                tag_name=dialog_data['tag'], name=dialog_data['title'],
                body=dialog_data['notes'], prerelease=dialog_data['prerelease'])
        elif next_step == "BUILD_ASSETS":
            self._run_build_script()
        elif next_step == "UPLOAD_ASSETS":
            self._upload_assets()

    def _on_git_step_success(self, msg, data):
        step_map = {"BUMP_VERSION_COMMIT": "PUSH_MAIN_BRANCH", "PUSH_MAIN_BRANCH": "CREATE_TAG", "CREATE_TAG": "PUSH_TAG", "PUSH_TAG": "CREATE_RELEASE"}
        if next_step := step_map.get(self._release_state.get('step')):
            self._advance_release_state(next_step)

    def _on_github_step_success(self, msg, data):
        step = self._release_state.get('step')
        if step == "CREATE_RELEASE":
            self._release_state['release_info'] = data.get("release_data", {})
            self._advance_release_state("BUILD_ASSETS")
        elif step == "UPLOAD_ASSET":
            self._upload_next_asset()

    def _run_build_script(self):
        # This is a placeholder for the actual build script execution
        self._log_to_dialog("Simulating build process...", is_warning=True)
        self._advance_release_state("UPLOAD_ASSETS")

    def _upload_assets(self):
        # This is a placeholder for asset gathering and uploading
        self._log_to_dialog("Simulating asset upload...", is_warning=True)
        self._cleanup_release_process(success=True)

    def _upload_next_asset(self):
        if not self._release_state.get('asset_queue'):
            self._log_to_dialog("All assets uploaded.")
            self._cleanup_release_process(success=True)
            return

    def _on_release_step_failed(self, error_message):
        step = self._release_state.get('step', 'UNKNOWN')
        self._log_to_dialog(f"FAILED on step '{step}': {error_message}", is_error=True)
        self.api.show_message("critical", "Release Failed", f"An error occurred at step '{step}'.\n\n{error_message}")
        self._cleanup_release_process(success=False)

    def _cleanup_connections(self):
        try:
            self.git_manager.git_success.disconnect()
            self.git_manager.git_error.disconnect()
            self.github_manager.operation_success.disconnect()
            self.github_manager.operation_failed.disconnect()
        except TypeError: pass

    def _cleanup_release_process(self, success=False):
        self._cleanup_connections()
        if sc_panel := self._get_sc_panel(): sc_panel.set_ui_locked(False, "Release process finished.")
        if self.progress_dialog:
            self.progress_dialog.add_log(f"\n--- RELEASE {'COMPLETE' if success else 'FAILED'} ---")
            self.progress_dialog.show_close_button()
        self._release_state = {}

    def _publish_repo(self, path):
        repo_name, ok = QInputDialog.getText(self.main_window, "Publish to GitHub", "Repository Name:", text=os.path.basename(path))
        if not (ok and repo_name): return
        if not self.ensure_git_identity(path): return
        desc, _ = QInputDialog.getText(self.main_window, "Description", "Description (optional):")
        private = QMessageBox.question(self.main_window, "Visibility", "Make repository private?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No) == QMessageBox.StandardButton.Yes
        self.github_manager.create_repo(repo_name, desc, private)
        self.api.get_main_window().source_control_panel.set_ui_locked(True, f"Creating '{repo_name}'...")

    def _link_repo(self, path):
        if not self.ensure_git_identity(path): return
        dialog = SelectRepoDialog(self.github_manager, self.main_window)
        if dialog.exec() and (repo_data := dialog.selected_repo_data):
            self.git_manager.link_to_remote(path, repo_data.get('clone_url'))

    def _change_visibility(self, path):
        try:
            repo = git.Repo(path)
            if not repo.remotes: return
            owner, repo_name = self.git_manager.parse_git_url(repo.remotes.origin.url)
            private = QMessageBox.question(self.main_window, "Visibility", "Make repository private?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No) == QMessageBox.StandardButton.Yes
            self.github_manager.update_repo_visibility(owner, repo_name, private)
        except Exception as e:
            self.api.show_message("critical", "Error", f"Could not get repository info: {e}")

    def _show_github_dialog(self):
        if not self.github_dialog:
            self.github_dialog = GitHubDialog(self.github_manager, self.git_manager, self.main_window)
            self.github_manager.project_cloned.connect(self.project_manager.open_project)
        self.github_dialog.show()
        
def initialize(puffin_api: PuffinPluginAPI):
    plugin = GitHubToolsPlugin(puffin_api)
    puffin_api.add_menu_action("tools", "GitHub Repositories...", plugin._show_github_dialog, icon_name="fa5b.github")
    puffin_api.add_menu_action("tools", "New Release...", plugin.show_create_release_dialog, icon_name="fa5s.tag")
    return plugin
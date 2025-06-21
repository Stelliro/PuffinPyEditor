# PuffinPyEditor/app_core/source_control_manager.py
import os
import git
from git import Repo, GitCommandError, InvalidGitRepositoryError, NoSuchPathError
from PyQt6.QtCore import QObject, QThread, pyqtSignal
from utils.logger import log
from app_core.settings_manager import settings_manager
import configparser


class GitWorker(QObject):
    summaries_ready = pyqtSignal(dict)
    status_ready = pyqtSignal(list, list, str)
    error_occurred = pyqtSignal(str)
    operation_success = pyqtSignal(str, dict)
    git_config_ready = pyqtSignal(str, str)

    def get_git_config(self):
        try:
            git_cmd = git.Git()
            name, email = "", ""
            try:
                name = git_cmd.config('--global', '--get', 'user.name')
            except GitCommandError:
                log.warning("Git user.name is not set globally.")
            try:
                email = git_cmd.config('--global', '--get', 'user.email')
            except GitCommandError:
                log.warning("Git user.email is not set globally.")
            self.git_config_ready.emit(name, email)
        except Exception as e:
            log.error(f"Failed to get git config: {e}")
            self.git_config_ready.emit("", "")

    def set_git_config(self, name, email):
        try:
            git_cmd = git.Git()
            if name:
                git_cmd.config('--global', 'user.name', name)
                log.info(f"Set global git user.name to '{name}'")
            if email:
                git_cmd.config('--global', 'user.email', email)
                log.info(f"Set global git user.email to '{email}'")
            self.operation_success.emit("Global Git config updated.", {})
        except Exception as e:
            log.error(f"Failed to set git config: {e}")
            self.error_occurred.emit(f"Failed to set Git config: {e}")

    def link_to_remote(self, local_path, remote_url):
        try:
            log.info(f"Linking local path '{local_path}' to remote '{remote_url}'")
            repo = Repo.init(local_path)

            if 'origin' in repo.remotes:
                origin = repo.remotes.origin
                origin.set_url(remote_url)
            else:
                origin = repo.create_remote('origin', remote_url)

            origin.fetch()
            remote_head = repo.remote().refs.HEAD

            if remote_head.is_valid():
                remote_branch_name = remote_head.reference.name.split('/')[-1]
                log.info(f"Remote default branch is '{remote_branch_name}'. Aligning local repo.")
                repo.git.branch('-M', remote_branch_name)
                repo.git.reset('--soft', f'origin/{remote_branch_name}')
            else:
                log.warning("Remote repository is empty.")

            if not repo.head.is_valid():
                log.info("No local commits found. Staging all files and creating initial commit.")
                repo.git.add(A=True)
                repo.index.commit("Initial commit after linking to remote")

            self.operation_success.emit(f"Successfully linked to {remote_url}", {})

        except Exception as e:
            log.error(f"Failed to link to remote: {e}", exc_info=True)
            self.error_occurred.emit(f"Failed to link repository: {e}")

    def get_multiple_repo_summaries(self, repo_paths: list):
        summaries = {}
        for path in repo_paths:
            try:
                repo = Repo(path, search_parent_directories=True)
                if repo.bare:
                    summaries[path] = {'branch': '(bare repo)', 'commit': 'N/A'}
                elif not repo.head.is_valid():
                    summaries[path] = {'branch': '(no commits)', 'commit': 'N/A'}
                else:
                    summaries[path] = {'branch': repo.active_branch.name, 'commit': repo.head.commit.hexsha[:7]}
            except InvalidGitRepositoryError:
                log.info(f"'{os.path.basename(path)}' is not a Git repository. Skipping.")
            except Exception as e:
                log.error(f"Unexpected error getting Git summary for {path}: {e}")
                summaries[path] = {'branch': '(error)', 'commit': 'N/A'}
        self.summaries_ready.emit(summaries)

    def create_tag(self, repo_path, tag, title):
        try:
            try:
                repo = Repo(repo_path)
            except InvalidGitRepositoryError:
                self.error_occurred.emit(f"Operation failed: '{os.path.basename(repo_path)}' is not a Git repository.")
                return

            with repo.config_reader() as cr:
                try:
                    name = cr.get_value('user', 'name')
                    email = cr.get_value('user', 'email')
                    if not name or not email:
                        raise ValueError("User name or email not configured.")
                except (configparser.NoSectionError, configparser.NoOptionError, ValueError):
                    self.error_occurred.emit(
                        "Git user config is missing.\n\n"
                        "Please configure your user identity in Preferences > Source Control."
                    )
                    return

            # FIX: Check if the repository has any commits. If not, create one.
            if not repo.head.is_valid():
                log.info(f"No commits found in '{repo_path}'. Creating initial commit.")
                if repo.is_dirty(untracked_files=True):
                    repo.git.add(A=True)
                    repo.index.commit("Initial commit for release")
                    log.info("Staged all files and created initial commit.")
                else:
                    self.error_occurred.emit("Cannot create a release for an empty project with no files.")
                    return

            repo.create_tag(tag, message=title)
            self.operation_success.emit(f"Tag created: {tag}", {})

        except GitCommandError as e:
            if "already exists" in str(e):
                self.error_occurred.emit(f"Tag '{tag}' already exists.")
            else:
                log.error(f"GitCommandError while tagging: {e}", exc_info=True)
                self.error_occurred.emit(f"Failed to create tag. Check logs.")
        except Exception as e:
            log.error(f"Unexpected error while tagging repository {repo_path}: {e}", exc_info=True)
            self.error_occurred.emit("An unexpected error occurred while tagging. Check logs.")

    def get_status(self, repo_path):
        try:
            repo = Repo(repo_path)
            staged = [item.a_path for item in repo.index.diff('HEAD')]
            unstaged = [item.a_path for item in repo.index.diff(None)] + repo.untracked_files
            self.status_ready.emit(staged, unstaged, repo_path)
        except Exception as e:
            self.error_occurred.emit(f"Git Status for {os.path.basename(repo_path)} failed: {e}")

    def commit_files(self, repo_path, message):
        try:
            repo = Repo(repo_path)
            with repo.config_reader() as cr:
                try:
                    name = cr.get_value('user', 'name')
                    email = cr.get_value('user', 'email')
                    if not name or not email:
                        raise ValueError("User name or email not configured.")
                except (configparser.NoSectionError, configparser.NoOptionError, ValueError):
                    self.error_occurred.emit(
                        "Git user config is missing.\n\n"
                        "Please configure your user identity in Preferences > Source Control."
                    )
                    return

            log.info(f"Staging all changes in {repo_path}")
            repo.git.add(A=True)

            if repo.index.diff("HEAD"):
                repo.index.commit(message)
                self.operation_success.emit("Changes committed.", {'repo_path': repo_path})
            else:
                self.operation_success.emit("No changes to commit.", {'repo_path': repo_path, 'no_changes': True})

        except Exception as e:
            self.error_occurred.emit(f"Git Commit failed: {e}")

    def push(self, repo_path):
        try:
            repo = Repo(repo_path)
            origin = repo.remotes.origin
            active_branch = repo.active_branch.name
            log.info(f"Pushing branch '{active_branch}' and all tags to remote...")
            origin.push(refspec=f'{active_branch}:{active_branch}', tags=True)
            self.operation_success.emit("Push successful", {})
        except GitCommandError as e:
            error_str = str(e).lower()
            if "authentication failed" in error_str:
                msg = "Authentication failed. Please use the 'Login to GitHub' button in Preferences."
            else:
                msg = f"Git Push failed: {e}"
            self.error_occurred.emit(msg)
        except Exception as e:
            self.error_occurred.emit(f"Git Push failed: An unexpected error occurred: {e}")

    def pull(self, repo_path):
        try:
            repo = Repo(repo_path)
            repo.remotes.origin.pull()
            self.operation_success.emit("Pull successful", {})
            self.get_status(repo_path)
        except Exception as e:
            self.error_occurred.emit(f"Git Pull failed: {e}")

    def clone_repo(self, url, path, branch):
        try:
            log.info(
                f"Cloning '{url}' (branch: {branch}) into '{os.path.join(path, os.path.basename(url).replace('.git', ''))}'")
            Repo.clone_from(url, os.path.join(path, os.path.basename(url).replace('.git', '')), branch=branch)
            self.operation_success.emit("Clone successful", {})
        except GitCommandError as e:
            error_str = str(e).lower()
            if "authentication failed" in error_str:
                msg = "Authentication failed. The repository may be private. Please login via Preferences."
            else:
                msg = f"Clone failed: {e}"
            self.error_occurred.emit(msg)
        except Exception as e:
            self.error_occurred.emit(f"Clone failed: An unexpected error occurred: {e}")

    def publish_repo(self, path, url):
        try:
            repo = Repo.init(path)
            with repo.config_reader() as cr:
                try:
                    name = cr.get_value('user', 'name')
                    email = cr.get_value('user', 'email')
                    if not name or not email:
                        raise ValueError("User name or email not configured.")
                except (configparser.NoSectionError, configparser.NoOptionError, ValueError):
                    self.error_occurred.emit(
                        "Git user config is missing.\n\n"
                        "Please configure your user identity in Preferences > Source Control."
                    )
                    return

            repo.git.add(A=True)
            if not repo.head.is_valid():
                repo.index.commit("Initial commit")
            if 'origin' in repo.remotes:
                origin = repo.remotes.origin
                origin.set_url(url)
            else:
                origin = repo.create_remote('origin', url)
            origin.push(refspec='HEAD:main', set_upstream=True)
            self.operation_success.emit(f"Successfully published project to {url}", {})
        except Exception as e:
            log.error(f"Publish failed: {e}", exc_info=True)
            self.error_occurred.emit(f"Publish failed: {e}")


class SourceControlManager(QObject):
    summaries_ready = pyqtSignal(dict)
    status_updated = pyqtSignal(list, list, str)
    git_error = pyqtSignal(str)
    git_success = pyqtSignal(str, dict)
    git_config_ready = pyqtSignal(str, str)

    _request_summaries = pyqtSignal(list)
    _request_status = pyqtSignal(str)
    _request_commit = pyqtSignal(str, str)
    _request_push = pyqtSignal(str)
    _request_pull = pyqtSignal(str)
    _request_clone = pyqtSignal(str, str, str)
    _request_publish = pyqtSignal(str, str)
    _request_create_tag = pyqtSignal(str, str, str)
    _request_link_to_remote = pyqtSignal(str, str)
    _request_get_git_config = pyqtSignal()
    _request_set_git_config = pyqtSignal(str, str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.thread = QThread()
        self.worker = GitWorker()
        self.worker.moveToThread(self.thread)

        self._request_summaries.connect(self.worker.get_multiple_repo_summaries)
        self._request_status.connect(self.worker.get_status)
        self._request_commit.connect(self.worker.commit_files)
        self._request_push.connect(self.worker.push)
        self._request_pull.connect(self.worker.pull)
        self._request_clone.connect(self.worker.clone_repo)
        self._request_publish.connect(self.worker.publish_repo)
        self._request_create_tag.connect(self.worker.create_tag)
        self._request_link_to_remote.connect(self.worker.link_to_remote)
        self._request_get_git_config.connect(self.worker.get_git_config)
        self._request_set_git_config.connect(self.worker.set_git_config)

        self.worker.summaries_ready.connect(self.summaries_ready)
        self.worker.status_ready.connect(self.status_updated)
        self.worker.error_occurred.connect(self.git_error)
        self.worker.operation_success.connect(self.git_success)
        self.worker.git_config_ready.connect(self.git_config_ready)

        self.thread.start()

    def get_git_config(self):
        self._request_get_git_config.emit()

    def set_git_config(self, name, email):
        self._request_set_git_config.emit(name, email)

    def link_to_remote(self, path: str, url: str):
        self._request_link_to_remote.emit(path, url)

    def get_summaries(self, paths: list):
        self._request_summaries.emit(paths)

    def get_status(self, path):
        self._request_status.emit(path)

    def commit_files(self, path, msg):
        self._request_commit.emit(path, msg)

    def push(self, path):
        self._request_push.emit(path)

    def pull(self, path):
        self._request_pull.emit(path)

    def clone_repo(self, url, path, branch):
        self._request_clone.emit(url, path, branch)

    def publish_repo(self, path, url):
        self._request_publish.emit(path, url)

    def create_tag(self, path, tag, title):
        self._request_create_tag.emit(path, tag, title)

    def shutdown(self):
        if self.thread.isRunning():
            self.thread.quit()
            self.thread.wait(3000)
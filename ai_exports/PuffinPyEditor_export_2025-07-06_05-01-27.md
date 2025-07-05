# Project Export: PuffinPyEditor
## Export Timestamp: 2025-07-06T05:01:27.407837
---

## AI Instructions
You are Inspector Val, a world-renowned digital detective. Code is your crime scene. A bug has been reported, and you've been called in to solve the case. Your approach is methodical, logical, and evidence-based. You will analyze the provided code and context (like a traceback) to find the root cause and prescribe a definitive fix.

## Guidelines & Rules
- Begin your report with a 'Case File Summary', clearly stating the reported issue (the bug) and its user-facing impact.
- Present 'The Evidence'. This section must include the problematic code snippets and the full stack trace or error message.
- Identify 'The Suspects'. List the specific variables, functions, or expressions that are potentially responsible for the bug.
- Formulate the 'Primary Hypothesis'. In a clear, step-by-step narrative, explain exactly how you believe the bug is occurring.
- Provide 'The Solution'. Offer a corrected code snippet that fixes the bug, with comments explaining the change.
- Conclude with a 'Case Closed' statement, briefly explaining how the fix prevents the issue from recurring and any lessons learned.

## Golden Rules
1. Only edit and add features, the only features should stay unless asked to be removed, or may be completely redundant.
2. any scripts over 1000 lines, please write in a new response.
3. multiple scripts together exceeding 2000 lines together need to be separated into smaller responses, (example: these scripts have 2340 lines together I'm going to separate it into 2 messages that way i dont lose formatting and dont accidentally remove any features)
4. Do not remove any code that is unrelated to the fix, only remove code if it is being substituted or is not needed anymore.

---

## Project Files

Here is the project context you need to work with.
## File Tree
```
/PuffinPyEditor
 ├── app_core
 │   └── github_manager.py
 └── plugins
     └── github_tools
         ├── __init__.py
         ├── github_dialog.py
         ├── new_release_dialog.py
         ├── plugin.json
         ├── plugin_main.py
         └── select_repo_dialog.py

```
## File Contents
### File: `/app_core/github_manager.py`

```python
# PuffinPyEditor/app_core/github_manager.py
import requests
import time
import os
import json
from typing import Dict, Optional, List
from PyQt6.QtCore import QObject, QThread, pyqtSignal
from .settings_manager import settings_manager
from utils.versioning import APP_VERSION
from utils.logger import log

CLIENT_ID = "178c6fc778ccc68e1d6a"
DEVICE_CODE_URL = "https://github.com/login/device/code"
ACCESS_TOKEN_URL = "https://github.com/login/oauth/access_token"


class GitHubWorker(QObject):
    """
    Worker that runs all GitHub API requests in a background thread.
    """
    device_code_ready = pyqtSignal(dict)
    auth_successful = pyqtSignal(str)
    auth_failed = pyqtSignal(str)
    auth_polling_lapsed = pyqtSignal()
    repos_ready = pyqtSignal(list)
    branches_ready = pyqtSignal(list)
    plugin_index_ready = pyqtSignal(list)
    operation_success = pyqtSignal(str, dict)
    operation_failed = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.access_token: Optional[str] = settings_manager.get(
            "github_access_token")
        self.user_agent = f"PuffinPyEditor/{APP_VERSION}"

    def _get_headers(self) -> Dict[str, str]:
        """Constructs the standard headers for authenticated API requests."""
        return {
            "Accept": "application/vnd.github.v3+json",
            "Authorization": f"Bearer {self.access_token}",
            "User-Agent": self.user_agent
        }

    def start_device_flow(self):
        log.info("Starting GitHub device authorization flow.")
        try:
            headers = {"Accept": "application/json",
                       "User-Agent": self.user_agent}
            payload = {"client_id": CLIENT_ID, "scope": "repo user"}
            response = requests.post(
                DEVICE_CODE_URL, data=payload, headers=headers, timeout=10
            )
            response.raise_for_status()
            data = response.json()
            log.info(f"Received device code: {data.get('user_code')}")
            self.device_code_ready.emit(data)
        except requests.RequestException as e:
            log.error(f"Failed to start device flow: {e}", exc_info=True)
            self.auth_failed.emit(
                "Could not connect to GitHub. Check network and logs."
            )

    def poll_for_token(self, device_code: str, interval: int, expires_in: int):
        log.info("Polling for GitHub access token...")
        start_time = time.time()
        headers = {"Accept": "application/json", "User-Agent": self.user_agent}
        payload = {
            "client_id": CLIENT_ID,
            "device_code": device_code,
            "grant_type": "urn:ietf:params:oauth:grant-type:device_code"
        }
        while time.time() - start_time < expires_in:
            try:
                response = requests.post(
                    ACCESS_TOKEN_URL, data=payload,
                    headers=headers, timeout=interval + 2
                )
                data = response.json()
                if "access_token" in data:
                    self.access_token = data["access_token"]
                    user_info = self._get_authenticated_user_info()
                    user_login = user_info.get("login") if user_info else "user"
                    settings_manager.set(
                        "github_access_token", self.access_token, False
                    )
                    settings_manager.set("github_user", user_login, False)
                    settings_manager.set(
                        "github_user_info", user_info, False
                    )
                    settings_manager.save()
                    log.info(
                        "Successfully authenticated as GitHub user: "
                        f"{user_login}"
                    )
                    self.auth_successful.emit(user_login)
                    return
                elif data.get("error") == "authorization_pending":
                    time.sleep(interval)
                else:
                    error_desc = data.get(
                        "error_description", "Unknown authentication error"
                    )
                    log.error(f"GitHub authentication error: {error_desc}")
                    self.auth_failed.emit(error_desc)
                    return
            except requests.RequestException as e:
                log.error(f"Exception while polling for token: {e}",
                          exc_info=True)
                self.auth_failed.emit(f"Network error during auth: {e}")
                return
        log.warning("Device flow expired before user authorized.")
        self.auth_polling_lapsed.emit()

    def _get_authenticated_user_info(self) -> Optional[Dict]:
        if not self.access_token:
            return None
        try:
            response = requests.get(
                "https://api.github.com/user",
                headers=self._get_headers(), timeout=10
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            log.error(f"Failed to get user info from GitHub: {e}")
            return None

    def _paginated_request(self, url: str) -> List[Dict]:
        """Helper to handle paginated GitHub API requests."""
        all_items = []
        page = 1
        while True:
            paginated_url = f"{url}?page={page}&per_page=100"
            response = requests.get(
                paginated_url, headers=self._get_headers(), timeout=15
            )
            response.raise_for_status()
            data = response.json()
            if not data:
                break
            all_items.extend(data)
            page += 1
        return all_items

    def list_user_repos(self):
        if not self.access_token:
            self.operation_failed.emit("Not logged in to GitHub.")
            return
        try:
            # Use the paginated helper
            all_repos = self._paginated_request("https://api.github.com/user/repos")
            # Sort by most recently pushed to
            self.repos_ready.emit(sorted(all_repos, key=lambda r: r.get('pushed_at', ''), reverse=True))
        except requests.RequestException as e:
            self.operation_failed.emit(f"Failed to list repositories: {e}")

    def list_repo_branches(self, full_repo_name: str):
        if not self.access_token:
            self.operation_failed.emit("Not logged in to GitHub.")
            return
        try:
            url = f"https://api.github.com/repos/{full_repo_name}/branches"
            response = requests.get(
                url, headers=self._get_headers(), timeout=10
            )
            response.raise_for_status()
            self.branches_ready.emit(response.json())
        except requests.RequestException as e:
            self.operation_failed.emit(
                f"Failed to list branches for {full_repo_name}: {e}")

    def create_github_release(self, owner: str, repo: str, tag_name: str,
                              name: str, body: str, prerelease: bool):
        if not self.access_token:
            self.operation_failed.emit("Not logged in to GitHub.")
            return
        url = f"https://api.github.com/repos/{owner}/{repo}/releases"
        payload = {"tag_name": tag_name, "name": name, "body": body,
                   "prerelease": prerelease}
        try:
            response = requests.post(
                url, headers=self._get_headers(), json=payload, timeout=20
            )
            response.raise_for_status()
            self.operation_success.emit(
                "Release created", {"release_data": response.json()}
            )
        except requests.exceptions.HTTPError as e:
            msg = f"HTTP {e.response.status_code}: "
            try:
                error_body = e.response.json()
                errs = error_body.get('errors', [])
                if any(err.get('code') == 'already_exists' for err in errs):
                    msg += f"A release for tag '{tag_name}' already exists."
                else:
                    msg += error_body.get(
                        'message', 'Failed to create release.'
                    )
            except json.JSONDecodeError:
                msg += "Failed to create GitHub release."
            self.operation_failed.emit(msg)
        except requests.RequestException as e:
            self.operation_failed.emit(f"Failed to create GitHub release: {e}")

    def upload_release_asset(self, upload_url: str, asset_path: str):
        if not self.access_token:
            self.operation_failed.emit("Not logged in to GitHub.")
            return
        upload_url = upload_url.split('{')[0]
        asset_name = os.path.basename(asset_path)
        headers = self._get_headers()
        headers['Content-Type'] = 'application/octet-stream'
        try:
            with open(asset_path, 'rb') as f:
                data = f.read()
            response = requests.post(
                f"{upload_url}?name={asset_name}",
                headers=headers, data=data, timeout=300
            )
            response.raise_for_status()
            self.operation_success.emit(
                "Asset uploaded", {"asset_data": response.json()}
            )
        except (requests.RequestException, IOError) as e:
            self.operation_failed.emit(f"Failed to upload asset: {e}")

    def delete_release(self, owner: str, repo: str, release_id: int):
        if not self.access_token:
            self.operation_failed.emit("Not logged in to GitHub.")
            return
        url = (f"https://api.github.com/repos/{owner}/{repo}/releases/"
               f"{release_id}")
        log.info(f"ROLLBACK: Attempting to delete release at {url}")
        try:
            response = requests.delete(
                url, headers=self._get_headers(), timeout=20
            )
            response.raise_for_status()
            self.operation_success.emit(
                "Release deleted", {"release_id": release_id}
            )
        except requests.RequestException as e:
            msg = f"Failed to delete release: {e}"
            if hasattr(e, 'response') and e.response:
                msg += f" (Status: {e.response.status_code})"
            self.operation_failed.emit(msg)

    def create_repo(self, name: str, description: str, is_private: bool):
        if not self.access_token:
            self.operation_failed.emit("Not logged in to GitHub.")
            return
        api_url = "https://api.github.com/user/repos"
        payload = {"name": name, "description": description,
                   "private": is_private}
        try:
            response = requests.post(
                api_url, headers=self._get_headers(), json=payload, timeout=15
            )
            response.raise_for_status()
            self.operation_success.emit(
                f"Repository '{name}' created.", response.json()
            )
        except requests.RequestException as e:
            error_msg = e.response.json().get('message', str(e)) if hasattr(e, 'response') and e.response else str(e)
            self.operation_failed.emit(
                f"Failed to create repository: {error_msg}")

    def fetch_plugin_index(self, repo_path: str):
        url = f"https://raw.githubusercontent.com/{repo_path}/main/index.json"
        log.info(f"Fetching plugin index from: {url}")
        try:
            response = requests.get(url, timeout=15)
            response.raise_for_status()
            self.plugin_index_ready.emit(response.json())
        except requests.RequestException as e:
            self.operation_failed.emit(f"Failed to fetch plugin index: {e}")
        except json.JSONDecodeError:
            self.operation_failed.emit(
                "Invalid plugin index format (not valid JSON).")

    def update_repo_visibility(self, owner: str, repo: str, is_private: bool):
        if not self.access_token:
            self.operation_failed.emit("Not logged in to GitHub.")
            return
        api_url = f"https://api.github.com/repos/{owner}/{repo}"
        payload = {"private": is_private}
        try:
            response = requests.patch(
                api_url, headers=self._get_headers(), json=payload, timeout=15
            )
            response.raise_for_status()
            visibility = "private" if is_private else "public"
            self.operation_success.emit(
                f"Repository visibility changed to {visibility}.",
                response.json()
            )
        except requests.RequestException as e:
            error_msg = e.response.json().get('message', str(e)) if hasattr(e, 'response') and e.response else str(e)
            self.operation_failed.emit(
                f"Failed to change visibility: {error_msg}")

    def list_repo_tags(self, owner: str, repo: str) -> List[Dict]:
        """Fetches all tags for a repository."""
        url = f"https://api.github.com/repos/{owner}/{repo}/tags"
        return self._paginated_request(url)

    def list_repo_releases(self, owner: str, repo: str) -> List[Dict]:
        """Fetches all releases for a repository."""
        url = f"https://api.github.com/repos/{owner}/{repo}/releases"
        return self._paginated_request(url)

    def delete_remote_tag_ref(self, owner: str, repo: str, tag: str) -> bool:
        """Deletes a tag reference from the remote repository."""
        url = f"https://api.github.com/repos/{owner}/{repo}/git/refs/tags/{tag}"
        try:
            response = requests.delete(url, headers=self._get_headers(), timeout=10)
            response.raise_for_status()
            log.info(f"Successfully deleted remote tag ref: {tag}")
            return True
        except requests.RequestException as e:
            log.error(f"Failed to delete tag '{tag}': {e}")
            return False

    def cleanup_orphaned_tags(self, owner: str, repo: str):
        """Finds and deletes tags that are not associated with any release."""
        if not self.access_token:
            self.operation_failed.emit("Not logged in to GitHub.")
            return

        try:
            log.info(f"Starting orphaned tag cleanup for {owner}/{repo}")
            all_tags_data = self.list_repo_tags(owner, repo)
            all_releases_data = self.list_repo_releases(owner, repo)

            all_tag_names = {tag['name'] for tag in all_tags_data}
            release_tag_names = {rel['tag_name'] for rel in all_releases_data}

            orphaned_tags = all_tag_names - release_tag_names
            log.info(f"Found {len(orphaned_tags)} orphaned tags: {orphaned_tags}")

            if not orphaned_tags:
                self.operation_success.emit("No orphaned tags found to clean up.", {})
                return

            deleted_tags, failed_tags = [], []
            for tag in orphaned_tags:
                if self.delete_remote_tag_ref(owner, repo, tag):
                    deleted_tags.append(tag)
                else:
                    failed_tags.append(tag)

            summary_lines = []
            if deleted_tags:
                summary_lines.append(f"Successfully deleted {len(deleted_tags)} orphaned tags: {', '.join(deleted_tags)}")
            if failed_tags:
                summary_lines.append(f"Failed to delete {len(failed_tags)} tags: {', '.join(failed_tags)}")

            final_message = "\n".join(summary_lines)
            if failed_tags:
                self.operation_failed.emit(final_message)
            else:
                self.operation_success.emit(final_message, {"deleted_tags": deleted_tags})

        except requests.RequestException as e:
            self.operation_failed.emit(f"Failed to fetch repo data for cleanup: {e}")
        except Exception as e:
            log.error(f"Unexpected error during tag cleanup: {e}", exc_info=True)
            self.operation_failed.emit("An unexpected error occurred during cleanup.")


class GitHubManager(QObject):
    """
    Manages all interaction with the GitHub API by delegating to a background
    worker thread.
    """
    device_code_ready = pyqtSignal(dict)
    auth_successful = pyqtSignal(str)
    auth_failed = pyqtSignal(str)
    auth_polling_lapsed = pyqtSignal()
    repos_ready = pyqtSignal(list)
    branches_ready = pyqtSignal(list)
    plugin_index_ready = pyqtSignal(list)
    operation_success = pyqtSignal(str, dict)
    operation_failed = pyqtSignal(str)

    _start_device_flow = pyqtSignal()
    _poll_for_token = pyqtSignal(str, int, int)
    _request_repos = pyqtSignal()
    _request_branches = pyqtSignal(str)
    _request_create_repo = pyqtSignal(str, str, bool)
    _request_create_release = pyqtSignal(str, str, str, str, str, bool)
    _request_upload_asset = pyqtSignal(str, str)
    _request_update_visibility = pyqtSignal(str, str, bool)
    _request_plugin_index = pyqtSignal(str)
    _request_delete_release = pyqtSignal(str, str, int)
    _request_cleanup_tags = pyqtSignal(str, str)

    def __init__(self, parent: Optional[QObject] = None):
        super().__init__(parent)
        self.thread = QThread()
        self.worker = GitHubWorker()
        self.worker.moveToThread(self.thread)
        self.user_info = settings_manager.get("github_user_info")
        log.info(f"Loaded stored GitHub user info on startup: "
                 f"{bool(self.user_info)}")

        self._start_device_flow.connect(self.worker.start_device_flow)
        self._poll_for_token.connect(self.worker.poll_for_token)
        self._request_repos.connect(self.worker.list_user_repos)
        self._request_branches.connect(self.worker.list_repo_branches)
        self._request_create_repo.connect(self.worker.create_repo)
        self._request_create_release.connect(self.worker.create_github_release)
        self._request_upload_asset.connect(self.worker.upload_release_asset)
        self._request_update_visibility.connect(
            self.worker.update_repo_visibility)
        self._request_plugin_index.connect(self.worker.fetch_plugin_index)
        self._request_delete_release.connect(self.worker.delete_release)
        self._request_cleanup_tags.connect(self.worker.cleanup_orphaned_tags)

        self.worker.device_code_ready.connect(self.device_code_ready)
        self.worker.auth_successful.connect(self._on_auth_successful)
        self.worker.auth_failed.connect(self.auth_failed)
        self.worker.auth_polling_lapsed.connect(self.auth_polling_lapsed)
        self.worker.repos_ready.connect(self.repos_ready)
        self.worker.branches_ready.connect(self.branches_ready)
        self.worker.plugin_index_ready.connect(self.plugin_index_ready)
        self.worker.operation_success.connect(self.operation_success)
        self.worker.operation_failed.connect(self.operation_failed)

        self.thread.start()

    def _on_auth_successful(self, username: str):
        self.user_info = settings_manager.get("github_user_info")
        log.info(
            f"Authentication successful. Loaded user info for {username}.")
        self.auth_successful.emit(username)

    def get_authenticated_user(self) -> Optional[str]:
        return settings_manager.get("github_user")

    def get_user_info(self) -> Optional[Dict]:
        return self.user_info

    def get_active_repo_config(self) -> Optional[Dict]:
        """
        Retrieves the configuration dictionary for the repo marked as active.
        This is the single source of truth for the project's main repository.

        Returns:
            A dictionary with 'owner' and 'repo' keys, or None if not set.
        """
        active_repo_id = settings_manager.get("active_update_repo_id")
        if not active_repo_id:
            return None

        all_repos = settings_manager.get("source_control_repos", [])
        active_repo_config = next(
            (r for r in all_repos if r.get("id") == active_repo_id), None
        )
        return active_repo_config

    def start_device_flow(self):
        self._start_device_flow.emit()

    def poll_for_token(self, device_code: str, interval: int, expires_in: int):
        self._poll_for_token.emit(device_code, interval, expires_in)

    def logout(self):
        settings_manager.set("github_access_token", None, False)
        settings_manager.set("github_user", None, False)
        settings_manager.set("github_user_info", None, False)
        settings_manager.save()
        self.worker.access_token = None
        self.user_info = None
        log.info("Logged out of GitHub and cleared session data.")

    def list_repos(self):
        self._request_repos.emit()

    def list_branches(self, full_repo_name: str):
        self._request_branches.emit(full_repo_name)

    def create_repo(self, name: str, description: str, is_private: bool):
        self._request_create_repo.emit(name, description, is_private)

    def create_github_release(self, owner: str, repo: str, tag_name: str,
                              name: str, body: str, prerelease: bool):
        self._request_create_release.emit(
            owner, repo, tag_name, name, body, prerelease
        )

    def upload_asset(self, upload_url: str, asset_path: str):
        self._request_upload_asset.emit(upload_url, asset_path)

    def delete_release(self, owner: str, repo: str, release_id: int):
        self._request_delete_release.emit(owner, repo, release_id)

    def update_repo_visibility(self, owner: str, repo: str, is_private: bool):
        self._request_update_visibility.emit(owner, repo, is_private)

    def fetch_plugin_index(self, repo_path: str):
        self._request_plugin_index.emit(repo_path)
        
    def cleanup_orphaned_tags(self, owner: str, repo: str):
        """Requests a cleanup of orphaned tags for the specified repository."""
        self._request_cleanup_tags.emit(owner, repo)

    def shutdown(self):
        if self.thread and self.thread.isRunning():
            log.info("Shutting down GitHubManager thread.")
            self.thread.quit()
            if not self.thread.wait(3000):
                log.warning(
                    "GitHubManager thread did not shut down "
                    "gracefully. Terminating."
                )
                self.thread.terminate()
```

### File: `/plugins/github_tools/__init__.py`

```python

```

### File: `/plugins/github_tools/github_dialog.py`

```python
# PuffinPyEditor/plugins/github_tools/github_dialog.py
import os
from typing import Optional, List, Dict, Any
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QWidget,
                             QSplitter, QLabel, QListWidget, QListWidgetItem,
                             QPushButton, QMessageBox, QFileDialog)
from PyQt6.QtCore import Qt, pyqtSignal
from app_core.github_manager import GitHubManager
from app_core.source_control_manager import SourceControlManager
import qtawesome as qta


class GitHubDialog(QDialog):
    """
    A dialog for browsing and cloning a user's GitHub repositories.
    """
    project_cloned = pyqtSignal(str)

    def __init__(self, github_manager: GitHubManager,
                 git_manager: SourceControlManager,
                 parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.github_manager = github_manager
        self.git_manager = git_manager

        self.setWindowTitle("GitHub Repository Management")
        self.setMinimumSize(800, 600)
        self._setup_ui()
        self._connect_signals()

    def _setup_ui(self):
        layout = QVBoxLayout(self)

        top_bar_layout = QHBoxLayout()
        self.user_label = QLabel("<i>Checking authentication...</i>")
        top_bar_layout.addWidget(self.user_label)
        top_bar_layout.addStretch()
        layout.addLayout(top_bar_layout)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        layout.addWidget(splitter)
        left_pane = self._create_repo_list_pane()
        right_pane = self._create_details_pane()
        splitter.addWidget(left_pane)
        splitter.addWidget(right_pane)
        splitter.setSizes([300, 500])

    def _create_repo_list_pane(self) -> QWidget:
        pane = QWidget()
        layout = QVBoxLayout(pane)
        layout.setContentsMargins(0, 0, 0, 0)
        toolbar_layout = QHBoxLayout()
        self.refresh_button = QPushButton("Refresh List")
        self.refresh_button.setIcon(qta.icon('fa5s.sync-alt'))
        toolbar_layout.addWidget(self.refresh_button)
        toolbar_layout.addStretch()
        self.repo_list = QListWidget()
        layout.addLayout(toolbar_layout)
        layout.addWidget(self.repo_list)
        return pane

    def _create_details_pane(self) -> QWidget:
        pane = QWidget()
        layout = QVBoxLayout(pane)
        self.repo_details_label = QLabel("<i>Select a repository...</i>")
        self.repo_details_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.repo_details_label.setWordWrap(True)
        layout.addWidget(self.repo_details_label, 1)
        layout.addWidget(QLabel("<b>Branches:</b>"))
        self.branch_list = QListWidget()
        layout.addWidget(self.branch_list, 2)
        self.clone_button = QPushButton("Clone Selected Branch")
        self.clone_button.setIcon(qta.icon('fa5s.download'))
        self.clone_button.setEnabled(False)
        layout.addWidget(self.clone_button)
        return pane

    def _connect_signals(self):
        self.github_manager.repos_ready.connect(self.populate_repo_list)
        self.github_manager.branches_ready.connect(self.populate_branch_list)
        self.github_manager.operation_failed.connect(
            self._on_operation_failed)
        self.repo_list.currentItemChanged.connect(self.on_repo_selected)
        self.refresh_button.clicked.connect(self.github_manager.list_repos)
        self.clone_button.clicked.connect(self.on_clone_clicked)

    def showEvent(self, event):
        super().showEvent(event)
        self._update_user_info()
        self.refresh_button.click()

    def closeEvent(self, event):
        try:
            self.github_manager.repos_ready.disconnect(self.populate_repo_list)
            self.github_manager.branches_ready.disconnect(
                self.populate_branch_list)
            self.github_manager.operation_failed.disconnect(
                self._on_operation_failed)
        except TypeError:
            pass  # Suppress errors if signals are not connected
        super().closeEvent(event)

    def _update_user_info(self):
        user_info = self.github_manager.get_user_info()
        if user_info and user_info.get('login'):
            self.user_label.setText(
                f"Authenticated as: <b>{user_info['login']}</b>")
        else:
            self.user_label.setText(
                "<i>Authentication details not available.</i>")

    def populate_repo_list(self, repos: List[Dict[str, Any]]):
        self.repo_list.clear()
        for repo in sorted(repos, key=lambda r: r['name'].lower()):
            item = QListWidgetItem(repo['name'])
            item.setToolTip(repo['full_name'])
            item.setData(Qt.ItemDataRole.UserRole, repo)
            self.repo_list.addItem(item)

    def populate_branch_list(self, branches: List[Dict[str, Any]]):
        self.branch_list.clear()
        for branch in branches:
            item = QListWidgetItem(branch['name'])
            item.setData(Qt.ItemDataRole.UserRole, branch)
            self.branch_list.addItem(item)
        if branches:
            self.branch_list.setCurrentRow(0)

    def on_repo_selected(self, current_item: QListWidgetItem):
        self.branch_list.clear()
        self.clone_button.setEnabled(False)
        if not current_item:
            self.repo_details_label.setText("<i>Select a repository...</i>")
            return
        repo_data = current_item.data(Qt.ItemDataRole.UserRole)
        desc = repo_data.get('description') or 'No description provided.'
        self.repo_details_label.setText(
            f"<b>{repo_data['full_name']}</b><br/><small>{desc}</small>")
        self.github_manager.list_branches(repo_data['full_name'])
        self.clone_button.setEnabled(True)

    def on_clone_clicked(self):
        repo_item = self.repo_list.currentItem()
        branch_item = self.branch_list.currentItem()
        if not repo_item or not branch_item:
            QMessageBox.warning(self, "Selection Required",
                                "Please select a repository and a branch.")
            return
        repo_data = repo_item.data(Qt.ItemDataRole.UserRole)
        branch_data = branch_item.data(Qt.ItemDataRole.UserRole)
        path = QFileDialog.getExistingDirectory(
            self, f"Select Folder to Clone '{repo_data['name']}' Into")
        if not path:
            return
        clone_path = os.path.join(path, repo_data['name'])
        if os.path.exists(clone_path):
            QMessageBox.critical(
                self, "Folder Exists",
                f"The folder '{repo_data['name']}' already exists here.")
            return
        self.git_manager.clone_repo(
            repo_data['clone_url'], path, branch_data['name'])
        QMessageBox.information(
            self, "Clone Started",
            "Cloning has started. The project will open when complete.")
        self.project_cloned.emit(clone_path)
        self.accept()

    def _on_operation_failed(self, error_message: str):
        QMessageBox.critical(self, "GitHub Error", error_message)

```

### File: `/plugins/github_tools/new_release_dialog.py`

```python
# PuffinPyEditor/plugins/github_tools/new_release_dialog.py
from typing import Optional, Dict, Any
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QFormLayout,
                             QDialogButtonBox, QLineEdit, QTextEdit, QLabel,
                             QCheckBox, QComboBox, QHBoxLayout, QWidget,
                             QGroupBox, QPushButton, QMessageBox)
from app_core.source_control_manager import SourceControlManager
from utils.versioning import suggest_next_version

try:
    import git
except ImportError:
    git = None


class NewReleaseDialog(QDialog):
    """
    A dialog for creating a new GitHub release. It collects tag name, title,
    notes, and other release options.
    """

    def __init__(self, project_path: str, git_manager: SourceControlManager,
                 parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.project_path = project_path
        self.git_manager = git_manager

        self.setWindowTitle("Create New Release")
        self.setMinimumWidth(500)

        self._setup_ui()
        self._connect_signals()
        self._populate_branches()
        self._validate_input()

    def _setup_ui(self):
        """Creates the main UI layout and widgets."""
        self.main_layout = QVBoxLayout(self)

        # Use a FormLayout for standard label-field pairs
        form_layout = QFormLayout()
        form_layout.setRowWrapPolicy(QFormLayout.RowWrapPolicy.WrapAllRows)

        # Tag Name
        tag_layout_widget = QWidget()
        tag_layout = QHBoxLayout(tag_layout_widget)
        tag_layout.setContentsMargins(0, 0, 0, 0)
        suggested_tag = suggest_next_version()
        self.tag_edit = QLineEdit(suggested_tag)
        self.tag_edit.setPlaceholderText("e.g., v1.2.1")
        self.branch_combo = QComboBox()
        self.branch_combo.setToolTip(
            "Select the branch to create the release from.")
        tag_layout.addWidget(self.tag_edit, 2)
        tag_layout.addWidget(QLabel("on branch:"))
        tag_layout.addWidget(self.branch_combo, 1)
        form_layout.addRow("<b>Tag Name:</b>", tag_layout_widget)

        # Release Title
        self.title_edit = QLineEdit()
        self.title_edit.setText(suggested_tag)
        self.title_edit.setPlaceholderText(
            "e.g., Feature Update and Bug Fixes")
        form_layout.addRow("<b>Release Title:</b>", self.title_edit)

        # Add the form layout to the main dialog layout
        self.main_layout.addLayout(form_layout)

        # --- Release Notes Section (manual layout) ---
        notes_header_layout = QHBoxLayout()
        notes_header_layout.addWidget(QLabel("<b>Release Notes:</b>"))
        notes_header_layout.addStretch()
        self.generate_notes_button = QPushButton("Generate from Commits")
        self.generate_notes_button.setToolTip(
            "Generate release notes from commits since the last tag.")
        notes_header_layout.addWidget(self.generate_notes_button)
        self.main_layout.addLayout(notes_header_layout)

        self.notes_edit = QTextEdit()
        self.notes_edit.setPlaceholderText(
            "Describe the changes in this release (Markdown is supported).")
        self.notes_edit.setMinimumHeight(150)
        self.main_layout.addWidget(self.notes_edit)
        # --- End of Release Notes Section ---

        # Options and Assets Groups
        options_group = QGroupBox("Options")
        options_layout = QVBoxLayout(options_group)
        self.prerelease_checkbox = QCheckBox("Mark as a pre-release")
        self.prerelease_checkbox.setToolTip(
            "Indicates that this is not a production-ready release.")
        options_layout.addWidget(self.prerelease_checkbox)
        options_layout.addStretch()
        self.main_layout.addWidget(options_group)

        assets_group = QGroupBox("Release Assets")
        assets_layout = QVBoxLayout(assets_group)
        self.build_installer_checkbox = QCheckBox(
            "Build and attach installer")
        self.build_installer_checkbox.setToolTip(
            "Runs the project's build script and uploads the setup file.")
        self.build_installer_checkbox.setChecked(True)
        assets_layout.addWidget(self.build_installer_checkbox)
        assets_layout.addStretch()
        self.main_layout.addWidget(assets_group)

        # Dialog Buttons
        self.button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok |
            QDialogButtonBox.StandardButton.Cancel
        )
        self.main_layout.addWidget(self.button_box)

    def _connect_signals(self):
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        self.tag_edit.textChanged.connect(self._validate_input)
        self.title_edit.textChanged.connect(self._validate_input)
        self.generate_notes_button.clicked.connect(
            self._generate_release_notes)

    def _populate_branches(self):
        branches = self.git_manager.get_local_branches(self.project_path)
        self.branch_combo.addItems(branches)
        if 'main' in branches:
            self.branch_combo.setCurrentText('main')
        elif 'master' in branches:
            self.branch_combo.setCurrentText('master')

    def _validate_input(self):
        is_valid = bool(
            self.tag_edit.text().strip() and
            self.title_edit.text().strip() and
            self.branch_combo.currentText()
        )
        ok_button = self.button_box.button(QDialogButtonBox.StandardButton.Ok)
        ok_button.setEnabled(is_valid)

    def _generate_release_notes(self):
        if git is None:
            QMessageBox.critical(
                self, "Missing Dependency",
                "The 'GitPython' library is not installed. Please install it "
                "(`pip install GitPython`) to use this feature.")
            return
        try:
            repo = git.Repo(self.project_path, search_parent_directories=True)
            tags = sorted(repo.tags, key=lambda t: t.commit.committed_datetime)
            latest_tag = tags[-1] if tags else None
            latest_tag_name = latest_tag.name if latest_tag else "the beginning"
            target_branch = self.branch_combo.currentText()

            rev_range = target_branch
            if latest_tag:
                rev_range = f"{latest_tag.commit.hexsha}..{target_branch}"

            commits = list(repo.iter_commits(rev_range))
            commit_log = []
            for commit in commits:
                if len(commit.parents) > 1:  # Skip merge commits
                    continue
                commit_log.append(f"- {commit.summary} ({commit.hexsha[:7]})")

            if commit_log:
                self.notes_edit.setText("\n".join(commit_log))
            else:
                QMessageBox.information(
                    self, "No New Commits",
                    "No new commits found on branch "
                    f"'{target_branch}' since tag '{latest_tag_name}'.")
        except Exception as e:
            QMessageBox.critical(self, "Error Generating Notes",
                                 f"An error occurred: {e}")

    def get_release_data(self) -> Dict[str, Any]:
        return {
            "tag": self.tag_edit.text().strip(),
            "title": self.title_edit.text().strip(),
            "notes": self.notes_edit.toPlainText().strip(),
            "prerelease": self.prerelease_checkbox.isChecked(),
            "target_branch": self.branch_combo.currentText(),
            "build_installer": self.build_installer_checkbox.isChecked()
        }
```

### File: `/plugins/github_tools/plugin.json`

```json
{
    "id": "github_tools",
    "name": "GitHub Tools",
    "author": "PuffinPy Team",
    "version": "1.2.0",
    "description": "Provides UI for cloning, releases, and other GitHub interactions.",
    "entry_point": "plugin_main.py"
}
```

### File: `/plugins/github_tools/plugin_main.py`

```python
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
        self._advance_release_state("PULL_CHANGES")

    def _advance_release_state(self, next_step):
        self._release_state['step'] = next_step
        step = next_step
        dialog_data, project_path = self._release_state['dialog_data'], self._release_state['project_path']
        self._cleanup_all_connections()
        step_title = step.replace('_', ' ').title()
        if sc_panel := self._get_sc_panel(): sc_panel.set_ui_locked(True, f"Step: {step_title}...")
        if self.progress_dialog: self.progress_dialog.set_step(step_title)

        author = self._release_state.get('author')
        if not author:
            try:
                repo = git.Repo(project_path)
                with repo.config_reader() as cr:
                    name = cr.get_value('user', 'name')
                    email = cr.get_value('user', 'email')
                author = Actor(name, email)
                self._release_state['author'] = author
            except Exception as e:
                self._on_release_step_failed(f"Could not read Git author info: {e}")
                return

        if step == "PULL_CHANGES":
            self.git_manager.git_success.connect(self._on_release_step_succeeded)
            self.git_manager.git_error.connect(self._on_release_step_failed)
            self.git_manager.pull(project_path)
        elif step == "BUMP_VERSION_COMMIT":
            if not versioning.write_new_version(dialog_data['tag']):
                self._on_release_step_failed("Failed to write new version to VERSION.txt.")
                return
            self.main_window._update_window_title()
            self.git_manager.git_success.connect(self._on_release_step_succeeded)
            self.git_manager.git_error.connect(self._on_release_step_failed)
            self.git_manager.commit_files(project_path, f"ci: Release {dialog_data['tag']}", author)
        
        elif step == "PUSH_MAIN_BRANCH":
            self.git_manager.git_success.connect(self._on_release_step_succeeded)
            self.git_manager.git_error.connect(self._on_release_step_failed)
            self.git_manager.push(project_path)

        elif step == "CREATE_TAG":
            self.git_manager.git_success.connect(self._on_release_step_succeeded)
            self.git_manager.git_error.connect(self._on_release_step_failed)
            self.git_manager.create_tag(project_path, dialog_data['tag'], dialog_data['title'], author)

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

    def _on_release_step_succeeded(self, msg, data):
        step = self._release_state.get('step')
        self._log_to_dialog(f"SUCCESS on step '{step}': {msg}")
        
        # New logical flow
        if step == "PULL_CHANGES":
            self._advance_release_state("BUMP_VERSION_COMMIT")
        elif step == "BUMP_VERSION_COMMIT":
            self._advance_release_state("PUSH_MAIN_BRANCH")
        elif step == "PUSH_MAIN_BRANCH":
            self._advance_release_state("CREATE_TAG")
        elif step == "CREATE_TAG":
            self._advance_release_state("PUSH_TAG")
        elif step == "PUSH_TAG":
            self._advance_release_state("CREATE_RELEASE")
        elif step == "CREATE_RELEASE":
            self._release_state['release_info'] = data.get("release_data", {})
            self._advance_release_state(
                "BUILD_ASSETS" if self._release_state['dialog_data'].get("build_installer") else "UPLOAD_ASSETS")
        elif step == "UPLOAD_ASSET":
            self._upload_next_asset()


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
            self._log_to_dialog("No assets to upload, finishing release.")
            self._cleanup_release_process(success=True) # End of the line if no assets
            return

        self._release_state['asset_queue'] = assets_to_upload
        self._log_to_dialog(f"Found {len(assets_to_upload)} asset(s) to upload.")
        self._upload_next_asset()

    def _upload_next_asset(self):
        asset_queue = self._release_state.get('asset_queue', [])
        if not asset_queue:
            self._log_to_dialog("All assets uploaded successfully.")
            self._cleanup_release_process(success=True) # End of the line
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
```

### File: `/plugins/github_tools/select_repo_dialog.py`

```python
# PuffinPyEditor/plugins/github_tools/select_repo_dialog.py
from typing import Optional, List, Dict, Any
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QListWidget,
                             QListWidgetItem, QDialogButtonBox, QMessageBox,
                             QLineEdit, QHBoxLayout, QLabel, QWidget)
from PyQt6.QtCore import Qt
from app_core.github_manager import GitHubManager


class SelectRepoDialog(QDialog):
    """
    A reusable dialog for selecting a GitHub repository from a user's account.
    """
    def __init__(self, github_manager: GitHubManager,
                 parent: Optional[QWidget] = None,
                 title: str = "Select Target Repository"):
        super().__init__(parent)
        self.github_manager = github_manager
        self.selected_repo_data: Optional[Dict[str, Any]] = None
        self.all_repos: List[Dict[str, Any]] = []

        self.setWindowTitle(title)
        self.setMinimumSize(500, 400)
        self.main_layout = QVBoxLayout(self)

        self._setup_ui()
        self._connect_signals()
        self.github_manager.list_repos()

    def _setup_ui(self):
        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("Filter:"))
        self.filter_edit = QLineEdit()
        self.filter_edit.setPlaceholderText("Type to filter repositories...")
        search_layout.addWidget(self.filter_edit)
        self.main_layout.addLayout(search_layout)

        self.repo_list_widget = QListWidget()
        self.repo_list_widget.itemDoubleClicked.connect(self.accept)
        self.main_layout.addWidget(self.repo_list_widget)

        self.button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok |
            QDialogButtonBox.StandardButton.Cancel
        )
        self.main_layout.addWidget(self.button_box)
        ok_button = self.button_box.button(QDialogButtonBox.StandardButton.Ok)
        ok_button.setEnabled(False)

    def _connect_signals(self):
        self.github_manager.repos_ready.connect(self._handle_repos_loaded)
        self.github_manager.operation_failed.connect(self._on_load_failed)
        self.filter_edit.textChanged.connect(self._filter_repo_list)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)

    def closeEvent(self, event):
        try:
            self.github_manager.repos_ready.disconnect(
                self._handle_repos_loaded)
            self.github_manager.operation_failed.disconnect(
                self._on_load_failed)
        except TypeError:
            pass  # Suppress errors if signals are not connected
        super().closeEvent(event)

    def _handle_repos_loaded(self, repos: List[Dict[str, Any]]):
        self.all_repos = sorted(repos, key=lambda r: r['full_name'].lower())
        self._populate_repo_list()
        if self.repo_list_widget.count() > 0:
            ok_button = self.button_box.button(
                QDialogButtonBox.StandardButton.Ok)
            ok_button.setEnabled(True)
            self.repo_list_widget.setCurrentRow(0)

    def _populate_repo_list(self):
        self.repo_list_widget.clear()
        filter_text = self.filter_edit.text().lower()
        for repo in self.all_repos:
            if filter_text in repo['full_name'].lower():
                item = QListWidgetItem(repo['full_name'])
                item.setToolTip(repo.get('description', 'No description'))
                item.setData(Qt.ItemDataRole.UserRole, repo)
                self.repo_list_widget.addItem(item)

    def _filter_repo_list(self):
        self._populate_repo_list()

    def _on_load_failed(self, error_message: str):
        QMessageBox.critical(self, "Failed to Load Repositories",
                             error_message)
        self.reject()

    def accept(self):
        current_item = self.repo_list_widget.currentItem()
        if not current_item:
            QMessageBox.warning(self, "No Selection",
                                "Please select a repository.")
            return
        self.selected_repo_data = current_item.data(Qt.ItemDataRole.UserRole)
        super().accept()
```

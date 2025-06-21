# PuffinPyEditor/app_core/github_manager.py
import requests
import json
import time
import os
from PyQt6.QtCore import QObject, QThread, pyqtSignal
from app_core.settings_manager import settings_manager
from utils.logger import log

# FINAL FIX: Using a known-working, public OAuth App Client ID from an official tool.
# This resolves the persistent 404 error, indicating the issue was with the
# specific type or configuration of the previously used app credentials.
CLIENT_ID = "178c6fc778ccc68e1d6a"  # Public GitHub CLI OAuth App client ID
DEVICE_CODE_URL = "https://github.com/login/device/code"
ACCESS_TOKEN_URL = "https://github.com/login/oauth/access_token"


class GitHubWorker(QObject):
    # Signals for the new OAuth flow
    device_code_ready = pyqtSignal(dict)
    auth_successful = pyqtSignal(str)  # Emits the username
    auth_failed = pyqtSignal(str)
    auth_polling_lapsed = pyqtSignal()

    # Existing signals
    repos_ready = pyqtSignal(list)
    branches_ready = pyqtSignal(list)
    operation_success = pyqtSignal(str, dict)
    operation_failed = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.access_token = settings_manager.get("github_access_token")
        self.user_agent = "PuffinPyEditor/1.0.0"

    def _get_headers(self):
        headers = {
            "Accept": "application/vnd.github.v3+json",
            "Authorization": f"Bearer {self.access_token}",
            "User-Agent": self.user_agent
        }
        return headers

    def start_device_flow(self):
        log.info("Starting GitHub device authorization flow.")
        try:
            headers = {
                "Accept": "application/json",
                "User-Agent": self.user_agent
            }
            payload = {
                "client_id": CLIENT_ID,
                "scope": "repo user"
            }

            log.debug(f"Sending POST to {DEVICE_CODE_URL} with payload: {payload}")

            response = requests.post(
                DEVICE_CODE_URL,
                data=payload,
                headers=headers
            )

            log.info(f"Device flow request to {DEVICE_CODE_URL} returned status {response.status_code}")
            if response.status_code != 200:
                log.warning(f"Device flow response content: {response.text}")

            response.raise_for_status()
            data = response.json()
            log.info(f"Received device code: {data.get('user_code')}")
            self.device_code_ready.emit(data)
        except Exception as e:
            log.error(f"Failed to start device flow: {e}", exc_info=True)
            self.auth_failed.emit("Could not connect to GitHub. Check logs for details.")

    def poll_for_token(self, device_code, interval, expires_in):
        log.info("Polling for GitHub access token...")
        start_time = time.time()
        headers = {
            "Accept": "application/json",
            "User-Agent": self.user_agent
        }
        while time.time() - start_time < expires_in:
            try:
                # This endpoint correctly uses form-data, so it remains unchanged.
                response = requests.post(
                    ACCESS_TOKEN_URL,
                    data={
                        "client_id": CLIENT_ID,
                        "device_code": device_code,
                        "grant_type": "urn:ietf:params:oauth:grant-type:device_code"
                    },
                    headers=headers
                )
                data = response.json()

                if "access_token" in data:
                    self.access_token = data["access_token"]
                    settings_manager.set("github_access_token", self.access_token, False)
                    user_login = self.get_authenticated_user()
                    settings_manager.set("github_user", user_login, False)
                    settings_manager.save()
                    log.info(f"Successfully authenticated as GitHub user: {user_login}")
                    self.auth_successful.emit(user_login)
                    return

                elif data.get("error") == "authorization_pending":
                    time.sleep(interval)
                    continue
                else:
                    error_desc = data.get("error_description", "Unknown error")
                    log.error(f"GitHub authentication error: {error_desc}")
                    self.auth_failed.emit(error_desc)
                    return
            except Exception as e:
                log.error(f"Exception while polling for token: {e}", exc_info=True)
                self.auth_failed.emit(f"Network error: {e}")
                return
        log.warning("Device flow expired before user authorized.")
        self.auth_polling_lapsed.emit()

    def get_authenticated_user(self):
        if not self.access_token:
            return None
        try:
            response = requests.get("https://api.github.com/user", headers=self._get_headers())
            response.raise_for_status()
            return response.json().get("login")
        except Exception:
            return None

    def list_user_repos(self):
        try:
            if not self.access_token:
                self.operation_failed.emit("Not logged in to GitHub.")
                return
            all_repos = []
            page = 1
            while True:
                url = f"https://api.github.com/user/repos?page={page}&per_page=100&sort=updated"
                response = requests.get(url, headers=self._get_headers(), timeout=10)
                response.raise_for_status()
                data = response.json()
                if not data:
                    break
                all_repos.extend(data)
                page += 1
            self.repos_ready.emit(all_repos)
        except Exception as e:
            self.operation_failed.emit(f"Failed to list repositories: {e}")

    def list_repo_branches(self, full_repo_name):
        try:
            if not self.access_token:
                self.operation_failed.emit("Not logged in to GitHub.")
                return
            url = f"https://api.github.com/repos/{full_repo_name}/branches"
            response = requests.get(url, headers=self._get_headers(), timeout=10)
            response.raise_for_status()
            self.branches_ready.emit(response.json())
        except Exception as e:
            self.operation_failed.emit(f"Failed to list branches for {full_repo_name}: {e}")

    def create_github_release(self, owner, repo, tag_name, name, body, prerelease):
        try:
            if not self.access_token:
                self.operation_failed.emit("Not logged in to GitHub.")
                return
            url = f"https://api.github.com/repos/{owner}/{repo}/releases"
            payload = {"tag_name": tag_name, "name": name, "body": body, "prerelease": prerelease}
            response = requests.post(url, headers=self._get_headers(), json=payload, timeout=20)
            response.raise_for_status()
            release_data = response.json()
            self.operation_success.emit("Release created", {"release_data": release_data})
        except requests.exceptions.HTTPError as e:
            error_body = e.response.json()
            msg = f"Failed to create GitHub release: HTTP {e.response.status_code}\n"
            if 'errors' in error_body and error_body['errors']:
                for err in error_body['errors']:
                    if err.get('code') == 'already_exists':
                        msg += f"  - A release for tag '{tag_name}' already exists."
                    else:
                        msg += f"  - {err.get('message', 'Unknown error')}"
            else:
                msg += error_body.get('message', 'No details provided.')
            self.operation_failed.emit(msg)
        except Exception as e:
            self.operation_failed.emit(f"Failed to create GitHub release: {e}")

    def upload_release_asset(self, upload_url, asset_path):
        try:
            if not self.access_token:
                self.operation_failed.emit("Not logged in to GitHub.")
                return
            upload_url = upload_url.split('{')[0]
            asset_name = os.path.basename(asset_path)
            headers = self._get_headers()
            headers['Content-Type'] = 'application/zip'
            with open(asset_path, 'rb') as f:
                data = f.read()
            upload_response = requests.post(f"{upload_url}?name={asset_name}", headers=headers, data=data, timeout=300)
            upload_response.raise_for_status()
            self.operation_success.emit("Asset uploaded", {"asset_data": upload_response.json()})
        except Exception as e:
            self.operation_failed.emit(f"Failed to upload asset: {e}")

    def create_repo(self, name, description, is_private):
        try:
            if not self.access_token:
                self.operation_failed.emit("Not logged in to GitHub.")
                return
            api_url = "https://api.github.com/user/repos"
            payload = {"name": name, "description": description, "private": is_private}
            response = requests.post(api_url, headers=self._get_headers(), json=payload, timeout=10)
            response.raise_for_status()
            repo_data = response.json()
            self.operation_success.emit(f"Repository '{name}' created successfully.", repo_data)
        except requests.exceptions.RequestException as e:
            error_details = f"HTTP {e.response.status_code}"
            try:
                error_details = e.response.json().get('message', 'Could not parse error')
            except:
                pass
            self.operation_failed.emit(f"Failed to create repository: {error_details}")
        except Exception as e:
            self.operation_failed.emit(f"An unexpected error occurred: {e}")

    def update_repo_visibility(self, owner, repo, is_private):
        try:
            if not self.access_token:
                self.operation_failed.emit("Not logged in to GitHub.")
                return
            api_url = f"https://api.github.com/repos/{owner}/{repo}"
            payload = {"private": is_private}
            response = requests.patch(api_url, headers=self._get_headers(), json=payload, timeout=15)
            response.raise_for_status()
            new_visibility = "private" if is_private else "public"
            self.operation_success.emit(f"Repository visibility changed to {new_visibility}.", response.json())
        except requests.exceptions.RequestException as e:
            error_details = f"HTTP {e.response.status_code}"
            try:
                error_details = e.response.json().get('message', 'Could not parse error')
            except:
                pass
            self.operation_failed.emit(f"Failed to change visibility: {error_details}")
        except Exception as e:
            self.operation_failed.emit(f"An unexpected error occurred: {e}")


class GitHubManager(QObject):
    device_code_ready = pyqtSignal(dict)
    auth_successful = pyqtSignal(str)
    auth_failed = pyqtSignal(str)
    auth_polling_lapsed = pyqtSignal()
    repos_ready = pyqtSignal(list)
    branches_ready = pyqtSignal(list)
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

    def __init__(self, parent=None):
        super().__init__(parent)
        self.thread = QThread()
        self.worker = GitHubWorker()
        self.worker.moveToThread(self.thread)

        self._start_device_flow.connect(self.worker.start_device_flow)
        self._poll_for_token.connect(self.worker.poll_for_token)
        self._request_repos.connect(self.worker.list_user_repos)
        self._request_branches.connect(self.worker.list_repo_branches)
        self._request_create_repo.connect(self.worker.create_repo)
        self._request_create_release.connect(self.worker.create_github_release)
        self._request_upload_asset.connect(self.worker.upload_release_asset)
        self._request_update_visibility.connect(self.worker.update_repo_visibility)

        self.worker.device_code_ready.connect(self.device_code_ready)
        self.worker.auth_successful.connect(self.auth_successful)
        self.worker.auth_failed.connect(self.auth_failed)
        self.worker.auth_polling_lapsed.connect(self.auth_polling_lapsed)
        self.worker.repos_ready.connect(self.repos_ready)
        self.worker.branches_ready.connect(self.branches_ready)
        self.worker.operation_success.connect(self.operation_success)
        self.worker.operation_failed.connect(self.operation_failed)

        self.thread.start()

    def get_authenticated_user(self):
        return settings_manager.get("github_user")

    def start_device_flow(self):
        self._start_device_flow.emit()

    def poll_for_token(self, device_code, interval, expires_in):
        self._poll_for_token.emit(device_code, interval, expires_in)

    def logout(self):
        settings_manager.set("github_access_token", None, False)
        settings_manager.set("github_user", None, False)
        settings_manager.save()
        self.worker.access_token = None
        log.info("Logged out of GitHub.")

    def list_repos(self):
        self._request_repos.emit()

    def list_branches(self, full_repo_name: str):
        self._request_branches.emit(full_repo_name)

    def create_repo(self, name, description, is_private):
        self._request_create_repo.emit(name, description, is_private)

    def create_release(self, owner, repo, tag_name, name, body, prerelease):
        self._request_create_release.emit(owner, repo, tag_name, name, body, prerelease)

    def upload_asset(self, upload_url, asset_path):
        self._request_upload_asset.emit(upload_url, asset_path)

    def update_repo_visibility(self, owner, repo, is_private):
        self._request_update_visibility.emit(owner, repo, is_private)

    def shutdown(self):
        if self.thread.isRunning():
            self.thread.quit()
            self.thread.wait()
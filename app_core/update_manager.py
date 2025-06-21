# PuffinPyEditor/app_core/update_manager.py
import requests
from packaging import version
from PyQt6.QtCore import QObject, pyqtSignal
from utils.logger import log
from app_core.settings_manager import settings_manager

APP_CURRENT_VERSION = "1.0.0"

class UpdateManager(QObject):
    update_check_finished = pyqtSignal(dict)

    def check_for_updates(self):
        log.info("Checking for application updates...")

        active_repo_id = settings_manager.get("active_update_repo_id")
        if not active_repo_id:
            msg = "No active repository set for updates in Preferences -> Source Control."
            log.error(f"Update check failed: {msg}")
            self.update_check_finished.emit({"error": msg})
            return

        all_repos = settings_manager.get("source_control_repos", [])
        active_repo_config = next((repo for repo in all_repos if repo.get("id") == active_repo_id), None)

        if not active_repo_config:
            msg = f"Active repository with ID '{active_repo_id}' not found in configuration."
            log.error(f"Update check failed: {msg}")
            self.update_check_finished.emit({"error": msg})
            return

        owner = active_repo_config.get("owner")
        repo = active_repo_config.get("repo")

        if not owner or not repo:
            msg = f"Active repository '{active_repo_id}' is missing owner or repo name."
            log.error(f"Update check failed: {msg}")
            self.update_check_finished.emit({"error": "Active repository configuration is incomplete."})
            return

        github_api_url = f"https://api.github.com/repos/{owner}/{repo}/releases/latest"
        log.info(f"Using GitHub API URL for updates: {github_api_url}")

        try:
            response = requests.get(github_api_url, timeout=10)
            response.raise_for_status()
            release_data = response.json()
            latest_version_tag = release_data.get("tag_name", "").lstrip('v')
            log.info(f"Latest release tag found: {latest_version_tag}")

            if not latest_version_tag:
                self.update_check_finished.emit({"error": "Latest release has no version tag."})
                return

            if version.parse(latest_version_tag) > version.parse(APP_CURRENT_VERSION):
                log.info(f"New version available: {latest_version_tag}")
                result = {
                    "update_available": True,
                    "latest_version": latest_version_tag,
                    "release_notes": release_data.get("body", "No release notes provided."),
                    "download_url": None
                }
                for asset in release_data.get("assets", []):
                    if asset.get("name", "").endswith(".zip"):
                        result["download_url"] = asset.get("browser_download_url")
                        break
                self.update_check_finished.emit(result)
            else:
                log.info("Application is up to date.")
                self.update_check_finished.emit({"update_available": False})

        except requests.exceptions.HTTPError as e:
            msg = f"HTTP Error checking for updates: {e.response.status_code}"
            log.error(msg)
            self.update_check_finished.emit({"error": msg})
        except requests.exceptions.RequestException as e:
            msg = f"Network error checking for updates: {e}"
            log.error(msg)
            self.update_check_finished.emit({"error": msg})
        except Exception as e:
            msg = f"An unexpected error occurred during update check: {e}"
            log.critical(msg, exc_info=True)
            self.update_check_finished.emit({"error": "An unexpected error occurred."})

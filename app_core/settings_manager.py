# PuffinPyEditor/app_core/settings_manager.py
import json
import os
from utils.logger import log

SETTINGS_FILE = "puffin_editor_settings.json"

DEFAULT_SETTINGS = {
    "window_size": [1200, 800],
    "window_position": None,
    "last_theme_id": "puffin_dark",
    "font_family": "Consolas",
    "font_size": 11,
    "show_line_numbers": True,
    "word_wrap": False,
    "open_projects": [],
    "active_project_path": None,
    "splitter_sizes": [250, 950],
    "github_access_token": None,  # Replaces github_pat
    "github_user": None,  # New: To store the username
    "source_control_repos": [],
    "active_update_repo_id": None,
    "source_control_auto_fetch_enabled": False,
    "source_control_auto_fetch_interval_minutes": 15,
}


class SettingsManager:
    def __init__(self, settings_file=SETTINGS_FILE):
        self.settings_file = settings_file
        self.settings = self._load_settings()

    def _load_settings(self):
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    loaded_settings = json.load(f)

                # Migrate old 'github_pat' to 'github_access_token' if it exists
                if "github_pat" in loaded_settings and "github_access_token" not in loaded_settings:
                    loaded_settings["github_access_token"] = loaded_settings.pop("github_pat")
                    log.info("Migrated old 'github_pat' setting.")

                settings = DEFAULT_SETTINGS.copy()
                settings.update(loaded_settings)

                log.debug("Successfully loaded and merged settings.")
                return settings
            else:
                log.info(f"Settings file '{self.settings_file}' not found. Creating with defaults.")
                self._save_settings(DEFAULT_SETTINGS.copy())
                return DEFAULT_SETTINGS.copy()
        except Exception as e:
            log.error(f"Error loading settings: {e}. Using default settings.", exc_info=True)
            return DEFAULT_SETTINGS.copy()

    def _save_settings(self, settings_data):
        try:
            temp_file = self.settings_file + ".tmp"
            with open(temp_file, 'w', encoding='utf-8') as f:
                json.dump(settings_data, f, indent=4)
            os.replace(temp_file, self.settings_file)

        except Exception as e:
            log.error(f"Error saving settings: {e}", exc_info=True)

    def get(self, key, default=None):
        return self.settings.get(key, DEFAULT_SETTINGS.get(key, default))

    def set(self, key, value, save_immediately=True):
        self.settings[key] = value
        if save_immediately:
            self.save()

    def save(self):
        self._save_settings(self.settings)


settings_manager = SettingsManager()
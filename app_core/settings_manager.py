# PuffinPyEditor/app_core/settings_manager.py
import json
import os
from typing import Any, Dict
from utils.logger import log, get_app_data_path

# Use the same application data path for the settings file to ensure it's
# in a user-writable location, especially after installation.
APP_DATA_ROOT = get_app_data_path()
SETTINGS_FILE = os.path.join(APP_DATA_ROOT, "puffin_editor_settings.json")

DEFAULT_SETTINGS = {
    # --- Window & Layout ---
    "window_size": [1600, 1000],
    "window_position": None,
    "splitter_sizes": [300, 1300],

    # --- Editor & Appearance ---
    "last_theme_id": "puffin_dark",
    "font_family": "Consolas",
    "font_size": 11,
    "show_line_numbers": True,
    "show_indentation_guides": True,
    "word_wrap": False,
    "indent_style": "spaces",  # "spaces" or "tabs"
    "indent_width": 4,

    # --- File Handling ---
    "auto_save_enabled": False,
    "auto_save_delay_seconds": 3,
    "max_recent_files": 15,
    "favorites": [],
    "open_files": [],

    # --- Project State ---
    "open_projects": [],
    "active_project_path": None,
    "explorer_expanded_paths": [],

    # --- Integrations & Run ---
    "python_interpreter_path": "",
    "github_access_token": None,
    "github_user": None,
    "source_control_repos": [],
    "active_update_repo_id": None,
    "plugins_distro_repo": "Stelliro/puffin-plugins",
    "commit_message_history": [],  # NEW: For storing commit history
    "max_commit_history": 50,      # NEW: To limit the history size
    "ai_export_loadouts": {},
    "ai_export_golden_rules": {},  # MODIFIED: Start with an empty dictionary
    "cleanup_after_build": True,
    "nsis_path": ""
}


class SettingsManager:
    """Handles loading, accessing, and saving application settings."""

    def __init__(self, settings_file: str = SETTINGS_FILE):
        self.settings_file = settings_file
        self.settings = self._load_settings()

    def _load_settings(self) -> Dict[str, Any]:
        """Loads settings from the JSON file, merging with defaults."""
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    loaded_settings = json.load(f)

                if "github_pat" in loaded_settings:
                    if "github_access_token" not in loaded_settings:
                        loaded_settings["github_access_token"] = \
                            loaded_settings.pop("github_pat")
                    else:
                        del loaded_settings["github_pat"]
                    log.info("Migrated old 'github_pat' setting.")

                settings = DEFAULT_SETTINGS.copy()
                settings.update(loaded_settings)
                return settings
            else:
                log.info(
                    f"Settings file not found. Creating with defaults "
                    f"at: {self.settings_file}"
                )
                self._save_settings(DEFAULT_SETTINGS.copy())
                return DEFAULT_SETTINGS.copy()
        except (json.JSONDecodeError, IOError) as e:
            log.error(f"Error loading settings: {e}. Reverting to defaults.",
                      exc_info=True)
            return DEFAULT_SETTINGS.copy()

    def _save_settings(self, settings_data: Dict[str, Any]):
        """Saves the provided settings data to the JSON file atomically."""
        try:
            os.makedirs(os.path.dirname(self.settings_file), exist_ok=True)
            temp_file = self.settings_file + ".tmp"
            with open(temp_file, 'w', encoding='utf-8') as f:
                json.dump(settings_data, f, indent=4)
            os.replace(temp_file, self.settings_file)
        except IOError as e:
            log.error(f"Error saving settings to {self.settings_file}: {e}",
                      exc_info=True)

    def get(self, key: str, default: Any = None) -> Any:
        return self.settings.get(key, DEFAULT_SETTINGS.get(key, default))

    def set(self, key: str, value: Any, save_immediately: bool = True):
        self.settings[key] = value
        if save_immediately:
            self.save()

    def save(self):
        """Saves the current settings to the disk."""
        self._save_settings(self.settings)


settings_manager = SettingsManager()
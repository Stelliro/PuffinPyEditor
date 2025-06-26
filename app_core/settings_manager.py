# PuffinPyEditor/app_core/settings_manager.py
import json
import os
from typing import Any, Dict, List
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

    # --- Project State ---
    "open_projects": [],
    "active_project_path": None,

    # --- Integrations & Run ---
    "python_interpreter_path": "",
    "github_access_token": None,
    "github_user": None,
    "source_control_repos": [],
    "active_update_repo_id": None,
    "plugins_distro_repo": "Stelliro/puffin-plugins",
    "run_in_background": False,
    "ai_export_loadouts": {},
    "ai_export_golden_rules": {
        "Default Golden Rules": [
            "Do not remove any code that is unrelated to the fix, only remove "
            "code if it is being substituted or is not needed anymore.",
            "Only edit and add features, the only features should stay unless "
            "asked to be removed, or may be completely redundant.",
            "any scripts over 1000 lines, please write in a new response.",
            "multiple scripts together exceeding 2000 lines together need to be "
            "separated into smaller responses, (example: these scripts have "
            "2340 lines together I'm going to separate it into 2 messages "
            "that way i dont lose formatting and dont accidentally remove "
            "any features)"
        ]
    },
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

                # Migration for old setting name
                if "github_pat" in loaded_settings:
                    if "github_access_token" not in loaded_settings:
                        loaded_settings["github_access_token"] = loaded_settings.pop("github_pat")
                    else:
                        del loaded_settings["github_pat"]
                    log.info("Migrated old 'github_pat' setting.")

                # Merge loaded settings with defaults to ensure all keys exist
                settings = DEFAULT_SETTINGS.copy()
                settings.update(loaded_settings)
                return settings
            else:
                log.info(f"Settings file not found. Creating with defaults "
                         f"at: {self.settings_file}")
                self._save_settings(DEFAULT_SETTINGS.copy())
                return DEFAULT_SETTINGS.copy()
        except (json.JSONDecodeError, IOError) as e:
            log.error(f"Error loading settings: {e}. Reverting to defaults.",
                      exc_info=True)
            return DEFAULT_SETTINGS.copy()

    def _save_settings(self, settings_data: Dict[str, Any]):
        """Saves the provided settings data to the JSON file atomically."""
        try:
            # Ensure the directory exists before writing
            os.makedirs(os.path.dirname(self.settings_file), exist_ok=True)
            temp_file = self.settings_file + ".tmp"
            with open(temp_file, 'w', encoding='utf-8') as f:
                json.dump(settings_data, f, indent=4)
            # Atomic move/rename
            os.replace(temp_file, self.settings_file)
        except IOError as e:
            log.error(f"Error saving settings to {self.settings_file}: {e}",
                      exc_info=True)

    def get(self, key: str, default: Any = None) -> Any:
        """
        Gets a setting value by key.

        Args:
            key: The key of the setting to retrieve.
            default: The value to return if the key is not found.

        Returns:
            The setting value.
        """
        return self.settings.get(key, DEFAULT_SETTINGS.get(key, default))

    def set(self, key: str, value: Any, save_immediately: bool = True):
        """
        Sets a setting value by key.

        Args:
            key: The key of the setting to set.
            value: The new value for the setting.
            save_immediately: If True, saves all settings to disk immediately.
        """
        self.settings[key] = value
        if save_immediately:
            self.save()

    def save(self):
        """Saves the current settings to the disk."""
        self._save_settings(self.settings)


# Singleton instance to be used across the application
settings_manager = SettingsManager()
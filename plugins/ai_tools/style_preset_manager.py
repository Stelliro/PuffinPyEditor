# /plugins/ai_tools/style_preset_manager.py
import os
import json
from typing import Dict, List, Optional, Tuple
from utils.logger import log
from utils.helpers import get_base_path

PRESETS_DIR = os.path.join(get_base_path(), "assets", "style_presets")

class StylePresetManager:
    """Handles loading, saving, and managing Style Presets."""

    def __init__(self):
        self._ensure_presets_dir_exists()
        self.presets = self.load_presets()

    def _ensure_presets_dir_exists(self):
        """Creates the style_presets directory if it doesn't exist."""
        if not os.path.isdir(PRESETS_DIR):
            try:
                os.makedirs(PRESETS_DIR)
                log.info(f"Created style presets directory: {PRESETS_DIR}")
            except OSError as e:
                log.error(f"Failed to create presets directory: {e}")

    def load_presets(self) -> Dict[str, Dict]:
        """
        Loads all .json files from the presets directory into a dictionary.
        The key is the filename without extension.
        """
        loaded_presets = {}
        if not os.path.isdir(PRESETS_DIR):
            return {}

        for filename in sorted(os.listdir(PRESETS_DIR)):
            if filename.endswith(".json"):
                preset_id = os.path.splitext(filename)[0]
                filepath = os.path.join(PRESETS_DIR, filename)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        if "name" in data and "rules" in data:
                            loaded_presets[preset_id] = data
                        else:
                            log.warning(f"Preset file '{filename}' is missing 'name' or 'rules' key.")
                except (json.JSONDecodeError, IOError) as e:
                    log.error(f"Failed to load preset '{filename}': {e}")
        return loaded_presets

    def get_preset_names_for_ui(self) -> List[Tuple[str, str]]:
        """Returns a list of (preset_id, preset_name) tuples for UI population."""
        return sorted([(pid, pdata.get("name", pid)) for pid, pdata in self.presets.items()], key=lambda x: x[1])

    def save_preset(self, preset_id: str, data: Dict) -> bool:
        """Saves a single preset to a .json file."""
        filepath = os.path.join(PRESETS_DIR, f"{preset_id}.json")
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4)
            log.info(f"Saved preset '{preset_id}'.")
            self.presets = self.load_presets()
            return True
        except IOError as e:
            log.error(f"Failed to save preset '{preset_id}': {e}")
            return False

    def delete_preset(self, preset_id: str) -> bool:
        """Deletes a preset file."""
        filepath = os.path.join(PRESETS_DIR, f"{preset_id}.json")
        if os.path.exists(filepath):
            try:
                os.remove(filepath)
                log.info(f"Deleted preset '{preset_id}'.")
                self.presets = self.load_presets()
                return True
            except OSError as e:
                log.error(f"Failed to delete preset '{preset_id}': {e}")
                return False
        return False
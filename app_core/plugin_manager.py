import os
import sys
import json
import importlib.util
import zipfile
import tempfile
import shutil
import re
from utils.logger import log


class PluginManager:

    def __init__(self, main_window):
        self.main_window = main_window
        self.plugins_directory = "plugins"
        self.loaded_plugins = {}

        if not os.path.isdir(self.plugins_directory):
            log.info(f"Creating plugins directory at: {os.path.abspath(self.plugins_directory)}")
            os.makedirs(self.plugins_directory)

    def discover_and_load_plugins(self):
        log.info("Starting plugin discovery...")
        for item_name in os.listdir(self.plugins_directory):
            plugin_path = os.path.join(self.plugins_directory, item_name)
            if not os.path.isdir(plugin_path) or item_name.startswith('__'): continue
            manifest_path = os.path.join(plugin_path, "plugin.json")
            if not os.path.exists(manifest_path): continue
            try:
                with open(manifest_path, 'r', encoding='utf-8') as f:
                    manifest = json.load(f)
                if self._validate_manifest(manifest, item_name): self._load_plugin(item_name, manifest)
            except Exception as e:
                log.error(f"Failed to process or load plugin '{item_name}': {e}", exc_info=True)

    def _validate_manifest(self, manifest, plugin_id):
        if not manifest.get("entry_point"): log.error(
            f"Manifest for '{plugin_id}' is missing 'entry_point'. Skipping."); return False
        entry_path = os.path.join(self.plugins_directory, plugin_id, manifest["entry_point"])
        if not os.path.exists(entry_path): log.error(
            f"Entry point '{manifest['entry_point']}' not found for '{plugin_id}'. Skipping."); return False
        return True

    def _load_plugin(self, plugin_id, manifest):
        plugin_path = os.path.join(self.plugins_directory, plugin_id)
        spec = importlib.util.spec_from_file_location(f"puffin_plugins.{plugin_id}.main",
                                                      os.path.join(plugin_path, manifest["entry_point"]))
        if not spec or not spec.loader: log.error(f"Could not create module spec for plugin: {plugin_id}"); return

        module = importlib.util.module_from_spec(spec)
        try:
            if plugin_path not in sys.path: sys.path.insert(0, plugin_path)
            spec.loader.exec_module(module)
            if hasattr(module, 'initialize'):
                self.loaded_plugins[plugin_id] = {"module": module, "instance": module.initialize(self.main_window),
                                                  "manifest": manifest}
                log.info(f"Successfully initialized plugin: {manifest.get('name', plugin_id)}")
            else:
                log.error(f"Plugin '{plugin_id}' has no 'initialize' function. Skipping.")
        finally:
            if plugin_path in sys.path: sys.path.remove(plugin_path)

    def install_plugin_from_zip(self, zip_filepath: str) -> tuple[bool, str]:
        if not zipfile.is_zipfile(zip_filepath): return False, "Not a valid zip archive."
        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                with zipfile.ZipFile(zip_filepath, 'r') as z:
                    z.extractall(temp_dir)

                items = os.listdir(temp_dir)
                src_dir = os.path.join(temp_dir, items[0]) if len(items) == 1 and os.path.isdir(
                    os.path.join(temp_dir, items[0])) else temp_dir

                manifest_path = os.path.join(src_dir, 'plugin.json')
                if not os.path.exists(
                    manifest_path): return False, "Archive does not contain a 'plugin.json' at its root."

                with open(manifest_path, 'r') as f:
                    manifest = json.load(f)
                plugin_id = manifest.get('id', os.path.basename(src_dir))

                target_path = os.path.join(self.plugins_directory, plugin_id)
                if os.path.exists(target_path): return False, f"A plugin named '{plugin_id}' already exists."

                shutil.move(src_dir, target_path)
                log.info(f"Plugin '{manifest.get('name', plugin_id)}' installed to '{target_path}'")
                return True, f"Plugin '{manifest.get('name', plugin_id)}' installed successfully."
        except Exception as e:
            log.error(f"Failed to install plugin from {zip_filepath}: {e}", exc_info=True)
            return False, f"An unexpected error occurred: {e}"
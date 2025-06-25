# PuffinPyEditor/app_core/plugin_manager.py
import os
import sys
import json
import importlib.util
import zipfile
import tempfile
import shutil
from utils.logger import log
from utils.helpers import get_base_path


class PluginManager:

    def __init__(self, main_window):
        self.main_window = main_window
        base_path = get_base_path()

        self.plugins_directory = os.path.join(base_path, "plugins")
        self.core_tools_directory = os.path.join(base_path, "core_debug_tools")
        log.info(f"Plugin search directories set to: {self.plugins_directory} and {self.core_tools_directory}")

        self.loaded_plugins = {}
        self.installed_plugins_metadata = []

        if not os.path.isdir(self.plugins_directory):
            log.info(f"Creating plugins directory at: {os.path.abspath(self.plugins_directory)}")
            os.makedirs(self.plugins_directory)

    def discover_and_load_plugins(self):
        """
        Discovers and loads all plugins from the /plugins directory.
        It also discovers metadata for core tools but does not load them.
        """
        log.info("Starting plugin discovery...")
        self.installed_plugins_metadata = []
        plugins_to_load = {}

        # Discover and process regular, user-installable plugins
        try:
            plugin_folders = [d for d in os.listdir(self.plugins_directory) if
                              os.path.isdir(os.path.join(self.plugins_directory, d)) and not d.startswith('__')]

            for item_name in plugin_folders:
                manifest_path = os.path.join(self.plugins_directory, item_name, "plugin.json")
                if not os.path.exists(manifest_path):
                    continue
                try:
                    with open(manifest_path, 'r', encoding='utf-8') as f:
                        manifest = json.load(f)

                    plugin_id = manifest.get('id', item_name)
                    manifest['id'] = plugin_id
                    manifest['is_core'] = True # Mark all built-in plugins as core/non-deletable
                    self.installed_plugins_metadata.append(manifest)
                    plugins_to_load[item_name] = manifest
                except (json.JSONDecodeError, IOError) as e:
                    log.error(f"Failed to read manifest for plugin '{item_name}': {e}")
        except FileNotFoundError:
            log.error(f"Plugins directory not found at '{self.plugins_directory}'.")

        # Discover metadata for core debug tools (for UI listing only)
        try:
            if os.path.isdir(self.core_tools_directory):
                tool_folders = [d for d in os.listdir(self.core_tools_directory) if
                                os.path.isdir(os.path.join(self.core_tools_directory, d)) and not d.startswith('__')]

                for item_name in tool_folders:
                    manifest_path = os.path.join(self.core_tools_directory, item_name, "plugin.json")
                    if not os.path.exists(manifest_path):
                        continue
                    try:
                        with open(manifest_path, 'r', encoding='utf-8') as f:
                            manifest = json.load(f)
                        plugin_id = manifest.get('id', item_name)
                        manifest['id'] = plugin_id
                        manifest['is_core'] = True
                        self.installed_plugins_metadata.append(manifest)
                        # NOTE: We do NOT add these to `plugins_to_load`. They are loaded separately.
                    except (json.JSONDecodeError, IOError) as e:
                        log.error(f"Failed to read manifest for core tool '{item_name}': {e}")
        except FileNotFoundError:
            log.warning(f"Core debug tools directory not found at '{self.core_tools_directory}'.")


        # Load the regular plugins
        for item_name, manifest in plugins_to_load.items():
            try:
                if self._validate_manifest(manifest, item_name):
                    self._load_plugin(item_name, manifest)
            except Exception as e:
                log.error(f"Failed to process or load plugin '{item_name}': {e}", exc_info=True)

    def _validate_manifest(self, manifest, plugin_id):
        if not manifest.get("entry_point"):
            entry_point_file = "plugin_main.py"
            manifest["entry_point"] = entry_point_file
        else:
            entry_point_file = manifest["entry_point"]

        entry_path = os.path.join(self.plugins_directory, plugin_id, entry_point_file)
        if not os.path.exists(entry_path):
            log.error(f"Entry point '{entry_point_file}' not found for '{plugin_id}'. Skipping.")
            return False
        return True

    def _load_plugin(self, plugin_id, manifest):
        plugin_path = os.path.abspath(os.path.join(self.plugins_directory, plugin_id))
        module_name = f"puffin_plugin_{plugin_id.replace('-', '_')}"
        spec_path = os.path.join(plugin_path, manifest["entry_point"])

        original_sys_path = list(sys.path)
        if plugin_path not in sys.path:
            sys.path.insert(0, plugin_path)

        try:
            spec = importlib.util.spec_from_file_location(module_name, spec_path)
            if not spec or not spec.loader:
                log.error(f"Could not create module spec for plugin: {plugin_id}")
                return

            module = importlib.util.module_from_spec(spec)
            sys.modules[module_name] = module

            spec.loader.exec_module(module)

            if hasattr(module, 'initialize'):
                instance = module.initialize(self.main_window)
                self.loaded_plugins[plugin_id] = {
                    "module": module,
                    "instance": instance,
                    "manifest": manifest
                }
                log.info(f"Successfully initialized plugin: {manifest.get('name', plugin_id)}")
            else:
                log.error(f"Plugin '{plugin_id}' has no 'initialize' function. Skipping.")
        finally:
            sys.path[:] = original_sys_path

    def get_installed_plugins(self) -> list:
        return self.installed_plugins_metadata

    def install_plugin_from_zip(self, zip_filepath: str) -> tuple[bool, str]:
        if not zipfile.is_zipfile(zip_filepath): return False, "Not a valid zip archive."
        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                with zipfile.ZipFile(zip_filepath, 'r') as z:
                    z.extractall(temp_dir)
                items = os.listdir(temp_dir)
                is_nested_folder = len(items) == 1 and os.path.isdir(os.path.join(temp_dir, items[0]))
                src_dir = os.path.join(temp_dir, items[0]) if is_nested_folder else temp_dir
                manifest_path = os.path.join(src_dir, 'plugin.json')
                if not os.path.exists(
                        manifest_path): return False, "Archive does not contain a 'plugin.json' at its root."
                with open(manifest_path, 'r', encoding='utf-8') as f:
                    manifest = json.load(f)
                plugin_id = manifest.get('id', os.path.basename(src_dir).lower().replace(' ', '_'))
                target_path = os.path.join(self.plugins_directory, plugin_id)
                if os.path.exists(target_path): return False, f"A plugin named '{plugin_id}' already exists."
                shutil.move(src_dir, target_path)
                log.info(f"Plugin '{manifest.get('name', plugin_id)}' installed to '{target_path}'")
                return True, f"Plugin '{manifest.get('name', plugin_id)}' installed successfully."
        except Exception as e:
            log.error(f"Failed to install plugin from {zip_filepath}: {e}", exc_info=True)
            return False, f"An unexpected error occurred: {e}"

    def uninstall_plugin(self, plugin_id: str) -> tuple[bool, str]:
        # Check if the plugin is marked as core from its manifest
        plugin_meta = next((p for p in self.installed_plugins_metadata if p.get('id') == plugin_id), None)
        if plugin_meta and plugin_meta.get('is_core'):
            return False, "This is a core plugin and cannot be uninstalled."

        target_path = os.path.join(self.plugins_directory, plugin_id)
        if not os.path.exists(target_path): return False, f"Plugin '{plugin_id}' not found."
        try:
            shutil.rmtree(target_path)
            log.info(f"Successfully uninstalled plugin '{plugin_id}'.")
            return True, f"Plugin '{plugin_id}' uninstalled."
        except OSError as e:
            log.error(f"Failed to uninstall plugin '{plugin_id}': {e}", exc_info=True)
            return False, f"Error removing plugin directory: {e}"
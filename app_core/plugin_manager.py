# PuffinPyEditor/app_core/plugin_manager.py
import os
import sys
import json
import importlib.util
import zipfile
import tempfile
import shutil
from utils.logger import log, get_app_data_path
from utils.helpers import get_base_path


class PluginManager:

    def __init__(self, main_window):
        self.main_window = main_window
        base_app_path = get_base_path()
        app_data_path = get_app_data_path()

        # Built-in plugins are read-only from the installation directory
        self.built_in_plugins_dir = os.path.join(base_app_path, "plugins")
        self.core_tools_directory = os.path.join(base_app_path, "core_debug_tools")
        # User-installed plugins go to the writable app data directory
        self.user_plugins_directory = os.path.join(app_data_path, "plugins")

        log.info(f"Plugin search directories set to: "
                 f"{self.built_in_plugins_dir} (built-in) and "
                 f"{self.user_plugins_directory} (user)")

        self.loaded_plugins = {}
        self.installed_plugins_metadata = []

        # Ensure the user plugins directory exists and is a package
        if not os.path.isdir(self.user_plugins_directory):
            log.info(f"Creating user plugins directory at: "
                     f"{os.path.abspath(self.user_plugins_directory)}")
            os.makedirs(self.user_plugins_directory)

        init_path = os.path.join(self.user_plugins_directory, "__init__.py")
        if not os.path.exists(init_path):
            with open(init_path, 'w', encoding='utf-8') as f:
                pass

    def discover_and_load_plugins(self, ignore_list: list = None):
        """
        Discovers plugins from both built-in and user directories and loads them.

        Args:
            ignore_list: A list of plugin IDs to skip (e.g., if loaded manually).
        """
        if ignore_list is None:
            ignore_list = []

        log.info("Starting plugin discovery...")
        self.installed_plugins_metadata = []
        plugins_to_load = {}

        # Discover from all potential plugin sources
        plugin_sources = {
            "built-in": self.built_in_plugins_dir,
            "core-tool": self.core_tools_directory,
            "user": self.user_plugins_directory,
        }

        for source_type, plugin_dir in plugin_sources.items():
            if not os.path.isdir(plugin_dir):
                log.warning(f"Plugin directory not found: '{plugin_dir}'. Skipping.")
                continue

            for item_name in os.listdir(plugin_dir):
                plugin_path = os.path.join(plugin_dir, item_name)
                if os.path.isdir(plugin_path) and not item_name.startswith('__'):
                    manifest_path = os.path.join(plugin_path, "plugin.json")
                    if os.path.exists(manifest_path):
                        try:
                            with open(manifest_path, 'r', encoding='utf-8') as f:
                                manifest = json.load(f)

                            plugin_id = manifest.get('id', item_name)

                            if plugin_id in ignore_list:
                                log.info(f"Skipping plugin '{plugin_id}' as it's in the ignore list.")
                                continue

                            if plugin_id in plugins_to_load:
                                log.warning(f"Duplicate plugin ID '{plugin_id}'. "
                                            f"User/Core plugin overrides built-in.")

                            manifest['id'] = plugin_id
                            manifest['is_core'] = (source_type != "user")
                            self.installed_plugins_metadata.append(manifest)
                            plugins_to_load[plugin_id] = (manifest, plugin_path)

                        except (json.JSONDecodeError, IOError) as e:
                            log.error(f"Failed to read manifest for "
                                      f"'{item_name}': {e}")

        for plugin_id, (manifest, plugin_path) in plugins_to_load.items():
            try:
                self._load_plugin(plugin_id, manifest, plugin_path)
            except Exception as e:
                log.error(f"Failed to process or load plugin '{plugin_id}': {e}",
                          exc_info=True)

    def _load_plugin(self, plugin_id: str, manifest: dict, plugin_path: str):
        """
        Loads a single plugin from an arbitrary path using importlib.util.
        """
        entry_point = manifest.get("entry_point", "plugin_main.py")
        entry_point_path = os.path.join(plugin_path, entry_point)

        if not os.path.exists(entry_point_path):
            log.error(f"Entry point '{entry_point}' not found for plugin "
                      f"'{plugin_id}'. Skipping.")
            return

        try:
            # Treat the plugin's directory as a package to allow relative imports.
            spec = importlib.util.spec_from_file_location(
                name=plugin_id,
                location=entry_point_path,
                submodule_search_locations=[plugin_path]  # This makes it a package
            )

            if spec is None:
                log.error(f"Could not create module spec for plugin '{plugin_id}' at '{entry_point_path}'")
                return

            module = importlib.util.module_from_spec(spec)
            sys.modules[spec.name] = module  # Use spec.name, which is plugin_id
            spec.loader.exec_module(module)

            if hasattr(module, 'initialize'):
                instance = module.initialize(self.main_window)
                self.loaded_plugins[plugin_id] = {
                    "module": module, "instance": instance, "manifest": manifest
                }
                log.info(f"Successfully initialized plugin: "
                         f"{manifest.get('name', plugin_id)}")
            else:
                log.error(f"Plugin '{plugin_id}' has no 'initialize' function. "
                          f"Skipping.")

        except Exception as e:
            log.error(f"An unexpected error occurred loading plugin '{plugin_id}': "
                      f"{e}", exc_info=True)

    def get_installed_plugins(self) -> list:
        return self.installed_plugins_metadata

    def install_plugin_from_zip(self, zip_filepath: str) -> tuple[bool, str]:
        if not zipfile.is_zipfile(zip_filepath):
            return False, "Not a valid zip archive."
        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                with zipfile.ZipFile(zip_filepath, 'r') as z:
                    z.extractall(temp_dir)
                items = os.listdir(temp_dir)
                is_nested = len(items) == 1 and os.path.isdir(os.path.join(temp_dir, items[0]))
                src_dir = os.path.join(temp_dir, items[0]) if is_nested else temp_dir
                manifest_path = os.path.join(src_dir, 'plugin.json')
                if not os.path.exists(manifest_path):
                    return False, "Archive missing 'plugin.json' at its root."
                with open(manifest_path, 'r', encoding='utf-8') as f:
                    manifest = json.load(f)
                plugin_id = manifest.get('id', os.path.basename(src_dir).lower().replace(' ', '_'))
                target_path = os.path.join(self.user_plugins_directory, plugin_id)
                if os.path.exists(target_path):
                    return False, f"A plugin named '{plugin_id}' already exists."
                shutil.move(src_dir, target_path)
                log.info(f"Plugin '{manifest.get('name', plugin_id)}' installed "
                         f"to '{target_path}'")
                return True, f"Plugin '{manifest.get('name', plugin_id)}' installed."
        except Exception as e:
            log.error(f"Failed to install plugin from {zip_filepath}: {e}",
                      exc_info=True)
            return False, f"An unexpected error occurred: {e}"

    def uninstall_plugin(self, plugin_id: str) -> tuple[bool, str]:
        plugin_meta = next((p for p in self.installed_plugins_metadata
                            if p.get('id') == plugin_id), None)
        if plugin_meta and plugin_meta.get('is_core'):
            return False, "This is a built-in plugin and cannot be uninstalled."

        target_path = os.path.join(self.user_plugins_directory, plugin_id)
        if not os.path.exists(target_path):
            return False, f"Plugin '{plugin_id}' not in the user directory."
        try:
            shutil.rmtree(target_path)
            log.info(f"Successfully uninstalled plugin '{plugin_id}'.")
            return True, f"Plugin '{plugin_id}' uninstalled."
        except OSError as e:
            log.error(f"Failed to uninstall plugin '{plugin_id}': {e}",
                      exc_info=True)
            return False, f"Error removing plugin directory: {e}"
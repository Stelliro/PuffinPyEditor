# PuffinPyEditor/app_core/plugin_manager.py
import os
import sys
import json
import importlib
import importlib.util
import inspect
import zipfile
import tempfile
import shutil
from dataclasses import dataclass, field
from typing import Dict, Any, Optional, Tuple, List
from utils.logger import log, get_app_data_path

# Using packaging is the standard for version comparison.
# If you don't have it, run: pip install packaging
try:
    from packaging.version import Version, InvalidVersion
except ImportError:
    # Basic fallback if 'packaging' is not installed
    log.warning(
        "The 'packaging' library is not installed. Version comparison "
        "will be basic. Run 'pip install packaging'."
    )
    Version = InvalidVersion = None

from utils.helpers import get_base_path


# This assumes your API class is in app_core.
# from app_core.puffin_api import PuffinPluginAPI

# Dummy PluginAPI for demonstration if it's not available
class PuffinPluginAPI:
    def __init__(self, main_window):
        self._main_window = main_window

    def get_main_window(self):
        return self._main_window


@dataclass
class Plugin:
    """A dataclass to hold all information about a plugin."""
    manifest: Dict[str, Any]
    path: str
    source_type: str  # 'built-in', 'core-tool', 'user'
    is_core: bool = field(init=False)
    is_loaded: bool = False
    enabled: bool = True
    module: Optional[Any] = None
    instance: Optional[Any] = None
    status_reason: str = "Not loaded"

    def __post_init__(self):
        self.is_core = self.source_type != "user"

    @property
    def id(self) -> str:
        return self.manifest.get('id', 'unknown')

    @property
    def name(self) -> str:
        return self.manifest.get('name', self.id)

    @property
    def version(self) -> str:
        return self.manifest.get('version', '0.0.0')


class PluginManager:

    def __init__(self, main_window, built_in_dir: Optional[str] = None,
                 user_dir: Optional[str] = None,
                 core_tools_dir: Optional[str] = None):
        """
        Initializes the Plugin Manager.

        Note: Passing main_window is a temporary bridge. In the future, this should
        take a dedicated API object. For now, we'll create the API here.
        """
        # Local import to avoid circular dependency
        from app_core.puffin_api import PuffinPluginAPI
        self.api = PuffinPluginAPI(main_window)
        base_app_path = get_base_path()
        app_data_path = get_app_data_path()

        # Configurable plugin directories with sensible defaults
        self.built_in_plugins_dir = built_in_dir or os.path.join(
            base_app_path, "plugins")
        self.core_tools_directory = core_tools_dir or os.path.join(
            base_app_path, "core_debug_tools")
        self.user_plugins_directory = user_dir or os.path.join(
            app_data_path, "plugins")

        self.plugin_states_file = os.path.join(
            app_data_path, "plugin_states.json")

        self._ensure_paths_and_packages()

        self.plugins: Dict[str, Plugin] = {}  # Store Plugin objects by ID
        log.info("PluginManager initialized.")

    def _ensure_paths_and_packages(self):
        """Ensures all plugin directories exist and are on sys.path."""
        for path in [get_base_path(), self.user_plugins_directory]:
            if path not in sys.path:
                sys.path.insert(0, path)
                log.info(f"Added to sys.path: {path}")

        if not os.path.isdir(self.user_plugins_directory):
            log.info(
                "Creating user plugins directory: "
                f"{self.user_plugins_directory}"
            )
            os.makedirs(self.user_plugins_directory)

        # Make user plugins directory a package
        init_path = os.path.join(self.user_plugins_directory, "__init__.py")
        if not os.path.exists(init_path):
            with open(init_path, 'w', encoding='utf-8') as f:
                f.write("# This file makes the plugins directory a package.\n")

    def discover_and_load_plugins(self,
                                  ignore_list: Optional[List[str]] = None):
        """
        Discovers all plugins, resolves dependencies, and loads enabled ones.

        Args:
            ignore_list: A list of plugin IDs to skip loading (e.g., loaded manually).
        """
        log.info("Starting full plugin discovery and loading process...")
        if ignore_list is None:
            ignore_list = []

        # 1. Discover all available plugins from all sources.
        self._discover_plugins()

        # 2. Load enabled/disabled states from config
        self._load_plugin_states()

        # 3. Resolve dependencies and determine load order
        load_order = self._resolve_dependencies()

        # 4. Load plugins in the correct order
        for plugin_id in load_order:
            plugin = self.plugins.get(plugin_id)

            if plugin_id in ignore_list:
                log.info(
                    f"Skipping plugin '{plugin.name if plugin else plugin_id}' "
                    "as it's in the ignore list.")
                if plugin:
                    plugin.status_reason = "Ignored (pre-loaded)"
                continue

            if plugin and plugin.enabled:
                self.load_plugin(plugin_id)
            elif plugin:
                log.info(
                    f"Plugin '{plugin.name}' is disabled and will not be loaded."
                )

        log.info("Plugin discovery and loading complete.")

    def _discover_plugins(self):
        """Scans directories and populates the self.plugins dictionary."""
        plugin_sources = {
            "built-in": self.built_in_plugins_dir,
            "core-tool": self.core_tools_directory,
            "user": self.user_plugins_directory,
        }

        for source_type, plugin_dir in plugin_sources.items():
            if not os.path.isdir(plugin_dir):
                log.warning(
                    f"Plugin directory not found: '{plugin_dir}'. Skipping.")
                continue

            for item_name in os.listdir(plugin_dir):
                if item_name.startswith(('__', '.')):
                    continue
                plugin_path = os.path.join(plugin_dir, item_name)
                if os.path.isdir(plugin_path):
                    self._process_potential_plugin(plugin_path, source_type)

    def _process_potential_plugin(self, plugin_path: str, source_type: str):
        """Reads a plugin's manifest and adds it to the discovery list."""
        manifest_path = os.path.join(plugin_path, "plugin.json")
        if not os.path.exists(manifest_path):
            return

        try:
            with open(manifest_path, 'r', encoding='utf-8') as f:
                manifest = json.load(f)

            if not self._validate_manifest(manifest, manifest_path):
                return

            plugin_id = manifest['id']

            if plugin_id in self.plugins and source_type == "built-in":
                log.warning(
                    f"Plugin '{plugin_id}' from '{source_type}' is being "
                    "overridden by a user/core version.")
                return

            plugin = Plugin(
                manifest=manifest, path=plugin_path, source_type=source_type)
            self.plugins[plugin_id] = plugin
            log.debug(f"Discovered plugin: '{plugin.name}' (ID: {plugin_id})")

        except (json.JSONDecodeError, IOError) as e:
            log.error(
                f"Failed to read or parse manifest at '{manifest_path}': {e}")

    def _validate_manifest(self, manifest: Dict, path: str) -> bool:
        """Validates that the manifest contains required fields."""
        required_fields = ['id', 'name', 'version']
        for field_name in required_fields:
            if field_name not in manifest or not manifest[field_name]:
                log.error(
                    f"Manifest at {path} is missing required field or "
                    f"it is empty: '{field_name}'. Skipping.")
                return False
        return True

    def _resolve_dependencies(self) -> List[str]:
        """Resolves plugin dependencies and returns a valid load order."""
        log.info("Resolving plugin dependencies...")
        dependencies = {
            pid: set(p.manifest.get('dependencies', {}).keys())
            for pid, p in self.plugins.items()}
        load_order = []
        resolved = set()

        while len(load_order) < len(self.plugins):
            ready_to_load = {
                pid for pid, deps in dependencies.items()
                if pid not in resolved and not deps - resolved
            }

            if not ready_to_load:
                unresolved_deps = {
                    pid: deps - resolved
                    for pid, deps in dependencies.items() if pid not in resolved}
                log.error(
                    "Could not resolve plugin dependencies. Circular dependency"
                    " or missing plugins detected.")
                log.error(f"Unresolved dependencies: {unresolved_deps}")
                for pid in unresolved_deps:
                    if pid in self.plugins:
                        self.plugins[pid].enabled = False
                        self.plugins[pid].status_reason = (
                            f"Dependency error: {unresolved_deps[pid]}"
                        )
                break

            for plugin_id in sorted(list(ready_to_load)):
                plugin = self.plugins[plugin_id]
                deps_manifest = plugin.manifest.get('dependencies', {})

                can_load = True
                for dep_id, req_version_str in deps_manifest.items():
                    if dep_id not in self.plugins:
                        plugin.status_reason = f"Missing dependency: {dep_id}"
                        can_load = False
                        break

                    dep_plugin = self.plugins[dep_id]
                    if not self._check_version(
                            dep_plugin.version, req_version_str):
                        plugin.status_reason = (
                            f"Dependency '{dep_id}' version incompatibility. "
                            f"Have {dep_plugin.version}, need {req_version_str}"
                        )
                        can_load = False
                        break

                if can_load:
                    plugin.status_reason = "Dependencies met"
                    load_order.append(plugin_id)
                else:
                    plugin.enabled = False

                resolved.add(plugin_id)

        log.info(f"Plugin load order determined: {load_order}")
        return load_order

    def _check_version(
            self, installed_version: str, required_version_spec: str) -> bool:
        """Checks if an installed version satisfies a requirement specifier."""
        if Version is None:  # Fallback if 'packaging' is not installed
            return installed_version == required_version_spec

        try:
            installed_v = Version(installed_version)
            spec = required_version_spec.strip()

            if spec.startswith('>='):
                return installed_v >= Version(spec[2:])
            if spec.startswith('<='):
                return installed_v <= Version(spec[2:])
            if spec.startswith('=='):
                return installed_v == Version(spec[2:])
            if spec.startswith('>'):
                return installed_v > Version(spec[1:])
            if spec.startswith('<'):
                return installed_v < Version(spec[1:])
            return installed_v == Version(spec)
        except (InvalidVersion, ValueError) as e:
            log.warning(
                f"Could not parse version. installed='{installed_version}', "
                f"required='{required_version_spec}'. Error: {e}")
            return False

    def load_plugin(self, plugin_id: str) -> bool:
        """Loads a single, already discovered plugin."""
        plugin = self.plugins.get(plugin_id)
        if not plugin:
            log.error(f"Attempted to load non-existent plugin '{plugin_id}'.")
            return False
        if plugin.is_loaded:
            log.warning(f"Plugin '{plugin.name}' is already loaded.")
            return True

        entry_point = plugin.manifest.get("entry_point", "plugin_main.py")
        entry_point_path = os.path.join(plugin.path, entry_point)

        if not os.path.exists(entry_point_path):
            plugin.status_reason = f"Entry point '{entry_point}' not found."
            log.error(f"{plugin.status_reason} for plugin '{plugin.name}'.")
            return False

        entry_module_name = os.path.splitext(entry_point)[0]

        if plugin.source_type == 'user':
            package_name = plugin.id
        else:
            parent_package = os.path.basename(os.path.dirname(plugin.path))
            package_name = f"{parent_package}.{plugin.id}"

        module_name = f"{package_name}.{entry_module_name}"

        try:
            spec = importlib.util.spec_from_file_location(
                module_name, entry_point_path)
            if not spec or not spec.loader:
                raise ImportError(
                    f"Could not create module spec for {module_name}")

            module = importlib.util.module_from_spec(spec)
            sys.modules[module_name] = module
            spec.loader.exec_module(module)

            if hasattr(module, 'initialize'):
                # Smartly pass argument based on signature
                arg_to_pass = self.api
                try:
                    sig = inspect.signature(module.initialize)
                    # Check if the first parameter is NOT 'puffin_api'. This is
                    # our heuristic for identifying a legacy plugin.
                    if sig.parameters:
                        first_param_name = list(sig.parameters.keys())[0]
                        if first_param_name != 'puffin_api':
                            log.warning(
                                f"Plugin '{plugin.name}' has legacy signature "
                                f"(expects '{first_param_name}'). Passing "
                                "MainWindow directly for compatibility."
                            )
                            arg_to_pass = self.api.get_main_window()
                except (ValueError, IndexError) as e:
                    log.warning(
                        f"Could not inspect signature for plugin "
                        f"'{plugin.name}': {e}. Defaulting to passing "
                        f"modern API object.")

                instance = module.initialize(arg_to_pass)
                plugin.module = module
                plugin.instance = instance
                plugin.is_loaded = True
                plugin.status_reason = "Loaded successfully"
                log.info(
                    f"Successfully initialized plugin: '{plugin.name}' "
                    f"(Version: {plugin.version})")
                return True
            else:
                plugin.status_reason = "No 'initialize' function found."
                log.error(
                    f"Plugin '{plugin.name}' has no 'initialize' function. "
                    "Skipping.")
                if module_name in sys.modules:
                    del sys.modules[module_name]
                return False

        except Exception as e:
            plugin.status_reason = f"Load error: {e}"
            log.error(
                f"An unexpected error occurred loading plugin '{plugin.name}': "
                f"{e}", exc_info=True)
            if module_name in sys.modules:
                del sys.modules[module_name]
            return False

    def unload_plugin(self, plugin_id: str) -> bool:
        """Unloads a single plugin, calling its shutdown method if it exists."""
        plugin = self.plugins.get(plugin_id)
        if not plugin or not plugin.is_loaded:
            log.warning(
                f"Attempted to unload plugin '{plugin_id}' which is not loaded."
            )
            return True

        log.info(f"Unloading plugin: '{plugin.name}'")

        try:
            if hasattr(plugin.instance, 'shutdown'):
                plugin.instance.shutdown()

            plugin.is_loaded = False
            plugin.instance = None

            if plugin.module:
                module_name = plugin.module.__name__
                plugin.module = None
                if module_name in sys.modules:
                    del sys.modules[module_name]

                import gc
                gc.collect()

            plugin.status_reason = "Unloaded"
            log.info(f"Successfully unloaded plugin '{plugin.name}'.")
            return True
        except Exception as e:
            plugin.status_reason = f"Unload error: {e}"
            log.error(
                f"Error during shutdown of plugin '{plugin.name}': {e}",
                exc_info=True)
            return False

    def reload_plugin(self, plugin_id: str) -> bool:
        """Reloads a single plugin."""
        log.info(f"Reloading plugin '{plugin_id}'...")
        if self.unload_plugin(plugin_id):
            return self.load_plugin(plugin_id)
        log.error(
            f"Failed to unload plugin '{plugin_id}' during reload process.")
        return False

    def enable_plugin(self, plugin_id: str):
        """Enables a plugin, saves state, and loads it if dependencies are met."""
        plugin = self.plugins.get(plugin_id)
        if not plugin:
            log.error(f"Cannot enable non-existent plugin '{plugin_id}'")
            return

        plugin.enabled = True
        self._save_plugin_states()
        log.info(
            f"Plugin '{plugin.name}' enabled. Re-evaluating and loading "
            "plugins.")
        self.discover_and_load_plugins()

    def disable_plugin(self, plugin_id: str):
        """Disables a plugin, unloads it, and saves the state."""
        plugin = self.plugins.get(plugin_id)
        if not plugin:
            log.error(f"Cannot disable non-existent plugin '{plugin_id}'")
            return

        self.unload_plugin(plugin_id)
        plugin.enabled = False
        self._save_plugin_states()
        log.info(f"Plugin '{plugin.name}' disabled and unloaded.")

    def _load_plugin_states(self):
        """Loads the enabled/disabled state of plugins from a JSON file."""
        if not os.path.exists(self.plugin_states_file):
            return
        try:
            with open(self.plugin_states_file, 'r', encoding='utf-8') as f:
                states = json.load(f)
            for plugin_id, state in states.items():
                if plugin_id in self.plugins and isinstance(state, dict):
                    self.plugins[plugin_id].enabled = state.get('enabled', True)
        except (IOError, json.JSONDecodeError) as e:
            log.warning(
                "Could not load plugin states from "
                f"{self.plugin_states_file}: {e}"
            )

    def _save_plugin_states(self):
        """Saves the current enabled/disabled state of all known plugins."""
        states = {
            pid: {'enabled': p.enabled} for pid, p in self.plugins.items()
        }
        try:
            with open(self.plugin_states_file, 'w', encoding='utf-8') as f:
                json.dump(states, f, indent=4)
        except IOError as e:
            log.error(
                "Could not save plugin states to "
                f"{self.plugin_states_file}: {e}"
            )

    def get_all_plugins(self) -> List[Plugin]:
        """Returns a list of all discovered Plugin objects."""
        return list(self.plugins.values())

    def get_loaded_plugins(self) -> List[Plugin]:
        """Returns a list of currently loaded Plugin objects."""
        return [p for p in self.plugins.values() if p.is_loaded]

    def install_plugin_from_zip(self, zip_filepath: str) -> Tuple[bool, str]:
        """Installs a plugin from a zip file into the user directory."""
        if not zipfile.is_zipfile(zip_filepath):
            return False, "Not a valid zip archive."
        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                with zipfile.ZipFile(zip_filepath, 'r') as z:
                    z.extractall(temp_dir)

                items = os.listdir(temp_dir)
                is_nested = len(items) == 1 and os.path.isdir(
                    os.path.join(temp_dir, items[0]))
                src_dir = os.path.join(temp_dir,
                                       items[0]) if is_nested else temp_dir

                manifest_path = os.path.join(src_dir, 'plugin.json')
                if not os.path.exists(manifest_path):
                    return False, "Archive is missing 'plugin.json'."

                with open(manifest_path, 'r', encoding='utf-8') as f:
                    manifest = json.load(f)

                if not self._validate_manifest(manifest, manifest_path):
                    return False, "Plugin manifest is invalid."

                plugin_id = manifest['id']
                target_path = os.path.join(
                    self.user_plugins_directory, plugin_id)

                if os.path.exists(target_path):
                    return False, f"A plugin with ID '{plugin_id}' already exists."

                shutil.move(src_dir, target_path)
                plugin_name = manifest.get('name', plugin_id)
                log.info(
                    f"Plugin '{plugin_name}' installed. Reloading plugins...")

                self.discover_and_load_plugins()

                return True, f"Plugin '{plugin_name}' installed and loaded."
        except Exception as e:
            log.error(f"Failed to install plugin from {zip_filepath}: {e}",
                      exc_info=True)
            return False, f"An unexpected error occurred: {e}"

    def uninstall_plugin(self, plugin_id: str) -> Tuple[bool, str]:
        """Uninstalls a user plugin."""
        plugin = self.plugins.get(plugin_id)
        if not plugin:
            return False, f"Plugin '{plugin_id}' is not installed."
        if plugin.is_core:
            return False, "This is a built-in plugin and cannot be uninstalled."

        self.unload_plugin(plugin_id)

        target_path = os.path.join(self.user_plugins_directory, plugin_id)
        if not os.path.isdir(target_path):
            return False, f"Plugin directory for '{plugin_id}' not found."

        try:
            shutil.rmtree(target_path)

            if plugin_id in self.plugins:
                del self.plugins[plugin_id]
            self._save_plugin_states()

            log.info(f"Successfully uninstalled plugin '{plugin_id}'.")
            return True, f"Plugin '{plugin_id}' was uninstalled."
        except OSError as e:
            log.error(
                f"Failed to uninstall plugin '{plugin_id}': {e}", exc_info=True)
            return False, f"Error removing plugin directory: {e}"
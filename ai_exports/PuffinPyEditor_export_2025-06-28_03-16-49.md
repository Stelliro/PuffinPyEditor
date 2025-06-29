# Project Export: PuffinPyEditor
## Export Timestamp: 2025-06-28T03:16:49.085318
---

## Golden Rules
1. Only edit and add features, the only features should stay unless asked to be removed, or may be completely redundant.
2. any scripts over 1000 lines, please write in a new response.
3. multiple scripts together exceeding 2000 lines together need to be separated into smaller responses, (example: these scripts have 2340 lines together I'm going to separate it into 2 messages that way i dont lose formatting and dont accidentally remove any features)
4. Do not remove any code that is unrelated to the fix, only remove code if it is being substituted or is not needed anymore.

---

## Project Files

Here is the project context you need to work with.
## File Tree
```
/PuffinPyEditor
 ├── app_core
 │   ├── plugin_api.py
 │   ├── plugin_manager.py
 │   ├── project_manager.py
 │   ├── settings_manager.py
 │   └── theme_manager.py
 ├── plugins
 │   └── source_control_ui
 │       ├── plugin.json
 │       ├── plugin_main.py
 │       └── project_source_control_panel.py
 └── ui
     └── main_window.py

```
## File Contents
### File: `/app_core/plugin_api.py`

#### Linter Issues Found:
```

- L20 (E501) No message available

- L31 (W292) No message available

```


```python
# PuffinPyEditor/app_core/plugin_api.py
from utils.logger import log


class PluginAPI:
    """A dedicated, safe API for plugins to interact with the editor."""

    def __init__(self, main_window):
        self._main_window = main_window
        self.log = log  # Expose the logger safely

    def get_main_window(self):
        """Provides access to the main application window."""
        return self._main_window

    def add_menu_item(self, menu_name: str, item_name: str, callback):
        """Adds a new item to a specified top-level menu."""
        # In a real Qt/Tkinter app, you would find the menu and add the action.
        log.info(f"API: Adding '{item_name}' to menu '{menu_name}'.")
        # self._main_window.menuBar().findChild(QMenu, menu_name).addAction(...)

    def get_current_editor_text(self) -> str:
        """Returns the full text of the currently active editor tab."""
        # return self._main_window.tab_widget.currentWidget().toPlainText()
        log.info("API: Getting current editor text.")
        return "Example text from the current editor."

    def set_current_editor_text(self, text: str):
        """Sets the full text of the currently active editor tab."""
        # self._main_window.tab_widget.currentWidget().setPlainText(text)
        log.info("API: Setting current editor text.")
```

### File: `/app_core/plugin_manager.py`

#### Linter Issues Found:
```

- L79 (E501) No message available

- L130 (E501) No message available

- L151 (E501) No message available

- L161 (E501) No message available

- L246 (E501) No message available

- L248 (E501) No message available

- L275 (E501) No message available

- L400 (E501) No message available

- L407 (E501) No message available

- L411 (E501) No message available

- L453 (E501) No message available

- L487 (E501) No message available

- L546 (E501) No message available

- L567 (E501) No message available

- L586 (E501) No message available

- L587 (W292) No message available

```


```python
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
```

### File: `/app_core/project_manager.py`

#### Linter Issues Found:
```

- L54 (E501) No message available

- L75 (E501) No message available

- L255 (W292) No message available

```


```python
# PuffinPyEditor/app_core/project_manager.py
import os
import datetime
import zipfile
from pathlib import Path
from typing import List, Tuple, Optional, Dict
from .settings_manager import settings_manager
from utils.logger import log


class ProjectManager:
    """Manages the state of open projects and project-wide operations."""

    def __init__(self):
        self._open_projects: List[str] = []
        self._active_project_path: Optional[str] = None
        self._load_session()
        log.info(
            f"ProjectManager initialized with {len(self._open_projects)} "
            "projects."
        )

    def _load_session(self):
        """Loads the list of open projects from the settings."""
        open_projects = settings_manager.get("open_projects", [])
        active_project = settings_manager.get("active_project_path")

        # Ensure all stored project paths are valid directories
        self._open_projects = [
            os.path.normpath(p) for p in open_projects if os.path.isdir(p)
        ]

        if (active_project and
                os.path.normpath(active_project) in self._open_projects):
            self._active_project_path = os.path.normpath(active_project)
        elif self._open_projects:
            self._active_project_path = self._open_projects[0]
        else:
            self._active_project_path = None
        log.info(
            "Loaded project session. Active project: "
            f"{self._active_project_path}"
        )

    def save_session(self):
        """Saves the current list of open projects to the settings."""
        settings_manager.set("open_projects", self._open_projects, False)
        settings_manager.set(
            "active_project_path", self._active_project_path, False
        )
        log.info("Project session saved.")

    def open_project(self, path: str) -> bool:
        """Adds a project to the list of open projects and sets it as active."""
        if not os.path.isdir(path):
            log.error(f"Cannot open project. Path is not a directory: {path}")
            return False

        norm_path = os.path.normpath(path)
        if norm_path not in self._open_projects:
            self._open_projects.append(norm_path)
            log.info(f"Project opened: {norm_path}")
        self.set_active_project(norm_path)
        return True

    def close_project(self, path: str):
        """Closes a project and updates the active project if necessary."""
        norm_path = os.path.normpath(path)
        if norm_path in self._open_projects:
            self._open_projects.remove(norm_path)
            log.info(f"Project closed: {norm_path}")

            # If the closed project was the active one, pick a new active one
            if self.get_active_project_path() == norm_path:
                new_active = self._open_projects[0] if self._open_projects else None
                self.set_active_project(new_active)

    def get_open_projects(self) -> List[str]:
        """Returns the list of currently open project paths."""
        return self._open_projects

    def set_active_project(self, path: Optional[str]):
        """Sets the currently active project."""
        norm_path = os.path.normpath(path) if path else None
        if self._active_project_path != norm_path:
            self._active_project_path = norm_path
            log.info(f"Active project set to: {norm_path}")

    def get_active_project_path(self) -> Optional[str]:
        """Returns the path of the currently active project."""
        return self._active_project_path

    def is_project_open(self) -> bool:
        """Checks if any project is currently active."""
        return self._active_project_path is not None

    def create_project_zip(self, output_zip_path: str) -> bool:
        """
        Creates a zip archive of the active project, ignoring common artifacts.

        Returns:
            True if the zip was created successfully, False otherwise.
        """
        if not self.is_project_open():
            log.error("Cannot create zip. No active project.")
            return False

        project_root = self.get_active_project_path()
        ignore_dirs = {
            '__pycache__', '.git', 'venv', '.venv', 'dist', 'build', 'logs'
        }
        # Explicitly ignore the user settings file for security
        ignore_files = {'.gitignore', 'puffin_editor_settings.json'}

        try:
            with zipfile.ZipFile(
                    output_zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, dirs, files in os.walk(project_root):
                    # Modify dirs in-place to prevent walking into ignored dirs
                    dirs[:] = [d for d in dirs if d not in ignore_dirs]
                    for file in files:
                        if file in ignore_files:
                            continue
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, project_root)
                        zipf.write(file_path, arcname)
            log.info(
                f"Successfully created project archive at {output_zip_path}"
            )
            return True
        except (IOError, OSError, zipfile.BadZipFile) as e:
            log.error(f"Failed to create project zip: {e}", exc_info=True)
            return False

    def _generate_file_tree_from_list(
        self, project_root: str, file_list: List[str]
    ) -> List[str]:
        """Generates a text-based file tree from a specific list of files."""
        tree = {}
        for file_path in file_list:
            relative_path = os.path.relpath(file_path, project_root)
            parts = Path(relative_path).parts
            current_level = tree
            for part in parts:
                if part not in current_level:
                    current_level[part] = {}
                current_level = current_level[part]

        def build_tree_lines(d: dict, prefix: str = "") -> List[str]:
            lines = []
            # Sort entries so directories (which have children) come first
            entries = sorted(
                d.keys(), key=lambda k: (not bool(d[k]), k.lower())
            )
            for i, name in enumerate(entries):
                is_last = (i == len(entries) - 1)
                connector = "└── " if is_last else "├── "
                lines.append(f"{prefix}{connector}{name}")
                if d[name]:  # It's a directory with children
                    new_prefix = prefix + ("    " if is_last else "│   ")
                    lines.extend(build_tree_lines(d[name], new_prefix))
            return lines

        return build_tree_lines(tree)

    def export_project_for_ai(
        self,
        output_filepath: str,
        selected_files: List[str],
        instructions: str,
        guidelines: List[str],
        golden_rules: List[str],
        all_problems: Optional[Dict[str, List[Dict]]] = None
    ) -> Tuple[bool, str]:
        """
        Exports selected project files into a single Markdown file for AI.
        """
        if not self.is_project_open():
            return False, "No project is open."

        project_root = self.get_active_project_path()
        project_name = os.path.basename(project_root)
        output_lines = [
            f"# Project Export: {project_name}",
            f"## Export Timestamp: {datetime.datetime.now().isoformat()}",
            "---",
            "\n## 📝 AI Instructions", "```text",
            instructions or "No specific instructions were provided.", "```",
            "\n## 📜 AI Guidelines & Rules", "```text",
        ]
        guideline_text = "\n".join(
            [f"- {g}" for g in guidelines]
        ) if guidelines else "No specific guidelines were provided."
        output_lines.append(guideline_text)
        output_lines.extend(["```", "---"])

        output_lines.append("\n## ✨ Golden Rules\n```text")
        golden_rules_text = "\n".join(
            [f"{i+1}. {g}" for i, g in enumerate(golden_rules)]
        ) if golden_rules else "No specific golden rules were provided."
        output_lines.append(golden_rules_text)
        output_lines.extend(["```", "---"])

        output_lines.append("\n## 🗂️ File Tree of Included Files:\n```")
        output_lines.append(f"/{project_name}")
        output_lines.extend(
            self._generate_file_tree_from_list(project_root, selected_files)
        )
        output_lines.append("```\n---")
        output_lines.append("\n## 📄 File Contents:\n")

        file_count = 0
        for filepath in sorted(selected_files):
            norm_filepath = os.path.normpath(filepath)
            relative_path = Path(
                filepath).relative_to(project_root).as_posix()
            language = Path(filepath).suffix.lstrip('.') or 'text'
            if language == 'py':
                language = 'python'

            output_lines.append(f"### File: `/{relative_path}`\n")

            if all_problems and norm_filepath in all_problems:
                output_lines.append("#### Linter Issues Found:")
                output_lines.append("```")
                for problem in all_problems[norm_filepath]:
                    output_lines.append(
                        f"- Line {problem['line']}, Col {problem['col']} "
                        f"({problem['code']}): {problem['description']}"
                    )
                output_lines.append("```\n")

            output_lines.append(f"```{language}")
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    output_lines.append(f.read())
                file_count += 1
            except (IOError, UnicodeDecodeError) as e:
                log.warning(
                    "Could not read file during AI export: "
                    f"{filepath}. Error: {e}"
                )
                output_lines.append(f"[Error reading file: {e}]")
            output_lines.append("```\n---")

        try:
            with open(output_filepath, 'w', encoding='utf-8') as f:
                f.write("\n".join(output_lines))
            return True, (
                f"Project exported to {Path(output_filepath).name}. "
                f"Included {file_count} files."
            )
        except IOError as e:
            log.error(f"Failed to write AI export file: {e}", exc_info=True)
            return False, f"Failed to write export file: {e}"
```

### File: `/app_core/settings_manager.py`

#### Linter Issues Found:
```

- L150 (W292) No message available

```


```python
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
    "ai_export_loadouts": {},
    "ai_export_golden_rules": {
        "Default Golden Rules": [
            "Do not remove any code that is unrelated to the fix, only remove "
            "code if it is being substituted or is not needed anymore.",
            "Only edit and add features, the only features should stay unless "
            "asked to be removed, or may be completely redundant.",
            "any scripts over 1000 lines, please write in a new response.",
            "multiple scripts together exceeding 2000 lines together need to "
            "be separated into smaller responses, (example: these scripts "
            "have 2340 lines together I'm going to separate it into 2 "
            "messages that way i dont lose formatting and dont accidentally "
            "remove any features)"
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
                        loaded_settings["github_access_token"] = \
                            loaded_settings.pop("github_pat")
                    else:
                        del loaded_settings["github_pat"]
                    log.info("Migrated old 'github_pat' setting.")

                # Merge loaded settings with defaults to ensure all keys exist
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
```

### File: `/app_core/theme_manager.py`

#### Linter Issues Found:
```

- L124 (E501) No message available

- L435 (W292) No message available

```


```python
# PuffinPyEditor/app_core/theme_manager.py
import os
import json
import base64
import shutil
from typing import Dict, Any, Optional
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QColor

from app_core.settings_manager import settings_manager
from utils.logger import log, get_app_data_path
from utils.helpers import get_base_path

# Correct, valid SVG path data for simple arrow/chevron icons.
SVG_ARROW_PATHS = {
    'up': "M4 10 L8 6 L12 10",
    'down': "M4 6 L8 10 L12 6"
}

# --- Paths for themes ---
APP_BASE_PATH = get_base_path()
APP_DATA_ROOT = get_app_data_path()
CUSTOM_THEMES_FILE_PATH = os.path.join(APP_DATA_ROOT, "custom_themes.json")
DEFAULT_CUSTOM_THEMES_FILE_PATH = os.path.join(
    APP_BASE_PATH, "assets", "themes", "custom_themes.json"
)

BUILT_IN_THEMES = {
    "puffin_dark": {
        "name": "Puffin Dark", "author": "PuffinPy", "type": "dark",
        "is_custom": False,
        "colors": {
            "window.background": "#2f383e",
            "sidebar.background": "#2a3338",
            "editor.background": "#272e33",
            "editor.foreground": "#d3c6aa",
            "editorGutter.background": "#2f383e",
            "editorGutter.foreground": "#5f6c6d",
            "editor.lineHighlightBackground": "#3a4145",
            "editor.matchingBracketBackground": "#545e62",
            "editor.matchingBracketForeground": "#d3c6aa",
            "menu.background": "#3a4145",
            "menu.foreground": "#d3c6aa",
            "statusbar.background": "#282f34",
            "statusbar.foreground": "#d3c6aa",
            "tab.activeBackground": "#272e33",
            "tab.inactiveBackground": "#2f383e",
            "tab.activeForeground": "#d3c6aa",
            "tab.inactiveForeground": "#5f6c6d",
            "button.background": "#424d53",
            "button.foreground": "#d3c6aa",
            "input.background": "#3a4145",
            "input.foreground": "#d3c6aa",
            "input.border": "#5f6c6d",
            "scrollbar.background": "#2f383e",
            "scrollbar.handle": "#424d53",
            "scrollbar.handleHover": "#545e62",
            "scrollbar.handlePressed": "#545e62",
            "accent": "#83c092",
            "syntax.keyword": "#e67e80",
            "syntax.operator": "#d3c6aa",
            "syntax.brace": "#d3c6aa",
            "syntax.decorator": "#dbbc7f",
            "syntax.self": "#e67e80",
            "syntax.className": "#dbbc7f",
            "syntax.functionName": "#83c092",
            "syntax.comment": "#5f6c6d",
            "syntax.string": "#a7c080",
            "syntax.docstring": "#5f6c6d",
            "syntax.number": "#d699b6"
        }
    },
    "puffin_light": {
        "name": "Puffin Light", "author": "PuffinPy", "type": "light",
        "is_custom": False,
        "colors": {
            "window.background": "#f5f5f5",
            "sidebar.background": "#ECECEC",
            "editor.background": "#ffffff",
            "editor.foreground": "#000000",
            "editorGutter.background": "#f5f5f5",
            "editorGutter.foreground": "#505050",
            "editor.lineHighlightBackground": "#e0e8f0",
            "editor.matchingBracketBackground": "#c0c8d0",
            "editor.matchingBracketForeground": "#000000",
            "menu.background": "#e0e0e0",
            "menu.foreground": "#000000",
            "statusbar.background": "#007acc",
            "statusbar.foreground": "#ffffff",
            "tab.activeBackground": "#ffffff",
            "tab.inactiveBackground": "#f5f5f5",
            "tab.activeForeground": "#000000",
            "tab.inactiveForeground": "#555555",
            "button.background": "#E0E0E0",
            "button.foreground": "#000000",
            "input.background": "#ffffff",
            "input.foreground": "#000000",
            "input.border": "#D0D0D0",
            "scrollbar.background": "#f0f0f0",
            "scrollbar.handle": "#cccccc",
            "scrollbar.handleHover": "#bbbbbb",
            "scrollbar.handlePressed": "#aaaaaa",
            "accent": "#007ACC",
            "syntax.keyword": "#0000ff",
            "syntax.operator": "#000000",
            "syntax.brace": "#a00050",
            "syntax.decorator": "#267f99",
            "syntax.self": "#800080",
            "syntax.className": "#267f99",
            "syntax.functionName": "#795e26",
            "syntax.comment": "#008000",
            "syntax.string": "#a31515",
            "syntax.docstring": "#a31515",
            "syntax.number": "#098658"
        }
    }
}


def get_arrow_svg_uri(direction: str, color: str) -> str:
    """Builds a robust, dependency-free SVG data URI for an arrow icon."""
    path_data = SVG_ARROW_PATHS.get(direction, "")
    if not path_data:
        log.warning(f"Invalid arrow direction '{direction}' requested for SVG.")
        return ""

    # Correctly generates a fill-based solid arrow icon for consistency.
    svg_content = (
        '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" '
        'viewBox="0 0 16 16">'
        f'<path fill="{color}" d="{path_data}" />'
        '</svg>'
    )
    b64_content = base64.b64encode(svg_content.encode('utf-8')).decode('utf-8')
    return f"data:image/svg+xml;base64,{b64_content}"


class ThemeManager:
    """Manages loading, applying, and customizing UI themes."""

    def __init__(self):
        self.all_themes_data: Dict[str, Dict] = {}
        self.current_theme_id: str = "puffin_dark"
        self.current_theme_data: Dict[str, Any] = {}
        self.reload_themes()
        log.info(
            f"ThemeManager initialized. Current theme: "
            f"'{self.current_theme_id}'"
        )

    def reload_themes(self):
        """Loads built-in and custom themes from disk."""
        self.all_themes_data = self._load_all_themes()
        last_theme_id = settings_manager.get("last_theme_id", "puffin_dark")

        if last_theme_id not in self.all_themes_data:
            log.warning(
                f"Last used theme '{last_theme_id}' not found. Reverting."
            )
            last_theme_id = "puffin_dark"
            settings_manager.set("last_theme_id", last_theme_id)

        self.current_theme_id = last_theme_id
        self.current_theme_data = self.all_themes_data.get(
            self.current_theme_id, {})

    def _load_all_themes(self) -> Dict[str, Dict]:
        """
        Loads themes from the built-in dictionary and the user's custom file.
        """
        all_themes = BUILT_IN_THEMES.copy()

        if not os.path.exists(CUSTOM_THEMES_FILE_PATH):
            log.info(
                f"User custom themes file not found at "
                f"{CUSTOM_THEMES_FILE_PATH}."
            )
            if os.path.exists(DEFAULT_CUSTOM_THEMES_FILE_PATH):
                try:
                    log.info("Copying default custom themes to user data dir.")
                    os.makedirs(os.path.dirname(CUSTOM_THEMES_FILE_PATH),
                                exist_ok=True)
                    shutil.copy2(DEFAULT_CUSTOM_THEMES_FILE_PATH,
                                 CUSTOM_THEMES_FILE_PATH)
                except Exception as e:
                    log.error(f"Failed to copy default custom themes: {e}")

        if os.path.exists(CUSTOM_THEMES_FILE_PATH):
            try:
                with open(CUSTOM_THEMES_FILE_PATH, 'r', encoding='utf-8') as f:
                    custom_themes_data = json.load(f)
                    for theme_data in custom_themes_data.values():
                        theme_data['is_custom'] = True
                    all_themes.update(custom_themes_data)
            except Exception as e:
                log.error(f"Error loading user custom themes: {e}")

        return all_themes

    def _save_custom_themes(self):
        """Saves only the themes marked as custom to the user-writable file."""
        custom_themes = {
            theme_id: data for theme_id, data in self.all_themes_data.items()
            if data.get("is_custom")
        }
        temp_file = CUSTOM_THEMES_FILE_PATH + ".tmp"
        try:
            os.makedirs(
                os.path.dirname(CUSTOM_THEMES_FILE_PATH), exist_ok=True)
            with open(temp_file, 'w', encoding='utf-8') as f:
                json.dump(custom_themes, f, indent=4)
            os.replace(temp_file, CUSTOM_THEMES_FILE_PATH)
            log.info("Custom themes saved successfully.")
        except IOError as e:
            log.error(f"Failed to save custom themes: {e}", exc_info=True)

    def add_or_update_custom_theme(self, theme_id: str, theme_data: Dict):
        """Adds or updates a theme, ensuring it's marked as custom."""
        theme_data['is_custom'] = True
        self.all_themes_data[theme_id] = theme_data
        self._save_custom_themes()

    def delete_custom_theme(self, theme_id: str):
        """Deletes a custom theme by its ID."""
        if (theme_id in self.all_themes_data and
                self.all_themes_data[theme_id].get("is_custom")):
            del self.all_themes_data[theme_id]
            self._save_custom_themes()

    def get_available_themes_for_ui(self) -> Dict[str, str]:
        """Returns a dict of {theme_id: theme_name} for UI display."""
        return {
            tid: d.get("name", tid) for tid, d in
            sorted(
                self.all_themes_data.items(),
                key=lambda i: i[1].get("name", i[0]).lower()
            )
        }

    def get_theme_data_by_id(self, theme_id: str) -> Optional[Dict]:
        """Gets the full data for a single theme by its ID."""
        return self.all_themes_data.get(theme_id)

    def set_theme(self, theme_id: str,
                  app_instance: Optional[QApplication] = None):
        """Sets and applies a new theme to the application."""
        if theme_id not in self.all_themes_data:
            log.warning(
                f"Attempted to set non-existent theme '{theme_id}'. Reverting."
            )
            theme_id = "puffin_dark"

        self.current_theme_id = theme_id
        self.current_theme_data = self.all_themes_data.get(theme_id, {})
        settings_manager.set("last_theme_id", theme_id)
        self.apply_theme_to_app(app_instance or QApplication.instance())
        theme_name = self.current_theme_data.get('name', 'Unknown')
        log.info(f"Theme set to '{theme_name}'")

    def apply_theme_to_app(self, app: Optional[QApplication]):
        """Generates and applies the global stylesheet."""
        if not app or not self.current_theme_data:
            return

        colors = self.current_theme_data.get("colors", {})

        def c(key: str, fallback: str) -> str:
            return colors.get(key, fallback)

        def adjust_color(hex_str: str, factor: int) -> str:
            color = QColor(hex_str)
            if factor > 100:
                return color.lighter(factor).name()
            return color.darker(factor).name()

        accent = c('accent', '#83c092')
        win_bg = c('window.background', '#2f383e')
        btn_bg = c('button.background', '#424d53')
        btn_fg = c('button.foreground', '#d3c6aa')
        input_bg = c('input.background', '#3a4145')
        input_fg = c('input.foreground', '#d3c6aa')
        input_border = c('input.border', '#5f6c6d')
        sidebar_bg = c('sidebar.background', '#2a3338')

        combo_arrow_uri = get_arrow_svg_uri('down', color=input_fg)
        spin_up_arrow_uri = get_arrow_svg_uri('up', color=input_fg)
        spin_down_arrow_uri = get_arrow_svg_uri('down', color=input_fg)

        stylesheet = f"""
            QWidget {{
                background-color: {win_bg}; color: {input_fg}; border: none;
            }}
            QMainWindow, QDialog {{ background-color: {win_bg}; }}
            QPushButton {{
                background-color: {btn_bg}; color: {btn_fg};
                border: 1px solid {input_border}; border-radius: 4px;
                padding: 6px 12px; min-width: 80px;
            }}
            QPushButton:hover {{
                background-color: {adjust_color(btn_bg, 115)};
                border-color: {accent};
            }}
            QPushButton:pressed {{
                background-color: {adjust_color(btn_bg, 95)};
            }}
            QPushButton:disabled {{
                background-color: {adjust_color(btn_bg, 105)};
                color: {c('editorGutter.foreground', '#888')};
                border-color: {adjust_color(input_border, 110)};
            }}
            QSplitter::handle {{
                background-color: {sidebar_bg}; width: 1px; image: none;
            }}
            QSplitter::handle:hover {{ background-color: {accent}; }}
            QMenuBar {{
                background-color: {adjust_color(win_bg, 105)};
                border-bottom: 1px solid {input_border};
            }}
            QMenuBar::item {{ padding: 6px 12px; }}
            QMenuBar::item:selected {{
                background-color: {accent};
                color: {c('button.foreground', '#000')};
            }}
            QMenu {{
                background-color: {c('menu.background', '#3a4145')};
                border: 1px solid {input_border}; padding: 4px;
            }}
            QMenu::item {{ padding: 6px 24px; }}
            QMenu::item:selected {{
                background-color: {accent};
                color: {c('button.foreground', '#000')};
            }}
            QTabWidget::pane {{ border: none; }}
            QTabBar::tab {{
                background: transparent;
                color: {c('tab.inactiveForeground', '#5f6c6d')};
                padding: 8px 15px; border: none;
                border-bottom: 2px solid transparent;
            }}
            QTabBar::tab:hover {{ background: {adjust_color(win_bg, 110)}; }}
            QTabBar::tab:selected {{
                color: {c('tab.activeForeground', '#d3c6aa')};
                border-bottom: 2px solid {accent};
            }}
            QToolButton {{
                background: transparent; border: none;
                border-radius: 4px; padding: 4px;
            }}
            QToolButton:hover {{
                background-color: {adjust_color(btn_bg, 120)};
            }}
            QAbstractItemView {{
                background-color: {sidebar_bg}; outline: 0;
            }}
            QTreeView, QListWidget, QTableWidget, QTreeWidget {{
                alternate-background-color: {adjust_color(sidebar_bg, 103)};
            }}
            QTreeView::item:hover, QListWidget::item:hover {{
                background-color: {adjust_color(sidebar_bg, 120)};
            }}
            QTreeView::item:selected, QListWidget::item:selected {{
                background-color: {accent};
                color: {c('button.foreground', '#000')};
            }}
            QHeaderView::section {{
                background-color: {adjust_color(sidebar_bg, 110)};
                padding: 4px; border: 1px solid {win_bg};
            }}
            QDockWidget::title {{
                background-color: {adjust_color(win_bg, 105)};
                text-align: left; padding: 5px;
                border-bottom: 1px solid {input_border};
            }}
            QLineEdit, QTextEdit, QPlainTextEdit, QAbstractSpinBox,
            QComboBox {{
                background-color: {input_bg};
                border: 1px solid {input_border};
                border-radius: 4px; padding: 5px;
            }}
            QLineEdit:focus, QAbstractSpinBox:focus, QComboBox:focus,
            QTextEdit:focus, QPlainTextEdit:focus {{
                border: 1px solid {accent};
            }}
            QComboBox::drop-down {{
                subcontrol-origin: padding; subcontrol-position: top right;
                width: 20px; border-left: 1px solid {input_border};
            }}
            QComboBox::down-arrow {{
                image: url({combo_arrow_uri});
                width: 8px; height: 8px;
            }}
            QSpinBox {{ padding-right: 22px; }}
            QSpinBox::up-button, QSpinBox::down-button {{
                subcontrol-origin: border; width: 22px;
                background-color: transparent;
                border-left: 1px solid {input_border};
            }}
            QSpinBox::up-button:hover, QSpinBox::down-button:hover {{
                background-color: {adjust_color(input_bg, 120)};
            }}
            QSpinBox::up-button {{ subcontrol-position: top right; }}
            QSpinBox::down-button {{ subcontrol-position: bottom right; }}
            QSpinBox::up-arrow {{
                image: url({spin_up_arrow_uri}); width: 8px; height: 8px;
            }}
            QSpinBox::down-arrow {{
                image: url({spin_down_arrow_uri}); width: 8px; height: 8px;
            }}
            QStatusBar {{
                background-color: {c('statusbar.background', '#282f34')};
                border-top: 1px solid {input_border};
                color: {c('statusbar.foreground', '#d3c6aa')};
            }}
            QScrollBar:vertical {{ width: 10px; }}
            QScrollBar:horizontal {{ height: 10px; }}
            QScrollBar::handle {{
                background: {c('scrollbar.handle', '#424d53')};
                border-radius: 5px; min-height: 20px;
            }}
            QScrollBar::handle:hover {{
                background: {c('scrollbar.handleHover', '#545e62')};
            }}
            QScrollBar::add-line, QScrollBar::sub-line {{
                height: 0px; width: 0px;
            }}
            QScrollBar::add-page, QScrollBar::sub-page {{ background: none; }}
        """
        try:
            app.setStyleSheet(stylesheet)
        except Exception as e:
            log.error(f"Failed to apply stylesheet: {e}", exc_info=True)


# Singleton instance
theme_manager = ThemeManager()
```

### File: `/plugins/source_control_ui/plugin.json`

```json
{
    "id": "source_control_ui",
    "name": "Source Control UI",
    "author": "PuffinPy Team",
    "version": "1.1.1",
    "description": "Provides the 'Source Control' panel to view Git status.",
    "entry_point": "plugin_main.py"
}
```

### File: `/plugins/source_control_ui/plugin_main.py`

#### Linter Issues Found:
```

- L5 (E302) No message available

- L23 (E501) No message available

- L24 (E501) No message available

- L25 (E501) No message available

- L33 (W292) No message available

```


```python
# PuffinPyEditor/plugins/source_control_ui/plugin_main.py
from PyQt6.QtCore import Qt
from .project_source_control_panel import ProjectSourceControlPanel

class SourceControlUIPlugin:
    def __init__(self, main_window):
        self.api = main_window.puffin_api
        project_manager = self.api.get_manager("project")
        git_manager = self.api.get_manager("git")
        self.source_control_panel = ProjectSourceControlPanel(
            project_manager, git_manager, main_window)
        self._setup_ui()
        self._connect_signals()

    def _setup_ui(self):
        self.api.register_dock_panel(
            self.source_control_panel, "Source Control",
            Qt.DockWidgetArea.BottomDockWidgetArea, "fa5b.git-alt"
        )

    def _connect_signals(self):
        main_window = self.api.get_main_window()
        # Refresh the panel when the active project changes or a git operation succeeds
        main_window.project_tabs.currentChanged.connect(self.source_control_panel.refresh_all_projects)
        main_window.theme_changed_signal.connect(self.source_control_panel.update_icons)
        self.api.get_manager("git").git_success.connect(
            self.source_control_panel.refresh_all_projects)
        self.api.get_manager("github").operation_success.connect(
            self.source_control_panel.refresh_all_projects)


def initialize(main_window):
    return SourceControlUIPlugin(main_window)
```

### File: `/plugins/source_control_ui/project_source_control_panel.py`

#### Linter Issues Found:
```

- L5 (E501) No message available

- L6 (E501) No message available

- L52 (E501) No message available

- L66 (E501) No message available

- L79 (E501) No message available

- L121 (E501) No message available

- L124 (E501) No message available

- L129 (E501) No message available

- L135 (E501) No message available

- L164 (E501) No message available

- L165 (E501) No message available

- L170 (E501) No message available

- L176 (E501) No message available

- L177 (E501) No message available

- L179 (E501) No message available

- L180 (E501) No message available

- L189 (E501) No message available

- L198 (E501) No message available

- L214 (E501) No message available

- L215 (E501) No message available

- L220 (E501) No message available

- L221 (E501) No message available

- L222 (E501) No message available

- L228 (E501) No message available

- L232 (W292) No message available

```


```python
# PuffinPyEditor/plugins/source_control_ui/project_source_control_panel.py
import os
from typing import List, Dict, Optional
from git import Repo, InvalidGitRepositoryError
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTreeWidget,
                             QTreeWidgetItem, QMenu, QMessageBox, QLabel, QHeaderView, QLineEdit)
from PyQt6.QtGui import QColor
from PyQt6.QtCore import Qt, pyqtSignal, QPoint
import qtawesome as qta

from app_core.project_manager import ProjectManager
from app_core.source_control_manager import SourceControlManager


class ProjectSourceControlPanel(QWidget):
    """
    A widget that displays the Git status for all open projects and provides
    controls for common Git operations.
    """
    publish_repo_requested = pyqtSignal(str)
    create_release_requested = pyqtSignal(str)
    link_to_remote_requested = pyqtSignal(str)
    change_visibility_requested = pyqtSignal(str)

    def __init__(self, project_manager: ProjectManager,
                 git_manager: SourceControlManager, parent=None):
        super().__init__(parent)
        self.project_manager = project_manager
        self.git_manager = git_manager
        self.staged_color = QColor("#A7C080")
        self.unstaged_color = QColor("#DBBC7F")
        self._setup_ui()
        self._connect_signals()
        self.update_icons()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        toolbar_layout = QHBoxLayout()
        self.refresh_all_button = QPushButton("Refresh")
        self.pull_button = QPushButton("Pull")
        self.push_button = QPushButton("Push")
        self.new_release_button = QPushButton("New Release...")
        toolbar_layout.addWidget(self.refresh_all_button)
        toolbar_layout.addWidget(self.pull_button)
        toolbar_layout.addWidget(self.push_button)
        toolbar_layout.addStretch()
        toolbar_layout.addWidget(self.new_release_button)
        layout.addLayout(toolbar_layout)
        self.project_tree = QTreeWidget()
        self.project_tree.setHeaderLabels(["Project / Changes", ""])
        self.project_tree.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        header = self.project_tree.header()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        layout.addWidget(self.project_tree)
        self.commit_message_edit = QLineEdit()
        self.commit_message_edit.setPlaceholderText("Commit message...")
        self.commit_button = QPushButton("Commit All")
        commit_layout = QHBoxLayout()
        commit_layout.addWidget(self.commit_message_edit)
        commit_layout.addWidget(self.commit_button)
        layout.addLayout(commit_layout)
        self.status_label = QLabel("Ready.")
        layout.addWidget(self.status_label)
        self.action_buttons = [self.refresh_all_button, self.pull_button, self.push_button,
                               self.new_release_button, self.commit_button]

    def _connect_signals(self):
        self.git_manager.summaries_ready.connect(self._populate_tree)
        self.git_manager.status_updated.connect(self._update_project_files)
        self.git_manager.git_error.connect(self._handle_git_error)
        self.git_manager.git_success.connect(self._handle_git_success)
        self.refresh_all_button.clicked.connect(self.refresh_all_projects)
        self.push_button.clicked.connect(self._on_push_clicked)
        self.pull_button.clicked.connect(self._on_pull_clicked)
        self.new_release_button.clicked.connect(self._on_new_release_clicked)
        self.commit_button.clicked.connect(self._on_commit_clicked)
        self.project_tree.customContextMenuRequested.connect(self._show_context_menu)

    def set_ui_locked(self, locked: bool, message: str = ""):
        for button in self.action_buttons:
            button.setEnabled(not locked)
        self.commit_message_edit.setEnabled(not locked)
        self.status_label.setText(message)

    def update_icons(self):
        self.refresh_all_button.setIcon(qta.icon('fa5s.sync-alt'))
        self.pull_button.setIcon(qta.icon('fa5s.arrow-down'))
        self.push_button.setIcon(qta.icon('fa5s.arrow-up'))
        self.new_release_button.setIcon(qta.icon('fa5s.tag'))
        self.commit_button.setIcon(qta.icon('fa5s.check'))

    def _get_selected_project_path(self) -> Optional[str]:
        item = self.project_tree.currentItem()
        if not item:
            return self.project_manager.get_active_project_path()
        while parent := item.parent():
            item = parent
        data = item.data(0, Qt.ItemDataRole.UserRole)
        return data.get('path') if data else None

    def _on_push_clicked(self):
        if path := self._get_selected_project_path():
            self.set_ui_locked(True, f"Pushing {os.path.basename(path)}...")
            self.git_manager.push(path)

    def _on_pull_clicked(self):
        if path := self._get_selected_project_path():
            self.set_ui_locked(True, f"Pulling {os.path.basename(path)}...")
            self.git_manager.pull(path)

    def _on_new_release_clicked(self):
        if path := self._get_selected_project_path():
            self.create_release_requested.emit(path)

    def _on_commit_clicked(self):
        path = self._get_selected_project_path()
        message = self.commit_message_edit.text().strip()
        if not path or not message:
            QMessageBox.warning(self, "Commit Failed", "A project must be selected "
                                "and a commit message must be provided.")
            return
        self.set_ui_locked(True, f"Committing changes in {os.path.basename(path)}...")
        self.git_manager.commit_files(path, message)

    def _on_fix_branch_mismatch_clicked(self, path: str):
        reply = QMessageBox.warning(
            self, "Confirm Branch Fix", "This will perform a force-push and delete "
            "the 'master' branch from the remote. Are you sure?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.Cancel,
            QMessageBox.StandardButton.Cancel
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.set_ui_locked(True, f"Fixing branch mismatch for {os.path.basename(path)}...")
            self.git_manager.fix_branch_mismatch(path)

    def _handle_git_success(self, message: str, data: dict):
        self.set_ui_locked(False, f"Success: {message}")
        self.refresh_all_projects()
        if "committed" in message.lower() and not data.get('no_changes'):
            self.commit_message_edit.clear()

    def _handle_git_error(self, error_message: str):
        self.set_ui_locked(False, f"Error: {error_message}")
        self.refresh_all_projects()

    def refresh_all_projects(self):
        self.set_ui_locked(True, "Fetching project statuses...")
        all_projects = self.project_manager.get_open_projects()
        if all_projects:
            self.git_manager.get_summaries(all_projects)
        else:
            self.project_tree.clear()
            self.set_ui_locked(False, "No projects open.")

    def _populate_tree(self, summaries: Dict[str, Dict]):
        self.project_tree.clear()
        git_project_paths = summaries.keys()
        for path in self.project_manager.get_open_projects():
            project_name = os.path.basename(path)
            if path in git_project_paths:
                summary = summaries[path]
                item = QTreeWidgetItem(self.project_tree, [project_name, f"Branch: {summary.get('branch', 'N/A')}"])
                item.setData(0, Qt.ItemDataRole.UserRole, {'type': 'project', 'path': path})
                item.setIcon(0, qta.icon('fa5b.git-alt'))
                self.git_manager.get_status(path)
            else:
                item = QTreeWidgetItem(self.project_tree, [project_name])
                item.setData(0, Qt.ItemDataRole.UserRole, {'type': 'non-git-project', 'path': path})
                item.setIcon(0, qta.icon('fa5.folder', color='gray'))
                actions_widget = QWidget()
                actions_layout = QHBoxLayout(actions_widget)
                actions_layout.setContentsMargins(0, 0, 0, 0)
                link_button = QPushButton("Link...")
                link_button.setToolTip("Link this local folder to an existing GitHub repository")
                link_button.clicked.connect(lambda _, p=path: self.link_to_remote_requested.emit(p))
                publish_button = QPushButton("Publish...")
                publish_button.setToolTip("Create a new repository on GitHub from this project")
                publish_button.clicked.connect(lambda _, p=path: self.publish_repo_requested.emit(p))
                actions_layout.addStretch()
                actions_layout.addWidget(link_button)
                actions_layout.addWidget(publish_button)
                self.project_tree.setItemWidget(item, 1, actions_widget)
        self.set_ui_locked(False, "Ready.")
        if self.project_tree.topLevelItemCount() > 0:
            self.project_tree.setCurrentItem(self.project_tree.topLevelItem(0))

    def _update_project_files(self, staged: List[str], unstaged: List[str], repo_path: str):
        root = self.project_tree.invisibleRootItem()
        for i in range(root.childCount()):
            project_item = root.child(i)
            item_data = project_item.data(0, Qt.ItemDataRole.UserRole)
            if item_data and item_data.get('path') == repo_path:
                project_item.takeChildren()
                for f in sorted(list(set(staged + unstaged))):
                    child = QTreeWidgetItem(project_item, [f])
                    child.setForeground(0, self.staged_color if f in staged else self.unstaged_color)
                project_item.setExpanded(True)
                break

    def _show_context_menu(self, position: QPoint):
        item = self.project_tree.itemAt(position)
        if not item:
            return
        data = item.data(0, Qt.ItemDataRole.UserRole)
        if not (data and (path := data.get('path'))):
            return

        menu = QMenu()
        if data['type'] == 'project':
            menu.addAction(qta.icon('fa5s.sync-alt'), "Refresh Status",
                           lambda: self.git_manager.get_status(path))
            vis_action = menu.addAction(qta.icon('fa5s.eye'), "Change GitHub Visibility...")
            vis_action.triggered.connect(lambda: self.change_visibility_requested.emit(path))
            try:
                branches = [b.name for b in Repo(path).branches]
                if 'main' in branches and 'master' in branches:
                    menu.addSeparator()
                    fix_action = menu.addAction(qta.icon('fa5s.exclamation-triangle',
                                                         color='orange'), "Fix Branch Mismatch...")
                    fix_action.triggered.connect(lambda: self._on_fix_branch_mismatch_clicked(path))
            except (InvalidGitRepositoryError, TypeError):
                pass
        elif data['type'] == 'non-git-project':
            menu.addAction(qta.icon('fa5s.link'), "Link to GitHub Repo...",
                           lambda: self.link_to_remote_requested.emit(path))
            menu.addAction(qta.icon('fa5s.cloud-upload-alt'), "Publish to GitHub...",
                           lambda: self.publish_repo_requested.emit(path))

        if menu.actions():
            menu.exec(self.project_tree.viewport().mapToGlobal(position))
```

### File: `/ui/main_window.py`

#### Linter Issues Found:
```

- L9 (E501) No message available

- L71 (E501) No message available

- L101 (E501) No message available

- L104 (E501) No message available

- L122 (E261) No message available

- L122 (E501) No message available

- L176 (E501) No message available

- L178 (E501) No message available

- L180 (E501) No message available

- L182 (E501) No message available

- L184 (E501) No message available

- L186 (E501) No message available

- L286 (E501) No message available

- L288 (E501) No message available

- L292 (E501) No message available

- L332 (E501) No message available

- L335 (E501) No message available

- L352 (E501) No message available

- L371 (E501) No message available

- L375 (E501) No message available

- L388 (E501) No message available

- L430 (E501) No message available

- L432 (E501) No message available

- L433 (E501) No message available

- L434 (E501) No message available

- L435 (E501) No message available

- L438 (E501) No message available

- L439 (E501) No message available

- L454 (W293) No message available

- L475 (E701) No message available

- L475 (E261) No message available

- L476 (W293) No message available

- L488 (W293) No message available

- L490 (E501) No message available

- L547 (E501) No message available

- L549 (E501) No message available

- L578 (E501) No message available

- L585 (E501) No message available

- L602 (E501) No message available

- L606 (E501) No message available

- L620 (E501) No message available

- L630 (E501) No message available

- L638 (E501) No message available

- L644 (E111) No message available

- L644 (E117) No message available

- L647 (E501) No message available

- L655 (E501) No message available

- L658 (E701) No message available

- L663 (W293) No message available

- L664 (E501) No message available

- L670 (E111) No message available

- L670 (E117) No message available

- L670 (E501) No message available

- L672 (E111) No message available

- L672 (E117) No message available

- L682 (E701) No message available

- L684 (E501) No message available

- L685 (E701) No message available

- L687 (W293) No message available

- L690 (W293) No message available

- L693 (E111) No message available

- L693 (E117) No message available

- L694 (W293) No message available

- L695 (E501) No message available

- L696 (E701) No message available

- L697 (W293) No message available

- L714 (E501) No message available

- L716 (W293) No message available

- L720 (E501) No message available

- L733 (W293) No message available

- L735 (E111) No message available

- L735 (E117) No message available

- L736 (E111) No message available

- L736 (E117) No message available

- L771 (E111) No message available

- L771 (E117) No message available

- L785 (W291) No message available

- L789 (W291) No message available

- L791 (E111) No message available

- L791 (E117) No message available

- L805 (E501) No message available

- L808 (E111) No message available

- L808 (E117) No message available

- L810 (E111) No message available

- L810 (E117) No message available

- L811 (W293) No message available

- L818 (W293) No message available

- L821 (E501) No message available

- L829 (W292) No message available

```


```python
# PuffinPyEditor/ui/main_window.py
import os
import sys
from typing import Optional, Callable
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QStatusBar, QSplitter, QTabWidget, QMessageBox,
                             QApplication, QFileDialog, QLabel, QToolButton,
                             QToolBar, QSizePolicy, QMenu)
from PyQt6.QtGui import QAction, QKeySequence, QColor, QKeyEvent, QActionGroup, \
    QDesktopServices, QCloseEvent
from PyQt6.QtCore import Qt, QSize, QTimer, pyqtSignal, QUrl

import qtawesome as qta

# Core component imports
from utils.logger import log
from utils import versioning
from app_core.settings_manager import settings_manager
from app_core.theme_manager import theme_manager
from app_core.file_handler import FileHandler
from app_core.project_manager import ProjectManager
from app_core.linter_manager import LinterManager
from app_core.plugin_manager import PluginManager
from app_core.completion_manager import CompletionManager
from app_core.update_manager import UpdateManager
from app_core.source_control_manager import SourceControlManager
from app_core.github_manager import GitHubManager
from app_core.puffin_api import PuffinPluginAPI

# UI component imports
from .file_tree_view import FileTreeViewWidget
from .editor_widget import EditorWidget
from .preferences_dialog import PreferencesDialog


class MainWindow(QMainWindow):
    untitled_file_counter = 0
    _is_app_closing = False
    theme_changed_signal = pyqtSignal(str)

    def __init__(self, debug_mode: bool = False):
        super().__init__()
        self.debug_mode = debug_mode
        self.preferences_dialog = None  # To hold the dialog instance
        log.info(
            f"PuffinPyEditor v{versioning.APP_VERSION} starting... "
            f"(Debug: {self.debug_mode})"
        )

        self._initialize_managers()
        self.puffin_api = PuffinPluginAPI(self)
        self.file_open_handlers: dict[str, Callable] = {}
        log.info("Core API initialized.")

        self.setWindowTitle(f"PuffinPyEditor - v{versioning.APP_VERSION}")
        self._load_window_geometry()
        self._create_core_widgets()
        self._create_core_actions()
        self._create_core_menu()
        self._create_toolbar()
        self._create_layout()
        self._create_statusbar()

        # Manually load core debug tool before other plugins if in debug mode
        plugins_to_ignore = []
        if self.debug_mode:
            try:
                from core_debug_tools.enhanced_exceptions.plugin_main \
                    import initialize as init_eh
                self.eh_instance = init_eh(self, sys.excepthook)
                log.info("Core debug tool 'Enhanced Exceptions' loaded manually.")
                plugins_to_ignore.append('enhanced_exceptions')
            except Exception as e:
                log.error(f"Failed to load core exception handler: {e}",
                          exc_info=True)
                QMessageBox.critical(
                    self, "Debug Tools Failed",
                    "Could not initialize core exception handler."
                    f"\n\nError: {e}"
                )

        # Let the plugin manager handle everything else
        self.plugin_manager.discover_and_load_plugins(
            ignore_list=plugins_to_ignore
        )
        self._connect_signals()
        self._apply_theme_and_icons(self.settings.get("last_theme_id"))

        QTimer.singleShot(0, self._post_init_setup)

        log.info("MainWindow __init__ has completed.")

    def _post_init_setup(self):
        log.debug("Running post-initialization setup...")
        self._initialize_project_views()
        self._update_window_title()
        self._update_editor_actions_state()

        if self.debug_mode:
            plugin_obj = next(
                (p for p in self.plugin_manager.get_loaded_plugins() if p.id == 'live_log_viewer'),
                None
            )
            if plugin_obj and plugin_obj.instance and hasattr(plugin_obj.instance, 'launch_on_startup'):
                log.info("Found live_log_viewer plugin, launching on startup.")
                plugin_obj.instance.launch_on_startup()

        log.debug("Post-initialization setup finished.")

    def _initialize_managers(self):
        self.settings = settings_manager
        self.theme_manager = theme_manager
        self.project_manager = ProjectManager()
        self.completion_manager = CompletionManager(self)
        self.github_manager = GitHubManager(self)
        self.git_manager = SourceControlManager(self)
        self.file_handler = FileHandler(self)
        self.linter_manager = LinterManager(self)
        self.update_manager = UpdateManager(self)
        self.plugin_manager = PluginManager(self)
        self.actions: dict[str, QAction] = {}
        self.editor_tabs_data: dict[QWidget, dict] = {} # Now supports more than EditorWidget
        self.lint_timer = QTimer(self)
        self.lint_timer.setSingleShot(True)
        self.lint_timer.setInterval(1500)
        self.auto_save_timer = QTimer(self)
        self.auto_save_timer.setSingleShot(True)

    def _load_window_geometry(self):
        size = self.settings.get("window_size", [1600, 1000])
        pos = self.settings.get("window_position")
        self.resize(QSize(size[0], size[1]))
        if pos:
            self.move(pos[0], pos[1])

    def _create_core_widgets(self):
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.tab_widget = QTabWidget()
        self.project_tabs = QTabWidget()
        for tab_widget, action in [
            (self.tab_widget, self._add_new_tab),
            (self.project_tabs, self._action_open_folder)
        ]:
            button = QToolButton()
            button.setIcon(qta.icon('fa5s.plus'))
            button.setAutoRaise(True)
            button.clicked.connect(action)
            tab_widget.setCornerWidget(button, Qt.Corner.TopRightCorner)
            tab_widget.setDocumentMode(True)
            tab_widget.setTabsClosable(True)
            tab_widget.setMovable(True)
        self.project_sidebar_container = QWidget()
        sb_layout = QVBoxLayout(self.project_sidebar_container)
        sb_layout.setContentsMargins(0, 0, 0, 0)
        sb_layout.addWidget(self.project_tabs)

    def _create_core_actions(self):
        actions_map = {
            "new_file": ("&New File", self._add_new_tab,
                         "Ctrl+N", 'fa5s.file'),
            "open_file": ("&Open File...", self._action_open_file_dialog,
                          "Ctrl+O", 'fa5s.folder-open'),
            "open_folder": ("Open &Folder...", self._action_open_folder,
                            None, None),
            "close_project": ("&Close Project", self._action_close_project,
                              None, None),
            "save": ("&Save", self._action_save_file, "Ctrl+S", 'fa5s.save'),
            "save_as": ("Save &As...", self._action_save_as,
                        "Ctrl+Shift+S", None),
            "save_all": ("Save A&ll", self._action_save_all,
                         "Ctrl+Alt+S", None),
            "preferences": ("&Preferences...", self._action_open_preferences,
                            "Ctrl+,", 'fa5s.cog'),
            "exit": ("E&xit", self.close, "Ctrl+Q", None),
            "undo": ("&Undo", lambda: self.tab_widget.currentWidget().text_area.undo(),
                     QKeySequence.StandardKey.Undo, 'fa5s.undo'),
            "redo": ("&Redo", lambda: self.tab_widget.currentWidget().text_area.redo(),
                     QKeySequence.StandardKey.Redo, 'fa5s.redo'),
            "cut": ("&Cut", lambda: self.tab_widget.currentWidget().text_area.cut(),
                    QKeySequence.StandardKey.Cut, 'fa5s.cut'),
            "copy": ("C&opy", lambda: self.tab_widget.currentWidget().text_area.copy(),
                     QKeySequence.StandardKey.Copy, 'fa5s.copy'),
            "paste": ("&Paste", lambda: self.tab_widget.currentWidget().text_area.paste(),
                      QKeySequence.StandardKey.Paste, 'fa5s.paste'),
            "select_all": ("Select &All", lambda: self.tab_widget.currentWidget().text_area.selectAll(),
                           QKeySequence.StandardKey.SelectAll, None),
        }
        for key, (text, cb, sc, icon) in actions_map.items():
            action = QAction(text, self)
            if icon:
                action.setData(icon)
            action.triggered.connect(cb)
            if sc:
                action.setShortcut(QKeySequence(sc))
            self.actions[key] = action
            if key in ["undo", "redo", "cut", "copy", "paste", "select_all"]:
                action.setEnabled(False)

    def _create_core_menu(self):
        menu_bar = self.menuBar()
        self.file_menu = menu_bar.addMenu("&File")
        self.edit_menu = menu_bar.addMenu("&Edit")
        self.view_menu = menu_bar.addMenu("&View")
        self.tools_menu = menu_bar.addMenu("&Tools")
        self.help_menu = menu_bar.addMenu("&Help")

        # File Menu
        self.file_menu.addActions([self.actions[k] for k in
                                   ["new_file", "open_file"]])
        self.recent_files_menu = self.file_menu.addMenu("Open &Recent")
        self._update_recent_files_menu()
        self.file_menu.addSeparator()
        self.file_menu.addActions([self.actions[k] for k in
                                   ["open_folder", "close_project"]])
        self.file_menu.addSeparator()
        self.file_menu.addActions([self.actions[k] for k in
                                   ["save", "save_as", "save_all"]])
        self.file_menu.addSeparator()
        self.file_menu.addAction(self.actions["preferences"])
        self.file_menu.addSeparator()
        self.file_menu.addAction(self.actions["exit"])

        # Edit Menu
        self.edit_menu.addActions([self.actions[k] for k in ["undo", "redo"]])
        self.edit_menu.addSeparator()
        self.edit_menu.addActions([self.actions[k] for k in
                                   ["cut", "copy", "paste"]])
        self.edit_menu.addSeparator()
        self.edit_menu.addAction(self.actions["select_all"])

        # View Menu
        self.theme_menu = self.view_menu.addMenu("&Themes")

        # Help Menu
        about_action = QAction("About PuffinPyEditor", self,
                               triggered=self._show_about_dialog)
        github_action = QAction("View on GitHub", self,
                                triggered=self._open_github_link)
        self.help_menu.addAction(about_action)
        self.help_menu.addAction(github_action)

    def _create_toolbar(self):
        self.main_toolbar = QToolBar("Main Toolbar")
        self.main_toolbar.setIconSize(QSize(18, 18))
        self.addToolBar(self.main_toolbar)
        self.main_toolbar.addActions([self.actions[k] for k in
                                      ["new_file", "open_file", "save"]])
        self.main_toolbar.addSeparator()
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Policy.Expanding,
                             QSizePolicy.Policy.Preferred)
        self.main_toolbar.addWidget(spacer)
        self.main_toolbar.addAction(self.actions["preferences"])

    def _create_layout(self):
        layout = QHBoxLayout(self.central_widget)
        layout.setContentsMargins(5, 5, 5, 5)
        self.splitter = QSplitter(Qt.Orientation.Horizontal)

        self.right_pane_widget = QWidget()
        self.right_pane_layout = QVBoxLayout(self.right_pane_widget)
        self.right_pane_layout.setContentsMargins(0, 0, 0, 0)
        self.right_pane_layout.setSpacing(0)

        self.right_pane_layout.addWidget(self.tab_widget)

        self.splitter.addWidget(self.project_sidebar_container)
        self.splitter.addWidget(self.right_pane_widget)

        layout.addWidget(self.splitter)
        self.splitter.setSizes(self.settings.get("splitter_sizes", [250, 950]))
        self.splitter.setHandleWidth(5)

    def _create_statusbar(self):
        self.setStatusBar(QStatusBar(self))
        self.cursor_label = QLabel(" Ln 1, Col 1 ")
        self.statusBar().addPermanentWidget(self.cursor_label)

    def _connect_signals(self):
        self.project_tabs.currentChanged.connect(self._on_project_tab_changed)
        self.project_tabs.tabCloseRequested.connect(
            self._action_close_project_by_index
        )
        self.tab_widget.currentChanged.connect(self._on_tab_changed)
        self.tab_widget.tabCloseRequested.connect(self._action_close_tab_by_index)
        self.splitter.splitterMoved.connect(
            lambda: self.settings.set("splitter_sizes", self.splitter.sizes(), False)
        )
        self.auto_save_timer.timeout.connect(self._auto_save_current_tab)
        self.lint_timer.timeout.connect(self._trigger_file_linter)
        self.completion_manager.definition_found.connect(self._goto_definition_result)

    def _apply_theme_and_icons(self, theme_id: str):
        self.theme_manager.set_theme(theme_id, QApplication.instance())
        self.theme_changed_signal.emit(theme_id)
        accent_color = self.theme_manager.current_theme_data['colors'].get(
            'accent', 'silver'
        )
        icon_color = ("#000000" if QColor(accent_color).lightnessF() > 0.6
                      else "#FFFFFF")
        qta.set_defaults(color=accent_color, color_active=icon_color)

        actions_with_icons = list(self.actions.values())
        for menu in self.menuBar().findChildren(QMenu):
            actions_with_icons.extend(menu.actions())
        for action in self.main_toolbar.actions():
            if action not in actions_with_icons:
                actions_with_icons.append(action)

        for action in actions_with_icons:
            icon_name = action.data()
            is_fontawesome = (isinstance(icon_name, str) and
                              (icon_name.startswith('fa.') or
                               icon_name.startswith('fa5.')))
            if is_fontawesome:
                action.setIcon(qta.icon(icon_name))

        self._rebuild_theme_menu()
        for i in range(self.tab_widget.count()):
            widget = self.tab_widget.widget(i)
            # Handle standard editors and custom widgets with an update method
            if isinstance(widget, EditorWidget):
                widget.highlighter.rehighlight_document()
            elif hasattr(widget, 'update_theme'):
                widget.update_theme()

    def _rebuild_theme_menu(self):
        self.theme_menu.clear()
        group = QActionGroup(self)
        group.setExclusive(True)
        for theme_id, name in self.theme_manager.get_available_themes_for_ui().items():
            action = QAction(
                name, self, checkable=True,
                triggered=lambda _, t_id=theme_id: self._on_theme_selected(t_id)
            )
            action.setData(theme_id)
            action.setChecked(theme_id == self.theme_manager.current_theme_id)
            group.addAction(action)
            self.theme_menu.addAction(action)

    def _initialize_project_views(self):
        log.debug("Initializing project views...")
        active_project = self.project_manager.get_active_project_path()
        self.project_tabs.blockSignals(True)
        self.project_tabs.clear()
        open_projects = self.project_manager.get_open_projects()
        self.project_sidebar_container.setVisible(len(open_projects) > 0)
        active_index = 0
        for i, path in enumerate(open_projects):
            # Pass theme manager to the tree view
            tree = FileTreeViewWidget(self.file_handler, self.theme_manager, self)
            tree.file_open_requested.connect(self._action_open_file)
            tree.file_to_open_created.connect(self._add_new_tab)
            # Connect tree to theme changes
            self.theme_changed_signal.connect(tree.update_theme)
            tree.set_project_root(path)
            tab_index = self.project_tabs.addTab(tree, os.path.basename(path))
            self.project_tabs.setTabToolTip(tab_index, path)
            if path == active_project:
                active_index = i
        self.project_tabs.setCurrentIndex(active_index)
        self.project_tabs.blockSignals(False)
        self._on_project_tab_changed(active_index if open_projects else -1)
        if self.tab_widget.count() == 0:
            self._add_new_tab(is_placeholder=True)
        log.debug("Project views initialized.")

    def _add_new_tab(self, filepath: Optional[str] = None,
                     content: str = "", is_placeholder: bool = False):
        if self.tab_widget.count() == 1 and isinstance(self.tab_widget.widget(0), QLabel):
            self.tab_widget.removeTab(0)

        if is_placeholder:
            placeholder = QLabel("\n\n\tOpen a file or project to get started.",
                                 alignment=Qt.AlignmentFlag.AlignCenter)
            placeholder.setObjectName("PlaceholderLabel")
            self.tab_widget.addTab(placeholder, "Welcome")
            self.tab_widget.setTabsClosable(False)
            self._update_editor_actions_state()
            return

        self.tab_widget.setTabsClosable(True)
        editor = EditorWidget(self.completion_manager, self)
        editor.set_filepath(filepath)
        editor.set_text(content)
        editor.cursor_position_display_updated.connect(
            lambda line, col: self.cursor_label.setText(f" Ln {line}, Col {col} ")
        )
        editor.content_possibly_changed.connect(self._on_content_changed)

        if not filepath:
            self.untitled_file_counter += 1
        name = os.path.basename(filepath) if filepath else \
            f"Untitled-{self.untitled_file_counter}"
        index = self.tab_widget.addTab(editor, name)
        self.tab_widget.setTabToolTip(index, filepath or f"Unsaved {name}")
        self.editor_tabs_data[editor] = {
            'filepath': filepath, 'original_hash': hash(content)
        }
        self.tab_widget.setCurrentWidget(editor)
        editor.text_area.setFocus()
        self._update_editor_actions_state()
        self._on_content_changed()

    def _on_theme_selected(self, theme_id: str):
        self._apply_theme_and_icons(theme_id)

    def _on_tab_changed(self, index: int):
        self._update_window_title()
        self._update_editor_actions_state()

        editor = self.tab_widget.currentWidget()
        is_editor = isinstance(editor, EditorWidget)

        # Disconnect all previous editor-specific action triggers
        for key in ["undo", "redo", "cut", "copy", "paste", "select_all"]:
            try:
                self.actions[key].triggered.disconnect()
            except TypeError:
                pass  # No connection to disconnect

        # Reconnect actions to the new current editor
        if is_editor:
            self.actions["undo"].triggered.connect(editor.text_area.undo)
            self.actions["redo"].triggered.connect(editor.text_area.redo)
            self.actions["cut"].triggered.connect(editor.text_area.cut)
            self.actions["copy"].triggered.connect(editor.text_area.copy)
            self.actions["paste"].triggered.connect(editor.text_area.paste)
            self.actions["select_all"].triggered.connect(editor.text_area.selectAll)

            editor.text_area.undoAvailable.connect(self.actions["undo"].setEnabled)
            editor.text_area.redoAvailable.connect(self.actions["redo"].setEnabled)
            editor.text_area.copyAvailable.connect(self.actions["cut"].setEnabled)
            editor.text_area.copyAvailable.connect(self.actions["copy"].setEnabled)

            # Manually set the initial state
            self.actions["undo"].setEnabled(editor.text_area.document().isUndoAvailable())
            self.actions["redo"].setEnabled(editor.text_area.document().isRedoAvailable())
            has_selection = editor.text_area.textCursor().hasSelection()
            self.actions["cut"].setEnabled(has_selection)
            self.actions["copy"].setEnabled(has_selection)

        # Update general edit actions
        self.actions["paste"].setEnabled(is_editor)
        self.actions["select_all"].setEnabled(is_editor)
        self._trigger_file_linter()

    def _on_content_changed(self):
        # Check if widget still exists before updating
        widget = self.sender()
        if not widget or widget not in self.editor_tabs_data:
            return
            
        self._update_window_title()
        self.lint_timer.start()
        if settings_manager.get("auto_save_enabled"):
            delay = settings_manager.get("auto_save_delay_seconds") * 1000
            self.auto_save_timer.start(delay)

    def _on_project_tab_changed(self, index: int):
        path = self.project_tabs.tabToolTip(index) if index != -1 else None
        self.project_manager.set_active_project(path)
        self.completion_manager.update_project_path(path)
        self._update_window_title()

    def _update_window_title(self):
        title_parts = [f"PuffinPyEditor - v{versioning.APP_VERSION}"]
        if p_path := self.project_manager.get_active_project_path():
            title_parts.insert(0, f"[{os.path.basename(p_path)}]")

        editor = self.tab_widget.currentWidget()
        if isinstance(editor, QWidget) and editor in self.editor_tabs_data:
            idx = self.tab_widget.indexOf(editor)
            if idx == -1: return # Widget might be in a floating window
            
            tab_text = self.tab_widget.tabText(idx).strip().replace(' ●', '')

            # Only check 'is_dirty' for EditorWidgets that can be modified
            is_dirty = False
            if isinstance(editor, EditorWidget):
                is_dirty = hash(editor.get_text()) != \
                    self.editor_tabs_data[editor]['original_hash']

            display_text = f"{tab_text}{' ●' if is_dirty else ''}"
            if self.tab_widget.tabText(idx) != display_text:
                self.tab_widget.setTabText(idx, display_text)
                
            filepath = self.editor_tabs_data[editor].get('filepath')
            title_parts.insert(0, os.path.basename(filepath) if filepath else tab_text)

        self.setWindowTitle(" - ".join(title_parts))

    def _update_recent_files_menu(self):
        self.recent_files_menu.clear()
        recent_files = self.settings.get("recent_files", [])
        if not recent_files:
            self.recent_files_menu.addAction(
                QAction("No Recent Files", self, enabled=False)
            )
            return
        for fp in recent_files:
            action = QAction(os.path.basename(fp), self,
                             triggered=self._action_open_recent_file)
            action.setData(fp)
            action.setToolTip(fp)
            self.recent_files_menu.addAction(action)

    def _trigger_file_linter(self):
        editor = self.tab_widget.currentWidget()
        if isinstance(editor, EditorWidget):
            filepath = self.editor_tabs_data.get(editor, {}).get('filepath')
            if filepath:
                self.linter_manager.lint_file(filepath)

    def _action_open_recent_file(self):
        if isinstance(action := self.sender(), QAction):
            if filepath := action.data():
                self._action_open_file(filepath)

    def _action_open_folder(self):
        path = QFileDialog.getExistingDirectory(self, "Open Folder")
        if path:
            self.project_manager.open_project(path)
            self._initialize_project_views()

    def _action_close_project_by_index(self, index: int):
        if not (0 <= index < self.project_tabs.count()):
            return
        path = self.project_tabs.tabToolTip(index)
        self.project_manager.close_project(path)
        self._initialize_project_views()

    def _action_close_project(self):
        self._action_close_project_by_index(self.project_tabs.currentIndex())

    def _action_open_file_dialog(self):
        filepath, content, error = self.file_handler.open_file_dialog()
        if error:
            QMessageBox.critical(self, "Error Opening File", error)
        elif filepath:
            self._action_open_file(filepath, content)

    def _action_open_preferences(self):
        if self.preferences_dialog is None:
            self.preferences_dialog = PreferencesDialog(
                self.git_manager, self.github_manager, self.plugin_manager, self
            )
            self.preferences_dialog.settings_changed_for_editor_refresh.connect(
                self._on_editor_settings_changed)
            self.preferences_dialog.theme_changed_signal.connect(
                self._apply_theme_and_icons)
        self.preferences_dialog.show()
        self.preferences_dialog.raise_()
        self.preferences_dialog.activateWindow()

    def _show_about_dialog(self):
        QMessageBox.about(
            self,
            "About PuffinPyEditor",
            f"""<h3>PuffinPyEditor</h3>
            <p>Version: {versioning.APP_VERSION}</p>
            <p>A Modern, Extensible Python IDE built with PyQt6 and AI.</p>
            <br>
            <p>Copyright (c) 2024-2025 Stelliro</p>
            """
        )

    def _open_github_link(self):
        url = QUrl("https://github.com/Stelliro/PuffinPyEditor")
        QDesktopServices.openUrl(url)

    def _action_open_file(self, filepath: str, content: Optional[str] = None):
        norm_path = os.path.normpath(filepath)
        ext = os.path.splitext(norm_path)[1].lower()

        # ---> THE FIX IS HERE <---
        # This loop now robustly checks all tracked widgets (tabbed or floating)
        # to see if the file is already open.
        for widget, data in self.editor_tabs_data.items():
            if data.get('filepath') == norm_path:
                # If it's found, bring its window to the front and focus it.
                log.info(f"File '{norm_path}' is already open. Focusing it.")
                window = widget.window()
                window.setWindowState(window.windowState() & ~Qt.WindowState.WindowMinimized | Qt.WindowState.WindowActive)
                window.raise_()
                window.activateWindow()

                # If the widget is in the main tab bar, also switch to it.
                if self.tab_widget.indexOf(widget) > -1:
                    self.tab_widget.setCurrentWidget(widget)
                return  # Stop execution to prevent opening a duplicate.

        # Custom file handler check
        if ext in self.file_open_handlers:
            self.file_open_handlers[ext](norm_path)
            return

        # If the file wasn't found open, proceed to read and open it.
        if content is None:
            try:
                with open(norm_path, 'r', encoding='utf-8', errors='replace') as f:
                    content = f.read()
                self.file_handler._add_to_recent_files(norm_path)
            except Exception as e:
                QMessageBox.critical(self, "Error Opening File", f"Could not read file: {e}")
                return

        self._add_new_tab(norm_path, content)

    def _action_save_file(self, widget: Optional[EditorWidget] = None) -> bool:
        editor = widget or self.tab_widget.currentWidget()
        if not isinstance(editor, EditorWidget):
            return False

        filepath = self.editor_tabs_data.get(editor, {}).get('filepath')
        if not filepath:
            return self._action_save_as(editor)

        if saved_path := self.file_handler.save_file_content(filepath, editor.get_text()):
            self._update_tab_info(editor, saved_path)
            return True
        return False

    def _action_save_as(self, editor: Optional[EditorWidget] = None) -> bool:
        editor_to_save = editor or self.tab_widget.currentWidget()
        if not isinstance(editor_to_save, EditorWidget):
            return False

        current_path = self.editor_tabs_data.get(editor_to_save, {}).get('filepath')
        new_path = self.file_handler.save_file_content(
            current_path, editor_to_save.get_text(), save_as=True
        )
        if new_path:
            self._update_tab_info(editor_to_save, new_path)
            # Update window title of floating window if necessary
            if editor_to_save.window() is not self:
                editor_to_save.window().setWindowTitle(f"{os.path.basename(new_path)} - PuffinPyEditor")
            return True
        return False

    def _action_save_all(self):
        for editor, data in list(self.editor_tabs_data.items()):
             if isinstance(editor, EditorWidget):
                is_dirty = hash(editor.get_text()) != data['original_hash']
                if is_dirty and data.get('filepath'):
                    if self.file_handler.save_file_content(data['filepath'], editor.get_text()):
                        self._update_tab_info(editor, data['filepath'])
        self._update_window_title()

    def _action_close_tab_by_index(self, index: int):
        widget = self.tab_widget.widget(index)
        self._close_widget_safely(widget)

    def _close_widget_safely(self, widget: QWidget, event: Optional[QCloseEvent] = None):
        is_editor_widget = isinstance(widget, EditorWidget)
        if not is_editor_widget or widget not in self.editor_tabs_data:
            if event: event.accept()
            # If it's a non-editor tab (like "Welcome"), just remove it.
            if self.tab_widget.indexOf(widget) > -1:
                self.tab_widget.removeTab(self.tab_widget.indexOf(widget))
            return
        
        is_dirty = hash(widget.get_text()) != self.editor_tabs_data.get(widget, {})['original_hash']

        if is_dirty:
            # Determine the name for the dialog message
            tab_name = "this item"
            if self.tab_widget.indexOf(widget) > -1:
                 tab_name = f"'{self.tab_widget.tabText(self.tab_widget.indexOf(widget))}'"
            elif widget.window() is not self:
                 tab_name = f"'{widget.window().windowTitle()}'"

            reply = QMessageBox.question(
                self, "Unsaved Changes",
                f"Save changes to {tab_name}?",
                QMessageBox.StandardButton.Save |
                QMessageBox.StandardButton.Discard |
                QMessageBox.StandardButton.Cancel
            )
            if reply == QMessageBox.StandardButton.Cancel:
                if event: event.ignore()
                return
            if reply == QMessageBox.StandardButton.Save and not self._action_save_file(widget=widget):
                if event: event.ignore()
                return
        
        # If we reached here, it's safe to close.
        self.editor_tabs_data.pop(widget, None)
        
        # If it was a tab, remove it from the tab widget
        if (tab_index := self.tab_widget.indexOf(widget)) > -1:
             self.tab_widget.removeTab(tab_index)
        
        # Accept the close event for the widget (important for floating windows)
        if event: event.accept()
        
        if self.tab_widget.count() == 0 and not self._is_app_closing:
            self._add_new_tab(is_placeholder=True)

    def keyPressEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key.Key_Print:
            event.ignore()
            return
        super().keyPressEvent(event)

    def closeEvent(self, event):
        if self._is_app_closing:
            event.accept()
            return

        unsaved_widgets = [
            w for w, data in self.editor_tabs_data.items()
            if isinstance(w, EditorWidget) and (hash(w.get_text()) != data['original_hash'])
        ]
        
        if unsaved_widgets:
            reply = QMessageBox.question(
                self, "Unsaved Changes",
                "You have unsaved changes in one or more windows. Save before exiting?",
                QMessageBox.StandardButton.SaveAll |
                QMessageBox.StandardButton.Discard |
                QMessageBox.StandardButton.Cancel
            )
            if reply == QMessageBox.StandardButton.SaveAll:
                self._action_save_all()
            elif reply == QMessageBox.StandardButton.Cancel:
                event.ignore()
                return

        log.info("Starting graceful shutdown...")
        self._is_app_closing = True
        
        for widget in list(self.editor_tabs_data.keys()):
             if widget.window() is not self:
                  widget.window().close()

        self.completion_manager.shutdown()
        self.git_manager.shutdown()
        self.github_manager.shutdown()
        self.linter_manager.shutdown()
        self.project_manager.save_session()
        self._save_window_geometry()
        self.settings.save()
        log.info("PuffinPyEditor closing clean.")
        event.accept()

    def _auto_save_current_tab(self):
        editor = self.tab_widget.currentWidget()
        if isinstance(editor, EditorWidget):
            is_dirty = (hash(editor.get_text()) !=
                        self.editor_tabs_data[editor]['original_hash'])
            filepath = self.editor_tabs_data[editor].get('filepath')
            if filepath and is_dirty:
                self.statusBar().showMessage(
                    f"Auto-saving {os.path.basename(filepath)}...", 1500
                )
                self._action_save_file()

    def _update_tab_info(self, editor: QWidget, path: str):
        if not path:
            return
        norm_path = os.path.normpath(path)
        if isinstance(editor, EditorWidget):
            editor.set_filepath(norm_path)
            new_hash = hash(editor.get_text())
            self.editor_tabs_data[editor].update({
                'filepath': norm_path, 'original_hash': new_hash
            })
        else:
             self.editor_tabs_data[editor].update({'filepath': norm_path})

        if (idx := self.tab_widget.indexOf(editor)) != -1:
            self.tab_widget.setTabText(idx, os.path.basename(norm_path))
            self.tab_widget.setTabToolTip(idx, norm_path)

        self.statusBar().showMessage(f"Saved: {norm_path}", 3000)
        self._update_window_title()
        if isinstance(editor, EditorWidget):
            self._trigger_file_linter()

    def _update_editor_actions_state(self):
        widget = self.tab_widget.currentWidget()
        is_editor = isinstance(widget, EditorWidget)
        can_save = hasattr(widget, 'get_text') 

        self.actions["save"].setEnabled(can_save)
        self.actions["save_as"].setEnabled(can_save)
        self.actions["save_all"].setEnabled(True) 
        for key in ["undo", "redo", "cut", "copy", "paste", "select_all"]:
             self.actions[key].setEnabled(is_editor)

    def _on_editor_settings_changed(self):
        for widget in self.editor_tabs_data.keys():
            if isinstance(widget, EditorWidget):
                widget.update_editor_settings()

    def _goto_definition_result(self, filepath: str, line: int, col: int):
        if not filepath:
            self.statusBar().showMessage("Definition not found", 3000)
            return

        norm_path = os.path.normpath(filepath)
        for editor, data in self.editor_tabs_data.items():
            if data.get('filepath') == norm_path and isinstance(editor, EditorWidget):
                # Activate the window it lives in
                if editor.window() is not self:
                     editor.window().activateWindow()
                else:
                     self.tab_widget.setCurrentWidget(editor)
                
                editor.goto_line_and_column(line, col)
                return

        # File not open, open it first
        self._action_open_file(norm_path)
        QApplication.processEvents()
        
        # Check again now that it should be open
        for editor, data in self.editor_tabs_data.items():
            if data.get('filepath') == norm_path and isinstance(editor, EditorWidget):
                editor.goto_line_and_column(line, col)
                break

    def _save_window_geometry(self):
        self.settings.set("window_size",
                          [self.size().width(), self.size().height()], False)
        self.settings.set("window_position",
                          [self.pos().x(), self.pos().y()], False)
```

# AI Task: No Persona (General Review)
## Timestamp: 2025-07-13T19:20:13.129555

---SYSTEM-PROMPT---

You are a helpful and experienced software developer. Your goal is to perform a general code review based on the user's instructions and the provided files. Offer concrete suggestions for improvement.

---USER-PROMPT---

# Project Review Request

**User's Goal:**
can you please make a plugin that replaces the need for an installer folder that is the replacement to the upload installer button? the botton should not be there if this new plugin is not installed

---
**Project File Tree:**
```
/PuffinPyEditor
 ├── LICENSE.md
 ├── README.md
 ├── VERSION.txt
 ├── app_core
 │   ├── __init__.py
 │   ├── completion_manager.py
 │   ├── file_handler.py
 │   ├── github_manager.py
 │   ├── golden_rules.py
 │   ├── highlighters
 │   │   ├── cpp_syntax_highlighter.py
 │   │   ├── csharp_syntax_highlighter.py
 │   │   ├── css_syntax_highlighter.py
 │   │   ├── html_syntax_highlighter.py
 │   │   ├── javascript_syntax_highlighter.py
 │   │   ├── json_syntax_highlighter.py
 │   │   ├── python_syntax_highlighter.py
 │   │   └── rust_syntax_highlighter.py
 │   ├── linter_manager.py
 │   ├── plugin_manager.py
 │   ├── project_manager.py
 │   ├── puffin_api.py
 │   ├── settings_manager.py
 │   ├── source_control_manager.py
 │   ├── syntax_highlighters.py
 │   ├── theme_manager.py
 │   └── update_manager.py
 ├── assets
 │   ├── ai_personas
 │   │   ├── anya_the_architect.py
 │   │   ├── average_joe_steve.py
 │   │   ├── chad_the_village_idiot.py
 │   │   ├── eva_the_sentinel.py
 │   │   ├── forge_the_devops_engineer.py
 │   │   ├── glitch_the_qa_maverick.py
 │   │   ├── isabella_the_api_artisan.py
 │   │   ├── julian_the_perfectionist.py
 │   │   ├── kaito_the_algorithmist.py
 │   │   ├── kaito_the_logician.py
 │   │   ├── leo_the_documentarian.py
 │   │   ├── marcus_the_data_modeler.py
 │   │   ├── sofia_the_ux_visionary.py
 │   │   └── spark_the_greenfield_innovator.py
 │   ├── fonts
 │   │   └── README.txt
 │   ├── golden_rules.json
 │   ├── style_presets
 │   │   └── default_puffinpy_style.json
 │   └── themes
 │       ├── __init__.py
 │       ├── custom_themes.json
 │       └── icon_colors.json
 ├── core_debug_tools
 │   ├── debug_framework
 │   │   ├── api.py
 │   │   ├── debug_window.py
 │   │   ├── plugin.json
 │   │   └── plugin_main.py
 │   ├── enhanced_exceptions
 │   │   ├── exception_dialog.py
 │   │   ├── plugin.json
 │   │   └── plugin_main.py
 │   ├── live_log_viewer
 │   │   ├── plugin.json
 │   │   └── plugin_main.py
 │   └── plugin_initializer
 │       ├── __init__.py
 │       ├── new_plugin_dialog.py
 │       ├── plugin.json
 │       └── plugin_main.py
 ├── index.json
 ├── installer
 │   ├── build.py
 │   └── create_installer_assets.py
 ├── main.py
 ├── plugins
 │   ├── __init__.py
 │   ├── ai_export_viewer
 │   │   ├── __init__.py
 │   │   ├── ai_export_viewer_widget.py
 │   │   ├── plugin.json
 │   │   └── plugin_main.py
 │   ├── ai_patcher
 │   │   ├── __init__.py
 │   │   ├── patcher_dialog.py
 │   │   ├── plugin.json
 │   │   ├── plugin_main.py
 │   │   └── response_parser.py
 │   ├── ai_quick_actions
 │   │   ├── __init__.py
 │   │   ├── plugin.json
 │   │   └── plugin_main.py
 │   ├── ai_tools
 │   │   ├── __init__.py
 │   │   ├── ai_export_dialog.py
 │   │   ├── ai_response_dialog.py
 │   │   ├── api_client.py
 │   │   ├── persona_logic.py
 │   │   ├── persona_manager_dialog.py
 │   │   ├── plugin.json
 │   │   ├── plugin_main.py
 │   │   └── style_preset_manager.py
 │   ├── api_keys_manager
 │   │   ├── __init__.py
 │   │   ├── api_keys_settings_page.py
 │   │   ├── plugin.json
 │   │   └── plugin_main.py
 │   ├── github_tools
 │   │   ├── __init__.py
 │   │   ├── github_dialog.py
 │   │   ├── new_release_dialog.py
 │   │   ├── plugin.json
 │   │   ├── plugin_main.py
 │   │   └── select_repo_dialog.py
 │   ├── markdown_viewer
 │   │   ├── __init__.py
 │   │   ├── markdown_editor_widget.py
 │   │   ├── markdown_syntax_highlighter.py
 │   │   ├── plugin.json
 │   │   └── plugin_main.py
 │   ├── plugin_publisher
 │   │   ├── __init__.py
 │   │   ├── plugin.json
 │   │   ├── plugin_main.py
 │   │   └── publish_dialog.py
 │   ├── refactor_tool
 │   │   ├── plugin.json
 │   │   ├── plugin_main.py
 │   │   └── refactor_dialog.py
 │   ├── script_runner
 │   │   ├── code_runner.py
 │   │   ├── output_panel.py
 │   │   ├── plugin.json
 │   │   └── plugin_main.py
 │   ├── terminal
 │   │   ├── __init__.py
 │   │   ├── plugin.json
 │   │   ├── plugin_main.py
 │   │   └── terminal_widget.py
 │   └── theme_editor
 │       ├── plugin.json
 │       ├── plugin_main.py
 │       └── theme_editor_dialog.py
 ├── requirements.txt
 ├── tray_app.py
 ├── ui
 │   ├── __init__.py
 │   ├── editor_widget.py
 │   ├── explorer
 │   │   ├── __init__.py
 │   │   ├── context_menu.py
 │   │   ├── folder_size_worker.py
 │   │   ├── helpers.py
 │   │   ├── icon_provider.py
 │   │   └── list_view_widget.py
 │   ├── main_window.py
 │   ├── preferences_dialog.py
 │   └── widgets
 │       ├── __init__.py
 │       ├── draggable_tab_widget.py
 │       ├── find_panel.py
 │       ├── problems_panel.py
 │       ├── source_control_panel.py
 │       └── splash_screen.py
 ├── updater.py
 └── utils
     ├── __init__.py
     ├── helpers.py
     ├── log_viewer.py
     ├── logger.py
     ├── markdown_linter.py
     ├── validate_assets.py
     └── versioning.py

```
---
**Files for Review:**
### File: `/updater.py`
```py
# PuffinPyEditor/updater.py
import sys
import os
import time
import requests
import zipfile
import shutil

# --- Configuration ---
# A set of files and folders that the updater will NEVER overwrite, even if they
# exist in the downloaded update. This protects user-specific data.
# Paths should use forward slashes and be relative to the install directory.
PROTECTED_ITEMS = {
    "puffin_editor_settings.json",
    "logs",
    "assets/themes/custom_themes.json"
}
# --- End Configuration ---


def log(message):
    """Simple logger for the updater script."""
    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {message}")


def safe_copy(source_dir, install_dir):
    """
    Intelligently copies files from the update source to the installation
    directory, skipping any protected files or folders.
    """
    log("Starting safe copy process...")
    for root, dirs, files in os.walk(source_dir):
        # Prevent os.walk from going into protected directories
        dirs[:] = [d for d in dirs
                   if os.path.relpath(os.path.join(root, d), source_dir)
                   .replace(os.sep, '/') not in PROTECTED_ITEMS]

        # Process directories first
        for d in dirs:
            rel_path = os.path.relpath(os.path.join(root, d), source_dir)
            dest_path = os.path.join(install_dir, rel_path)
            os.makedirs(dest_path, exist_ok=True)

        # Process files
        for f in files:
            src_path = os.path.join(root, f)
            rel_path = os.path.relpath(src_path, source_dir)
            # Use forward slashes for cross-platform comparison
            if rel_path.replace(os.sep, '/') in PROTECTED_ITEMS:
                log(f"Skipping protected file: {rel_path}")
                continue
            dest_path = os.path.join(install_dir, rel_path)
            shutil.copy2(src_path, dest_path)
    log("Safe copy process finished.")


def main():
    log("PuffinPy Updater started.")

    if len(sys.argv) < 3:
        log("Error: Missing arguments. "
            "Usage: python updater.py <download_url> <install_dir>")
        return

    download_url = sys.argv[1]
    install_dir = sys.argv[2]

    log(f"Update requested for directory: {install_dir}")
    log(f"Downloading from: {download_url}")

    log("Waiting for main application to exit...")
    time.sleep(2)

    try:
        log("Downloading new version...")
        response = requests.get(download_url, stream=True)
        response.raise_for_status()

        zip_path = os.path.join(install_dir, "update.zip")
        with open(zip_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        log("Download complete.")

    except requests.exceptions.RequestException as e:
        log(f"Error: Failed to download update. {e}")
        return

    backup_dir = os.path.join(install_dir,
                              f"PuffinPyEditor_backup_{int(time.time())}")
    log(f"Creating backup at: {backup_dir}")
    try:
        # Update ignore pattern to also ignore temp update files
        ignore_patterns = shutil.ignore_patterns(
            'PuffinPyEditor_backup_*', 'update_temp', '*.zip', '*.log',
            'venv', '.git*'
        )
        shutil.copytree(install_dir, backup_dir, ignore=ignore_patterns)
    except Exception as e:
        log(f"Warning: Could not create full backup. {e}")

    temp_extract_dir = os.path.join(install_dir, "update_temp")
    try:
        log("Unzipping update...")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(temp_extract_dir)

        # Check if the zip contains a single root folder
        extracted_content = os.listdir(temp_extract_dir)
        source_dir = temp_extract_dir
        if len(extracted_content) == 1:
            possible_root = os.path.join(temp_extract_dir, extracted_content[0])
            if os.path.isdir(possible_root):
                log(f"Update is in a root folder: {extracted_content[0]}")
                source_dir = possible_root

        log(f"Replacing files in '{install_dir}' using safe copy method.")
        safe_copy(source_dir, install_dir)
        log("Update successfully installed.")

    except Exception as e:
        log(f"Error: Failed during installation. {e}")
        log("Attempting to restore from backup...")
        # (Restore logic would go here if implemented)
        return

    finally:
        log("Cleaning up temporary files...")
        if os.path.exists(zip_path):
            os.remove(zip_path)
        if os.path.exists(temp_extract_dir):
            shutil.rmtree(temp_extract_dir)

    log("Update process finished. Relaunch application to see the changes.")


if __name__ == "__main__":
    main()
```

### File: `/tray_app.py`
```py
# PuffinPyEditor/tray_app.py
import sys
import os
import subprocess
from PyQt6.QtWidgets import QApplication, QSystemTrayIcon, QMenu
from PyQt6.QtGui import QIcon, QAction

# This script is intended to be run as a standalone executable.
# It finds its sibling 'PuffinPyEditor.exe' and launches it.

def get_executable_path():
    """Determine the path of the main PuffinPyEditor executable."""
    if getattr(sys, 'frozen', False):
        # We are running in a bundled app
        exe_dir = os.path.dirname(sys.executable)
        return os.path.join(exe_dir, "PuffinPyEditor.exe")
    else:
        # We are running from source, for testing
        return os.path.join(os.path.dirname(__file__), "dist", "PuffinPyEditor", "PuffinPyEditor.exe")

def get_icon_path():
    """Determine the path of the application icon."""
    if getattr(sys, 'frozen', False):
        base_dir = os.path.dirname(sys.executable)
    else:
        base_dir = os.path.dirname(__file__)
    
    # Path when running from source or in the final bundled structure
    icon_path = os.path.join(base_dir, "installer", "assets", "PuffinPyEditor.ico")
    if not os.path.exists(icon_path):
        # Fallback for when 'tray_app.exe' is in the root of the install dir
        icon_path = os.path.join(base_dir, "PuffinPyEditor.ico")

    return icon_path if os.path.exists(icon_path) else None

class PuffinTrayApp(QApplication):
    def __init__(self, argv):
        super().__init__(argv)
        self.setQuitOnLastWindowClosed(False)

        main_exe_path = get_executable_path()
        icon_path = get_icon_path()

        if not icon_path:
            print("Error: Could not find application icon.", file=sys.stderr)
            # Use a default icon if not found
            self.tray_icon = QSystemTrayIcon(self)
        else:
            self.tray_icon = QSystemTrayIcon(QIcon(icon_path), self)

        self.tray_icon.setToolTip("PuffinPyEditor")

        menu = QMenu()
        open_action = QAction("Open PuffinPyEditor", self)
        open_action.triggered.connect(lambda: self.open_editor(main_exe_path))
        menu.addAction(open_action)

        menu.addSeparator()

        quit_action = QAction("Quit Background App", self)
        quit_action.triggered.connect(self.quit)
        menu.addAction(quit_action)

        self.tray_icon.setContextMenu(menu)
        self.tray_icon.activated.connect(self.on_tray_activated)
        self.tray_icon.show()

    def on_tray_activated(self, reason):
        # Open on left-click
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            self.open_editor(get_executable_path())

    def open_editor(self, path):
        if not os.path.exists(path):
            self.tray_icon.showMessage(
                "Error",
                f"Could not find PuffinPyEditor.exe at:\n{path}",
                QSystemTrayIcon.MessageIcon.Critical
            )
            return
        
        try:
            # Launch the main process. This will trigger UAC if manifested correctly.
            subprocess.Popen([path])
        except Exception as e:
            self.tray_icon.showMessage(
                "Launch Error",
                f"Failed to start PuffinPyEditor:\n{e}",
                QSystemTrayIcon.MessageIcon.Critical
            )


if __name__ == "__main__":
    # Ensure only one instance of the tray app runs
    # This is a simple implementation; more robust solutions exist (e.g., using a QSharedMemory)
    # but this is sufficient for this use case.
    
    app = PuffinTrayApp(sys.argv)
    sys.exit(app.exec())
```

### File: `/requirements.txt`
```txt
flake8
findstr
GitPython
jedi
jsonschema
Markdown
pywin32
PyQt6
qtawesome
requests
winshell
```

### File: `/main.py`
```py
# PuffinPyEditor/main.py
import sys
import traceback
import os

# --- Initial Dependency Check ---
# This is a user-friendly check for the most critical dependency.
# It provides a clear message if PyQt6 is not installed, which is
# a common issue when running from source for the first time.
try:
    from PyQt6.QtWidgets import QApplication
except ImportError:
    print("---------------------------------------------------------")
    print("FATAL ERROR: The 'PyQt6' library is not installed.")
    print("This is a required dependency for PuffinPyEditor to run.")
    print("\nPlease run the following command in your terminal:")
    print("pip install -r requirements.txt")
    print("---------------------------------------------------------")
    # input("\nPress Enter to exit...") # Optional: uncomment to wait for user input
    sys.exit(1)  # Exit with a non-zero code to indicate an error

# --- Core Imports ---
from app_core.theme_manager import ThemeManager
from app_core.file_handler import FileHandler
from utils.logger import log
from ui.widgets.splash_screen import SplashScreen # MODIFIED: Import the new splash screen


def fallback_excepthook(exc_type, exc_value, exc_tb):
    """
    A simple fallback excepthook to log uncaught exceptions.
    """
    # CORRECTED: This handler now also ignores KeyboardInterrupt.
    if issubclass(exc_type, KeyboardInterrupt):
        log.warning("KeyboardInterrupt caught and ignored by fallback handler.")
        print("KeyboardInterrupt ignored.", file=sys.stderr)
        return
        
    log.critical("--- FATAL UNHANDLED EXCEPTION ---")
    tb_text = "".join(traceback.format_exception(exc_type, exc_value, exc_tb))
    log.critical(f"Traceback:\n{tb_text}")
    print(f"FATAL ERROR:\n{tb_text}", file=sys.stderr)
    sys.__excepthook__(exc_type, exc_value, exc_tb)


def main():
    sys.excepthook = fallback_excepthook

    DEBUG_MODE = "--debug" in sys.argv

    log.info("=" * 53)
    log.info(f"PuffinPyEditor Application Starting... (Debug: {DEBUG_MODE})")
    log.info(f"Python version: {sys.version.splitlines()[0]}")
    log.info(f"Operating System: {sys.platform}")
    log.info("=" * 53)

    app = QApplication(sys.argv)
    app.setApplicationName("PuffinPyEditor")
    app.setOrganizationName("PuffinPyEditorProject")

    # --- MODIFIED: Splash screen integration ---
    splash = SplashScreen()
    splash.show()
    QApplication.processEvents()

    # Instantiate the managers here, after QApplication
    splash.set_status("Loading themes...")
    theme_manager = ThemeManager()
    theme_manager.apply_theme_to_app(app)

    splash.set_status("Initializing file system...")
    file_handler = FileHandler()

    from ui.main_window import MainWindow

    try:
        splash.set_status("Creating main window...")
        main_window = MainWindow(file_handler, theme_manager, debug_mode=DEBUG_MODE)
        log.info("MainWindow instance created successfully.")
    except Exception:
        log.critical("A fatal error occurred during MainWindow initialization.")
        # Make sure splash screen is closed before showing traceback
        splash.close()
        raise
    
    # Hide the splash and show the main window with a fade effect
    splash.finish(main_window)
    log.info("MainWindow shown. Entering main event loop.")
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
```

### File: `/index.json`
```json
[
    {
        "id": "find_replace",
        "name": "Find/Replace",
        "author": "PuffinPy Team",
        "version": "1.1.1",
        "description": "Adds a Find/Replace dialog (Ctrl+F).",
        "download_url": "https://raw.githubusercontent.com/Stelliro/PuffinPyEditor/main/zips/find_replace.zip"
    },
    {
        "id": "linter_ui",
        "name": "Linter UI",
        "author": "PuffinPy Team",
        "version": "1.1.1",
        "description": "Provides the 'Problems' panel to display linter results from Flake8.",
        "download_url": "https://raw.githubusercontent.com/Stelliro/PuffinPyEditor/main/zips/linter_ui.zip"
    },
    {
        "id": "python_runner",
        "name": "Python Runner",
        "author": "PuffinPy Team",
        "version": "1.1.1",
        "description": "Adds functionality to run Python scripts (F5).",
        "download_url": "https://raw.githubusercontent.com/Stelliro/PuffinPyEditor/main/zips/python_runner.zip"
    },
    {
        "id": "source_control_ui",
        "name": "Source Control UI",
        "author": "PuffinPy Team",
        "version": "1.1.1",
        "description": "Provides the 'Source Control' panel to view Git status.",
        "download_url": "https://raw.githubusercontent.com/Stelliro/PuffinPyEditor/main/zips/source_control_ui.zip"
    },
    {
        "id": "ai_export_viewer",
        "name": "AI Export Viewer",
        "author": "PuffinPy Team",
        "version": "1.1.0",
        "description": "Provides a tab-based viewer to manage and review past AI project exports.",
        "download_url": "https://raw.githubusercontent.com/Stelliro/PuffinPyEditor/main/zips/ai_export_viewer.zip"
    },
    {
        "id": "ai_patcher",
        "name": "AI Patcher",
        "author": "PuffinPy Team",
        "version": "2.0.0",
        "description": "A multi-step tool to generate prompts, parse AI responses, and visually review and apply code changes to the project.",
        "download_url": "https://raw.githubusercontent.com/Stelliro/PuffinPyEditor/main/zips/ai_patcher.zip"
    },
    {
        "id": "ai_quick_actions",
        "name": "AI Quick Actions",
        "author": "PuffinPy Team",
        "version": "1.0.0",
        "description": "Adds AI-powered actions like 'Explain' and 'Refactor' to the editor's context menu.",
        "download_url": "https://raw.githubusercontent.com/Stelliro/PuffinPyEditor/main/zips/ai_quick_actions.zip"
    },
    {
        "id": "ai_tools",
        "name": "AI Tools",
        "author": "PuffinPy Team",
        "version": "1.1.2",
        "description": "Adds an 'Export for AI' dialog.",
        "download_url": "https://raw.githubusercontent.com/Stelliro/PuffinPyEditor/main/zips/ai_tools.zip"
    },
    {
        "id": "api_keys_manager",
        "name": "API Keys Manager",
        "author": "PuffinPy Team",
        "version": "1.0.0",
        "description": "Provides a secure settings page for managing API provider keys.",
        "download_url": "https://raw.githubusercontent.com/Stelliro/PuffinPyEditor/main/zips/api_keys_manager.zip"
    },
    {
        "id": "github_tools",
        "name": "GitHub Tools",
        "author": "PuffinPy Team",
        "version": "1.2.0",
        "description": "Provides UI for cloning, releases, and other GitHub interactions.",
        "download_url": "https://raw.githubusercontent.com/Stelliro/PuffinPyEditor/main/zips/github_tools.zip"
    },
    {
        "id": "markdown_viewer",
        "name": "Markdown Viewer",
        "author": "AI Assistant",
        "version": "1.0.2",
        "description": "Adds support for viewing rendered Markdown (.md) files in a separate tab. It intercepts file open calls to provide a rich text view instead of a plain text editor for .md files.",
        "download_url": "https://raw.githubusercontent.com/Stelliro/PuffinPyEditor/main/zips/markdown_viewer.zip"
    },
    {
        "id": "plugin_publisher",
        "name": "Plugin Publisher",
        "author": "AI Assistant",
        "version": "1.0.1",
        "description": "Provides a tool to package and publish installed plugins to a specified GitHub distribution repository. Manages versioning and updates the repository's index.json.",
        "download_url": "https://raw.githubusercontent.com/Stelliro/PuffinPyEditor/main/zips/plugin_publisher.zip"
    },
    {
        "id": "script_runner",
        "name": "Script Runner",
        "author": "PuffinPy Team",
        "version": "1.2.0",
        "description": "Adds functionality to run Python, C++, C#, and JavaScript files from the editor.",
        "download_url": "https://raw.githubusercontent.com/Stelliro/PuffinPyEditor/main/zips/script_runner.zip"
    },
    {
        "id": "terminal",
        "name": "Integrated Terminal",
        "author": "PuffinPy Team",
        "version": "1.0.0",
        "description": "Provides a dockable, theme-aware terminal that runs a native shell within the editor.",
        "download_url": "https://raw.githubusercontent.com/Stelliro/PuffinPyEditor/main/zips/terminal.zip"
    },
    {
        "id": "theme_editor",
        "name": "Theme Editor",
        "author": "PuffinPy",
        "version": "1.0.0",
        "description": "A graphical editor for creating and modifying UI themes.",
        "download_url": "https://raw.githubusercontent.com/Stelliro/PuffinPyEditor/main/zips/theme_editor.zip"
    },
    {
        "id": "debug_framework",
        "name": "Debug Tools Framework",
        "author": "AI Assistant",
        "version": "1.0.0",
        "description": "Provides a core framework and UI for debugging plugins. Other debug tools can register themselves with this framework.",
        "download_url": "https://raw.githubusercontent.com/Stelliro/PuffinPyEditor/main/zips/debug_framework.zip"
    },
    {
        "id": "enhanced_exceptions",
        "name": "Enhanced Exception Reporter",
        "author": "AI Assistant",
        "version": "1.0.0",
        "description": "Replaces the default crash handler with a developer-friendly dialog showing a detailed traceback.",
        "download_url": "https://raw.githubusercontent.com/Stelliro/PuffinPyEditor/main/zips/enhanced_exceptions.zip"
    },
    {
        "id": "live_log_viewer",
        "name": "Live Log Viewer",
        "author": "AI Assistant",
        "version": "1.0.0",
        "description": "Adds a tool to launch a separate, real-time log viewer application that persists across application restarts.",
        "download_url": "https://raw.githubusercontent.com/Stelliro/PuffinPyEditor/main/zips/live_log_viewer.zip"
    },
    {
        "id": "plugin_initializer",
        "name": "Plugin Initializer",
        "author": "PuffinPy AI",
        "version": "1.0.0",
        "description": "A developer tool to quickly scaffold new plugins for PuffinPyEditor.",
        "download_url": "https://raw.githubusercontent.com/Stelliro/PuffinPyEditor/main/zips/plugin_initializer.zip"
    }
]
```

### File: `/VERSION.txt`
```txt
1.9.71
```

### File: `/README.md`
```md
# 🐧 PuffinPyEditor

**DEVELOPED WITH AI**

**A Modern, Extensible Python IDE built with PyQt6 and a lot of passion.**

PuffinPyEditor is a lightweight yet powerful Integrated Development Environment for Python developers. Built from the ground up using Python and the PyQt6 framework, it aims to provide a clean, modern, and highly customizable coding experience. It's perfect for developers who want a fast, native-feeling tool that integrates essential features like version control, a built-in terminal, and a dynamic plugin system, without the overhead of larger IDEs.

### Why PuffinPyEditor?

*   **For Python, By Python:** The entire application is a testament to what's possible with Python, using the powerful PyQt6 framework for its native UI.
*   **Lightweight & Fast:** Starts quickly and stays responsive. PuffinPyEditor focuses on providing the essential tools you need without the bloat.
*   **You're in Control:** With a deep theme customizer, extensive preferences, and a simple plugin system, you can tailor the editor to your exact workflow and aesthetic.

## ✨ Key Features

---

#### 📝 **Modern Code Editor**
*   **Advanced Syntax Highlighting:** Full Python syntax highlighting that adapts instantly to your chosen theme.
*   **Intelligent Code Completion:** Smart suggestions, function signature hints, and detailed tooltips powered by the Jedi engine.
*   **Go to Definition:** Instantly jump to the definition of any class, function, or variable with a single keypress (`F12`).
*   **Efficient Text Editing:** Enjoy modern editor features like line numbers, auto-indentation (tabs or spaces), automatic bracket/quote pairing, and multi-line editing.
*   **Powerful Find & Replace:** A familiar and robust dialog for searching within files, with support for case sensitivity, whole words, and more.

---

#### 🗂️ **Full Project & File Management**
*   **Tabbed Project Management:** Open multiple project folders in a tabbed sidebar, allowing you to switch between different contexts effortlessly.
*   **Intuitive File Explorer:** A full-featured file tree with a context menu to create, rename, and delete files and folders directly within the editor.
*   **Drag and Drop:** Easily reorganize your project by dragging and dropping files and folders within the file tree.

---

#### 🤖 **Advanced AI Export**
*   **Intelligent Context Creation:** A powerful tool under the `Tools` menu designed to package your project for analysis by Large Language Models (LLMs) like GPT, Claude, or Gemini.
*   **Selective File Inclusion:** Don't send your entire project. Use the built-in file tree to select exactly which files and folders should be included in the export, keeping the context clean and relevant.
*   **Custom Instructions & Guidelines:** Guide the AI's analysis by providing detailed instructions and a list of specific rules or guidelines for it to follow.
*   **Reusable Prompt Loadouts:**
    *   Comes with pre-packaged loadouts for common tasks like "Code Review," "Documentation Generation," and "Refactoring Suggestions."
    *   Create and save your own custom loadouts for your unique workflows.
    *   Easily load, update, and delete your saved prompts, streamlining your interaction with AI.
*   **Integrated Linter Results:** The export automatically includes `flake8` linter results for each selected Python file, giving the AI immediate insight into code quality issues.

---

#### 🔧 **Integrated Tooling**
*   **Flexible Dockable UI:** Rearrange the Terminal, Problems, Output, and Source Control panels to create a layout that works for you.
*   **Built-in Terminal:** A fully interactive terminal that opens in your project's root directory. It automatically detects Python virtual environments (`venv`) for a seamless workflow.
*   **One-Click Code Runner:** Execute Python scripts directly from the editor (`F5`) and see their output in the dedicated Output panel.
*   **Live Linter Integration:** Get on-the-fly code analysis using `flake8`. Errors and warnings are clearly displayed in the "Problems" panel, allowing you to jump straight to the issue.

---

#### 🐙 **Deep Source Control & GitHub Integration**
*   **Git Aware:** The "Source Control" panel automatically detects Git repositories and shows you changed files at a glance.
*   **Core Git Actions:** Stage changes, commit your work with a message, and push and pull to/from your remotes with the click of a button.
*   **Seamless GitHub Workflow:**
    *   **Publish Project:** Have a local project that's not on Git? The "Publish" button will create a new GitHub repository and push your project to it in one go.
    *   **Clone & Manage:** The GitHub dialog allows you to list your personal repositories, view their branches, and clone them directly to your machine.
    *   **Create Releases:** Create new versioned releases on GitHub, complete with tags, notes, and asset uploads, all from within the app.

---

#### 🎨 **Powerful Customization**
*   **Advanced Theme Manager:** PuffinPyEditor comes with a curated set of light and dark themes. The powerful **Theme Customizer** allows you to edit any theme, tweak every color, and save your own unique creations.
*   **Extensive Preferences:** Customize everything from font family and size to indentation settings (tabs vs. spaces) and auto-save behavior.

---

#### 🔌 **Simple & Extensible Plugin System**
*   **Dynamic Plugin Loading:** Add new features and tools to the editor without ever touching the core source code.
*   **Easy Plugin Management:** Install new plugins by fetching them from a GitHub repository or by uploading a local `.zip` file directly through the Preferences menu.

## 🚀 Getting Started

### Using the Installer (Windows)
The easiest way to get started on Windows is to download the latest setup executable from the [**Releases**](https://github.com/Stelliro/PuffinPyEditor/releases) page. The installer provides options for creating desktop and Start Menu shortcuts.

### Running from Source
To run the editor from the source code, you will need `Python 3` and `Git` installed on your system.

1.  **Clone the Repository:**
    ```bash
    git clone https://github.com/Stelliro/PuffinPyEditor.git
    cd PuffinPyEditor
    ```

2.  **Create and Activate a Virtual Environment:**
    ```bash
    # For Windows
    python -m venv venv
    .\venv\Scripts\activate

    # For macOS/Linux
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Run the Editor:**
    ```bash
    python main.py
    ```

## 📦 Creating a Windows Installer

A Windows installer can be created using the provided `build.bat` script. This process bundles the application into a standalone executable and then packages it into a themed, user-friendly setup file.

#### Prerequisites

1.  **NSIS:** You must have [NSIS (Nullsoft Scriptable Install System)](https://nsis.sourceforge.io/Download) installed. During installation, make sure to allow it to be added to your system's PATH.
2.  **Project Dependencies:** Ensure you have installed all the project's Python dependencies by running `pip install -r requirements.txt`.

#### Build Steps

1.  Open a command prompt in the root directory of the project.
2.  Run the build script:
    ```bash
    .\installer\build.bat
    ```
3.  The script will:
    *   Verify that `pyinstaller` and `makensis` are available.
    *   Run PyInstaller to bundle the application into the `/dist/PuffinPyEditor` directory.
    *   Run NSIS to compile the installer using the script and assets in the `/installer` directory.
4.  Once complete, the final setup file (e.g., `PuffinPyEditor_v1.2.0_Setup.exe`) will be located in the `/dist` directory.

## 🔒 Security & Privacy

**Important:** The editor stores your personal settings, including your GitHub access token and AI Export loadouts, in a file named `puffin_editor_settings.json` in the project's root directory.

*   This file is **automatically ignored by Git** thanks to the `.gitignore` file. You should **never** commit this file to a public repository.
*   The "Export for AI" and "Create Release" tools are also configured to **exclude** this file automatically.
*   Always be mindful not to hard-code sensitive information like passwords or API keys directly into your source code.

## 🧩 The Plugin System

PuffinPyEditor can be extended with custom plugins located in the `/plugins` directory.

**🔒 Security Warning:** Plugins are powerful and execute with the same permissions as the editor itself. For your security, **only install plugins from authors and sources you trust.** PuffinPyEditor cannot vet the safety or integrity of third-party plugins.

#### For Users
You can install new plugins easily:
1.  Navigate to `File > Preferences > Plugins`.
2.  **From GitHub:** Enter a repository URL (like `Stelliro/puffin-plugins`) and click "Fetch" to see a list of available plugins.
3.  **From a File:** Click "Install from File..." to upload a `.zip` archive of a plugin.
4.  After installation, a restart will be required to load the new plugin.

#### For Developers
Creating a plugin is simple. Each plugin lives in its own subdirectory inside `/plugins` and must contain two files:
1.  **`plugin.json`**: A manifest file describing your plugin.
    ```json
    {
        "name": "My Awesome Plugin",
        "author": "Your Name",
        "version": "1.0.0",
        "description": "This plugin does awesome things.",
        "entry_point": "plugin_main.py"
    }
    ```
2.  **`plugin_main.py`** (or your specified `entry_point`): The Python file with your plugin's logic. It must contain an `initialize(main_window)` function.
    ```python
    from PyQt6.QtGui import QAction
    
    def initialize(main_window):
        # main_window is an instance of the MainWindow class
        action = QAction("Do Awesome Thing", main_window)
        action.triggered.connect(lambda: print("Awesome thing done!"))
        
        # You can access existing menus or create new ones
        main_window.tools_menu.addAction(action)

        # The function should return the plugin instance if it needs to persist
        return None 
    ```

## 🤝 Contributing
Contributions are welcome! Whether it's reporting a bug, suggesting a new feature, or submitting a pull request, your help is appreciated. Please feel free to open an issue to discuss your ideas.

## 📜 License
This project is licensed under the **Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License**.

In short, you are free to share and adapt the material for **non-commercial purposes**, as long as you give appropriate credit and distribute your contributions under the same license. For the full license text, please see the `LICENSE.md` file.

# PuffinPyEditor Plugin Distribution Repository
This repository is structured to serve plugins for the PuffinPyEditor.
- `index.json`: A manifest file listing all available plugins and their download URLs.
- `zips/`: This directory contains the packaged `.zip` files for each plugin.
To publish a new version of a plugin, use the "Publish Plugin" tool inside PuffinPyEditor.

```

### File: `/LICENSE.md`
```md
## License

This project is licensed under the **Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License (CC BY-NC-SA 4.0)**.

**You are free to:**

*   **Share** — copy and redistribute the material in any medium or format.
*   **Adapt** — remix, transform, and build upon the material.

The licensor cannot revoke these freedoms as long as you follow the license terms.

**Under the following terms:**

*   **Attribution (BY)** — You must give appropriate credit. A good way to do this is by mentioning "stelliro" as the original envisioner and crediting the development team, including **Google Gemini** for AI-assisted code generation and **[ENVIXITY-8-5-3](https://github.com/ENVIXITY-8-5-3)** for their contributions. Please also provide a link to the license and indicate if changes were made. You may do so in any reasonable manner, but not in any way that suggests the licensor endorses you or your use.
*   **NonCommercial (NC)** — **You may not use the material for commercial purposes.** This means you are not permitted to use this code, or any derivative works based on this code, for direct or indirect financial gain. This includes, but is not limited to:
    *   Selling the software or access to it.
    *   Using the software as part of a paid service or product.
    *   Integrating the software into a product that is sold or monetized.
    *   Using the software to generate revenue through advertising or other means.
*   **ShareAlike (SA)** — If you remix, transform, or build upon the material, you must distribute your contributions under the same license as the original.

**No additional restrictions** — You may not apply legal terms or technological measures that legally restrict others from doing anything the license permits.

For the full license text, please see the [LICENSE.md](LICENSE.md) file or visit:
[https://creativecommons.org/licenses/by-nc-sa/4.0/](https://creativecommons.org/licenses/by-nc-sa/4.0/)

**In simpler terms: This code is shared for personal, educational, and non-profit community use. It is not to be used to make profit.**

```

### File: `/utils/versioning.py`
```py
# PuffinPyEditor/utils/versioning.py
import os
from packaging import version
from .logger import log
from .helpers import get_base_path

# This will now correctly find the project root whether running from source or frozen.
ROOT_DIR = get_base_path()
VERSION_FILE_PATH = os.path.join(ROOT_DIR, "VERSION.txt")


def get_current_version() -> str:
    """
    Reads the version from the VERSION.txt file.

    Returns:
        The version string or '0.0.0' if the file is not found or invalid.
    """
    try:
        with open(VERSION_FILE_PATH, 'r', encoding='utf-8') as f:
            v_str = f.read().strip()
            # Ensure it's a valid version format before returning
            version.parse(v_str)
            return v_str
    except FileNotFoundError:
        log.error(f"VERSION.txt not found at: {VERSION_FILE_PATH}")
        return "0.0.0"
    except (version.InvalidVersion, ValueError, IOError) as e:
        log.error(f"Could not read or parse VERSION.txt: {e}")
        return "0.0.0"


def suggest_next_version() -> str:
    """
    Reads the current version and suggests the next patch version.
    e.g., "1.2.0" -> "v1.2.1", "1.3.5-alpha" -> "v1.3.5"

    Returns:
        The suggested next version string, prefixed with 'v'.
    """
    current_v_str = get_current_version()
    try:
        v = version.parse(current_v_str)
        # If it's a pre-release, suggest the final version of that number
        if v.is_prerelease:
            return f"v{v.base_version}"

        # Otherwise, increment the patch number
        major, minor, micro = v.major, v.minor, v.micro
        return f"v{major}.{minor}.{micro + 1}"

    except version.InvalidVersion:
        return "v1.0.0"


def write_new_version(new_version_string: str) -> bool:
    """
    Writes a new version string to the VERSION.txt file after validation.
    Strips any leading 'v' or whitespace.

    Args:
        new_version_string: The new version to write (e.g., "v1.2.1").

    Returns:
        True if the write was successful, False otherwise.
    """
    if not new_version_string:
        log.warning("Attempted to write an empty version string.")
        return False

    # Sanitize the version string
    clean_version = new_version_string.lstrip('v').strip()
    try:
        # Validate that it's a parseable version
        version.parse(clean_version)
        with open(VERSION_FILE_PATH, 'w', encoding='utf-8') as f:
            f.write(clean_version)
        log.info(f"Updated application version in VERSION.txt to: {clean_version}")
        # Update the global constant after a successful write
        global APP_VERSION
        APP_VERSION = clean_version
        return True
    except (version.InvalidVersion, IOError) as e:
        log.error(f"Failed to write new version '{clean_version}': {e}")
        return False


# A constant that can be easily imported elsewhere in the application
APP_VERSION = get_current_version()
```

### File: `/utils/validate_assets.py`
```py
# PuffinPyEditor/utils/validate_assets.py
import os
import json
import re
from typing import List, Dict, Any, Tuple

# --- Configuration ---
# Adjust these paths if your project structure changes
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
THEMES_DIR = os.path.join(ROOT_DIR, "assets", "themes")
CUSTOM_THEMES_FILE = os.path.join(THEMES_DIR, "custom_themes.json")
THEME_MANAGER_FILE = os.path.join(ROOT_DIR, "app_core", "theme_manager.py")


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'


def _print_header(title: str):
    print(f"\n{bcolors.HEADER}{bcolors.BOLD}===== {title.upper()} "
          f"====={bcolors.ENDC}")


def _load_json_file(filepath: str) -> Tuple[Any, List[str]]:
    """Loads a JSON file and returns its content and any errors found."""
    errors = []
    data = None
    if not os.path.exists(filepath):
        # This is not an error, the file might be optional
        return None, errors

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        err_msg = (f"Invalid JSON in '{os.path.basename(filepath)}':\n"
                   f"  {bcolors.FAIL}L{e.lineno}:C{e.colno} - {e.msg}"
                   f"{bcolors.ENDC}")
        errors.append(err_msg)
    except Exception as e:
        errors.append(f"Could not read '{os.path.basename(filepath)}': {e}")

    return data, errors


def validate_json_syntax() -> Tuple[Dict, List[str]]:
    """Checks basic JSON syntax of theme files."""
    _print_header("1. JSON Syntax Validation")

    all_themes = {}
    all_errors = []

    # Validate custom themes (if they exist)
    custom_data, errors = _load_json_file(CUSTOM_THEMES_FILE)
    all_errors.extend(errors)
    if custom_data:
        all_themes.update(custom_data)

    if not all_errors:
        print(f"{bcolors.OKGREEN}All theme files are valid JSON.{bcolors.ENDC}")

    return all_themes, all_errors


def get_required_color_keys_from_code(manager_file: str) -> set:
    """Extracts color keys from the QSS in theme_manager.py."""
    required_keys = set()
    if not os.path.exists(manager_file):
        return required_keys

    with open(manager_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # Regex to find all instances of c("some.key", ...)
    matches = re.findall(r'c\("([^"]+)"', content)
    for key in matches:
        required_keys.add(key)

    return required_keys


def validate_key_completeness(all_themes: Dict, required_keys: set) -> List[str]:
    """Checks if each theme defines all the keys required by the app."""
    _print_header("2. Color Key Completeness Validation")
    all_errors = []

    # Manually add keys for custom-painted widgets that are not discoverable
    # via the c() helper function in the main QSS.
    custom_painted_widget_keys = {
        "tree.indentationGuides.stroke", "tree.trace.color", "tree.trace.shadow",
        "tree.node.color", "tree.node.fill", "list.hoverBackground",
        "list.activeSelectionBackground", "list.activeSelectionForeground",
        "list.inactiveSelectionBackground", "list.inactiveSelectionForeground",
        "icon.foreground"
    }
    required_keys.update(custom_painted_widget_keys)

    if not required_keys:
        msg = (f"{bcolors.FAIL}Could not find required color keys "
               f"in ThemeManager. Check path.{bcolors.ENDC}")
        all_errors.append(msg)
        return all_errors

    print(f"Found {len(required_keys)} required color keys in the code.")

    for theme_id, theme_data in all_themes.items():
        theme_keys = set(theme_data.get("colors", {}).keys())
        missing_keys = required_keys - theme_keys

        if missing_keys:
            all_errors.append(
                f"Theme '{bcolors.BOLD}{theme_id}{bcolors.ENDC}' "
                f"is missing {len(missing_keys)} keys:"
            )
            for key in sorted(list(missing_keys)):
                all_errors.append(f"  - {bcolors.WARNING}{key}{bcolors.ENDC}")

    if not all_errors:
        print(f"{bcolors.OKGREEN}All themes have all required keys."
              f"{bcolors.ENDC}")

    return all_errors


def main():
    """Run all validation checks."""
    print(f"{bcolors.BOLD}Running PuffinPyEditor Asset Validator..."
          f"{bcolors.ENDC}")

    all_themes, errors = validate_json_syntax()
    if errors:
        for error in errors:
            print(f"- {error}")
        print(f"\n{bcolors.FAIL}{bcolors.BOLD}Validation failed at Step 1. "
              f"Cannot continue.{bcolors.ENDC}")
        return

    required_keys = get_required_color_keys_from_code(THEME_MANAGER_FILE)
    errors.extend(validate_key_completeness(all_themes, required_keys))

    _print_header("Validation Summary")
    if errors:
        print(f"\n{bcolors.FAIL}{bcolors.BOLD}Validation finished with "
              f"{len(errors)} issue(s). See details above.{bcolors.ENDC}")
        for error in errors:
            print(f"- {error}")
    else:
        print(f"{bcolors.OKGREEN}{bcolors.BOLD}"
              f"All assets validated successfully!{bcolors.ENDC}")


if __name__ == "__main__":
    main()
```

### File: `/utils/markdown_linter.py`
```py
# PuffinPyEditor/utils/markdown_linter.py
import re
from typing import List, Dict


def lint_markdown_file(content: str) -> List[Dict]:
    """
    Performs a basic lint on Markdown content to find common errors.

    Args:
        content: The string content of the Markdown file.

    Returns:
        A list of problem dictionaries, compatible with the ProblemsPanel.
    """
    problems = []
    # Regex to find three backticks, optional whitespace, a newline,
    # and then a language identifier on the next line.
    # This is a common error that breaks syntax highlighting.
    malformed_fence_regex = re.compile(r"^(```)\s*\n\s*(\S+)")

    for i, line in enumerate(content.splitlines()):
        # --- Rule 1: Malformed code fence ---
        match = malformed_fence_regex.match(line)
        if match:
            lang = match.group(2)
            # The error is on the line with the backticks.
            # We report it for the line number `i`.
            problems.append({
                'line': i + 1,
                'col': 1,
                'code': 'MD001',
                'description': f"Fenced code block language '{lang}' should be "
                               f"on the same line as the opening ```."
            })

    # Add more rules here in the future...

    return problems
```

### File: `/utils/logger.py`
```py
# PuffinPyEditor/utils/logger.py
import logging
import os
import platform
from logging.handlers import RotatingFileHandler

APP_NAME = "PuffinPyEditor"
ORG_NAME = "PuffinPyEditorProject"


def get_app_data_path() -> str:
    """
    Gets a cross-platform writable directory for application data.

    Returns:
        A string representing the path to the application data directory.
    """
    system = platform.system()
    if system == "Windows":
        # e.g., C:\Users\<user>\AppData\Local\PuffinPyEditorProject\...
        path = os.path.join(os.environ.get('LOCALAPPDATA', ''),
                            ORG_NAME, APP_NAME)
    elif system == "Darwin":  # macOS
        # e.g., /Users/<user>/Library/Application Support/PuffinPyEditorProject/...
        path = os.path.join(os.path.expanduser(
            '~/Library/Application Support'), ORG_NAME, APP_NAME)
    else:  # Linux and other systems
        # e.g., /home/<user>/.local/share/PuffinPyEditorProject/...
        path = os.path.join(os.path.expanduser('~/.local/share'),
                            ORG_NAME, APP_NAME)

    return path


# This will now be a path in the user's home directory, which is always writable.
APP_DATA_ROOT = get_app_data_path()
LOG_DIR = os.path.join(APP_DATA_ROOT, "logs")

# Use exist_ok=True for robustness. This creates the directory if it doesn't
# exist and does nothing if it already exists, preventing race conditions.
os.makedirs(LOG_DIR, exist_ok=True)

LOG_FILE = os.path.join(LOG_DIR, "app.log")


def setup_logger(name: str = "PuffinPyEditor",
                   log_level: int = logging.DEBUG) -> logging.Logger:
    """
    Configures and returns a logger instance.
    """
    logger = logging.getLogger(name)
    if logger.hasHandlers():
        logger.handlers.clear()

    logger.setLevel(log_level)

    formatter = logging.Formatter(
        "%(asctime)s - %(levelname)s - "
        "[%(module)s.%(funcName)s:%(lineno)d] - %(message)s"
    )

    # StreamHandler logs to the console
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)  # Console logs can be less verbose
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    # RotatingFileHandler logs to a file in the user-writable location
    try:
        fh = RotatingFileHandler(
            LOG_FILE, maxBytes=5*1024*1024, backupCount=5, encoding='utf-8'
        )
        fh.setLevel(log_level)  # File logs should be detailed
        fh.setFormatter(formatter)
        logger.addHandler(fh)
    except Exception as e:
        logger.error(
            f"Failed to create file handler for logging: {e}", exc_info=False
        )

    logger.info(f"Logger initialized. Log file at: {LOG_FILE}")
    return logger


# Global logger instance for the application
log = setup_logger()
```

### File: `/utils/log_viewer.py`
```py
# PuffinPyEditor/utils/log_viewer.py
import sys
import os
import re
from collections import deque
from PyQt6.QtWidgets import (QApplication, QMainWindow, QTextEdit, QVBoxLayout,
                             QWidget, QHBoxLayout, QPushButton, QCheckBox, QLabel,
                             QFileDialog, QMessageBox)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import QFileSystemWatcher, QTimer
import qtawesome as qta


class LogViewerWindow(QMainWindow):
    """A standalone app to view a log file in real-time with filtering."""

    def __init__(self, log_file_path):
        super().__init__()
        self.log_file_path = log_file_path
        self.last_pos = 0
        self.all_lines = []
        # Default to only showing ERROR and CRITICAL levels on startup
        self.active_levels = {'ERROR', 'CRITICAL'}
        self.level_pattern = re.compile(
            r" - (DEBUG|INFO|WARNING|ERROR|CRITICAL) - "
        )
        # Regex to find file paths like [module.function:lineno]
        self.file_path_pattern = re.compile(r"\[([a-zA-Z0-9_.-]+):[0-9]+\]")
        self.project_root = self._get_project_root()

        self.setWindowTitle(
            f"PuffinPy Log Viewer - {os.path.basename(log_file_path)}"
        )
        self.setMinimumSize(800, 500)
        self.setStyleSheet("background-color: #2D2A2E;")

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        layout = QVBoxLayout(self.central_widget)
        self._setup_controls(layout)

        self.text_edit = QTextEdit()
        self.text_edit.setReadOnly(True)
        self.text_edit.setFont(QFont("Consolas", 10))
        self.text_edit.setStyleSheet(
            "background-color: #1E1C21; color: #E0E0E0; "
            "border: none; padding: 5px;"
        )
        layout.addWidget(self.text_edit)

        # File watcher
        self.watcher = QFileSystemWatcher()
        self.watcher.fileChanged.connect(self._read_new_log_content)

        # Initial load is deferred to avoid blocking the UI
        QTimer.singleShot(50, self.perform_initial_load)

    def _get_project_root(self):
        """Determines the project's root directory for finding source files."""
        if getattr(sys, 'frozen', False):
            # In a bundled app, the root is the executable's directory
            return os.path.dirname(sys.executable)
        else:
            # In dev, it's two levels up from this file (utils/ -> project_root/)
            return os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

    def _setup_controls(self, parent_layout):
        controls_widget = QWidget()
        controls_layout = QHBoxLayout(controls_widget)
        controls_layout.setContentsMargins(5, 5, 5, 5)

        # Level Filters
        controls_layout.addWidget(QLabel("Show Levels:"))
        self.debug_check = self._create_filter_checkbox("DEBUG", False)
        self.info_check = self._create_filter_checkbox("INFO", False)
        self.warning_check = self._create_filter_checkbox("WARNING", False)
        self.error_check = self._create_filter_checkbox("ERROR", True)
        self.critical_check = self._create_filter_checkbox("CRITICAL", True)

        controls_layout.addWidget(self.debug_check)
        controls_layout.addWidget(self.info_check)
        controls_layout.addWidget(self.warning_check)
        controls_layout.addWidget(self.error_check)
        controls_layout.addWidget(self.critical_check)
        controls_layout.addStretch()

        # Other Controls
        self.autoscroll_check = QCheckBox("Auto-scroll")
        self.autoscroll_check.setChecked(True)
        clear_button = QPushButton("Clear")
        export_button = QPushButton("Export for AI")
        export_button.setIcon(qta.icon('fa5s.robot'))
        export_button.setToolTip(
            "Export visible logs and referenced source files for AI analysis."
        )

        controls_layout.addWidget(self.autoscroll_check)
        controls_layout.addWidget(clear_button)
        controls_layout.addWidget(export_button)
        parent_layout.addWidget(controls_widget)

        # Connect signals
        clear_button.clicked.connect(self.clear_log)
        export_button.clicked.connect(self._export_for_ai)

    def _create_filter_checkbox(self, text, default_checked=True):
        cb = QCheckBox(text)
        cb.setChecked(default_checked)
        cb.toggled.connect(
            lambda checked, lvl=text: self._on_filter_changed(checked, [lvl])
        )
        return cb

    def perform_initial_load(self):
        """Loads the initial view of the log file, tailing it for speed."""
        if not os.path.exists(self.log_file_path):
            self.text_edit.setText(
                f"Waiting for log file: {self.log_file_path}..."
            )
            if not self.watcher.files():
                self.watcher.addPath(self.log_file_path)
            return

        if not self.watcher.files():
            self.watcher.addPath(self.log_file_path)

        try:
            with open(self.log_file_path, 'r', encoding='utf-8') as f:
                tailed_lines = deque(f, 500)
                self.all_lines = list(tailed_lines)
                self.last_pos = f.tell()
                self._apply_filters_to_display()

            QTimer.singleShot(200, self._load_full_log)
        except Exception as e:
            self.text_edit.setText(f"Error loading log file: {e}")

    def _load_full_log(self):
        """Reads the entire log file into memory after startup."""
        try:
            with open(self.log_file_path, 'r', encoding='utf-8') as f:
                self.all_lines = f.readlines()
            self._apply_filters_to_display()
        except Exception as e:
            print(f"Error doing full log read: {e}")

    def _read_new_log_content(self):
        """Reads only the new content from the log file and appends it."""
        try:
            with open(self.log_file_path, 'r', encoding='utf-8') as f:
                current_size = f.seek(0, 2)
                if current_size < self.last_pos:
                    self.last_pos = 0  # Log file was likely cleared

                f.seek(self.last_pos)
                new_content = f.read()
                if new_content:
                    new_lines = new_content.strip().split('\n')
                    self.all_lines.extend(line + '\n' for line in new_lines)

                    visible_new_lines = self._filter_lines(new_lines)
                    if visible_new_lines:
                        cursor = self.text_edit.textCursor()
                        cursor.movePosition(cursor.MoveOperation.End)
                        self.text_edit.setTextCursor(cursor)
                        self.text_edit.insertPlainText(
                            "\n".join(visible_new_lines) + "\n"
                        )
                self.last_pos = f.tell()

            if self.autoscroll_check.isChecked():
                v_bar = self.text_edit.verticalScrollBar()
                v_bar.setValue(v_bar.maximum())
        except Exception as e:
            print(f"Error updating log: {e}")
            self.last_pos = 0

    def _on_filter_changed(self, checked, levels):
        """Updates the active levels set and reapplies the filter."""
        for level in levels:
            if checked:
                self.active_levels.add(level)
            else:
                self.active_levels.discard(level)
        self._apply_filters_to_display()

    def _get_line_level(self, line: str):
        match = self.level_pattern.search(line)
        return match.group(1) if match else None

    def _filter_lines(self, lines: list[str]) -> list[str]:
        visible = []
        for line in lines:
            level = self._get_line_level(line)
            if level is None or level in self.active_levels:
                visible.append(line.strip())
        return visible

    def _apply_filters_to_display(self):
        visible_lines = self._filter_lines(self.all_lines)
        self.text_edit.setText("\n".join(visible_lines))
        if self.autoscroll_check.isChecked():
            v_bar = self.text_edit.verticalScrollBar()
            v_bar.setValue(v_bar.maximum())

    def _export_for_ai(self):
        """Gathers visible logs and associated source files for AI analysis."""
        visible_log_content = self.text_edit.toPlainText()
        if not visible_log_content.strip():
            QMessageBox.warning(self, "Empty Log",
                                "There is no visible log content to export.")
            return

        # Find unique source files mentioned in the logs
        files_to_include = set()
        for match in self.file_path_pattern.finditer(visible_log_content):
            module_path = match.group(1)
            # Convert module path (e.g., app_core.logger) to file path
            file_path = os.path.join(self.project_root, *module_path.split('.'))
            file_path += ".py"
            if os.path.exists(file_path):
                files_to_include.add(os.path.normpath(file_path))

        sugg_path = os.path.join(os.path.expanduser("~"), "puffin_debug_export.md")
        filepath, _ = QFileDialog.getSaveFileName(
            self, "Save Debug Export", sugg_path, "Markdown Files (*.md)"
        )
        if not filepath:
            return

        export_content = [
            "# PuffinPyEditor Debugging Export", "## AI Instructions",
            "Analyze the following log output and the associated source code "
            "files to identify the root cause of the error. Provide a "
            "detailed explanation and a suggested fix.", "---",
            "## Visible Log Output", "```log", visible_log_content, "```",
            "---", "## Included File Contents"
        ]

        for source_file in sorted(list(files_to_include)):
            rel_path = os.path.relpath(
                source_file, self.project_root
            ).replace(os.sep, '/')
            export_content.append(f"\n### File: `{rel_path}`\n")
            export_content.append("```python")
            try:
                with open(source_file, 'r', encoding='utf-8') as f:
                    export_content.append(f.read())
            except Exception as e:
                export_content.append(f"# Error reading file: {e}")
            export_content.append("```")

        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write("\n".join(export_content))
            QMessageBox.information(
                self, "Export Complete",
                f"Debug information successfully exported to:\n{filepath}"
            )
        except IOError as e:
            QMessageBox.critical(self, "Export Failed",
                                 f"Could not write to file: {e}")

    def clear_log(self):
        self.text_edit.clear()
        self.all_lines = []
        self.last_pos = 0
        if os.path.exists(self.log_file_path):
            try:
                open(self.log_file_path, 'w').close()
            except IOError as e:
                print(f"Could not clear log file on disk: {e}")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    if len(sys.argv) < 2:
        dummy_log_path = os.path.join(os.getcwd(), "dummy_app.log")
        if not os.path.exists(dummy_log_path):
            with open(dummy_log_path, 'w') as f:
                f.write("2025-01-01 12:00:00,000 - INFO - "
                        "[test.main:1] - This is a dummy log file.\n")
        log_path = dummy_log_path
    else:
        log_path = sys.argv[1]

    viewer = LogViewerWindow(log_path)
    viewer.show()
    sys.exit(app.exec())
```

### File: `/utils/helpers.py`
```py
# PuffinPyEditor/utils/helpers.py
import sys
import os
import re
import difflib
import hashlib
from typing import List, Optional
from PyQt6.QtGui import QFontDatabase
from .logger import log, get_app_data_path

if sys.platform == "win32":
    try:
        import winshell
    except ImportError:
        winshell = None
        log.warning("The 'winshell' package is not installed. Startup shortcut features will be disabled.")


def get_base_path():
    """
    Returns the application's base path for resource loading.

    This handles the difference between running from source and a frozen
    (e.g., PyInstaller) executable. For a frozen app, this is the directory
    of the executable. For a source app, this is the project root.
    """
    if getattr(sys, 'frozen', False):
        # The application is frozen
        return os.path.dirname(sys.executable)
    else:
        # Assumes this file is in /utils, so two levels up is the project root
        return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# --- NEW: Session/Draft Management Helpers ---
def get_session_path() -> str:
    """Returns the path to the session data directory, creating it if needed."""
    session_dir = os.path.join(get_app_data_path(), "session_data", "drafts")
    os.makedirs(session_dir, exist_ok=True)
    return session_dir

def get_draft_path(original_filepath: str) -> str:
    """Generates a consistent, safe filename for a draft file."""
    # Hash the full, absolute path to ensure uniqueness
    path_hash = hashlib.sha256(original_filepath.encode('utf-8')).hexdigest()
    return os.path.join(get_session_path(), f"{path_hash}.draft")
# --- End of New Helpers ---


def clean_git_conflict_markers(content: str) -> str:
    """Removes Git conflict markers from a string, keeping the HEAD version."""
    if '<<<<<<<' not in content:
        return content

    lines = content.splitlines()
    cleaned_lines = []
    in_conflict = False
    # We want to keep the HEAD version, which is the part before '======='
    keep_current_version = True

    for line in lines:
        if line.startswith('<<<<<<<'):
            in_conflict = True
            keep_current_version = True
            continue

        if line.startswith('======='):
            if in_conflict:
                keep_current_version = False
                continue

        if line.startswith('>>>>>>>'):
            if in_conflict:
                in_conflict = False
                keep_current_version = False
                continue

        if not in_conflict or (in_conflict and keep_current_version):
            cleaned_lines.append(line)

    return "\n".join(cleaned_lines)


def generate_unified_diff(original_content: str, new_content: str, fromfile='original', tofile='new') -> str:
    """Generates a git-style unified diff string."""
    original_lines = original_content.splitlines(keepends=True)
    new_lines = new_content.splitlines(keepends=True)
    diff = difflib.unified_diff(original_lines, new_lines, fromfile=fromfile, tofile=tofile)
    return "".join(diff)


def get_startup_shortcut_path() -> Optional[str]:
    """
    Gets the cross-platform path to the user's startup folder.

    This is used for creating a shortcut to launch the app on system startup.
    Returns None if the platform is not supported (currently only Windows).
    """
    if sys.platform == "win32":
        try:
            startup_folder = winshell.folder("startup")
            return os.path.join(startup_folder, "PuffinPyEditor.lnk")
        except Exception as e:
            log.error(f"Could not get Windows startup folder path: {e}")
            return None
    return None


def get_best_available_font(preferred_list: List[str]) -> Optional[str]:
    """
    Scans a preferred list of font families and returns the first one found
    on the user's system.

    This is useful for setting sensible default fonts for different themes
    or operating systems.

    Args:
        preferred_list: A list of font family names, in order of preference.

    Returns:
        The name of the first available font, or None if none are found.
    """
    if not isinstance(preferred_list, list):
        log.warning(
            f"Font list provided is not a list: {preferred_list}. "
            "No font selected."
        )
        return None

    font_db = QFontDatabase()
    installed_fonts = {font.lower() for font in font_db.families()}

    for font_name in preferred_list:
        if font_name.lower() in installed_fonts:
            log.info(f"Font suggestion: Found '{font_name}' installed on system.")
            return font_name

    log.warning(
        f"Could not find any of the preferred fonts: {preferred_list}. "
        "The application will use a system default."
    )
    return None
```

### File: `/utils/__init__.py`
```py

```

### File: `/ui/preferences_dialog.py`
```py
# PuffinPyEditor/ui/preferences_dialog.py
import uuid
import sys
import os
import tempfile
import requests
from typing import Optional, Any, TYPE_CHECKING
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QTabWidget,
                             QWidget, QLabel, QComboBox, QSpinBox, QCheckBox,
                             QPushButton, QLineEdit, QDialogButtonBox,
                             QFontComboBox, QSplitter, QFormLayout,
                             QListWidget, QListWidgetItem, QMessageBox,
                             QGroupBox, QFileDialog, QInputDialog,
                             QStackedWidget)
from PyQt6.QtGui import QFont, QDesktopServices, QColor
from PyQt6.QtCore import Qt, QSize, pyqtSignal, QUrl

from utils.logger import log

if sys.platform == "win32":
    try:
        import winshell
    except ImportError:
        winshell = None
        log.warning("The 'winshell' package is not installed. Startup shortcut features will be disabled.")

import qtawesome as qta
from utils.helpers import get_startup_shortcut_path
from app_core.settings_manager import settings_manager
from app_core.github_manager import GitHubManager
from app_core.source_control_manager import SourceControlManager
from app_core.plugin_manager import PluginManager, Plugin
from app_core.puffin_api import PuffinPluginAPI

if TYPE_CHECKING:
    from app_core.theme_manager import ThemeManager


class AuthDialog(QDialog):
    def __init__(self, user_code: str, verification_uri: str,
                 parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setWindowTitle("GitHub Device Authorization")
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Please authorize PuffinPyEditor in your browser."))
        url_label = QLabel(f"1. Open: <a href='{verification_uri}'>{verification_uri}</a>")
        url_label.setOpenExternalLinks(True)
        layout.addWidget(url_label)
        layout.addWidget(QLabel("2. Enter this one-time code:"))
        code_label = QLineEdit(user_code)
        code_label.setReadOnly(True)
        code_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        code_label.setFont(QFont("Consolas", 14, QFont.Weight.Bold))
        layout.addWidget(code_label)
        QDesktopServices.openUrl(QUrl(verification_uri))
        self.setFixedSize(self.sizeHint())


class PreferencesDialog(QDialog):
    settings_changed_for_editor_refresh = pyqtSignal()
    theme_changed_signal = pyqtSignal(str)

    def __init__(self, theme_manager: 'ThemeManager', git_manager: SourceControlManager,
                 github_manager: GitHubManager, plugin_manager: PluginManager,
                 puffin_api: PuffinPluginAPI,
                 parent: Optional[QWidget] = None):
        super().__init__(parent)
        log.info("PreferencesDialog initializing...")
        self.setWindowTitle("Preferences")
        self.setMinimumSize(QSize(850, 700))
        self.theme_manager = theme_manager
        self.git_manager = git_manager
        self.github_manager = github_manager
        self.plugin_manager = plugin_manager
        self.puffin_api = puffin_api

        self.original_settings: dict[str, Any] = {}
        self.original_git_config: dict[str, str] = {}
        self.staged_repos: list[dict] = []
        self.staged_active_repo_id: Optional[str] = None
        self.current_repo_id_in_form: Optional[str] = None
        self.auth_dialog: Optional[AuthDialog] = None
        self.restart_needed = False
        self.is_loading = False
        self.main_layout = QVBoxLayout(self)
        self.tab_widget = QTabWidget()
        self.main_layout.addWidget(self.tab_widget)
        self._create_tabs()
        self._create_button_box()
        self._connect_global_signals()
        self._connect_ui_changed_signals()
        log.info("PreferencesDialog initialized.")

    def _create_tabs(self):
        self._create_appearance_tab()
        self._create_editor_tab()
        self._create_run_tab()
        self._create_system_tab()
        self._create_source_control_tab()
        self._create_plugins_tab()

    def _create_button_box(self):
        buttons = (
                QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel | QDialogButtonBox.StandardButton.Apply)
        self.button_box = QDialogButtonBox(buttons)
        self.main_layout.addWidget(self.button_box)

    def _connect_global_signals(self):
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        self.button_box.button(QDialogButtonBox.StandardButton.Apply).clicked.connect(self.apply_settings)
        self.git_manager.git_config_ready.connect(self._populate_git_config_fields)
        self.github_manager.device_code_ready.connect(self._on_device_code_ready)
        self.github_manager.auth_successful.connect(self._on_auth_successful)
        self.github_manager.auth_failed.connect(self._on_auth_failed)
        self.github_manager.auth_polling_lapsed.connect(self._on_auth_polling_lapsed)
        self.github_manager.operation_success.connect(self._handle_github_op_success)
        self.github_manager.plugin_index_ready.connect(self._on_plugin_index_ready)
        self.git_manager.git_success.connect(self._handle_git_success)

    def _handle_github_op_success(self, message, data):
        if "Repository" in message and "created" in message:
            new_repo_id = str(uuid.uuid4())
            owner, repo_name = self.git_manager.parse_git_url(data.get("clone_url"))
            new_repo = {"id": new_repo_id, "name": data.get("name"), "owner": owner, "repo": repo_name}
            self.staged_repos.append(new_repo)
            QMessageBox.information(self, "Success", f"Repository '{repo_name}' created on GitHub.")
            self._populate_repo_list(select_repo_id=new_repo_id)
            self._on_ui_setting_changed()

    def showEvent(self, event):
        self.is_loading = True
        self._load_settings_into_dialog()
        self.git_manager.get_git_config()
        self._update_auth_status()
        self._populate_all_plugin_lists()
        self.button_box.button(QDialogButtonBox.StandardButton.Apply).setEnabled(False)
        self.restart_needed = False
        super().showEvent(event)
        self.is_loading = False

    def _load_settings_into_dialog(self):
        self.original_settings = settings_manager.settings.copy()
        self._repopulate_theme_combo()
        self.font_family_combo.setCurrentFont(QFont(settings_manager.get("font_family")))
        self.font_size_spinbox.setValue(settings_manager.get("font_size"))
        self.show_line_numbers_checkbox.setChecked(settings_manager.get("show_line_numbers"))
        self.word_wrap_checkbox.setChecked(settings_manager.get("word_wrap"))
        self.show_indent_guides_checkbox.setChecked(settings_manager.get("show_indentation_guides"))
        self.indent_style_combo.setCurrentText(settings_manager.get("indent_style").capitalize())
        self.indent_width_spinbox.setValue(settings_manager.get("indent_width"))
        self.auto_save_checkbox.setChecked(settings_manager.get("auto_save_enabled"))
        self.auto_save_delay_spinbox.setValue(settings_manager.get("auto_save_delay_seconds"))
        self.max_recent_files_spinbox.setValue(settings_manager.get("max_recent_files"))
        self.python_path_edit.setText(settings_manager.get("python_interpreter_path", ""))
        if sys.platform == "win32":
            self.nsis_path_edit.setText(settings_manager.get("nsis_path", ""))
            self.cleanup_build_checkbox.setChecked(settings_manager.get("cleanup_after_build", True))
            if winshell and hasattr(self, 'run_in_background_checkbox'): self.run_in_background_checkbox.setChecked(
                settings_manager.get("run_in_background", False))

        self.staged_repos = [r.copy() for r in settings_manager.get("source_control_repos", [])]
        self.staged_active_repo_id = settings_manager.get("active_update_repo_id")
        self._populate_repo_list()
        self.plugins_repo_edit.setText(settings_manager.get("plugins_distro_repo", "Stelliro/puffin-plugins"))

    def _connect_ui_changed_signals(self):
        for w in self.findChildren((QComboBox, QSpinBox, QCheckBox, QFontComboBox, QLineEdit)):
            if isinstance(w, QComboBox):
                w.currentIndexChanged.connect(self._on_ui_setting_changed)
            elif isinstance(w, QFontComboBox):
                w.currentFontChanged.connect(self._on_ui_setting_changed)
            elif isinstance(w, QSpinBox):
                w.valueChanged.connect(self._on_ui_setting_changed)
            elif isinstance(w, QCheckBox):
                w.stateChanged.connect(self._on_ui_setting_changed)
            elif isinstance(w, QLineEdit):
                w.textChanged.connect(self._on_ui_setting_changed)

    def _on_ui_setting_changed(self, *args):
        if not self.is_loading and self.isVisible(): self.button_box.button(
            QDialogButtonBox.StandardButton.Apply).setEnabled(True)

    def apply_settings(self):
        ab = self.button_box.button(QDialogButtonBox.StandardButton.Apply)
        if not ab.isEnabled(): return

        ss = {
            "last_theme_id": self.theme_combo.currentData(),
            "font_family": self.font_family_combo.currentFont().family(),
            "font_size": self.font_size_spinbox.value(),
            "show_line_numbers": self.show_line_numbers_checkbox.isChecked(),
            "word_wrap": self.word_wrap_checkbox.isChecked(),
            "show_indentation_guides": self.show_indent_guides_checkbox.isChecked(),
            "indent_style": self.indent_style_combo.currentText().lower(),
            "indent_width": self.indent_width_spinbox.value(),
            "auto_save_enabled": self.auto_save_checkbox.isChecked(),
            "auto_save_delay_seconds": self.auto_save_delay_spinbox.value(),
            "max_recent_files": self.max_recent_files_spinbox.value(),
            "python_interpreter_path": self.python_path_edit.text().strip(),
            "source_control_repos": self.staged_repos,
            "active_update_repo_id": self.staged_active_repo_id,
            "plugins_distro_repo": self.plugins_repo_edit.text().strip(),
        }

        if sys.platform == "win32":
            ss["nsis_path"] = self.nsis_path_edit.text().strip()
            ss["cleanup_after_build"] = self.cleanup_build_checkbox.isChecked()
            if winshell and hasattr(self, 'run_in_background_checkbox'):
                ss["run_in_background"] = self.run_in_background_checkbox.isChecked()
                if ss["run_in_background"] != self.original_settings.get("run_in_background", False):
                    self._manage_startup_shortcut(ss["run_in_background"])

        nn, ne = self.git_user_name_edit.text().strip(), self.git_user_email_edit.text().strip()
        if nn != self.original_git_config.get('name') or ne != self.original_git_config.get('email'):
            self.git_manager.set_git_config(nn, ne)
            self.original_git_config = {'name': nn, 'email': ne}

        self._save_repo_form_to_staged()

        for k, v in ss.items(): settings_manager.set(k, v, False)
        settings_manager.save()
        self.theme_changed_signal.emit(self.theme_combo.currentData())
        self.settings_changed_for_editor_refresh.emit()
        self.original_settings = settings_manager.settings.copy()
        ab.setEnabled(False)
        if self.restart_needed: QMessageBox.information(self, "Restart Required", "Some changes require a restart.")
        self.restart_needed = False
        log.info("Applied settings.")

    def accept(self):
        if self.button_box.button(QDialogButtonBox.StandardButton.Apply).isEnabled(): self.apply_settings()
        super().accept()

    def reject(self):
        if self.auth_dialog and self.auth_dialog.isVisible(): self.auth_dialog.reject()
        if self.button_box.button(QDialogButtonBox.StandardButton.Apply).isEnabled():
            if QMessageBox.question(self, "Unsaved Changes", "Discard?",
                                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No) == QMessageBox.StandardButton.No: return
        if self.theme_combo.currentData() != self.original_settings.get("last_theme_id"):
            self.theme_changed_signal.emit(self.original_settings.get("last_theme_id"))
        super().reject()

    def _create_layout_in_groupbox(self, t, pl):
        g = QGroupBox(t)
        pl.addWidget(g)
        l = QFormLayout(g)
        return l

    def _create_appearance_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(15)
        theme_group = self._create_layout_in_groupbox("Theming", layout)
        self.theme_combo = QComboBox()
        self.edit_themes_button = QPushButton("Customize Themes...")
        self.connect_theme_editor_button()
        theme_group.addRow("Theme:", self.theme_combo)
        theme_group.addRow("", self.edit_themes_button)
        font_group = self._create_layout_in_groupbox("Editor Font", layout)
        self.font_family_combo = QFontComboBox()
        self.font_size_spinbox = QSpinBox()
        self.font_size_spinbox.setRange(6, 72)
        font_group.addRow("Font Family:", self.font_family_combo)
        font_group.addRow("Font Size:", self.font_size_spinbox)
        layout.addStretch()
        self.tab_widget.addTab(tab, qta.icon('fa5s.palette'), "Appearance")

    def _repopulate_theme_combo(self):
        current_id = self.original_settings.get("last_theme_id", "puffin_dark")
        self.theme_combo.blockSignals(True)
        self.theme_combo.clear()
        for theme_id, name in self.theme_manager.get_available_themes_for_ui().items():
            self.theme_combo.addItem(name, theme_id)
        if (index := self.theme_combo.findData(current_id)) != -1: self.theme_combo.setCurrentIndex(index)
        self.theme_combo.blockSignals(False)

    def connect_theme_editor_button(self):
        if self.puffin_api.theme_editor_launcher:
            try:
                self.edit_themes_button.clicked.disconnect()
            except TypeError:
                pass
            self.edit_themes_button.clicked.connect(self.puffin_api.theme_editor_launcher)
            if theme_editor_instance := self.puffin_api.get_plugin_instance('theme_editor'):
                if dialog := getattr(theme_editor_instance, 'dialog_instance', None):
                    if hasattr(dialog, 'custom_themes_changed'):
                        dialog.custom_themes_changed.connect(self._repopulate_theme_combo)
            self.edit_themes_button.show()
        else:
            self.edit_themes_button.hide()

    def _create_editor_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(15)
        display_layout = self._create_layout_in_groupbox("Display", layout)
        display_layout.setRowWrapPolicy(QFormLayout.RowWrapPolicy.WrapAllRows)
        self.show_line_numbers_checkbox = QCheckBox("Show line numbers")
        self.word_wrap_checkbox = QCheckBox("Enable word wrap")
        self.show_indent_guides_checkbox = QCheckBox("Show indentation guides")
        display_layout.addRow(self.show_line_numbers_checkbox)
        display_layout.addRow(self.word_wrap_checkbox)
        display_layout.addRow(self.show_indent_guides_checkbox)
        indent_layout = self._create_layout_in_groupbox("Indentation", layout)
        self.indent_style_combo = QComboBox()
        self.indent_style_combo.addItems(["Spaces", "Tabs"])
        self.indent_width_spinbox = QSpinBox()
        self.indent_width_spinbox.setRange(1, 16)
        indent_layout.addRow("Indent Using:", self.indent_style_combo)
        indent_layout.addRow("Indent/Tab Width:", self.indent_width_spinbox)
        file_layout = self._create_layout_in_groupbox("File Handling", layout)
        self.auto_save_checkbox = QCheckBox("Enable auto-save")
        self.auto_save_delay_spinbox = QSpinBox()
        self.auto_save_delay_spinbox.setRange(1, 60)
        self.auto_save_delay_spinbox.setSuffix(" seconds")
        self.max_recent_files_spinbox = QSpinBox()
        self.max_recent_files_spinbox.setRange(1, 50)
        file_layout.addRow(self.auto_save_checkbox)
        file_layout.addRow("Auto-Save Delay:", self.auto_save_delay_spinbox)
        file_layout.addRow("Max Recent Files:", self.max_recent_files_spinbox)
        layout.addStretch()
        self.tab_widget.addTab(tab, qta.icon('fa5s.edit'), "Editor")

    def _create_run_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(15)
        py_group = self._create_layout_in_groupbox("Python Interpreter", layout)
        py_path_layout = QHBoxLayout()
        self.python_path_edit = QLineEdit()
        self.python_path_edit.setPlaceholderText("Leave empty to use system default")
        browse_py_button = QPushButton("Browse...")
        browse_py_button.clicked.connect(self._browse_for_python)
        py_path_layout.addWidget(self.python_path_edit)
        py_path_layout.addWidget(browse_py_button)
        py_group.addRow("Python Executable Path:", py_path_layout)
        build_group = self._create_layout_in_groupbox("Build & Installation (Windows Only)", layout)
        if sys.platform == "win32":
            nsis_path_layout = QHBoxLayout()
            self.nsis_path_edit = QLineEdit()
            self.nsis_path_edit.setPlaceholderText("e.g., C:\\Program Files (x86)\\NSIS\\makensis.exe")
            browse_nsis_button = QPushButton("Browse...")
            browse_nsis_button.clicked.connect(self._browse_for_nsis)
            nsis_path_layout.addWidget(self.nsis_path_edit)
            nsis_path_layout.addWidget(browse_nsis_button)
            self.cleanup_build_checkbox = QCheckBox("Delete temporary build files after install")
            build_group.addRow("NSIS Path (for Installer):", nsis_path_layout)
            build_group.addRow("", self.cleanup_build_checkbox)
        else:
            build_group.addRow(QLabel("Build options are only available on Windows."))
        layout.addStretch()
        self.tab_widget.addTab(tab, qta.icon('fa5s.play-circle'), "Execution")

    def _browse_for_nsis(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select NSIS Executable", "", "NSIS (makensis.exe);;All Files (*)")
        if path: self.nsis_path_edit.setText(path)

    def _browse_for_python(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select Python Executable", "",
                                              "Python Executable (python.exe; python);;All Files (*)")
        if path: self.python_path_edit.setText(path)

    def _create_system_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(15)
        startup_group = self._create_layout_in_groupbox("System Startup", layout)
        if sys.platform == "win32" and winshell:
            self.run_in_background_checkbox = QCheckBox(
                "Launch PuffinPyEditor on system startup (runs in system tray)")
            self.run_in_background_checkbox.setToolTip(
                "Creates a shortcut in the Windows Startup folder.")
            startup_group.addRow(
                self.run_in_background_checkbox)
        else:
            startup_group.addRow(QLabel("Startup options are only available on Windows."))
        layout.addStretch()
        self.tab_widget.addTab(tab, qta.icon('fa5s.desktop'), "System")

    def _manage_startup_shortcut(self, create):
        if not winshell: return
        shortcut_path = get_startup_shortcut_path()
        if not shortcut_path: return
        try:
            if create and not os.path.exists(shortcut_path):
                tray_exe_path = os.path.join(os.path.dirname(sys.executable), "PuffinPyTray.exe")
                if not os.path.exists(tray_exe_path): raise FileNotFoundError("PuffinPyTray.exe not found.")
                winshell.CreateShortcut(Path=shortcut_path, Target=tray_exe_path)
            elif not create and os.path.exists(shortcut_path):
                os.remove(shortcut_path)
        except Exception as e:
            QMessageBox.critical(self, "Shortcut Error", f"Could not manage startup shortcut:\n{e}")

    def _create_source_control_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(15)
        git_user_group = self._create_layout_in_groupbox("Git Identity", layout)
        self.git_user_name_edit = QLineEdit()
        self.git_user_email_edit = QLineEdit()

        sync_button = QPushButton("Sync with GitHub")
        sync_button.setObjectName("syncWithGitHubButton")
        sync_button.clicked.connect(self._sync_git_with_github)

        git_user_group.addRow("Username:", self.git_user_name_edit)
        git_user_group.addRow("Email:", self.git_user_email_edit)
        git_user_group.addRow(sync_button)

        gh_auth_group = self._create_layout_in_groupbox("GitHub Integration", layout)
        self.auth_status_label = QLabel("<i>Checking status...</i>")
        self.auth_button = QPushButton("Log in to GitHub")
        self.auth_button.clicked.connect(self.github_manager.start_device_flow)
        self.logout_button = QPushButton("Log out")
        self.logout_button.clicked.connect(self._logout_github)
        gh_auth_group.addRow(self.auth_status_label)
        gh_auth_group.addRow(self.auth_button)
        gh_auth_group.addRow(self.logout_button)

        repo_group = self._create_layout_in_groupbox("Update Repository Management", layout)
        repo_splitter, _ = self._create_repo_management_widgets()
        repo_group.layout().addWidget(repo_splitter)
        layout.addStretch()
        self.tab_widget.addTab(tab, qta.icon('fa5b.git-alt'), "Source Control")

    def _create_repo_management_widgets(self):
        splitter = QSplitter()
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.addWidget(QLabel("Repositories:"))
        self.repo_list = QListWidget()
        self.repo_list.currentItemChanged.connect(self._on_repo_selection_changed)
        left_layout.addWidget(self.repo_list)
        repo_buttons = QHBoxLayout()
        add_repo_btn = QPushButton()
        add_repo_btn.setIcon(qta.icon('fa5s.plus'))
        remove_repo_btn = QPushButton()
        remove_repo_btn.setIcon(qta.icon('fa5s.minus'))
        add_repo_btn.clicked.connect(self._action_add_repo)
        remove_repo_btn.clicked.connect(self._action_remove_repo)
        repo_buttons.addStretch()
        repo_buttons.addWidget(add_repo_btn)
        repo_buttons.addWidget(remove_repo_btn)
        left_layout.addLayout(repo_buttons)
        splitter.addWidget(left_widget)
        form_widget = QWidget()
        form_layout = QFormLayout(form_widget)
        self.repo_name_edit = QLineEdit()
        self.repo_owner_edit = QLineEdit()
        self.repo_repo_edit = QLineEdit()
        self.repo_is_active_checkbox = QCheckBox("Set as active repo for app updates")
        self.repo_is_active_checkbox.toggled.connect(self._on_active_checkbox_toggled)
        self.create_on_gh_button = QPushButton("Create on GitHub & Link")
        self.create_on_gh_button.clicked.connect(self._action_create_repo)
        form_layout.addRow("Name:", self.repo_name_edit)
        form_layout.addRow("Owner (user or org):", self.repo_owner_edit)
        form_layout.addRow("Repository Name:", self.repo_repo_edit)
        form_layout.addRow(self.repo_is_active_checkbox)
        form_layout.addRow(self.create_on_gh_button)
        splitter.addWidget(form_widget)
        return splitter, form_widget

    def _create_plugins_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        plugins_tabs = QTabWidget()
        plugins_tabs.addTab(self._create_plugins_manage_tab(), qta.icon('fa5s.tasks'), "Manage")
        plugins_tabs.addTab(self._create_plugins_install_tab(), qta.icon('fa5s.download'), "Install")
        layout.addWidget(plugins_tabs)
        self.tab_widget.addTab(tab, qta.icon('fa5s.plug'), "Plugins")

    def _create_plugins_manage_tab(self):
        tab = QWidget()
        layout = QHBoxLayout(tab)
        splitter = QSplitter(Qt.Orientation.Horizontal)
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.addWidget(QLabel("Installed Plugins:"))
        self.manage_plugins_list = QListWidget()
        self.manage_plugins_list.itemSelectionChanged.connect(self._on_installed_plugin_selected)
        left_layout.addWidget(self.manage_plugins_list)
        batch_buttons_layout = QHBoxLayout()
        self.enable_all_button = QPushButton("Enable All")
        self.disable_all_button = QPushButton("Disable Non-Essential")
        self.enable_all_button.clicked.connect(self._enable_all_plugins)
        self.disable_all_button.clicked.connect(self._disable_all_non_core_plugins)
        batch_buttons_layout.addWidget(self.enable_all_button)
        batch_buttons_layout.addWidget(self.disable_all_button)
        left_layout.addLayout(batch_buttons_layout)
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        self.plugin_details_stack = QStackedWidget()
        placeholder = QLabel("Select a plugin to see details.")
        placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.plugin_details_stack.addWidget(placeholder)
        details_widget = QWidget()
        details_layout = QFormLayout(details_widget)
        self.plugin_name_label = QLabel()
        self.plugin_version_label = QLabel()
        self.plugin_author_label = QLabel()
        self.plugin_desc_label = QLabel()
        self.plugin_desc_label.setWordWrap(True)
        self.plugin_status_label = QLabel()
        details_layout.addRow("<b>Name:</b>", self.plugin_name_label)
        details_layout.addRow("<b>Version:</b>", self.plugin_version_label)
        details_layout.addRow("<b>Author:</b>", self.plugin_author_label)
        details_layout.addRow("<b>Description:</b>", self.plugin_desc_label)
        details_layout.addRow("<b>Status:</b>", self.plugin_status_label)
        self.plugin_details_stack.addWidget(details_widget)
        actions_layout = QHBoxLayout()
        self.enable_plugin_checkbox = QCheckBox("Enabled")
        self.enable_plugin_checkbox.toggled.connect(self._on_plugin_enabled_changed)
        self.reload_plugin_button = QPushButton("Reload")
        self.reload_plugin_button.clicked.connect(self._reload_selected_plugin)
        self.uninstall_button = QPushButton("Uninstall")
        self.uninstall_button.clicked.connect(self._uninstall_selected_plugin)
        actions_layout.addWidget(self.enable_plugin_checkbox)
        actions_layout.addStretch()
        actions_layout.addWidget(self.reload_plugin_button)
        actions_layout.addWidget(self.uninstall_button)
        right_layout.addWidget(self.plugin_details_stack, 1)
        right_layout.addLayout(actions_layout)
        splitter.addWidget(left_widget)
        splitter.addWidget(right_widget)
        splitter.setSizes([300, 550])
        layout.addWidget(splitter)
        return tab

    def _create_plugins_install_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(10)
        repo_group = QGroupBox("Install from Repository")
        repo_layout = QVBoxLayout(repo_group)
        repo_input_widget = QWidget()
        repo_input_layout = QHBoxLayout(repo_input_widget)
        repo_input_layout.setContentsMargins(0, 0, 0, 0)
        repo_input_layout.addWidget(QLabel("GitHub Repo (user/repo):"))
        self.plugins_repo_edit = QLineEdit()
        self.fetch_plugins_button = QPushButton("Fetch")
        self.fetch_plugins_button.clicked.connect(self._fetch_remote_plugins)
        repo_input_layout.addWidget(self.plugins_repo_edit, 1)
        repo_input_layout.addWidget(self.fetch_plugins_button)
        repo_layout.addWidget(repo_input_widget)
        self.remote_plugins_list = QListWidget()
        self.remote_plugins_list.itemSelectionChanged.connect(self._on_remote_plugin_selected)
        repo_layout.addWidget(self.remote_plugins_list)
        self.install_remote_button = QPushButton("Install Selected Plugin")
        self.install_remote_button.setEnabled(False)
        self.install_remote_button.clicked.connect(self._install_selected_remote_plugin)
        repo_layout.addWidget(self.install_remote_button, 0, Qt.AlignmentFlag.AlignRight)
        layout.addWidget(repo_group)
        local_group = QGroupBox("Install from File/URL")
        local_layout = QHBoxLayout(local_group)
        self.install_from_url_button = QPushButton("From URL...")
        self.install_from_file_button = QPushButton("From File...")
        self.install_from_url_button.clicked.connect(lambda: self._install_plugin_from_url(""))
        self.install_from_file_button.clicked.connect(self._install_plugin_from_file)
        local_layout.addWidget(self.install_from_url_button)
        local_layout.addWidget(self.install_from_file_button)
        local_layout.addStretch()
        layout.addWidget(local_group)
        layout.addStretch()
        return tab

    def _action_create_repo(self):
        owner, repo = self.repo_owner_edit.text(), self.repo_repo_edit.text()
        if owner and repo: self.github_manager.create_repo(repo, "", False)

    def _populate_git_config_fields(self, name, email):
        self.git_user_name_edit.setText(name)
        self.git_user_email_edit.setText(email)
        self.original_git_config = {'name': name, 'email': email}

    def _handle_git_success(self, msg, data):
        if "config updated" in msg: self._on_ui_setting_changed()

    def _sync_git_with_github(self):
        user_info = self.github_manager.get_user_info()
        if not user_info:
            QMessageBox.warning(self, "Not Logged In", "Please log in to GitHub first.")
            return
        user_name = user_info.get('login', '')
        user_email = user_info.get('email', '')
        if not user_email: user_email = f"{user_info.get('id')}+{user_name}@users.noreply.github.com"
        self.git_user_name_edit.setText(user_name)
        self.git_user_email_edit.setText(user_email)
        self._on_ui_setting_changed()

    def _logout_github(self):
        self.github_manager.logout()
        self._update_auth_status()

    def _update_auth_status(self):
        user = self.github_manager.get_authenticated_user()
        is_logged_in = bool(user)
        self.auth_status_label.setText(f"Logged in as: <b>{user}</b>" if is_logged_in else "<i>Not logged in.</i>")
        self.auth_button.setVisible(not is_logged_in)
        self.logout_button.setVisible(is_logged_in)
        sync_button = self.findChild(QPushButton, "syncWithGitHubButton")
        if sync_button:
            sync_button.setEnabled(is_logged_in)

    def _on_device_code_ready(self, data):
        self.auth_dialog = AuthDialog(data.get('user_code'), data.get('verification_uri'),
                                      self)
        self.auth_dialog.show()
        self.github_manager.poll_for_token(
            data['device_code'], data['interval'], data['expires_in'])

    def _on_auth_successful(self, username):
        if self.auth_dialog: self.auth_dialog.accept()
        self.auth_dialog = None
        self._update_auth_status()
        self._on_ui_setting_changed()

    def _on_auth_failed(self, error):
        if self.auth_dialog: self.auth_dialog.reject()
        self.auth_dialog = None
        QMessageBox.critical(self, "GitHub Authentication Failed", error)
        self._update_auth_status()

    def _on_auth_polling_lapsed(self):
        if self.auth_dialog: self.auth_dialog.reject()
        self.auth_dialog = None
        QMessageBox.warning(self, "Authentication Timed Out", "Device authorization timed out.")

    def _on_repo_selection_changed(self, current, previous):
        if previous: self._save_repo_form_to_staged()
        self._load_staged_to_repo_form(current)

    def _on_active_checkbox_toggled(self, checked):
        if checked and self.current_repo_id_in_form: self.staged_active_repo_id = self.current_repo_id_in_form
        self._on_ui_setting_changed()

    def _save_repo_form_to_staged(self):
        if not self.current_repo_id_in_form: return
        repo = next((r for r in self.staged_repos if r['id'] == self.current_repo_id_in_form), None)
        if repo:
            repo['name'] = self.repo_name_edit.text()
            repo['owner'] = self.repo_owner_edit.text()
            repo['repo'] = self.repo_repo_edit.text()

    def _load_staged_to_repo_form(self, item):
        self.is_loading = True
        self.current_repo_id_in_form = item.data(Qt.ItemDataRole.UserRole) if item else None
        if self.current_repo_id_in_form:
            repo = next((r for r in self.staged_repos if r['id'] == self.current_repo_id_in_form), {})
            self.repo_name_edit.setText(repo.get('name', ''))
            self.repo_owner_edit.setText(repo.get('owner', ''))
            self.repo_repo_edit.setText(repo.get('repo', ''))
            self.repo_is_active_checkbox.setChecked(self.current_repo_id_in_form == self.staged_active_repo_id)
        else:
            self._clear_repo_form()
        self.is_loading = False

    def _action_add_repo(self):
        new_repo = {"id": str(uuid.uuid4()), "name": "New Repository", "owner": "", "repo": ""}
        self.staged_repos.append(new_repo)
        self._populate_repo_list(select_repo_id=new_repo['id'])
        self._on_ui_setting_changed()

    def _action_remove_repo(self):
        if item := self.repo_list.currentItem():
            repo_id = item.data(Qt.ItemDataRole.UserRole)
            self.staged_repos = [r for r in self.staged_repos if r['id'] != repo_id]
            if self.staged_active_repo_id == repo_id: self.staged_active_repo_id = None
            self._populate_repo_list()
            self._on_ui_setting_changed()

    def _populate_repo_list(self, select_repo_id=None):
        self.repo_list.clear()
        self._clear_repo_form()
        for repo in self.staged_repos:
            item = QListWidgetItem(repo['name'])
            item.setData(Qt.ItemDataRole.UserRole, repo['id'])
            self.repo_list.addItem(item)
        if select_repo_id:
            for i in range(self.repo_list.count()):
                if self.repo_list.item(i).data(Qt.ItemDataRole.UserRole) == select_repo_id:
                    self.repo_list.setCurrentRow(i)
                    break

    def _clear_repo_form(self):
        self.repo_name_edit.clear()
        self.repo_owner_edit.clear()
        self.repo_repo_edit.clear()
        self.repo_is_active_checkbox.setChecked(False)

    def _populate_all_plugin_lists(self):
        self._populate_manage_plugins_list()

    def _populate_manage_plugins_list(self):
        self.manage_plugins_list.clear()
        plugins = sorted(self.plugin_manager.get_all_plugins(), key=lambda p: p.name.lower())
        for p in plugins:
            item = QListWidgetItem(p.name)
            item.setData(Qt.ItemDataRole.UserRole, p.id)
            self.manage_plugins_list.addItem(item)

    def _on_installed_plugin_selected(self):
        items = self.manage_plugins_list.selectedItems()
        if not items:
            self.plugin_details_stack.setCurrentIndex(0)
            return
        plugin = self.plugin_manager.plugins.get(items[0].data(Qt.ItemDataRole.UserRole))
        if plugin:
            self.plugin_details_stack.setCurrentIndex(1)
            self.is_loading = True
            self.plugin_name_label.setText(plugin.name)
            self.plugin_version_label.setText(plugin.version)
            self.plugin_author_label.setText(plugin.manifest.get('author', 'N/A'))
            self.plugin_desc_label.setText(plugin.manifest.get('description', 'No description.'))
            self.plugin_status_label.setText(plugin.status_reason)
            self.enable_plugin_checkbox.setChecked(plugin.enabled)
            self.enable_plugin_checkbox.setEnabled(not plugin.is_core)
            self.reload_plugin_button.setEnabled(plugin.is_loaded)
            self.uninstall_button.setEnabled(plugin.source_type == 'user')
            self.is_loading = False

    def _on_plugin_enabled_changed(self, checked):
        if self.is_loading: return
        items = self.manage_plugins_list.selectedItems()
        if items and (plugin := self.plugin_manager.plugins.get(items[0].data(Qt.ItemDataRole.UserRole))):
            (self.plugin_manager.enable_plugin if checked else self.plugin_manager.disable_plugin)(plugin.id)
            self.restart_needed = True

    def _reload_selected_plugin(self):
        items = self.manage_plugins_list.selectedItems()
        self.restart_needed = True
        if items:
            self.plugin_manager.reload_plugin(items[0].data(Qt.ItemDataRole.UserRole))
            self._on_installed_plugin_selected()

    def _reload_all_plugins(self):
        self.plugin_manager.discover_and_load_plugins()
        self.restart_needed = True
        self._populate_manage_plugins_list()

    def _enable_all_plugins(self):
        if QMessageBox.question(self, "Enable All Plugins",
                                "This will enable all plugins and reload them. A restart might be required for all changes to take full effect.\n\nContinue?",
                                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                QMessageBox.StandardButton.No) == QMessageBox.StandardButton.Yes:
            log.info("User requested to enable all plugins.")
            self.plugin_manager.enable_all()
            self.restart_needed = True
            self._populate_manage_plugins_list()
            self._on_ui_setting_changed()

    def _disable_all_non_core_plugins(self):
        if QMessageBox.question(self, "Disable Non-Essential Plugins",
                                "This will disable and unload all non-essential plugins (e.g., language support, AI tools, debug tools).\nCore functionality like the file explorer and search will not be affected.\n\nContinue?",
                                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                QMessageBox.StandardButton.No) == QMessageBox.StandardButton.Yes:
            log.info("User requested to disable all non-essential plugins.")
            self.plugin_manager.disable_all_non_core()
            self.restart_needed = True
            self._populate_manage_plugins_list()
            self._on_ui_setting_changed()

    def _on_remote_plugin_selected(self):
        self.install_remote_button.setEnabled(bool(self.remote_plugins_list.selectedItems()))

    def _fetch_remote_plugins(self):
        self.github_manager.fetch_plugin_index(self.plugins_repo_edit.text().strip())

    def _on_plugin_index_ready(self, plugin_list):
        self.remote_plugins_list.clear()
        for p in plugin_list:
            item = QListWidgetItem(f"{p['name']} v{p['version']}")
            item.setData(Qt.ItemDataRole.UserRole, p)
            self.remote_plugins_list.addItem(item)

    def _install_selected_remote_plugin(self):
        if item := self.remote_plugins_list.currentItem():
            self._install_plugin_from_url(item.data(Qt.ItemDataRole.UserRole).get('download_url'))

    def _install_plugin_from_url(self, url):
        # The QInputDialog will be pre-filled with the 'url' if it's provided.
        # The user can just confirm by clicking OK, or enter a new URL.
        url, ok = QInputDialog.getText(self, "Install from URL", "Plugin ZIP URL:", text=url)

        # If the user cancels or the URL is empty, we stop.
        if not (url and ok):
            return

        with tempfile.TemporaryDirectory() as temp_dir:
            try:
                # Perform the web request
                r = requests.get(url)
                # This will raise an exception for bad status codes (like 404, 500)
                r.raise_for_status()

                # Save the downloaded content to a temporary zip file
                zip_path = os.path.join(temp_dir, "plugin.zip")
                with open(zip_path, 'wb') as f:
                    f.write(r.content)

                # Ask the plugin manager to install from the zip
                ok, msg = self.plugin_manager.install_plugin_from_zip(zip_path)

                # Show the result to the user
                (QMessageBox.information if ok else QMessageBox.warning)(self, "Plugin Install", msg)

                # If installation was successful, mark that a restart is needed
                # and refresh the list of installed plugins.
                if ok:
                    self.restart_needed = True
                    self._populate_all_plugin_lists()

            except Exception as e:
                # Catch any errors during download or installation
                QMessageBox.critical(self, "Download Error", f"Failed to download or install plugin: {e}")

    def _install_plugin_from_file(self):
        f, _ = QFileDialog.getOpenFileName(self, "Select Plugin Zip", "", "ZIP Archives (*.zip)")
        if f:
            ok, msg = self.plugin_manager.install_plugin_from_zip(f)
            (QMessageBox.information if ok else QMessageBox.warning)(self, "Install Failed", msg)
            if ok:
                self.restart_needed = True
                self._populate_manage_plugins_list()

    def _uninstall_selected_plugin(self):
        if items := self.manage_plugins_list.selectedItems():
            pid = items[0].data(Qt.ItemDataRole.UserRole)
            plugin = self.plugin_manager.plugins.get(pid)
            if QMessageBox.question(self, "Confirm Uninstall",
                                    f"Are you sure you want to uninstall '{plugin.name}'?") == QMessageBox.StandardButton.Yes:
                ok, msg = self.plugin_manager.uninstall_plugin(pid)
                (QMessageBox.information if ok else QMessageBox.warning)(self, "Uninstall Status", msg)
                if ok:
                    self.restart_needed = True
                    self._populate_all_plugin_lists()
```

### File: `/ui/main_window.py`
```py
# /ui/main_window.py
import os, sys, re
from functools import partial
from typing import Optional
from PyQt6.QtGui import (QKeySequence, QAction, QCloseEvent, QDesktopServices, QIcon, QActionGroup, QDragEnterEvent,
                         QDropEvent)
from PyQt6.QtWidgets import (QMessageBox, QMenu, QWidget, QVBoxLayout, QHBoxLayout, QMainWindow, QStatusBar, QTabWidget, \
                             QLabel, QToolButton, QToolBar, QSizePolicy, QApplication, QFileDialog, QDockWidget, QComboBox)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer, QSize, QUrl, QEvent

import qtawesome as qta
from utils.logger import log
from utils import versioning, helpers
from app_core.file_handler import FileHandler
from app_core.settings_manager import settings_manager
from app_core.project_manager import ProjectManager
from app_core.linter_manager import LinterManager
from app_core.plugin_manager import PluginManager
from app_core.completion_manager import CompletionManager
from app_core.update_manager import UpdateManager
from app_core.source_control_manager import SourceControlManager
from app_core.github_manager import GitHubManager
from app_core.puffin_api import PuffinPluginAPI
from .preferences_dialog import PreferencesDialog
from .widgets.draggable_tab_widget import DraggableTabWidget
from .explorer.list_view_widget import FileSystemListView
from .widgets.problems_panel import ProblemsPanel
from .widgets.source_control_panel import ProjectSourceControlPanel
from .editor_widget import EditorWidget, HighlightManager
from app_core.syntax_highlighters import (
    PythonSyntaxHighlighter, JsonSyntaxHighlighter, HtmlSyntaxHighlighter,
    CssSyntaxHighlighter, CppSyntaxHighlighter, CSharpSyntaxHighlighter, JavaScriptSyntaxHighlighter,
    RustSyntaxHighlighter
)


class MainWindow(QMainWindow):
    untitled_file_counter, _is_app_closing = 0, False
    theme_changed_signal = pyqtSignal(str)
    COMMENT_MAP = {'.py': '#', '.js': '//', '.ts': '//', '.cs': '//', '.java': '//', '.go': '//', '.rs': '//',
                   '.c': '//', '.cpp': '//', '.h': '//', '.hpp': '//', '.css': '/*', '.html': '<!--'}
    END_COMMENT_MAP = {'/*': '*/', '<!--': '-->'}

    def __init__(self, file_handler, theme_manager, debug_mode=False, parent=None):
        super().__init__(parent)
        self.file_handler, self.theme_manager, self.debug_mode = file_handler, theme_manager, debug_mode
        self.file_handler.parent_window = self
        self.preferences_dialog, self._bottom_tab_widget, self._bottom_dock_widget = None, None, None

        self._initialize_managers()
        self.puffin_api = PuffinPluginAPI(self)
        self.puffin_api.highlight_manager = self.highlight_manager

        # --- NEW: Encoding Map for the UI ---
        self.encoding_map = {
            "UTF-8": "utf-8",
            "UTF-8-SIG": "utf-8-sig",
            "UTF-16 LE": "utf-16le",
            "UTF-16 BE": "utf-16be",
            "Latin-1": "latin-1",
            "Windows-1252": "cp1252"
        }
        self.reverse_encoding_map = {v: k for k, v in self.encoding_map.items()}

        self._register_built_in_highlighters()

        self.plugin_manager = PluginManager(self)
        self.setWindowTitle(f"PuffinPyEditor - v{versioning.APP_VERSION}")
        self._load_window_geometry()

        self._create_core_widgets()
        self._create_core_actions()
        self._create_core_menu()
        self._create_toolbar()
        self._create_layout()
        self._create_statusbar()
        self._integrate_file_explorer()
        self._integrate_linter_ui()
        self._integrate_source_control_ui()
        self._integrate_global_drag_drop()

        if self.explorer_panel:
            self.project_manager.projects_changed.connect(self.explorer_panel.refresh)
            self.explorer_panel.tree_widget.currentItemChanged.connect(self._on_active_project_changed)
        if self.source_control_panel:
            self.theme_changed_signal.connect(self.source_control_panel.update_icons)
            self.git_manager.git_success.connect(self.source_control_panel.refresh_all_projects)
            self.github_manager.operation_success.connect(self.source_control_panel.refresh_all_projects)
            if self.explorer_panel:
                self.explorer_panel.tree_widget.currentItemChanged.connect(
                    self.source_control_panel.refresh_all_projects)

        plugins_to_ignore = []
        if self.debug_mode:
            try:
                from core_debug_tools.enhanced_exceptions.plugin_main import initialize as init_eh
                self.eh_instance = init_eh(self.puffin_api, sys.excepthook)
                plugins_to_ignore.append('enhanced_exceptions')
            except Exception as e:
                log.error(f"Failed to load core exception handler: {e}", exc_info=True)

        self.plugin_manager.discover_and_load_plugins(ignore_list=plugins_to_ignore)
        self._connect_signals()
        self._apply_theme_and_icons(self.settings.get("last_theme_id"))
        QTimer.singleShot(0, self._post_init_setup)
        log.info("MainWindow __init__ has completed.")

    def _register_built_in_highlighters(self):
        """
        Directly registers core syntax highlighters with the PuffinAPI.
        This ensures essential features are always available without relying on the plugin system.
        """
        log.info("Registering built-in syntax highlighters...")
        built_in_map = {
            '.py': PythonSyntaxHighlighter,
            '.pyw': PythonSyntaxHighlighter,
            '.json': JsonSyntaxHighlighter,
            '.html': HtmlSyntaxHighlighter,
            '.css': CssSyntaxHighlighter,
            '.js': JavaScriptSyntaxHighlighter,
            '.rs': RustSyntaxHighlighter,
            '.c': CppSyntaxHighlighter,
            '.cpp': CppSyntaxHighlighter,
            '.h': CppSyntaxHighlighter,
            '.hpp': CppSyntaxHighlighter,
            '.cs': CSharpSyntaxHighlighter,
        }
        for ext, highlighter_class in built_in_map.items():
            if highlighter_class:
                self.puffin_api.register_highlighter(ext, highlighter_class)
        log.info("Built-in highlighters registered.")

    def _initialize_managers(self):
        self.settings = settings_manager
        self.project_manager = ProjectManager()
        self.highlight_manager = HighlightManager()
        self.completion_manager = CompletionManager(self.theme_manager, self)
        self.github_manager = GitHubManager(self)
        self.git_manager = SourceControlManager(self)
        self.linter_manager = LinterManager(self)
        self.update_manager = UpdateManager(self)
        self.actions = {}
        self.editor_tabs_data = {}
        self.file_open_handlers = {}
        self.lint_timer = QTimer(self);
        self.lint_timer.setSingleShot(True);
        self.lint_timer.setInterval(1500)
        self.auto_save_timer = QTimer(self);
        self.auto_save_timer.setSingleShot(True)
        # --- NEW: Timer for saving drafts ---
        self.draft_save_timer = QTimer(self)
        self.draft_save_timer.setSingleShot(True)
        self.draft_save_timer.setInterval(2000) # Save draft 2s after user stops typing

    def _add_new_tab(self, filepath=None, content="", encoding='utf-8', is_placeholder=False):
        if not is_placeholder and self.tab_widget.count() == 1 and isinstance(self.tab_widget.widget(0), QLabel):
            self.tab_widget.removeTab(0)
        if is_placeholder:
            placeholder = QLabel("Open a file or project...", alignment=Qt.AlignmentFlag.AlignCenter)
            placeholder.setObjectName("PlaceholderLabel")
            self.tab_widget.addTab(placeholder, "Welcome")
            self.tab_widget.setTabsClosable(False)
            return
        try:
            self.tab_widget.setTabsClosable(True)
            editor = EditorWidget(self.puffin_api, self.completion_manager, self.highlight_manager, self.theme_manager, self)
            if hc := self.puffin_api.highlighter_map.get(os.path.splitext(filepath or "")[1].lower()):
                editor.set_highlighter(hc)
            editor.set_filepath(filepath);
            editor.set_text(content)
            editor.cursor_position_display_updated.connect(lambda l, c: self.cursor_label.setText(f" Ln {l}, Col {c} "))
            editor.content_possibly_changed.connect(partial(self._on_content_changed, editor))
            editor.status_message_requested.connect(self.statusBar().showMessage)
            name = os.path.basename(filepath or f"Untitled-{self.untitled_file_counter + 1}")
            if not filepath: self.untitled_file_counter += 1
            idx = self.tab_widget.addTab(editor, name)
            self.tab_widget.setTabToolTip(idx, filepath or f"Unsaved {name}")
            self.editor_tabs_data[editor] = {'filepath': filepath, 'original_hash': hash(content), 'encoding': encoding}
            self.tab_widget.setCurrentWidget(editor)
            editor.text_area.setFocus()
        except Exception as e:
            log.critical(f"CRASH during _add_new_tab: {e}", exc_info=True)
            QMessageBox.critical(self, "Fatal Error", f"Could not create editor tab:\n\n{e}")

    def _post_init_setup(self):
        self._update_recent_files_menu()
        self._update_window_title()
        if open_files := settings_manager.get("open_files", []):
            log.info(f"Restoring {len(open_files)} open files from last session.")
            for filepath in open_files:
                if os.path.exists(filepath):
                    self._action_open_file(filepath)
                else:
                    log.warning(f"Could not restore non-existent file: {filepath}")
        if self.tab_widget.count() == 0:
            self._add_new_tab(is_placeholder=True)

    def _on_file_renamed(self, old_path, new_path):
        norm_old_path = os.path.normpath(old_path)
        for i in range(self.tab_widget.count()):
            widget = self.tab_widget.widget(i)
            if isinstance(widget, EditorWidget) and (data := self.editor_tabs_data.get(widget)) and data.get(
                    'filepath') == norm_old_path:
                data['filepath'] = new_path
                index = self.tab_widget.indexOf(widget)
                if index != -1:
                    self.tab_widget.setTabText(index, os.path.basename(new_path))
                    self.tab_widget.setTabToolTip(index, new_path)
                    data['original_hash'] = hash(widget.get_text())
                    self._on_content_changed(widget)
                break

    def _integrate_file_explorer(self):
        self.explorer_panel = FileSystemListView(self.puffin_api)
        dock = QDockWidget("Explorer", self)
        dock.setWidget(self.explorer_panel)
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, dock)
        self.view_menu.addSeparator()
        self.view_menu.addAction(dock.toggleViewAction())
        # The connection is now done in __init__ after project_manager is created
        QTimer.singleShot(100, self.explorer_panel.refresh)

    def _integrate_linter_ui(self):
        self.problems_panel = ProblemsPanel(self)
        self.add_dock_panel(self.problems_panel, "Problems", "bottom", "mdi.bug-outline")
        self.linter_manager.lint_results_ready.connect(self._update_problems_panel)
        self.linter_manager.error_occurred.connect(
            lambda err: self.problems_panel.show_info_message(f"Linter Error: {err}"))
        self.problems_panel.problem_selected.connect(self._goto_definition_result)

    def _integrate_source_control_ui(self):
        self.source_control_panel = ProjectSourceControlPanel(
            self.project_manager, self.git_manager, self.github_manager, self.puffin_api, self
        )
        self.add_dock_panel(self.source_control_panel, "Source Control", "bottom",
                            "mdi.git")

    def _integrate_global_drag_drop(self):
        self.setAcceptDrops(True)

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent):
        if event.mimeData().hasUrls():
            for url in event.mimeData().urls():
                if url.isLocalFile():
                    self._action_open_file(url.toLocalFile())
            event.acceptProposedAction()

    def _update_problems_panel(self, problems):
        if isinstance(editor := self.tab_widget.currentWidget(), EditorWidget) and (
                fp := self.editor_tabs_data.get(editor, {}).get('filepath')):
            self.problems_panel.update_problems({fp: problems})

    def _load_window_geometry(self):
        size = self.settings.get("window_size", [1600, 1000])
        pos = self.settings.get("window_position")
        self.resize(QSize(size[0], size[1]))
        if pos:
            self.move(pos[0], pos[1])

    def _create_core_widgets(self):
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.tab_widget = DraggableTabWidget(self)
        self.tab_widget.setObjectName("MainTabWidget")
        btn = QToolButton()
        btn.setIcon(qta.icon('mdi.plus'))
        btn.setAutoRaise(True)
        btn.clicked.connect(self._add_new_tab)
        self.tab_widget.setCornerWidget(btn, Qt.Corner.TopRightCorner)
        self.tab_widget.setDocumentMode(True)
        self.tab_widget.setTabsClosable(True)
        self.tab_widget.setMovable(True)

    def _create_core_actions(self):
        actions_map = {
            "new_file": ("&New File", self._add_new_tab, "Ctrl+N", 'mdi.file-outline'),
            "open_file": ("&Open File...", self._action_open_file_dialog, "Ctrl+O", 'mdi.folder-open-outline'),
            "open_folder": ("Open &Folder...", self._action_open_folder, "Ctrl+Shift+O", 'mdi.folder-outline'),
            "close_project": ("&Close Project", self._action_close_project, None, None),
            "save": ("&Save", self._action_save_file, "Ctrl+S", 'mdi.content-save-outline'),
            "save_as": ("Save &As...", self._action_save_as, "Ctrl+Shift+S", None),
            "save_all": ("Save A&ll", self._action_save_all, "Ctrl+Alt+S", None),
            "find_replace": ("&Find/Replace...", self.toggle_find_panel, "Ctrl+F", "mdi.magnify"),
            "preferences": ("&Preferences...", self._action_open_preferences, "Ctrl+,", 'mdi.cog-outline'),
            "exit": ("E&xit", self.close, "Ctrl+Q", None),
            "force_quit": ("&Force Quit", self._action_force_quit, "Ctrl+Shift+Q", 'mdi.alert-outline')
        }
        for key, props in actions_map.items():
            text, callback = props[0], props[1]
            shortcut = props[2] if len(props) > 2 else None
            icon = props[3] if len(props) > 3 else None

            action = QAction(text, self)
            action.triggered.connect(callback)
            if icon:
                action.setData(icon)
            if shortcut:
                action.setShortcut(QKeySequence(shortcut))
            self.actions[key] = action

        self.actions["find_replace"].setEnabled(False)

    def _create_core_menu(self):
        mb = self.menuBar();
        self.file_menu, self.edit_menu, self.view_menu, self.run_menu, self.tools_menu, self.help_menu = mb.addMenu(
            "&File"), mb.addMenu("&Edit"), mb.addMenu("&View"), mb.addMenu("&Run"), mb.addMenu("&Tools"), mb.addMenu(
            "&Help")
        self.file_menu.addActions([self.actions[k] for k in ["new_file", "open_file"]]);
        self.recent_files_menu = self.file_menu.addMenu("Open &Recent");
        self.file_menu.addSeparator()
        self.file_menu.addActions([self.actions[k] for k in ["open_folder", "close_project"]]);
        self.file_menu.addSeparator();
        self.file_menu.addActions([self.actions[k] for k in ["save", "save_as", "save_all"]]);
        self.file_menu.addSeparator()
        self.file_menu.addAction(self.actions["preferences"]);
        self.file_menu.addSeparator();
        self.file_menu.addActions([self.actions["exit"], self.actions["force_quit"]])
        self.edit_menu.addAction(self.actions["find_replace"]);
        self.theme_menu = self.view_menu.addMenu("&Themes");
        self.help_menu.addAction("About PuffinPyEditor", self._show_about_dialog);
        self.help_menu.addAction("View on GitHub", self._open_github_link)

    def _create_toolbar(self):
        tb = QToolBar("Main Toolbar");
        tb.setIconSize(QSize(18, 18));
        self.addToolBar(tb);
        self.main_toolbar = tb
        tb.addActions([self.actions[k] for k in ["new_file", "open_file", "save"]])
        tb.addSeparator()

        sp = QWidget();
        sp.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred);
        tb.addWidget(sp);
        
        # --- NEW Encoding Dropdown ---
        self.encoding_toolbar_label = QLabel(" Encoding: ")
        self.encoding_combo = QComboBox()
        self.encoding_combo.setToolTip("Change file encoding and re-save")
        for display_name, actual_name in self.encoding_map.items():
            self.encoding_combo.addItem(display_name, actual_name)
        
        tb.addWidget(self.encoding_toolbar_label)
        tb.addWidget(self.encoding_combo)
        tb.addSeparator()

        tb.addAction(self.actions["find_replace"])
        tb.addAction(self.actions["preferences"])

    def _create_layout(self):
        lay = QHBoxLayout(self.central_widget);
        lay.setContentsMargins(0, 0, 0, 0);
        lay.addWidget(self.tab_widget)

    def _create_statusbar(self):
        self.setStatusBar(QStatusBar(self))
        self.encoding_label = QLabel(" UTF-8 ")
        self.cursor_label = QLabel(" Ln 1, Col 1 ")
        self.statusBar().addPermanentWidget(self.encoding_label)
        self.statusBar().addPermanentWidget(self.cursor_label)

    def _connect_signals(self):
        self.tab_widget.currentChanged.connect(self._on_tab_changed);
        self.tab_widget.tabCloseRequested.connect(self._action_close_tab_by_index);
        self.lint_timer.timeout.connect(self._trigger_file_linter);
        self.completion_manager.definition_found.connect(self._goto_definition_result);
        self.auto_save_timer.timeout.connect(self._auto_save_current_tab)
        self.file_handler.recent_files_changed.connect(self._update_recent_files_menu)
        self.encoding_combo.activated.connect(self._on_encoding_changed_from_dropdown)
        # --- NEW: Connect draft save timer ---
        self.draft_save_timer.timeout.connect(self._save_current_draft)

    def _apply_theme_and_icons(self, theme_id):
        self.theme_manager.set_theme(theme_id, QApplication.instance());
        self.theme_changed_signal.emit(theme_id)
        for act in self.actions.values():
            if ico := act.data(): act.setIcon(qta.icon(ico))
        self._rebuild_theme_menu();
        [w.update_theme() for i in range(self.tab_widget.count()) if
         hasattr(w := self.tab_widget.widget(i), 'update_theme')]
        if hasattr(self, 'explorer_panel'): self.explorer_panel.refresh()

    def _rebuild_theme_menu(self):
        self.theme_menu.clear();
        group = QActionGroup(self);
        group.setExclusive(True)
        for t_id, name in self.theme_manager.get_available_themes_for_ui().items():
            act = QAction(name, self, checkable=True, triggered=lambda _, tid=t_id: self._on_theme_selected(tid));
            act.setData(t_id);
            act.setChecked(t_id == self.theme_manager.current_theme_id);
            group.addAction(act);
            self.theme_menu.addAction(act)

    def add_dock_panel(self, panel, title, area_str: str, icon_name=None):
        area_map = {
            "left": Qt.DockWidgetArea.LeftDockWidgetArea,
            "right": Qt.DockWidgetArea.RightDockWidgetArea,
            "top": Qt.DockWidgetArea.TopDockWidgetArea,
            "bottom": Qt.DockWidgetArea.BottomDockWidgetArea,
        }
        area = area_map.get(area_str.lower(), Qt.DockWidgetArea.BottomDockWidgetArea)

        if area == Qt.DockWidgetArea.BottomDockWidgetArea:
            if not self._bottom_tab_widget:
                self._bottom_dock_widget = QDockWidget("Info Panels", self)
                self._bottom_dock_widget.setObjectName("SharedBottomDock")
                self._bottom_tab_widget = QTabWidget()
                self._bottom_tab_widget.setObjectName("InfoPanelTabBar")
                self._bottom_tab_widget.setDocumentMode(True)
                self._bottom_dock_widget.setWidget(self._bottom_tab_widget)
                self.addDockWidget(area, self._bottom_dock_widget)
                if self.view_menu:
                    self.view_menu.addSeparator()
                    self.view_menu.addAction(self._bottom_dock_widget.toggleViewAction())

            icon = qta.icon(icon_name) if icon_name else QIcon()
            self._bottom_tab_widget.addTab(panel, icon, title)
            return self._bottom_dock_widget

        dock = QDockWidget(title, self);
        dock.setWidget(panel)
        if icon_name: dock.setWindowIcon(qta.icon(icon_name))
        self.addDockWidget(area, dock)
        if self.view_menu:
            self.view_menu.addSeparator()
            self.view_menu.addAction(dock.toggleViewAction())
        return dock

    def _action_open_file(self, fp=None, content=None, encoding=None):
        if not (isinstance(fp, str) and fp): return
        np = os.path.normpath(fp)
        for i in range(self.tab_widget.count()):
            if isinstance(w := self.tab_widget.widget(i), EditorWidget) and self.editor_tabs_data.get(w, {}).get(
                    'filepath') == np: self.tab_widget.setCurrentIndex(i); return
        if h := self.file_open_handlers.get(os.path.splitext(np)[1].lower()): h(
            np); self.file_handler._add_to_recent_files(np); return
        
        # --- MODIFIED: Draft Checking Logic ---
        draft_path = helpers.get_draft_path(np)
        use_draft = False
        if os.path.exists(draft_path) and os.path.getmtime(draft_path) > os.path.getmtime(np):
            reply = QMessageBox.question(
                self, "Unsaved Changes Found",
                f"It looks like you have unsaved changes for '{os.path.basename(np)}' from a previous session.\n\n"
                "Do you want to restore them?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.Yes
            )
            if reply == QMessageBox.StandardButton.Yes:
                use_draft = True
            else:
                # User chose not to restore, so we delete the draft
                os.remove(draft_path)

        if use_draft:
            log.info(f"Restoring unsaved changes from draft for: {np}")
            content, encoding = self.file_handler._read_with_encoding_detection(draft_path)
            if content is None:
                QMessageBox.warning(self, "Draft Read Error", "Could not read the draft file. Opening original.")
                content, encoding = self.file_handler._read_with_encoding_detection(np)
        elif content is None:
            content, encoding = self.file_handler._read_with_encoding_detection(np)

        if content is None:
            self.puffin_api.show_message("critical", "Error Opening File", f"Could not read file: {np}")
            return
        
        self._add_new_tab(np, content, encoding or 'utf-8')
        self.file_handler._add_to_recent_files(np)

    def _action_open_file_dialog(self):
        fp, content, encoding, err = self.file_handler.open_file_dialog()
        if err:
            QMessageBox.critical(self, "Error Opening File", err)
        elif fp:
            self._action_open_file(fp, content, encoding)

    def _action_open_folder(self, path=None):
        if not path or not isinstance(path, str): path = QFileDialog.getExistingDirectory(self, "Open Folder",
                                                                                          self.project_manager.get_active_project_path() or os.path.expanduser(
                                                                                              "~"))
        if path: self.project_manager.open_project(path)

    def _action_close_project(self, path=None):
        if path := path if isinstance(path, str) else self.project_manager.get_active_project_path():
            self.project_manager.close_project(path)
        else:
            self.statusBar().showMessage("No active project to close.", 2000)

    def _on_theme_selected(self, theme_id):
        self.settings.set("last_theme_id", theme_id);
        self._apply_theme_and_icons(theme_id)

    def _on_tab_changed(self, index):
        self._update_window_title()
        widget = self.tab_widget.widget(index) if index != -1 else None
        is_editor = False
        
        # --- UPDATED: Auto-detect and update encoding dropdown ---
        self.encoding_combo.blockSignals(True)
        if isinstance(widget, EditorWidget):
            is_editor, (line, col) = True, widget.get_cursor_position()
            self.cursor_label.setText(f" Ln {line}, Col {col} ")
            data = self.editor_tabs_data.get(widget, {})
            encoding = data.get('encoding', 'utf-8')
            encoding_display_name = self.reverse_encoding_map.get(encoding, "UTF-8")
            self.encoding_label.setText(f" {encoding_display_name} ")
            
            # Update the toolbar dropdown
            if (idx := self.encoding_combo.findData(encoding)) != -1:
                self.encoding_combo.setCurrentIndex(idx)
            
            self.encoding_combo.setEnabled(bool(data.get('filepath')))
        else:
            self.cursor_label.setText("")
            self.encoding_label.setText("")
            self.encoding_combo.setEnabled(False)
            for i in range(self.tab_widget.count()):
                if (w := self.tab_widget.widget(i)) and isinstance(w,
                                                                   EditorWidget) and w.find_panel.isVisible(): w.hide_find_panel()
        
        self.encoding_combo.blockSignals(False)
        self.actions["find_replace"].setEnabled(is_editor)

    def _is_editor_modified(self, ed):
        return isinstance(ed, EditorWidget) and (data := self.editor_tabs_data.get(ed)) and hash(ed.get_text()) != data[
            'original_hash']

    def _on_content_changed(self, editor):
        if not (isinstance(editor, EditorWidget) and self.tab_widget.isAncestorOf(editor)): return
        mod, idx = self._is_editor_modified(editor), self.tab_widget.indexOf(editor)
        if idx != -1:
            txt = self.tab_widget.tabText(idx)
            if mod and not txt.endswith(' *'):
                self.tab_widget.setTabText(idx, f'{txt} *')
            elif not mod and txt.endswith(' *'):
                self.tab_widget.setTabText(idx, txt[:-2])
        self._update_window_title()
        if self.settings.get("auto_save_enabled"): self.auto_save_timer.start(
            self.settings.get("auto_save_delay_seconds", 3) * 1000)
        
        # --- NEW: Trigger draft save on content change ---
        if mod:
            self.draft_save_timer.start()

    def _update_window_title(self):
        proj = os.path.basename(self.project_manager.get_active_project_path() or "");
        current = ""
        if isinstance(w := self.tab_widget.currentWidget(), EditorWidget):
            current = os.path.basename(self.editor_tabs_data.get(w, {}).get('filepath') or self.tab_widget.tabText(
                self.tab_widget.currentIndex()).replace(" *", ""))
            if self._is_editor_modified(w): current += " *"
        self.setWindowTitle(" - ".join(filter(None, [current, proj, "PuffinPyEditor"])))

    def _action_save_file(self, editor_widget=None, save_as=False):
        editor = editor_widget or self.tab_widget.currentWidget()
        if not (isinstance(editor, EditorWidget) and (data := self.editor_tabs_data.get(editor))):
            return None

        content = editor.get_text()
        encoding = data.get('encoding', 'utf-8')
        
        # This will either do a 'Save As...' (if filepath is missing or save_as=True) or a direct 'Save'.
        new_fp, new_encoding = self.file_handler.save_file_content(data['filepath'], content, save_as, encoding=encoding)
        
        if new_fp:
            # Delete the draft file since changes are now permanent
            draft_path = helpers.get_draft_path(new_fp)
            if os.path.exists(draft_path):
                os.remove(draft_path)
                log.info(f"Removed draft file for saved file: {new_fp}")

            self.file_handler._add_to_recent_files(new_fp)

            # --- FIX: Reassign the entire dictionary for the editor to ensure its state is fully updated.
            # This robustly handles the transition from an unsaved "Untitled" file to a saved file with a path.
            self.editor_tabs_data[editor] = {
                'filepath': new_fp,
                'original_hash': hash(content),
                'encoding': new_encoding
            }
            # --- END FIX ---
            
            editor.set_filepath(new_fp)
            
            if (idx := self.tab_widget.indexOf(editor)) != -1:
                self.tab_widget.setTabText(idx, os.path.basename(new_fp))
                self.tab_widget.setTabToolTip(idx, new_fp)
                
            self.statusBar().showMessage(f"File saved: {os.path.basename(new_fp)}", 3000)
            self._on_content_changed(editor)  # This will remove the '*' modification marker
            self._on_tab_changed(self.tab_widget.currentIndex()) # Update status bar with encoding
            return new_fp
        
        self.statusBar().showMessage("Save cancelled.", 2000)
        return None

    def _action_save_as(self):
        self._action_save_file(save_as=True)

    def _action_save_all(self):
        saved_count = 0
        for i in range(self.tab_widget.count()):
            editor = self.tab_widget.widget(i)
            if self._is_editor_modified(editor):
                if self._action_save_file(editor_widget=editor):
                    saved_count += 1
        if saved_count > 0:
            self.statusBar().showMessage(f"Saved {saved_count} file(s).", 3000)

    def _action_close_tab_by_index(self, index):
        widget_to_close = self.tab_widget.widget(index)
        if not widget_to_close:
            return

        dummy_close_event = QCloseEvent()
        self._close_widget_safely(widget_to_close, dummy_close_event)

        if dummy_close_event.isAccepted():
            if self.tab_widget.indexOf(widget_to_close) != -1:
                self.tab_widget.removeTab(self.tab_widget.indexOf(widget_to_close))
            widget_to_close.deleteLater()
            if self.tab_widget.count() == 0:
                self._add_new_tab(is_placeholder=True)

    def _close_widget_safely(self, widget, event):
        # --- MODIFIED: No more save prompt, just save a draft if needed ---
        if isinstance(widget, EditorWidget):
            if self._is_editor_modified(widget):
                self._save_draft(widget)
            if widget in self.editor_tabs_data:
                del self.editor_tabs_data[widget]

        event.accept()

    def _update_recent_files_menu(self):
        self.recent_files_menu.clear();
        recent = self.settings.get("recent_files", []);
        self.recent_files_menu.setEnabled(bool(recent))
        for i, fp in enumerate(recent[:10]):
            act = QAction(f"&{i + 1} {os.path.basename(fp)}", self);
            act.setData(fp);
            act.setToolTip(fp);
            act.triggered.connect(self._action_open_recent_file);
            self.recent_files_menu.addAction(act)

    def _action_open_recent_file(self):
        if act := self.sender(): self._action_open_file(act.data())

    def _trigger_file_linter(self):
        if (editor := self.tab_widget.currentWidget()) and (
                fp := self.editor_tabs_data.get(editor, {}).get('filepath')):
            self.linter_manager.lint_file(fp)

    def _show_about_dialog(self):
        QMessageBox.about(self, "About", f"PuffinPyEditor v{versioning.APP_VERSION}")

    def _open_github_link(self):
        QDesktopServices.openUrl(QUrl("https://github.com/Stelliro/PuffinPyEditor"))

    def _auto_save_current_tab(self):
        if self._is_editor_modified(ed := self.tab_widget.currentWidget()):
            self._action_save_file(editor_widget=ed)

    def _on_editor_settings_changed(self):
        [w.apply_styles_and_settings() for i in range(self.tab_widget.count()) if
         isinstance(w := self.tab_widget.widget(i), EditorWidget)]

    def _action_open_preferences(self):
        if not self.preferences_dialog or not self.preferences_dialog.isVisible():
            self.preferences_dialog = PreferencesDialog(self.theme_manager, self.git_manager, self.github_manager, self.plugin_manager,
                                                        self.puffin_api, self)
            self.preferences_dialog.settings_changed_for_editor_refresh.connect(self._on_editor_settings_changed);
            self.preferences_dialog.theme_changed_signal.connect(self._on_theme_selected)
        self.preferences_dialog.show();
        self.preferences_dialog.raise_();
        self.preferences_dialog.activateWindow()

    def _action_force_quit(self):
        log.warning("Force Quit triggered.");
        QApplication.instance().quit()

    def _goto_definition_result(self, fp, line, col):
        if not fp: self.statusBar().showMessage("Definition not found", 3000); return
        np = os.path.normpath(fp)
        for i in range(self.tab_widget.count()):
            if isinstance(ed := self.tab_widget.widget(i), EditorWidget) and self.editor_tabs_data.get(ed, {}).get(
                    'filepath') == np:
                self.tab_widget.setCurrentIndex(i);
                ed.goto_line_and_column(line, col);
                return
        self._action_open_file(np);
        if isinstance(cur := self.tab_widget.currentWidget(), EditorWidget):
            cur.goto_line_and_column(line, col)
        else:
            log.warning(f"Could not jump to definition. Expected editor for {np}.")

    def _shutdown_plugins(self):
        log.info("Shutting down plugins...");
        [p.instance.shutdown() for p in self.plugin_manager.get_loaded_plugins()
         if hasattr(p.instance, 'shutdown')]

    def _shutdown_managers(self):
        log.info("Shutting down core managers...");
        [m.shutdown() for m in
         [self.completion_manager, self.github_manager, self.git_manager,
          self.linter_manager] if hasattr(m, 'shutdown')]

    def closeEvent(self, e: QCloseEvent):
        if self._is_app_closing: e.accept(); return
        self._is_app_closing = True

        open_fps = []
        for i in range(self.tab_widget.count()):
            widget = self.tab_widget.widget(i)
            if isinstance(widget, EditorWidget):
                data = self.editor_tabs_data.get(widget)
                if data and (filepath := data.get('filepath')):
                    open_fps.append(filepath)
                # --- NEW: Save final drafts on close ---
                if self._is_editor_modified(widget):
                    self._save_draft(widget)

        settings_manager.set("open_files", open_fps, save_immediately=False)
        if hasattr(self, 'explorer_panel'):
            settings_manager.set("explorer_expanded_paths", self.explorer_panel.get_expanded_paths(),
                                 save_immediately=False)
        self.project_manager.save_session()
        self.settings.save()

        self._shutdown_plugins()
        self._shutdown_managers()
        log.info("PuffinPyEditor exited cleanly.")
        e.accept()

    def toggle_find_panel(self):
        if isinstance(ed := self.tab_widget.currentWidget(), EditorWidget):
            ed.toggle_find_panel()
        else:
            log.warning("Find called on non-editor widget.")

    def _on_active_project_changed(self, cur, _):
        if not cur: return
        root = cur;
        while parent := root.parent(): root = parent
        if (data := root.data(0, Qt.ItemDataRole.UserRole)) and (path := data.get('path')):
            self.project_manager.set_active_project(path)
            # Update completion manager context when active project changes
            self.completion_manager.update_project_path(path)

    def _on_item_created(self, item_type, path):
        if item_type == 'file': self._add_header_to_new_file(path)

    def _generate_header_line(self, file_path: str):
        ext = os.path.splitext(file_path)[1].lower()
        start = self.COMMENT_MAP.get(ext)
        if not start or not (root := self.project_manager.get_active_project_path()) or not file_path.startswith(
                root): return None
        end_comment = self.END_COMMENT_MAP.get(start, '')

        # Ensure project basename is part of the path if not root
        rel_path_to_proj_root = os.path.relpath(file_path, root)
        final_path_in_header = os.path.join(os.path.basename(root), rel_path_to_proj_root).replace(os.sep, '/')

        return f"{start} PuffinPyEditor/{final_path_in_header} {end_comment}\n"

    def _add_header_to_new_file(self, file_path):
        if not (header := self._generate_header_line(file_path)): return
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(header);
                log.info(f"Autopopulated header for {file_path}")
        except IOError as e:
            log.error(f"Failed to write header to {file_path}: {e}")

    def _update_file_header(self, file_path):
        if not (header := self._generate_header_line(file_path)): return
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            if not lines:
                lines.append(header)
            elif re.compile(r"^(#|//|<!--|\/\*)\s*PuffinPyEditor/.*").match(lines[0]):
                lines[0] = header
            else:
                lines.insert(0, header)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.writelines(lines);
                log.info(f"Updated header for: {file_path}")
        except Exception as e:
            log.error(f"Failed to update header for {file_path}: {e}", exc_info=True)
            
    def _on_encoding_changed_from_dropdown(self, index: int):
        editor = self.tab_widget.currentWidget()
        if not isinstance(editor, EditorWidget):
            return

        new_encoding = self.encoding_combo.itemData(index)
        data = self.editor_tabs_data.get(editor)
        if not data or new_encoding == data.get('encoding'):
            return

        reply = QMessageBox.question(
            self,
            "Change File Encoding",
            f"This will re-save the file '{os.path.basename(data.get('filepath'))}' with the new encoding '{self.encoding_combo.currentText()}'.\n\n"
            "This may alter the file content if it contains characters not supported by the new encoding. Are you sure you want to continue?",
            QMessageBox.StandardButton.Save | QMessageBox.StandardButton.Cancel,
            QMessageBox.StandardButton.Cancel
        )

        if reply == QMessageBox.StandardButton.Save:
            self._resave_with_new_encoding(editor, new_encoding)
        else:
            # Revert the dropdown to the file's actual encoding
            self._on_tab_changed(self.tab_widget.currentIndex())

    def _resave_with_new_encoding(self, editor: EditorWidget, new_encoding: str):
        data = self.editor_tabs_data.get(editor)
        if not data or not data.get('filepath'):
            return # Should not happen as dropdown is disabled for unsaved files

        content = editor.get_text()
        filepath = data['filepath']

        # Use the file_handler to save with the new encoding
        saved_path, final_encoding = self.file_handler.save_file_content(filepath, content, save_as=False, encoding=new_encoding)
        
        if saved_path:
            # Update the editor's data store with the new encoding and reset the hash
            data['encoding'] = final_encoding
            data['original_hash'] = hash(content)
            self._on_content_changed(editor) # Update modification status
            self.statusBar().showMessage(f"File saved with new encoding: {self.reverse_encoding_map.get(final_encoding, final_encoding)}", 4000)
        else:
            self.statusBar().showMessage("Failed to re-save file with new encoding.", 4000)
            self._on_tab_changed(self.tab_widget.currentIndex()) # Revert dropdown on failure

    def _save_draft(self, editor: EditorWidget):
        data = self.editor_tabs_data.get(editor)
        if not data or not data['filepath']:
            return  # Can't save a draft for an unsaved file

        draft_path = helpers.get_draft_path(data['filepath'])
        content = editor.get_text()
        encoding = data.get('encoding', 'utf-8')
        try:
            with open(draft_path, 'w', encoding=encoding) as f:
                f.write(content)
            log.info(f"Saved draft for {os.path.basename(data['filepath'])}")
        except (IOError, OSError) as e:
            log.error(f"Failed to write draft file to {draft_path}: {e}")

    def _save_current_draft(self):
        if editor := self.tab_widget.currentWidget():
            if isinstance(editor, EditorWidget) and self._is_editor_modified(editor):
                self._save_draft(editor)
```

### File: `/ui/editor_widget.py`
```py
# /ui/editor_widget.py
"""
PuffinPyEditor - Advanced Editor Widget
"""
from __future__ import annotations
from typing import Optional, Set, Dict, List, Tuple, TYPE_CHECKING
import re
import os
from math import cos, sin

from PyQt6.QtWidgets import (QWidget, QPlainTextEdit, QTextEdit, QHBoxLayout, QVBoxLayout, QSplitter, QApplication)
from PyQt6.QtGui import (QPainter, QColor, QFont, QPaintEvent, QTextFormat,
                         QTextBlockFormat, QPen, QTextCursor, QMouseEvent, QFontMetrics,
                         QKeyEvent, QTextDocument, QKeySequence, QWheelEvent, QPolygonF, QSyntaxHighlighter)
from PyQt6.QtCore import (Qt, QSize, QRect, QRectF, QPointF, QEvent, pyqtSignal,
                          QObject, QTimer, QPoint)
import qtawesome as qta
from app_core.settings_manager import settings_manager
from .widgets.find_panel import FindPanel
from utils.logger import log

if TYPE_CHECKING:
    from app_core.theme_manager import ThemeManager
    from app_core.completion_manager import CompletionManager
    from app_core.puffin_api import PuffinPluginAPI


class HighlightManager(QObject):
    """Manages custom line highlights from multiple sources (e.g., linter, user)."""
    highlights_changed = pyqtSignal()

    def __init__(self):
        super().__init__()
        self._highlights: Dict[str, Dict[int, QColor]] = {}

    def add_highlight(self, source_id: str, line_number: int, color: QColor):
        if source_id not in self._highlights: self._highlights[source_id] = {}
        self._highlights[source_id][line_number] = color
        self.highlights_changed.emit()

    def clear_highlights(self, source_id: str):
        if source_id in self._highlights:
            self._highlights.pop(source_id, None)
            self.highlights_changed.emit()

    def get_all_highlights(self) -> Dict[int, QColor]:
        combined = {}
        for source in self._highlights.values(): combined.update(source)
        return combined


class GutterWidget(QWidget):
    """The widget responsible for drawing the line number gutter."""
    RULER_WIDTH = 4

    def __init__(self, editor: 'CodeEditor'):
        super().__init__(editor.container)
        self.editor = editor
        self.setMouseTracking(True)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.hovered_line = -1

    def sizeHint(self) -> QSize:
        return QSize(self.editor.calculate_gutter_width(), 0)

    def paintEvent(self, event: QPaintEvent):
        self.editor.paint_gutter_event(event, self)

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self.editor.handle_gutter_left_click(event.pos())

    def mouseMoveEvent(self, event: QMouseEvent):
        block = self.editor.cursorForPosition(event.pos()).block()
        line_num = block.blockNumber() if block.isValid() else -1
        if line_num != self.hovered_line:
            self.hovered_line = line_num
            self.update()
        super().mouseMoveEvent(event)

    def leaveEvent(self, event: QEvent):
        self.hovered_line = -1
        self.update()
        super().leaveEvent(event)


class MiniMapWidget(QWidget):
    def __init__(self, editor: 'CodeEditor'):
        super().__init__(editor.container)
        self.editor = editor
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setMinimumWidth(80)
        self.editor.verticalScrollBar().valueChanged.connect(self.update)
        self.editor.document().blockCountChanged.connect(self.update)

    def paintEvent(self, event: QPaintEvent):
        painter, colors = QPainter(self), self.editor.container.theme_manager.current_theme_data.get('colors', {})
        painter.fillRect(self.rect(), QColor(colors.get('editorGutter.background', '#16161e')))
        doc, v_scroll = self.editor.document(), self.editor.verticalScrollBar()
        if doc.blockCount() == 0: return
        line_height_map, total_content_height = 2.0, doc.blockCount() * 2.0
        scale = min(1.0, self.height() / total_content_height if total_content_height > 0 else 1.0)
        scroll_proportion = v_scroll.value() / (v_scroll.maximum() or 1)
        scroll_offset = -(total_content_height - self.height()) * scroll_proportion if total_content_height > self.height() else 0
        painter.setPen(QColor(colors.get('editor.foreground', '#c0caf5')))
        for i in range(doc.blockCount()):
            block = doc.findBlockByNumber(i); text = block.text().lstrip()
            if not text: continue
            y = scroll_offset + (i * line_height_map * scale)
            if y > self.height(): break
            x = (len(block.text()) - len(text)) * 1.5; width = len(text) * 0.8
            painter.drawRect(QRectF(x, y, width, max(1.0, line_height_map * scale)))
        first_visible = self.editor.firstVisibleBlock().blockNumber()
        visible_blocks = self.editor.viewport().height() // self.editor.fontMetrics().height() if self.editor.fontMetrics().height() > 0 else 0
        viewport_y = scroll_offset + (first_visible * line_height_map * scale)
        viewport_h = max(1.0, visible_blocks * line_height_map * scale)
        viewport_rect = QRectF(0, viewport_y, self.width() - 1, viewport_h)
        painter.fillRect(viewport_rect, QColor(colors.get('editorGutter.ruler.color', '#41a6b530')))
        painter.setPen(QPen(QColor(colors.get('editorGutter.ruler.color', '#41a6b5')), 1)); painter.drawRect(viewport_rect)

    def mousePressEvent(self, e: QMouseEvent): self._scroll_from_mouse(e.position())
    def mouseMoveEvent(self, e: QMouseEvent):
        if e.buttons() & Qt.MouseButton.LeftButton: self._scroll_from_mouse(e.position())
    def _scroll_from_mouse(self, pos: QPointF):
        v_scroll = self.editor.verticalScrollBar()
        v_scroll.setValue(int((pos.y() / self.height()) * v_scroll.maximum()) if self.height() > 0 else 0)


class CodeOutlineMinimap(MiniMapWidget):
    LANG_PATTERNS = {
        'python': [(re.compile(r"^\s*class\s+(\w+)"), 'class', 1), (re.compile(r"^\s*def\s+(_?[a-zA-Z0-9_]+)"), 'def', 1)],
        'javascript': [(re.compile(r"^\s*class\s+(\w+)"), 'class', 1), (re.compile(r"^\s*function\s*\*?\s*(\w*)"), 'def', 1), (re.compile(r"^\s*(?:const|let|var)\s+([\w$]+)\s*=\s*(?:async\s*)?\("), 'def', 1)],
        'csharp': [(re.compile(r"^\s*(?:public|private|protected|internal)?\s*(?:sealed|abstract)?\s*class\s+(\w+)"), 'class', 1), (re.compile(r"^\s*(?:public|private|protected|internal)?\s*struct\s+(\w+)"), 'class', 1), (re.compile(r"^\s*(?:public|private|protected|internal)?\s*(?:static|virtual|override|async|unsafe)?\s*[\w<>\[\],]+\s+([\w]+)\s*\("), 'def', 1)],
        'cpp': [(re.compile(r"^\s*class\s+(\w+)"), 'class', 1), (re.compile(r"^\s*struct\s+(\w+)"), 'class', 1), (re.compile(r"^\w[\w\s\*&<>,:]*?([\w_]+)\s*\([^;]*\)\s*\{?$"), 'def', 1)],
        'rust': [(re.compile(r"^\s*struct\s+(\w+)"), 'class', 1), (re.compile(r"^\s*enum\s+(\w+)"), 'class', 1), (re.compile(r"^\s*(?:pub\s)?(?:async\s)?fn\s+(\w+)"), 'def', 1)]}
    LANG_MAP = {'.py': 'python', '.pyw': 'python', '.js': 'javascript', '.ts': 'javascript', '.cs': 'csharp', '.c': 'cpp', '.cpp': 'cpp', '.h': 'cpp', '.hpp': 'cpp', '.rs': 'rust'}
    def __init__(self, editor: 'CodeEditor', language_ext: str):
        super().__init__(editor); self.setMouseTracking(True); self.clickable_regions, self.hovered_region_index = [], -1
        self.patterns = self.LANG_PATTERNS.get(self.LANG_MAP.get(language_ext, ''), [])
        self._load_icons()
    def _load_icons(self):
        self.class_icon, self.def_icon = qta.icon('fa5s.cubes', color="#E5C07B"), qta.icon('fa5s.cube', color="#61AFEF")
    def _get_indent(self, text: str): return len(text) - len(text.lstrip())
    def _precompute_structure(self) -> List[Tuple[int, int, str, str]]:
        structure, doc = [], self.editor.document()
        if not self.patterns: return structure
        for i in range(doc.blockCount()):
            text = doc.findBlockByNumber(i).text()
            if not text.strip(): continue
            for pattern, item_type, name_group_idx in self.patterns:
                if match := pattern.match(text):
                    if name := match.group(name_group_idx): structure.append((i, self._get_indent(text), item_type, name)); break
        return structure
    def _format_name(self, name: str): return name.lstrip('_').replace('_', ' ').title()
    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            for i, (region_rect, line_num) in enumerate(self.clickable_regions):
                if region_rect.contains(event.position()):
                    cursor = QTextCursor(self.editor.document().findBlockByNumber(line_num)); self.editor.setTextCursor(cursor); self.editor.centerCursor(); return
            v_scroll = self.editor.verticalScrollBar(); v_scroll.setValue(int((event.position().y() / self.height()) * v_scroll.maximum())) if self.height() > 0 else None
    def mouseMoveEvent(self, event: QMouseEvent):
        new_hover_index = next((i for i, (rr, _) in enumerate(self.clickable_regions) if rr.contains(event.position())), -1)
        if new_hover_index != self.hovered_region_index: self.hovered_region_index = new_hover_index; self.update()
        super().mouseMoveEvent(event)
    def leaveEvent(self, event: QEvent):
        if self.hovered_region_index != -1: self.hovered_region_index = -1; self.update()
        super().leaveEvent(event)
    def paintEvent(self, event: QPaintEvent):
        painter = QPainter(self); painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        colors = self.editor.container.theme_manager.current_theme_data.get('colors', {})
        painter.fillRect(self.rect(), QColor(colors.get('editorGutter.background', '#16161e')))
        structure = self._precompute_structure()
        if not structure: super().paintEvent(event); return
        self._draw_structure_items(painter, colors, structure); self._draw_viewport_indicator(painter, colors)
    def _draw_structure_items(self, painter, colors, structure):
        self.clickable_regions.clear(); row_height, icon_size, class_indent, def_indent = 24, 14, 10, 25
        class_color, func_color, label_font = QColor(colors.get('syntax.className')), QColor(colors.get('syntax.functionName')), self.editor.font(); label_font.setPointSizeF(label_font.pointSizeF() * 0.9); painter.setFont(label_font)
        font_metrics, v_scroll = painter.fontMetrics(), self.editor.verticalScrollBar()
        total_content_height = len(structure) * row_height; scrollable_height = max(0, total_content_height - self.height())
        scroll_offset = -scrollable_height * (v_scroll.value() / (v_scroll.maximum() or 1))
        for i, (line_num, indent, item_type, name) in enumerate(structure):
            y_pos = i * row_height + scroll_offset
            if y_pos + row_height < 0 or y_pos > self.height(): continue
            item_rect = QRectF(0, y_pos, self.width(), row_height); self.clickable_regions.append((item_rect, line_num))
            if i == self.hovered_region_index: painter.fillRect(item_rect, QColor(colors.get('editor.lineHighlightBackground')).lighter(110))
            icon, indent_x = (self.class_icon, class_indent) if item_type == "class" else (self.def_icon, def_indent)
            icon.paint(painter, QRect(indent_x, int(y_pos + (row_height - icon_size) / 2), icon_size, icon_size))
            painter.setPen(class_color if item_type == "class" else func_color)
            text_x = indent_x + icon_size + 5
            painter.drawText(QPointF(text_x, y_pos + (row_height - font_metrics.height()) / 2 + font_metrics.ascent()), font_metrics.elidedText(self._format_name(name), Qt.TextElideMode.ElideRight, self.width() - text_x - 5))
    def _draw_viewport_indicator(self, painter, colors):
        doc = self.editor.document(); total_doc_lines = doc.blockCount()
        if total_doc_lines == 0: return
        first_visible = self.editor.firstVisibleBlock().blockNumber()
        visible_lines = self.editor.viewport().height() // self.editor.fontMetrics().height() if self.editor.fontMetrics().height() > 0 else 0
        indicator_y = (first_visible / total_doc_lines) * self.height(); indicator_h = max(3.0, (visible_lines / total_doc_lines) * self.height())
        viewport_rect = QRectF(0, indicator_y, self.width() - 1, indicator_h)
        painter.fillRect(viewport_rect, QColor(colors.get('editorGutter.ruler.color', '#41a6b530')))
        painter.setPen(QPen(QColor(colors.get('editorGutter.ruler.color', '#41a6b5')), 1)); painter.drawRect(viewport_rect)


class CodeEditor(QPlainTextEdit):
    def __init__(self, parent_container: 'EditorWidget'):
        super().__init__(parent_container)
        self.container = parent_container
        self.highlight_manager = self.container.highlight_manager
        self.multi_selection_source_id = f"multi_select_{id(self)}"
        self.highlight_manager.highlights_changed.connect(self.viewport().update)
        self.cursorPositionChanged.connect(self.update_extra_selections)

    def keyPressEvent(self, event: QKeyEvent):
        if event.modifiers() & Qt.KeyboardModifier.ControlModifier and event.key() == Qt.Key.Key_Slash: self._toggle_comment(); event.accept(); return
        if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter): self._auto_indent(); event.accept(); return
        if event.matches(QKeySequence.StandardKey.Find): self.container.toggle_find_panel(); event.accept(); return
        if event.key() == Qt.Key.Key_Escape:
            if self.highlight_manager._highlights.get(self.multi_selection_source_id):
                self.highlight_manager.clear_highlights(self.multi_selection_source_id)
                self.setFocus(); event.accept(); return
        super().keyPressEvent(event)

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton and QApplication.keyboardModifiers() & Qt.KeyboardModifier.ControlModifier:
            self.handle_multi_select_click(event)
            event.accept()
        else:
            self.highlight_manager.clear_highlights(self.multi_selection_source_id)
            super().mousePressEvent(event)
    
    def handle_multi_select_click(self, event: QMouseEvent):
        cursor = self.cursorForPosition(event.pos())
        selections = self.highlight_manager._highlights.get(self.multi_selection_source_id, {})
        color_hex = self.container.theme_manager.current_theme_data.get('colors', {}).get('editor.userHighlightBackground', '#83c0924D')
        selection_color = QColor(color_hex)
        line_num = cursor.blockNumber() + 1
        if line_num in selections: del selections[line_num]
        else: selections[line_num] = selection_color
        self.highlight_manager._highlights[self.multi_selection_source_id] = selections
        self.highlight_manager.highlights_changed.emit()

    def paintEvent(self, event: QPaintEvent):
        painter, event_rect = QPainter(self.viewport()), event.rect()
        all_highlights = self.highlight_manager.get_all_highlights()
        for line_num, color in all_highlights.items():
            block = self.document().findBlockByNumber(line_num - 1)
            if block.isValid() and block.isVisible():
                block_rect = self.blockBoundingGeometry(block).translated(self.contentOffset())
                if block_rect.intersects(event_rect):
                    full_width_rect = QRectF(self.viewport().rect().left(), block_rect.top(), self.viewport().rect().width(), block_rect.height())
                    painter.fillRect(full_width_rect, color)
        super().paintEvent(event); self.paint_indentation_guides(event)

    def handle_gutter_left_click(self, pos: QPointF):
        block = self.cursorForPosition(pos).block()
        if not block.isValid(): return
        line_num = block.blockNumber() + 1
        source_id, source_highlights = "user_breakpoint", self.highlight_manager._highlights.get("user_breakpoint", {})
        if line_num in source_highlights: del source_highlights[line_num]
        else: source_highlights[line_num] = QColor(self.container.theme_manager.current_theme_data.get('colors', {}).get('editor.breakpoint.color', '#dc143c'))
        self.highlight_manager._highlights[source_id] = source_highlights
        self.highlight_manager.highlights_changed.emit()

    def update_extra_selections(self):
        selections = []
        if self.hasFocus():
            selection = QTextEdit.ExtraSelection(); selection.format.setBackground(QColor(self.container.theme_manager.current_theme_data.get('colors', {}).get('editor.lineHighlightBackground', '#222436')))
            selection.format.setProperty(QTextFormat.Property.FullWidthSelection, True); selection.cursor = self.textCursor(); selection.cursor.clearSelection(); selections.append(selection)
        self.setExtraSelections(selections); self.container.gutter_widget.update()

    def calculate_gutter_width(self) -> int:
        if not self.container.settings.get("show_line_numbers", True): return 0
        return GutterWidget.RULER_WIDTH + self.fontMetrics().horizontalAdvance('9' * len(str(max(1, self.blockCount())))) + 15

    def paint_gutter_event(self, event: QPaintEvent, gutter: GutterWidget):
        painter = QPainter(gutter)
        colors = self.container.theme_manager.current_theme_data.get('colors', {})
        # CORRECTED: Added fallback values to all QColor lookups.
        painter.fillRect(event.rect(), QColor(colors.get('editorGutter.background', '#2f383e')))
        block = self.firstVisibleBlock()
        if not block.isValid(): return
        highlights, top = self.highlight_manager.get_all_highlights(), int(self.blockBoundingGeometry(block).translated(self.contentOffset()).top())
        block_num = block.blockNumber()
        
        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and top + int(self.blockBoundingRect(block).height()) >= event.rect().top():
                is_current = self.textCursor().blockNumber() == block_num
                is_hovered = block_num == gutter.hovered_line
                block_height = int(self.blockBoundingRect(block).height())
                if color := highlights.get(block_num + 1):
                    painter.fillRect(QRect(0, top, gutter.width(), block_height), color)
                elif is_hovered:
                    painter.fillRect(QRect(0, top, gutter.width(), block_height), QColor(colors.get('editorGutter.hoverBackground', '#ffffff1a')))
                
                if is_current and self.hasFocus():
                    # CORRECTED: Safely get the ruler color with a fallback.
                    ruler_color_str = colors.get('editorGutter.ruler.color', colors.get('accent'))
                    painter.fillRect(QRectF(0, top, gutter.RULER_WIDTH, block_height), QColor(ruler_color_str))

                active_fg = QColor(colors.get('editorLineNumber.activeForeground', '#d3c6aa'))
                default_fg = QColor(colors.get('editorLineNumber.foreground', '#5f6c6d'))
                painter.setPen(active_fg if is_current and self.hasFocus() else default_fg)
                painter.setFont(self.font())
                painter.drawText(QRect(gutter.RULER_WIDTH, top, gutter.width() - gutter.RULER_WIDTH - 5, block_height), Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter, str(block_num + 1))
            
            top += int(self.blockBoundingRect(block).height())
            block, block_num = block.next(), block_num + 1

    def paint_indentation_guides(self, event: QPaintEvent):
        painter = QPainter(self.viewport()); pen = QPen(QColor(self.container.theme_manager.current_theme_data.get('colors', {}).get('editorIndentGuide.background', '#3b4261'))); pen.setStyle(Qt.PenStyle.DotLine); painter.setPen(pen)
        indent_width = self.container.settings.get("indent_width", 4)
        if indent_width <= 0: return
        tab_width, offset = self.fontMetrics().horizontalAdvance(' ') * indent_width, self.contentOffset()
        block = self.firstVisibleBlock()
        while block.isValid() and block.isVisible():
            geom, indent_level = self.blockBoundingGeometry(block), len(block.text()) - len(block.text().lstrip(' '))
            for i in range(1, (indent_level // indent_width) + 1):
                if (x := i * tab_width + offset.x() - 1) > 0: painter.drawLine(int(x), int(geom.top() + offset.y()), int(x), int(geom.bottom() + offset.y()))
            block = block.next()

    def _auto_indent(self):
        cursor = self.textCursor(); indentation = (t := cursor.block().text())[:len(t) - len(t.lstrip())]
        cursor.insertBlock(); cursor.insertText(indentation)
        
    def _toggle_comment(self):
        cursor = self.textCursor(); start_pos, end_pos = cursor.selectionStart(), cursor.selectionEnd()
        doc = self.document(); start_block, end_block = doc.findBlock(start_pos), doc.findBlock(end_pos)
        if cursor.position() == end_pos and cursor.columnNumber() == 0 and start_pos != end_pos: end_block = end_block.previous()
        
        blocks_to_process = []
        block = start_block
        while block.isValid() and block.position() <= end_block.position():
            blocks_to_process.append(block); block = block.next()
            
        comment_char = self.container.get_comment_char()
        are_all_commented = all(b.text().lstrip().startswith(comment_char) for b in blocks_to_process if b.text().strip())
        
        cursor.beginEditBlock()
        for block in blocks_to_process:
            bc, text = QTextCursor(block), block.text()
            if are_all_commented:
                if (index := text.find(f'{comment_char} ')) != -1: bc.setPosition(block.position() + index); bc.setPosition(block.position() + index + len(comment_char) + 1, QTextCursor.MoveMode.KeepAnchor)
                elif (index := text.find(comment_char)) != -1: bc.setPosition(block.position() + index); bc.setPosition(block.position() + index + len(comment_char), QTextCursor.MoveMode.KeepAnchor)
                else: continue
                bc.removeSelectedText()
            else:
                bc.movePosition(QTextCursor.MoveOperation.StartOfLine); bc.insertText(f'{comment_char} ')
        cursor.endEditBlock()


class EditorWidget(QWidget):
    content_possibly_changed, cursor_position_display_updated, status_message_requested = pyqtSignal(), pyqtSignal(int, int), pyqtSignal(str, int)
    def __init__(self, puffin_api: 'PuffinPluginAPI', completion_manager: 'CompletionManager', highlight_manager: HighlightManager, theme_manager: 'ThemeManager', parent: Optional[QWidget] = None):
        super().__init__(parent); self.puffin_api, self.completion_manager, self.theme_manager, self.settings, self.highlight_manager = puffin_api, completion_manager, theme_manager, settings_manager, highlight_manager
        self.filepath: Optional[str] = None; self.highlighter: Optional[QSyntaxHighlighter] = None
        self.find_panel, self.text_area = FindPanel(self.theme_manager, self), CodeEditor(self)
        self.find_panel.hide(); self.gutter_widget, self.minimap_widget = GutterWidget(self.text_area), self._create_minimap()
        self._setup_layout(); self._connect_signals(); self.apply_styles_and_settings()

    def _create_minimap(self) -> MiniMapWidget:
        file_ext = os.path.splitext(self.filepath or '')[1].lower()
        if file_ext in {'.py', '.js', '.ts', '.cs', '.cpp', '.h', '.hpp', '.rs'}: return CodeOutlineMinimap(self.text_area, language_ext=file_ext)
        return MiniMapWidget(self.text_area)

    def _setup_layout(self):
        self.content_splitter = QSplitter(Qt.Orientation.Horizontal, self)
        editor_area_widget = QWidget(); editor_layout = QHBoxLayout(editor_area_widget)
        editor_layout.setContentsMargins(0, 0, 0, 0); editor_layout.setSpacing(0)
        editor_layout.addWidget(self.gutter_widget); editor_layout.addWidget(self.text_area, 1)
        self.content_splitter.addWidget(editor_area_widget); self.content_splitter.addWidget(self.minimap_widget)
        self.content_splitter.setSizes([800, 150]); self.content_splitter.setHandleWidth(4)
        self.main_layout = QVBoxLayout(self); self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0); self.main_layout.addWidget(self.find_panel)
        self.main_layout.addWidget(self.content_splitter, 1)

    def _connect_signals(self):
        self.text_area.blockCountChanged.connect(self._update_widget_geometries)
        self.text_area.updateRequest.connect(self._on_update_request)
        self.text_area.cursorPositionChanged.connect(self._on_cursor_position_changed)
        self.text_area.textChanged.connect(self.content_possibly_changed.emit)
        self.find_panel.close_requested.connect(self.hide_find_panel)
        self.find_panel.status_message_requested.connect(self.status_message_requested)

    def _on_update_request(self, rect: QRect, dy: int):
        if dy: self.gutter_widget.scroll(0, dy)
        else: self.gutter_widget.update(0, rect.y(), self.gutter_widget.width(), rect.height())
        if rect.contains(self.text_area.viewport().rect()): self._update_widget_geometries()

    def _update_widget_geometries(self): self.gutter_widget.setFixedWidth(self.text_area.calculate_gutter_width())
    def _on_cursor_position_changed(self): self.cursor_position_display_updated.emit(*self.get_cursor_position())
    def apply_styles_and_settings(self):
        font = QFont(self.settings.get("font_family"), self.settings.get("font_size")); self.text_area.setFont(font)
        self.text_area.setTabStopDistance(self.fontMetrics().horizontalAdvance(' ') * self.settings.get("indent_width", 4))
        self.update_theme()
    def update_theme(self):
        colors = self.theme_manager.current_theme_data.get("colors", {}); stylesheet = f"QPlainTextEdit {{ background-color: {colors.get('editor.background')}; color: {colors.get('editor.foreground')}; border: none; selection-background-color: {colors.get('editor.selectionBackground')}; }} QSplitter::handle {{ background-color: {colors.get('editorGutter.background')}; }} QSplitter::handle:hover {{ background-color: {colors.get('accent')}; }}"
        self.text_area.setStyleSheet(stylesheet); self.content_splitter.setStyleSheet(stylesheet)
        if hasattr(self.minimap_widget, '_load_icons'): self.minimap_widget._load_icons()
        if self.highlighter: self.highlighter.rehighlight()
        self._update_widget_geometries(); self.gutter_widget.update(); self.minimap_widget.update()
    def set_filepath(self, fp: Optional[str]):
        self.filepath = fp; new_minimap = self._create_minimap()
        if new_minimap.__class__ != self.minimap_widget.__class__: self.content_splitter.replaceWidget(1, new_minimap); self.minimap_widget.deleteLater(); self.minimap_widget = new_minimap
    def get_cursor_position(self) -> tuple[int, int]: c = self.text_area.textCursor(); return c.blockNumber() + 1, c.columnNumber()
    def goto_line_and_column(self, line: int, col: int):
        cursor = QTextCursor(self.document().findBlockByNumber(line - 1)); cursor.movePosition(QTextCursor.MoveOperation.Right, QTextCursor.MoveMode.MoveAnchor, col)
        self.text_area.setTextCursor(cursor); self.text_area.setFocus()
    def set_text(self, text: str): self.text_area.setPlainText(text)
    def get_text(self) -> str: return self.text_area.toPlainText()
    def set_highlighter(self, h_class):
        if self.highlighter: self.highlighter.setDocument(None)
        if h_class: self.highlighter = h_class(self.text_area.document(), self.theme_manager)
    def toggle_find_panel(self):
        if self.find_panel.isVisible(): self.hide_find_panel()
        else: self.show_find_panel()
    def show_find_panel(self): self.find_panel.show(); self.find_panel.connect_editor(self)
    def hide_find_panel(self): self.find_panel.hide(); self.text_area.setFocus()
    def get_comment_char(self) -> str: return self.puffin_api.get_main_window().COMMENT_MAP.get(os.path.splitext(self.filepath or "")[1].lower(), '#')
    def find_next(self, query: str, flags: QTextDocument.FindFlag) -> bool: return self.text_area.find(query, flags)
    def replace_current(self, query: str, replace: str, flags: QTextDocument.FindFlag) -> bool:
        c = self.text_area.textCursor()
        if c.hasSelection() and c.selectedText() == query: c.insertText(replace); return True
        if self.find_next(query, flags): self.text_area.textCursor().insertText(replace); return True
        return False
    def replace_all(self, query: str, replace: str, flags: QTextDocument.FindFlag) -> int:
        count, cursor = 0, self.text_area.textCursor(); cursor.beginEditBlock()
        cursor.movePosition(QTextCursor.MoveOperation.Start); self.text_area.setTextCursor(cursor)
        while self.find_next(query, flags): self.text_area.textCursor().insertText(replace); count += 1
        cursor.endEditBlock(); return count
    def document(self): return self.text_area.document()
```

### File: `/ui/__init__.py`
```py

```

### File: `/ui/widgets/splash_screen.py`
```py
# /ui/widgets/splash_screen.py
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QApplication
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QTimer, QSize
import qtawesome as qta


class SplashScreen(QWidget):
    """
    A modern, frameless splash screen that shows loading status and
    fades out smoothly.
    """

    def __init__(self):
        super().__init__()
        # Set window flags for a frameless, top-level splash screen
        self.setWindowFlags(
            Qt.WindowType.SplashScreen |
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        self.setFixedSize(320, 200)

        # Main layout
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(20, 20, 20, 20)

        # Puffin Icon
        # --- FIX: Create an empty QLabel and then set its QPixmap ---
        self.icon_label = QLabel()
        icon = qta.icon('mdi.penguin', color='#83c092')
        pixmap = icon.pixmap(QSize(70, 70))  # Create a pixmap of the desired size
        self.icon_label.setPixmap(pixmap)   # Set the pixmap on the label
        # --- END FIX ---
        self.icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.main_layout.addWidget(self.icon_label)

        # Title Label
        title_font = QFont("Arial", 16, QFont.Weight.Bold)
        self.title_label = QLabel("PuffinPyEditor")
        self.title_label.setFont(title_font)
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.main_layout.addWidget(self.title_label)

        # Spacer
        self.main_layout.addStretch(1)

        # Status Label
        status_font = QFont("Arial", 9)
        self.status_label = QLabel("Initializing...")
        self.status_label.setFont(status_font)
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.main_layout.addWidget(self.status_label)

        # Apply a nice stylesheet
        self.setStyleSheet("""
            QWidget {
                background-color: #272e33;
                color: #d3c6aa;
                border-radius: 10px;
            }
        """)

    def set_status(self, message: str):
        """Updates the status message displayed on the splash screen."""
        self.status_label.setText(message)
        # Process events to ensure the UI updates immediately
        QApplication.processEvents()

    def finish(self, main_window):
        """
        Fades out the splash screen and then shows the main application window.
        """
        self.animation = QPropertyAnimation(self, b"windowOpacity")
        self.animation.setDuration(500)
        self.animation.setStartValue(1.0)
        self.animation.setEndValue(0.0)
        self.animation.setEasingCurve(QEasingCurve.Type.InOutQuad)

        # When the fade-out is complete, show the main window and close this splash screen
        self.animation.finished.connect(lambda: (
            main_window.show(),
            self.close()
        ))

        self.animation.start()
```

### File: `/ui/widgets/source_control_panel.py`
```py
# PuffinPyEditor/ui/widgets/source_control_panel.py
import os
from typing import List, Dict, Optional
from git import Repo, InvalidGitRepositoryError, Actor
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTreeWidget,
                             QTreeWidgetItem, QMenu, QMessageBox, QLabel, QHeaderView, QLineEdit, QComboBox,
                             QSizePolicy, QFrame)
from PyQt6.QtGui import QColor
from PyQt6.QtCore import Qt, pyqtSignal, QPoint
import qtawesome as qta

from app_core.project_manager import ProjectManager
from app_core.source_control_manager import SourceControlManager
from app_core.github_manager import GitHubManager
from app_core.puffin_api import PuffinPluginAPI
from app_core.settings_manager import settings_manager


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
                 git_manager: SourceControlManager,
                 github_manager: GitHubManager,
                 puffin_api: PuffinPluginAPI, parent=None):
        super().__init__(parent)
        self.project_manager = project_manager
        self.git_manager = git_manager
        self.github_manager = github_manager
        self.api = puffin_api
        self.staged_color = QColor("#A7C080")
        self.unstaged_color = QColor("#DBBC7F")
        self.conflicted_color = QColor("#E53935")  # Added color for conflicts
        self._setup_ui()
        self._connect_signals()
        self.update_icons()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)

        # Main actions toolbar
        main_actions_layout = QHBoxLayout()
        self.refresh_all_button = QPushButton("Refresh")
        self.pull_button = QPushButton("Pull")
        self.push_button = QPushButton("Push")
        self.new_release_button = QPushButton("New Release...")

        main_actions_layout.addWidget(self.refresh_all_button)
        main_actions_layout.addWidget(self.pull_button)
        main_actions_layout.addWidget(self.push_button)
        main_actions_layout.addStretch()
        main_actions_layout.addWidget(self.new_release_button)
        layout.addLayout(main_actions_layout)

        # Advanced/dangerous actions toolbar
        advanced_actions_frame = QFrame()
        advanced_actions_frame.setObjectName("AdvancedActionsFrame")
        advanced_actions_layout = QHBoxLayout(advanced_actions_frame)
        advanced_actions_layout.setContentsMargins(0, 2, 0, 2)
        advanced_actions_layout.addWidget(QLabel("Advanced:"))
        self.force_push_button = QPushButton("Force Push")
        self.force_push_button.setToolTip("DANGER: Overwrites remote history with your local branch.")
        self.abort_merge_button = QPushButton("Abort Merge")
        self.abort_merge_button.setToolTip("Aborts a conflicted merge and resets your branch.")
        self.cleanup_tags_button = QPushButton("Cleanup Tags")
        self.cleanup_tags_button.setToolTip("Delete remote tags that are not part of a release.")

        advanced_actions_layout.addWidget(self.force_push_button)
        advanced_actions_layout.addWidget(self.abort_merge_button)
        advanced_actions_layout.addStretch()
        advanced_actions_layout.addWidget(self.cleanup_tags_button)
        self.abort_merge_button.hide()  # Hide by default
        layout.addWidget(advanced_actions_frame)

        self.project_tree = QTreeWidget()
        self.project_tree.setHeaderLabels(["Project / Changes", ""])
        self.project_tree.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        header = self.project_tree.header()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        layout.addWidget(self.project_tree)

        self.commit_message_edit = QComboBox()
        self.commit_message_edit.setEditable(True)
        self.commit_message_edit.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)
        self.commit_message_edit.setToolTip("Enter a commit message or select a previous one.")
        self.commit_message_edit.lineEdit().setPlaceholderText("Commit message...")
        self.commit_message_edit.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        self.commit_button = QPushButton("Commit All")
        commit_layout = QHBoxLayout()
        commit_layout.addWidget(self.commit_message_edit)
        commit_layout.addWidget(self.commit_button)
        layout.addLayout(commit_layout)
        self.status_label = QLabel("Ready.")
        layout.addWidget(self.status_label)

        self.action_buttons = [self.refresh_all_button, self.pull_button, self.push_button,
                               self.new_release_button, self.commit_button, self.cleanup_tags_button,
                               self.force_push_button, self.abort_merge_button]

    def _connect_signals(self):
        self.git_manager.status_updated.connect(self._update_project_files)
        self.git_manager.summaries_ready.connect(self._populate_tree)
        self.git_manager.git_error.connect(self._handle_git_error)
        self.git_manager.dubious_ownership_detected.connect(self._handle_dubious_ownership)
        self.git_manager.git_success.connect(self._handle_git_success)
        self.github_manager.operation_success.connect(self._handle_git_success)
        self.github_manager.operation_failed.connect(self._handle_git_error)

        self.refresh_all_button.clicked.connect(self.refresh_all_projects)
        self.push_button.clicked.connect(self._on_push_clicked)
        self.pull_button.clicked.connect(self._on_pull_clicked)
        self.new_release_button.clicked.connect(self._on_new_release_clicked)
        self.commit_button.clicked.connect(self._on_commit_clicked)
        self.force_push_button.clicked.connect(self._on_force_push_clicked)
        self.abort_merge_button.clicked.connect(self._on_abort_merge_clicked)
        self.cleanup_tags_button.clicked.connect(self._on_cleanup_tags_clicked)
        self.project_tree.customContextMenuRequested.connect(self._show_context_menu)

    def set_ui_locked(self, locked: bool, message: str = ""):
        for button in self.action_buttons:
            if button != self.abort_merge_button:
                button.setEnabled(not locked)
        self.commit_message_edit.setEnabled(not locked)
        self.status_label.setText(message)

    def update_icons(self):
        self.refresh_all_button.setIcon(qta.icon('mdi.refresh'))
        self.pull_button.setIcon(qta.icon('mdi.arrow-down-bold-outline'))
        self.push_button.setIcon(qta.icon('mdi.arrow-up-bold-outline'))
        self.new_release_button.setIcon(qta.icon('mdi.tag-outline'))
        self.cleanup_tags_button.setIcon(qta.icon('mdi.tag-remove-outline'))
        self.commit_button.setIcon(qta.icon('mdi.check'))
        self.force_push_button.setIcon(qta.icon('mdi.upload-off-outline', color='orange'))
        self.abort_merge_button.setIcon(qta.icon('mdi.close-octagon-outline', color='red'))

    def showEvent(self, event):
        super().showEvent(event)
        self._populate_commit_history()

    def _populate_commit_history(self):
        history = settings_manager.get("commit_message_history", [])
        self.commit_message_edit.clear()
        self.commit_message_edit.addItems(history)
        self.commit_message_edit.setCurrentText("")

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

    def _on_force_push_clicked(self):
        if not (path := self._get_selected_project_path()):
            return

        reply = QMessageBox.warning(
            self,
            "Confirm Force Push",
            "<b>DANGER:</b> Force pushing overwrites the remote history with your local "
            "branch. This can discard commits for other team members.\n\n"
            "Only do this if you are absolutely sure. Are you sure you want to force push?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.Cancel,
            QMessageBox.StandardButton.Cancel
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.set_ui_locked(True, f"Force pushing {os.path.basename(path)}...")
            self.git_manager.force_push(path)

    def _on_abort_merge_clicked(self):
        if not (path := self._get_selected_project_path()):
            return
        self.set_ui_locked(True, f"Aborting merge in {os.path.basename(path)}...")
        self.git_manager.abort_merge(path)

    def _on_pull_clicked(self):
        if path := self._get_selected_project_path():
            self.set_ui_locked(True, f"Pulling {os.path.basename(path)}...")
            self.git_manager.pull(path)

    def _on_new_release_clicked(self):
        if path := self._get_selected_project_path():
            self.create_release_requested.emit(path)

    def _on_commit_clicked(self):
        path = self._get_selected_project_path()
        message = self.commit_message_edit.currentText().strip()

        if message.lower().startswith("git commit"):
            QMessageBox.warning(self, "Invalid Message",
                                "Please enter only the commit message, not the full 'git commit' command.")
            return

        if not path or not message:
            QMessageBox.warning(self, "Commit Failed",
                                "A project must be selected and a commit message must be provided.")
            return

        # FIX: The manager now handles the author, so we don't need to create the Actor here.
        self.set_ui_locked(True, f"Committing changes in {os.path.basename(path)}...")
        self.git_manager.commit_files(path, message)

    def _on_cleanup_tags_clicked(self):
        path = self._get_selected_project_path()
        if not path:
            QMessageBox.warning(self, "No Project Selected", "Please select a Git project.")
            return

        try:
            repo = Repo(path)
            if not repo.remotes:
                QMessageBox.warning(self, "No Remote", "The selected project does not have a remote configured.")
                return
            remote_url = repo.remotes.origin.url
            owner, repo_name = self.git_manager.parse_git_url(remote_url)
            if not owner or not repo_name:
                QMessageBox.critical(self, "Error", "Could not parse owner/repo from the remote URL.")
                return
        except Exception as e:
            QMessageBox.critical(self, "Git Error", f"Could not analyze repository: {e}")
            return

        reply = QMessageBox.question(
            self,
            "Confirm Tag Cleanup",
            "This will permanently delete all tags from the remote repository "
            f"<b>{owner}/{repo_name}</b> that are NOT associated with a GitHub Release.\n\n"
            "This action cannot be undone. Are you sure you want to continue?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.Cancel,
            QMessageBox.StandardButton.Cancel
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.set_ui_locked(True, f"Cleaning up tags for {owner}/{repo_name}...")
            self.github_manager.cleanup_orphaned_tags(owner, repo_name)

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
        if data.get("deleted_tags") is not None:
            QMessageBox.information(self, "Cleanup Complete", message)

        self.set_ui_locked(False, f"Success: {message}")

        if "committed" in message.lower() and not data.get('no_changes'):
            commit_message = self.commit_message_edit.currentText().strip()
            history = settings_manager.get("commit_message_history", [])
            if commit_message in history:
                history.remove(commit_message)
            history.insert(0, commit_message)
            max_history = settings_manager.get("max_commit_history", 50)
            settings_manager.set("commit_message_history", history[:max_history])
            self._populate_commit_history()

        self.refresh_all_projects()

    # NEW METHOD
    def _handle_dubious_ownership(self, repo_path: str):
        """Shows a user-friendly dialog for the 'dubious ownership' error."""
        self.set_ui_locked(False, "Git ownership issue detected.")
        msg_box = QMessageBox(self)
        msg_box.setIcon(QMessageBox.Icon.Warning)
        msg_box.setWindowTitle("Git Security Warning")
        msg_box.setText(
            f"Git has detected a potential security issue with the repository at:\n<b>{repo_path}</b>"
        )
        msg_box.setInformativeText(
            "This can happen if the repository was cloned by a different user or with different permissions. "
            "To resolve this, you can mark this directory as safe in your global Git configuration.\n\n"
            "Would you like to do this automatically?"
        )
        fix_button = msg_box.addButton("Fix Automatically", QMessageBox.ButtonRole.AcceptRole)
        cancel_button = msg_box.addButton("Cancel", QMessageBox.ButtonRole.RejectRole)
        msg_box.exec()

        if msg_box.clickedButton() == fix_button:
            self.set_ui_locked(True, f"Marking '{os.path.basename(repo_path)}' as safe...")
            self.git_manager.add_safe_directory(repo_path)

    def _handle_git_error(self, error_message: str):
        self.set_ui_locked(False, "Operation Failed.")
        msg_box = QMessageBox(self)
        msg_box.setIcon(QMessageBox.Icon.Critical)
        msg_box.setWindowTitle("Operation Failed")
        msg_box.setText("A Git operation failed to complete.")
        msg_box.setInformativeText(f"<b>Reason:</b><br><pre>{error_message}</pre>")
        msg_box.exec()
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
                item.setIcon(0, qta.icon('mdi.git'))
                self.git_manager.get_status(path)
            else:
                item = QTreeWidgetItem(self.project_tree, [project_name])
                item.setData(0, Qt.ItemDataRole.UserRole, {'type': 'non-git-project', 'path': path})
                item.setIcon(0, qta.icon('mdi.folder-outline', color='gray'))
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

    def _update_project_files(self, staged: List[str], unstaged: List[str], conflicted: List[str], repo_path: str):
        root = self.project_tree.invisibleRootItem()
        for i in range(root.childCount()):
            project_item = root.child(i)
            item_data = project_item.data(0, Qt.ItemDataRole.UserRole)
            if item_data and item_data.get('path') == repo_path:
                project_item.takeChildren()

                repo = Repo(repo_path)
                is_merging = os.path.exists(os.path.join(repo.git_dir, 'MERGE_HEAD'))
                self.abort_merge_button.setVisible(is_merging)

                if conflicted:
                    conflicts_header = QTreeWidgetItem(project_item, ["Conflicts (Resolve Manually)"])
                    conflicts_header.setForeground(0, self.conflicted_color)
                    for f in sorted(conflicted):
                        child = QTreeWidgetItem(conflicts_header, [f])
                        child.setForeground(0, self.conflicted_color)

                if staged:
                    staged_header = QTreeWidgetItem(project_item, ["Staged Changes"])
                    staged_header.setForeground(0, self.staged_color)
                    for f in sorted(staged):
                        child = QTreeWidgetItem(staged_header, [f])
                        child.setForeground(0, self.staged_color)

                if unstaged:
                    unstaged_header = QTreeWidgetItem(project_item, ["Changes"])
                    unstaged_header.setForeground(0, self.unstaged_color)
                    for f in sorted(unstaged):
                        child = QTreeWidgetItem(unstaged_header, [f])
                        child.setForeground(0, self.unstaged_color)

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
            menu.addAction(qta.icon('mdi.refresh'), "Refresh Status",
                           lambda: self.git_manager.get_status(path))
            vis_action = menu.addAction(qta.icon('mdi.eye-outline'), "Change GitHub Visibility...")
            vis_action.triggered.connect(lambda: self.change_visibility_requested.emit(path))

            repo = Repo(path)
            is_merging = os.path.exists(os.path.join(repo.git_dir, 'MERGE_HEAD'))
            if is_merging:
                menu.addSeparator()
                abort_action = menu.addAction(qta.icon('mdi.close-octagon-outline', color='red'), "Abort Merge")
                abort_action.triggered.connect(lambda: self._on_abort_merge_clicked())

            try:
                branches = [b.name for b in repo.branches]
                if 'main' in branches and 'master' in branches:
                    menu.addSeparator()
                    fix_action = menu.addAction(qta.icon('mdi.alert-outline',
                                                         color='orange'), "Fix Branch Mismatch...")
                    fix_action.triggered.connect(lambda: self._on_fix_branch_mismatch_clicked(path))
            except (InvalidGitRepositoryError, TypeError):
                pass
        elif data['type'] == 'non-git-project':
            menu.addAction(qta.icon('mdi.link-variant'), "Link to GitHub Repo...",
                           lambda: self.link_to_remote_requested.emit(path))
            menu.addAction(qta.icon('mdi.cloud-upload-outline'), "Publish to GitHub...",
                           lambda: self.publish_repo_requested.emit(path))

        if menu.actions():
            menu.exec(self.project_tree.viewport().mapToGlobal(position))
```

### File: `/ui/widgets/problems_panel.py`
```py
# PuffinPyEditor/ui/widgets/problems_panel.py
import os
from typing import Dict, List, Optional
from PyQt6.QtWidgets import QTreeWidget, QTreeWidgetItem, QHeaderView, QWidget
from PyQt6.QtCore import pyqtSignal, Qt
from utils.logger import log


class ProblemsPanel(QTreeWidget):
    """
    A widget that displays linting problems in a hierarchical tree view,
    grouped by file.
    """
    problem_selected = pyqtSignal(str, int, int)

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        log.info("ProblemsPanel initializing...")

        self.setColumnCount(4)
        self.setHeaderLabels(["Description", "File", "Line", "Code"])
        self.setSelectionBehavior(QTreeWidget.SelectionBehavior.SelectRows)
        self.setSelectionMode(QTreeWidget.SelectionMode.SingleSelection)
        self.setEditTriggers(QTreeWidget.EditTrigger.NoEditTriggers)
        self.setAlternatingRowColors(True)
        self.setIndentation(12)
        self.setSortingEnabled(True)

        header = self.header()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)

        self.itemDoubleClicked.connect(self._on_item_double_clicked)
        log.info("ProblemsPanel initialized as QTreeWidget.")

    def update_problems(self, problems_by_file: Dict[str, List[Dict]]):
        """
        Clears and repopulates the tree with a new set of problems.
        """
        self.clear()
        self.setSortingEnabled(False)

        if not problems_by_file:
            self.show_info_message("No problems found.")
            return

        for filepath, problems in problems_by_file.items():
            if not problems:
                continue

            file_node = QTreeWidgetItem(self)
            file_node.setText(
                0, f"{os.path.basename(filepath)} ({len(problems)} issues)")
            file_node.setData(
                0, Qt.ItemDataRole.UserRole, {'is_file_node': True})
            file_node.setFirstColumnSpanned(True)

            for problem in problems:
                problem_node = QTreeWidgetItem(file_node)
                problem_node.setText(0, problem.get("description", ""))
                problem_node.setText(1, os.path.basename(filepath))
                problem_node.setText(2, str(problem.get("line", "")))
                problem_node.setText(3, problem.get("code", ""))
                problem_node.setData(0, Qt.ItemDataRole.UserRole, {
                    'filepath': filepath,
                    'line': problem.get("line"),
                    'col': problem.get("col")
                })
        self.expandAll()
        self.setSortingEnabled(True)
        self.sortByColumn(1, Qt.SortOrder.AscendingOrder)

    def clear_problems(self):
        """Clears all items from the panel."""
        self.clear()

    def show_info_message(self, message: str):
        """Displays a single, un-clickable informational message."""
        self.clear()
        info_item = QTreeWidgetItem(self, [message])
        info_item.setFirstColumnSpanned(True)
        info_item.setDisabled(True)

    def _on_item_double_clicked(self, item: QTreeWidgetItem, column: int):
        """Emits a signal when a specific problem item is double-clicked."""
        problem_data = item.data(0, Qt.ItemDataRole.UserRole)
        if problem_data and not problem_data.get('is_file_node', False):
            filepath = problem_data.get("filepath")
            line = problem_data.get("line")
            col = problem_data.get("col")
            if filepath and line is not None:
                log.debug(f"Problem selected: Go to {filepath}:{line}:{col}")
                self.problem_selected.emit(filepath, line, col)
```

### File: `/ui/widgets/find_panel.py`
```py
# /ui/widgets/find_panel.py
from typing import Optional, TYPE_CHECKING
from PyQt6.QtWidgets import (QWidget, QHBoxLayout, QVBoxLayout, QLineEdit,
                             QPushButton, QCheckBox, QToolButton, QFrame)
from PyQt6.QtGui import QTextDocument, QKeyEvent
from PyQt6.QtCore import Qt, pyqtSignal
import qtawesome as qta

from app_core.settings_manager import settings_manager

# This is a super neat trick I learned to prevent circular import errors!
# It lets me use EditorWidget for type hinting without actually importing it at runtime.
if TYPE_CHECKING:
    from ..editor_widget import EditorWidget
    from app_core.theme_manager import ThemeManager


class FindPanel(QFrame):
    """An integrated panel for find and replace operations."""
    # This signal tells the parent (the EditorWidget) to close me.
    close_requested = pyqtSignal()
    # This signal asks the main window to show a message in the status bar.
    status_message_requested = pyqtSignal(str, int)

    def __init__(self, theme_manager: "ThemeManager", parent: QWidget):
        super().__init__(parent)
        # This will be the editor widget this panel is currently controlling.
        self.editor: Optional["EditorWidget"] = None
        self.theme_manager = theme_manager
        # Giving this an object name is great for styling with CSS-like QSS!
        self.setObjectName("FindPanelFrame")
        self._setup_ui()
        self._connect_signals()
        self.load_settings()
        self.update_theme()

    def _setup_ui(self):
        # This function builds the visual components of the panel.
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(5, 5, 5, 5)
        self.main_layout.setSpacing(5)

        find_layout = QHBoxLayout()
        self.toggle_button = QToolButton()
        self.toggle_button.setCheckable(True)
        self.toggle_button.setAutoRaise(True)
        self.toggle_button.setIcon(qta.icon('mdi.chevron-right'))
        find_layout.addWidget(self.toggle_button)

        self.find_input = QLineEdit()
        self.find_input.setPlaceholderText("Find")
        find_layout.addWidget(self.find_input)

        self.find_prev_button = self._create_tool_button(
            'mdi.arrow-up', "Find Previous (Shift+F3)")
        self.find_next_button = self._create_tool_button(
            'mdi.arrow-down', "Find Next (F3)")
        self.close_button = self._create_tool_button(
            'mdi.close', "Close (Esc)")
        find_layout.addWidget(self.find_prev_button)
        find_layout.addWidget(self.find_next_button)
        find_layout.addWidget(self.close_button)
        self.main_layout.addLayout(find_layout)

        # This widget holds the "replace" parts and can be hidden/shown.
        self.expandable_widget = QWidget()
        expandable_layout = QVBoxLayout(self.expandable_widget)
        expandable_layout.setContentsMargins(0, 5, 0, 0)
        expandable_layout.setSpacing(5)

        replace_layout = QHBoxLayout()
        self.replace_input = QLineEdit()
        self.replace_input.setPlaceholderText("Replace")
        self.replace_button = self._create_tool_button(
            'mdi.find-replace', "Replace", text="Replace")
        self.replace_all_button = self._create_tool_button(
            'mdi.auto-fix', "Replace All", text="All")
        replace_layout.addWidget(self.replace_input)
        replace_layout.addWidget(self.replace_button)
        replace_layout.addWidget(self.replace_all_button)
        expandable_layout.addLayout(replace_layout)

        options_layout = QHBoxLayout()
        options_layout.setContentsMargins(25, 0, 0, 0)
        self.case_checkbox = QCheckBox("Case Sensitive")
        self.whole_word_checkbox = QCheckBox("Whole Word")
        options_layout.addWidget(self.case_checkbox)
        options_layout.addWidget(self.whole_word_checkbox)
        options_layout.addStretch()
        expandable_layout.addLayout(options_layout)

        self.main_layout.addWidget(self.expandable_widget)
        self.expandable_widget.hide()

    def _create_tool_button(
            self, icon_name: str, tooltip: str, text: Optional[str] = None
    ) -> QToolButton:
        # A helper function to make creating buttons less repetitive. DRY principle!
        button = QToolButton()
        button.setAutoRaise(True)
        button.setToolTip(tooltip)
        button.setProperty("icon_name", icon_name) # Store the icon name for theming
        if text:
            button.setText(text)
            button.setToolButtonStyle(
                Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        return button

    def _connect_signals(self):
        # Connecting all the button clicks to their functions.
        self.close_button.clicked.connect(self.close_requested.emit)
        self.toggle_button.toggled.connect(self.expandable_widget.setVisible)
        self.find_input.textChanged.connect(self._update_button_states)
        self.find_input.returnPressed.connect(self.find_next_button.click)
        self.find_next_button.clicked.connect(
            lambda: self._find(backwards=False))
        self.find_prev_button.clicked.connect(
            lambda: self._find(backwards=True))
        self.replace_button.clicked.connect(self._replace)
        self.replace_all_button.clicked.connect(self._replace_all)

    def connect_editor(self, editor: "EditorWidget"):
        # This method links the panel to a specific editor instance.
        self.editor = editor
        # Pre-fill the find input with any selected text.
        initial_text = editor.text_area.textCursor().selectedText()
        if initial_text:
            self.find_input.setText(initial_text)
        self.focus_find_input()
        self._update_button_states()

    def focus_find_input(self):
        self.find_input.setFocus()
        self.find_input.selectAll()

    def update_theme(self):
        # Applies the current theme's colors to the panel.
        colors = self.theme_manager.current_theme_data['colors']
        frame_bg = colors.get('sidebar.background', '#333')
        self.setStyleSheet(
            f"#FindPanelFrame {{ background-color: {frame_bg}; "
            f"border-bottom: 1px solid {colors.get('input.border')}; }}")
        # I'm re-applying icons here to make sure they get the new theme colors.
        for button in self.findChildren((QToolButton, QPushButton)):
            if icon_name := button.property("icon_name"):
                button.setIcon(qta.icon(icon_name))

    def keyPressEvent(self, event: QKeyEvent):
        # A key press event handler to allow closing the panel with the Escape key.
        if event.key() == Qt.Key.Key_Escape:
            self.close_requested.emit()
            return
        super().keyPressEvent(event)

    def load_settings(self):
        # Loads user preferences for search options.
        self.case_checkbox.setChecked(
            settings_manager.get("search_case_sensitive", False))
        self.whole_word_checkbox.setChecked(
            settings_manager.get("search_whole_word", False))

    def save_settings(self):
        # Saves user preferences for search options.
        settings_manager.set(
            "search_case_sensitive", self.case_checkbox.isChecked())
        settings_manager.set(
            "search_whole_word", self.whole_word_checkbox.isChecked())

    def _update_button_states(self):
        # Disables buttons if there's no text to find.
        has_text = bool(self.find_input.text())
        self.find_next_button.setEnabled(has_text)
        self.find_prev_button.setEnabled(has_text)
        self.replace_button.setEnabled(has_text)
        self.replace_all_button.setEnabled(has_text)

    def _get_find_flags(self) -> QTextDocument.FindFlag:
        # Converts our checkboxes into flags that Qt's find function understands.
        flags = QTextDocument.FindFlag(0)
        if self.case_checkbox.isChecked():
            flags |= QTextDocument.FindFlag.FindCaseSensitively
        if self.whole_word_checkbox.isChecked():
            flags |= QTextDocument.FindFlag.FindWholeWords
        return flags

    def _find(self, backwards: bool = False):
        # Performs the find operation.
        if not self.editor:
            return
        query = self.find_input.text()
        flags = self._get_find_flags()
        if backwards:
            flags |= QTextDocument.FindFlag.FindBackward
        if not self.editor.find_next(query, flags):
            self.status_message_requested.emit(
                f"No more occurrences of '{query}' found.", 2000)
        self.save_settings()

    def _replace(self):
        # Performs a single replacement.
        if not self.editor:
            return
        query = self.find_input.text()
        replace_text = self.replace_input.text()
        flags = self._get_find_flags()
        if not self.editor.replace_current(query, replace_text, flags):
            self.status_message_requested.emit(
                "Nothing selected to replace.", 2000)
        self.save_settings()

    def _replace_all(self):
        # Performs a "replace all" operation.
        if not self.editor:
            return
        query = self.find_input.text()
        replace_text = self.replace_input.text()
        flags = self._get_find_flags()
        count = self.editor.replace_all(query, replace_text, flags)
        self.save_settings()
        self.status_message_requested.emit(
            f"Replaced {count} occurrence(s).", 3000)
```

### File: `/ui/widgets/draggable_tab_widget.py`
```py
# PuffinPyEditor/ui/widgets/draggable_tab_widget.py [MODIFIED]
import os
from PyQt6.QtWidgets import (QTabWidget, QTabBar, QMainWindow, QWidget,
                             QApplication)
from PyQt6.QtCore import Qt, pyqtSignal, QPoint, QMimeData, QByteArray
from PyQt6.QtGui import QMouseEvent, QDrag
from utils.logger import log

# Custom MIME type to identify our widget drags
WIDGET_REFERENCE_MIME_TYPE = "application/x-puffin-widget-reference"


class FloatingTabWindow(QMainWindow):
    """A QMainWindow to host a detached tab. It now knows how to be dragged."""

    def __init__(self, main_window_ref, widget, tab_text, tooltip_text, icon):
        super().__init__()
        self.main_window_ref = main_window_ref
        self.hosted_widget = widget
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)

        self.setWindowTitle(f"{tab_text} - PuffinPyEditor")
        self.setCentralWidget(self.hosted_widget)
        if icon:
            self.setWindowIcon(icon)

        self.resize(800, 600)
        self.setToolTip(tooltip_text)
        self.drag_start_pos = None

    def closeEvent(self, event):
        self.main_window_ref._close_widget_safely(self.hosted_widget, event)

    def mousePressEvent(self, event: QMouseEvent):
        # We start a drag if the left button is pressed on the window frame (title bar).
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_start_pos = event.globalPosition().toPoint()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent):
        if not (event.buttons() & Qt.MouseButton.LeftButton) or not self.drag_start_pos:
            return super().mouseMoveEvent(event)

        # Check if the mouse has moved far enough to be considered a drag
        if (
                event.globalPosition().toPoint() - self.drag_start_pos).manhattanLength() < QApplication.startDragDistance():
            return super().mouseMoveEvent(event)

        log.info(f"Initiating drag for widget ID: {id(self.hosted_widget)}")
        drag = QDrag(self)
        mime_data = QMimeData()
        widget_id_bytes = QByteArray(str(id(self.hosted_widget)).encode())
        mime_data.setData(WIDGET_REFERENCE_MIME_TYPE, widget_id_bytes)
        drag.setMimeData(mime_data)

        # Hide the window while dragging. If the drag is cancelled, we'll show it again.
        self.hide()

        # The exec() call blocks until the drag is finished.
        result = drag.exec(Qt.DropAction.MoveAction)

        if result == Qt.DropAction.IgnoreAction:
            # Drop was cancelled or unsuccessful, show the window again.
            log.debug("Tab drag cancelled, showing floating window again.")
            self.show()

        self.drag_start_pos = None


class DraggableTabBar(QTabBar):
    """A QTabBar that detects dragging out and accepts drops from floating windows."""
    tab_dragged_out = pyqtSignal(int, QPoint)
    tab_reinserted = pyqtSignal(QWidget, int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.drag_start_pos = None
        self.setAcceptDrops(True)

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_start_pos = event.pos()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent):
        if not (event.buttons() & Qt.MouseButton.LeftButton) or self.drag_start_pos is None:
            return super().mouseMoveEvent(event)

        if (event.pos() - self.drag_start_pos).manhattanLength() < QApplication.startDragDistance():
            return super().mouseMoveEvent(event)

        # If drag moves outside the tab bar, initiate a drag-out
        if not self.rect().contains(event.pos()):
            tab_index = self.tabAt(self.drag_start_pos)
            if tab_index > -1:
                self.tab_dragged_out.emit(tab_index, event.globalPosition().toPoint())
                self.drag_start_pos = None

    def dragEnterEvent(self, event):
        if event.mimeData().hasFormat(WIDGET_REFERENCE_MIME_TYPE):
            event.acceptProposedAction()
        else:
            super().dragEnterEvent(event)

    def dropEvent(self, event):
        if not event.mimeData().hasFormat(WIDGET_REFERENCE_MIME_TYPE):
            return super().dropEvent(event)

        widget_id_bytes = event.mimeData().data(WIDGET_REFERENCE_MIME_TYPE)
        widget_id_str = widget_id_bytes.data().decode()

        # Find the widget instance from the main window's tracking dict
        main_window = self.parentWidget().main_window_ref
        widget_to_reinsert = None
        for widget, data in main_window.editor_tabs_data.items():
            if str(id(widget)) == widget_id_str:
                widget_to_reinsert = widget
                break

        if widget_to_reinsert:
            drop_index = self.tabAt(event.position().toPoint())
            log.info(f"Dropping widget ID {widget_id_str} at tab index {drop_index}")
            self.tab_reinserted.emit(widget_to_reinsert, drop_index)
            event.acceptProposedAction()
        else:
            log.warning(f"Could not find widget with ID {widget_id_str} to re-insert.")
            event.ignore()


class DraggableTabWidget(QTabWidget):
    """A QTabWidget that uses a DraggableTabBar to allow detaching and re-attaching tabs."""

    def __init__(self, main_window_ref, parent=None):
        super().__init__(parent)
        self.main_window_ref = main_window_ref
        tab_bar = DraggableTabBar(self)
        self.setTabBar(tab_bar)
        tab_bar.tab_dragged_out.connect(self._handle_tab_drag_out)
        tab_bar.tab_reinserted.connect(self._handle_tab_reinsert)

    def _handle_tab_drag_out(self, index: int, global_pos: QPoint):
        log.info(f"Detaching tab at index {index}.")
        widget = self.widget(index)
        widget_data = self.main_window_ref.editor_tabs_data.get(widget)
        if not widget or not widget_data:
            log.warning("Could not detach tab: widget or its data not found.")
            return

        tab_text, tooltip, icon = self.tabText(index), self.tabToolTip(index), self.tabIcon(index)
        self.removeTab(index)

        floating_window = FloatingTabWindow(self.main_window_ref, widget, tab_text, tooltip, icon)
        floating_window.move(global_pos)
        floating_window.show()

    def _handle_tab_reinsert(self, widget: QWidget, index: int):
        log.info(f"Re-inserting widget into tab bar at index: {index}")
        floating_window = widget.window()
        if not isinstance(floating_window, FloatingTabWindow):
            return

        widget_data = self.main_window_ref.editor_tabs_data.get(widget, {})
        tab_text = os.path.basename(widget_data.get('filepath')) if widget_data.get('filepath') else "Untitled"
        tooltip = widget_data.get('filepath', "Unsaved file")
        icon = floating_window.windowIcon()

        widget.setParent(self)

        if index < 0:
            index = self.count()

        self.insertTab(index, widget, icon, tab_text)
        self.setTabToolTip(index, tooltip)
        self.setCurrentWidget(widget)

        floating_window.setCentralWidget(None)
        floating_window.close()
```

### File: `/ui/widgets/__init__.py`
```py

```

### File: `/ui/explorer/list_view_widget.py`
```py
# PuffinPyEditor/ui/explorer/list_view_widget.py
import os
import sys
from typing import List, Optional
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QTreeWidget, QTreeWidgetItem, QInputDialog, QMessageBox,
                             QProxyStyle, QStyle, QApplication, QAbstractItemView, QToolButton,
                             QHBoxLayout, QTreeWidgetItemIterator, QHeaderView, QFrame)
from PyQt6.QtGui import (QPainter, QColor, QPen, QDrag, QKeyEvent, QIcon, QPaintEvent, QDragEnterEvent, QDropEvent,
                         QDragMoveEvent, QMouseEvent, QAction)
from PyQt6.QtCore import (Qt, QFileInfo, QMimeData, QRect, QFileSystemWatcher, QTimer, QPoint, QPointF,
                          QUrl, QItemSelection, QItemSelectionModel) # Corrected: QItemSelectionModel moved here
from functools import partial
import qtawesome as qta

from app_core.puffin_api import PuffinPluginAPI
from utils.logger import log
from app_core.settings_manager import settings_manager
from ..explorer.icon_provider import CustomFileIconProvider
from ..explorer.context_menu import show_project_context_menu
from ..explorer.helpers import get_git_statuses_for_root

TREE_ITEM_MIME_TYPE = "application/x-puffin-tree-item"


class NoDrawProxyStyle(QProxyStyle):
    """A proxy style to prevent drawing the default expand/collapse arrows."""

    def drawPrimitive(self, element: QStyle.PrimitiveElement, option, painter, widget=None):
        if element == QStyle.PrimitiveElement.PE_IndicatorBranch:
            return
        super().drawPrimitive(element, option, painter, widget)


class StyledTreeView(QTreeWidget):
    """A QTreeWidget with custom branch and indentation guide painting."""

    def __init__(self, puffin_api: PuffinPluginAPI, parent_view: 'FileSystemListView', parent: QWidget = None):
        super().__init__(parent)
        self.puffin_api = puffin_api
        self.parent_view = parent_view
        self.theme_manager = puffin_api.get_manager("theme")
        self.file_handler = puffin_api.get_manager("file_handler")

        self.setStyle(NoDrawProxyStyle(self.style()))
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.setDropIndicatorShown(True)
        self.setDragDropMode(QAbstractItemView.DragDropMode.DragDrop)
        self.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.setExpandsOnDoubleClick(False)


    def supportedDropActions(self) -> Qt.DropAction:
        return Qt.DropAction.CopyAction | Qt.DropAction.MoveAction

    def mimeData(self, items: List[QTreeWidgetItem]) -> Optional[QMimeData]:
        if not items:
            return None

        if len(items) > 1:
            return None

        item = items[0]
        data = item.data(0, Qt.ItemDataRole.UserRole)
        path = data.get('path') if data else None
        if not path:
            return None

        mime = QMimeData()
        mime.setData(TREE_ITEM_MIME_TYPE, path.encode('utf-8'))
        mime.setUrls([QUrl.fromLocalFile(path)])
        return mime

    def paintEvent(self, event: QPaintEvent):
        super().paintEvent(event)
        if self.topLevelItemCount() == 0:
            return

        painter = QPainter(self.viewport())
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        colors = self.theme_manager.current_theme_data.get('colors', {})
        pen = QPen(QColor(colors.get('accent', '#83c092')), 1)
        painter.setPen(pen)
        painter.drawLine(8, 0, 8, self.viewport().height())

    def drawBranches(self, painter: QPainter, rect: QRect, index: 'QModelIndex'):
        item = self.itemFromIndex(index)
        if not item or not item.parent() or item.parent() == self.invisibleRootItem():
            return

        colors = self.theme_manager.current_theme_data.get('colors', {})
        accent_color = QColor(colors.get('accent', '#83c092'))
        indent = self.indentation()
        half_indent = indent / 2.0
        ROOT_ITEM_OFFSET = 14

        painter.save()
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        depth = -1
        temp_item = item
        while temp_item.parent() and temp_item.parent() != self.invisibleRootItem():
            depth += 1
            temp_item = temp_item.parent()

        if depth < 0:
            painter.restore()
            return

        painter.setPen(QPen(accent_color, 1))
        for i in range(depth):
            ancestor = item
            for _ in range(depth - i):
                ancestor = ancestor.parent()
            if ancestor.parent() and ancestor.parent().indexOfChild(ancestor) < ancestor.parent().childCount() - 1:
                line_x = ROOT_ITEM_OFFSET + (i * indent) + half_indent
                painter.drawLine(QPointF(line_x, rect.top()), QPointF(line_x, rect.bottom()))

        item_is_folder = item.childCount() > 0 or (item.childCount() == 1 and not item.child(0).text(0))
        item_is_last_child = item.parent().indexOfChild(item) == item.parent().childCount() - 1
        expander_x = ROOT_ITEM_OFFSET + (depth * indent) + (indent * 0.25)
        parent_guide_x = (ROOT_ITEM_OFFSET + ((depth - 1) * indent) + half_indent) if depth > 0 else ROOT_ITEM_OFFSET
        center_y = rect.center().y()
        diagonal_start_y = rect.center().y() - 4.0

        if depth > 0:
            end_y = diagonal_start_y if item_is_last_child else rect.bottom()
            painter.drawLine(QPointF(parent_guide_x, rect.top()), QPointF(parent_guide_x, end_y))

        painter.setPen(QPen(accent_color, 2.0 if item_is_folder else 1.0))
        painter.drawLine(QPointF(parent_guide_x, diagonal_start_y), QPointF(expander_x, center_y))

        if item_is_folder:
            painter.setPen(QPen(accent_color, 1.2))
            self._draw_expander_at(painter, QPointF(expander_x, center_y), item.isExpanded())
        painter.restore()

    def _draw_expander_at(self, painter: QPainter, pos: QPointF, is_open: bool):
        arrow_size = 3.5
        p1 = pos + QPointF(-arrow_size / 2, -arrow_size)
        p2 = pos + QPointF(arrow_size / 2, 0)
        p3 = pos + QPointF(-arrow_size / 2, arrow_size)
        painter.save()
        painter.translate(pos)
        painter.rotate(90 if is_open else 0)
        painter.translate(-pos)
        painter.drawLine(p1, p2)
        painter.drawLine(p2, p3)
        painter.restore()

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasFormat(TREE_ITEM_MIME_TYPE):
            event.acceptProposedAction()
        else:
            super().dragEnterEvent(event)

    def dragMoveEvent(self, event: QDragMoveEvent):
        if not event.mimeData().hasFormat(TREE_ITEM_MIME_TYPE):
            event.ignore()
            return

        target_item = self.itemAt(event.position().toPoint())
        if not target_item:
            event.ignore()
            return

        source_path = event.mimeData().data(TREE_ITEM_MIME_TYPE).data().decode('utf-8')
        target_data = target_item.data(0, Qt.ItemDataRole.UserRole)
        target_path = target_data.get('path') if target_data else None

        if not target_path or os.path.normpath(source_path) == os.path.normpath(target_path):
            event.ignore()
            return
        
        dest_dir = target_path if target_data.get('is_dir') else os.path.dirname(target_path)

        if os.path.isdir(source_path) and os.path.normpath(dest_dir).startswith(os.path.normpath(source_path) + os.sep):
            event.ignore()
            return
            
        event.acceptProposedAction()


    def dropEvent(self, event: QDropEvent):
        if not event.mimeData().hasFormat(TREE_ITEM_MIME_TYPE):
            event.ignore()
            return

        source_path = event.mimeData().data(TREE_ITEM_MIME_TYPE).data().decode('utf-8')
        target_item = self.itemAt(event.position().toPoint())
        if not target_item:
            event.ignore()
            return

        target_data = target_item.data(0, Qt.ItemDataRole.UserRole)
        target_path = target_data.get('path') if target_data else None
        if not target_path:
            event.ignore()
            return

        dest_dir = target_path if target_data.get('is_dir') else os.path.dirname(target_path)
        is_copy = (event.modifiers() & Qt.KeyboardModifier.ControlModifier) == Qt.KeyboardModifier.ControlModifier
        
        operation = self.file_handler.copy_item_to_dest if is_copy else self.file_handler.move_item
        success, new_path = self.parent_view._perform_file_operation(operation, source_path, dest_dir, return_result=True)
        
        if success:
            log.info("Drag-and-drop operation successful, refreshing tree view.")
            self.parent_view.refresh()
            QTimer.singleShot(150, lambda p=new_path: self.parent_view._select_and_scroll_to_path(p))
            
        event.acceptProposedAction()


    def keyPressEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key.Key_Delete:
            selected_items = self.selectedItems()
            if selected_items:
                paths = [item.data(0, Qt.ItemDataRole.UserRole)['path'] for item in selected_items if item.data(0, Qt.ItemDataRole.UserRole)]
                if paths:
                    self.parent_view._action_delete(paths)
                    event.accept()
                    return
        super().keyPressEvent(event)
    
    def mousePressEvent(self, event: QMouseEvent):
        super().mousePressEvent(event)
        
        if event.button() == Qt.MouseButton.LeftButton:
            item = self.itemAt(event.pos())
            if not item:
                self.clearSelection()
                return

            modifiers = QApplication.keyboardModifiers()
            if modifiers & Qt.KeyboardModifier.ShiftModifier:
                if current_item := self.currentItem():
                    selection_model = self.selectionModel()
                    selection_model.select(QItemSelection(self.indexFromItem(item), self.indexFromItem(current_item)), QItemSelectionModel.SelectionFlag.Select | QItemSelectionModel.SelectionFlag.Rows)
            else:
                # Toggle expansion on single click
                if (data := item.data(0, Qt.ItemDataRole.UserRole)) and data.get('is_dir'):
                    item.setExpanded(not item.isExpanded())

    def mouseDoubleClickEvent(self, event: QMouseEvent):
        item = self.itemAt(event.pos())
        if item and (data := item.data(0, Qt.ItemDataRole.UserRole)) and data.get('is_dir'):
            # If it's a directory, we consume the event to prevent toggling again,
            # as mousePressEvent already handled it.
            event.accept()
            return
        # For files, let the default or connected slots handle it
        super().mouseDoubleClickEvent(event)


class FileSystemListView(QWidget):
    def __init__(self, puffin_api: PuffinPluginAPI, parent: QWidget = None):
        super().__init__(parent)
        self.api = puffin_api
        self.project_manager = self.api.get_manager("project")
        self.file_handler = self.api.get_manager("file_handler")
        self.theme_manager = self.api.get_manager("theme")
        self.icon_provider = CustomFileIconProvider(self.api)
        self.git_statuses = {}
        self.fs_watcher = QFileSystemWatcher(self)
        self.watched_paths = set()
        self._refresh_timer = QTimer(self)
        self._refresh_timer.setSingleShot(True)
        self._refresh_timer.setInterval(300)
        self._is_programmatic_change = False
        self._setup_ui()
        self._connect_signals()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        toolbar_frame = QFrame()
        toolbar_frame.setObjectName("ExplorerToolbar")
        toolbar_layout = QHBoxLayout(toolbar_frame)
        toolbar_layout.setContentsMargins(5, 2, 5, 2)
        toolbar_layout.setSpacing(5)
        self.expand_button = QToolButton()
        self.expand_button.setIcon(qta.icon('mdi.arrow-expand-all', color='gray'))
        self.expand_button.setToolTip("Expand All")
        self.expand_button.setAutoRaise(True)
        self.collapse_button = QToolButton()
        self.collapse_button.setIcon(qta.icon('mdi.arrow-collapse-all', color='gray'))
        self.collapse_button.setToolTip("Collapse All")
        self.collapse_button.setAutoRaise(True)
        self.refresh_button = QToolButton()
        self.refresh_button.setIcon(qta.icon('mdi.refresh', color='gray'))
        self.refresh_button.setToolTip("Refresh")
        self.refresh_button.setAutoRaise(True)
        toolbar_layout.addStretch()
        toolbar_layout.addWidget(self.expand_button)
        toolbar_layout.addWidget(self.collapse_button)
        toolbar_layout.addWidget(self.refresh_button)
        layout.addWidget(toolbar_frame)
        self.tree_widget = StyledTreeView(self.api, self)
        self.tree_widget.setHeaderLabels(["Project / File", ""])
        header = self.tree_widget.header()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)
        header.resizeSection(1, 60)
        self.tree_widget.setAlternatingRowColors(True)
        self.tree_widget.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.tree_widget.setIndentation(14)
        layout.addWidget(self.tree_widget)

    def _connect_signals(self):
        self.expand_button.clicked.connect(self.expand_all)
        self.collapse_button.clicked.connect(self.collapse_all)
        self.refresh_button.clicked.connect(self.refresh)
        self.tree_widget.itemExpanded.connect(self.on_item_expanded)
        self.tree_widget.itemCollapsed.connect(self.on_item_collapsed)
        self.tree_widget.itemDoubleClicked.connect(self.on_item_double_clicked)
        self.tree_widget.customContextMenuRequested.connect(self.show_context_menu)
        self.fs_watcher.directoryChanged.connect(self._schedule_refresh)
        self.fs_watcher.fileChanged.connect(self._schedule_refresh)
        self._refresh_timer.timeout.connect(self.refresh)
        if git_manager := self.api.get_manager("git"):
            git_manager.git_success.connect(self.refresh)
        self.file_handler.item_created.connect(self._on_item_created)
        self.file_handler.item_renamed.connect(self._on_item_renamed)
        self.file_handler.item_deleted.connect(self._on_item_deleted)

    def _action_new_file(self, target_dir: str):
        file_name, ok = QInputDialog.getText(self, "New File", "Enter file name:")
        if ok and file_name:
            self._perform_file_operation(self.file_handler.create_file, os.path.join(target_dir, file_name))

    def _action_new_folder(self, target_dir: str):
        folder_name, ok = QInputDialog.getText(self, "New Folder", "Enter folder name:")
        if ok and folder_name:
            self._perform_file_operation(self.file_handler.create_folder, os.path.join(target_dir, folder_name))

    def _action_rename(self, path: str):
        old_name = os.path.basename(path)
        new_name, ok = QInputDialog.getText(self, f"Rename '{old_name}'", "Enter new name:", text=old_name)
        if ok and new_name and new_name != old_name:
            self._perform_file_operation(self.file_handler.rename_item, path, new_name)

    def _action_delete(self, paths: List[str] or str):
        if isinstance(paths, str): paths = [paths]
        if not paths: return
        names = ", ".join([f"'{os.path.basename(p)}'" for p in paths])
        reply = QMessageBox.question(self, "Confirm Delete", f"Are you sure you want to delete {names}?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            for path in paths:
                self._perform_file_operation(self.file_handler.delete_item, path)

    def _action_duplicate(self, path: str):
        self._perform_file_operation(self.file_handler.duplicate_item, path)

    def _action_remove_boms(self, path: str):
        self.file_handler.remove_boms_in_path(path)

    def _perform_file_operation(self, operation_func, *args, return_result=False):
        try:
            success, message_or_data = operation_func(*args)
            if not success:
                QMessageBox.warning(self, "Operation Failed", message_or_data)
            if return_result:
                return success, message_or_data
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An unexpected error occurred: {e}")
            if return_result:
                return False, None

    def expand_all(self):
        self._is_programmatic_change = True
        self.tree_widget.expandAll()
        self._is_programmatic_change = False
        self._save_expanded_state_to_settings()

    def collapse_all(self):
        self._is_programmatic_change = True
        self.tree_widget.collapseAll()
        self._is_programmatic_change = False
        self._save_expanded_state_to_settings()

    def get_expanded_paths(self):
        expanded = set()
        iterator = QTreeWidgetItemIterator(self.tree_widget, QTreeWidgetItemIterator.IteratorFlag.All)
        while (item := iterator.value()):
            if item.isExpanded() and (data := item.data(0, Qt.ItemDataRole.UserRole)) and (path := data.get('path')):
                expanded.add(os.path.normpath(path))
            iterator += 1
        return list(expanded)
    
    def _save_expanded_state_to_settings(self):
        settings_manager.set("explorer_expanded_paths", self.get_expanded_paths())

    def _on_item_created(self, item_type: str, path: str):
        log.debug(f"Created {item_type}: {path}, refreshing.")
        self.refresh()
        QTimer.singleShot(150, lambda: self._select_and_scroll_to_path(path))
        if item_type == "file":
            self.api.get_main_window()._action_open_file(path)

    def _on_item_renamed(self, item_type: str, old: str, new: str):
        self.api.get_main_window()._on_file_renamed(old, new)
        self.refresh()
        QTimer.singleShot(100, lambda: self._select_and_scroll_to_path(new))

    def _on_item_deleted(self, item_type: str, path: str):
        self.refresh()
        QTimer.singleShot(150, lambda: self._select_and_scroll_to_path(os.path.dirname(path)))

    def on_item_double_clicked(self, item: QTreeWidgetItem, col: int):
        if (data := item.data(0, Qt.ItemDataRole.UserRole)) and not data.get('is_dir') and (path := data.get('path')) and os.path.isfile(path):
            self.api.get_main_window()._action_open_file(path)
            
    def _schedule_refresh(self, path: str):
        if not self._is_programmatic_change:
            log.debug(f"FS event at {path}. Refresh scheduled.")
            self._refresh_timer.start()

    def _move_project(self, path: str, direction: str):
        to_top = (direction == 'up')
        if QApplication.keyboardModifiers() & Qt.KeyboardModifier.ShiftModifier:
            self.project_manager.move_project_to_end(path, to_top)
        else:
            self.project_manager.move_project(path, direction)

    def refresh(self):
        log.info("Refreshing file explorer.")
        expanded_paths = set(os.path.normpath(p) for p in settings_manager.get("explorer_expanded_paths", []))
        is_first_load = not self.tree_widget.topLevelItemCount() > 0
        selected_paths = {os.path.normpath(item.data(0, Qt.ItemDataRole.UserRole)['path']) for item in self.tree_widget.selectedItems() if item.data(0, Qt.ItemDataRole.UserRole)}
        
        self.tree_widget.blockSignals(True)
        self._is_programmatic_change = True

        if self.watched_paths:
            self.fs_watcher.removePaths(list(self.watched_paths))
        self.watched_paths.clear()
        self.tree_widget.clear()
        
        open_projects = self.project_manager.get_open_projects()
        get_git_statuses_for_root.cache_clear()
        self.git_statuses = {p: get_git_statuses_for_root(p) for p in open_projects}
        self.flat_git_status = {k: v for d in self.git_statuses.values() for k, v in d.items()}
        items_to_reselect = []

        def build_tree_level(parent_item, path):
            try:
                self._add_to_watcher(path)
                for entry in sorted(os.scandir(path), key=lambda e: (not e.is_dir(), e.name.lower())):
                    if entry.name.startswith(('.', '__pycache__', 'venv')):
                        continue
                    norm_path = os.path.normpath(entry.path)
                    child = QTreeWidgetItem(parent_item, [entry.name])
                    child.setFirstColumnSpanned(True)
                    child.setIcon(0, self.icon_provider.icon(QFileInfo(entry.path)))
                    child.setData(0, Qt.ItemDataRole.UserRole, {'path': norm_path, 'is_dir': entry.is_dir()})
                    if norm_path in selected_paths:
                        items_to_reselect.append(child)
                    
                    if status := self.flat_git_status.get(norm_path):
                        colors = self.theme_manager.current_theme_data.get('colors', {})
                        color_map = {'??': 'git.added', 'M': 'git.modified', 'A': 'git.added', 'D': 'git.deleted', '!!': 'syntax.comment'}
                        for code, color_key in color_map.items():
                            if code in status and (color_val := colors.get(color_key)):
                                child.setForeground(0, QColor(color_val))
                                break

                    if entry.is_dir():
                        if norm_path in expanded_paths:
                            child.setExpanded(True)
                            build_tree_level(child, norm_path)
                        else:
                            child.addChild(QTreeWidgetItem([""]))
            except OSError as e:
                log.warning(f"Scan dir error: {e}")

        for proj in open_projects:
            norm_proj = os.path.normpath(proj)
            item = QTreeWidgetItem(self.tree_widget, [os.path.basename(norm_proj)])
            item.setToolTip(0, norm_proj)
            item.setIcon(0, qta.icon('mdi.folder-open-outline', color=self.theme_manager.current_theme_data.get('colors', {}).get('accent')))
            item.setData(0, Qt.ItemDataRole.UserRole, {'path': norm_proj, 'is_dir': True, 'is_root': True})
            if is_first_load or norm_proj in expanded_paths:
                item.setExpanded(True)
            controls_widget = QWidget()
            controls_layout = QHBoxLayout(controls_widget)
            controls_layout.setContentsMargins(0, 0, 0, 0)
            controls_layout.setSpacing(0)
            up_btn = QToolButton(icon=qta.icon('mdi.arrow-up-bold-box-outline'), toolTip="Move project up")
            down_btn = QToolButton(icon=qta.icon('mdi.arrow-down-bold-box-outline'), toolTip="Move project down")
            up_btn.clicked.connect(partial(self._move_project, norm_proj, 'up'))
            down_btn.clicked.connect(partial(self._move_project, norm_proj, 'down'))
            for btn in (up_btn, down_btn):
                btn.setAutoRaise(True)
            controls_layout.addStretch()
            controls_layout.addWidget(up_btn)
            controls_layout.addWidget(down_btn)
            self.tree_widget.setItemWidget(item, 1, controls_widget)
            build_tree_level(item, norm_proj)
            
        if items_to_reselect:
            self.tree_widget.clearSelection()
            for item in items_to_reselect:
                item.setSelected(True)
            if items_to_reselect:
                self.tree_widget.scrollToItem(items_to_reselect[0])
        elif self.tree_widget.topLevelItemCount() > 0:
            current = self.tree_widget.currentItem()
            if not current or not current.isSelected():
                self.tree_widget.setCurrentItem(self.tree_widget.topLevelItem(0))

        self.tree_widget.blockSignals(False)
        self._is_programmatic_change = False

    def _add_to_watcher(self, path):
        if path and path not in self.watched_paths:
            self.fs_watcher.addPath(path)
            self.watched_paths.add(path)

    def _find_item_by_path(self, parent_item, path_to_find):
        iterator = QTreeWidgetItemIterator(parent_item)
        while (item := iterator.value()):
            if (data := item.data(0, Qt.ItemDataRole.UserRole)) and os.path.normpath(data.get('path', '')) == path_to_find:
                return item
            iterator += 1
        return None
        
    def _select_and_scroll_to_path(self, path: str):
        if path and (item := self._find_item_by_path(self.tree_widget.invisibleRootItem(), os.path.normpath(path))):
            try:
                self.tree_widget.scrollToItem(item, QAbstractItemView.ScrollHint.PositionAtCenter)
                self.tree_widget.setCurrentItem(item)
            except RuntimeError as e:
                log.warning(f"Scroll failed (ignored): {e}")

    def on_item_expanded(self, item: QTreeWidgetItem):
        if self._is_programmatic_change:
            return
        data = item.data(0, Qt.ItemDataRole.UserRole)
        if data and data.get('is_dir') and item.childCount() == 1 and not item.child(0).text(0):
            self._is_programmatic_change = True
            item.takeChildren()
            self._populate_node(item)
            self._is_programmatic_change = False
        self._save_expanded_state_to_settings()

    def on_item_collapsed(self, item: QTreeWidgetItem):
        if not self._is_programmatic_change:
            self._save_expanded_state_to_settings()

    def _populate_node(self, parent_item):
        path = (data := parent_item.data(0, Qt.ItemDataRole.UserRole)) and data.get('path')
        if not path or not os.path.isdir(path):
            return
        try:
            for entry in sorted(os.scandir(path), key=lambda e: (not e.is_dir(), e.name.lower())):
                if entry.name.startswith(('.', '__pycache__', 'venv')):
                    continue
                child = QTreeWidgetItem(parent_item, [entry.name])
                child.setFirstColumnSpanned(True)
                child.setIcon(0, self.icon_provider.icon(QFileInfo(entry.path)))
                child.setData(0, Qt.ItemDataRole.UserRole, {'path': os.path.normpath(entry.path), 'is_dir': entry.is_dir()})
                if status := self.flat_git_status.get(os.path.normpath(entry.path)):
                    colors, color_map = self.theme_manager.current_theme_data.get('colors', {}), {'??': 'git.added', 'M': 'git.modified', 'A': 'git.added', 'D': 'git.deleted', '!!': 'syntax.comment'}
                    for code, color_key in color_map.items():
                        if code in status and (color := colors.get(color_key)):
                            child.setForeground(0, QColor(color))
                            break
                if entry.is_dir():
                    child.addChild(QTreeWidgetItem([""]))
        except OSError:
            pass

    def show_context_menu(self, position: QPoint):
        item = self.tree_widget.itemAt(position)
        path, is_dir = self.project_manager.get_active_project_path(), True
        if item and (data := item.data(0, Qt.ItemDataRole.UserRole)):
            path, is_dir = data.get('path'), data.get('is_dir')
        if path:
            show_project_context_menu(self, self.tree_widget.mapToGlobal(position), path, is_dir, self.project_manager)
```

### File: `/ui/explorer/icon_provider.py`
```py
# PuffinPyEditor/ui/explorer/icon_provider.py
from PyQt6.QtWidgets import QFileIconProvider
from PyQt6.QtCore import QFileInfo
import qtawesome as qta
from app_core.puffin_api import PuffinPluginAPI


class CustomFileIconProvider(QFileIconProvider):
    BINARY_EXTENSIONS = {'.exe', '.dll', '.so', '.o', '.a', '.lib', '.dylib', '.app', '.msi'}
    ICON_MAP = {
        ".git": "mdi.git", "__pycache__": "mdi.folder-cog-outline", "venv": "mdi.folder-cog-outline",
        ".venv": "mdi.folder-cog-outline", "dist": "mdi.folder-zip-outline", "build": "mdi.folder-zip-outline",
        "node_modules": "mdi.folder-npm-outline", "logs": "mdi.folder-text-outline",
        "tests": "mdi.folder-search-outline", "test": "mdi.folder-search-outline",
        ".vscode": "mdi.folder-vscode", ".idea": "mdi.folder-cog-outline",
        "Dockerfile": "mdi.docker", ".dockerignore": "mdi.docker", "docker-compose.yml": "mdi.docker",
        ".gitignore": "mdi.git", ".gitattributes": "mdi.git", "pyproject.toml": "mdi.language-python",
        "poetry.lock": "mdi.language-python", "requirements.txt": "mdi.format-list-numbered",
        "package.json": "mdi.npm", "package-lock.json": "mdi.npm", "pnpm-lock.yaml": "mdi.npm", "yarn.lock": "mdi.npm",
        ".env": "mdi.key-variant", ".env.example": "mdi.key-outline",
        "README.md": "mdi.book-open-variant",
        ".py": "mdi.language-python", ".pyc": "mdi.language-python", ".pyw": "mdi.language-python",
        ".js": "mdi.language-javascript", ".mjs": "mdi.language-javascript", ".ts": "mdi.language-typescript",
        ".tsx": "mdi.language-typescript", ".java": "mdi.language-java", ".jar": "mdi.language-java",
        ".cs": "mdi.language-csharp", ".csproj": "mdi.language-csharp", ".cpp": "mdi.language-cpp",
        ".hpp": "mdi.language-cpp", ".c": "mdi.language-c", ".h": "mdi.language-c",
        ".rs": "mdi.language-rust", ".go": "mdi.language-go", ".rb": "mdi.language-ruby",
        ".php": "mdi.language-php", ".swift": "mdi.language-swift", ".kt": "mdi.language-kotlin",
        ".sh": "mdi.bash", ".bat": "mdi.powershell", ".ps1": "mdi.powershell",
        ".html": "mdi.language-html5", ".htm": "mdi.language-html5", ".css": "mdi.language-css3",
        ".scss": "mdi.language-css3", ".json": "mdi.code-json", ".xml": "mdi.xml",
        ".yaml": "mdi.yaml", ".yml": "mdi.yaml", ".toml": "mdi.cog-outline", ".ini": "mdi.cog-outline",
        ".cfg": "mdi.cog-outline", ".conf": "mdi.cog-outline", ".sql": "mdi.database", ".db": "mdi.database",
        ".sqlite3": "mdi.database", ".zip": "mdi.folder-zip-outline", ".rar": "mdi.folder-zip-outline",
        ".7z": "mdi.folder-zip-outline", ".tar": "mdi.folder-zip-outline", ".gz": "mdi.folder-zip-outline",
        ".bz2": "mdi.folder-zip-outline", ".png": "mdi.file-image", ".jpg": "mdi.file-image",
        ".jpeg": "mdi.file-image", ".gif": "mdi.file-image", ".bmp": "mdi.file-image",
        ".ico": "mdi.file-image", ".svg": "mdi.svg",
    }

    def __init__(self, puffin_api: PuffinPluginAPI):
        super().__init__()
        self.api = puffin_api

    def icon(self, fileInfoOrType):
        # The argument can be a QFileInfo object or an IconType enum.
        # We only care about QFileInfo for our custom logic.
        if not isinstance(fileInfoOrType, QFileInfo):
            # This handles cases where Qt asks for generic icons like Folder, Computer etc.
            # We use the correct enum for this check.
            if isinstance(fileInfoOrType, QFileIconProvider.IconType):
                return super().icon(fileInfoOrType)
            # Fallback for unexpected types
            return qta.icon('fa5s.file')

        file_info = fileInfoOrType
        main_window = self.api.get_main_window()
        if not main_window: return qta.icon('fa5s.file')

        theme_manager = main_window.theme_manager
        # Ensure we have a valid theme data structure to prevent crashes if theme fails
        theme_data = theme_manager.current_theme_data or {}
        colors = theme_data.get('colors', {})
        icon_colors = colors.get('icon.colors', {})

        default_folder_color = icon_colors.get('default_folder', '#79b8f2')
        default_file_color = icon_colors.get('default_file', '#C0C5CE')

        if file_info.isDir():
            folder_name = file_info.fileName()
            icon_name = self.ICON_MAP.get(folder_name, 'mdi.folder-outline')
            color = icon_colors.get(folder_name, default_folder_color)
            return qta.icon(icon_name, color=color)

        file_name = file_info.fileName()
        extension = f".{file_info.suffix().lower()}"

        if file_name in self.ICON_MAP:
            icon_name = self.ICON_MAP[file_name]
            color = icon_colors.get(file_name, default_file_color)
            return qta.icon(icon_name, color=color)
        if extension in self.BINARY_EXTENSIONS:
            return qta.icon('mdi.cog', color=default_file_color)
        if extension in self.ICON_MAP:
            icon_name = self.ICON_MAP[extension]
            color = icon_colors.get(extension, default_file_color)
            return qta.icon(icon_name, color=color)

        # Fallback to the default system icon if no match is found
        return super().icon(file_info)
```

### File: `/ui/explorer/helpers.py`
```py
# /ui/explorer/helpers.py
import os
import subprocess
from functools import lru_cache
from utils.logger import log


@lru_cache(maxsize=2)
def get_git_statuses_for_root(project_root: str) -> dict:
    """
    Runs `git status` and parses the output into a dictionary mapping file
    paths to their status. Uses a cache to avoid redundant calls.
    """
    if not project_root or not os.path.isdir(os.path.join(project_root, '.git')):
        return {}

    try:
        startupinfo = None
        if os.name == 'nt':
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

        # --ignored=matching includes ignored files that are explicitly listed
        command = ['git', 'status', '--porcelain', '--untracked-files=all', '--ignored=matching']
        result = subprocess.check_output(
            command,
            cwd=project_root, text=True, startupinfo=startupinfo, stderr=subprocess.PIPE,
            encoding='utf-8', errors='ignore'
        )
        status_dict = {}
        for line in result.strip().split('\n'):
            if not line:
                continue

            status, path = line[:2], line[3:].strip().replace('"', '')
            full_path = os.path.join(project_root, path.replace('/', os.sep))

            # Normalize the status character. '??' for untracked, 'M' for modified, '!!' for ignored
            final_status = status.strip() if status.strip() else " "
            if status.startswith("??"):
                final_status = "??"
            elif status.startswith("!!"):
                final_status = "!!"
            elif "M" in status:
                final_status = "M"

            status_dict[os.path.normpath(full_path)] = final_status

        return status_dict
    except (subprocess.CalledProcessError, FileNotFoundError, OSError) as e:
        log.warning(f"Could not get git status for {project_root}: {e}")
        return {}
```

### File: `/ui/explorer/folder_size_worker.py`
```py
# PuffinPyEditor/ui/explorer/folder_size_worker.py
import os
from PyQt6.QtCore import QObject, QRunnable, pyqtSignal


class WorkerSignals(QObject):
    finished = pyqtSignal(str, int)


class FolderSizeWorker(QRunnable):
    def __init__(self, path: str):
        super().__init__()
        self.path = path
        self.signals = WorkerSignals()
        self.is_cancelled = False

    def run(self):
        total_size = 0
        try:
            for dirpath, _, filenames in os.walk(self.path, topdown=True, onerror=None):
                if self.is_cancelled:
                    self.signals.finished.emit(self.path, -2)
                    return
                for f in filenames:
                    try:
                        fp = os.path.join(dirpath, f)
                        if not os.path.islink(fp):
                            total_size += os.path.getsize(fp)
                    except (OSError, FileNotFoundError):
                        continue

            if not self.is_cancelled:
                self.signals.finished.emit(self.path, total_size)
        except Exception:
            if not self.is_cancelled:
                self.signals.finished.emit(self.path, -1)

    def cancel(self):
        self.is_cancelled = True
```

### File: `/ui/explorer/context_menu.py`
```py
# PuffinPyEditor/ui/explorer/context_menu.py
import os
from functools import partial
from PyQt6.QtWidgets import QMenu, QApplication, QMessageBox
from PyQt6.QtCore import QPoint
import qtawesome as qta
from app_core.project_manager import ProjectManager


def _copy_to_clipboard(text: str):
    """Helper to put text on the system clipboard."""
    if clip := QApplication.instance().clipboard():
        clip.setText(text)


def show_project_context_menu(panel, position: QPoint, path: str, is_dir: bool, project_manager: ProjectManager):
    """
    Creates and displays the context menu for the project explorer.
    """
    tree = panel.tree_widget
    target_dir = path if is_dir else os.path.dirname(path)

    # Check if a valid item was clicked
    item = tree.itemAt(position)
    is_valid_selection = item is not None
    is_project_root = path in project_manager.get_open_projects()

    menu = QMenu(tree)
    menu.addAction(qta.icon('mdi.file-plus-outline'), "New File...", partial(panel._action_new_file, target_dir))
    menu.addAction(qta.icon('mdi.folder-plus-outline'), "New Folder...", partial(panel._action_new_folder, target_dir))

    if is_valid_selection:
        menu.addSeparator()
        if is_project_root:
            menu.addAction(qta.icon('mdi.folder-remove-outline'), "Close Project",
                           partial(project_manager.close_project, path))
            menu.addSeparator()

        menu.addAction(qta.icon('mdi.pencil-outline'), "Rename...", partial(panel._action_rename, path))
        menu.addAction(qta.icon('mdi.trash-can-outline', color='crimson'), "Delete", partial(panel._action_delete, path))
        menu.addAction(qta.icon('mdi.content-copy'), "Duplicate", partial(panel._action_duplicate, path))
        menu.addSeparator()

        # --- NEW: BOM Removal Action ---
        menu.addAction(qta.icon('mdi.code-tags-check'), "Remove BOM from Files...", partial(panel._action_remove_boms, path))
        menu.addSeparator()

        if path.lower().endswith(('.py', '.js', '.cpp', '.c', '.cs')) and not is_dir:
            runner_plugin = panel.api.get_plugin_instance("script_runner")
            if runner_plugin:
                menu.addAction(qta.icon('mdi.play-outline', color='#4CAF50'), "Run Script",
                               lambda: runner_plugin.run_specific_script(path))
                menu.addSeparator()

        abs_path_action = menu.addAction(qta.icon('mdi.link-variant'), "Copy Path")
        abs_path_action.triggered.connect(lambda: _copy_to_clipboard(os.path.normpath(path)))

        project_path = panel.project_manager.get_active_project_path()
        if project_path:
            try:
                relative_path = os.path.relpath(path, start=project_path)
                rel_path_action = menu.addAction(qta.icon('mdi.link-box-variant-outline'), "Copy Relative Path")
                rel_path_action.triggered.connect(lambda: _copy_to_clipboard(relative_path.replace("\\", "/")))
            except ValueError:
                pass

    menu.addSeparator()
    reveal_path = path if is_valid_selection else target_dir
    menu.addAction("Reveal in Explorer", partial(panel.file_handler.reveal_in_explorer, reveal_path))

    menu.exec(tree.viewport().mapToGlobal(position))
```

### File: `/ui/explorer/__init__.py`
```py

```

### File: `/plugins/__init__.py`
```py

```

### File: `/plugins/theme_editor/theme_editor_dialog.py`
```py
# PuffinPyEditor/plugins/theme_editor/theme_editor_dialog.py
import re
import datetime
import copy
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QGridLayout,
                             QWidget, QLabel, QLineEdit, QPushButton,
                             QDialogButtonBox, QScrollArea, QMessageBox,
                             QColorDialog, QListWidget, QListWidgetItem,
                             QSplitter, QFrame, QGroupBox)
from PyQt6.QtGui import QColor, QFont, QPixmap, QIcon
from PyQt6.QtCore import Qt, pyqtSignal, QSize
from utils.logger import log


class ColorPickerButton(QPushButton):
    """A custom button that displays a color swatch and opens a color picker."""
    color_changed = pyqtSignal(str, QColor)

    def __init__(self, key_name: str, initial_color=QColor("black"), parent=None):
        super().__init__(parent)
        self.key_name = key_name
        self._color = QColor(initial_color)
        self.setFixedSize(QSize(130, 28))
        self.setIconSize(QSize(20, 20))
        self._update_swatch()
        self.clicked.connect(self._pick_color)

    def _update_swatch(self):
        pixmap = QPixmap(self.iconSize())
        pixmap.fill(self._color)
        self.setIcon(QIcon(pixmap))
        self.setText(self._color.name().upper())

    def set_color(self, new_color: QColor, from_picker=False):
        new_color = QColor(new_color)
        if self._color != new_color:
            self._color = new_color
            self._update_swatch()
            if from_picker:
                self.color_changed.emit(self.key_name, self._color)

    def get_color(self) -> QColor:
        return self._color

    def _pick_color(self):
        dialog = QColorDialog(self._color, self)
        if dialog.exec():
            self.set_color(dialog.currentColor(), from_picker=True)


class ThemeEditorDialog(QDialog):
    """A dialog for creating, editing, and deleting UI themes."""
    custom_themes_changed = pyqtSignal()

    def __init__(self, theme_manager, parent=None):
        super().__init__(parent)
        self.theme_manager = theme_manager
        log.info("ThemeEditorDialog initializing...")
        self.setWindowTitle("Theme Customizer")
        self.setMinimumSize(QSize(950, 700))
        self.setModal(True)
        # MODIFIED: Added missing color keys to the group definitions for a complete UI
        self.COLOR_GROUPS = {
            "Window & General": ["window.background", "sidebar.background", "accent"],
            "Editor": ["editor.background", "editor.foreground", "editor.userHighlightBackground",
                       "editor.lineHighlightBackground", "editor.selectionBackground"],
            "Editor Gutter": ["editorGutter.background",
                              "editorGutter.foreground", "editorLineNumber.foreground",
                              "editorLineNumber.activeForeground"],
            "Editor Matching": ["editor.matchingBracketBackground",
                                "editor.matchingBracketForeground"],
            "Controls": ["button.background", "button.foreground",
                         "input.background", "input.foreground", "input.border"],
            "Bars & Menus": ["statusbar.background", "statusbar.foreground",
                             "menu.background", "menu.foreground"],
            "Editor Tabs": ["tab.activeBackground", "tab.inactiveBackground",
                            "tab.activeForeground", "tab.inactiveForeground"],
            "Scrollbar": ["scrollbar.background", "scrollbar.handle",
                          "scrollbar.handleHover", "scrollbar.handlePressed"],
            "Syntax Highlighting": [
                "syntax.keyword", "syntax.operator", "syntax.brace",
                "syntax.decorator", "syntax.self", "syntax.className",
                "syntax.functionName", "syntax.comment", "syntax.string",
                "syntax.docstring", "syntax.number"
            ],
            "Git Status": [
                "git.added", "git.modified", "git.deleted",
                "git.status.foreground"
            ],
            "Tree View": [
                "tree.indentationGuides.stroke", "tree.trace.color",
                "tree.trace.shadow", "tree.node.color", "tree.node.fill"
            ]
        }
        self.current_theme_id = None
        self.is_custom_theme = False
        self.color_widgets = {}
        self.unsaved_changes = False
        self._setup_ui()
        self._repopulate_theme_list()
        self._update_ui_state()
        log.info("ThemeEditorDialog initialized successfully.")

    def _setup_ui(self):
        self.main_layout = QVBoxLayout(self)
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        self.main_layout.addWidget(self.splitter, 1)
        self._create_left_pane()
        self._create_right_pane()
        self.splitter.setSizes([240, 710])
        self.button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        self.button_box.rejected.connect(self.reject)
        self.main_layout.addWidget(self.button_box)

    def _create_left_pane(self):
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.addWidget(QLabel("<b>Available Themes:</b>"))
        self.theme_list_widget = QListWidget()
        self.theme_list_widget.setAlternatingRowColors(True)
        self.theme_list_widget.currentItemChanged.connect(
            self._on_theme_selection_changed
        )
        layout.addWidget(self.theme_list_widget, 1)
        actions_layout = QHBoxLayout()
        self.duplicate_button = QPushButton("Duplicate")
        self.delete_button = QPushButton("Delete")
        self.duplicate_button.clicked.connect(self._action_duplicate_theme)
        self.delete_button.clicked.connect(self._action_delete_theme)
        actions_layout.addWidget(self.duplicate_button)
        actions_layout.addWidget(self.delete_button)
        layout.addLayout(actions_layout)
        self.splitter.addWidget(container)

    def _create_right_pane(self):
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(10, 5, 5, 5)
        form_layout = QGridLayout()
        form_layout.addWidget(QLabel("<b>Theme Name:</b>"), 0, 0)
        self.name_edit = QLineEdit()
        self.name_edit.textChanged.connect(self._mark_unsaved_changes)
        form_layout.addWidget(self.name_edit, 0, 1)
        self.info_label = QLabel()
        self.info_label.setStyleSheet("font-style: italic; color: grey;")
        form_layout.addWidget(self.info_label, 1, 1)
        form_layout.setColumnStretch(1, 1)
        layout.addLayout(form_layout)
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        self.scroll_content = QWidget()
        self.v_scroll_layout = QVBoxLayout(self.scroll_content)
        self.v_scroll_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        scroll_area.setWidget(self.scroll_content)
        layout.addWidget(scroll_area, 1)
        actions_layout = QHBoxLayout()
        self.reset_button = QPushButton("Reset Changes")
        self.update_button = QPushButton("Update Custom Theme")
        self.reset_button.clicked.connect(self._load_theme_to_editor)
        self.update_button.clicked.connect(self._action_save)
        actions_layout.addWidget(self.reset_button)
        actions_layout.addStretch()
        actions_layout.addWidget(self.update_button)
        layout.addLayout(actions_layout)
        self.splitter.addWidget(container)

    def _repopulate_theme_list(self, select_theme_id=None):
        self.theme_list_widget.blockSignals(True)
        self.theme_list_widget.clear()
        all_themes = self.theme_manager.get_available_themes_for_ui()
        target_row = 0
        current_selection = (select_theme_id or self.current_theme_id or
                             self.theme_manager.current_theme_id)
        for i, (theme_id, name) in enumerate(all_themes.items()):
            item = QListWidgetItem(name)
            item.setData(Qt.ItemDataRole.UserRole, theme_id)
            theme_data = self.theme_manager.all_themes_data.get(theme_id, {})
            if theme_data and theme_data.get("is_custom"):
                item.setFont(QFont(self.font().family(), -1, QFont.Weight.Bold))
            self.theme_list_widget.addItem(item)
            if theme_id == current_selection:
                target_row = i
        self.theme_list_widget.setCurrentRow(target_row)
        self.theme_list_widget.blockSignals(False)
        self._on_theme_selection_changed(
            self.theme_list_widget.currentItem(), None
        )

    def _on_theme_selection_changed(self, current, previous):
        if not current:
            self._clear_editor()
            return

        if self.unsaved_changes and current is not previous:
            reply = QMessageBox.question(
                self, "Unsaved Changes",
                "Discard changes to the previous theme?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.No:
                self.theme_list_widget.blockSignals(True)
                if previous:
                    self.theme_list_widget.setCurrentItem(previous)
                self.theme_list_widget.blockSignals(False)
                return

        new_theme_id = current.data(Qt.ItemDataRole.UserRole)
        if new_theme_id != self.current_theme_id:
            self.current_theme_id = new_theme_id
            self._load_theme_to_editor()

    def _load_theme_to_editor(self):
        theme_data = self.theme_manager.all_themes_data.get(self.current_theme_id, {})
        if not theme_data or "colors" not in theme_data:
            self._clear_editor()
            return

        self._clear_layout(self.v_scroll_layout)
        self.color_widgets.clear()

        self.is_custom_theme = theme_data.get("is_custom", False)
        self.name_edit.setText(theme_data.get("name", ""))
        self.name_edit.setReadOnly(not self.is_custom_theme)
        self.info_label.setText(f"Author: {theme_data.get('author', 'N/A')}")

        all_color_keys = theme_data["colors"].keys()
        sorted_keys = sorted(all_color_keys)

        for group_name, prefixes in self.COLOR_GROUPS.items():
            group_keys = [k for k in sorted_keys if
                          any(k.startswith(p) for p in prefixes)]
            if not group_keys:
                continue

            group_box = QGroupBox(group_name)
            grid = QGridLayout(group_box)
            grid.setSpacing(5)
            row, col = 0, 0
            for key in group_keys:
                color_val = QColor(theme_data["colors"].get(key, '#ff00ff'))
                picker = ColorPickerButton(key, color_val)
                picker.setEnabled(self.is_custom_theme)
                picker.color_changed.connect(self._mark_unsaved_changes)
                self.color_widgets[key] = picker
                grid.addWidget(QLabel(f"{key.split('.')[-1]}:"), row, col)
                grid.addWidget(picker, row, col + 1)
                col += 2
                if col >= 4:
                    col = 0
                    row += 1
            self.v_scroll_layout.addWidget(group_box)

        self.v_scroll_layout.addStretch()
        self.unsaved_changes = False
        self._update_ui_state()

    def _action_duplicate_theme(self):
        if not self.current_theme_id:
            return
        original_theme = copy.deepcopy(
            self.theme_manager.all_themes_data.get(self.current_theme_id)
        )
        if not original_theme:
            return

        new_name = f"{original_theme.get('name', 'New Theme')} (Copy)"
        safe_name = re.sub(r'[^a-z0-9_]', '', new_name.lower())
        timestamp = int(datetime.datetime.now().timestamp())
        new_id = f"custom_{safe_name}_{timestamp}"

        original_theme['name'] = new_name
        original_theme['author'] = "PuffinPy User"
        original_theme['is_custom'] = True

        self.theme_manager.add_or_update_custom_theme(new_id, original_theme)
        self.custom_themes_changed.emit()
        self._repopulate_theme_list(select_theme_id=new_id)

    def _action_delete_theme(self):
        if not self.current_theme_id or not self.is_custom_theme:
            return
        theme_data = self.theme_manager.all_themes_data.get(self.current_theme_id)
        theme_name = theme_data.get('name', self.current_theme_id)
        reply = QMessageBox.question(
            self, "Confirm Delete",
            f"Are you sure you want to delete the theme '{theme_name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.theme_manager.delete_custom_theme(self.current_theme_id)
            self.custom_themes_changed.emit()
            if self.current_theme_id == self.theme_manager.current_theme_id:
                self.theme_manager.set_theme("puffin_dark")
            self._repopulate_theme_list(select_theme_id="puffin_dark")

    def _action_save(self):
        if not self.is_custom_theme or not self.unsaved_changes:
            return
        theme_data = copy.deepcopy(
            self.theme_manager.all_themes_data.get(self.current_theme_id)
        )
        theme_data['name'] = self.name_edit.text()
        for key, widget in self.color_widgets.items():
            theme_data['colors'][key] = widget.get_color().name()

        self.theme_manager.add_or_update_custom_theme(self.current_theme_id, theme_data)
        self.custom_themes_changed.emit()
        self.unsaved_changes = False
        self._update_ui_state()
        if self.current_theme_id == self.theme_manager.current_theme_id:
            self.theme_manager.set_theme(self.current_theme_id)
        QMessageBox.information(
            self, "Success", f"Theme '{theme_data['name']}' has been updated."
        )

    def _mark_unsaved_changes(self, *args):
        if self.is_custom_theme:
            self.unsaved_changes = True
            self._update_ui_state()

    def _update_ui_state(self):
        has_selection = self.current_theme_id is not None
        can_edit = self.is_custom_theme
        self.name_edit.setEnabled(can_edit)
        self.reset_button.setEnabled(can_edit and self.unsaved_changes)
        self.update_button.setEnabled(can_edit and self.unsaved_changes)
        self.delete_button.setEnabled(can_edit)
        self.duplicate_button.setEnabled(has_selection)
        for widget in self.color_widgets.values():
            widget.setEnabled(can_edit)

    def _clear_layout(self, layout):
        if layout is None:
            return
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
            else:
                sub_layout = item.layout()
                if sub_layout is not None:
                    self._clear_layout(sub_layout)

    def _clear_editor(self):
        self._clear_layout(self.v_scroll_layout)
        self.name_edit.clear()
        self.info_label.clear()
        self.current_theme_id = None
        self.is_custom_theme = False
        self.unsaved_changes = False
        self._update_ui_state()

    def reject(self):
        if self.unsaved_changes:
            reply = QMessageBox.question(
                self, "Unsaved Changes", "Discard changes and close?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.Yes:
                super().reject()
        else:
            super().reject()
```

### File: `/plugins/theme_editor/plugin_main.py`
```py
# PuffinPyEditor/plugins/theme_editor/plugin_main.py
from .theme_editor_dialog import ThemeEditorDialog
from app_core.puffin_api import PuffinPluginAPI
from utils.logger import log


class ThemeEditorPlugin:
    """Initializes the Theme Editor and connects it to the UI."""

    def __init__(self, puffin_api: PuffinPluginAPI):
        self.api = puffin_api
        self.main_window = self.api.get_main_window()
        # Correctly get the theme_manager via the API
        self.theme_manager = self.api.get_manager("theme")
        self.dialog_instance = None

        # This action will be added to the "Tools" menu.
        self.action = self.api.add_menu_action(
            menu_name="tools",
            text="Theme Editor...",
            callback=self.show_theme_editor_dialog,
            icon_name="fa5s.palette"
        )

        # Let the core application know how to launch this plugin's main feature.
        # This is used by the Preferences dialog.
        self.api.register_theme_editor_launcher(self.show_theme_editor_dialog)
        log.info("Theme Editor registered its launcher with the core API.")

    def show_theme_editor_dialog(self):
        """Creates and shows the theme editor dialog."""
        # Lazily create the dialog instance to save resources on startup
        if self.dialog_instance is None or not self.dialog_instance.parent():
            self.dialog_instance = ThemeEditorDialog(self.theme_manager, self.main_window)
            # When a theme is saved/deleted in the dialog, tell the main window to update its menus
            self.dialog_instance.custom_themes_changed.connect(
                self.main_window._rebuild_theme_menu
            )
        self.dialog_instance.exec()

    def shutdown(self):
        """
        A cleanup method called by the plugin manager before unloading.
        This is crucial for preventing errors on plugin reloads.
        """
        log.info("Theme Editor plugin is shutting down.")
        if self.action:
            # Safely remove the menu action from the UI
            if menu := self.api.get_menu("tools"):
                menu.removeAction(self.action)
            self.action.deleteLater()
        if self.dialog_instance:
            self.dialog_instance.deleteLater()


def initialize(puffin_api: PuffinPluginAPI):
    """Entry point for the Theme Editor plugin."""
    return ThemeEditorPlugin(puffin_api)
```

### File: `/plugins/theme_editor/plugin.json`
```json
{
    "id": "theme_editor",
    "name": "Theme Editor",
    "version": "1.0.0",
    "author": "PuffinPy",
    "description": "A graphical editor for creating and modifying UI themes.",
    "entry_point": "plugin_main.py",
    "dependencies": {}
}
```

### File: `/plugins/terminal/terminal_widget.py`
```py
# PuffinPyEditor/plugins/terminal/terminal_widget.py
import os
import sys
import platform
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QTextEdit, QMenu, QFileDialog, QApplication,
                             QHBoxLayout, QPushButton, QFrame)
from PyQt6.QtGui import QColor, QFont, QTextCursor, QKeySequence
from PyQt6.QtCore import QProcess, Qt
import qtawesome as qta
from utils.logger import log


class TerminalWidget(QWidget):
    """An interactive terminal widget that runs a native shell process."""

    def __init__(self, puffin_api):
        super().__init__()
        self.api = puffin_api
        self.project_manager = self.api.get_manager("project")
        self.settings = self.api.get_manager("settings")
        self.theme_manager = self.api.get_manager("theme")

        self.process = QProcess(self)
        self.input_start_position = 0

        self._setup_ui()
        self._connect_signals()
        self.update_theme()
        self.start_shell()

    def _setup_ui(self):
        """Initializes the UI components."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Toolbar for buttons
        toolbar = QFrame()
        toolbar.setObjectName("TerminalToolbar")
        toolbar_layout = QHBoxLayout(toolbar)
        toolbar_layout.setContentsMargins(5, 2, 5, 2)

        self.clear_button = QPushButton(qta.icon('fa5s.broom'), "Clear")
        self.stop_button = QPushButton(qta.icon('fa5s.stop-circle'), "Stop Process")

        toolbar_layout.addWidget(self.clear_button)
        toolbar_layout.addWidget(self.stop_button)
        toolbar_layout.addStretch()
        main_layout.addWidget(toolbar)

        # Main terminal text area
        self.output_area = QTextEdit()
        self.output_area.setAcceptRichText(False)
        self.output_area.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        main_layout.addWidget(self.output_area)

    def _connect_signals(self):
        """Connects signals for the process and UI."""
        self.process.readyReadStandardOutput.connect(self._handle_stdout)
        self.process.readyReadStandardError.connect(self._handle_stderr)
        self.process.finished.connect(self._on_process_finished)

        self.clear_button.clicked.connect(self.clear_terminal)
        self.stop_button.clicked.connect(self.stop_process)
        self.output_area.customContextMenuRequested.connect(self._show_context_menu)

        # We must override the key press event to handle input.
        self.output_area.keyPressEvent = self.keyPressEvent

    def update_theme(self):
        """Applies colors and fonts from the current theme."""
        font = QFont(self.settings.get("font_family"), self.settings.get("font_size"))
        self.output_area.setFont(font)

        colors = self.theme_manager.current_theme_data.get('colors', {})
        bg = colors.get('editor.background', '#1E1E1E')
        fg = colors.get('editor.foreground', '#D4D4D4')
        toolbar_bg = colors.get('sidebar.background', '#252526')
        border = colors.get('input.border', '#3c3c3c')

        self.setStyleSheet(f"""
            TerminalWidget {{ background-color: {bg}; }}
            #TerminalToolbar {{ 
                background-color: {toolbar_bg}; 
                border-bottom: 1px solid {border}; 
            }}
            QTextEdit {{
                background-color: {bg};
                color: {fg};
                border: none;
                padding: 5px;
            }}
        """)

    def start_shell(self):
        """Starts the appropriate native shell for the OS."""
        if self.process.state() == QProcess.ProcessState.Running:
            return

        project_path = self.project_manager.get_active_project_path()
        start_dir = project_path if project_path and os.path.isdir(project_path) else os.path.expanduser("~")

        shell_cmd, args = "", []
        if platform.system() == "Windows":
            shell_cmd = "cmd.exe"
            args = ["/K", "prompt $g"]  # Keep open, set prompt to ">"
        else:
            shell_cmd = os.environ.get("SHELL", "/bin/bash")

        self.process.setWorkingDirectory(start_dir)
        self.process.start(shell_cmd, args)
        log.info(f"Terminal started in '{start_dir}' with shell '{shell_cmd}'.")
        self.output_area.setFocus()

    def keyPressEvent(self, event):
        """Handles user input, sending it to the shell process."""
        cursor = self.output_area.textCursor()

        # Stop user from deleting the prompt or previous output
        if cursor.position() < self.input_start_position:
            cursor.setPosition(self.input_start_position)
            self.output_area.setTextCursor(cursor)

        if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            command = self.output_area.toPlainText()[self.input_start_position:]
            QTextEdit.keyPressEvent(self.output_area, event)  # Let the editor handle the newline
            self.process.write((command + "\n").encode())
            return

        # Basic backspace protection
        if event.key() == Qt.Key.Key_Backspace:
            if cursor.position() > self.input_start_position:
                QTextEdit.keyPressEvent(self.output_area, event)
            return

        # Ctrl+C to stop current process in shell
        if event.key() == Qt.Key.Key_C and event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            self.process.write(b'\x03')  # Send SIGINT
            return

        QTextEdit.keyPressEvent(self.output_area, event)

    def _append_text(self, text, color=None):
        """Appends text to the output, scrolling to the end."""
        cursor = self.output_area.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        self.output_area.setTextCursor(cursor)

        if color: self.output_area.setTextColor(color)
        self.output_area.insertPlainText(text)
        if color: self.output_area.setTextColor(QColor(self.settings.get('editor.foreground')))

        self.output_area.verticalScrollBar().setValue(self.output_area.verticalScrollBar().maximum())
        self.input_start_position = self.output_area.textCursor().position()

    def _handle_stdout(self):
        data = self.process.readAllStandardOutput().data().decode(errors='ignore')
        self._append_text(data)

    def _handle_stderr(self):
        data = self.process.readAllStandardError().data().decode(errors='ignore')
        colors = self.theme_manager.current_theme_data.get('colors', {})
        error_color = QColor(colors.get('syntax.comment', '#cd5c5c'))
        self._append_text(data, color=error_color)

    def _on_process_finished(self):
        self._append_text("\n[Process finished. Relaunching shell...]\n")
        self.start_shell()

    def _show_context_menu(self, pos):
        """Displays a custom context menu."""
        menu = QMenu()
        menu.addAction(qta.icon('fa5.copy'), "Copy", self.output_area.copy)
        menu.addAction("Paste", self.output_area.paste)
        menu.addSeparator()
        menu.addAction("Copy All", self.copy_all)
        menu.addSeparator()
        menu.addAction(qta.icon('fa5s.file-export'), "Export Session...", self.export_to_file)
        menu.exec(self.output_area.mapToGlobal(pos))

    def copy_all(self):
        QApplication.clipboard().setText(self.output_area.toPlainText())

    def export_to_file(self):
        path, _ = QFileDialog.getSaveFileName(self, "Export Terminal Session", "", "Text Files (*.txt);;All Files (*)")
        if path:
            try:
                with open(path, 'w', encoding='utf-8') as f:
                    f.write(self.output_area.toPlainText())
                log.info(f"Terminal session exported to {path}")
            except Exception as e:
                log.error(f"Failed to export terminal session: {e}")

    def clear_terminal(self):
        self.output_area.clear()
        # On Windows, sending a 'cls' command is a clean way to clear
        if platform.system() == "Windows":
            self.process.write(b'cls\n')
        else:  # For other systems, just restart the shell for a clean slate
            self.stop_process()
            self.start_shell()

    def stop_process(self):
        if self.process and self.process.state() != QProcess.ProcessState.NotRunning:
            log.info("Stopping terminal process...")
            # Disconnect all signals to prevent dangling calls during shutdown
            try:
                self.process.readyReadStandardOutput.disconnect()
                self.process.readyReadStandardError.disconnect()
                self.process.finished.disconnect()
                if hasattr(self.process, 'errorOccurred'):
                    self.process.errorOccurred.disconnect()
            except TypeError:
                pass  # Signals might have already been disconnected

            # Forcefully terminate the process
            self.process.kill()

            # Wait for it to finish to avoid the "Destroyed while running" warning
            if not self.process.waitForFinished(2000):
                log.warning("Terminal process did not terminate within 2 seconds of being killed.")

    def closeEvent(self, event):
        """Ensure the shell process is terminated when the widget closes."""
        self.stop_process()
        super().closeEvent(event)
```

### File: `/plugins/terminal/plugin_main.py`
```py
# PuffinPyEditor/plugins/terminal/plugin_main.py
from PyQt6.QtCore import Qt
from utils.logger import log
from .terminal_widget import TerminalWidget
from app_core.puffin_api import PuffinPluginAPI


class TerminalPlugin:
    def __init__(self, puffin_api: PuffinPluginAPI):
        self.api = puffin_api
        self.terminal_widget = None

        self._setup_ui()
        log.info("Integrated Terminal plugin initialized.")

    def _setup_ui(self):
        """Creates and registers the terminal panel and menu action."""
        self.terminal_widget = TerminalWidget(self.api)

        # THE FIX: This call now passes a string for the area, as expected by the API layer.
        dock = self.api.add_dock_panel(
            area_str="bottom",
            widget=self.terminal_widget,
            title="Terminal",
            icon_name="mdi.console"
        )

        if dock and dock.toggleViewAction():
            self.api.add_menu_action(
                menu_name="view",
                text="Terminal",
                callback=dock.toggleViewAction().trigger,
                icon_name="mdi.console"
            )

    def shutdown(self):
        """
        Called by the plugin manager or main window to ensure the terminal's
        underlying shell process is terminated correctly.
        """
        if self.terminal_widget:
            self.terminal_widget.stop_process()
            log.info("Terminal process stopped on shutdown request.")


def initialize(puffin_api: PuffinPluginAPI):
    """Entry point for PuffinPyEditor to load the plugin."""
    try:
        return TerminalPlugin(puffin_api)
    except Exception as e:
        log.error(f"Failed to initialize Terminal Plugin: {e}", exc_info=True)
        return None
```

### File: `/plugins/terminal/plugin.json`
```json
{
    "id": "terminal",
    "name": "Integrated Terminal",
    "author": "PuffinPy Team",
    "version": "1.0.0",
    "description": "Provides a dockable, theme-aware terminal that runs a native shell within the editor.",
    "entry_point": "plugin_main.py"
}
```

### File: `/plugins/terminal/__init__.py`
```py
# This file makes this directory a Python package.

```

### File: `/plugins/script_runner/plugin_main.py`
```py
# PuffinPyEditor/plugins/script_runner/plugin_main.py
import os
import sys
import shutil
import platform
from PyQt6.QtWidgets import QMessageBox
from PyQt6.QtCore import QObject, QProcess, QTimer
from app_core.puffin_api import PuffinPluginAPI
from .output_panel import OutputPanel
from .code_runner import _find_python_interpreter
from utils.logger import log


class ScriptRunnerPlugin(QObject):
    def __init__(self, puffin_api: PuffinPluginAPI):
        super().__init__()
        self.api = puffin_api
        self.main_window = self.api.get_main_window()
        # THE FIX: Pass the theme_manager to the OutputPanel
        self.output_panel = OutputPanel(
            theme_manager=self.api.get_manager("theme"),
            parent=self.main_window
        )
        self.process = None
        self._current_task_info = {}

        self.RUN_CONFIG = {
            '.py': {'handler': self._run_python_script, 'menu_text': 'Run Python Script', 'shortcut': 'F5',
                    'icon': 'mdi.language-python'},
            '.js': {'handler': self._run_node_script, 'menu_text': 'Run JS File', 'shortcut': 'Ctrl+F5',
                    'icon': 'mdi.language-javascript'},
            '.cpp': {'handler': self._compile_run_cpp, 'menu_text': 'Compile & Run C++', 'shortcut': 'F6',
                     'icon': 'mdi.language-cpp'},
            '.c': {'handler': self._compile_run_cpp, 'menu_text': 'Compile & Run C', 'shortcut': 'F6',
                   'icon': 'mdi.language-cpp'},
            '.cs': {'handler': self._compile_run_csharp, 'menu_text': 'Compile & Run C#', 'shortcut': 'F7',
                    'icon': 'mdi.language-csharp'},
        }
        self.run_actions = {}
        self._setup_ui()
        self._connect_signals()

    def _setup_ui(self):
        self.api.add_dock_panel(
            widget=self.output_panel,
            title="Output",
            area_str="bottom",
            icon_name='mdi.console-line'
        )
        for config in self.RUN_CONFIG.values():
            action = self.api.add_menu_action("run", config['menu_text'], config['handler'], config['shortcut'],
                                              config['icon'])
            action.setEnabled(False)
            self.run_actions[config['menu_text']] = action

        self.stop_action = self.api.add_menu_action("run", "Stop Script", self.stop_script, "Ctrl+F2",
                                                    'mdi.stop-circle-outline')
        self.stop_action.setEnabled(False)

        py_action = self.run_actions['Run Python Script']
        self.api.add_toolbar_action(py_action)
        self.api.add_toolbar_action(self.stop_action)

    def _connect_signals(self):
        self.main_window.tab_widget.currentChanged.connect(self._on_tab_changed)
        QTimer.singleShot(0, lambda: self._on_tab_changed(self.main_window.tab_widget.currentIndex()))
        self.main_window.theme_changed_signal.connect(self.output_panel.update_theme)

    def _on_tab_changed(self, index):
        from ui.editor_widget import EditorWidget
        active_ext = None
        if index != -1:
            if widget := self.main_window.tab_widget.widget(index):
                if hasattr(widget, 'filepath') and widget.filepath:
                    _, active_ext = os.path.splitext(widget.filepath)

        for ext, config in self.RUN_CONFIG.items():
            action = self.run_actions.get(config['menu_text'])
            if action:
                action.setEnabled(ext == active_ext)

    def stop_script(self):
        if self.process and self.process.state() != QProcess.ProcessState.NotRunning:
            self.output_panel.append_output("[Runner] Terminating process...\n", is_error=True)
            self.process.terminate()
            if not self.process.waitForFinished(1000):
                self.process.kill()
                self.output_panel.append_output("[Runner] Process killed.\n", is_error=True)
        else:
            self._on_run_finished(-1)

    def _get_current_filepath(self):
        from ui.editor_widget import EditorWidget
        editor = self.main_window.tab_widget.currentWidget()
        if not hasattr(editor, 'filepath'):
            return None

        filepath = editor.filepath
        if not filepath:
            self.api.show_message("info", "Save File", "Please save the file before running.")
            return None

        if self.main_window._is_editor_modified(editor):
            self.main_window._action_save_file()

        return filepath

    def run_specific_script(self, filepath: str):
        ext = os.path.splitext(filepath)[1].lower()
        for config_ext, config in self.RUN_CONFIG.items():
            if ext == config_ext:
                config['handler'](filepath=filepath)
                return
        self.api.show_message("warning", "Unsupported File Type", f"No run configuration for '{ext}' files.")

    def _run_python_script(self, filepath: str = None):
        filepath = filepath or self._get_current_filepath()
        if not filepath: return
        if not (interpreter_path := _find_python_interpreter()):
            self.api.show_message("critical", "Python Not Found", "Could not find a Python interpreter.")
            return

        self._current_task_info = {'name': 'Python Script'}
        self._start_process(interpreter_path, [filepath])

    def _run_node_script(self, filepath: str = None):
        filepath = filepath or self._get_current_filepath()
        if not filepath: return
        if not (node_path := shutil.which("node")):
            self.api.show_message("critical", "Node.js Not Found", "Could not find 'node' on your system PATH.")
            return

        self._current_task_info = {'name': 'Node.js Script'}
        self._start_process(node_path, [filepath])

    def _compile_run_cpp(self, filepath: str = None):
        source_path = filepath or self._get_current_filepath()
        if not source_path: return
        compiler_path = shutil.which("g++") or shutil.which("cl")
        if not compiler_path:
            self.api.show_message("critical", "Compiler Not Found", "No C++ compiler (g++ or cl.exe) found.")
            return

        source_dir = os.path.dirname(source_path)
        base_name = os.path.splitext(os.path.basename(source_path))[0]
        exe_path = os.path.join(source_dir, base_name + (".exe" if platform.system() == "Windows" else ""))

        if "g++" in os.path.basename(compiler_path):
            args = [source_path, "-o", exe_path, "-std=c++17", "-Wall"]
        else:
            args = [source_path, f"/Fe:{exe_path}", "/EHsc"]

        self._current_task_info = {'name': 'C++ Compilation', 'type': 'compile', 'runner_path': exe_path}
        self._start_process(compiler_path, args)

    def _compile_run_csharp(self, filepath: str = None):
        source_path = filepath or self._get_current_filepath()
        if not source_path: return
        if not (compiler_path := shutil.which("csc")):
            self.api.show_message("critical", "C# Compiler Not Found", "C# compiler (csc.exe) not found.")
            return

        source_dir = os.path.dirname(source_path)
        base_name = os.path.splitext(os.path.basename(source_path))[0]
        exe_path = os.path.join(source_dir, f"{base_name}.exe")

        args = [f"/out:{exe_path}", source_path]
        self._current_task_info = {'name': 'C# Compilation', 'type': 'compile', 'runner_path': exe_path}
        self._start_process(compiler_path, args)

    def _start_process(self, program, args):
        if self.process and self.process.state() != QProcess.ProcessState.NotRunning:
            self.output_panel.append_output("[Runner] A process is already running.", is_error=True)
            return

        self.output_panel.clear_output()
        self.output_panel.append_output(f"[{self._current_task_info.get('name', 'Process')}] Starting...")
        self.output_panel.append_output(f"> {os.path.basename(program)} {' '.join(args)}\n")

        self.process = QProcess()
        self.process.readyReadStandardOutput.connect(self._handle_stdout)
        self.process.readyReadStandardError.connect(self._handle_stderr)
        self.process.finished.connect(self._handle_finished)
        self.process.setWorkingDirectory(os.path.dirname(args[0]))

        self.stop_action.setEnabled(True)
        self.process.start(program, args)

    def _handle_stdout(self):
        if self.process: self.output_panel.append_output(
            self.process.readAllStandardOutput().data().decode(errors='replace'))

    def _handle_stderr(self):
        if self.process: self.output_panel.append_output(
            self.process.readAllStandardError().data().decode(errors='replace'), is_error=True)

    def _handle_finished(self, exit_code, exit_status):
        task_name = self._current_task_info.get('name', 'Process')
        task_type = self._current_task_info.get('type')

        if task_type == 'compile':
            if exit_code == 0:
                self.output_panel.append_output(f"\n[{task_name}] Compilation successful.")
                runner_path = self._current_task_info.get('runner_path')
                self._current_task_info = {'name': f"{task_name.split(' ')[0]} Execution", 'type': 'run',
                                           'runner_path': runner_path}
                self._start_process(runner_path, [])
            else:
                self.output_panel.append_output(f"\n[{task_name}] Compilation failed.", is_error=True)
                self._on_run_finished(exit_code)
        else:
            self.output_panel.append_output(f"\n[{task_name}] Finished with exit code {exit_code}.")
            runner_path = self._current_task_info.get('runner_path')
            if runner_path and os.path.exists(runner_path) and not runner_path.endswith(('.py', '.js')):
                try:
                    os.remove(runner_path)
                except OSError as e:
                    self.output_panel.append_output(f"Could not remove temporary file: {e}", is_error=True)
            self._on_run_finished(exit_code)

    def _on_run_finished(self, exit_code):
        self.stop_action.setEnabled(False)
        self.process = None
        self._current_task_info = {}
        self._on_tab_changed(self.main_window.tab_widget.currentIndex())


def initialize(puffin_api: PuffinPluginAPI):
    return ScriptRunnerPlugin(puffin_api)
```

### File: `/plugins/script_runner/plugin.json`
```json
{
    "id": "script_runner",
    "name": "Script Runner",
    "author": "PuffinPy Team",
    "version": "1.2.0",
    "description": "Adds functionality to run Python, C++, C#, and JavaScript files from the editor.",
    "entry_point": "plugin_main.py"
}
```

### File: `/plugins/script_runner/output_panel.py`
```py
# PuffinPyEditor/plugins/script_runner/output_panel.py
from typing import TYPE_CHECKING
from PyQt6.QtWidgets import QDockWidget, QTextEdit, QVBoxLayout, QWidget, QPushButton, QHBoxLayout
from PyQt6.QtGui import QFont, QColor, QTextCursor
from PyQt6.QtCore import Qt
from app_core.settings_manager import settings_manager

if TYPE_CHECKING:
    from app_core.theme_manager import ThemeManager

class OutputPanel(QDockWidget):
    def __init__(self, theme_manager: "ThemeManager", parent=None):
        super().__init__("Output", parent)
        self.theme_manager = theme_manager
        self.setObjectName("OutputPanelDock")
        self.setAllowedAreas(Qt.DockWidgetArea.BottomDockWidgetArea |
                             Qt.DockWidgetArea.RightDockWidgetArea)

        self.container_widget = QWidget()
        self.layout = QVBoxLayout(self.container_widget)
        self.layout.setContentsMargins(2, 2, 2, 2)

        self.control_bar_layout = QHBoxLayout()
        self.clear_button = QPushButton("Clear")
        self.clear_button.clicked.connect(self.clear_output)
        self.control_bar_layout.addWidget(self.clear_button)
        self.control_bar_layout.addStretch(1)
        self.layout.addLayout(self.control_bar_layout)

        self.output_text_edit = QTextEdit()
        self.output_text_edit.setReadOnly(True)
        self.layout.addWidget(self.output_text_edit)

        self.container_widget.setLayout(self.layout)
        self.setWidget(self.container_widget)

        self.update_theme()

    def append_output(self, text: str, is_error: bool = False):
        """
        Appends text to the output panel, handling color for errors and ensuring
        correct line endings.
        """
        # --- FIX: Use insertPlainText with a cursor to prevent extra newlines ---
        cursor = self.output_text_edit.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        self.output_text_edit.setTextCursor(cursor)
        
        original_format = cursor.charFormat()
        
        if is_error:
            colors = self.theme_manager.current_theme_data.get("colors", {})
            error_color_hex = colors.get("syntax.comment", "#FF4444")
            error_color = QColor(error_color_hex if error_color_hex else "#FF0000")
            
            error_format = cursor.charFormat()
            error_format.setForeground(error_color)
            cursor.setCharFormat(error_format)

        # Insert text without adding an automatic newline
        cursor.insertText(text)

        # Restore the original format
        if is_error:
            cursor.setCharFormat(original_format)

        # Keep scrolled to the bottom
        scrollbar = self.output_text_edit.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())


    def clear_output(self):
        self.output_text_edit.clear()

    def update_theme(self):
        font_family = settings_manager.get("font_family", "Consolas")
        font_size = settings_manager.get("font_size", 10)
        font = QFont(font_family, font_size)
        self.output_text_edit.setFont(font)

        colors = self.theme_manager.current_theme_data.get("colors", {})
        bg_color = colors.get("editor.background", "#1e1e1e")
        fg_color = colors.get("editor.foreground", "#d4d4d4")
        self.output_text_edit.setStyleSheet(f"background-color: {bg_color}; "
                                              f"color: {fg_color}; border: none;")
```

### File: `/plugins/script_runner/code_runner.py`
```py
# PuffinPyEditor/plugins/pythong_tools/code_runner.py
import os
import sys
import shutil
from PyQt6.QtCore import QObject, pyqtSignal, QProcess
from app_core.settings_manager import settings_manager
from utils.logger import log
from typing import Optional


def _find_python_interpreter() -> str:
    """
    Intelligently finds the best Python executable for running scripts.
    This prevents the app from trying to execute itself when frozen.

    Priority:
    1. User-defined path in settings.
    2. A 'python.exe' bundled alongside the main PuffinPyEditor.exe.
    3. The python.exe from the current virtual environment (if from source).
    4. The first 'python' found on the system's PATH.

    Returns:
        The path to a suitable Python executable, or an empty string.
    """
    # 1. User-defined path
    user_path = settings_manager.get("python_interpreter_path", "").strip()
    if user_path and os.path.exists(user_path) and \
            "PuffinPyEditor.exe" not in user_path:
        log.info(f"CodeRunner: Using user-defined interpreter: {user_path}")
        return user_path

    # 2. Local python.exe if frozen (e.g., if bundled with the app)
    if getattr(sys, 'frozen', False):
        local_python_path = os.path.join(os.path.dirname(sys.executable), "python.exe")
        if os.path.exists(local_python_path):
            log.info("CodeRunner: Found local python.exe in frozen app dir: "
                     f"{local_python_path}")
            return local_python_path

    # 3. Venv python if running from source
    if not getattr(sys, 'frozen', False):
        # Ensure we don't return the main app if it was launched via a script
        if "PuffinPyEditor.exe" not in sys.executable:
            log.info("CodeRunner: Running from source, using sys.executable: "
                     f"{sys.executable}")
            return sys.executable

    # 4. System PATH python
    system_python = shutil.which("python")
    if system_python and "PuffinPyEditor.exe" not in system_python:
        log.info(f"CodeRunner: Found system python on PATH: {system_python}")
        return system_python

    log.error("CodeRunner: Could not find a suitable Python interpreter.")
    return ""


class CodeRunner(QObject):
    """
    Manages the execution of Python scripts in a separate process.
    """
    output_received = pyqtSignal(str)
    error_received = pyqtSignal(str)
    process_finished = pyqtSignal(int)

    def __init__(self, parent: Optional[QObject] = None):
        super().__init__(parent)
        self.process: Optional[QProcess] = None

    def run_script(self, script_filepath: str):
        """
        Executes a Python script using the configured interpreter.

        Args:
            script_filepath: The absolute path to the Python script to run.
        """
        if not script_filepath or not os.path.exists(script_filepath):
            err_msg = f"Script path is invalid: {script_filepath}"
            log.error(err_msg)
            self.error_received.emit(err_msg + "\n")
            self.process_finished.emit(-1)
            return

        interpreter_path = _find_python_interpreter()

        if not interpreter_path:
            err_msg = ("Could not find a valid Python interpreter.\nPlease set "
                       "a path in Preferences or ensure 'python' is in your "
                       "system PATH.")
            log.error(err_msg)
            self.error_received.emit(err_msg + "\n")
            self.process_finished.emit(-1)
            return

        if self.process and self.process.state() != QProcess.ProcessState.NotRunning:
            warning_msg = "A script is already running. Please wait."
            log.warning(warning_msg)
            self.error_received.emit(f"[INFO] {warning_msg}\n")
            return

        self.process = QProcess()
        self.process.setProgram(interpreter_path)
        self.process.setArguments([script_filepath])

        # Set working dir to script's dir for correct relative imports
        script_dir = os.path.dirname(script_filepath)
        self.process.setWorkingDirectory(script_dir)
        log.info(f"Setting working directory for script to: {script_dir}")

        # Connect signals
        self.process.readyReadStandardOutput.connect(self._handle_stdout)
        self.process.readyReadStandardError.connect(self._handle_stderr)
        self.process.finished.connect(self._handle_finished)
        self.process.errorOccurred.connect(self._handle_process_error)

        log.info(f"Starting script: '{interpreter_path}' '{script_filepath}'")
        self.output_received.emit(
            f"[PuffinPyRun] Executing: {os.path.basename(script_filepath)} ...\n")
        self.process.start()

        if not self.process.waitForStarted(5000):
            err_msg = f"Failed to start process: {self.process.errorString()}"
            log.error(err_msg)
            self.error_received.emit(err_msg + "\n")
            self.process_finished.emit(self.process.exitCode())
            self.process = None  # Clean up the failed process
            return

        pid = self.process.processId() if self.process else 'N/A'
        log.debug(f"Process started successfully (PID: {pid}).")

    def stop_script(self):
        """Terminates the currently running script process."""
        if self.process and self.process.state() != QProcess.ProcessState.NotRunning:
            pid = self.process.processId()
            log.info(f"Attempting to terminate process (PID: {pid}).")
            self.output_received.emit("[PuffinPyRun] Terminating script...\n")
            self.process.terminate()
            # If terminate fails, forcefully kill it
            if not self.process.waitForFinished(1000):
                log.warning(f"Process {pid} did not terminate gracefully, killing.")
                self.process.kill()
                self.output_received.emit("[PuffinPyRun] Script process killed.\n")
            else:
                self.output_received.emit("[PuffinPyRun] Script process terminated.\n")
        else:
            log.info("Stop script requested, but no process is running.")

    def _handle_stdout(self):
        if self.process:
            data = self.process.readAllStandardOutput().data().decode(errors='replace')
            self.output_received.emit(data)

    def _handle_stderr(self):
        if self.process:
            data = self.process.readAllStandardError().data().decode(errors='replace')
            self.error_received.emit(data)

    def _handle_finished(self, exit_code: int, exit_status: QProcess.ExitStatus):
        log.info(f"Script finished. Exit code: {exit_code}, Status: {exit_status.name}")
        if exit_status == QProcess.ExitStatus.CrashExit:
            self.error_received.emit("[PuffinPyRun] Script process crashed.\n")

        self.output_received.emit(
            f"[PuffinPyRun] Process finished with exit code {exit_code}.\n")
        self.process_finished.emit(exit_code)
        self.process = None  # Clean up after finishing

    def _handle_process_error(self, error: QProcess.ProcessError):
        if self.process:
            err_msg = f"[PuffinPyRun] QProcess Error: {self.process.errorString()} " \
                      f"(Code: {error.name})"
            log.error(err_msg)
            self.error_received.emit(err_msg + "\n")
```

### File: `/plugins/refactor_tool/refactor_dialog.py`
```py
# /plugins/refactor_tool/refactor_dialog.py
import os
import jedi
from typing import Optional, List, Dict
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QWidget, QFormLayout,
                             QLineEdit, QCheckBox, QPushButton, QTextEdit,
                             QMessageBox, QProgressDialog, QApplication)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt, pyqtSignal, QObject, QRunnable, QThreadPool

from app_core.puffin_api import PuffinPluginAPI
from app_core.completion_manager import find_python_interpreter_for_jedi
from utils.logger import log


class JediRefactorSignals(QObject):
    """Defines signals for the background refactoring worker."""
    preview_ready = pyqtSignal(str)
    refactor_finished = pyqtSignal(bool, str)
    error = pyqtSignal(str)


class JediRefactorWorker(QRunnable):
    """A worker thread to perform Jedi refactoring operations."""
    def __init__(self, script, new_name, get_diff=True):
        super().__init__()
        self.script: jedi.Script = script
        self.new_name: str = new_name
        self.get_diff: bool = get_diff
        self.signals = JediRefactorSignals()

    def run(self):
        try:
            refactoring = self.script.rename(new_name=self.new_name)
        except (jedi.RefactoringError, Exception) as e:
            self.signals.error.emit(f"Could not perform rename: {e}")
            return
            
        if self.get_diff:
            diff = refactoring.get_diff()
            self.signals.preview_ready.emit(diff)
        else:
            try:
                refactoring.apply()
                self.signals.refactor_finished.emit(True, "Refactoring applied successfully.")
            except Exception as e:
                self.signals.refactor_finished.emit(False, f"Failed to apply refactoring: {e}")


class RefactorDialog(QDialog):
    def __init__(self, puffin_api: PuffinPluginAPI, parent=None):
        super().__init__(parent)
        self.api = puffin_api
        self.main_window = self.api.get_main_window()
        self.project_manager = self.api.get_manager("project")
        
        # --- Jedi Setup ---
        python_executable = find_python_interpreter_for_jedi()
        project_path = self.project_manager.get_active_project_path()
        try:
            self.jedi_project = jedi.Project(path=project_path, environment_path=python_executable)
        except Exception as e:
            QMessageBox.critical(self, "Jedi Error", f"Could not initialize code analysis engine (Jedi): {e}")
            # Defer closing to allow the message box to show
            self.close() 
            return

        self.threadpool = QThreadPool()

        self._setup_ui()
        self._get_initial_state()

    def _setup_ui(self):
        self.setWindowTitle("Rename Symbol")
        self.setMinimumSize(700, 500)
        layout = QVBoxLayout(self)

        form_layout = QFormLayout()
        self.old_name_edit = QLineEdit()
        self.old_name_edit.setReadOnly(True)
        self.new_name_edit = QLineEdit()

        form_layout.addRow("Original Name:", self.old_name_edit)
        form_layout.addRow("New Name:", self.new_name_edit)
        layout.addLayout(form_layout)
        
        self.scope_checkbox = QCheckBox("Rename in entire project (disables preview)")
        self.scope_checkbox.toggled.connect(lambda checked: self.preview_button.setDisabled(checked))
        layout.addWidget(self.scope_checkbox)

        self.diff_viewer = QTextEdit()
        self.diff_viewer.setReadOnly(True)
        self.diff_viewer.setFont(QFont("Consolas", 10))
        layout.addWidget(self.diff_viewer, 1)

        button_layout = QHBoxLayout()
        self.preview_button = QPushButton("Preview Changes")
        self.apply_button = QPushButton("Apply")
        self.close_button = QPushButton("Close")

        button_layout.addStretch()
        button_layout.addWidget(self.preview_button)
        button_layout.addWidget(self.apply_button)
        button_layout.addWidget(self.close_button)
        layout.addLayout(button_layout)
        
        self.preview_button.clicked.connect(self._get_preview)
        self.apply_button.clicked.connect(self._apply_refactor)
        self.close_button.clicked.connect(self.close)

    def _get_initial_state(self):
        self.editor = self.main_window.tab_widget.currentWidget()
        cursor = self.editor.text_area.textCursor()
        
        selected_text = cursor.selectedText()
        # If nothing is selected, select the word under the cursor
        if not selected_text:
            cursor.select(cursor.SelectionType.WordUnderCursor)
            selected_text = cursor.selectedText()
            
        self.old_name_edit.setText(selected_text)
        self.new_name_edit.setText(selected_text)
        self.new_name_edit.setFocus()
        self.new_name_edit.selectAll()

    def _create_jedi_script(self):
        line, col = self.editor.get_cursor_position()
        source = self.editor.get_text()
        filepath = self.editor.filepath
        
        try:
            return jedi.Script(code=source, path=filepath, project=self.jedi_project,
                               line=line, column=col)
        except Exception as e:
            QMessageBox.critical(self, "Jedi Error", f"Could not create script context: {e}")
            return None

    def _get_preview(self):
        if not self._validate_input(): return
            
        script = self._create_jedi_script()
        if not script: return
        
        self._run_worker(script, get_diff=True)
    
    def _apply_refactor(self):
        if not self._validate_input(): return

        new_name = self.new_name_edit.text()
        old_name = self.old_name_edit.text()
        reply = QMessageBox.question(
            self,
            "Confirm Refactoring",
            f"Are you sure you want to rename all occurrences of '{old_name}' to '{new_name}'?\n\nThis action will modify files on disk.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.Cancel,
        )
        if reply == QMessageBox.StandardButton.Cancel: return
            
        script = self._create_jedi_script()
        if not script: return

        self._run_worker(script, get_diff=False)
    
    def _validate_input(self):
        new_name = self.new_name_edit.text().strip()
        if not new_name.isidentifier():
            QMessageBox.warning(self, "Invalid Name", f"'{new_name}' is not a valid Python identifier.")
            return False
        return True

    def _run_worker(self, script, get_diff):
        self.progress_dialog = QProgressDialog(self)
        self.progress_dialog.setLabelText("Analyzing code...")
        self.progress_dialog.setCancelButton(None)
        self.progress_dialog.setModal(True)
        self.progress_dialog.show()

        worker = JediRefactorWorker(script, self.new_name_edit.text(), get_diff=get_diff)
        worker.signals.preview_ready.connect(self._on_preview_ready)
        worker.signals.refactor_finished.connect(self._on_refactor_finished)
        worker.signals.error.connect(self._on_error)
        self.threadpool.start(worker)

    def _on_preview_ready(self, diff):
        self.progress_dialog.close()
        self.diff_viewer.setPlainText(diff)
        if not diff:
            self.diff_viewer.setText("(No changes detected in the current file)")
    
    def _on_refactor_finished(self, success, message):
        self.progress_dialog.close()
        if success:
            QMessageBox.information(self, "Success", message)
            self.api.get_main_window().explorer_panel.refresh()
            self.accept()
        else:
            QMessageBox.critical(self, "Error", message)
    
    def _on_error(self, message):
        self.progress_dialog.close()
        QMessageBox.critical(self, "Refactoring Error", message)
```

### File: `/plugins/refactor_tool/plugin_main.py`
```py
# /plugins/refactor_tool/plugin_main.py

from app_core.puffin_api import PuffinPluginAPI
from .refactor_dialog import RefactorDialog
from utils.logger import log


class RefactorPlugin:
    def __init__(self, puffin_api: PuffinPluginAPI):
        self.api = puffin_api
        self.main_window = self.api.get_main_window()
        self.dialog = None

        # Create a new top-level "Refactor" menu
        self.refactor_menu = self.api.get_main_window().menuBar().addMenu("&Refactor")
        
        # Add the "Rename Symbol" action to it
        self.rename_action = self.api.add_menu_action(
            menu_name="refactor",
            text="Rename Symbol...",
            callback=self.show_refactor_dialog,
            shortcut="F2",
            icon_name="mdi.pencil-box-outline"
        )
        self.refactor_menu.addAction(self.rename_action)

    def show_refactor_dialog(self):
        """Shows the refactoring dialog."""
        current_widget = self.main_window.tab_widget.currentWidget()
        if not hasattr(current_widget, 'text_area'):
            self.api.show_message("info", "No Editor Active",
                                  "Please open a file and select an identifier to refactor.")
            return
            
        self.dialog = RefactorDialog(self.api, self.main_window)
        self.dialog.exec()

    def shutdown(self):
        if self.refactor_menu:
            self.refactor_menu.clear()
            self.refactor_menu.deleteLater()
            
        log.info("Refactor Plugin shut down.")


def initialize(puffin_api: PuffinPluginAPI):
    """Entry point for the Refactor Plugin."""
    return RefactorPlugin(puffin_api)
```

### File: `/plugins/refactor_tool/plugin.json`
```json
{
    "id": "refactor_tool",
    "name": "Refactor Tool",
    "author": "PuffinPy AI",
    "version": "1.0.0",
    "description": "Provides context-aware renaming for variables, functions, and classes across files.",
    "entry_point": "plugin_main.py"
}
```

### File: `/plugins/plugin_publisher/publish_dialog.py`
```py
# PuffinPyEditor/plugins/plugin_publisher/publish_dialog.py
import os
import shutil
import tempfile
import json
import copy
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QFormLayout, QComboBox,
                             QTextEdit, QPushButton, QDialogButtonBox, QLabel,
                             QMessageBox, QHBoxLayout, QListWidget,
                             QListWidgetItem, QRadioButton, QGroupBox,
                             QLineEdit)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

# --- Content for auto-initializing a distro repo ---
README_CONTENT = """# PuffinPyEditor Plugin Distribution Repository
This repository is structured to serve plugins for the PuffinPyEditor.
- `index.json`: A manifest file listing all available plugins and their download URLs.
- `zips/`: This directory contains the packaged `.zip` files for each plugin.
To publish a new version of a plugin, use the "Publish Plugin" tool inside
PuffinPyEditor.
"""
GITIGNORE_CONTENT = """# Ignore common temp files
*.tmp, *.bak, *~
# Ignore local environment
venv/, .venv/
"""


def _bump_version(version_str, level='patch'):
    """Bumps a semantic version string."""
    try:
        parts = version_str.split('.')
        if len(parts) != 3 or not all(p.isdigit() for p in parts):
            return version_str
        major, minor, patch = [int(p) for p in parts]
        if level == 'patch':
            patch += 1
        elif level == 'minor':
            minor, patch = minor + 1, 0
        elif level == 'major':
            major, minor, patch = major + 1, 0, 0
        return f"{major}.{minor}.{patch}"
    except Exception:
        return version_str


class VersionConflictDialog(QDialog):
    """Dialog to resolve a version conflict by overwriting or creating a new version."""
    def __init__(self, plugin_name, local_version, remote_version, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Version Conflict")
        self.result = (None, None)  # (action, version)
        self.local_version = local_version

        layout = QVBoxLayout(self)
        msg = f"A version conflict was detected for <b>{plugin_name}</b>."
        layout.addWidget(QLabel(msg))

        info_layout = QFormLayout()
        info_layout.addRow("Your local version:", QLabel(f"<b>{local_version}</b>"))
        info_layout.addRow("Version in repository:",
                           QLabel(f"<b>{remote_version}</b>"))
        layout.addLayout(info_layout)

        group = QGroupBox("Choose an action:")
        group_layout = QVBoxLayout(group)

        self.overwrite_radio = QRadioButton(
            f"Overwrite with version {local_version}")
        self.new_version_radio = QRadioButton("Create a new version:")
        self.new_version_edit = QLineEdit(_bump_version(remote_version, 'patch'))

        new_version_layout = QHBoxLayout()
        new_version_layout.addWidget(self.new_version_radio)
        new_version_layout.addWidget(self.new_version_edit)

        group_layout.addWidget(self.overwrite_radio)
        group_layout.addLayout(new_version_layout)
        self.new_version_radio.setChecked(True)
        self.overwrite_radio.toggled.connect(self.toggle_line_edit)
        layout.addWidget(group)

        buttons = (QDialogButtonBox.StandardButton.Ok |
                   QDialogButtonBox.StandardButton.Cancel)
        button_box = QDialogButtonBox(buttons)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        self.toggle_line_edit(True)

    def toggle_line_edit(self, checked):
        self.new_version_edit.setEnabled(self.new_version_radio.isChecked())

    def accept(self):
        if self.overwrite_radio.isChecked():
            self.result = ('overwrite', self.local_version)
        elif self.new_version_radio.isChecked():
            new_version = self.new_version_edit.text().strip()
            if not new_version:
                QMessageBox.warning(self, "Invalid Version",
                                    "New version cannot be empty.")
                return
            self.result = ('new', new_version)
        super().accept()


class BumpVersionDialog(QDialog):
    """Dialog to ask the user how to bump the version of a new plugin."""
    def __init__(self, current_version, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Set Initial Version")
        self.current_version = current_version
        self.new_version = current_version

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Publishing a new plugin with initial version:"))

        group = QGroupBox("Choose version:")
        group_layout = QVBoxLayout(group)

        self.radios = {
            'none': QRadioButton(f"Keep current version ({current_version})"),
            'patch': QRadioButton(
                f"Patch -> {_bump_version(current_version, 'patch')}"),
            'minor': QRadioButton(
                f"Minor -> {_bump_version(current_version, 'minor')}"),
            'major': QRadioButton(
                f"Major -> {_bump_version(current_version, 'major')}")
        }

        self.radios['none'].setChecked(True)
        for radio in self.radios.values():
            group_layout.addWidget(radio)

        layout.addWidget(group)

        buttons = (QDialogButtonBox.StandardButton.Ok |
                   QDialogButtonBox.StandardButton.Cancel)
        button_box = QDialogButtonBox(buttons)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

    def accept(self):
        for level, radio in self.radios.items():
            if radio.isChecked():
                if level == 'none':
                    self.new_version = self.current_version
                else:
                    self.new_version = _bump_version(self.current_version, level)
                break
        super().accept()


class MultiPublishSelectionDialog(QDialog):
    """A dialog to select which plugins to include in a batch publish."""
    def __init__(self, plugins, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Select Plugins to Publish")
        self.setMinimumSize(400, 300)
        layout = QVBoxLayout(self)

        layout.addWidget(QLabel("Select plugins to include in this batch:"))
        self.list_widget = QListWidget()
        for plugin_data in plugins:
            display = (f"{plugin_data.get('name', 'Unknown')} "
                       f"v{plugin_data.get('version', '0.0.0')}")
            item = QListWidgetItem(display)
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            item.setCheckState(Qt.CheckState.Checked)
            item.setData(Qt.ItemDataRole.UserRole, plugin_data)
            self.list_widget.addItem(item)
        layout.addWidget(self.list_widget)

        buttons = (QDialogButtonBox.StandardButton.Ok |
                   QDialogButtonBox.StandardButton.Cancel)
        button_box = QDialogButtonBox(buttons)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

    def get_selected_plugins(self):
        selected = []
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            if item.checkState() == Qt.CheckState.Checked:
                selected.append(item.data(Qt.ItemDataRole.UserRole))
        return selected


class PublishDialog(QDialog):
    """A dialog to manage the process of publishing a plugin."""

    def __init__(self, api, parent):
        super().__init__(parent)
        self.api = api
        self.git_manager = api.get_manager("git")
        self.github_manager = api.get_manager("github")
        self.plugin_manager = api.get_manager("plugin")
        self.settings = api.get_manager("settings")
        self.publish_queue = []
        self._temp_dir = None
        self._current_step = None
        self.cloned_repo_path = None
        self.auto_increment_choice = False

        self.setWindowTitle("Publish a Plugin")
        self.setMinimumSize(600, 450)
        self._setup_ui()
        self._connect_ui_signals()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        form_layout = QFormLayout()

        self.plugin_selector = QComboBox()
        form_layout.addRow("Plugin to Publish:", self.plugin_selector)

        repo_layout = QHBoxLayout()
        repo_layout.setContentsMargins(0, 0, 0, 0)
        self.repo_combo = QComboBox()
        self.manage_repos_button = QPushButton("Manage...")
        repo_layout.addWidget(self.repo_combo, 1)
        repo_layout.addWidget(self.manage_repos_button)
        form_layout.addRow("Target Repository:", repo_layout)

        self.commit_message = QTextEdit()
        self.commit_message.setFixedHeight(80)
        form_layout.addRow("Commit Message:", self.commit_message)
        layout.addLayout(form_layout)

        layout.addWidget(QLabel("Log:"))
        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        self.log_output.setFont(QFont("Consolas", 9))
        self.log_output.setStyleSheet(
            "background-color: #1E1E1E; color: #D4D4D4;")
        layout.addWidget(self.log_output, 1)

        self.button_box = QDialogButtonBox()
        self.publish_button = self.button_box.addButton(
            "Publish Selected", QDialogButtonBox.ButtonRole.AcceptRole)
        self.auto_publish_button = self.button_box.addButton(
            "Publish Multiple...", QDialogButtonBox.ButtonRole.ActionRole)
        self.close_button = self.button_box.addButton(
            "Close", QDialogButtonBox.ButtonRole.RejectRole)
        layout.addWidget(self.button_box)

    def _connect_ui_signals(self):
        self.publish_button.clicked.connect(self._start_single_publish_flow)
        self.auto_publish_button.clicked.connect(self._start_auto_publish_flow)
        self.close_button.clicked.connect(self.reject)
        self.manage_repos_button.clicked.connect(self._open_preferences)
        self.plugin_selector.currentIndexChanged.connect(
            self._on_plugin_selected)

    def _open_preferences(self):
        self.api.get_main_window()._action_open_preferences()

    def _set_ui_locked(self, locked: bool):
        self.publish_button.setEnabled(not locked)
        self.auto_publish_button.setEnabled(not locked)
        self.plugin_selector.setEnabled(not locked)
        self.repo_combo.setEnabled(not locked)
        self.commit_message.setEnabled(not locked)
        self.manage_repos_button.setEnabled(not locked)
        self.close_button.setText("Cancel" if locked else "Close")

    def _add_log(self, message, is_error=False, is_warning=False):
        color = ("#FF5555" if is_error else
                 "#FFC66D" if is_warning else "#A9B7C6")
        self.log_output.append(
            f"<span style='color: {color};'>{message}</span>")
        self.api.log_info(f"[Plugin Publisher] {message}")

    def showEvent(self, event):
        super().showEvent(event)
        self._populate_plugins()
        self._populate_repos()
        can_publish = bool(self.repo_combo.count() and
                           self.plugin_selector.count())
        self.publish_button.setEnabled(can_publish)
        self.auto_publish_button.setEnabled(can_publish)
        tooltip = ""
        if not can_publish:
            tooltip = "Configure a distribution repo and select a plugin."
        self.publish_button.setToolTip(tooltip)
        self.auto_publish_button.setToolTip(tooltip)
        self.log_output.clear()

    def _populate_plugins(self):
        self.plugin_selector.clear()
        for plugin in self._get_publishable_plugins():
            display = (f"{plugin.get('name', 'Unknown')} "
                       f"(v{plugin.get('version', '0.0.0')})")
            self.plugin_selector.addItem(display, plugin)
        self._on_plugin_selected()

    def _get_publishable_plugins(self):
        """Gets a list of publishable plugin metadata from the plugin manager."""
        return self.plugin_manager.get_installed_plugins()

    def _populate_repos(self):
        self.repo_combo.clear()
        all_repos = self.settings.get("source_control_repos", [])
        primary_repo_id = self.settings.get("active_update_repo_id")
        primary_idx = -1
        for i, repo_config in enumerate(all_repos):
            repo_path = f"{repo_config.get('owner')}/{repo_config.get('repo')}"
            self.repo_combo.addItem(repo_path, repo_config)
            if repo_config.get('id') == primary_repo_id:
                primary_idx = i
        if primary_idx != -1:
            self.repo_combo.setCurrentIndex(primary_idx)

    def _on_plugin_selected(self, index=0):
        plugin_data = self.plugin_selector.currentData()
        if not plugin_data:
            self.commit_message.clear()
            return

        name = plugin_data.get('name', 'Unknown Plugin')
        version = plugin_data.get('version', '0.0.0')
        commit_msg = f"feat(plugin): Publish {name} v{version}"
        self.commit_message.setText(commit_msg)

    def _cleanup(self, success=True):
        self._set_ui_locked(False)
        self.git_manager.git_success.disconnect(self._on_git_step_success)
        self.git_manager.git_error.disconnect(self._on_publish_failed)
        if self._temp_dir and os.path.exists(self._temp_dir):
            shutil.rmtree(self._temp_dir, ignore_errors=True)
            self._add_log("Cleaned up temporary directory.")
        self._temp_dir = None
        self.cloned_repo_path = None
        self._current_step = None
        self.publish_queue = []

    def _on_publish_failed(self, error_message):
        self._add_log(f"FAILED on step '{self._current_step}': {error_message}",
                      is_error=True)
        self._cleanup(success=False)

    def _start_single_publish_flow(self):
        plugin_data = self.plugin_selector.currentData()
        if not plugin_data:
            QMessageBox.warning(self, "No Plugin Selected",
                                "Please select a plugin.")
            return

        publish_item = {
            "original_data": plugin_data,
            "run_data": copy.deepcopy(plugin_data)
        }
        self.auto_increment_choice = False
        self._start_publish_flow([publish_item])

    def _start_auto_publish_flow(self):
        all_plugins = self._get_publishable_plugins()
        if not all_plugins:
            QMessageBox.information(self, "No Plugins",
                                    "No publishable plugins found.")
            return

        dialog = MultiPublishSelectionDialog(all_plugins, self)
        if not dialog.exec():
            return

        plugins_to_publish = dialog.get_selected_plugins()
        if not plugins_to_publish:
            QMessageBox.information(self, "No Selection",
                                    "No plugins were selected.")
            return

        reply = QMessageBox.question(
            self, "Auto-increment Versions?",
            "Do you want to automatically increment the patch version for "
            "plugins that are not newer than the repository version?",
            (QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No |
             QMessageBox.StandardButton.Cancel),
            QMessageBox.StandardButton.Yes)

        if reply == QMessageBox.StandardButton.Cancel:
            return

        self.auto_increment_choice = (reply == QMessageBox.StandardButton.Yes)
        publish_list = [{"original_data": p, "run_data": copy.deepcopy(p)}
                        for p in plugins_to_publish]
        self._start_publish_flow(publish_list)

    def _start_publish_flow(self, publish_list):
        repo_data = self.repo_combo.currentData()
        if not repo_data:
            QMessageBox.warning(self, "Missing Repository",
                                "Please select a distribution repository.")
            return

        commit_text = self.commit_message.toPlainText().strip()
        if len(publish_list) == 1 and not commit_text:
            QMessageBox.warning(self, "Missing Commit Message",
                                "Please provide a commit message.")
            return

        self.publish_queue = publish_list
        owner = repo_data.get('owner')
        repo = repo_data.get('repo')
        self.distro_repo_path = f"{owner}/{repo}"

        self._set_ui_locked(True)
        self.log_output.clear()
        self._add_log("Starting plugin publication process...")
        self._temp_dir = tempfile.mkdtemp(prefix="puffin-plugin-publish-")
        self.git_manager.git_success.connect(self._on_git_step_success)
        self.git_manager.git_error.connect(self._on_publish_failed)
        self._current_step = "CLONE"
        self._add_log(f"Cloning '{self.distro_repo_path}'...")
        repo_url = f"https://github.com/{self.distro_repo_path}.git"
        self.git_manager.clone_repo(repo_url, self._temp_dir)

    def _on_git_step_success(self, message: str, data: dict):
        if self._current_step == "CLONE":
            self.cloned_repo_path = data.get("path")
            self._add_log("Successfully cloned repository.")
            index_json_path = os.path.join(self.cloned_repo_path, "index.json")

            if not os.path.exists(index_json_path):
                self._current_step = "INITIALIZE_COMMIT"
                self._add_log("Empty repo detected. Initializing structure...")
                self._initialize_distro_repo()
                commit_msg = "ci: Initialize plugin distribution repository"
                self.git_manager.commit_files(self.cloned_repo_path, commit_msg)
            else:
                self._process_publish_queue()

        elif self._current_step == "INITIALIZE_COMMIT":
            self._add_log("Initial commit successful.")
            self._process_publish_queue()

        elif self._current_step == "PUBLISH_COMMIT":
            self._add_log(f"Commit successful. {message}")
            self._current_step = "PUSH"
            self._add_log(f"Pushing changes to '{self.distro_repo_path}'...")
            self.git_manager.push(self.cloned_repo_path)

        elif self._current_step == "PUSH":
            self._add_log("Push successful!")
            for item in self.publish_queue:
                original_version = item["original_data"].get("version")
                new_version = item["run_data"].get("version")
                if new_version != original_version:
                    self._update_local_plugin_json(item["original_data"],
                                                   new_version)

            self._add_log("\n--- PUBLICATION COMPLETE ---")
            self._cleanup(success=True)
            self._populate_plugins()

    def _process_publish_queue(self):
        self._current_step = "PROCESS_PLUGINS"
        is_batch = len(self.publish_queue) > 1
        index_path = os.path.join(self.cloned_repo_path, 'index.json')
        index_data = []
        try:
            if os.path.exists(index_path):
                with open(index_path, 'r', encoding='utf-8') as f:
                    index_data = json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            self._on_publish_failed(f"Failed to load or parse index.json: {e}")
            return

        processed_items = []
        for item in self.publish_queue:
            plugin_data = item["run_data"]
            plugin_name = plugin_data.get('name', 'Unknown')
            self._add_log(f"--- Processing {plugin_name} ---")
            try:
                should_publish, final_version = self._check_version(
                    item, index_data, batch_mode=is_batch)

                if should_publish:
                    item['run_data']['version'] = final_version
                    self._package_plugin(item['run_data'])
                    self._update_index_data(item['run_data'], index_data)
                    processed_items.append(item)
                else:
                    self._add_log(f"Skipping '{plugin_name}'.", is_warning=True)
            except FileNotFoundError as e:
                self._add_log(f"ERROR for '{plugin_name}': {e}. Skipping.",
                              is_error=True)
            except Exception as e:
                msg = f"UNEXPECTED ERROR for '{plugin_name}': {e}. Skipping."
                self._add_log(msg, is_error=True)

        self.publish_queue = processed_items
        if not self.publish_queue:
            msg = "No plugins processed for publication. Nothing to commit."
            self._add_log(msg, is_warning=True)
            self._cleanup()
            return

        try:
            with open(index_path, 'w', encoding='utf-8') as f:
                json.dump(index_data, f, indent=4)
        except IOError as e:
            self._on_publish_failed(f"Failed to write updated index.json: {e}")
            return

        commit_msg = self.commit_message.toPlainText()
        if is_batch:
            count = len(self.publish_queue)
            plural = 's' if count > 1 else ''
            commit_msg = f"feat(plugins): Update {count} plugin{plural}"
        elif len(self.publish_queue) == 1:
            p_data = self.publish_queue[0]['run_data']
            p_name = p_data.get('name', 'Unknown')
            p_ver = p_data.get('version', '0.0.0')
            commit_msg = f"feat(plugin): Publish {p_name} v{p_ver}"
        self.commit_message.setText(commit_msg)

        count = len(self.publish_queue)
        self._add_log(f"Committing updates for {count} plugin(s)...")
        self._current_step = "PUBLISH_COMMIT"
        self.git_manager.commit_files(self.cloned_repo_path, commit_msg)

    def _check_version(self, publish_item, index_data, batch_mode=False):
        local_data = publish_item['original_data']
        local_version = local_data.get('version', '0.0.0')
        plugin_id = local_data.get('id')
        plugin_name = local_data.get('name', 'Unknown')

        old_entry = next((p for p in index_data if p.get('id') == plugin_id), None)

        if not old_entry:
            self._add_log(f"New plugin '{plugin_id}'.")
            if not batch_mode:
                dialog = BumpVersionDialog(local_version, self)
                if dialog.exec():
                    self._add_log(f"User selected initial version "
                                  f"{dialog.new_version}.")
                    return True, dialog.new_version
                return False, None
            return True, local_version

        remote_version = old_entry.get('version')
        if not remote_version:
            return True, local_version

        if local_version > remote_version:
            self._add_log(f"Newer version found: {remote_version} -> "
                          f"{local_version}.")
            return True, local_version

        if batch_mode:
            if self.auto_increment_choice:
                new_version = _bump_version(remote_version, 'patch')
                self._add_log(f"Auto-incrementing version: {remote_version} -> "
                              f"{new_version}.")
                return True, new_version
            else:
                return False, None

        dialog = VersionConflictDialog(
            plugin_name, local_version, remote_version, self)
        if dialog.exec():
            action, version = dialog.result
            if action:
                self._add_log(f"User chose to '{action}' with version {version}.")
                return True, version

        return False, None

    def _package_plugin(self, plugin_data):
        plugin_id = plugin_data.get('id')
        plugin_source_path = plugin_data.get('path')

        if not plugin_source_path or not os.path.isdir(plugin_source_path):
            raise FileNotFoundError(
                f"Source directory for '{plugin_id}' not found in metadata")

        zips_dir = os.path.join(self.cloned_repo_path, 'zips')
        os.makedirs(zips_dir, exist_ok=True)
        final_zip_path = os.path.join(zips_dir, f"{plugin_id}.zip")

        self._add_log(f"Packaging '{plugin_id}' to zip from "
                      f"'{plugin_source_path}'...")
        shutil.make_archive(os.path.splitext(final_zip_path)[0], 'zip',
                            plugin_source_path)

    def _update_index_data(self, plugin_data, index_data):
        plugin_id = plugin_data.get('id')
        rel_zip_path = os.path.join('zips', f"{plugin_id}.zip").replace("\\", "/")
        download_url = (f"https://raw.githubusercontent.com/"
                        f"{self.distro_repo_path}/main/{rel_zip_path}")

        new_entry = {k: plugin_data.get(k) for k in
                     ('id', 'name', 'author', 'version', 'description')}
        new_entry['download_url'] = download_url

        index_data[:] = [entry for entry in index_data
                         if entry.get('id') != plugin_id]
        index_data.append(new_entry)
        self._add_log(f"Updated index for '{plugin_id}'.")

    def _update_local_plugin_json(self, plugin_data, new_version):
        plugin_id = plugin_data.get('id')
        self._add_log(f"Updating local plugin.json for '{plugin_id}' to "
                      f"v{new_version}")
        try:
            plugin_source_path = plugin_data.get('path')
            if not plugin_source_path:
                raise FileNotFoundError(
                    f"Source path for {plugin_id} not found in metadata.")

            json_file_path = os.path.join(plugin_source_path, 'plugin.json')

            with open(json_file_path, 'r+', encoding='utf-8') as f:
                plugin_json = json.load(f)
                plugin_json['version'] = new_version
                f.seek(0)
                json.dump(plugin_json, f, indent=4)
                f.truncate()
            self._add_log(f"Successfully updated local version for {plugin_id}.")
        except Exception as e:
            self._add_log(f"Could not update local plugin.json for "
                          f"{plugin_id}: {e}", is_error=True)

    def _initialize_distro_repo(self):
        try:
            with open(os.path.join(self.cloned_repo_path, 'index.json'), 'w') as f:
                json.dump([], f, indent=4)
            with open(os.path.join(self.cloned_repo_path, 'README.md'), 'w') as f:
                f.write(README_CONTENT)
            with open(os.path.join(self.cloned_repo_path, '.gitignore'), 'w') as f:
                f.write(GITIGNORE_CONTENT)
            zips_dir = os.path.join(self.cloned_repo_path, 'zips')
            os.makedirs(zips_dir, exist_ok=True)
            with open(os.path.join(zips_dir, '.gitkeep'), 'w') as f:
                pass
        except Exception as e:
            self._on_publish_failed(f"Error initializing distro repo files: {e}")
            raise
```

### File: `/plugins/plugin_publisher/plugin_main.py`
```py
# PuffinPyEditor/plugins/plugin_publisher/plugin_main.py
from app_core.puffin_api import PuffinPluginAPI
from .publish_dialog import PublishDialog
from utils.logger import log

class PluginPublisherPlugin:
    def __init__(self, puffin_api: PuffinPluginAPI):
        self.api = puffin_api
        self.publish_dialog = None
        self.publish_action = self.api.add_menu_action(
            menu_name="tools",
            text="Publish Plugin...",
            callback=self.show_publish_dialog,
            icon_name="fa5s.cloud-upload-alt"
        )
        self.update_action_state()
        github_manager = self.api.get_manager("github")
        if github_manager:
            # Connect to a method that can be disconnected reliably
            github_manager.auth_successful.connect(self._on_auth_state_changed)
            github_manager.auth_failed.connect(self._on_auth_state_changed)

    def shutdown(self):
        # Disconnect signals to prevent calls to a deleted object
        github_manager = self.api.get_manager("github")
        if github_manager:
            try:
                github_manager.auth_successful.disconnect(self._on_auth_state_changed)
                github_manager.auth_failed.disconnect(self._on_auth_state_changed)
            except (TypeError, RuntimeError):
                # This can happen if the connection was already broken.
                # It's safe to ignore.
                pass

        if self.publish_action:
            # Use a safer way to get the menu
            if hasattr(self.api.get_main_window(), 'tools_menu'):
                 self.api.get_main_window().tools_menu.removeAction(self.publish_action)
            self.publish_action.deleteLater()
            # Nullify the reference to prevent further access
            self.publish_action = None
        log.info("Plugin Publisher shutdown complete.")

    def _on_auth_state_changed(self, *args, **kwargs):
        """
        Slot to handle authentication state changes. This will call the UI
        update method.
        """
        self.update_action_state()

    def show_publish_dialog(self):
        github_manager = self.api.get_manager("github")
        if not (github_manager and github_manager.get_authenticated_user()):
            self.api.show_message("warning", "Login Required", "You must be logged into GitHub to publish a plugin.")
            return

        if self.publish_dialog is None or not self.publish_dialog.isVisible():
            self.publish_dialog = PublishDialog(self.api, self.api.get_main_window())
        self.publish_dialog.show()
        self.publish_dialog.raise_()
        self.publish_dialog.activateWindow()

    def update_action_state(self):
        # Add a guard to ensure the action exists before modification.
        if not self.publish_action:
            return
            
        github_manager = self.api.get_manager("github")
        is_logged_in = bool(github_manager and github_manager.get_authenticated_user())
        self.publish_action.setEnabled(is_logged_in)
        self.publish_action.setToolTip("Upload a plugin." if is_logged_in else "Log in to GitHub to use.")

def initialize(puffin_api: PuffinPluginAPI):
    return PluginPublisherPlugin(puffin_api)
```

### File: `/plugins/plugin_publisher/plugin.json`
```json
{
    "id": "plugin_publisher",
    "name": "Plugin Publisher",
    "author": "AI Assistant",
    "version": "1.0.2",
    "description": "Provides a tool to package and publish installed plugins to a specified GitHub distribution repository. Manages versioning and updates the repository's index.json.",
    "entry_point": "plugin_main.py"
}
```

### File: `/plugins/plugin_publisher/__init__.py`
```py

```

### File: `/plugins/markdown_viewer/plugin_main.py`
```py
# /plugins/markdown_viewer/plugin_main.py
import os
from .markdown_editor_widget import MarkdownEditorWidget
from utils.logger import log
from app_core.puffin_api import PuffinPluginAPI


class MarkdownPlugin:
    """
    Manages the lifecycle and functionality of the Markdown Editor plugin.
    Provides a dual-pane editor with live preview for Markdown files.
    """

    def __init__(self, puffin_api: PuffinPluginAPI):
        self.api = puffin_api
        self.main_window = self.api.get_main_window()
        self.instances = {}  # Track open editor instances

        # Register our custom editor widget as the handler for .md files
        self.api.register_file_opener('.md', self.open_markdown_editor)
        log.info("Markdown Editor: Registered dual-pane handler for .md files.")

    def open_markdown_editor(self, filepath: str):
        """
        Callback to open a .md file in our custom MarkdownEditorWidget.
        It creates a new tab with the dual-pane editor or focuses an existing one.
        """
        if filepath in self.instances:
            widget = self.instances[filepath]
            if widget:
                index = self.main_window.tab_widget.indexOf(widget)
                if index != -1:
                    self.main_window.tab_widget.setCurrentIndex(index)
                    return

        if self.main_window.tab_widget.count() == 1:
            if current_widget := self.main_window.tab_widget.widget(0):
                if current_widget.objectName() == "PlaceholderLabel":
                    self.main_window.tab_widget.removeTab(0)

        log.info(f"Markdown Editor: Creating new dual-pane view for '{filepath}'.")

        # THE FIX: We pass the theme_manager to the widget's constructor.
        editor = MarkdownEditorWidget(
            puffin_api=self.api,
            theme_manager=self.api.get_manager("theme"),
            parent=self.main_window
        )
        editor.load_file(filepath)
        editor.content_changed.connect(lambda: self.main_window._on_content_changed(editor))

        tab_name = os.path.basename(filepath)
        index = self.main_window.tab_widget.addTab(editor, tab_name)
        self.main_window.tab_widget.setTabToolTip(index, filepath)
        self.main_window.tab_widget.setCurrentIndex(index)
        self.main_window.tab_widget.setTabsClosable(True)

        self.instances[filepath] = editor
        editor.destroyed.connect(lambda: self.instances.pop(filepath, None))


def initialize(puffin_api: PuffinPluginAPI):
    """Entry point for PuffinPyEditor to load the plugin."""
    try:
        plugin_instance = MarkdownPlugin(puffin_api)
        log.info("Markdown Editor Plugin (dual-pane) initialized successfully.")
        return plugin_instance
    except Exception as e:
        log.error(f"Failed to initialize Markdown Editor Plugin: {e}", exc_info=True)
        return None
```

### File: `/plugins/markdown_viewer/plugin.json`
```json
{
    "id": "markdown_viewer",
    "name": "Markdown Viewer",
    "author": "AI Assistant",
    "version": "1.0.2",
    "description": "Adds support for viewing rendered Markdown (.md) files in a separate tab. It intercepts file open calls to provide a rich text view instead of a plain text editor for .md files.",
    "entry_point": "plugin_main.py"
}
```

### File: `/plugins/markdown_viewer/markdown_syntax_highlighter.py`
```py
# /plugins/markdown_viewer/markdown_syntax_highlighter.py
from typing import TYPE_CHECKING
from PyQt6.QtGui import QSyntaxHighlighter, QTextCharFormat, QColor, QFont
from PyQt6.QtCore import QRegularExpression, Qt

if TYPE_CHECKING:
    from app_core.theme_manager import ThemeManager

class MarkdownSyntaxHighlighter(QSyntaxHighlighter):
    def __init__(self, parent_document, theme_manager: "ThemeManager"):
        super().__init__(parent_document)
        self.theme_manager = theme_manager
        self.formats = {}
        self.rules = []
        # Fallback to a default color if something goes wrong
        default_fg_color = self.theme_manager.current_theme_data.get("colors", {}).get("editor.foreground", "#ffffff")
        self.default_fg = QColor(default_fg_color)
        self.initialize_formats_and_rules()

    def _get_high_contrast_color(self, fg_color: QColor, bg_color: QColor) -> QColor:
        CONTRAST_THRESHOLD = 80
        fg_lightness = fg_color.lightness()
        bg_lightness = bg_color.lightness()

        if abs(fg_lightness - bg_lightness) < CONTRAST_THRESHOLD:
            return QColor(Qt.GlobalColor.white) if bg_lightness < 128 else QColor(Qt.GlobalColor.black)
        return fg_color

    def initialize_formats_and_rules(self):
        colors = self.theme_manager.current_theme_data.get("colors", {})
        editor_bg = QColor(colors.get('editor.background', '#2b2b2b'))
        accent = QColor(colors.get('accent', '#88c0d0'))
        comment_color = QColor(colors.get('syntax.comment', '#808080'))

        self.formats['marker'] = QTextCharFormat()
        self.formats['marker'].setForeground(editor_bg.lighter(150))
        self.formats['marker'].setFontWeight(QFont.Weight.Bold)
        self.formats['blockquote'] = QTextCharFormat()
        self.formats['blockquote'].setForeground(comment_color)
        self.formats['blockquote'].setFontItalic(True)
        self.formats['hr'] = QTextCharFormat()
        self.formats['hr'].setForeground(editor_bg.lighter(130))
        self.formats['hr'].setFontWeight(QFont.Weight.Bold)

        base_heading_format = QTextCharFormat()
        base_heading_format.setFontWeight(QFont.Weight.Bold)
        base_heading_format.setForeground(accent)
        for i in range(1, 7):
            self.formats[f'h{i}'] = QTextCharFormat(base_heading_format)
            self.formats[f'h{i}'].setFontPointSize(22 - (i-1)*2)

        self.formats['bold'] = QTextCharFormat()
        self.formats['bold'].setFontWeight(QFont.Weight.Bold)
        self.formats['italic'] = QTextCharFormat()
        self.formats['italic'].setFontItalic(True)
        self.formats['strikethrough'] = QTextCharFormat()
        self.formats['strikethrough'].setFontStrikeOut(True)
        
        code_block_bg_color = QColor(colors.get('editor.lineHighlightBackground', '#323232'))
        self.formats['code_block'] = QTextCharFormat()
        self.formats['code_block'].setBackground(code_block_bg_color)
        self.formats['code_block'].setFontFamily("Consolas")
        
        self.formats['inline_code'] = QTextCharFormat()
        original_inline_code_fg = QColor(colors.get('syntax.string', '#a7c080'))
        final_inline_code_fg = self._get_high_contrast_color(original_inline_code_fg, code_block_bg_color)
        self.formats['inline_code'].setBackground(code_block_bg_color)
        self.formats['inline_code'].setForeground(final_inline_code_fg)
        self.formats['inline_code'].setFontFamily("Consolas")

        self.rules = [
            (QRegularExpression(r"^(#{1,6})\s"), self._format_heading),
            (QRegularExpression(r"^>+\s?"), self._format_simple('blockquote')),
            (QRegularExpression(r"^[-_*]{3,}\s*$"), self._format_simple('hr')),
            (QRegularExpression(r"^(\s*[\*\-\+]\s)"), self._format_marker_only()),
            (QRegularExpression(r"^(\s*[0-9]+\.\s)"), self._format_marker_only()),
            (QRegularExpression(r"(\*\*)(\S.*?\S)(\*\*)"), self._format_inline('bold')),
            (QRegularExpression(r"(\*)(\S.*?\S)(\*)"), self._format_inline('italic')),
            (QRegularExpression(r"(__)(\S.*?\S)(__)"), self._format_inline('bold')),
            (QRegularExpression(r"(_)(\S.*?\S)(_)"), self._format_inline('italic')),
            (QRegularExpression(r"(~~)([^~]+)(~~)"), self._format_inline('strikethrough')),
            (QRegularExpression(r"(`)([^`]+)(`)"), self._format_inline('inline_code')),
        ]
        self.code_block_delimiter = QRegularExpression(r"^```")

    def _format_simple(self, fmt_name):
        return lambda match: self.setFormat(match.capturedStart(0), match.capturedLength(0), self.formats[fmt_name])
        
    def _format_marker_only(self):
        return lambda match: self.setFormat(match.capturedStart(1), match.capturedLength(1), self.formats['marker'])

    def _format_heading(self, match):
        level = len(match.captured(1))
        self.setFormat(match.capturedStart(1), level, self.formats['marker'])
        self.setFormat(match.capturedEnd(1), self.currentBlock().length() - match.capturedEnd(1), self.formats[f'h{level}'])
    
    def _format_inline(self, fmt_name):
        def formatter(match):
            self.setFormat(match.capturedStart(2), len(match.captured(2)), self.formats[fmt_name])
            marker_format = self.formats['inline_code'] if fmt_name == 'inline_code' else self.formats['marker']
            self.setFormat(match.capturedStart(1), len(match.captured(1)), marker_format)
            self.setFormat(match.capturedStart(3), len(match.captured(3)), marker_format)
        return formatter

    def highlightBlock(self, text: str):
        # State 0: Normal text, State 1: Inside a code block
        is_in_code_block = self.previousBlockState() == 1
        delimiter_match = self.code_block_delimiter.match(text)
        
        if is_in_code_block:
            if delimiter_match.hasMatch():
                # We are at the end of a code block, so mark this line
                # as a delimiter and switch state back to normal.
                self.setCurrentBlockState(0)
                self.setFormat(0, len(text), self.formats['marker'])
            else:
                # We are still inside a code block. Apply the block format.
                self.setCurrentBlockState(1)
                code_bg = self.formats['code_block'].background().color()
                corrected_fg = self._get_high_contrast_color(self.default_fg, code_bg)
                block_format = QTextCharFormat(self.formats['code_block'])
                block_format.setForeground(corrected_fg)
                self.setFormat(0, len(text), block_format)
        else: # Normal text block
            if delimiter_match.hasMatch():
                # This is the start of a new code block. Mark the delimiter
                # line and switch the state for the next block.
                self.setCurrentBlockState(1)
                self.setFormat(0, len(text), self.formats['marker'])
            else:
                # This is a normal text line. Reset state and apply inline rules.
                self.setCurrentBlockState(0)
                # THE FIX: Replace the incorrect `for...in` loop.
                for pattern, formatter in self.rules:
                    iterator = pattern.globalMatch(text)
                    while iterator.hasNext():
                        match = iterator.next()
                        formatter(match)

    def rehighlight(self):
        default_fg_color = self.theme_manager.current_theme_data.get("colors", {}).get("editor.foreground", "#ffffff")
        self.default_fg = QColor(default_fg_color)
        self.initialize_formats_and_rules()
        super().rehighlight()
```

### File: `/plugins/markdown_viewer/markdown_editor_widget.py`
```py
# /plugins/markdown_viewer/markdown_editor_widget.py
import qtawesome as qta
from typing import TYPE_CHECKING
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTextBrowser,
                             QSplitter, QMenu, QToolButton, QFrame, QPlainTextEdit)
from PyQt6.QtGui import (QFont, QTextCursor, QAction)
from PyQt6.QtCore import QTimer, pyqtSignal, Qt
from markdown import markdown

from app_core.puffin_api import PuffinPluginAPI
from app_core.settings_manager import settings_manager
from ui.editor_widget import HighlightManager
from .markdown_syntax_highlighter import MarkdownSyntaxHighlighter
from utils.logger import log

if TYPE_CHECKING:
    from app_core.theme_manager import ThemeManager

class MarkdownFormattingToolbar(QWidget):
    # This class seems fine, no changes needed.
    format_bold_requested = pyqtSignal()
    format_italic_requested = pyqtSignal()
    format_strikethrough_requested = pyqtSignal()
    format_inline_code_requested = pyqtSignal()
    heading_level_requested = pyqtSignal(int)
    code_block_requested = pyqtSignal()
    def __init__(self, theme_manager: "ThemeManager", parent=None):
        super().__init__(parent)
        self.theme_manager = theme_manager
        self.setWindowFlags(Qt.WindowType.ToolTip | Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.frame = QFrame(self)
        self.frame.setObjectName("FormattingToolbarFrame")
        layout = QHBoxLayout(self.frame)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(2)
        self._add_tool_button("fa5s.bold", "Bold (Ctrl+B)", self.format_bold_requested)
        self._add_tool_button("fa5s.italic", "Italic (Ctrl+I)", self.format_italic_requested)
        self._add_tool_button("fa5s.strikethrough", "Strikethrough", self.format_strikethrough_requested)
        self._add_tool_button("fa5s.code", "Inline Code", self.format_inline_code_requested)
        layout.addWidget(self._create_separator())
        self._create_heading_menu()
        layout.addWidget(self._create_separator())
        self._add_tool_button("fa5s.file-code", "Insert Code Block", self.code_block_requested)
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(self.frame)
        self.update_theme()
    def _add_tool_button(self, icon_name, tooltip, signal_to_emit):
        button = QToolButton()
        button.setIcon(qta.icon(icon_name, color='white'))
        button.setToolTip(tooltip)
        button.clicked.connect(signal_to_emit.emit)
        self.frame.layout().addWidget(button)
    def _create_separator(self):
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.VLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        return separator
    def _create_heading_menu(self):
        button = QToolButton()
        button.setIcon(qta.icon("fa5s.heading", color='white'))
        button.setToolTip("Apply Heading")
        button.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        menu = QMenu(self)
        for i in range(1, 7):
            action = QAction(f"Heading {i}", self)
            action.triggered.connect(lambda _, level=i: self.heading_level_requested.emit(level))
            menu.addAction(action)
        button.setMenu(menu)
        self.frame.layout().addWidget(button)
    def update_theme(self):
        colors = self.theme_manager.current_theme_data.get('colors', {})
        bg, border, accent = colors.get('menu.background', '#3a4145'), colors.get('input.border', '#555555'), colors.get('accent', '#88c0d0')
        self.setStyleSheet(f"""#FormattingToolbarFrame {{ background-color: {bg}; border: 1px solid {border}; border-radius: 6px; }} QToolButton {{ background: transparent; border: none; padding: 5px; border-radius: 4px; }} QToolButton:hover {{ background-color: {accent}; }} QFrame[frameShape="5"] {{ color: {border}; }}""")
    def show_at(self, global_pos):
        self.move(global_pos)
        self.show()
        self.activateWindow()
    def focusOutEvent(self, event):
        self.hide()
        super().focusOutEvent(event)


class MarkdownEditorWidget(QWidget):
    content_changed = pyqtSignal()
    def __init__(self, puffin_api: PuffinPluginAPI, theme_manager: "ThemeManager", parent=None):
        super().__init__(parent)
        from ui.editor_widget import EditorWidget
        self.EditorWidgetClass = EditorWidget
        self.api = puffin_api
        self.theme_manager = theme_manager
        self.highlight_manager = HighlightManager()
        self.filepath = None
        self.original_hash = 0
        self.is_syncing_scroll = False
        self.formatting_toolbar = MarkdownFormattingToolbar(self.theme_manager, self)
        self._setup_ui()
        self._connect_signals()
        self.update_theme()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        self.editor_widget = self.EditorWidgetClass(self.api, self.api.get_manager("completion"), self.highlight_manager, self.theme_manager, self)
        self.editor_widget.text_area.setLineWrapMode(QPlainTextEdit.LineWrapMode.WidgetWidth)
        # THE FIX: Pass the theme_manager instance to the highlighter's constructor.
        self.highlighter = MarkdownSyntaxHighlighter(self.editor_widget.text_area.document(), self.theme_manager)
        self.viewer = QTextBrowser()
        self.viewer.setOpenExternalLinks(True)
        splitter = QSplitter(self)
        splitter.addWidget(self.editor_widget)
        splitter.addWidget(self.viewer)
        splitter.setSizes([self.width() // 2, self.width() // 2])
        layout.addWidget(splitter)

    def _connect_signals(self):
        self.update_timer = QTimer(self)
        self.update_timer.setSingleShot(True)
        self.update_timer.setInterval(250)
        self.update_timer.timeout.connect(self._render_preview)
        text_area = self.editor_widget.text_area
        text_area.textChanged.connect(self.update_timer.start)
        text_area.textChanged.connect(self.content_changed.emit)
        self.formatting_toolbar.format_bold_requested.connect(lambda: self._wrap_selection("**"))
        self.formatting_toolbar.format_italic_requested.connect(lambda: self._wrap_selection("*"))
        self.formatting_toolbar.format_strikethrough_requested.connect(lambda: self._wrap_selection("~~"))
        self.formatting_toolbar.format_inline_code_requested.connect(lambda: self._wrap_selection("`"))
        self.formatting_toolbar.heading_level_requested.connect(self._format_heading)
        self.formatting_toolbar.code_block_requested.connect(self._insert_code_block)
        editor_scroll = text_area.verticalScrollBar()
        viewer_scroll = self.viewer.verticalScrollBar()
        editor_scroll.valueChanged.connect(self._sync_scroll_from_editor)
        viewer_scroll.valueChanged.connect(self._sync_scroll_from_viewer)

    def contextMenuEvent(self, event):
        # We need to find the correct text_area widget within the editor_widget child
        if self.editor_widget.text_area.rect().contains(event.pos()):
            self.formatting_toolbar.show_at(event.globalPos())
        super().contextMenuEvent(event)
    def _wrap_selection(self, prefix, suffix=None):
        suffix = suffix or prefix
        cursor = self.editor_widget.text_area.textCursor()
        if not cursor.hasSelection():
            cursor.insertText(f"{prefix}text{suffix}")
            cursor.movePosition(QTextCursor.MoveOperation.Left, n=len(suffix))
            cursor.movePosition(QTextCursor.MoveOperation.Left, QTextCursor.MoveMode.KeepAnchor, n=4)
        else:
            selected_text = cursor.selectedText()
            cursor.insertText(f"{prefix}{selected_text}{suffix}")
        self.editor_widget.text_area.setTextCursor(cursor)
    def _format_heading(self, level):
        cursor = self.editor_widget.text_area.textCursor()
        cursor.beginEditBlock()
        cursor.movePosition(QTextCursor.MoveOperation.StartOfBlock)
        cursor.insertText(f'{"#" * level} ')
        cursor.endEditBlock()
    def _insert_code_block(self):
        cursor = self.editor_widget.text_area.textCursor()
        cursor.beginEditBlock()
        cursor.insertText("\n```python\n\n```\n")
        cursor.movePosition(QTextCursor.MoveOperation.Up, n=2)
        cursor.endEditBlock()
        self.editor_widget.text_area.setTextCursor(cursor)
    def _sync_scroll_factory(self, source_bar, target_bar):
        def sync_scroll(value):
            if self.is_syncing_scroll: return
            self.is_syncing_scroll = True
            source_max = source_bar.maximum() or 1
            ratio = value / source_max
            target_bar.setValue(int(target_bar.maximum() * ratio))
            self.is_syncing_scroll = False
        return sync_scroll
    @property
    def _sync_scroll_from_editor(self):
        return self._sync_scroll_factory(self.editor_widget.text_area.verticalScrollBar(), self.viewer.verticalScrollBar())
    @property
    def _sync_scroll_from_viewer(self):
        return self._sync_scroll_factory(self.viewer.verticalScrollBar(), self.editor_widget.text_area.verticalScrollBar())
    def load_file(self, filepath: str):
        self.filepath = filepath
        self.editor_widget.set_filepath(filepath)
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            self.editor_widget.set_text(content)
            self.original_hash = hash(content)
            log.info(f"Markdown Editor: Successfully loaded '{filepath}'.")
        except Exception as e:
            log.error(f"Failed to load markdown file {filepath}: {e}")
            self.editor_widget.set_text(f"# Error\n\nCould not load file: {e}")

    def get_content(self) -> str:
        return self.editor_widget.get_text()

    def _render_preview(self):
        viewer_scroll = self.viewer.verticalScrollBar()
        scroll_max = viewer_scroll.maximum() or 1
        old_pos_ratio = viewer_scroll.value() / scroll_max
        md_text = self.get_content()
        html = markdown(md_text, extensions=['fenced_code', 'tables', 'extra', 'sane_lists'])
        self.viewer.setHtml(html)
        QTimer.singleShot(0, lambda: viewer_scroll.setValue(int(viewer_scroll.maximum() * old_pos_ratio)))
    
    def update_theme(self):
        colors = self.theme_manager.current_theme_data.get('colors', {})
        font_family = settings_manager.get("font_family", "Arial")
        code_font_family = settings_manager.get("font_family", "Consolas")
        font_size = settings_manager.get("font_size", 11)
        bg = colors.get('editor.background', '#2b2b2b')
        string = colors.get('syntax.string', '#6A8759')
        accent = colors.get('accent', '#88c0d0')
        line_highlight_bg = colors.get('editor.lineHighlightBackground', '#323232')
        border = colors.get('input.border', '#555')
        comment = colors.get('syntax.comment', '#808080')
        
        style_sheet = f""" h1, h2, h3, h4, h5, h6 {{ color: {accent}; border-bottom: 1px solid {line_highlight_bg}; padding-bottom: 4px; margin-top: 15px; }} a {{ color: {string}; text-decoration: none; }} a:hover {{ text-decoration: underline; }} p, li {{ font-size: {font_size}pt; }} pre {{ background-color: {line_highlight_bg}; border: 1px solid {border}; border-radius: 4px; padding: 10px; font-family: "{code_font_family}"; }} code {{ background-color: {line_highlight_bg}; font-family: "{code_font_family}"; border-radius: 3px; padding: 2px 4px; }} blockquote {{ color: {comment}; border-left: 3px solid {accent}; padding-left: 15px; margin-left: 5px; font-style: italic; }} table {{ border-collapse: collapse; margin: 1em 0; }} th, td {{ border: 1px solid {border}; padding: 8px; }} th {{ background-color: {line_highlight_bg}; font-weight: bold; }} """
        doc = self.viewer.document()
        doc.setDefaultStyleSheet(style_sheet)
        doc.setDefaultFont(QFont(font_family, font_size))
        self.viewer.setStyleSheet(f"background-color: {bg}; border: none; padding: 10px;")
        
        # Ensure editor widget and highlighter also get updated
        self.editor_widget.update_theme()
        if self.highlighter:
            self.highlighter.rehighlight()

        self.formatting_toolbar.update_theme()
        self._render_preview()
```

### File: `/plugins/markdown_viewer/__init__.py`
```py

```

### File: `/plugins/github_tools/select_repo_dialog.py`
```py
# PuffinPyEditor/plugins/github_tools/select_repo_dialog.py
from typing import Optional, List, Dict, Any
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QListWidget,
                             QListWidgetItem, QDialogButtonBox, QMessageBox,
                             QLineEdit, QHBoxLayout, QLabel, QWidget)
from PyQt6.QtCore import Qt
from app_core.github_manager import GitHubManager


class SelectRepoDialog(QDialog):
    """
    A reusable dialog for selecting a GitHub repository from a user's account.
    """
    def __init__(self, github_manager: GitHubManager,
                 parent: Optional[QWidget] = None,
                 title: str = "Select Target Repository"):
        super().__init__(parent)
        self.github_manager = github_manager
        self.selected_repo_data: Optional[Dict[str, Any]] = None
        self.all_repos: List[Dict[str, Any]] = []

        self.setWindowTitle(title)
        self.setMinimumSize(500, 400)
        self.main_layout = QVBoxLayout(self)

        self._setup_ui()
        self._connect_signals()
        self.github_manager.list_repos()

    def _setup_ui(self):
        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("Filter:"))
        self.filter_edit = QLineEdit()
        self.filter_edit.setPlaceholderText("Type to filter repositories...")
        search_layout.addWidget(self.filter_edit)
        self.main_layout.addLayout(search_layout)

        self.repo_list_widget = QListWidget()
        self.repo_list_widget.itemDoubleClicked.connect(self.accept)
        self.main_layout.addWidget(self.repo_list_widget)

        self.button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok |
            QDialogButtonBox.StandardButton.Cancel
        )
        self.main_layout.addWidget(self.button_box)
        ok_button = self.button_box.button(QDialogButtonBox.StandardButton.Ok)
        ok_button.setEnabled(False)

    def _connect_signals(self):
        self.github_manager.repos_ready.connect(self._handle_repos_loaded)
        self.github_manager.operation_failed.connect(self._on_load_failed)
        self.filter_edit.textChanged.connect(self._filter_repo_list)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)

    def closeEvent(self, event):
        try:
            self.github_manager.repos_ready.disconnect(
                self._handle_repos_loaded)
            self.github_manager.operation_failed.disconnect(
                self._on_load_failed)
        except TypeError:
            pass  # Suppress errors if signals are not connected
        super().closeEvent(event)

    def _handle_repos_loaded(self, repos: List[Dict[str, Any]]):
        self.all_repos = sorted(repos, key=lambda r: r['full_name'].lower())
        self._populate_repo_list()
        if self.repo_list_widget.count() > 0:
            ok_button = self.button_box.button(
                QDialogButtonBox.StandardButton.Ok)
            ok_button.setEnabled(True)
            self.repo_list_widget.setCurrentRow(0)

    def _populate_repo_list(self):
        self.repo_list_widget.clear()
        filter_text = self.filter_edit.text().lower()
        for repo in self.all_repos:
            if filter_text in repo['full_name'].lower():
                item = QListWidgetItem(repo['full_name'])
                item.setToolTip(repo.get('description', 'No description'))
                item.setData(Qt.ItemDataRole.UserRole, repo)
                self.repo_list_widget.addItem(item)

    def _filter_repo_list(self):
        self._populate_repo_list()

    def _on_load_failed(self, error_message: str):
        QMessageBox.critical(self, "Failed to Load Repositories",
                             error_message)
        self.reject()

    def accept(self):
        current_item = self.repo_list_widget.currentItem()
        if not current_item:
            QMessageBox.warning(self, "No Selection",
                                "Please select a repository.")
            return
        self.selected_repo_data = current_item.data(Qt.ItemDataRole.UserRole)
        super().accept()
```

### File: `/plugins/github_tools/plugin_main.py`
```py
# PuffinPyEditor/plugins/github_tools/plugin_main.py
import os
import shutil
import tempfile
import git
import configparser
from git import Actor, Repo
from PyQt6.QtWidgets import (QInputDialog, QMessageBox, QTextEdit, QDialog,
                             QVBoxLayout, QLabel, QProgressBar, QPushButton,
                             QDialogButtonBox)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from app_core.puffin_api import PuffinPluginAPI
from .new_release_dialog import NewReleaseDialog
from .select_repo_dialog import SelectRepoDialog
from .github_dialog import GitHubDialog
from utils import versioning
import sys


class UploadProgressDialog(QDialog):
    """A dialog to show the real-time progress of an asset upload."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Release Progress")
        self.setMinimumWidth(600)
        self.setModal(True)
        self.setWindowFlag(Qt.WindowType.WindowCloseButtonHint, False)
        layout = QVBoxLayout(self)
        self.step_label = QLabel("Starting release...")
        font = self.step_label.font()
        font.setBold(True)
        self.step_label.setFont(font)
        layout.addWidget(self.step_label)
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)
        self.progress_bar.setTextVisible(False)
        layout.addWidget(self.progress_bar)
        self.log_console = QTextEdit()
        self.log_console.setReadOnly(True)
        self.log_console.setFont(QFont("Consolas", 9))
        self.log_console.setStyleSheet("background-color: #1e1e1e; color: #d4d4d4;")
        layout.addWidget(self.log_console)
        self.button_box = QDialogButtonBox()
        self.close_button = self.button_box.addButton("Close", QDialogButtonBox.ButtonRole.RejectRole)
        self.close_button.clicked.connect(self.reject)
        self.close_button.hide()
        layout.addWidget(self.button_box)

    def set_step(self, step_name: str):
        self.step_label.setText(f"Step: {step_name}")

    def add_log(self, message: str, is_error: bool = False, is_warning: bool = False):
        if is_error:
            color = "#FF5555"
        elif is_warning:
            color = "#FFC66D"  # A nice amber/yellow color for warnings
        else:
            color = "#D4D4D4"

        self.log_console.append(f"<span style='color:{color};'>{message}</span>")
        self.log_console.verticalScrollBar().setValue(self.log_console.verticalScrollBar().maximum())

    def show_close_button(self):
        self.close_button.show()
        self.setWindowTitle("Release Complete")


class GitHubToolsPlugin:
    def __init__(self, puffin_api: PuffinPluginAPI):
        self.api = puffin_api
        self.main_window = self.api.get_main_window()
        self.project_manager = self.api.get_manager("project")
        self.git_manager = self.api.get_manager("git")
        self.github_manager = self.api.get_manager("github")
        self.github_dialog = None
        self._release_state = {}
        self.build_process = None
        self.progress_dialog = None
        self.api.log_info("GitHub Tools plugin initialized.")
        if sc_panel := self._get_sc_panel():
            sc_panel.create_release_requested.connect(self.show_create_release_dialog)
            sc_panel.publish_repo_requested.connect(self._publish_repo)
            sc_panel.link_to_remote_requested.connect(self._link_repo)
            sc_panel.change_visibility_requested.connect(self._change_visibility)
            self.api.log_info("GitHub Tools: Connected signals from Source Control Panel.")

    def _get_sc_panel(self):
        return getattr(self.main_window, 'source_control_panel', None)

    def _log_to_dialog(self, message: str, is_error: bool = False, is_warning: bool = False):
        log_func = self.api.log_error if is_error else (self.api.log_warning if is_warning else self.api.log_info)
        log_func(f"[Release] {message}")
        if self.progress_dialog:
            self.progress_dialog.add_log(message, is_error=is_error, is_warning=is_warning)

    def ensure_git_identity(self, project_path: str) -> bool:
        # Check for local .git/config first
        try:
            repo = git.Repo(project_path)
            with repo.config_reader() as cr:
                if cr.has_section('user') and cr.has_option('user', 'name') and cr.has_option('user', 'email'):
                    return True
        except Exception:
            pass

        user_info = self.github_manager.get_user_info()
        if not (user_info and user_info.get('login')):
            self.api.show_message("warning", "GitHub Login Required",
                                  "You must be logged into GitHub to ensure a valid author.")
            return False

        return True

    def show_create_release_dialog(self, project_path: str = None):
        if not project_path: project_path = self.project_manager.get_active_project_path()
        if not project_path:
            self.api.show_message("info", "No Project", "Please open a project to create a release.")
            return
        self._prepare_repository_for_release(project_path)

    def _prepare_repository_for_release(self, path: str):
        self.api.show_status_message("Verifying repository state...")

        try:
            repo = git.Repo(path)
            if repo.is_dirty(untracked_files=True):
                unmerged_paths = [p for p, _ in repo.index.unmerged_blobs().items()]
                if unmerged_paths:
                    msg = "Your repository has unresolved merge conflicts. Please resolve them, commit the changes, and try again."
                else:
                    msg = "Your repository has uncommitted changes or untracked files. Please commit or stash them before creating a release."
                self.api.show_message("critical", "Unclean Repository", msg)
                return

            if not repo.remotes:
                self.api.show_message("critical", "No Remote", "This project has no remote repository configured.")
                return

            is_synced, fix_attempted, error = self._check_and_handle_branch_sync(repo)
            if error:
                self.api.show_message("info", "Release Cancelled", error)
                return
            if fix_attempted:
                return

            if is_synced:
                self.api.show_status_message("Repository is clean and ready for release.", 2000)
                self._start_release_process(path)

        except git.GitCommandError as e:
            self.api.show_message("critical", "Git Error",
                                  f"A Git command failed during pre-flight checks:\n\n{e.stderr}")
        except Exception as e:
            self.api.show_message("critical", "Repository Error", f"Could not check repository status: {e}")

    def _check_and_handle_branch_sync(self, repo: Repo) -> tuple[bool, bool, str]:
        self.api.show_status_message("Fetching remote status...")
        try:
            repo.remotes.origin.fetch()
        except git.GitCommandError as e:
            return False, False, f"Could not fetch from remote: {e.stderr}"

        active_branch = repo.active_branch
        tracking_branch = active_branch.tracking_branch()

        if not tracking_branch:
            return False, False, f"Local branch '{active_branch.name}' is not tracking a remote branch. Please push it to the remote first."

        ahead_commits = list(repo.iter_commits(f'{tracking_branch.name}..{active_branch.name}'))
        behind_commits = list(repo.iter_commits(f'{active_branch.name}..{tracking_branch.name}'))

        if ahead_commits and behind_commits:
            error_msg = (
                "Your local branch has diverged from the remote repository "
                "(both have new changes).\n\nPlease use an external Git client to "
                "manually `git pull` or `git rebase` to resolve the divergence "
                "before creating a release."
            )
            self.api.show_message("critical", "Branch has Diverged", error_msg)
            return False, False, "User intervention required for diverged branch."

        if behind_commits:
            msg_box = QMessageBox(self.main_window)
            msg_box.setIcon(QMessageBox.Icon.Question)
            msg_box.setWindowTitle("Branch Is Behind")
            msg_box.setText("Your local branch is behind the remote repository.")
            msg_box.setInformativeText(
                "It is strongly recommended to pull these changes before creating a release. Do you want to pull now?")

            pull_button = msg_box.addButton("Pull Changes", QMessageBox.ButtonRole.AcceptRole)
            cancel_button = msg_box.addButton("Cancel Release", QMessageBox.ButtonRole.RejectRole)
            msg_box.setDefaultButton(pull_button)
            msg_box.exec()

            if msg_box.clickedButton() == pull_button:
                self._trigger_background_pull(repo.working_dir)
                return False, True, ""
            else:
                return False, False, "Synchronization was cancelled by user."

        if ahead_commits:
            self.api.log_info(
                f"Branch '{active_branch.name}' is {len(ahead_commits)} commit(s) ahead, which is expected for a new release.")
        else:
            self.api.log_info(f"Branch '{active_branch.name}' is up-to-date with the remote.")

        return True, False, ""

    def _trigger_background_pull(self, repo_path: str):
        self.api.show_status_message("Pulling remote changes...")
        self.git_manager.git_success.connect(lambda msg, data: self._on_preflight_pull_finished(True, msg, repo_path))
        self.git_manager.git_error.connect(lambda err: self._on_preflight_pull_finished(False, err, repo_path))
        self.git_manager.pull(repo_path)

    def _on_preflight_pull_finished(self, success: bool, message: str, repo_path: str):
        try:
            self.git_manager.git_success.disconnect()
            self.git_manager.git_error.disconnect()
        except TypeError:
            pass

        if success:
            if hasattr(self.main_window, 'explorer_panel') and self.main_window.explorer_panel:
                self.main_window.explorer_panel.refresh()
            self._prepare_repository_for_release(repo_path)
        else:
            msg_box = QMessageBox(self.main_window)
            msg_box.setIcon(QMessageBox.Icon.Critical)
            msg_box.setWindowTitle("Pull Failed")
            msg_box.setText("Could not synchronize with the remote repository.")
            msg_box.setInformativeText(f"<b>Reason:</b><br><pre>{message}</pre>")
            msg_box.exec()

    def _start_release_process(self, project_path: str):
        if not self.ensure_git_identity(project_path): return
        dialog = NewReleaseDialog(project_path, self.git_manager, self.main_window)
        if not dialog.exec():
            self.api.show_status_message("Release cancelled.", 3000)
            return

        self.progress_dialog = UploadProgressDialog(self.main_window)
        self.progress_dialog.show()

        try:
            repo = git.Repo(project_path)
            owner, repo_name = self.git_manager.parse_git_url(repo.remotes.origin.url)
            if not owner or not repo_name:
                self._on_release_step_failed("Could not parse owner/repo from remote URL.")
                return
        except Exception as e:
            self._on_release_step_failed(f"Could not analyze repository: {e}")
            return

        self._release_state = {'dialog_data': dialog.get_release_data(), 'project_path': project_path,
                               'owner': owner, 'repo_name': repo_name}
        self._advance_release_state("BUMP_VERSION_COMMIT")

    def _advance_release_state(self, next_step):
        self._release_state['step'] = next_step
        step_title = next_step.replace('_', ' ').title()
        self._log_to_dialog(f"Starting step: {step_title}")
        if sc_panel := self._get_sc_panel(): sc_panel.set_ui_locked(True, f"Step: {step_title}...")

        project_path = self._release_state['project_path']
        dialog_data = self._release_state['dialog_data']

        self._cleanup_connections()

        if next_step in ["CREATE_RELEASE", "UPLOAD_ASSET"]:
            self.github_manager.operation_success.connect(self._on_github_step_success)
            self.github_manager.operation_failed.connect(self._on_release_step_failed)
        else:
            self.git_manager.git_success.connect(self._on_git_step_success)
            self.git_manager.git_error.connect(self._on_release_step_failed)

        if next_step == "BUMP_VERSION_COMMIT":
            if not versioning.write_new_version(dialog_data['tag']):
                self._on_release_step_failed("Failed to write new version to VERSION.txt")
                return
            self.main_window._update_window_title()
            self.git_manager.commit_files(project_path, f"ci: Release {dialog_data['tag']}")
        elif next_step == "PUSH_MAIN_BRANCH":
            self.git_manager.push(project_path)
        elif next_step == "CREATE_TAG":
            self.git_manager.create_tag(project_path, dialog_data['tag'], dialog_data['title'])
        elif next_step == "PUSH_TAG":
            self.git_manager.push_specific_tag(project_path, dialog_data['tag'])
        elif next_step == "CREATE_RELEASE":
            self.github_manager.create_github_release(
                owner=self._release_state['owner'], repo=self._release_state['repo_name'],
                tag_name=dialog_data['tag'], name=dialog_data['title'],
                body=dialog_data['notes'], prerelease=dialog_data['prerelease'])
        elif next_step == "BUILD_ASSETS":
            self._run_build_script()
        elif next_step == "UPLOAD_ASSETS":
            self._upload_assets()

    def _on_git_step_success(self, msg, data):
        step_map = {"BUMP_VERSION_COMMIT": "PUSH_MAIN_BRANCH", "PUSH_MAIN_BRANCH": "CREATE_TAG",
                    "CREATE_TAG": "PUSH_TAG", "PUSH_TAG": "CREATE_RELEASE"}
        if next_step := step_map.get(self._release_state.get('step')):
            self._advance_release_state(next_step)

    def _on_github_step_success(self, msg, data):
        step = self._release_state.get('step')
        if step == "CREATE_RELEASE":
            self._release_state['release_info'] = data.get("release_data", {})
            self._advance_release_state("BUILD_ASSETS")
        elif step == "UPLOAD_ASSET":
            self._upload_next_asset()

    def _run_build_script(self):
        self._log_to_dialog("Simulating build process...", is_warning=True)
        self._advance_release_state("UPLOAD_ASSETS")

    def _upload_assets(self):
        self._log_to_dialog("Simulating asset upload...", is_warning=True)
        self._cleanup_release_process(success=True)

    def _upload_next_asset(self):
        if not self._release_state.get('asset_queue'):
            self.api.show_message("info", "Release Complete", "Release created and all assets uploaded successfully.")
            self._cleanup_release_process(success=True)
            return

    def _on_release_step_failed(self, error_message):
        step = self._release_state.get('step', 'UNKNOWN')
        self._log_to_dialog(f"FAILED on step '{step}': {error_message}", is_error=True)
        self.api.show_message("critical", "Release Failed", f"An error occurred at step '{step}'.\n\n{error_message}")
        self._cleanup_release_process(success=False)

    def _cleanup_connections(self):
        try:
            self.git_manager.git_success.disconnect()
            self.git_manager.git_error.disconnect()
            self.github_manager.operation_success.disconnect()
            self.github_manager.operation_failed.disconnect()
        except TypeError:
            pass

    def _cleanup_release_process(self, success=False):
        self._cleanup_connections()
        if sc_panel := self._get_sc_panel(): sc_panel.set_ui_locked(False, "Release process finished.")
        if self.progress_dialog:
            self.progress_dialog.add_log(f"\n--- RELEASE {'COMPLETE' if success else 'FAILED'} ---")
            self.progress_dialog.show_close_button()
        self._release_state = {}

    def _publish_repo(self, path):
        repo_name, ok = QInputDialog.getText(self.main_window, "Publish to GitHub", "Repository Name:",
                                             text=os.path.basename(path))
        if not (ok and repo_name): return
        if not self.ensure_git_identity(path): return
        desc, _ = QInputDialog.getText(self.main_window, "Description", "Description (optional):")
        private = QMessageBox.question(self.main_window, "Visibility", "Make repository private?",
                                       QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No) == QMessageBox.StandardButton.Yes
        self.github_manager.create_repo(repo_name, desc, private)
        if sc_panel := self._get_sc_panel():
            sc_panel.set_ui_locked(True, f"Creating '{repo_name}'...")

    def _link_repo(self, path):
        if not self.ensure_git_identity(path): return
        dialog = SelectRepoDialog(self.github_manager, self.main_window)
        if dialog.exec() and (repo_data := dialog.selected_repo_data):
            self.git_manager.link_to_remote(path, repo_data.get('clone_url'))

    def _change_visibility(self, path):
        try:
            repo = git.Repo(path)
            if not repo.remotes: return
            owner, repo_name = self.git_manager.parse_git_url(repo.remotes.origin.url)
            private = QMessageBox.question(self.main_window, "Visibility", "Make repository private?",
                                           QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No) == QMessageBox.StandardButton.Yes
            self.github_manager.update_repo_visibility(owner, repo_name, private)
        except Exception as e:
            self.api.show_message("critical", "Error", f"Could not get repository info: {e}")

    def _show_github_dialog(self):
        if not self.github_dialog:
            self.github_dialog = GitHubDialog(self.github_manager, self.git_manager, self.main_window)
            self.github_manager.project_cloned.connect(self.project_manager.open_project)
        self.github_dialog.show()


def initialize(puffin_api: PuffinPluginAPI):
    plugin = GitHubToolsPlugin(puffin_api)
    puffin_api.add_menu_action("tools", "GitHub Repositories...", plugin._show_github_dialog, icon_name="fa5b.github")
    puffin_api.add_menu_action("tools", "New Release...", plugin.show_create_release_dialog, icon_name="fa5s.tag")
    return plugin
```

### File: `/plugins/github_tools/plugin.json`
```json
{
    "id": "github_tools",
    "name": "GitHub Tools",
    "author": "PuffinPy Team",
    "version": "1.2.0",
    "description": "Provides UI for cloning, releases, and other GitHub interactions.",
    "entry_point": "plugin_main.py"
}
```

### File: `/plugins/github_tools/new_release_dialog.py`
```py
# PuffinPyEditor/plugins/github_tools/new_release_dialog.py
from typing import Optional, Dict, Any
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QFormLayout,
                             QDialogButtonBox, QLineEdit, QTextEdit, QLabel,
                             QCheckBox, QComboBox, QHBoxLayout, QWidget,
                             QGroupBox, QPushButton, QMessageBox)
from app_core.source_control_manager import SourceControlManager
from utils.versioning import suggest_next_version

try:
    import git
except ImportError:
    git = None


class NewReleaseDialog(QDialog):
    """
    A dialog for creating a new GitHub release. It collects tag name, title,
    notes, and other release options.
    """

    def __init__(self, project_path: str, git_manager: SourceControlManager,
                 parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.project_path = project_path
        self.git_manager = git_manager

        self.setWindowTitle("Create New Release")
        self.setMinimumWidth(500)

        self._setup_ui()
        self._connect_signals()
        self._populate_branches()
        self._validate_input()

    def _setup_ui(self):
        self.main_layout = QVBoxLayout(self)
        form_layout = QFormLayout()
        form_layout.setRowWrapPolicy(QFormLayout.RowWrapPolicy.WrapAllRows)
        
        # Tag Name with Tooltip
        tag_layout_widget = QWidget()
        tag_layout = QHBoxLayout(tag_layout_widget)
        tag_layout.setContentsMargins(0, 0, 0, 0)
        suggested_tag = suggest_next_version()
        self.tag_edit = QLineEdit(suggested_tag)
        self.tag_edit.setPlaceholderText("e.g., v1.2.1")
        self.tag_edit.setToolTip("The Git tag to create (e.g., v1.0.0). This should be a unique version number.")
        self.branch_combo = QComboBox()
        self.branch_combo.setToolTip("Select the branch to create the release from. This should be your main, stable branch.")
        tag_layout.addWidget(self.tag_edit, 2)
        tag_layout.addWidget(QLabel("on branch:"))
        tag_layout.addWidget(self.branch_combo, 1)
        form_layout.addRow("<b>Tag Name:</b>", tag_layout_widget)

        # Release Title with Tooltip
        self.title_edit = QLineEdit(suggested_tag)
        self.title_edit.setPlaceholderText("e.g., Feature Update and Bug Fixes")
        self.title_edit.setToolTip("The title of the GitHub Release. Can be the same as the tag.")
        form_layout.addRow("<b>Release Title:</b>", self.title_edit)
        self.main_layout.addLayout(form_layout)

        # Release Notes with Tooltip
        notes_header_layout = QHBoxLayout()
        notes_header_layout.addWidget(QLabel("<b>Release Notes:</b>"))
        notes_header_layout.addStretch()
        self.generate_notes_button = QPushButton("Generate from Commits")
        self.generate_notes_button.setToolTip("Generate release notes automatically from commits since the last tag.")
        notes_header_layout.addWidget(self.generate_notes_button)
        self.main_layout.addLayout(notes_header_layout)
        self.notes_edit = QTextEdit()
        self.notes_edit.setPlaceholderText("Describe the changes in this release (Markdown is supported).")
        self.notes_edit.setMinimumHeight(150)
        self.main_layout.addWidget(self.notes_edit)

        # Options with Tooltips
        options_group = QGroupBox("Options")
        options_layout = QVBoxLayout(options_group)
        self.prerelease_checkbox = QCheckBox("Mark as a pre-release")
        self.prerelease_checkbox.setToolTip("Check this for alpha, beta, or release candidate versions. It indicates the release is not production-ready.")
        options_layout.addWidget(self.prerelease_checkbox)
        self.main_layout.addWidget(options_group)
        
        assets_group = QGroupBox("Release Assets")
        assets_layout = QVBoxLayout(assets_group)
        self.build_installer_checkbox = QCheckBox("Build and attach installer")
        self.build_installer_checkbox.setToolTip("If your project has an installer script, this will run it and upload the result.")
        self.build_installer_checkbox.setChecked(True)
        assets_layout.addWidget(self.build_installer_checkbox)
        self.main_layout.addWidget(assets_group)
        
        self.button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.main_layout.addWidget(self.button_box)

    def _connect_signals(self):
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        self.tag_edit.textChanged.connect(self._validate_input)
        self.title_edit.textChanged.connect(self._validate_input)
        self.generate_notes_button.clicked.connect(self._generate_release_notes)

    def _populate_branches(self):
        branches = self.git_manager.get_local_branches(self.project_path)
        self.branch_combo.addItems(branches)
        if 'main' in branches: self.branch_combo.setCurrentText('main')
        elif 'master' in branches: self.branch_combo.setCurrentText('master')

    def _validate_input(self):
        is_valid = bool(self.tag_edit.text().strip() and self.title_edit.text().strip() and self.branch_combo.currentText())
        self.button_box.button(QDialogButtonBox.StandardButton.Ok).setEnabled(is_valid)

    def _generate_release_notes(self):
        if not git:
            QMessageBox.critical(self, "Missing Dependency", "The 'GitPython' library is required for this feature.")
            return
        try:
            repo = git.Repo(self.project_path, search_parent_directories=True)
            tags = sorted(repo.tags, key=lambda t: t.commit.committed_datetime)
            latest_tag = tags[-1] if tags else None
            rev_range = f"{latest_tag.commit.hexsha}..{self.branch_combo.currentText()}" if latest_tag else self.branch_combo.currentText()
            commits = list(repo.iter_commits(rev_range, no_merges=True))
            if not commits:
                QMessageBox.information(self, "No New Commits", f"No new commits found on branch '{self.branch_combo.currentText()}' since the last tag.")
                return
            commit_log = [f"- {c.summary} ({c.hexsha[:7]})" for c in commits]
            self.notes_edit.setText("\n".join(commit_log))
        except Exception as e:
            QMessageBox.critical(self, "Error Generating Notes", f"An error occurred: {e}")

    def get_release_data(self) -> Dict[str, Any]:
        return {
            "tag": self.tag_edit.text().strip(),
            "title": self.title_edit.text().strip(),
            "notes": self.notes_edit.toPlainText().strip(),
            "prerelease": self.prerelease_checkbox.isChecked(),
            "target_branch": self.branch_combo.currentText(),
            "build_installer": self.build_installer_checkbox.isChecked()
        }
```

### File: `/plugins/github_tools/github_dialog.py`
```py
# PuffinPyEditor/plugins/github_tools/github_dialog.py
import os
from typing import Optional, List, Dict, Any
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QWidget,
                             QSplitter, QLabel, QListWidget, QListWidgetItem,
                             QPushButton, QMessageBox, QFileDialog)
from PyQt6.QtCore import Qt, pyqtSignal
from app_core.github_manager import GitHubManager
from app_core.source_control_manager import SourceControlManager
import qtawesome as qta


class GitHubDialog(QDialog):
    """
    A dialog for browsing and cloning a user's GitHub repositories.
    """
    project_cloned = pyqtSignal(str)

    def __init__(self, github_manager: GitHubManager,
                 git_manager: SourceControlManager,
                 parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.github_manager = github_manager
        self.git_manager = git_manager

        self.setWindowTitle("GitHub Repository Management")
        self.setMinimumSize(800, 600)
        self._setup_ui()
        self._connect_signals()

    def _setup_ui(self):
        layout = QVBoxLayout(self)

        top_bar_layout = QHBoxLayout()
        self.user_label = QLabel("<i>Checking authentication...</i>")
        top_bar_layout.addWidget(self.user_label)
        top_bar_layout.addStretch()
        layout.addLayout(top_bar_layout)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        layout.addWidget(splitter)
        left_pane = self._create_repo_list_pane()
        right_pane = self._create_details_pane()
        splitter.addWidget(left_pane)
        splitter.addWidget(right_pane)
        splitter.setSizes([300, 500])

    def _create_repo_list_pane(self) -> QWidget:
        pane = QWidget()
        layout = QVBoxLayout(pane)
        layout.setContentsMargins(0, 0, 0, 0)
        toolbar_layout = QHBoxLayout()
        self.refresh_button = QPushButton("Refresh List")
        self.refresh_button.setIcon(qta.icon('fa5s.sync-alt'))
        toolbar_layout.addWidget(self.refresh_button)
        toolbar_layout.addStretch()
        self.repo_list = QListWidget()
        layout.addLayout(toolbar_layout)
        layout.addWidget(self.repo_list)
        return pane

    def _create_details_pane(self) -> QWidget:
        pane = QWidget()
        layout = QVBoxLayout(pane)
        self.repo_details_label = QLabel("<i>Select a repository...</i>")
        self.repo_details_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.repo_details_label.setWordWrap(True)
        layout.addWidget(self.repo_details_label, 1)
        layout.addWidget(QLabel("<b>Branches:</b>"))
        self.branch_list = QListWidget()
        layout.addWidget(self.branch_list, 2)
        self.clone_button = QPushButton("Clone Selected Branch")
        self.clone_button.setIcon(qta.icon('fa5s.download'))
        self.clone_button.setEnabled(False)
        layout.addWidget(self.clone_button)
        return pane

    def _connect_signals(self):
        self.github_manager.repos_ready.connect(self.populate_repo_list)
        self.github_manager.branches_ready.connect(self.populate_branch_list)
        self.github_manager.operation_failed.connect(
            self._on_operation_failed)
        self.repo_list.currentItemChanged.connect(self.on_repo_selected)
        self.refresh_button.clicked.connect(self.github_manager.list_repos)
        self.clone_button.clicked.connect(self.on_clone_clicked)

    def showEvent(self, event):
        super().showEvent(event)
        self._update_user_info()
        self.refresh_button.click()

    def closeEvent(self, event):
        try:
            self.github_manager.repos_ready.disconnect(self.populate_repo_list)
            self.github_manager.branches_ready.disconnect(
                self.populate_branch_list)
            self.github_manager.operation_failed.disconnect(
                self._on_operation_failed)
        except TypeError:
            pass  # Suppress errors if signals are not connected
        super().closeEvent(event)

    def _update_user_info(self):
        user_info = self.github_manager.get_user_info()
        if user_info and user_info.get('login'):
            self.user_label.setText(
                f"Authenticated as: <b>{user_info['login']}</b>")
        else:
            self.user_label.setText(
                "<i>Authentication details not available.</i>")

    def populate_repo_list(self, repos: List[Dict[str, Any]]):
        self.repo_list.clear()
        for repo in sorted(repos, key=lambda r: r['name'].lower()):
            item = QListWidgetItem(repo['name'])
            item.setToolTip(repo['full_name'])
            item.setData(Qt.ItemDataRole.UserRole, repo)
            self.repo_list.addItem(item)

    def populate_branch_list(self, branches: List[Dict[str, Any]]):
        self.branch_list.clear()
        for branch in branches:
            item = QListWidgetItem(branch['name'])
            item.setData(Qt.ItemDataRole.UserRole, branch)
            self.branch_list.addItem(item)
        if branches:
            self.branch_list.setCurrentRow(0)

    def on_repo_selected(self, current_item: QListWidgetItem):
        self.branch_list.clear()
        self.clone_button.setEnabled(False)
        if not current_item:
            self.repo_details_label.setText("<i>Select a repository...</i>")
            return
        repo_data = current_item.data(Qt.ItemDataRole.UserRole)
        desc = repo_data.get('description') or 'No description provided.'
        self.repo_details_label.setText(
            f"<b>{repo_data['full_name']}</b><br/><small>{desc}</small>")
        self.github_manager.list_branches(repo_data['full_name'])
        self.clone_button.setEnabled(True)

    def on_clone_clicked(self):
        repo_item = self.repo_list.currentItem()
        branch_item = self.branch_list.currentItem()
        if not repo_item or not branch_item:
            QMessageBox.warning(self, "Selection Required",
                                "Please select a repository and a branch.")
            return
        repo_data = repo_item.data(Qt.ItemDataRole.UserRole)
        branch_data = branch_item.data(Qt.ItemDataRole.UserRole)
        path = QFileDialog.getExistingDirectory(
            self, f"Select Folder to Clone '{repo_data['name']}' Into")
        if not path:
            return
        clone_path = os.path.join(path, repo_data['name'])
        if os.path.exists(clone_path):
            QMessageBox.critical(
                self, "Folder Exists",
                f"The folder '{repo_data['name']}' already exists here.")
            return
        self.git_manager.clone_repo(
            repo_data['clone_url'], path, branch_data['name'])
        QMessageBox.information(
            self, "Clone Started",
            "Cloning has started. The project will open when complete.")
        self.project_cloned.emit(clone_path)
        self.accept()

    def _on_operation_failed(self, error_message: str):
        QMessageBox.critical(self, "GitHub Error", error_message)

```

### File: `/plugins/github_tools/__init__.py`
```py

```

### File: `/plugins/api_keys_manager/plugin_main.py`
```py
# PuffinPyEditor/plugins/api_keys_manager/plugin_main.py
from .api_keys_settings_page import ApiKeysDialog
from app_core.puffin_api import PuffinPluginAPI

class ApiKeysManagerPlugin:
    def __init__(self, puffin_api: PuffinPluginAPI):
        self.api = puffin_api
        self.api.add_menu_action(
            menu_name="tools",
            text="Manage API Keys...",
            callback=self.show_api_keys_dialog,
            icon_name="fa5s.key"
        )

    def show_api_keys_dialog(self):
        settings_manager = self.api.get_manager("settings")
        dialog = ApiKeysDialog(settings_manager, self.api.get_main_window())
        dialog.exec()

def initialize(puffin_api: PuffinPluginAPI):
    return ApiKeysManagerPlugin(puffin_api)
```

### File: `/plugins/api_keys_manager/plugin.json`
```json
{
    "id": "api_keys_manager",
    "name": "API Keys Manager",
    "author": "PuffinPy Team",
    "version": "1.0.0",
    "description": "Provides a secure settings page for managing API provider keys.",
    "entry_point": "plugin_main.py"
}
```

### File: `/plugins/api_keys_manager/api_keys_settings_page.py`
```py
# PuffinPyEditor/plugins/api_keys_manager/api_keys_settings_page.py
from PyQt6.QtWidgets import (
    QDialog, QFormLayout, QLineEdit, QHBoxLayout, QPushButton, QLabel,
    QDialogButtonBox, QVBoxLayout
)
import qtawesome as qta


class ApiKeysDialog(QDialog):
    """A dialog for managing API keys."""
    def __init__(self, settings_manager, parent=None):
        super().__init__(parent)
        self.settings_manager = settings_manager

        self.setWindowTitle("Manage API Keys")
        self.setMinimumWidth(500)

        main_layout = QVBoxLayout(self)
        form_layout = QFormLayout()

        info_label = QLabel(
            "Enter your API keys below. They are stored locally and securely."
        )
        form_layout.addRow(info_label)

        # Add providers here. We'll start with OpenAI.
        self.openai_key_input, openai_layout = self._create_key_input()
        form_layout.addRow("OpenAI API Key:", openai_layout)

        main_layout.addLayout(form_layout)

        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok |
            QDialogButtonBox.StandardButton.Cancel
        )
        main_layout.addWidget(button_box)

        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)

        self.load_settings()

    def _create_key_input(self) -> tuple[QLineEdit, QHBoxLayout]:
        """Creates a password-style QLineEdit with a show/hide button."""
        layout = QHBoxLayout()
        line_edit = QLineEdit()
        line_edit.setEchoMode(QLineEdit.EchoMode.Password)

        show_hide_button = QPushButton(qta.icon('fa5s.eye'), "")
        show_hide_button.setCheckable(True)
        show_hide_button.setToolTip("Show/Hide Key")
        show_hide_button.setFixedWidth(30)
        show_hide_button.toggled.connect(
            lambda c: line_edit.setEchoMode(
                QLineEdit.EchoMode.Normal if c
                else QLineEdit.EchoMode.Password)
        )

        layout.addWidget(line_edit)
        layout.addWidget(show_hide_button)
        return line_edit, layout

    def load_settings(self):
        """Loads saved API keys into the input fields."""
        keys = self.settings_manager.get("api_keys", {})
        self.openai_key_input.setText(keys.get("OpenAI", ""))

    def save_settings(self):
        """Saves the API keys from the input fields."""
        keys = self.settings_manager.get("api_keys", {})
        keys["OpenAI"] = self.openai_key_input.text()
        self.settings_manager.set("api_keys", keys)
        self.settings_manager.save()

    def accept(self):
        """Saves settings and closes the dialog."""
        self.save_settings()
        super().accept()
```

### File: `/plugins/api_keys_manager/__init__.py`
```py

```

### File: `/plugins/ai_tools/style_preset_manager.py`
```py
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
```

### File: `/plugins/ai_tools/plugin_main.py`
```py
# PuffinPyEditor/plugins/ai_tools/plugin_main.py
from .ai_export_dialog import AIExportDialog
from app_core.puffin_api import PuffinPluginAPI
from utils.logger import log


class AIToolsPlugin:
    def __init__(self, puffin_api: PuffinPluginAPI):
        self.api = puffin_api
        self.main_window = self.api.get_main_window()
        self.export_dialog_instance = None 

        self.api.add_menu_action(
            menu_name="tools",
            text="AI Task Manager...",
            callback=self.show_export_dialog,
            icon_name="fa5s.robot"
        )
        log.info("AI Tools plugin initialized.")

    def show_export_dialog(self):
        """Opens the main AI Export dialog."""
        project_manager = self.api.get_manager("project")
        project_path = project_manager.get_active_project_path()
        if not project_path:
            self.api.show_message("info", "No Project Open", "Please open a project to use the AI Task Manager.")
            return

        self.export_dialog_instance = AIExportDialog(
            project_path=project_path,
            puffin_api=self.api,
            parent=self.main_window
        )
        self.export_dialog_instance.exec()


def initialize(puffin_api: PuffinPluginAPI):
    """Entry point for PuffinPyEditor to load the plugin."""
    return AIToolsPlugin(puffin_api)
```

### File: `/plugins/ai_tools/plugin.json`
```json
{
    "id": "ai_tools",
    "name": "AI Tools",
    "author": "PuffinPy Team",
    "version": "1.1.2",
    "description": "Adds an 'Export for AI' dialog.",
    "entry_point": "plugin_main.py"
}
```

### File: `/plugins/ai_tools/persona_manager_dialog.py`
```py
# /plugins/ai_tools/persona_manager_dialog.py
import os
import re
import json
import shutil
import importlib.util
from typing import Dict, List, Any
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QTabWidget, QWidget, QSplitter,
    QListWidget, QListWidgetItem, QGroupBox, QFormLayout, QLineEdit,
    QPlainTextEdit, QPushButton, QDialogButtonBox, QMessageBox,
    QLabel, QHBoxLayout, QInputDialog
)
from PyQt6.QtGui import QFont, QTextCursor
from PyQt6.QtCore import Qt
import qtawesome as qta
from app_core.settings_manager import settings_manager
from app_core.highlighters.python_syntax_highlighter import PythonSyntaxHighlighter
from utils.logger import log
from utils.helpers import get_base_path
from .style_preset_manager import StylePresetManager
from app_core import golden_rules

# Boilerplate for creating a new persona file from scratch.
PERSONA_TEMPLATE = """
# /assets/ai_personas/{file_name}.py
import os

class Persona:
    \"\"\"
    {description}
    \"\"\"

    @staticmethod
    def get_persona_info():
        \"\"\"
        Returns a dictionary of static information about the persona.
        \"\"\"
        return {{
            "id": os.path.splitext(os.path.basename(__file__))[0],
            "name": "{name}",
            "title": "{title}",
            "expertise": "{expertise}"
        }}

    def __init__(self):
        self.name = self.get_persona_info()['name']
        self.title = self.get_persona_info()['title']
        self.expertise = self.get_persona_info()['expertise']

    def generate_prompt(self, context: dict) -> tuple[str, str]:
        \"\"\"
        Generates the system and user prompts for this persona.
        \"\"\"
        # --- System Prompt ---
        system_prompt = '''
{system_prompt_logic}
'''

        # --- User Prompt ---
        file_contents_section = []
        for path, content in context.get("file_contents", {{}}).items():
            relative_path = path.replace(context.get("project_root", ""), "", 1).lstrip("/\\\\")
            language = os.path.splitext(path)[1].lstrip('.') or 'text'

            linter_output = ""
            if linter_issues := context.get("linter_results", {{}}).get(path):
                linter_output += "\\n**Linter Issues Found:**\\n"
                for issue in linter_issues:
                    linter_output += "- `Line " + str(issue['line']) + "`: " + issue['code'] + " - " + issue['description'] + "\\n"

            file_contents_section.append(
                "### File: `/" + relative_path + "`" +
                linter_output + "\\n" +
                "```" + language + "\\n" + content + "\\n```"
            )

        file_contents_str = "\\n\\n".join(file_contents_section)

        user_prompt = (
            "**User's Primary Goal:**\\n" +
            context.get("user_instructions", "Perform a general review of the provided code based on your expertise.") +
            "\\n\\n---\\n\\n**Project File Tree:**\\n```\\n" +
            context.get("file_tree", "No file tree provided.") +
            "\\n```\\n\\n---\\n\\n**Full File Contents & Context:**\\n" +
            file_contents_str
        )
        return system_prompt.strip(), user_prompt.strip()

def get_persona_info():
    return Persona.get_persona_info()

def get_persona_instance():
    return Persona()
"""


class PersonaManagerDialog(QDialog):
    """A dialog for managing AI Personas and Style Presets."""

    def __init__(self, theme_manager, parent=None):
        super().__init__(parent)
        self.theme_manager = theme_manager
        self.preset_manager = StylePresetManager()
        self.personas: Dict[str, Dict] = {}
        self.persona_modules: Dict[str, Any] = {}
        self.current_persona_path: str = ""
        self.has_unsaved_changes = False

        self.setWindowTitle("Persona & Style Preset Manager")
        self.setMinimumSize(950, 750)
        self.main_layout = QVBoxLayout(self)

        self.tab_widget = QTabWidget()
        self.tab_widget.addTab(self._create_personas_tab(), "Personas")
        self.tab_widget.addTab(self._create_presets_tab(), "Style Presets")
        self.tab_widget.addTab(self._create_golden_rules_tab(), "Golden Rules")
        self.main_layout.addWidget(self.tab_widget)
        
        self.tab_widget.currentChanged.connect(self._on_tab_changed)

        self._load_all_data()

    def _create_personas_tab(self) -> QWidget:
        widget = QWidget()
        layout = QHBoxLayout(widget)
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        left_pane = QWidget()
        left_layout = QVBoxLayout(left_pane)
        left_layout.addWidget(QLabel("<b>Available Personas:</b>"))
        self.persona_list = QListWidget()
        self.persona_list.currentItemChanged.connect(self._on_persona_selected)
        left_layout.addWidget(self.persona_list)
        
        list_actions_layout = QHBoxLayout()
        add_button = QPushButton("Create New...")
        add_button.clicked.connect(self._create_new_persona)
        self.delete_button = QPushButton("Delete")
        self.delete_button.clicked.connect(self._delete_selected_persona)
        list_actions_layout.addWidget(add_button)
        list_actions_layout.addStretch()
        list_actions_layout.addWidget(self.delete_button)
        left_layout.addLayout(list_actions_layout)
        splitter.addWidget(left_pane)

        right_pane = QWidget()
        right_layout = QVBoxLayout(right_pane)
        
        meta_group = QGroupBox("Metadata")
        meta_layout = QFormLayout(meta_group)
        self.persona_name_edit = QLineEdit()
        self.persona_title_edit = QLineEdit()
        self.persona_expertise_edit = QLineEdit()
        meta_layout.addRow("Name:", self.persona_name_edit)
        meta_layout.addRow("Title:", self.persona_title_edit)
        meta_layout.addRow("Expertise:", self.persona_expertise_edit)
        right_layout.addWidget(meta_group)

        prompt_group = QGroupBox("Prompt Logic (Python)")
        prompt_layout = QVBoxLayout(prompt_group)
        self.persona_code_edit = QPlainTextEdit()
        self.persona_code_edit.setFont(QFont("Consolas", 10))
        self.highlighter = PythonSyntaxHighlighter(self.persona_code_edit.document(), self.theme_manager)
        prompt_layout.addWidget(self.persona_code_edit)
        right_layout.addWidget(prompt_group, 1)

        self.save_changes_button = QPushButton("Save Changes")
        self.save_changes_button.clicked.connect(self._save_persona_changes)
        right_layout.addWidget(self.save_changes_button, 0, Qt.AlignmentFlag.AlignRight)

        splitter.addWidget(right_pane)
        splitter.setSizes([250, 700])
        layout.addWidget(splitter)

        for editor in [self.persona_name_edit, self.persona_title_edit, self.persona_expertise_edit, self.persona_code_edit]:
            if isinstance(editor, QLineEdit):
                editor.textChanged.connect(self._mark_unsaved)
            else:
                editor.textChanged.connect(self._mark_unsaved)

        return widget

    def _create_presets_tab(self) -> QWidget:
        widget = QWidget()
        layout = QHBoxLayout(widget)
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        left_pane = QWidget()
        left_layout = QVBoxLayout(left_pane)
        left_layout.addWidget(QLabel("<b>Style Presets:</b>"))
        self.rules_preset_list = QListWidget()
        self.rules_preset_list.currentItemChanged.connect(self._on_preset_selected)
        left_layout.addWidget(self.rules_preset_list)
        
        preset_actions = QHBoxLayout()
        new_preset_btn = QPushButton("New Preset...")
        new_preset_btn.clicked.connect(self._create_new_preset)
        self.delete_preset_btn = QPushButton("Delete Preset")
        self.delete_preset_btn.clicked.connect(self._delete_selected_preset)
        preset_actions.addWidget(new_preset_btn)
        preset_actions.addStretch()
        preset_actions.addWidget(self.delete_preset_btn)
        left_layout.addLayout(preset_actions)
        splitter.addWidget(left_pane)

        right_pane = QWidget()
        right_layout = QVBoxLayout(right_pane)
        self.rules_group_box = QGroupBox("Preset Details")
        rules_editor_layout = QVBoxLayout(self.rules_group_box)
        
        self.preset_desc_label = QLabel("<i>Select a preset to edit its rules.</i>")
        self.preset_desc_label.setWordWrap(True)
        rules_editor_layout.addWidget(self.preset_desc_label)
        
        self.rules_list_widget = QListWidget()
        rules_editor_layout.addWidget(self.rules_list_widget)

        rule_actions = QHBoxLayout()
        add_rule_btn = QPushButton("Add Rule")
        add_rule_btn.clicked.connect(self._add_rule)
        edit_rule_btn = QPushButton("Edit Rule")
        edit_rule_btn.clicked.connect(self._edit_rule)
        remove_rule_btn = QPushButton("Remove Rule")
        remove_rule_btn.clicked.connect(self._remove_rule)
        rule_actions.addWidget(add_rule_btn)
        rule_actions.addWidget(edit_rule_btn)
        rule_actions.addWidget(remove_rule_btn)
        rule_actions.addStretch()
        rules_editor_layout.addLayout(rule_actions)

        self.save_preset_button = QPushButton("Save Preset Changes")
        self.save_preset_button.clicked.connect(self._save_current_preset)
        right_layout.addWidget(self.rules_group_box)
        right_layout.addWidget(self.save_preset_button, 0, Qt.AlignmentFlag.AlignRight)

        splitter.addWidget(right_pane)
        splitter.setSizes([250, 700])
        layout.addWidget(splitter)

        return widget

    def _create_golden_rules_tab(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(10, 10, 10, 10)

        group_box = QGroupBox("Golden Rules for AI Interaction")
        group_layout = QVBoxLayout(group_box)
        
        description = QLabel(
            "These are the fundamental, non-negotiable rules sent with every AI request.<br>"
            "Edit the rules below. The numbering is for display and will be handled automatically."
        )
        description.setWordWrap(True)
        group_layout.addWidget(description)

        self.golden_rules_edit = QPlainTextEdit()
        self.golden_rules_edit.setFont(QFont("Consolas", 10))
        self.golden_rules_edit.setPlaceholderText("1. First rule...\n2. Second rule...")
        group_layout.addWidget(self.golden_rules_edit, 1)
        
        buttons_layout = QHBoxLayout()
        self.reset_golden_rules_button = QPushButton("Reset to Default")
        self.save_golden_rules_button = QPushButton("Save Changes")
        buttons_layout.addStretch()
        buttons_layout.addWidget(self.reset_golden_rules_button)
        buttons_layout.addWidget(self.save_golden_rules_button)
        group_layout.addLayout(buttons_layout)
        
        layout.addWidget(group_box)
        
        self.save_golden_rules_button.clicked.connect(self._save_golden_rules)
        self.reset_golden_rules_button.clicked.connect(self._reset_golden_rules)
        
        return widget

    def _load_all_data(self):
        self.has_unsaved_changes = False
        self._discover_and_populate_personas()
        
        if self.persona_list.count() > 0:
            self.persona_list.setCurrentRow(0)
            self._on_persona_selected(self.persona_list.item(0))
        else:
            self._set_editor_state(enabled=False)
            
        self._populate_rules_presets()
        if self.rules_preset_list.count() > 0:
            self.rules_preset_list.setCurrentRow(0)
        
        self._load_golden_rules()

    def _on_tab_changed(self, index: int):
        if self.tab_widget.tabText(index) == "Golden Rules":
            self._load_golden_rules()

    def _load_golden_rules(self):
        self.golden_rules_edit.setPlainText(golden_rules.get_golden_rules_text())

    def _save_golden_rules(self):
        text = self.golden_rules_edit.toPlainText()
        if golden_rules.save_golden_rules_from_text(text):
            QMessageBox.information(self, "Success", "Golden Rules have been saved.")
        else:
            QMessageBox.critical(self, "Error", "Could not save Golden Rules. Check logs for details.")

    def _reset_golden_rules(self):
        reply = QMessageBox.question(self, "Reset Rules", 
                                     "Are you sure you want to revert all Golden Rules to their default values?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                     QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            if golden_rules.reset_golden_rules_to_default():
                self._load_golden_rules()
                QMessageBox.information(self, "Success", "Golden Rules have been reset to default.")
            else:
                QMessageBox.critical(self, "Error", "Could not reset Golden Rules. Check logs for details.")

    def _discover_and_populate_personas(self):
        self.persona_list.clear()
        self.personas.clear()
        self.persona_modules.clear()
        persona_dir = os.path.join(get_base_path(), "assets", "ai_personas")

        if not os.path.isdir(persona_dir):
            os.makedirs(persona_dir, exist_ok=True)
            log.info(f"Created persona directory at {persona_dir}")
            return

        for filename in sorted(os.listdir(persona_dir)):
            if filename.endswith(".py") and not filename.startswith("__"):
                module_path = os.path.join(persona_dir, filename)
                module_name = f"assets.ai_personas.{os.path.splitext(filename)[0]}"
                try:
                    spec = importlib.util.spec_from_file_location(module_name, module_path)
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)

                    if hasattr(module, "get_persona_info"):
                        info = module.get_persona_info()
                        self.personas[info['id']] = info
                        item = QListWidgetItem(info['name'])
                        item.setData(Qt.ItemDataRole.UserRole, info['id'])
                        self.persona_list.addItem(item)
                except Exception as e:
                    log.error(f"Failed to load AI persona '{filename}': {e}", exc_info=True)

    def _on_persona_selected(self, item: QListWidgetItem):
        if self.has_unsaved_changes:
            reply = QMessageBox.question(self, "Unsaved Changes", 
                                       "You have unsaved changes. Discard them?",
                                       QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.No:
                previous_id = os.path.basename(os.path.splitext(self.current_persona_path)[0])
                for i in range(self.persona_list.count()):
                    if self.persona_list.item(i).data(Qt.ItemDataRole.UserRole) == previous_id:
                        self.persona_list.setCurrentRow(i)
                        break
                return
                
        if not item:
            self._set_editor_state(False)
            return
            
        persona_id = item.data(Qt.ItemDataRole.UserRole)
        persona_info = self.personas.get(persona_id)

        if not persona_info:
             self._set_editor_state(False)
             log.warning(f"Could not find info for persona ID: {persona_id}")
             return
        
        self.persona_name_edit.setText(persona_info.get("name", ""))
        self.persona_title_edit.setText(persona_info.get("title", ""))
        self.persona_expertise_edit.setText(persona_info.get("expertise", ""))
        
        self.current_persona_path = os.path.join(get_base_path(), "assets", "ai_personas", f"{persona_id}.py")
        
        try:
            with open(self.current_persona_path, 'r', encoding='utf-8') as f:
                content = f.read()
                match = re.search(r"system_prompt\s*=\s*'''\n(.*?)\n'''", content, re.DOTALL)
                prompt_logic = match.group(1).strip() if match else "# Could not automatically extract system_prompt logic."
                self.persona_code_edit.setPlainText(prompt_logic)
        except Exception as e:
            self.persona_code_edit.setPlainText(f"# Error loading persona code: {e}")
            log.error(f"Error reading persona file {self.current_persona_path}: {e}")

        self._set_editor_state(True)
        self.has_unsaved_changes = False
        self.save_changes_button.setEnabled(False)
        self.delete_button.setEnabled(True)

    def _mark_unsaved(self):
        self.has_unsaved_changes = True
        self.save_changes_button.setEnabled(True)

    def _set_editor_state(self, enabled: bool):
        self.persona_name_edit.setEnabled(enabled)
        self.persona_title_edit.setEnabled(enabled)
        self.persona_expertise_edit.setEnabled(enabled)
        self.persona_code_edit.setEnabled(enabled)
        self.save_changes_button.setEnabled(enabled and self.has_unsaved_changes)
        self.delete_button.setEnabled(enabled)

    def _save_persona_changes(self):
        if not self.current_persona_path: return

        file_name_without_ext = os.path.basename(os.path.splitext(self.current_persona_path)[0])
        
        full_code = PERSONA_TEMPLATE.format(
            file_name=file_name_without_ext,
            name=self.persona_name_edit.text(),
            title=self.persona_title_edit.text(),
            expertise=self.persona_expertise_edit.text(),
            description=f"Represents {self.persona_name_edit.text()}",
            system_prompt_logic=self.persona_code_edit.toPlainText()
        )
        
        try:
            with open(self.current_persona_path, 'w', encoding='utf-8') as f:
                f.write(full_code)
            
            QMessageBox.information(self, "Success", f"Persona '{self.persona_name_edit.text()}' saved successfully.")
            self.has_unsaved_changes = False
            self.save_changes_button.setEnabled(False)
            current_id = file_name_without_ext
            
            self._discover_and_populate_personas()
            for i in range(self.persona_list.count()):
                 if self.persona_list.item(i).data(Qt.ItemDataRole.UserRole) == current_id:
                      self.persona_list.setCurrentRow(i)
                      break
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save persona: {e}")
            log.error(f"Error saving persona: {e}", exc_info=True)

    def _create_new_persona(self):
        name, ok = QInputDialog.getText(self, "Create New Persona", "Enter a name for the new persona:")
        if not (ok and name and name.strip()): return

        safe_id = re.sub(r'[\s\-]+', '_', name.strip()).lower()
        safe_id = re.sub(r'[^\w_]', '', safe_id)
        if not safe_id: safe_id = "new_persona"
        
        file_name = f"{safe_id}"
        
        new_path = os.path.join(get_base_path(), "assets", "ai_personas", f"{file_name}.py")
        if os.path.exists(new_path):
            QMessageBox.warning(self, "File Exists", f"A persona file named '{file_name}.py' already exists.")
            return

        initial_content = PERSONA_TEMPLATE.format(
            file_name=file_name,
            name=name,
            title="Custom Persona",
            expertise="User-defined expertise",
            description=f"A custom persona named {name}.",
            system_prompt_logic="You are a helpful AI assistant. Your goal is to provide clear, concise, and actionable advice based on the user's request."
        )

        try:
            with open(new_path, 'w', encoding='utf-8') as f:
                f.write(initial_content)
            
            self._discover_and_populate_personas()
            for i in range(self.persona_list.count()):
                if self.persona_list.item(i).data(Qt.ItemDataRole.UserRole) == file_name:
                    self.persona_list.setCurrentRow(i)
                    break
        except Exception as e:
            QMessageBox.critical(self, "Creation Failed", f"Could not create new persona file: {e}")
            log.error(f"Failed creating persona: {e}", exc_info=True)

    def _delete_selected_persona(self):
        item = self.persona_list.currentItem()
        if not item: return

        reply = QMessageBox.question(self, "Confirm Delete",
            f"Are you sure you want to permanently delete the '{item.text()}' persona?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.No)

        if reply == QMessageBox.StandardButton.Yes:
            persona_id = item.data(Qt.ItemDataRole.UserRole)
            persona_file = os.path.join(get_base_path(), "assets", "ai_personas", f"{persona_id}.py")
            try:
                os.remove(persona_file)
                self._discover_and_populate_personas()
                if self.persona_list.count() > 0:
                    self.persona_list.setCurrentRow(0)
                else:
                    self._set_editor_state(enabled=False)

            except Exception as e:
                QMessageBox.critical(self, "Deletion Failed", f"Could not delete persona file: {e}")
                log.error(f"Could not delete {persona_file}: {e}", exc_info=True)
                
    def _populate_rules_presets(self):
        current_id = None
        if current_item := self.rules_preset_list.currentItem():
            current_id = current_item.data(Qt.ItemDataRole.UserRole)
        
        self.rules_preset_list.clear()
        self.preset_manager.presets = self.preset_manager.load_presets()
        for preset_id, preset_name in self.preset_manager.get_preset_names_for_ui():
            item = QListWidgetItem(preset_name)
            item.setData(Qt.ItemDataRole.UserRole, preset_id)
            self.rules_preset_list.addItem(item)
            
        if current_id:
            for i in range(self.rules_preset_list.count()):
                if self.rules_preset_list.item(i).data(Qt.ItemDataRole.UserRole) == current_id:
                    self.rules_preset_list.setCurrentRow(i)
                    break
            
    def _on_preset_selected(self, item: QListWidgetItem):
        self.rules_list_widget.clear()
        if not item:
            self.rules_group_box.setEnabled(False)
            self.preset_desc_label.setText("<i>Select a preset to edit its rules.</i>")
            return
            
        self.rules_group_box.setEnabled(True)
        preset_id = item.data(Qt.ItemDataRole.UserRole)
        preset_data = self.preset_manager.presets.get(preset_id, {})
        
        self.rules_group_box.setTitle(preset_data.get("name", "Unnamed Preset"))
        self.preset_desc_label.setText(preset_data.get("description", "No description."))
        
        for rule in preset_data.get("rules", []):
            self.rules_list_widget.addItem(QListWidgetItem(rule))

    def _create_new_preset(self):
        name, ok = QInputDialog.getText(self, "New Preset", "Enter a name for the new style preset:")
        if not (ok and name and name.strip()): return
            
        preset_id = re.sub(r'[\s\-]+', '_', name.strip()).lower()
        preset_id = re.sub(r'[^\w_]', '', preset_id)
        if not preset_id: preset_id = "new_style_preset"
        
        if preset_id in self.preset_manager.presets:
            QMessageBox.warning(self, "Preset Exists", "A preset with that name/ID already exists.")
            return
            
        new_preset_data = {"name": name, "description": "A new custom style preset.", "rules": []}
        if self.preset_manager.save_preset(preset_id, new_preset_data):
            self._populate_rules_presets()
            for i in range(self.rules_preset_list.count()):
                if self.rules_preset_list.item(i).data(Qt.ItemDataRole.UserRole) == preset_id:
                    self.rules_preset_list.setCurrentRow(i)
                    break
                    
    def _delete_selected_preset(self):
        item = self.rules_preset_list.currentItem()
        if not item: return
        
        preset_id = item.data(Qt.ItemDataRole.UserRole)
        reply = QMessageBox.question(self, "Confirm Delete", f"Delete the preset '{item.text()}'?")
        if reply == QMessageBox.StandardButton.Yes:
            if self.preset_manager.delete_preset(preset_id):
                self._populate_rules_presets()
    
    def _add_rule(self):
        text, ok = QInputDialog.getText(self, "Add Rule", "Enter new rule text:")
        if ok and text: self.rules_list_widget.addItem(QListWidgetItem(text))

    def _edit_rule(self):
        item = self.rules_list_widget.currentItem()
        if not item: return
        new_text, ok = QInputDialog.getText(self, "Edit Rule", "Edit rule text:", text=item.text())
        if ok and new_text: item.setText(new_text)

    def _remove_rule(self):
        item = self.rules_list_widget.currentItem()
        if not item: return
        self.rules_list_widget.takeItem(self.rules_list_widget.row(item))

    def _save_current_preset(self):
        item = self.rules_preset_list.currentItem()
        if not item: return
        
        preset_id = item.data(Qt.ItemDataRole.UserRole)
        preset_data = self.preset_manager.presets.get(preset_id)
        if not preset_data: return

        preset_data["rules"] = [self.rules_list_widget.item(i).text() for i in range(self.rules_list_widget.count())]
        
        if self.preset_manager.save_preset(preset_id, preset_data):
            QMessageBox.information(self, "Success", f"Preset '{preset_data['name']}' saved.")
        else:
            QMessageBox.critical(self, "Error", "Failed to save preset.")
                
    def closeEvent(self, event):
        if self.has_unsaved_changes:
            reply = QMessageBox.question(self, "Unsaved Changes",
                                     "You have unsaved changes. Close without saving?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.No:
                event.ignore()
                return
        event.accept()
```

### File: `/plugins/ai_tools/persona_logic.py`
```py
# /plugins/ai_tools/persona_logic.py
import os
from typing import List

def get_files_for_persona(persona_id: str, project_root: str) -> List[str]:
    """
    Gets a list of recommended files to select for a given persona.
    Returns an empty list if no specific logic exists for the persona,
    prompting the UI to select all files by default.
    """
    
    file_list = []
    
    # Logic for "Dr. Anya Sharma" - The Architect
    if persona_id == "anya_the_architect":
        # Architects are interested in high-level structure.
        # Select core application logic, main entry points, and managers.
        patterns = ['main.py', 'app_core/', 'ui/main_window.py', 'plugins/']
        for root, _, files in os.walk(project_root):
            for p in patterns:
                if f"/{p}" in root.replace(project_root, "").replace("\\", "/"):
                    for file in files:
                        if file.endswith('.py'):
                            file_list.append(os.path.join(root, file))

    # Logic for "Sofia Reyes" - The UX Visionary
    elif persona_id == "sofia_the_ux_visionary":
        # UX visionaries focus on the user interface.
        patterns = ['ui/', 'qss', '.css', '.html']
        for root, _, files in os.walk(project_root):
            for file in files:
                if any(p in os.path.join(root, file) for p in patterns) and file.endswith(('.py', '.qss', '.css', '.html')):
                     file_list.append(os.path.join(root, file))

    # Logic for "Glitch" - The QA Maverick
    elif persona_id == "glitch_the_qa_maverick":
        # QA needs to see the source code to write tests.
        # Exclude test files themselves to avoid testing the tests.
        for root, dirs, files in os.walk(project_root):
            # Exclude test directories from the walk
            dirs[:] = [d for d in dirs if 'test' not in d.lower()]
            for file in files:
                if file.endswith('.py') and not file.startswith('test_'):
                    file_list.append(os.path.join(root, file))

    # Logic for "Eva the Sentinel" - The Security Expert
    elif persona_id == "eva_the_sentinel":
        # Security needs to see everything that could be an attack vector.
        # This includes requirements, configs, and all source code.
        patterns = ['.py', '.json', 'requirements.txt', '.cfg', '.ini']
        for root, _, files in os.walk(project_root):
             for file in files:
                 if any(file.endswith(p) for p in patterns):
                     file_list.append(os.path.join(root, file))

    # For other personas, return an empty list to indicate no specific preference.
    # The UI will default to selecting all files in this case.
    
    # Return a unique, sorted list of file paths
    return sorted(list(set(file_list)))
```

### File: `/plugins/ai_tools/api_client.py`
```py
# PuffinPyEditor/plugins/ai_tools/api_client.py
import requests
import json
from typing import Dict, Tuple
from utils.logger import log


class ApiClient:
    """A client to interact with various AI model APIs."""

    PROVIDER_CONFIG = {
        "OpenAI": {
            "endpoint": "https://api.openai.com/v1/chat/completions",
            "models": ["gpt-4o", "gpt-4-turbo", "gpt-3.5-turbo"],
        }
        # Other providers like Anthropic or Gemini could be added here
    }

    def __init__(self, settings_manager):
        self.settings_manager = settings_manager

    def get_api_key(self, provider: str) -> str | None:
        """Retrieves an API key for a given provider from settings."""
        api_keys = self.settings_manager.get("api_keys", {})
        return api_keys.get(provider)

    def send_request(
        self, provider: str, model: str, system_prompt: str, user_prompt: str
    ) -> Tuple[bool, str]:
        """
        Sends a request to the specified AI provider.

        Returns a tuple: (success: bool, response_content: str)
        """
        api_key = self.get_api_key(provider)
        if not api_key:
            msg = (
                f"API Key for {provider} not found. Please configure it in "
                "the settings."
            )
            return False, msg

        config = self.PROVIDER_CONFIG.get(provider)
        if not config:
            return False, f"Configuration for provider '{provider}' not found."

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "max_tokens": 4096,
        }

        try:
            log.info(f"Sending request to {provider} model {model}...")
            response = requests.post(
                config["endpoint"],
                headers=headers,
                data=json.dumps(payload),
                timeout=120  # 2-minute timeout
            )
            response.raise_for_status()

            data = response.json()
            content = data['choices'][0]['message']['content']
            log.info("Successfully received response from AI.")
            return True, content.strip()

        except requests.exceptions.RequestException as e:
            error_message = f"API request failed: {e}"
            if e.response is not None:
                error_message += f"\nResponse: {e.response.text}"
            log.error(error_message)
            return False, error_message
        except (KeyError, IndexError) as e:
            error_message = f"Failed to parse AI response: {e}"
            log.error(f"{error_message}\nFull Response: {response.text}")
            return False, error_message
        except Exception as e:
            error_message = f"An unexpected error occurred: {e}"
            log.error(error_message)
            return False, error_message
```

### File: `/plugins/ai_tools/ai_response_dialog.py`
```py
# PuffinPyEditor/plugins/ai_tools/ai_response_dialog.py
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QTextEdit, QDialogButtonBox, QPushButton,
    QApplication
)
import qtawesome as qta


class AIResponseDialog(QDialog):
    """A dialog to display the response from an AI model."""
    def __init__(self, response_text: str, parent=None):
        super().__init__(parent)
        self.response_text = response_text
        self.setWindowTitle("AI Response")
        self.setMinimumSize(700, 500)
        self.setObjectName("AIResponseDialog")

        self.layout = QVBoxLayout(self)

        self.text_edit = QTextEdit()
        self.text_edit.setMarkdown(self.response_text)
        self.text_edit.setReadOnly(True)
        self.layout.addWidget(self.text_edit)

        self.button_box = QDialogButtonBox()
        self.copy_button = QPushButton(
            qta.icon('fa5s.copy'), "Copy to Clipboard"
        )
        self.button_box.addButton(
            self.copy_button, QDialogButtonBox.ButtonRole.ActionRole
        )
        self.button_box.addButton(QDialogButtonBox.StandardButton.Close)
        self.layout.addWidget(self.button_box)

        self.copy_button.clicked.connect(self._copy_to_clipboard)
        self.button_box.rejected.connect(self.reject)

    def _copy_to_clipboard(self):
        """Copies the response text to the system clipboard."""
        QApplication.clipboard().setText(self.response_text)
        self.copy_button.setText("Copied!")
        self.copy_button.setEnabled(False)
```

### File: `/plugins/ai_tools/ai_export_dialog.py`
```py
# PuffinPyEditor/plugins/ai_tools/ai_export_dialog.py
import os
import sys
import json
import importlib.util
from typing import List, Dict, Optional, Any, Tuple
from datetime import datetime
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QSplitter, QWidget, QGroupBox,
    QTreeView, QTextEdit, QPushButton, QDialogButtonBox, QMessageBox,
    QComboBox, QProgressDialog, QApplication, QCheckBox, QLabel, QToolButton
)
from PyQt6.QtGui import QStandardItemModel, QStandardItem, QCursor
from PyQt6.QtCore import Qt, QCoreApplication

import qtawesome as qta

from app_core.puffin_api import PuffinPluginAPI
from app_core.settings_manager import settings_manager
from app_core.project_manager import ProjectManager
from app_core.linter_manager import LinterManager
from app_core import golden_rules
from utils.logger import log
from utils.helpers import get_base_path
from .api_client import ApiClient
from .ai_response_dialog import AIResponseDialog
from .persona_manager_dialog import PersonaManagerDialog
from .style_preset_manager import StylePresetManager
from .persona_logic import get_files_for_persona


class AIExportDialog(QDialog):
    """
    A dialog for selecting an AI Persona and exporting a project's context.
    """

    def __init__(self, project_path: str, puffin_api: PuffinPluginAPI, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.api = puffin_api
        self.project_path = project_path
        self.project_manager = self.api.get_manager("project")
        self.linter_manager = self.api.get_manager("linter")
        self.api_client = ApiClient(settings_manager)
        self.preset_manager = StylePresetManager()

        self.personas: Dict[str, Dict] = {}
        self.persona_modules: Dict[str, Any] = {}

        self.selected_files: List[str] = []
        self._is_updating_checks = False

        self.setWindowTitle("AI Task Manager")
        self.setMinimumSize(950, 700)
        self.setObjectName("AIExportDialog")

        self._setup_ui()
        self._connect_signals()
        self._populate_file_tree()
        self._load_and_populate_personas()
        self._populate_style_presets()

    def _setup_ui(self):
        self.main_layout = QVBoxLayout(self)
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        self.main_layout.addWidget(self.splitter, 1)
        self._create_left_pane()
        self._create_right_pane()
        self.splitter.setSizes([350, 600])

        bottom_options_layout = QHBoxLayout()
        api_context_group = QGroupBox("Execution & Context")
        api_context_layout = QVBoxLayout(api_context_group)
        api_mode_layout = QHBoxLayout()
        self.api_mode_checkbox = QCheckBox("Enable API Mode")
        self.api_mode_checkbox.setToolTip("Send context directly to an AI API instead of exporting a file.")
        api_mode_layout.addWidget(self.api_mode_checkbox)
        api_mode_layout.addStretch()
        api_context_layout.addLayout(api_mode_layout)

        self.api_controls_widget = QWidget()
        api_controls_layout = QHBoxLayout(self.api_controls_widget)
        api_controls_layout.setContentsMargins(0, 5, 0, 0)
        api_controls_layout.addWidget(QLabel("Provider:"))
        self.api_provider_combo = QComboBox()
        api_controls_layout.addWidget(self.api_provider_combo)
        api_controls_layout.addWidget(QLabel("Model:"))
        self.api_model_combo = QComboBox()
        api_controls_layout.addWidget(self.api_model_combo)
        api_context_layout.addWidget(self.api_controls_widget)

        self.include_linter_checkbox = QCheckBox("Include linter issues")
        self.include_linter_checkbox.setChecked(True)
        self.include_linter_checkbox.setToolTip("Include linter analysis in the context.")
        api_context_layout.addWidget(self.include_linter_checkbox)
        api_context_layout.addStretch()
        bottom_options_layout.addWidget(api_context_group)

        self.export_options_group = QGroupBox("File Export Options")
        export_layout = QVBoxLayout(self.export_options_group)
        format_layout = QHBoxLayout()
        format_layout.addWidget(QLabel("Format:"))
        self.format_combo = QComboBox()
        self.format_combo.addItems(["AI-Optimized", "Standard Markdown"])
        self.format_combo.setToolTip("Choose export format. 'AI-Optimized' is cleaner for models.")
        format_layout.addWidget(self.format_combo)
        export_layout.addLayout(format_layout)
        export_layout.addStretch()
        bottom_options_layout.addWidget(self.export_options_group)

        self.main_layout.addLayout(bottom_options_layout)
        self.button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        self.ok_button = self.button_box.button(QDialogButtonBox.StandardButton.Ok)
        self.main_layout.addWidget(self.button_box)
        self._init_providers_and_models()
        self._toggle_api_mode(self.api_mode_checkbox.isChecked())

    def _create_left_pane(self):
        left_pane = QWidget()
        layout = QVBoxLayout(left_pane)
        self.splitter.addWidget(left_pane)

        persona_group = QGroupBox("1. Select AI Persona (Optional)")
        persona_layout = QVBoxLayout(persona_group)
        persona_selection_layout = QHBoxLayout()
        self.persona_combo = QComboBox()
        persona_selection_layout.addWidget(self.persona_combo, 1)
        self.manage_personas_button = QPushButton("Manage...")
        self.manage_personas_button.setIcon(qta.icon('fa5s.cog'))
        self.manage_personas_button.setToolTip("Create, edit, or delete AI Personas")
        persona_selection_layout.addWidget(self.manage_personas_button)
        persona_layout.addLayout(persona_selection_layout)
        self.persona_desc_label = QLabel("<i>Select a persona to see their expertise.</i>")
        self.persona_desc_label.setWordWrap(True)
        persona_layout.addWidget(self.persona_desc_label)
        layout.addWidget(persona_group)

        files_group = QGroupBox("2. Select Files to Include")
        files_layout = QVBoxLayout(files_group)
        actions_layout = QHBoxLayout()
        self.expand_all_button = QToolButton(icon=qta.icon('fa5s.angle-double-down', color='grey'), toolTip="Expand all folders.")
        self.collapse_all_button = QToolButton(icon=qta.icon('fa5s.angle-double-up', color='grey'), toolTip="Collapse all folders.")
        self.toggle_select_button = QToolButton()
        for button in [self.expand_all_button, self.collapse_all_button, self.toggle_select_button]:
            button.setAutoRaise(True)
        actions_layout.addWidget(self.expand_all_button)
        actions_layout.addWidget(self.collapse_all_button)
        actions_layout.addStretch()
        actions_layout.addWidget(self.toggle_select_button)
        files_layout.addLayout(actions_layout)
        self.file_tree = QTreeView()
        self.file_tree.setHeaderHidden(True)
        self.file_model = QStandardItemModel()
        self.file_tree.setModel(self.file_model)
        files_layout.addWidget(self.file_tree)
        layout.addWidget(files_group, 1)

    def _create_right_pane(self):
        right_pane = QWidget()
        layout = QVBoxLayout(right_pane)
        self.splitter.addWidget(right_pane)

        goal_group = QGroupBox("3. Define Primary Goal (Optional)")
        goal_layout = QVBoxLayout(goal_group)
        self.user_goal_edit = QTextEdit()
        self.user_goal_edit.setPlaceholderText(
            "Leave blank for a general review based on the selected persona's expertise. Or, provide a specific goal, e.g., 'Refactor the database logic in file_handler.py' or 'Add a new endpoint to fetch user profiles'.")
        goal_layout.addWidget(self.user_goal_edit, 1)
        layout.addWidget(goal_group, 1)

        rules_group = QGroupBox("4. Select Style Preset")
        rules_layout = QVBoxLayout(rules_group)
        self.rules_combo = QComboBox()
        self.rules_combo.setToolTip("Select a set of stylistic rules for the AI.")
        rules_layout.addWidget(self.rules_combo)
        layout.addWidget(rules_group)

        layout.addStretch(1)

    def _connect_signals(self):
        self.button_box.accepted.connect(self._start_export)
        self.button_box.rejected.connect(self.reject)
        self.file_model.itemChanged.connect(self._on_item_changed)
        self.expand_all_button.clicked.connect(self.file_tree.expandAll)
        self.collapse_all_button.clicked.connect(self.file_tree.collapseAll)
        self.toggle_select_button.clicked.connect(self._on_toggle_select_clicked)
        self.persona_combo.currentIndexChanged.connect(self._on_persona_selected)
        self.api_mode_checkbox.toggled.connect(self._toggle_api_mode)
        self.api_provider_combo.currentIndexChanged.connect(self._on_api_provider_changed)
        self.manage_personas_button.clicked.connect(self._open_persona_manager)

    def _init_providers_and_models(self):
        self.api_provider_combo.addItems(self.api_client.PROVIDER_CONFIG.keys())
        self._on_api_provider_changed()

    def _open_persona_manager(self):
        manager_dialog = PersonaManagerDialog(self.api.get_manager("theme"), self)
        manager_dialog.finished.connect(self._load_and_populate_personas)
        manager_dialog.finished.connect(self._populate_style_presets)
        manager_dialog.exec()

    def _toggle_api_mode(self, checked: bool):
        self.api_controls_widget.setVisible(checked)
        self.export_options_group.setVisible(not checked)
        self.ok_button.setText("Send to AI" if checked else "Export")

    def _on_api_provider_changed(self):
        provider = self.api_provider_combo.currentText()
        models = self.api_client.PROVIDER_CONFIG.get(provider, {}).get("models", [])
        self.api_model_combo.clear()
        self.api_model_combo.addItems(models)

    def _set_all_check_states(self, state: Qt.CheckState):
        self._is_updating_checks = True
        root = self.file_model.invisibleRootItem()
        for i in range(root.rowCount()):
            self._recursive_set_state(root.child(i), state)
        self._is_updating_checks = False
        self._update_toggle_button_state()

    def _recursive_set_state(self, item: QStandardItem, state: Qt.CheckState):
        if item.isCheckable() and item.checkState() != state:
            item.setCheckState(state)
        for i in range(item.rowCount()):
            self._recursive_set_state(item.child(i), state)

    def _on_toggle_select_clicked(self):
        new_state = Qt.CheckState.Unchecked if self._are_all_items_checked() else Qt.CheckState.Checked
        self._set_all_check_states(new_state)

    def _on_item_changed(self, item: QStandardItem):
        if self._is_updating_checks: return
        self._is_updating_checks = True
        self._update_descendants(item)
        self._update_ancestors(item)
        self._is_updating_checks = False
        self._update_toggle_button_state()

    def _update_descendants(self, item: QStandardItem):
        state = item.checkState()
        if state == Qt.CheckState.PartiallyChecked: return
        for i in range(item.rowCount()):
            self._recursive_set_state(item.child(i), state)

    def _update_ancestors(self, item: QStandardItem):
        parent = item.parent()
        while parent:
            child_states = {parent.child(i).checkState() for i in range(parent.rowCount())}
            new_state = Qt.CheckState.Unchecked
            if all(s == Qt.CheckState.Checked for s in child_states):
                new_state = Qt.CheckState.Checked
            elif any(s != Qt.CheckState.Unchecked for s in child_states):
                new_state = Qt.CheckState.PartiallyChecked
            if parent.checkState() != new_state:
                parent.setCheckState(new_state)
            parent = parent.parent()

    def _get_all_checkable_items(self) -> List[QStandardItem]:
        items = []
        root = self.file_model.invisibleRootItem()
        stack = [root.child(i) for i in range(root.rowCount())]
        while stack:
            item = stack.pop()
            if item and item.isCheckable():
                items.append(item)
                stack.extend(item.child(i) for i in range(item.rowCount()))
        return items

    def _are_all_items_checked(self) -> bool:
        items = self._get_all_checkable_items()
        if not items: return False
        return all(item.checkState() == Qt.CheckState.Checked for item in items)

    def _update_toggle_button_state(self):
        if self._are_all_items_checked():
            self.toggle_select_button.setIcon(qta.icon('fa5s.check-square', color='grey'))
            self.toggle_select_button.setToolTip("Deselect all.")
        else:
            self.toggle_select_button.setIcon(qta.icon('fa5.square', color='grey'))
            self.toggle_select_button.setToolTip("Select all.")

    def _populate_file_tree(self):
        self.file_model.clear()
        root_node = self.file_model.invisibleRootItem()
        path_map = {self.project_path: root_node}
        ignore_dirs = {'__pycache__', '.git', 'venv', '.venv', 'dist', 'build', 'logs', 'ai_exports'}
        ignore_files = {'puffin_editor_settings.json'}
        include_extensions = ['.py', '.md', '.txt', '.json', '.html', '.css', '.js', '.yml', '.bat', '.qss']

        for dirpath, dirnames, filenames in os.walk(self.project_path, topdown=True):
            dirnames[:] = [d for d in dirnames if d not in ignore_dirs]
            parent_node = path_map.get(os.path.normpath(dirpath))
            if parent_node is None: continue

            for dirname in sorted(dirnames):
                dir_item = QStandardItem(dirname)
                dir_item.setIcon(qta.icon('fa5.folder', color='grey'))
                dir_item.setCheckable(True)
                path = os.path.join(dirpath, dirname)
                dir_item.setData(path, Qt.ItemDataRole.UserRole)
                parent_node.appendRow(dir_item)
                path_map[path] = dir_item

            for filename in sorted(filenames):
                if filename in ignore_files or not any(filename.lower().endswith(ext) for ext in include_extensions) and "LICENSE" not in filename:
                    continue
                file_item = QStandardItem(filename)
                file_item.setIcon(qta.icon('fa5.file-alt', color='grey'))
                file_item.setCheckable(True)
                path = os.path.join(dirpath, filename)
                file_item.setData(path, Qt.ItemDataRole.UserRole)
                parent_node.appendRow(file_item)

        self._set_all_check_states(Qt.CheckState.Checked)
        self.file_tree.collapseAll()

    def _get_checked_files(self) -> List[str]:
        files = []
        for item in self._get_all_checkable_items():
            if item.checkState() == Qt.CheckState.Checked:
                path = item.data(Qt.ItemDataRole.UserRole)
                if path and os.path.isfile(path):
                    files.append(path)
        return files

    def _load_and_populate_personas(self):
        current_selection_id = self.persona_combo.currentData()
        self.personas.clear(); self.persona_modules.clear(); self.persona_combo.clear()
        self.persona_combo.addItem("No Persona (General Review)", None)
        persona_dir = os.path.join(get_base_path(), "assets", "ai_personas")
        if not os.path.isdir(persona_dir):
            log.warning(f"AI Persona directory not found: {persona_dir}")
            return

        for filename in sorted(os.listdir(persona_dir)):
            if filename.endswith(".py") and not filename.startswith("__"):
                module_path = os.path.join(persona_dir, filename)
                module_name = f"assets.ai_personas.{os.path.splitext(filename)[0]}"
                try:
                    spec = importlib.util.spec_from_file_location(module_name, module_path)
                    if spec and spec.loader:
                        module = importlib.util.module_from_spec(spec)
                        if module_name in sys.modules:
                            del sys.modules[module_name]
                        sys.modules[module_name] = module
                        spec.loader.exec_module(module)
                        if hasattr(module, "get_persona_info"):
                            info = module.get_persona_info()
                            self.personas[info['id']] = info
                            self.persona_modules[info['id']] = module
                            self.persona_combo.addItem(f"{info['name']} - {info['title']}", info['id'])
                except Exception as e:
                    log.error(f"Failed to load AI persona '{filename}': {e}", exc_info=True)

        index_to_select = self.persona_combo.findData(current_selection_id)
        self.persona_combo.setCurrentIndex(index_to_select if index_to_select != -1 else 0)

    def _populate_style_presets(self):
        self.rules_combo.clear()
        self.preset_manager.presets = self.preset_manager.load_presets()
        for preset_id, preset_name in self.preset_manager.get_preset_names_for_ui():
            self.rules_combo.addItem(preset_name, preset_id)

    def _on_persona_selected(self, index: int):
        persona_id = self.persona_combo.itemData(index)

        if not persona_id:
            self.persona_desc_label.setText("<i>A general-purpose review will be performed using a standard prompt. All files are selected by default.</i>")
            self._set_all_check_states(Qt.CheckState.Checked)
            return

        if persona_info := self.personas.get(persona_id):
            self.persona_desc_label.setText(f"<b>Expertise:</b> {persona_info.get('expertise', 'N/A')}")

        files_to_select = get_files_for_persona(persona_id, self.project_path)
        if not files_to_select:
            self._set_all_check_states(Qt.CheckState.Checked)
            return

        self._set_all_check_states(Qt.CheckState.Unchecked)
        self._is_updating_checks = True
        for item in self._get_all_checkable_items():
            path = item.data(Qt.ItemDataRole.UserRole)
            if path in files_to_select:
                item.setCheckState(Qt.CheckState.Checked)
                self._update_ancestors(item)
        self._is_updating_checks = False
        self._update_toggle_button_state()

    def _build_prompt(self, user_goal: str, files: List[str], problems: Dict[str, List[Dict]]) -> Optional[Tuple[str, str]]:
        persona_id = self.persona_combo.currentData()
        style_preset_id = self.rules_combo.currentData()
        style_rules = []
        if style_preset_id and (preset := self.preset_manager.presets.get(style_preset_id)):
            style_rules = preset.get("rules", [])

        context = {
            "user_instructions": user_goal,
            "file_tree": self._generate_file_tree_text(files),
            "file_contents": {path: self._read_file(path) for path in files},
            "linter_results": problems,
            "project_root": self.project_path,
            "golden_rules": golden_rules.get_golden_rules_text().splitlines(),
            "style_rules": style_rules
        }

        if not persona_id:
            system_prompt = "You are a helpful and experienced software developer. Your goal is to perform a general code review based on the user's instructions and the provided files. Offer concrete suggestions for improvement."
            file_contents_section = []
            for path, content in context["file_contents"].items():
                relative_path = os.path.relpath(path, context["project_root"]).replace(os.sep, '/')
                lang = os.path.splitext(path)[1].lstrip('.') or 'text'
                file_contents_section.append(f"### File: `/{relative_path}`\n```{lang}\n{content}\n```")
            file_contents_str = "\n\n".join(file_contents_section)

            user_prompt = f"""
# Project Review Request

**User's Goal:**
{context.get("user_instructions") or "Perform a general review of the provided code."}

---
**Project File Tree:**
```
{context.get("file_tree", "No file tree provided.")}
```
---
**Files for Review:**
{file_contents_str}
"""
            return system_prompt.strip(), user_prompt.strip()

        if module := self.persona_modules.get(persona_id):
            try:
                persona_instance = module.get_persona_instance()
                return persona_instance.generate_prompt(context)
            except Exception as e:
                log.error(f"Error in prompt generation for '{persona_id}': {e}", exc_info=True)
                QMessageBox.critical(self, "Prompt Generation Error", f"Could not generate prompt: {e}")
                return None

        log.error(f"Could not load module for selected persona ID: {persona_id}")
        QMessageBox.critical(self, "Error", "The selected AI persona could not be loaded.")
        return None

    def _read_file(self, file_path: str) -> str:
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                return f.read()
        except Exception as e:
            return f"[Error reading file: {e}]"

    def _generate_file_tree_text(self, files: List[str]) -> str:
        tree, base_path = {}, self.project_path
        for f in files:
            rel_path = os.path.relpath(f, base_path).replace(os.sep, '/')
            parts, curr = rel_path.split('/'), tree
            for part in parts[:-1]: curr = curr.setdefault(part, {})
            curr[parts[-1]] = None

        def build_string(d, indent=''):
            s, items = '', sorted(d.items())
            for i, (key, val) in enumerate(items):
                is_last = i == len(items) - 1
                s += f"{indent}{'└── ' if is_last else '├── '}{key}\n"
                if val is not None: s += build_string(val, f"{indent}{'    ' if is_last else '│   '}")
            return s
        return f"/{os.path.basename(base_path)}\n{build_string(tree, ' ')}"

    def _start_export(self):
        self.ok_button.setEnabled(False)
        self.selected_files = self._get_checked_files()
        if not self.selected_files:
             QMessageBox.warning(self, "No Files Selected", "No files are checked. Please select at least one file.")
             self.ok_button.setEnabled(True)
             return

        self.progress = QProgressDialog("Linting selected files...", "Cancel", 0, 0, self)
        self.progress.setWindowModality(Qt.WindowModality.WindowModal)
        self.progress.show()
        QCoreApplication.processEvents()

        try: self.linter_manager.project_lint_results_ready.disconnect(self._on_lint_complete)
        except TypeError: pass
        self.linter_manager.project_lint_results_ready.connect(self._on_lint_complete)
        self.linter_manager.lint_project(self.project_path)

    def _on_lint_complete(self, all_problems: Dict[str, List[Dict]]):
        if self.progress.wasCanceled():
            self.ok_button.setEnabled(True)
            return

        self.progress.setLabelText("Preparing context...")
        QCoreApplication.processEvents()

        user_goal = self.user_goal_edit.toPlainText().strip()
        selected_problems = {k: v for k, v in all_problems.items() if self.include_linter_checkbox.isChecked() and k in self.selected_files}
        prompt_data = self._build_prompt(user_goal, self.selected_files, selected_problems)

        if not prompt_data:
            self.progress.close()
            self.ok_button.setEnabled(True)
            return

        system_prompt, user_prompt = prompt_data

        if self.api_mode_checkbox.isChecked():
            self.progress.setLabelText("Sending to AI...")
            self._handle_api_request(system_prompt, user_prompt)
        else:
            self.progress.setLabelText("Saving file...")
            self._handle_file_export(system_prompt, user_prompt)

        if not self.progress.wasCanceled():
            self.progress.close()

        self.ok_button.setEnabled(True)
        try:
            self.linter_manager.project_lint_results_ready.disconnect(self._on_lint_complete)
        except TypeError:
            pass # Already disconnected

    def _handle_api_request(self, system_prompt: str, user_prompt: str):
        QApplication.setOverrideCursor(QCursor(Qt.CursorShape.WaitCursor))
        try:
            provider, model = self.api_provider_combo.currentText(), self.api_model_combo.currentText()
            success, response = self.api_client.send_request(provider, model, system_prompt, user_prompt)
            if success:
                AIResponseDialog(response, self).exec()
                self.accept()
            else:
                QMessageBox.critical(self, "API Error", response)
        finally:
            QApplication.restoreOverrideCursor()

    def _handle_file_export(self, system_prompt: str, user_prompt: str):
        export_dir = os.path.join(get_base_path(), "ai_exports")
        os.makedirs(export_dir, exist_ok=True)
        proj_name = os.path.basename(self.project_path)
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        persona_name = self.persona_combo.currentText().split(' - ')[0].replace(' ', '_')
        output_filepath = os.path.join(export_dir, f"{proj_name}_{persona_name}_{timestamp}.md")
        QApplication.setOverrideCursor(QCursor(Qt.CursorShape.WaitCursor))
        try:
            # Using triple quotes correctly for the main content block
            content = f"""# AI Task: {self.persona_combo.currentText()}
## Timestamp: {datetime.now().isoformat()}

---SYSTEM-PROMPT---

{system_prompt}

---USER-PROMPT---

{user_prompt}
"""
            with open(output_filepath, 'w', encoding='utf-8') as f: f.write(content)
            QMessageBox.information(self, "Export Complete", f"Project context exported to:\n{output_filepath}")
            self.accept()
        except Exception as e:
            log.error(f"Export failed: {e}", exc_info=True)
            QMessageBox.critical(self, "Export Failed", f"An error occurred: '{e}'")
        finally:
            QApplication.restoreOverrideCursor()
```

### File: `/plugins/ai_tools/__init__.py`
```py

```

### File: `/plugins/ai_quick_actions/plugin_main.py`
```py
# PuffinPyEditor/plugins/ai_quick_actions/plugin_main.py
from functools import partial
from PyQt6.QtWidgets import QMessageBox
from PyQt6.QtCore import QObject, QRunnable, QThreadPool, pyqtSignal
from app_core.puffin_api import PuffinPluginAPI
from plugins.ai_tools.api_client import ApiClient
from plugins.ai_tools.ai_response_dialog import AIResponseDialog

class AIWorker(QRunnable):
    class Signals(QObject):
        finished = pyqtSignal(bool, str)

    def __init__(self, api_client, provider, model, system_prompt, user_prompt):
        super().__init__()
        self.api_client, self.provider, self.model = api_client, provider, model
        self.system_prompt, self.user_prompt = system_prompt, user_prompt
        self.signals = self.Signals()

    def run(self):
        success, response = self.api_client.send_request(
            self.provider, self.model, self.system_prompt, self.user_prompt)
        self.signals.finished.emit(success, response)

class AIQuickActionsPlugin:
    ACTIONS = [{"name": "Explain this code", "icon": "fa5s.question-circle", "system": "You are an expert developer. Explain the following code snippet clearly and concisely. Describe its purpose, inputs, and outputs.", "user": "Please explain this code:\n\n```python\n{selected_code}\n```"}, {"name": "Suggest a refactoring", "icon": "fa5s.magic", "system": "You are a senior developer focused on writing clean, efficient, and maintainable Python code. Refactor the following code snippet, explaining the key improvements you made.", "user": "Please refactor this code:\n\n```python\n{selected_code}\n```"}, {"name": "Find potential bugs", "icon": "fa5s.bug", "system": "You are a quality assurance expert. Analyze the following code for potential bugs, logical errors, or edge cases that might not be handled correctly.", "user": "Please find potential bugs in this code:\n\n```python\n{selected_code}\n```"}]

    def __init__(self, puffin_api: PuffinPluginAPI):
        self.api = puffin_api
        self.main_window = self.api.get_main_window()
        settings = self.api.get_manager("settings")
        self.api_client = ApiClient(settings)
        self.thread_pool = QThreadPool()

        for config in self.ACTIONS:
            self.api.add_menu_action(
                "ai", config["name"], partial(self._run_action, config), icon_name=config["icon"])

    def _run_action(self, config):
        editor = self.main_window.tab_widget.currentWidget()
        if not hasattr(editor, 'text_area'):
            self.api.show_message("info", "No Editor", "Please open a file in an editor tab to use AI actions.")
            return

        text = editor.text_area.textCursor().selectedText()
        if not text:
            self.api.show_message("info", "No Text Selected", "Please select some code to use this AI action.")
            return

        provider = "OpenAI"
        if not self.api_client.get_api_key(provider):
            QMessageBox.warning(self.main_window, "API Key Missing",
                                f"API Key for {provider} not found. Please add it via Tools -> Manage API Keys...")
            return

        model = self.api_client.PROVIDER_CONFIG.get(provider, {}).get("models", [])[0]
        self.api.show_status_message(f"Sending selection to {model}...")
        worker = AIWorker(self.api_client, provider, model, config["system"], config["user"].format(selected_code=text))
        worker.signals.finished.connect(self._on_action_finished)
        self.thread_pool.start(worker)

    def _on_action_finished(self, success, response):
        self.api.show_status_message("AI response received.", 2000)
        if success:
            dialog = AIResponseDialog(response, self.main_window)
            dialog.exec()
        else:
            QMessageBox.critical(self.main_window, "API Error", response)

def initialize(puffin_api: PuffinPluginAPI):
    return AIQuickActionsPlugin(puffin_api)
```

### File: `/plugins/ai_quick_actions/plugin.json`
```json
{
    "id": "ai_quick_actions",
    "name": "AI Quick Actions",
    "author": "PuffinPy Team",
    "version": "1.0.0",
    "description": "Adds AI-powered actions like 'Explain' and 'Refactor' to the editor's context menu.",
    "entry_point": "plugin_main.py"
}
```

### File: `/plugins/ai_quick_actions/__init__.py`
```py

```

### File: `/plugins/ai_patcher/response_parser.py`
```py
# /plugins/ai_patcher/response_parser.py
import os
import re
from typing import Dict, Tuple
from utils.logger import log

def parse_llm_response(response_text: str) -> Dict[str, str]:
    """
    Parses a markdown response from an LLM using a state machine to robustly
    handle file blocks and unassigned code blocks.
    """
    changes: Dict[str, str] = {}
    lines = response_text.splitlines()

    # Define states for the Finite State Machine (FSM)
    STATE_IDLE = 0           # Looking for a header or start of any code block
    STATE_IN_BLOCK = 1       # Inside a ``` code block

    state = STATE_IDLE
    current_path: Optional[str] = None
    current_content: List[str] = []
    unspecified_counter = 0

    header_pattern = re.compile(r"^\s*###\s+File:\s+`?(.*?)`?\s*$")

    i = 0
    while i < len(lines):
        line = lines[i]
        
        if state == STATE_IDLE:
            header_match = header_pattern.match(line)
            is_fence = line.strip().startswith('```')

            if header_match:
                path = header_match.group(1).strip()
                # Find the next line that is a code fence
                j = i + 1
                while j < len(lines) and not lines[j].strip().startswith('```'):
                    j += 1
                
                if j < len(lines): # Opening fence found
                    current_path = path if (path and path != "/") else None
                    if current_path:
                        state = STATE_IN_BLOCK
                        i = j  # Move pointer past the opening fence
                    else:
                        log.warning(f"AI Patcher: Ignoring invalid file path found in header: '{header_match.group(1)}'")
                else: # Header without a block, ignore
                    log.warning(f"AI Patcher: Found file header for '{path}' but no subsequent code block. Ignoring header.")
            
            elif is_fence:
                # Code block without a preceding header
                unspecified_counter += 1
                current_path = f"[UNSPECIFIED_FILE_{unspecified_counter}]"
                state = STATE_IN_BLOCK

        elif state == STATE_IN_BLOCK:
            if line.strip().startswith('```'):
                # Closing fence, end of block
                if current_path:
                    changes[current_path] = "\n".join(current_content)
                    log.info(f"AI Patcher: Parsed block for '{current_path}'.")
                
                # Reset for next block
                state = STATE_IDLE
                current_path = None
                current_content = []
            else:
                current_content.append(line)
        
        i += 1

    # If the response ends with an unterminated block, save what we have.
    if state == STATE_IN_BLOCK and current_path:
        log.warning(f"AI Patcher: Response ended with an unterminated code block for '{current_path}'. Including content.")
        changes[current_path] = "\n".join(current_content)
        
    return changes

def apply_changes_to_project(project_root: str, changes: Dict[str, str]) -> Tuple[bool, str]:
    """
    Applies the parsed changes to the files in the project directory.

    Args:
        project_root: The absolute path to the root of the project.
        changes: A dictionary mapping relative file paths to their new content.

    Returns:
        A tuple (success, message).
    """
    if not project_root or not os.path.isdir(project_root):
        return False, "Invalid project root directory."

    if not changes:
        return False, "No file changes were found to apply."

    errors = []
    success_count = 0

    for rel_path, content in changes.items():
        # Skip unspecified files that may have been parsed but not assigned a path.
        if rel_path.startswith("[UNSPECIFIED_FILE_"):
            log.warning(f"AI Patcher: Skipped applying unassigned content block '{rel_path}'.")
            continue
            
        clean_rel_path = rel_path.lstrip('/').lstrip('\\')
        abs_path = os.path.join(project_root, clean_rel_path)

        if not os.path.abspath(abs_path).startswith(os.path.abspath(project_root)):
            msg = f"Skipped unsafe path: '{rel_path}' resolves outside the project directory."
            log.error(f"AI Patcher: {msg}")
            errors.append(msg)
            continue

        try:
            os.makedirs(os.path.dirname(abs_path), exist_ok=True)
            with open(abs_path, 'w', encoding='utf-8') as f:
                f.write(content)
            success_count += 1
            log.info(f"AI Patcher: Successfully updated '{abs_path}'.")

        except IOError as e:
            msg = f"Failed to write to '{abs_path}': {e}"
            log.error(f"AI Patcher: {msg}")
            errors.append(msg)
        except Exception as e:
            msg = f"An unexpected error occurred for '{abs_path}': {e}"
            log.error(f"AI Patcher: {msg}", exc_info=True)
            errors.append(msg)

    final_message = f"Successfully updated {success_count} file(s)."
    if errors:
        final_message += "\n\nEncountered the following errors:\n" + "\n".join(f"- {e}" for e in errors)
        return False, final_message

    return True, final_message
```

### File: `/plugins/ai_patcher/plugin_main.py`
```py
# PuffinPyEditor/plugins/ai_patcher/plugin_main.py
from app_core.puffin_api import PuffinPluginAPI
from .patcher_dialog import AIPatcherDialog
from utils.logger import log


class AiPatcherPlugin:
    """Plugin to provide an interactive AI patching tool."""

    def __init__(self, api: PuffinPluginAPI):
        self.api = api
        self.main_window = self.api.get_main_window()
        self.dialog_instance = None

        self.api.add_menu_action(
            menu_name="tools",
            text="AI Patcher...",
            callback=self.show_patcher_dialog,
            icon_name="mdi.auto-fix"
        )
        log.info("AI Patcher plugin initialized and menu action added.")

    def show_patcher_dialog(self):
        """
        Creates and shows the AI Patcher dialog. If an instance already exists,
        it is shown and raised to the front. This prevents a RuntimeError
        from trying to access a deleted dialog object.
        """
        project_manager = self.api.get_manager("project")
        if not project_manager or not project_manager.is_project_open():
            self.api.show_message(
                "info", "No Project Open",
                "Please open a project folder to use the AI Patcher."
            )
            return

        # If the dialog doesn't exist or its underlying C++ object has been deleted, create a new one.
        if self.dialog_instance is None:
            self.dialog_instance = AIPatcherDialog(self.api, self.main_window)
            log.info("Creating new AI Patcher dialog instance.")
        
        try:
            # Check if the window handle is still valid. If not, it was closed and deleted.
            self.dialog_instance.isHidden() 
        except (RuntimeError, AttributeError):
            self.dialog_instance = AIPatcherDialog(self.api, self.main_window) # Re-create if deleted
            log.info("Re-creating AI Patcher dialog instance as previous one was deleted.")
            
        self.dialog_instance.show()
        self.dialog_instance.raise_()
        self.dialog_instance.activateWindow()

def initialize(puffin_api: PuffinPluginAPI):
    """Entry point for PuffinPyEditor to load the plugin."""
    try:
        return AiPatcherPlugin(puffin_api)
    except Exception as e:
        log.error(f"Failed to initialize AI Patcher Plugin: {e}", exc_info=True)
        return None
```

### File: `/plugins/ai_patcher/plugin.json`
```json
{
    "id": "ai_patcher",
    "name": "AI Patcher",
    "author": "PuffinPy Team",
    "version": "2.0.0",
    "description": "A multi-step tool to generate prompts, parse AI responses, and visually review and apply code changes to the project.",
    "entry_point": "plugin_main.py",
    "dependencies": {}
}
```

### File: `/plugins/ai_patcher/patcher_dialog.py`
```py
# /plugins/ai_patcher/patcher_dialog.py
import os
import re
from typing import Dict, List, Optional
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QWidget, QSplitter,
    QTextEdit, QPushButton, QMessageBox, QFrame, QLabel, QListWidget,
    QTreeView, QToolButton, QInputDialog, QSpinBox, QCheckBox,
    QGroupBox, QFormLayout, QLineEdit, QStackedWidget,
    QDialogButtonBox, QListWidgetItem, QApplication, QDockWidget, QMenu
)
from PyQt6.QtGui import QStandardItemModel, QStandardItem, QFont, QCursor, QCloseEvent
from PyQt6.QtCore import Qt, QTimer
import qtawesome as qta
from app_core.puffin_api import PuffinPluginAPI
from app_core.settings_manager import settings_manager
from .response_parser import parse_llm_response, apply_changes_to_project
from utils.logger import log
from utils.helpers import clean_git_conflict_markers, generate_unified_diff

# A simple syntax highlighter for the diff view
from app_core.highlighters.python_syntax_highlighter import PythonSyntaxHighlighter

class DiffViewer(QTextEdit):
    """A simple QTextEdit subclass for displaying unified diffs."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setReadOnly(True)
        self.setFont(QFont("Consolas", 10))
        self.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)

    def set_diff_text(self, diff_text: str):
        # Basic coloring for diffs
        html = ""
        for line in diff_text.splitlines():
            line_html = line.replace("&", "&").replace("<", "<").replace(">", ">")
            if line.startswith('+'):
                html += f'<span style="color: #a7c080;">{line_html}</span><br>'
            elif line.startswith('-'):
                html += f'<span style="color: #e67e80;">{line_html}</span><br>'
            elif line.startswith('@@'):
                html += f'<span style="color: #83c092;">{line_html}</span><br>'
            else:
                html += f'<span>{line_html}</span><br>'
        self.setHtml(f"<pre>{html}</pre>")

class AIPatcherDialog(QDialog):
    """A dialog to generate patch prompts and apply AI-generated code changes."""

    def __init__(self, puffin_api: PuffinPluginAPI, parent=None):
        super().__init__(parent)
        self.api = puffin_api
        self.project_manager = self.api.get_manager("project")
        self.project_root = self.project_manager.get_active_project_path()
        self.parsed_changes: Dict[str, str] = {}
        self.is_updating_checks = False
        self.generated_prompt = ""

        self.setWindowTitle("AI Patcher")
        self.setMinimumSize(1200, 800)
        self.setWindowModality(Qt.WindowModality.NonModal)
        self._setup_ui()
        self._connect_signals()
        self._populate_file_tree()

    def _setup_ui(self):
        self.main_layout = QVBoxLayout(self)
        self.stacked_widget = QStackedWidget()
        self.main_layout.addWidget(self.stacked_widget)
        
        self.stacked_widget.addWidget(self._create_main_split_view())
        self.stacked_widget.addWidget(self._create_completion_page())

        self.button_layout = QHBoxLayout()
        self.copy_prompt_button = QPushButton(qta.icon('fa5s.copy'), "Generate Copy Prompt")
        self.apply_button = QPushButton(qta.icon('fa5s.check'), "Apply Patch")
        self.close_button = QPushButton("Close")
        
        self.button_layout.addWidget(self.copy_prompt_button)
        self.button_layout.addStretch()
        self.button_layout.addWidget(self.apply_button)
        self.button_layout.addWidget(self.close_button)
        self.main_layout.addLayout(self.button_layout)
        
        self.apply_button.setEnabled(False) 

    def _create_main_split_view(self) -> QWidget:
        main_widget = QWidget()
        main_layout = QHBoxLayout(main_widget)
        main_splitter = QSplitter(Qt.Orientation.Horizontal)
        main_layout.addWidget(main_splitter)

        left_pane_widget = QWidget()
        left_pane_layout = QVBoxLayout(left_pane_widget)
        
        instructions_group = QGroupBox("1. AI Instructions & Context")
        instructions_layout = QVBoxLayout(instructions_group)
        self.prompt_edit = QTextEdit()
        self.prompt_edit.setPlaceholderText("Enter the main goal for the AI, e.g., 'Refactor this class...'")
        instructions_layout.addWidget(self.prompt_edit)
        left_pane_layout.addWidget(instructions_group, 1)

        files_group = QGroupBox("2. Select Files to Include")
        files_layout = QVBoxLayout(files_group)
        file_actions_layout = QHBoxLayout()
        self.expand_all_button = QToolButton(icon=qta.icon('fa5s.angle-double-down'), toolTip="Expand All")
        self.collapse_all_button = QToolButton(icon=qta.icon('fa5s.angle-double-up'), toolTip="Collapse All")
        self.toggle_select_button = QToolButton(autoRaise=True)
        file_actions_layout.addWidget(self.expand_all_button)
        file_actions_layout.addWidget(self.collapse_all_button)
        file_actions_layout.addStretch()
        file_actions_layout.addWidget(self.toggle_select_button)
        files_layout.addLayout(file_actions_layout)
        self.file_tree = QTreeView()
        self.file_tree.setHeaderHidden(True)
        self.file_model = QStandardItemModel()
        self.file_tree.setModel(self.file_model)
        files_layout.addWidget(self.file_tree)
        left_pane_layout.addWidget(files_group, 2)
        main_splitter.addWidget(left_pane_widget)

        right_pane_widget = QWidget()
        right_pane_layout = QVBoxLayout(right_pane_widget)
        
        response_group = QGroupBox("3. Paste AI Response")
        response_layout = QVBoxLayout(response_group)
        self.response_edit = QTextEdit()
        self.response_edit.setPlaceholderText("Paste the full markdown response from the AI here.")
        self.response_edit.setFontFamily("Consolas")
        load_button = QPushButton(qta.icon('fa5s.download'), "Load Patch from Text")
        load_button.clicked.connect(self._parse_and_load_review)
        response_layout.addWidget(self.response_edit, 1)
        response_layout.addWidget(load_button, 0, Qt.AlignmentFlag.AlignRight)
        right_pane_layout.addWidget(response_group, 1)

        review_splitter = QSplitter(Qt.Orientation.Horizontal)
        
        changes_group = QGroupBox("Detected Changes")
        changes_layout = QVBoxLayout(changes_group)
        self.changes_list = QListWidget()
        self.changes_list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.changes_list.setStyleSheet("""
            QListWidget::item::indicator {
                width: 15px; height: 15px; border: 1px solid #999;
                border-radius: 4px; background-color: transparent; margin-right: 5px;
            }
            QListWidget::item::indicator:checked { background-color: #66aaff; border-color: #5599ee; }
            QListWidget::item::indicator:disabled { border-color: #666; background-color: #444; }
        """)
        changes_layout.addWidget(self.changes_list)
        review_splitter.addWidget(changes_group)
        
        diff_group = QGroupBox("Diff Preview")
        diff_layout = QVBoxLayout(diff_group)
        self.diff_viewer = DiffViewer()
        diff_layout.addWidget(self.diff_viewer)
        review_splitter.addWidget(diff_group)
        review_splitter.setSizes([250, 450])
        right_pane_layout.addWidget(review_splitter, 2)
        main_splitter.addWidget(right_pane_widget)
        
        main_splitter.setSizes([400, 800])
        return main_widget

    def _create_completion_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.completion_label = QLabel()
        self.completion_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        font = QFont(); font.setPointSize(14)
        self.completion_label.setFont(font)
        
        actions_group = QGroupBox("Next Steps")
        actions_layout = QHBoxLayout(actions_group)
        self.linter_button = QPushButton(qta.icon('mdi.bug-check-outline'), "Run Linter on Changed Files")
        self.source_control_button = QPushButton(qta.icon('mdi.git'), "Open Source Control")
        self.back_to_patcher_button = QPushButton("Back to Patcher")
        
        actions_layout.addWidget(self.linter_button)
        actions_layout.addWidget(self.source_control_button)
        actions_layout.addWidget(self.back_to_patcher_button)

        layout.addStretch(1)
        layout.addWidget(self.completion_label)
        layout.addWidget(actions_group)
        layout.addStretch(2)
        return page

    def _connect_signals(self):
        self.close_button.clicked.connect(self.hide)
        self.apply_button.clicked.connect(self._apply_patch)
        self.copy_prompt_button.clicked.connect(self._copy_prompt_to_clipboard)
        
        self.file_model.itemChanged.connect(self._on_item_changed)
        self.expand_all_button.clicked.connect(self.file_tree.expandAll)
        self.collapse_all_button.clicked.connect(self.file_tree.collapseAll)
        self.toggle_select_button.clicked.connect(self._on_toggle_select_clicked)

        self.changes_list.itemChanged.connect(self._on_change_item_checked)
        self.changes_list.currentItemChanged.connect(self._display_diff)
        self.changes_list.customContextMenuRequested.connect(self._show_changes_list_context_menu)
        
        self.linter_button.clicked.connect(self._run_linter)
        self.source_control_button.clicked.connect(self._open_source_control)
        self.back_to_patcher_button.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(0))
        
    def _show_changes_list_context_menu(self, pos):
        item = self.changes_list.itemAt(pos)
        if not item: return
            
        data = item.data(Qt.ItemDataRole.UserRole)
        is_unspecified = data.get('unspecified', False)

        if is_unspecified:
            menu = QMenu()
            assign_action = menu.addAction(qta.icon('fa5s.file-signature'), "Assign File Path...")
            
            action = menu.exec(self.changes_list.mapToGlobal(pos))
            if action == assign_action: self._assign_path_to_item(item)
    
    def _assign_path_to_item(self, item: QListWidgetItem):
        current_data = item.data(Qt.ItemDataRole.UserRole)
        old_path = current_data['path']
        
        new_path, ok = QInputDialog.getText(self, "Assign File Path", "Enter relative path for this file:", text="/new_file.py")
        
        if ok and new_path:
            new_path = new_path.replace("\\", "/").lstrip("/")
            if not new_path:
                QMessageBox.warning(self, "Invalid Path", "File path cannot be empty.")
                return

            content = self.parsed_changes.pop(old_path, "")
            final_path_key = f"/{new_path}"
            self.parsed_changes[final_path_key] = content

            font = item.font(); font.setItalic(False); item.setFont(font)
            item.setText(new_path)
            item.setIcon(qta.icon('fa5s.file-medical'))
            current_data['path'] = final_path_key
            current_data['unspecified'] = False
            item.setData(Qt.ItemDataRole.UserRole, current_data)
            QTimer.singleShot(0, lambda: item.setCheckState(Qt.CheckState.Checked))

    def _setup_completion_page(self, applied_count):
        self.completion_label.setText(f"Successfully applied changes to {applied_count} file(s).")
        self.linter_button.setEnabled(applied_count > 0)
        self.stacked_widget.setCurrentIndex(1) 

    def _run_linter(self):
        linter = self.api.get_manager("linter")
        linter.lint_project(self.project_root)
        self.api.show_status_message("Project-wide linting started...", 3000)

    def _open_source_control(self):
        sc_panel = getattr(self.api.get_main_window(), 'source_control_panel', None)
        if sc_panel:
            bottom_tab_widget = getattr(self.api.get_main_window(), '_bottom_tab_widget', None)
            if bottom_tab_widget:
                for i in range(bottom_tab_widget.count()):
                    if bottom_tab_widget.widget(i) == sc_panel:
                        bottom_tab_widget.setCurrentIndex(i)
                        dock = sc_panel.parent()
                        while dock and not isinstance(dock, QDockWidget): dock = dock.parent()
                        if dock: dock.show(); dock.raise_()
                        break

    def _generate_prompt(self):
        selected_files = self._get_checked_files()
        instructions = self.prompt_edit.toPlainText().strip()
        if not instructions:
            QMessageBox.warning(self, "Missing Instructions", "Please provide instructions for the AI.")
            return False

        if not selected_files:
            reply = QMessageBox.question(self, "No Files Selected", "You have not selected any files. Continue generating a prompt with instructions only?",
                                         QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.No: return False

        project_name = os.path.basename(self.project_root)
        file_tree_text = "\n".join(self.project_manager.generate_file_tree_from_list(self.project_root, selected_files)) if selected_files else "No files were provided in context."
        
        prompt_parts = [
            f"# Project Patch Request: {project_name}", "---",
            "## AI Instructions", "```text", instructions, "```",
            "## Golden Rules", "```text", 
            "1. Your response MUST ONLY contain the complete, updated content for each file that needs to change.",
            "2. Enclose each file's content in the standard `### File: /path/to/file.ext` and code block format.",
            "3. Do not add any extra commentary, explanations, or summaries outside of the code blocks.",
            "```", "---", f"## Project File Tree:\n```\n{file_tree_text}\n```"
        ]
        
        if selected_files:
            prompt_parts.extend(["---", "## Project Files"])
            for file_path in sorted(selected_files):
                relative_path = os.path.relpath(file_path, self.project_root).replace(os.sep, '/')
                lang = os.path.splitext(file_path)[1].lstrip('.') or 'text'
                prompt_parts.append(f"### File: `/{relative_path}`\n```{lang}")
                try:
                    with open(file_path, 'r', encoding='utf-8') as f: content = f.read()
                    prompt_parts.append(clean_git_conflict_markers(content))
                except Exception as e:
                    prompt_parts.append(f"[Error reading file: {e}]")
                prompt_parts.append("```")

        self.generated_prompt = "\n\n".join(prompt_parts)
        return True

    def _copy_prompt_to_clipboard(self):
        if self._generate_prompt():
            QApplication.clipboard().setText(self.generated_prompt)
            self.api.show_status_message("Prompt copied to clipboard!", 3000)

    def _parse_and_load_review(self):
        self.parsed_changes = parse_llm_response(self.response_edit.toPlainText())
        self.changes_list.clear()
        self.diff_viewer.clear()

        if not self.parsed_changes:
            QMessageBox.information(self, "No Changes Found", "Could not find any valid file blocks in the response text.")
            self.apply_button.setEnabled(False)
            return
        
        is_any_change_applicable = False
        for rel_path, new_content in sorted(self.parsed_changes.items()):
            if not rel_path or not rel_path.strip():
                log.warning(f"AI Patcher: Ignored empty file path from response.")
                continue

            item = QListWidgetItem()
            is_unspecified = rel_path.startswith('[UNSPECIFIED_FILE_')
            
            data = {'path': rel_path, 'content': new_content, 'unspecified': is_unspecified}
            item.setData(Qt.ItemDataRole.UserRole, data)
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            
            if is_unspecified:
                item.setText(rel_path)
                font = item.font(); font.setItalic(True); item.setFont(font)
                item.setIcon(qta.icon('fa5s.question-circle', color='orange'))
                item.setCheckState(Qt.CheckState.Unchecked) 
            else:
                item.setText(rel_path.lstrip('/\\'))
                item.setCheckState(Qt.CheckState.Checked)
                is_any_change_applicable = True

            self.changes_list.addItem(item)
        
        if self.changes_list.count() > 0:
            self.changes_list.setCurrentRow(0)
        
        self.apply_button.setEnabled(is_any_change_applicable)

    def _display_diff(self, current: QListWidgetItem, _):
        self.diff_viewer.clear()
        if not current: return
            
        data = current.data(Qt.ItemDataRole.UserRole)
        rel_path = data['path']
        is_unspecified = data.get('unspecified', False)
        
        new_content = data['content']
        abs_path = os.path.join(self.project_root, rel_path.lstrip('/\\')) if not is_unspecified else ""

        original_content = ""
        is_new_file = is_unspecified or not os.path.exists(abs_path)
        
        if is_new_file:
            self.diff_viewer.setToolTip("This change will create a new file.")
        elif os.path.isdir(abs_path):
            self.diff_viewer.setPlainText(f"Error: Path '{rel_path}' refers to a directory.")
            return
        else:
            try:
                with open(abs_path, 'r', encoding='utf-8', errors='ignore') as f:
                    original_content = f.read()
                self.diff_viewer.setToolTip(f"Showing changes for:\n{abs_path}")
            except IOError as e:
                self.diff_viewer.setPlainText(f"Error reading original file:\n{e}")
                return
        
        fromfile = f"a{rel_path}" if not is_new_file else "/dev/null"
        tofile = f"b{rel_path}"
        
        diff_text = generate_unified_diff(original_content, new_content, fromfile=fromfile, tofile=tofile)
        self.diff_viewer.set_diff_text(diff_text)
    
    def _on_change_item_checked(self, item: QListWidgetItem):
        is_anything_checked = False
        data = item.data(Qt.ItemDataRole.UserRole)

        if data.get('unspecified', False) and item.checkState() == Qt.CheckState.Checked:
            QTimer.singleShot(0, lambda: item.setCheckState(Qt.CheckState.Unchecked))
            QMessageBox.information(self, "Path Required", "You must right-click and assign a file path before including this change.")
        
        for i in range(self.changes_list.count()):
            list_item = self.changes_list.item(i)
            if not list_item.data(Qt.ItemDataRole.UserRole).get('unspecified') and list_item.checkState() == Qt.CheckState.Checked:
                is_anything_checked = True
                break
        self.apply_button.setEnabled(is_anything_checked)

    def _apply_patch(self):
        changes_to_apply = {}
        applied_count = 0

        for i in range(self.changes_list.count()):
            item = self.changes_list.item(i)
            if item.checkState() == Qt.CheckState.Checked:
                data = item.data(Qt.ItemDataRole.UserRole)
                if not data.get('unspecified', False):
                    changes_to_apply[data['path']] = data['content']
                    applied_count += 1
        
        if not changes_to_apply:
            QMessageBox.warning(self, "No Changes Selected", "Please check the files you wish to apply changes to. Unspecified files must be assigned a path first.")
            return

        success, message = apply_changes_to_project(self.project_root, changes_to_apply)
        if success:
            if explorer := self.api.get_main_window().explorer_panel: explorer.refresh()
            self._setup_completion_page(applied_count)
        else:
            QMessageBox.critical(self, "Patch Failed", message)

    def _populate_file_tree(self):
        self.file_model.clear()
        root_node = self.file_model.invisibleRootItem()
        path_map = {self.project_root: root_node}
        ignore_dirs = {'.git', '__pycache__', 'venv', '.venv', 'dist', 'build', 'logs', 'ai_exports'}
        for dirpath, dirnames, filenames in os.walk(self.project_root, topdown=True):
            dirnames[:] = [d for d in dirnames if d not in ignore_dirs]
            parent_node = path_map.get(os.path.normpath(dirpath))
            if parent_node is None: continue
            for dirname in sorted(dirnames):
                dir_item = QStandardItem(dirname); dir_item.setIcon(qta.icon('fa5.folder')); dir_item.setCheckable(True)
                path = os.path.join(dirpath, dirname); dir_item.setData(path, Qt.ItemDataRole.UserRole)
                parent_node.appendRow(dir_item); path_map[path] = dir_item
            for filename in sorted(filenames):
                file_item = QStandardItem(filename); file_item.setIcon(qta.icon('fa5.file-alt')); file_item.setCheckable(True)
                path = os.path.join(dirpath, filename); file_item.setData(path, Qt.ItemDataRole.UserRole)
                parent_node.appendRow(file_item)
        self.file_tree.expandToDepth(0)
        self._set_all_check_states(Qt.CheckState.Unchecked)

    def _set_all_check_states(self, state: Qt.CheckState):
        self.is_updating_checks = True
        root = self.file_model.invisibleRootItem()
        for row in range(root.rowCount()): self._recursive_set_check_state(root.child(row), state)
        self.is_updating_checks = False
        self._update_toggle_button_state()

    def _recursive_set_check_state(self, item, state):
        if item.isCheckable(): item.setCheckState(state)
        for row in range(item.rowCount()):
            if child_item := item.child(row): self._recursive_set_check_state(child_item, state)

    def _on_toggle_select_clicked(self):
        if self._are_all_items_checked(): self._set_all_check_states(Qt.CheckState.Unchecked)
        else: self._set_all_check_states(Qt.CheckState.Checked)

    def _update_toggle_button_state(self):
        all_checked = self._are_all_items_checked()
        icon_name = 'fa5s.check-square' if all_checked else 'fa5.square'
        tooltip = "Deselect all files" if all_checked else "Select all files"
        self.toggle_select_button.setIcon(qta.icon(icon_name, color='grey')); self.toggle_select_button.setToolTip(tooltip)

    def _are_all_items_checked(self) -> bool:
        items = self._get_all_checkable_items()
        return bool(items) and all(item.checkState() == Qt.CheckState.Checked for item in items)

    def _get_all_checkable_items(self) -> List[QStandardItem]:
        items = []; root = self.file_model.invisibleRootItem()
        def recurse(parent):
            for r in range(parent.rowCount()):
                child = parent.child(r)
                if child and child.isCheckable():
                    items.append(child)
                    if child.hasChildren(): recurse(child)
        recurse(root)
        return items
        
    def _on_item_changed(self, item: QStandardItem):
        if self.is_updating_checks: return
        self.is_updating_checks = True
        state = item.checkState()
        if state != Qt.CheckState.PartiallyChecked: self._update_descendant_states(item, state)
        if item.parent(): self._update_ancestor_states(item.parent())
        self.is_updating_checks = False
        self._update_toggle_button_state()

    def _update_descendant_states(self, parent, state):
        for r in range(parent.rowCount()):
            child = parent.child(r)
            if child and child.isCheckable() and child.checkState() != state:
                child.setCheckState(state)
                if child.hasChildren(): self._update_descendant_states(child, state)

    def _update_ancestor_states(self, parent):
        if not parent or not hasattr(parent, 'checkState'): return
        states = [parent.child(r).checkState() for r in range(parent.rowCount()) if parent.child(r)]
        if not states: return
        
        if all(s == Qt.CheckState.Checked for s in states):
            new_state = Qt.CheckState.Checked
        elif all(s == Qt.CheckState.Unchecked for s in states):
            new_state = Qt.CheckState.Unchecked
        else:
            new_state = Qt.CheckState.PartiallyChecked
            
        if parent.isCheckable() and parent.checkState() != new_state:
            parent.setCheckState(new_state)

    def _get_checked_files(self) -> List[str]:
        files = []; root = self.file_model.invisibleRootItem()
        def recurse(parent):
            if parent.checkState() == Qt.CheckState.Unchecked: return
            if parent.isCheckable():
                path = parent.data(Qt.ItemDataRole.UserRole)
                if path and os.path.isfile(path) and parent.checkState() == Qt.CheckState.Checked: 
                    files.append(path)
                if parent.hasChildren():
                    for r in range(parent.rowCount()):
                        if child := parent.child(r): recurse(child)
        for r in range(root.rowCount()): recurse(root.child(r))
        return list(sorted(set(files)))

    def closeEvent(self, event: QCloseEvent):
        """Override close event to hide the dialog instead of deleting it."""
        self.hide()
        event.ignore()
```

### File: `/plugins/ai_patcher/__init__.py`
```py

```

### File: `/plugins/ai_export_viewer/plugin_main.py`
```py
# /plugins/ai_export_viewer/plugin_main.py
from app_core.puffin_api import PuffinPluginAPI
from .ai_export_viewer_widget import AIExportViewerWidget
from utils.logger import log


class AIExportViewerPlugin:
    """Plugin to view AI-generated export files."""

    def __init__(self, puffin_api: PuffinPluginAPI):
        self.api = puffin_api
        self.main_window = self.api.get_main_window()
        self.viewer_widget = None

        self.api.add_menu_action(
            menu_name="tools",
            text="View AI Exports",
            callback=self.open_viewer_tab,
            icon_name="fa5s.robot"
        )
        log.info("AI Export Viewer plugin initialized and menu action added.")

    def open_viewer_tab(self):
        """Opens a new tab containing the AI Export Viewer widget."""
        self.viewer_widget = AIExportViewerWidget(
            theme_manager=self.api.get_manager("theme"),
            parent=self.main_window
        )

        for i in range(self.main_window.tab_widget.count()):
            if isinstance(self.main_window.tab_widget.widget(i), AIExportViewerWidget):
                self.main_window.tab_widget.setCurrentIndex(i)
                return

        index = self.main_window.tab_widget.addTab(self.viewer_widget, "AI Exports")
        self.main_window.tab_widget.setCurrentIndex(index)
        self.main_window.tab_widget.setTabsClosable(True)


def initialize(puffin_api: PuffinPluginAPI):
    """Entry point for PuffinPyEditor to load the plugin."""
    try:
        return AIExportViewerPlugin(puffin_api)
    except Exception as e:
        log.error(f"Failed to initialize AI Export Viewer: {e}", exc_info=True)
        return None
```

### File: `/plugins/ai_export_viewer/plugin.json`
```json
{
    "id": "ai_export_viewer",
    "name": "AI Export Viewer",
    "author": "PuffinPy Team",
    "version": "1.1.0",
    "description": "Provides a tab-based viewer to manage and review past AI project exports.",
    "entry_point": "plugin_main.py"
}
```

### File: `/plugins/ai_export_viewer/ai_export_viewer_widget.py`
```py
# PuffinPyEditor/plugins/ai_export_viewer/ai_export_viewer_widget.py
import os
from typing import TYPE_CHECKING
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QListWidget, QListWidgetItem,
    QTextEdit, QPushButton, QMessageBox, QSplitter, QFrame
)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt
from markdown import markdown
import qtawesome as qta
from utils.helpers import get_base_path
from utils.logger import log
from app_core.settings_manager import settings_manager

if TYPE_CHECKING:
    from app_core.theme_manager import ThemeManager

class AIExportViewerWidget(QWidget):
    """
    A widget that displays a list of past AI exports and their content,
    designed to be embedded in a tab.
    """
    def __init__(self, theme_manager: "ThemeManager", parent=None):
        super().__init__(parent)
        self.theme_manager = theme_manager
        self.export_dir = os.path.join(get_base_path(), "ai_exports")
        self._ensure_export_dir_exists()

        self.setObjectName("AIExportViewerWidget")
        self._setup_ui()
        self._connect_signals()
        self.update_theme()
        self.refresh_list()

    def _setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Toolbar
        toolbar = QFrame()
        toolbar.setObjectName("ExportViewerToolbar")
        toolbar_layout = QHBoxLayout(toolbar)
        toolbar_layout.setContentsMargins(5, 5, 5, 5)

        self.refresh_button = QPushButton(qta.icon('fa5s.sync-alt'), "Refresh")
        self.delete_button = QPushButton(qta.icon('fa5s.trash-alt'), "Delete")
        toolbar_layout.addWidget(self.refresh_button)
        toolbar_layout.addWidget(self.delete_button)
        toolbar_layout.addStretch()
        main_layout.addWidget(toolbar)

        # Main content area
        splitter = QSplitter(Qt.Orientation.Horizontal)
        main_layout.addWidget(splitter)

        # Left pane for the list of exports
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)
        self.export_list_widget = QListWidget()
        self.export_list_widget.setAlternatingRowColors(True)
        left_layout.addWidget(self.export_list_widget)
        splitter.addWidget(left_widget)

        # Right pane for viewing the content of an export
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)
        self.content_view = QTextEdit()
        self.content_view.setReadOnly(True)
        right_layout.addWidget(self.content_view)
        splitter.addWidget(right_widget)

        splitter.setSizes([250, 550])

    def _connect_signals(self):
        self.export_list_widget.currentItemChanged.connect(
            self._on_export_selected
        )
        self.refresh_button.clicked.connect(self.refresh_list)
        self.delete_button.clicked.connect(self._delete_selected_export)

    def _ensure_export_dir_exists(self):
        try:
            os.makedirs(self.export_dir, exist_ok=True)
        except OSError as e:
            log.error(f"Could not create export directory: {e}", exc_info=True)

    def refresh_list(self):
        self.export_list_widget.clear()
        self.content_view.clear()
        self.delete_button.setEnabled(False)
        try:
            files = [
                f for f in os.listdir(self.export_dir)
                if f.endswith('.md') and
                os.path.isfile(os.path.join(self.export_dir, f))
            ]
            files.sort(reverse=True)  # Show newest first

            if not files:
                self.export_list_widget.addItem("No exports found.")
                self.export_list_widget.setEnabled(False)
                return

            self.export_list_widget.setEnabled(True)
            for filename in files:
                path = os.path.join(self.export_dir, filename)
                item = QListWidgetItem(filename)
                item.setData(Qt.ItemDataRole.UserRole, path)
                self.export_list_widget.addItem(item)
            if self.export_list_widget.count() > 0:
                self.export_list_widget.setCurrentRow(0)

        except OSError as e:
            log.error(f"Error reading export directory {self.export_dir}: {e}")
            self.export_list_widget.addItem("Error reading directory.")
            self.export_list_widget.setEnabled(False)

    def _on_export_selected(self, current: QListWidgetItem, _):
        if not current or not current.data(Qt.ItemDataRole.UserRole):
            self.content_view.clear()
            self.delete_button.setEnabled(False)
            return

        self.delete_button.setEnabled(True)
        filepath = current.data(Qt.ItemDataRole.UserRole)
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            html = markdown(content, extensions=['fenced_code', 'tables',
                                                  'extra', 'sane_lists'])
            self.content_view.setHtml(html)
        except Exception as e:
            error_message = f"Error reading file:\n{filepath}\n\n{str(e)}"
            self.content_view.setText(error_message)
            log.error(f"Failed to read export file {filepath}: {e}")

    def _delete_selected_export(self):
        current_item = self.export_list_widget.currentItem()
        if not current_item:
            return

        filepath = current_item.data(Qt.ItemDataRole.UserRole)
        filename = os.path.basename(filepath)
        reply = QMessageBox.question(
            self, "Confirm Deletion",
            f"Are you sure you want to permanently delete this export?\n\n{filename}",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            try:
                os.remove(filepath)
                log.info(f"Deleted AI export file: {filepath}")
                self.refresh_list()
            except OSError as e:
                log.error(f"Failed to delete file {filepath}: {e}")
                QMessageBox.critical(
                    self, "Deletion Failed", f"Could not delete file:\n{e}"
                )

    def update_theme(self):
        """Applies colors and fonts from the current theme."""
        colors = self.theme_manager.current_theme_data.get('colors', {})
        font_family = settings_manager.get("font_family", "Consolas")
        font_size = settings_manager.get("font_size", 11)

        bg_color = colors.get('editor.background', '#2b2b2b')
        fg_color = colors.get('editor.foreground', '#a9b7c6')
        accent = colors.get('accent', '#88c0d0')
        line_bg = colors.get('editor.lineHighlightBackground', '#323232')
        comment = colors.get('syntax.comment', '#808080')
        string = colors.get('syntax.string', '#6A8759')
        toolbar_bg = colors.get('sidebar.background', '#3c3f41')
        border = colors.get('input.border', '#555')

        self.setStyleSheet(f"""
            AIExportViewerWidget {{ background-color: {bg_color}; }}
            #ExportViewerToolbar {{
                background-color: {toolbar_bg};
                border-bottom: 1px solid {border};
            }}
            QListWidget {{ background-color: {bg_color}; border: none; }}
        """)

        md_style = f"""
            h1,h2,h3,h4,h5,h6 {{
                color:{accent}; border-bottom:1px solid {line_bg};
                padding-bottom:4px; margin-top:15px;
            }}
            a {{ color:{string}; text-decoration:none; }}
            a:hover {{ text-decoration:underline; }}
            p,li {{ font-size:{font_size}pt; }}
            pre,code {{
                background-color:{line_bg}; border:1px solid {border};
                border-radius:4px; padding:10px; font-family:"{font_family}";
            }}
            code {{ padding:2px 4px; border:none; }}
            blockquote {{
                color:{comment}; border-left:3px solid {accent};
                padding-left:10px; margin-left:5px;
            }}
            table{{border-collapse:collapse;}}
            th,td{{border:1px solid {border}; padding:6px;}}
            th{{background-color:{line_bg};}}
        """
        self.content_view.document().setDefaultStyleSheet(md_style)
        font = QFont(settings_manager.get("font_family", "Arial"), font_size)
        self.content_view.document().setDefaultFont(font)
        self.content_view.setStyleSheet(
            f"background-color: {bg_color}; border:none; padding:10px;")

        if item := self.export_list_widget.currentItem():
            self._on_export_selected(item, None)
```

### File: `/plugins/ai_export_viewer/__init__.py`
```py

```

### File: `/installer/create_installer_assets.py`
```py
# PuffinPyEditor/installer/create_installer_assets.py
import os
import struct
import sys
from pathlib import Path
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QPalette

# --- Helper Functions for creating BMP and ICO files ---

def create_bmp(width: int, height: int, color_hex: str, output_path: Path):
    """Generates a solid-color, 24-bit BMP file."""
    try:
        color_hex = color_hex.lstrip('#')
        # BMP uses BGR order
        bgr_color = tuple(int(color_hex[i:i + 2], 16) for i in (4, 2, 0))
    except (ValueError, IndexError):
        print(f"ERROR: Invalid color hex provided for BMP: {color_hex}")
        return False

    bytes_per_pixel = 3
    row_size_unpadded = width * bytes_per_pixel
    padding = (4 - (row_size_unpadded % 4)) % 4
    row_size_padded = row_size_unpadded + padding
    pixel_data_size = row_size_padded * height
    file_header_size, info_header_size = 14, 40
    file_size = file_header_size + info_header_size + pixel_data_size

    try:
        with open(output_path, 'wb') as f:
            # BITMAPFILEHEADER
            f.write(b'BM')
            f.write(struct.pack('<L', file_size))
            f.write(struct.pack('<HH', 0, 0)) # Reserved
            f.write(struct.pack('<L', file_header_size + info_header_size))
            
            # BITMAPINFOHEADER
            f.write(struct.pack('<L', info_header_size))
            f.write(struct.pack('<l', width))
            f.write(struct.pack('<l', height))
            f.write(struct.pack('<H', 1)) # Planes
            f.write(struct.pack('<H', 24)) # Bits per pixel
            f.write(struct.pack('<L', 0)) # Compression (BI_RGB)
            f.write(struct.pack('<L', pixel_data_size))
            f.write(struct.pack('<LLLL', 0, 0, 0, 0)) # XPels, YPels, ClrUsed, ClrImportant
            
            # Pixel Data (bottom-to-top scanlines)
            padding_bytes = b'\x00' * padding
            for _ in range(height):
                for _ in range(width):
                    f.write(struct.pack('BBB', *bgr_color))
                f.write(padding_bytes)
                
        print(f"SUCCESS: Created BMP asset '{output_path.name}'")
        return True
    except IOError as e:
        print(f"ERROR: Failed to write BMP '{output_path}': {e}")
        return False

def create_ico(size: int, color_hex: str, output_path: Path):
    """Generates a solid-color, 32-bit ICO file."""
    try:
        color_hex = color_hex.lstrip('#')
        # ICO uses BGRA order for its internal BMP
        bgra_color = tuple(int(color_hex[i:i + 2], 16) for i in (4, 2, 0)) + (255,) # Add full alpha
    except (ValueError, IndexError):
        print(f"ERROR: Invalid color hex provided for ICO: {color_hex}")
        return False

    # DIB (Device-Independent Bitmap) Data for the ICO
    # BITMAPINFOHEADER
    # Height is doubled to account for the XOR mask (color) and AND mask (transparency)
    info_header = struct.pack('<lllHHLLllLL', 40, size, size * 2, 1, 32, 0, 0, 0, 0, 0, 0)
    
    # XOR mask (color data)
    xor_mask = bytearray(struct.pack('<BBBB', *bgra_color) * (size * size))
    
    # AND mask (transparency data, 1 bit per pixel). All 0s for fully opaque.
    and_mask = bytearray([0x00] * (size * size // 8))
    
    dib_data = info_header + xor_mask + and_mask
    dib_size = len(dib_data)

    # ICO File Headers
    # ICONDIR (6 bytes)
    icon_dir = struct.pack('<HHH', 0, 1, 1) # Reserved, Type 1 (ICO), 1 image
    
    # ICONDIRENTRY (16 bytes)
    image_offset = 22 # 6 (ICONDIR) + 16 (ICONDIRENTRY)
    icon_dir_entry = struct.pack('<BBBBHHLL', size, size, 0, 0, 1, 32, dib_size, image_offset)

    try:
        with open(output_path, 'wb') as f:
            f.write(icon_dir)
            f.write(icon_dir_entry)
            f.write(dib_data)
        print(f"SUCCESS: Created ICO asset '{output_path.name}'")
        return True
    except IOError as e:
        print(f"ERROR: Failed to create ICO '{output_path}': {e}")
        return False

# --- Main Execution ---
if __name__ == "__main__":
    print("\n--- Generating Installer Assets ---")
    
    # Create a headless QApplication to access system-wide theme information
    app = QApplication(sys.argv)
    palette = app.palette()

    # Get system colors for a native look and feel
    # QPalette.ColorRole.Highlight is the main accent color (e.g., for selected items)
    icon_color = palette.color(QPalette.ColorRole.Highlight).name()
    # QPalette.ColorRole.Button is a good, neutral background for UI elements
    header_bg_color = palette.color(QPalette.ColorRole.Button).name()
    # QPalette.ColorRole.Window is the general window background color
    welcome_bg_color = palette.color(QPalette.ColorRole.Window).name()
    
    print(f"Using system colors: Icon Accent ({icon_color}), Header BG ({header_bg_color}), Welcome BG ({welcome_bg_color})")

    assets_dir = Path(__file__).parent / "assets"
    assets_dir.mkdir(exist_ok=True)

    # Generate all required assets using the system theme colors
    all_ok = all([
        create_ico(32, icon_color, assets_dir / "PuffinPyEditor.ico"),
        create_bmp(496, 58, header_bg_color, assets_dir / "PuffinPyEditor_Header.bmp"),
        create_bmp(164, 314, welcome_bg_color, assets_dir / "welcome.bmp")
    ])

    if not all_ok:
        print("\n--- ERROR: One or more assets failed to generate. ---")
        sys.exit(1)
    
    print("\n--- All installer assets generated successfully. ---")
    sys.exit(0)
```

### File: `/installer/build.py`
```py
# PuffinPyEditor/installer/build.py
import os
import sys
import subprocess
import shutil
import argparse
from pathlib import Path

# --- Configuration ---
APP_NAME = "PuffinPyEditor"
ROOT_DIR = Path(__file__).parent.parent
VERSION_FILE = ROOT_DIR / "VERSION.txt"
MAIN_SPEC = ROOT_DIR / "main.spec"
TRAY_SPEC = ROOT_DIR / "tray_app.spec"
LOG_VIEWER_SPEC = ROOT_DIR / "log_viewer.spec"
INSTALLER_ASSETS_SCRIPT = ROOT_DIR / "installer" / "create_installer_assets.py"
INSTALLER_SCRIPT = ROOT_DIR / "installer" / "create_installer.nsi"
DIST_DIR = ROOT_DIR / "dist"
FINAL_DIR = DIST_DIR / APP_NAME
ASSETS_DIR = ROOT_DIR / "assets"
BUILD_DIR = ROOT_DIR / "build"

# --- Colors for printing ---
class BColors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def run_command(command, cwd=None, capture_output=False, check_for_errors=False):
    """Runs a command and exits if it fails."""
    try:
        cmd_str = ' '.join(map(str, command))
        print(f"{BColors.OKBLUE}Running: {cmd_str}{BColors.ENDC}")
        result = subprocess.run(
            command,
            check=True,
            cwd=cwd,
            capture_output=capture_output,
            text=True,
            encoding='utf-8',
            errors='ignore'
        )
        output = (result.stdout or "") + (result.stderr or "")
        if capture_output:
            print(output)
        # Extra check for tools that don't return proper error codes
        if check_for_errors and ("error in script" in output.lower() or "aborting creation" in output.lower()):
            raise subprocess.CalledProcessError(result.returncode, command, output=result.stdout, stderr=result.stderr)
        return result
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        print(f"\n{BColors.FAIL}{BColors.BOLD}[FATAL ERROR] Command failed: {cmd_str}{BColors.ENDC}")
        if hasattr(e, 'stdout') and e.stdout:
            print(f"{BColors.FAIL}--- STDOUT ---\n{e.stdout}{BColors.ENDC}")
        if hasattr(e, 'stderr') and e.stderr:
            print(f"{BColors.FAIL}--- STDERR ---\n{e.stderr}{BColors.ENDC}")
        sys.exit(1)

def print_step(step_num, total_steps, message):
    """Prints a formatted step message."""
    print(f"\n{BColors.HEADER}{BColors.BOLD}===== [{step_num}/{total_steps}] {message} ====={BColors.ENDC}")

def find_nsis_path(override_path=None):
    """Finds the path to makensis.exe."""
    if override_path and Path(override_path).exists():
        print(f"  - Using NSIS path from settings: {override_path}")
        return override_path
    nsis_path = shutil.which("makensis")
    if nsis_path:
        print(f"  - Found 'makensis' on system PATH: {nsis_path}")
        return nsis_path
    if sys.platform == "win32":
        for path_str in [
            "C:\\Program Files (x86)\\NSIS\\makensis.exe",
            "C:\\Program Files\\NSIS\\makensis.exe",
        ]:
            path = Path(path_str)
            if path.exists():
                print(f"  - Found 'makensis' at default location: {path}")
                return str(path)
    return None

def main():
    parser = argparse.ArgumentParser(description=f"Build script for {APP_NAME}.")
    parser.add_argument('--cleanup', action='store_true', help="Remove temporary build directory after completion.")
    parser.add_argument('--nsis-path', type=str, help="Override path to makensis.exe.")
    parser.add_argument('--version', type=str, help="Override version from VERSION.txt.")
    args = parser.parse_args()
    print(f"{BColors.HEADER}PuffinPyEditor Build System v2.0{BColors.ENDC}")

    print_step(1, 6, "Reading Application Version")
    if args.version:
        app_version = args.version
    else:
        if not VERSION_FILE.exists():
            print(f"{BColors.FAIL}[FATAL ERROR] {VERSION_FILE} not found.{BColors.ENDC}"); sys.exit(1)
        app_version = VERSION_FILE.read_text().strip()
    print(f"  - Version identified as: {app_version}")

    step_num = 2
    for desc, spec_file in {
        "MAIN application (PuffinPyEditor.exe)": MAIN_SPEC,
        "TRAY application (PuffinPyTray.exe)": TRAY_SPEC,
        "LOG VIEWER application (log_viewer.exe)": LOG_VIEWER_SPEC,
    }.items():
        print_step(step_num, 6, f"Bundling {desc}")
        run_command([sys.executable, "-m", "PyInstaller", str(spec_file), "--noconfirm", "--distpath", str(FINAL_DIR)])
        print(f"  - {desc} bundled successfully.")
        step_num += 1

    print_step(5, 6, "Copying Application Assets")
    assets_dest = FINAL_DIR / "assets"
    if assets_dest.exists(): shutil.rmtree(assets_dest)
    shutil.copytree(ASSETS_DIR, assets_dest); print("  - Assets copied successfully.")

    print_step(6, 6, "Generating and Compiling Installer")
    print("  - Generating installer assets...")
    run_command([sys.executable, str(INSTALLER_ASSETS_SCRIPT)])
    makensis_exe = find_nsis_path(args.nsis_path)
    if not makensis_exe:
        print(f"{BColors.WARNING}[WARNING] NSIS (makensis.exe) not found. Skipping installer creation.{BColors.ENDC}")
    else:
        print(f"  - Compiling with: {makensis_exe}")
        installer_output_file = DIST_DIR / f"{APP_NAME}_v{app_version}_Setup.exe"
        nsis_cmd = [makensis_exe, f'/DAPP_VERSION={app_version}', f'/DAPP_NAME={APP_NAME}', f'/DSRC_DIR={FINAL_DIR.resolve()}', f'/DOUT_FILE={installer_output_file.resolve()}', str(INSTALLER_SCRIPT)]
        run_command(nsis_cmd, capture_output=True, check_for_errors=True)
        print(f"  - {BColors.OKGREEN}Installer created successfully at: {installer_output_file}{BColors.ENDC}")

    if args.cleanup:
        print_step("BONUS", "BONUS", "Cleaning up build artifacts")
        if BUILD_DIR.exists():
            shutil.rmtree(BUILD_DIR)
            print(f"  - Removed '{BUILD_DIR}' directory.")

    print(f"\n{BColors.OKGREEN}{BColors.BOLD}==============================================")
    print(f"    BUILD PROCESS FINISHED SUCCESSFULLY")
    print(f"=============================================={BColors.ENDC}")

if __name__ == "__main__":
    main()
```

### File: `/core_debug_tools/plugin_initializer/plugin_main.py`
```py
# /core_debug_tools/plugin_initializer/plugin_main.py
import os
import json
from PyQt6.QtWidgets import QMessageBox

from app_core.puffin_api import PuffinPluginAPI
from utils.helpers import get_base_path
from utils.logger import log
from .new_plugin_dialog import NewPluginDialog

# Boilerplate content for the new plugin's main Python file
PLUGIN_MAIN_BOILERPLATE = """
from app_core.puffin_api import PuffinPluginAPI
from utils.logger import log

class {class_name}:
    \"\"\"
    Main class for the {plugin_name} plugin.
    \"\"\"
    def __init__(self, puffin_api: PuffinPluginAPI):
        self.api = puffin_api
        self.main_window = self.api.get_main_window()
        
        # TODO: Add your plugin's initialization logic here.
        # This is a good place to add menu items, connect signals, etc.
        #
        # Example:
        # self.api.add_menu_action(
        #     menu_name="tools",
        #     text="{plugin_name}",
        #     callback=self.say_hello,
        #     icon_name="fa5s.hand-spock"
        # )
        
        log.info("{plugin_name} plugin initialized.")

    def say_hello(self):
        self.api.show_message("info", "{plugin_name}", "Hello from your new plugin!")
        
    def shutdown(self):
        \"\"\"
        (Optional) Called by the editor when the plugin is being unloaded.
        Use this to clean up resources, like disconnecting signals or removing UI.
        \"\"\"
        log.info("{plugin_name} is shutting down.")


def initialize(puffin_api: PuffinPluginAPI):
    \"\"\"
    Entry point for the plugin. PuffinPyEditor calls this to create an
    instance of your plugin.
    \"\"\"
    return {class_name}(puffin_api)

"""

class PluginInitializer:
    def __init__(self, puffin_api: PuffinPluginAPI):
        self.api = puffin_api
        self.main_window = self.api.get_main_window()
        self.base_plugins_path = os.path.join(get_base_path(), 'plugins')
        
        # Add the action to the 'Tools' menu
        self.api.add_menu_action(
            menu_name="tools",
            text="Create New Plugin...",
            callback=self.show_creation_dialog,
            icon_name="fa5s.magic"
        )
        log.info("Plugin Initializer is ready.")
        
    def show_creation_dialog(self):
        """Shows the dialog to get details for the new plugin."""
        dialog = NewPluginDialog(self.main_window)
        if dialog.exec():
            plugin_data = dialog.get_plugin_data()
            self._create_plugin_scaffold(plugin_data)

    def _create_plugin_scaffold(self, data: dict):
        """Creates the necessary directory and files for the new plugin."""
        plugin_id = data.get('id')
        plugin_path = os.path.join(self.base_plugins_path, plugin_id)

        try:
            # 1. Validate: Check if directory already exists
            if os.path.exists(plugin_path):
                self.api.show_message(
                    "critical", "Plugin Exists",
                    f"A plugin with the ID '{plugin_id}' already exists at:\n{plugin_path}"
                )
                return

            # 2. Create Directory Structure
            log.info(f"Creating plugin directory at: {plugin_path}")
            os.makedirs(plugin_path)

            # 3. Create __init__.py
            with open(os.path.join(plugin_path, '__init__.py'), 'w', encoding='utf-8') as f:
                f.write("# This file makes this directory a Python package.\n")
                
            # 4. Create plugin.json
            json_path = os.path.join(plugin_path, 'plugin.json')
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4)

            # 5. Create plugin_main.py
            main_py_path = os.path.join(plugin_path, data['entry_point'])
            class_name = data['name'].replace(' ', '') + "Plugin" # e.g., MyAwesomeToolsPlugin
            
            boilerplate = PLUGIN_MAIN_BOILERPLATE.format(
                class_name=class_name,
                plugin_name=data['name']
            )
            with open(main_py_path, 'w', encoding='utf-8') as f:
                f.write(boilerplate)

            log.info("Plugin scaffold created successfully.")
            self._on_creation_success(data, main_py_path)
        
        except Exception as e:
            log.error(f"Failed to create plugin scaffold for '{plugin_id}': {e}", exc_info=True)
            self.api.show_message("critical", "Creation Failed", f"An unexpected error occurred:\n{e}")

    def _on_creation_success(self, data: dict, main_py_path: str):
        """Handles post-creation steps, like showing a success message."""
        reply = QMessageBox.information(
            self.main_window,
            "Plugin Created",
            f"Successfully created the '{data['name']}' plugin.\n\n"
            "Would you like to open its main file to start editing?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.Yes
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.main_window._action_open_file(main_py_path)
            
        # Notify user that a reload/restart is needed to see the plugin in menus etc.
        self.api.show_status_message(
            "Reload required to see new plugin in Preferences list.", 5000
        )


def initialize(puffin_api: PuffinPluginAPI):
    """Entry point for the Plugin Initializer tool."""
    return PluginInitializer(puffin_api)
```

### File: `/core_debug_tools/plugin_initializer/plugin.json`
```json
{
    "id": "plugin_initializer",
    "name": "Plugin Initializer",
    "author": "PuffinPy AI",
    "version": "1.0.0",
    "description": "A developer tool to quickly scaffold new plugins for PuffinPyEditor.",
    "entry_point": "plugin_main.py"
}
```

### File: `/core_debug_tools/plugin_initializer/new_plugin_dialog.py`
```py
# /core_debug_tools/plugin_initializer/new_plugin_dialog.py
import re
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QFormLayout, QLineEdit,
                             QDialogButtonBox, QLabel, QMessageBox)
from PyQt6.QtCore import Qt

class NewPluginDialog(QDialog):
    """A dialog for collecting information to create a new plugin scaffold."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Create New Plugin")
        self.setMinimumWidth(400)

        # Main layout
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Enter the details for your new plugin."))
        
        # Form for input fields
        form_layout = QFormLayout()
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("e.g., My Awesome Tools")

        self.id_edit = QLineEdit()
        self.id_edit.setPlaceholderText("e.g., my_awesome_tools (auto-generated)")

        self.author_edit = QLineEdit()
        self.author_edit.setPlaceholderText("Your Name or Alias")

        self.desc_edit = QLineEdit()
        self.desc_edit.setPlaceholderText("A brief description of what this plugin does.")

        form_layout.addRow("Plugin Name:", self.name_edit)
        form_layout.addRow("Plugin ID:", self.id_edit)
        form_layout.addRow("Author:", self.author_edit)
        form_layout.addRow("Description:", self.desc_edit)
        layout.addLayout(form_layout)

        # OK and Cancel buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        layout.addWidget(button_box)
        
        # Connect signals
        button_box.accepted.connect(self.validate_and_accept)
        button_box.rejected.connect(self.reject)
        self.name_edit.textChanged.connect(self._auto_generate_id)

    def _auto_generate_id(self, text: str):
        """Generates a safe, snake_case ID from the plugin name."""
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', text)
        s2 = re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()
        safe_id = re.sub(r'[\s\-]+', '_', s2) # Replace spaces and hyphens
        safe_id = re.sub(r'[^\w_]', '', safe_id) # Remove invalid characters
        self.id_edit.setText(safe_id)

    def validate_and_accept(self):
        """Ensures required fields are filled before closing."""
        if not self.name_edit.text() or not self.id_edit.text() or not self.author_edit.text():
            QMessageBox.warning(self, "Missing Information",
                                "Plugin Name, ID, and Author are required fields.")
            return
        
        # If validation passes, accept the dialog
        self.accept()

    def get_plugin_data(self) -> dict:
        """Returns the entered data as a dictionary."""
        return {
            "name": self.name_edit.text().strip(),
            "id": self.id_edit.text().strip(),
            "author": self.author_edit.text().strip(),
            "description": self.desc_edit.text().strip(),
            "version": "1.0.0",  # Default starting version
            "entry_point": "plugin_main.py"
        }
```

### File: `/core_debug_tools/plugin_initializer/__init__.py`
```py
# This file makes this directory a Python package.

```

### File: `/core_debug_tools/live_log_viewer/plugin_main.py`
```py
# PuffinPyEditor/core_debug_tools/live_log_viewer/plugin_main.py
import subprocess
import sys
import os
from app_core.puffin_api import PuffinPluginAPI
from utils.logger import log, LOG_FILE
from utils.helpers import get_base_path

LOG_VIEWER_SCRIPT_PATH = os.path.join(get_base_path(), "utils", "log_viewer.py")

class LiveLogViewerPlugin:
    def __init__(self, puffin_api: PuffinPluginAPI):
        self.api = puffin_api
        self.log_file = LOG_FILE
        self.action = self.api.add_menu_action(
            menu_name="tools", text="Live Log Viewer",
            callback=self.launch_log_viewer,
            shortcut="Ctrl+Shift+L", icon_name="fa5s.bug"
        )
        self.action.setToolTip("Open a real-time viewer for the application log.")
        log.info("Live Log Viewer action added to Tools menu.")

    def launch_log_viewer(self):
        try:
            python_executable = sys.executable
            command = [python_executable, LOG_VIEWER_SCRIPT_PATH, self.log_file]
            log.info(f"Executing command: {' '.join(command)}")
            subprocess.Popen(command)
        except Exception as e:
            self.api.log_error(f"Failed to launch log viewer: {e}")

def initialize(puffin_api: PuffinPluginAPI):
    return LiveLogViewerPlugin(puffin_api)
```

### File: `/core_debug_tools/live_log_viewer/plugin.json`
```json
{
    "id": "live_log_viewer",
    "name": "Live Log Viewer",
    "author": "AI Assistant",
    "version": "1.0.0",
    "description": "Adds a tool to launch a separate, real-time log viewer application that persists across application restarts."
}
```

### File: `/core_debug_tools/enhanced_exceptions/plugin_main.py`
```py
# PuffinPyEditor/core_debug_tools/enhanced_exceptions/plugin_main.py
import sys
from utils.logger import log
from .exception_dialog import ExceptionDialog
from app_core.puffin_api import PuffinPluginAPI

class EnhancedExceptionsPlugin:
    _instance = None

    def __init__(self, puffin_api: PuffinPluginAPI, original_hook):
        self.api = puffin_api
        self.main_window = self.api.get_main_window()
        self.original_excepthook = original_hook or sys.excepthook
        sys.excepthook = self.show_exception_dialog
        log.info("Enhanced Exception Reporter initialized and hook installed.")

    def show_exception_dialog(self, exc_type, exc_value, exc_tb):
        # CORRECTED: Specifically ignore KeyboardInterrupt.
        if issubclass(exc_type, KeyboardInterrupt):
            log.warning("KeyboardInterrupt caught and ignored by the main thread.")
            return

        log.critical("Unhandled exception caught by Enhanced Reporter:",
                     exc_info=(exc_type, exc_value, exc_tb))
        dialog = ExceptionDialog(exc_type, exc_value, exc_tb, self.main_window)
        dialog.exec()
        self.original_excepthook(exc_type, exc_value, exc_tb)

def initialize(puffin_api: PuffinPluginAPI, original_hook=None):
    if EnhancedExceptionsPlugin._instance is None:
        EnhancedExceptionsPlugin._instance = EnhancedExceptionsPlugin(
            puffin_api, original_hook
        )
    return EnhancedExceptionsPlugin._instance
```

### File: `/core_debug_tools/enhanced_exceptions/plugin.json`
```json
{
    "id": "enhanced_exceptions",
    "name": "Enhanced Exception Reporter",
    "author": "AI Assistant",
    "version": "1.0.0",
    "description": "Replaces the default crash handler with a developer-friendly dialog showing a detailed traceback."
}
```

### File: `/core_debug_tools/enhanced_exceptions/exception_dialog.py`
```py
# PuffinPyEditor/core_debug_tools/enhanced_exceptions/exception_dialog.py
import traceback
import platform
import sys
from urllib.parse import quote_plus
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QTextEdit, QLabel,
                             QDialogButtonBox, QApplication)
from PyQt6.QtGui import QFont, QDesktopServices
from PyQt6.QtCore import QUrl
from utils.versioning import APP_VERSION
from utils.logger import log


class ExceptionDialog(QDialog):
    """A dialog to display unhandled exceptions with developer-friendly actions."""

    def __init__(self, exc_type, exc_value, exc_tb, parent=None):
        super().__init__(parent)
        self.setWindowTitle("PuffinPyEditor - Unhandled Exception")
        self.setMinimumSize(700, 500)

        # Format the traceback
        tb_list = traceback.format_exception(exc_type, exc_value, exc_tb)
        self.traceback_text = "".join(tb_list)
        self.exception_type = exc_type.__name__
        self.system_info = (
            f"PuffinPyEditor Version: {APP_VERSION}\n"
            f"Python Version: {sys.version.split()[0]}\n"
            f"Platform: {platform.system()} {platform.release()}"
        )
        self.full_report_display = (
            "--- System Information ---\n"
            f"{self.system_info}\n\n"
            "--- Traceback ---\n"
            f"{self.traceback_text}"
        )

        # UI Setup
        layout = QVBoxLayout(self)
        label = QLabel(
            "An unexpected error occurred. You can help improve PuffinPyEditor "
            "by reporting this issue on GitHub."
        )
        label.setWordWrap(True)
        layout.addWidget(label)

        self.details_box = QTextEdit()
        self.details_box.setReadOnly(True)
        self.details_box.setFont(QFont("Consolas", 10))
        self.details_box.setText(self.full_report_display)
        layout.addWidget(self.details_box)

        self.button_box = QDialogButtonBox()
        copy_button = self.button_box.addButton(
            "Copy Details", QDialogButtonBox.ButtonRole.ActionRole
        )
        report_button = self.button_box.addButton(
            "Report on GitHub", QDialogButtonBox.ButtonRole.HelpRole
        )
        quit_button = self.button_box.addButton(
            "Quit Application", QDialogButtonBox.ButtonRole.DestructiveRole
        )

        copy_button.clicked.connect(self._copy_to_clipboard)
        report_button.clicked.connect(self._open_github_issues)
        quit_button.clicked.connect(self._force_quit_app)

        layout.addWidget(self.button_box)

    def _copy_to_clipboard(self):
        """Copies the full report to the clipboard."""
        QApplication.clipboard().setText(self.full_report_display)
        self.details_box.selectAll()

    def _open_github_issues(self):
        """Opens a new issue on GitHub with pre-filled information."""
        issue_title = quote_plus(f"Crash Report: {self.exception_type}")
        issue_body_template = """
**Describe the bug**
A clear and concise description of what the bug is. What were you doing when the crash occurred?

**Steps to Reproduce**
Steps to reproduce the behavior:
1. Go to '...'
2. Click on '....'
3. See error

**Automatic Crash Report Details**

---
<details>
<summary>Click to expand</summary>

```
{traceback}
```

</details>
""".format(traceback=self.full_report_display)

        issue_body = quote_plus(issue_body_template.strip())

        url = QUrl(
            f"https://github.com/Stelliro/PuffinPyEditor/issues/new?title="
            f"{issue_title}&body={issue_body}"
        )
        QDesktopServices.openUrl(url)

    def _force_quit_app(self):
        """A failsafe to ensure the application quits immediately."""
        log.warning("Force quit initiated from exception dialog.")
        QApplication.instance().quit()
```

### File: `/core_debug_tools/debug_framework/plugin_main.py`
```py
# PuffinPyEditor/core_debug_tools/debug_framework/plugin_main.py
from utils.logger import log
from .api import PuffinDebugAPI
from .debug_window import DebugWindow
from app_core.puffin_api import PuffinPluginAPI


class DebugFrameworkPlugin:
    def __init__(self, puffin_api: PuffinPluginAPI):
        self.puffin_api = puffin_api
        self.main_window = self.puffin_api.get_main_window()
        self.debug_window = None

        log.info("Initializing Debug Tools Framework...")

        self.puffin_api.add_menu_action(
            menu_name="debug",
            text="Show Debugger",
            callback=self.show_debugger_window,
            icon_name="fa5s.bug"
        )

        if not hasattr(self.main_window, 'debug_api'):
            self.main_window.debug_api = PuffinDebugAPI(self)

        log.info("Debug Framework initialized and attached to MainWindow.")

    def show_debugger_window(self):
        if not self.debug_window or not self.debug_window.isVisible():
            self.debug_window = DebugWindow(self.puffin_api, self.main_window)
            # Re-register tools
            if hasattr(self.main_window, 'debug_api'):
                for name, widget_class in self.main_window.debug_api.registered_tools.items():
                    self.debug_window.add_tool_tab(name, widget_class)

        self.debug_window.show()
        self.debug_window.raise_()
        self.debug_window.activateWindow()

    def add_tool_tab(self, tool_name: str, widget_class: type):
        if self.debug_window:
            self.debug_window.add_tool_tab(tool_name, widget_class)


def initialize(puffin_api: PuffinPluginAPI):
    return DebugFrameworkPlugin(puffin_api)
```

### File: `/core_debug_tools/debug_framework/plugin.json`
```json
{
    "id": "debug_framework",
    "name": "Debug Tools Framework",
    "author": "AI Assistant",
    "version": "1.0.0",
    "description": "Provides a core framework and UI for debugging plugins. Other debug tools can register themselves with this framework."
}
```

### File: `/core_debug_tools/debug_framework/debug_window.py`
```py
# PuffinPyEditor/core_debug_tools/debug_framework/debug_window.py
from typing import Type
from PyQt6.QtWidgets import QMainWindow, QTabWidget, QWidget
from PyQt6.QtCore import QSize


class DebugWindow(QMainWindow):
    """A floating window that hosts various debugging tool widgets in tabs."""

    def __init__(self, puffin_api, parent=None):
        super().__init__(parent)
        self.puffin_api = puffin_api
        self.setWindowTitle("PuffinPyEditor - Debugger")
        self.setMinimumSize(QSize(800, 600))

        self.tab_widget = QTabWidget()
        self.tab_widget.setTabsClosable(False)
        self.tab_widget.setDocumentMode(True)

        self.setCentralWidget(self.tab_widget)
        self.tools = {}

    def add_tool_tab(self, tool_name: str, widget_class: Type[QWidget]):
        """Creates an instance of the widget class and adds it as a tab."""
        if tool_name in self.tools:
            return  # Avoid duplicate tabs

        # Pass the main Puffin API to the tool if it needs it
        tool_instance = widget_class(self.puffin_api)
        self.tab_widget.addTab(tool_instance, tool_name)
        self.tools[tool_name] = tool_instance
```

### File: `/core_debug_tools/debug_framework/api.py`
```py
# PuffinPyEditor/core_debug_tools/debug_framework/api.py
from typing import Dict, Type
from PyQt6.QtWidgets import QWidget
from utils.logger import log


class PuffinDebugAPI:
    """A specialized API for debug-related plugins."""

    def __init__(self, debug_window_instance):
        self._debug_window = debug_window_instance
        self.registered_tools: Dict[str, Type[QWidget]] = {}
        log.info("PuffinDebugAPI initialized.")

    def register_tool(self, tool_name: str, widget_class: Type[QWidget]):
        """
        Registers a widget to be shown in a tab in the main Debugger window.

        Args:
            tool_name: The name to be displayed on the tab.
            widget_class: The QWidget class (not an instance) to be
                          instantiated. The class constructor should accept
                          the main PuffinAPI instance.
        """
        if tool_name in self.registered_tools:
            log.warning(
                f"Debug tool '{tool_name}' is already registered. Overwriting.")
        self.registered_tools[tool_name] = widget_class
        log.info(f"Registered new debug tool: {tool_name}")
        self._debug_window.add_tool_tab(tool_name, widget_class)
```

### File: `/assets/golden_rules.json`
```json
{
    "name": "Default PuffinPy Golden Rules",
    "description": "The standard set of fundamental rules for AI code generation, emphasizing a clean, patch-like output.",
    "rules": [
        "Your response MUST ONLY contain the complete, updated content for each file that needs to change.",
        "Enclose each file's content in the standard `### File: /path/to/file.ext` and code block format.",
        "Do not add any extra commentary, explanations, or summaries outside of the code blocks.",
        "Each provided file must be complete and correct, including all necessary imports and boilerplate.",
        "If a file is not being changed, do not include it in the response.",
        "Ensure file paths are relative to the project root and use forward slashes (e.g., `app_core/main.py`).",
        "Maintain existing code style, indentation, and conventions for all unchanged parts of a file."
    ]
}
```

### File: `/assets/themes/icon_colors.json`
```json
{
    "default_folder": "#79b8f2",
    "default_file": "#C0C5CE",

    ".py": "#3572A5",
    ".js": "#f7df1e",
    ".ts": "#3178c6",
    ".html": "#e34f26",
    ".css": "#1572b6",
    ".scss": "#1572b6",
    ".json": "#fbc02d",
    ".md": "#90a4ae",
    ".yaml": "#a0a0a0",
    ".yml": "#a0a0a0",
    ".xml": "#009900",
    ".gitignore": "#f44336",

    "__pycache__": "#546e7a",
    "venv": "#8BC34A",
    ".venv": "#8BC34A",
    "node_modules": "#cb3837",
    "dist": "#FFCA28",
    ".git": "#f44336"
}
```

### File: `/assets/themes/custom_themes.json`
```json
{
    "custom_neoncircuit": {
        "name": "Neon Circuit",
        "author": "PuffinPy AI",
        "type": "dark",
        "colors": {
            "window.background": "#0A0D14",
            "sidebar.background": "#0F141F",
            "editor.background": "#0A0D14",
            "editor.foreground": "#E0E0E0",
            "editor.selectionBackground": "#16335F",
            "editor.userHighlightBackground": "#00BFFF4D",
            "editor.lineHighlightBackground": "#151B29",
            "editor.matchingBracketBackground": "#16335F",
            "editor.matchingBracketForeground": "#E0E0E0",
            "editor.breakpoint.color": "#FF4D8B",
            "editorGutter.background": "#0F141F",
            "editorGutter.hoverBackground": "#00BFFF1A",
            "editorGutter.foreground": "#4A5469",
            "editorGutter.ruler.color": "#00BFFF",
            "editorLineNumber.foreground": "#4A5469",
            "editorLineNumber.activeForeground": "#E0E0E0",
            "menu.background": "#151B29",
            "menu.foreground": "#E0E0E0",
            "statusbar.background": "#0F141F",
            "statusbar.foreground": "#E0E0E0",
            "tab.activeBackground": "#0A0D14",
            "tab.inactiveBackground": "#0F141F",
            "tab.activeForeground": "#E0E0E0",
            "tab.inactiveForeground": "#4A5469",
            "button.background": "#1F427A",
            "button.foreground": "#E0E0E0",
            "input.background": "#151B29",
            "input.foreground": "#E0E0E0",
            "input.border": "#4A5469",
            "scrollbar.background": "#0F141F",
            "scrollbar.handle": "#1F427A",
            "scrollbar.handleHover": "#2E5894",
            "scrollbar.handlePressed": "#2E5894",
            "accent": "#00BFFF",
            "syntax.keyword": "#DA70D6",
            "syntax.operator": "#00BFFF",
            "syntax.brace": "#E0E0E0",
            "syntax.decorator": "#39FF14",
            "syntax.self": "#DA70D6",
            "syntax.className": "#39FF14",
            "syntax.functionName": "#00FFFF",
            "syntax.comment": "#555555",
            "syntax.string": "#FFFF80",
            "syntax.docstring": "#555555",
            "syntax.number": "#FF4D8B",
            "tree.indentationGuides.stroke": "#1F427A",
            "tree.trace.color": "#00BFFF",
            "tree.trace.shadow": "#DA70D6",
            "tree.node.color": "#00BFFF",
            "tree.node.fill": "#1F427A"
        },
        "is_custom": true
    },
    "custom_tokyonight_1750416561": {
        "name": "Tokyo Night",
        "author": "enkia (adapted)",
        "type": "dark",
        "font_suggestion": [
            "Fira Code",
            "JetBrains Mono",
            "monospace"
        ],
        "colors": {
            "window.background": "#1a1b26",
            "sidebar.background": "#16161e",
            "editor.background": "#1a1b26",
            "editor.foreground": "#a9b1d6",
            "editor.selectionBackground": "#2e3c62",
            "editor.userHighlightBackground": "#7aa2f74D",
            "editorGutter.background": "#1a1b26",
            "editorGutter.foreground": "#414868",
            "editorGutter.hoverBackground": "#7aa2f71a",
            "editorLineNumber.foreground": "#414868",
            "editorLineNumber.activeForeground": "#a9b1d6",
            "editor.lineHighlightBackground": "#292e42",
            "editor.matchingBracketBackground": "#2e3c62",
            "editor.matchingBracketForeground": "#a9b1d6",
            "editor.breakpoint.color": "#ff757f",
            "menu.background": "#16161e",
            "menu.foreground": "#a9b1d6",
            "statusbar.background": "#101014",
            "statusbar.foreground": "#a9b1d6",
            "tab.activeBackground": "#292e42",
            "tab.inactiveBackground": "#1a1b26",
            "tab.activeForeground": "#a9b1d6",
            "tab.inactiveForeground": "#565f89",
            "button.background": "#414868",
            "button.foreground": "#a9b1d6",
            "input.background": "#16161e",
            "input.foreground": "#a9b1d6",
            "input.border": "#414868",
            "scrollbar.background": "#16161e",
            "scrollbar.handle": "#414868",
            "scrollbar.handleHover": "#565f89",
            "scrollbar.handlePressed": "#565f89",
            "accent": "#7aa2f7",
            "syntax.keyword": "#bb9af7",
            "syntax.operator": "#89ddff",
            "syntax.brace": "#a9b1d6",
            "syntax.decorator": "#7aa2f7",
            "syntax.self": "#ff9e64",
            "syntax.className": "#ff9e64",
            "syntax.functionName": "#7aa2f7",
            "syntax.comment": "#565f89",
            "syntax.string": "#9ece6a",
            "syntax.docstring": "#565f89",
            "syntax.number": "#ff9e64",
            "tree.indentationGuides.stroke": "#414868",
            "tree.trace.color": "#7aa2f7",
            "tree.trace.shadow": "#bb9af7",
            "tree.node.color": "#7aa2f7",
            "tree.node.fill": "#414868"
        },
        "is_custom": true
    },
    "custom_nightowl_1750416562": {
        "name": "Night Owl",
        "author": "Sarah Drasner (adapted)",
        "type": "dark",
        "font_suggestion": [
            "Operator Mono",
            "Fira Code",
            "monospace"
        ],
        "colors": {
            "window.background": "#011627",
            "sidebar.background": "#011627",
            "editor.background": "#011627",
            "editor.foreground": "#d6deeb",
            "editor.selectionBackground": "#092f4e",
            "editor.userHighlightBackground": "#7fdbca4D",
            "editorGutter.background": "#011627",
            "editorGutter.foreground": "#5f7e97",
            "editorGutter.hoverBackground": "#7fdbca1a",
            "editorLineNumber.foreground": "#5f7e97",
            "editorLineNumber.activeForeground": "#d6deeb",
            "editor.lineHighlightBackground": "#012030",
            "editor.matchingBracketBackground": "#374161",
            "editor.matchingBracketForeground": "#d6deeb",
            "editor.breakpoint.color": "#ff5874",
            "menu.background": "#01111d",
            "menu.foreground": "#d6deeb",
            "statusbar.background": "#01111d",
            "statusbar.foreground": "#d6deeb",
            "tab.activeBackground": "#7fdbca",
            "tab.inactiveBackground": "#011627",
            "tab.activeForeground": "#011627",
            "tab.inactiveForeground": "#5f7e97",
            "button.background": "#0b2942",
            "button.foreground": "#d6deeb",
            "input.background": "#01111d",
            "input.foreground": "#d6deeb",
            "input.border": "#5f7e97",
            "scrollbar.background": "#01111d",
            "scrollbar.handle": "#0b2942",
            "scrollbar.handleHover": "#374161",
            "scrollbar.handlePressed": "#374161",
            "accent": "#7fdbca",
            "syntax.keyword": "#c792ea",
            "syntax.operator": "#c792ea",
            "syntax.brace": "#d6deeb",
            "syntax.decorator": "#ffeb95",
            "syntax.self": "#addb67",
            "syntax.className": "#ffeb95",
            "syntax.functionName": "#82aaff",
            "syntax.comment": "#637777",
            "syntax.string": "#addb67",
            "syntax.docstring": "#637777",
            "syntax.number": "#f78c6c",
            "tree.indentationGuides.stroke": "#5f7e97",
            "tree.trace.color": "#82aaff",
            "tree.trace.shadow": "#7fdbca",
            "tree.node.color": "#82aaff",
            "tree.node.fill": "#0b2942"
        },
        "is_custom": true
    },
    "custom_cobalt2_1750416563": {
        "name": "Cobalt2",
        "author": "Wes Bos (adapted)",
        "type": "dark",
        "font_suggestion": [
            "Operator Mono",
            "Consolas",
            "monospace"
        ],
        "colors": {
            "window.background": "#193549",
            "sidebar.background": "#152d40",
            "editor.background": "#193549",
            "editor.foreground": "#e1efff",
            "editor.selectionBackground": "#265476",
            "editor.userHighlightBackground": "#ffc6004D",
            "editorGutter.background": "#193549",
            "editorGutter.foreground": "#3b5369",
            "editorGutter.hoverBackground": "#ffc6001a",
            "editorLineNumber.foreground": "#3b5369",
            "editorLineNumber.activeForeground": "#e1efff",
            "editor.lineHighlightBackground": "#21445e",
            "editor.matchingBracketBackground": "#152d40",
            "editor.matchingBracketForeground": "#ffc600",
            "editor.breakpoint.color": "#ff628c",
            "menu.background": "#152d40",
            "menu.foreground": "#e1efff",
            "statusbar.background": "#0e2334",
            "statusbar.foreground": "#e1efff",
            "tab.activeBackground": "#ffc600",
            "tab.inactiveBackground": "#193549",
            "tab.activeForeground": "#193549",
            "tab.inactiveForeground": "#3b5369",
            "button.background": "#21445e",
            "button.foreground": "#e1efff",
            "input.background": "#152d40",
            "input.foreground": "#e1efff",
            "input.border": "#3b5369",
            "scrollbar.background": "#152d40",
            "scrollbar.handle": "#21445e",
            "scrollbar.handleHover": "#3b5369",
            "scrollbar.handlePressed": "#3b5369",
            "accent": "#ffc600",
            "syntax.keyword": "#ff9d00",
            "syntax.operator": "#e1efff",
            "syntax.brace": "#e1efff",
            "syntax.decorator": "#ffc600",
            "syntax.self": "#9effff",
            "syntax.className": "#9effff",
            "syntax.functionName": "#ffc600",
            "syntax.comment": "#0088ff",
            "syntax.string": "#3ad900",
            "syntax.docstring": "#0088ff",
            "syntax.number": "#ff628c",
            "tree.indentationGuides.stroke": "#3b5369",
            "tree.trace.color": "#ffc600",
            "tree.trace.shadow": "#9effff",
            "tree.node.color": "#ffc600",
            "tree.node.fill": "#21445e"
        },
        "is_custom": true
    },
    "custom_dracula_1750416564": {
        "name": "Dracula",
        "author": "Zeno Rocha (adapted)",
        "type": "dark",
        "font_suggestion": [
            "Fira Code",
            "Consolas",
            "monospace"
        ],
        "colors": {
            "window.background": "#282a36",
            "sidebar.background": "#21222C",
            "editor.background": "#282a36",
            "editor.foreground": "#f8f8f2",
            "editor.selectionBackground": "#44475a",
            "editor.userHighlightBackground": "#bd93f94D",
            "editorGutter.background": "#282a36",
            "editorGutter.foreground": "#6272a4",
            "editorGutter.hoverBackground": "#bd93f91a",
            "editorLineNumber.foreground": "#6272a4",
            "editorLineNumber.activeForeground": "#f8f8f2",
            "editor.lineHighlightBackground": "#44475a",
            "editor.matchingBracketBackground": "#44475a",
            "editor.matchingBracketForeground": "#f8f8f2",
            "editor.breakpoint.color": "#ff5555",
            "menu.background": "#21222C",
            "menu.foreground": "#f8f8f2",
            "statusbar.background": "#191a21",
            "statusbar.foreground": "#f8f8f2",
            "tab.activeBackground": "#44475a",
            "tab.inactiveBackground": "#282a36",
            "tab.activeForeground": "#f8f8f2",
            "tab.inactiveForeground": "#6272a4",
            "button.background": "#44475a",
            "button.foreground": "#f8f8f2",
            "input.background": "#21222C",
            "input.foreground": "#f8f8f2",
            "input.border": "#6272a4",
            "scrollbar.background": "#21222C",
            "scrollbar.handle": "#44475a",
            "scrollbar.handleHover": "#6272a4",
            "scrollbar.handlePressed": "#6272a4",
            "accent": "#bd93f9",
            "syntax.keyword": "#ff79c6",
            "syntax.operator": "#f8f8f2",
            "syntax.brace": "#f8f8f2",
            "syntax.decorator": "#50fa7b",
            "syntax.self": "#bd93f9",
            "syntax.className": "#bd93f9",
            "syntax.functionName": "#50fa7b",
            "syntax.comment": "#6272a4",
            "syntax.string": "#f1fa8c",
            "syntax.docstring": "#6272a4",
            "syntax.number": "#bd93f9",
            "tree.indentationGuides.stroke": "#6272a4",
            "tree.trace.color": "#bd93f9",
            "tree.trace.shadow": "#ff79c6",
            "tree.node.color": "#bd93f9",
            "tree.node.fill": "#44475a"
        },
        "is_custom": true
    },
    "custom_monokaipro_1750416565": {
        "name": "Monokai Pro",
        "author": "monokai.pro (adapted)",
        "type": "dark",
        "font_suggestion": [
            "Operator Mono",
            "Fira Code",
            "Consolas",
            "monospace"
        ],
        "colors": {
            "window.background": "#2D2A2E",
            "sidebar.background": "#333034",
            "editor.background": "#2D2A2E",
            "editor.foreground": "#FCFCFA",
            "editor.selectionBackground": "#504c51",
            "editor.userHighlightBackground": "#ffd8664D",
            "editorGutter.background": "#333034",
            "editorGutter.foreground": "#7B797C",
            "editorGutter.hoverBackground": "#ffd8661a",
            "editorLineNumber.foreground": "#7B797C",
            "editorLineNumber.activeForeground": "#FCFCFA",
            "editor.lineHighlightBackground": "#3E3B3F",
            "editor.matchingBracketBackground": "#5b595c",
            "editor.matchingBracketForeground": "#FCFCFA",
            "editor.breakpoint.color": "#FF6188",
            "menu.background": "#333034",
            "menu.foreground": "#FCFCFA",
            "statusbar.background": "#221F22",
            "statusbar.foreground": "#FCFCFA",
            "tab.activeBackground": "#2D2A2E",
            "tab.inactiveBackground": "#221F22",
            "tab.activeForeground": "#FCFCFA",
            "tab.inactiveForeground": "#7B797C",
            "button.background": "#4A464B",
            "button.foreground": "#FCFCFA",
            "input.background": "#3E3B3F",
            "input.foreground": "#FCFCFA",
            "input.border": "#5b595c",
            "scrollbar.background": "#221F22",
            "scrollbar.handle": "#4A464B",
            "scrollbar.handleHover": "#5b595c",
            "scrollbar.handlePressed": "#5b595c",
            "accent": "#FFD866",
            "syntax.keyword": "#FF6188",
            "syntax.operator": "#FCFCFA",
            "syntax.brace": "#FCFCFA",
            "syntax.decorator": "#A9DC76",
            "syntax.self": "#FF6188",
            "syntax.className": "#78DCE8",
            "syntax.functionName": "#A9DC76",
            "syntax.comment": "#7B797C",
            "syntax.string": "#FFD866",
            "syntax.docstring": "#7B797C",
            "syntax.number": "#AB9DF2",
            "tree.indentationGuides.stroke": "#7B797C",
            "tree.trace.color": "#FFD866",
            "tree.trace.shadow": "#A9DC76",
            "tree.node.color": "#FFD866",
            "tree.node.fill": "#4A464B"
        },
        "is_custom": true
    },
    "custom_onedarkpro_1750416566": {
        "name": "One Dark Pro",
        "author": "Binaryify (adapted)",
        "type": "dark",
        "font_suggestion": [
            "JetBrains Mono",
            "Fira Code",
            "Consolas",
            "monospace"
        ],
        "colors": {
            "window.background": "#282c34",
            "sidebar.background": "#21252b",
            "editor.background": "#282c34",
            "editor.foreground": "#abb2bf",
            "editor.selectionBackground": "#3e4451",
            "editor.userHighlightBackground": "#61afef4D",
            "editorGutter.background": "#282c34",
            "editorGutter.foreground": "#5c6370",
            "editorGutter.hoverBackground": "#61afef1a",
            "editorLineNumber.foreground": "#5c6370",
            "editorLineNumber.activeForeground": "#abb2bf",
            "editor.lineHighlightBackground": "#2c313c",
            "editor.matchingBracketBackground": "#5c6370",
            "editor.matchingBracketForeground": "#abb2bf",
            "editor.breakpoint.color": "#e06c75",
            "menu.background": "#21252b",
            "menu.foreground": "#abb2bf",
            "statusbar.background": "#21252b",
            "statusbar.foreground": "#abb2bf",
            "tab.activeBackground": "#2c313c",
            "tab.inactiveBackground": "#282c34",
            "tab.activeForeground": "#abb2bf",
            "tab.inactiveForeground": "#5c6370",
            "button.background": "#3a3f4b",
            "button.foreground": "#abb2bf",
            "input.background": "#21252b",
            "input.foreground": "#abb2bf",
            "input.border": "#3a3f4b",
            "scrollbar.background": "#21252b",
            "scrollbar.handle": "#3a3f4b",
            "scrollbar.handleHover": "#5c6370",
            "scrollbar.handlePressed": "#5c6370",
            "accent": "#61afef",
            "syntax.keyword": "#c678dd",
            "syntax.operator": "#56b6c2",
            "syntax.brace": "#abb2bf",
            "syntax.decorator": "#61afef",
            "syntax.self": "#e5c07b",
            "syntax.className": "#e5c07b",
            "syntax.functionName": "#61afef",
            "syntax.comment": "#5c6370",
            "syntax.string": "#98c379",
            "syntax.docstring": "#5c6370",
            "syntax.number": "#d19a66",
            "tree.indentationGuides.stroke": "#5c6370",
            "tree.trace.color": "#61afef",
            "tree.trace.shadow": "#98c379",
            "tree.node.color": "#61afef",
            "tree.node.fill": "#3a3f4b"
        },
        "is_custom": true
    },
    "custom_gruvboxdark_1750416567": {
        "name": "Gruvbox Dark",
        "author": "Pavel Pertsev (adapted)",
        "type": "dark",
        "font_suggestion": [
            "Fira Mono",
            "JetBrains Mono",
            "monospace"
        ],
        "colors": {
            "window.background": "#282828",
            "sidebar.background": "#282828",
            "editor.background": "#1d2021",
            "editor.foreground": "#ebdbb2",
            "editor.selectionBackground": "#504945",
            "editor.userHighlightBackground": "#fe80194D",
            "editorGutter.background": "#282828",
            "editorGutter.foreground": "#928374",
            "editorGutter.hoverBackground": "#fe80191a",
            "editorLineNumber.foreground": "#928374",
            "editorLineNumber.activeForeground": "#ebdbb2",
            "editor.lineHighlightBackground": "#3c3836",
            "editor.matchingBracketBackground": "#504945",
            "editor.matchingBracketForeground": "#ebdbb2",
            "editor.breakpoint.color": "#fb4934",
            "menu.background": "#3c3836",
            "menu.foreground": "#ebdbb2",
            "statusbar.background": "#32302f",
            "statusbar.foreground": "#ebdbb2",
            "tab.activeBackground": "#1d2021",
            "tab.inactiveBackground": "#282828",
            "tab.activeForeground": "#ebdbb2",
            "tab.inactiveForeground": "#928374",
            "button.background": "#504945",
            "button.foreground": "#ebdbb2",
            "input.background": "#3c3836",
            "input.foreground": "#ebdbb2",
            "input.border": "#665c54",
            "scrollbar.background": "#282828",
            "scrollbar.handle": "#504945",
            "scrollbar.handleHover": "#665c54",
            "scrollbar.handlePressed": "#7c6f64",
            "accent": "#fe8019",
            "syntax.keyword": "#fb4934",
            "syntax.operator": "#ebdbb2",
            "syntax.brace": "#ebdbb2",
            "syntax.decorator": "#fabd2f",
            "syntax.self": "#d3869b",
            "syntax.className": "#fabd2f",
            "syntax.functionName": "#b8bb26",
            "syntax.comment": "#928374",
            "syntax.string": "#b8bb26",
            "syntax.docstring": "#83a598",
            "syntax.number": "#d3869b",
            "tree.indentationGuides.stroke": "#928374",
            "tree.trace.color": "#fe8019",
            "tree.trace.shadow": "#fabd2f",
            "tree.node.color": "#fe8019",
            "tree.node.fill": "#504945"
        },
        "is_custom": true
    },
    "custom_shadesofpurple_1750416568": {
        "name": "Shades of Purple",
        "author": "Ahmad Awais (adapted)",
        "type": "dark",
        "font_suggestion": [
            "Operator Mono",
            "Dank Mono",
            "monospace"
        ],
        "colors": {
            "window.background": "#2d2b55",
            "sidebar.background": "#28264e",
            "editor.background": "#2d2b55",
            "editor.foreground": "#ffffff",
            "editor.selectionBackground": "#684896",
            "editor.userHighlightBackground": "#fad0004D",
            "editorGutter.background": "#2d2b55",
            "editorGutter.foreground": "#6c6783",
            "editorGutter.hoverBackground": "#fad0001a",
            "editorLineNumber.foreground": "#6c6783",
            "editorLineNumber.activeForeground": "#ffffff",
            "editor.lineHighlightBackground": "#232043",
            "editor.matchingBracketBackground": "#684896",
            "editor.matchingBracketForeground": "#ffffff",
            "editor.breakpoint.color": "#ff9d00",
            "menu.background": "#28264e",
            "menu.foreground": "#ffffff",
            "statusbar.background": "#1e1c3f",
            "statusbar.foreground": "#fad000",
            "tab.activeBackground": "#4d479d",
            "tab.inactiveBackground": "#2d2b55",
            "tab.activeForeground": "#ffffff",
            "tab.inactiveForeground": "#6c6783",
            "button.background": "#4d479d",
            "button.foreground": "#ffffff",
            "input.background": "#28264e",
            "input.foreground": "#ffffff",
            "input.border": "#6c6783",
            "scrollbar.background": "#28264e",
            "scrollbar.handle": "#4d479d",
            "scrollbar.handleHover": "#684896",
            "scrollbar.handlePressed": "#684896",
            "accent": "#fad000",
            "syntax.keyword": "#b392f0",
            "syntax.operator": "#ff9d00",
            "syntax.brace": "#ffffff",
            "syntax.decorator": "#fad000",
            "syntax.self": "#ff9d00",
            "syntax.className": "#fad000",
            "syntax.functionName": "#a0e886",
            "syntax.comment": "#b362ff",
            "syntax.string": "#a0e886",
            "syntax.docstring": "#b362ff",
            "syntax.number": "#d5aaff",
            "tree.indentationGuides.stroke": "#6c6783",
            "tree.trace.color": "#fad000",
            "tree.trace.shadow": "#a0e886",
            "tree.node.color": "#fad000",
            "tree.node.fill": "#4d479d"
        },
        "is_custom": true
    },
    "custom_everforestdark_1750416569": {
        "name": "Everforest Dark",
        "author": "Sainnhe (adapted)",
        "type": "dark",
        "font_suggestion": [
            "Iosevka",
            "Fira Code",
            "monospace"
        ],
        "colors": {
            "window.background": "#2f383e",
            "sidebar.background": "#2f383e",
            "editor.background": "#2f383e",
            "editor.foreground": "#d3c6aa",
            "editor.selectionBackground": "#545e62",
            "editor.userHighlightBackground": "#a7c0804D",
            "editorGutter.background": "#3a4145",
            "editorGutter.foreground": "#5f6c6d",
            "editorGutter.hoverBackground": "#a7c0801a",
            "editorLineNumber.foreground": "#5f6c6d",
            "editorLineNumber.activeForeground": "#d3c6aa",
            "editor.lineHighlightBackground": "#3a4145",
            "editor.matchingBracketBackground": "#545e62",
            "editor.matchingBracketForeground": "#d3c6aa",
            "editor.breakpoint.color": "#e67e80",
            "menu.background": "#3a4145",
            "menu.foreground": "#d3c6aa",
            "statusbar.background": "#282f34",
            "statusbar.foreground": "#d3c6aa",
            "tab.activeBackground": "#424d53",
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
            "accent": "#a7c080",
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
            "syntax.number": "#d699b6",
            "tree.indentationGuides.stroke": "#5f6c6d",
            "tree.trace.color": "#83c092",
            "tree.trace.shadow": "#a7c080",
            "tree.node.color": "#83c092",
            "tree.node.fill": "#424d53"
        },
        "is_custom": true
    },
    "custom_nord_1750416570": {
        "name": "Nord",
        "author": "Arctic Ice Studio (adapted)",
        "type": "dark",
        "font_suggestion": [
            "JetBrains Mono",
            "Fira Code",
            "Consolas",
            "monospace"
        ],
        "colors": {
            "window.background": "#2E3440",
            "sidebar.background": "#2E3440",
            "editor.background": "#2E3440",
            "editor.foreground": "#D8DEE9",
            "editor.selectionBackground": "#434c5e",
            "editor.userHighlightBackground": "#88c0d04D",
            "editorGutter.background": "#3B4252",
            "editorGutter.foreground": "#4C566A",
            "editorGutter.hoverBackground": "#88c0d01a",
            "editorLineNumber.foreground": "#4C566A",
            "editorLineNumber.activeForeground": "#D8DEE9",
            "editor.lineHighlightBackground": "#3B4252",
            "editor.matchingBracketBackground": "#4C566A",
            "editor.matchingBracketForeground": "#ECEFF4",
            "editor.breakpoint.color": "#bf616a",
            "menu.background": "#3B4252",
            "menu.foreground": "#ECEFF4",
            "statusbar.background": "#3B4252",
            "statusbar.foreground": "#D8DEE9",
            "tab.activeBackground": "#434C5E",
            "tab.inactiveBackground": "#2E3440",
            "tab.activeForeground": "#ECEFF4",
            "tab.inactiveForeground": "#4C566A",
            "button.background": "#434C5E",
            "button.foreground": "#ECEFF4",
            "input.background": "#3B4252",
            "input.foreground": "#D8DEE9",
            "input.border": "#4C566A",
            "scrollbar.background": "#2E3440",
            "scrollbar.handle": "#434C5E",
            "scrollbar.handleHover": "#4C566A",
            "scrollbar.handlePressed": "#4C566A",
            "accent": "#88C0D0",
            "syntax.keyword": "#81A1C1",
            "syntax.operator": "#81A1C1",
            "syntax.brace": "#ECEFF4",
            "syntax.decorator": "#88C0D0",
            "syntax.self": "#81A1C1",
            "syntax.className": "#8FBCBB",
            "syntax.functionName": "#88C0D0",
            "syntax.comment": "#616E88",
            "syntax.string": "#A3BE8C",
            "syntax.docstring": "#616E88",
            "syntax.number": "#B48EAD",
            "tree.indentationGuides.stroke": "#4C566A",
            "tree.trace.color": "#88C0D0",
            "tree.trace.shadow": "#81A1C1",
            "tree.node.color": "#88C0D0",
            "tree.node.fill": "#434C5E"
        },
        "is_custom": true
    },
    "custom_solarizedlight_1750416571": {
        "name": "Solarized Light",
        "author": "Ethan Schoonover (adapted)",
        "type": "light",
        "font_suggestion": [
            "Source Code Pro",
            "Consolas",
            "Menlo",
            "monospace"
        ],
        "colors": {
            "window.background": "#fdf6e3",
            "sidebar.background": "#fdf6e3",
            "editor.background": "#fdf6e3",
            "editor.foreground": "#657b83",
            "editor.selectionBackground": "#eee8d5",
            "editor.userHighlightBackground": "#268bd24D",
            "editorGutter.background": "#eee8d5",
            "editorGutter.foreground": "#93a1a1",
            "editorGutter.hoverBackground": "#268bd21a",
            "editorLineNumber.foreground": "#93a1a1",
            "editorLineNumber.activeForeground": "#586e75",
            "editor.lineHighlightBackground": "#eee8d5",
            "editor.matchingBracketBackground": "#d4cdc3",
            "editor.matchingBracketForeground": "#586e75",
            "editor.breakpoint.color": "#dc322f",
            "menu.background": "#eee8d5",
            "menu.foreground": "#586e75",
            "statusbar.background": "#eee8d5",
            "statusbar.foreground": "#586e75",
            "tab.activeBackground": "#fdf6e3",
            "tab.inactiveBackground": "#eee8d5",
            "tab.activeForeground": "#073642",
            "tab.inactiveForeground": "#93a1a1",
            "button.background": "#eee8d5",
            "button.foreground": "#586e75",
            "input.background": "#fffbf2",
            "input.foreground": "#657b83",
            "input.border": "#eee8d5",
            "scrollbar.background": "#fdf6e3",
            "scrollbar.handle": "#eee8d5",
            "scrollbar.handleHover": "#d4cdc3",
            "scrollbar.handlePressed": "#d4cdc3",
            "accent": "#268bd2",
            "syntax.keyword": "#859900",
            "syntax.operator": "#657b83",
            "syntax.brace": "#657b83",
            "syntax.decorator": "#268bd2",
            "syntax.self": "#268bd2",
            "syntax.className": "#2aa198",
            "syntax.functionName": "#268bd2",
            "syntax.comment": "#93a1a1",
            "syntax.string": "#2aa198",
            "syntax.docstring": "#93a1a1",
            "syntax.number": "#d33682",
            "tree.indentationGuides.stroke": "#93a1a1",
            "tree.trace.color": "#268bd2",
            "tree.trace.shadow": "#2aa198",
            "tree.node.color": "#268bd2",
            "tree.node.fill": "#eee8d5"
        },
        "is_custom": true
    },
    "custom_onelight_1750416572": {
        "name": "One Light",
        "author": "Atom (adapted)",
        "type": "light",
        "font_suggestion": [
            "JetBrains Mono",
            "SF Mono",
            "monospace"
        ],
        "colors": {
            "window.background": "#fafafa",
            "sidebar.background": "#f0f0f0",
            "editor.background": "#fafafa",
            "editor.foreground": "#383a42",
            "editor.selectionBackground": "#eaeaeb",
            "editor.userHighlightBackground": "#4078f24D",
            "editorGutter.background": "#fafafa",
            "editorGutter.foreground": "#a0a1a7",
            "editorGutter.hoverBackground": "#4078f21a",
            "editorLineNumber.foreground": "#a0a1a7",
            "editorLineNumber.activeForeground": "#383a42",
            "editor.lineHighlightBackground": "#f0f1f1",
            "editor.matchingBracketBackground": "#d7d7d7",
            "editor.matchingBracketForeground": "#383a42",
            "editor.breakpoint.color": "#e45649",
            "menu.background": "#f0f0f0",
            "menu.foreground": "#383a42",
            "statusbar.background": "#eaeaeb",
            "statusbar.foreground": "#383a42",
            "tab.activeBackground": "#fafafa",
            "tab.inactiveBackground": "#eaeaeb",
            "tab.activeForeground": "#383a42",
            "tab.inactiveForeground": "#a0a1a7",
            "button.background": "#eaeaeb",
            "button.foreground": "#383a42",
            "input.background": "#f0f0f0",
            "input.foreground": "#383a42",
            "input.border": "#d7d7d7",
            "scrollbar.background": "#f0f0f0",
            "scrollbar.handle": "#d7d7d7",
            "scrollbar.handleHover": "#a0a1a7",
            "scrollbar.handlePressed": "#a0a1a7",
            "accent": "#4078f2",
            "syntax.keyword": "#a626a4",
            "syntax.operator": "#383a42",
            "syntax.brace": "#383a42",
            "syntax.decorator": "#50a14f",
            "syntax.self": "#e45649",
            "syntax.className": "#c18401",
            "syntax.functionName": "#4078f2",
            "syntax.comment": "#a0a1a7",
            "syntax.string": "#50a14f",
            "syntax.docstring": "#a0a1a7",
            "syntax.number": "#986801",
            "tree.indentationGuides.stroke": "#a0a1a7",
            "tree.trace.color": "#4078f2",
            "tree.trace.shadow": "#50a14f",
            "tree.node.color": "#4078f2",
            "tree.node.fill": "#eaeaeb"
        },
        "is_custom": true
    },
    "custom_githublight_1750416573": {
        "name": "GitHub Light",
        "author": "GitHub (adapted)",
        "type": "light",
        "font_suggestion": [
            "SF Mono",
            "Consolas",
            "monospace"
        ],
        "colors": {
            "window.background": "#ffffff",
            "sidebar.background": "#f6f8fa",
            "editor.background": "#ffffff",
            "editor.foreground": "#24292f",
            "editor.selectionBackground": "#afb8c1",
            "editor.userHighlightBackground": "#0969da4D",
            "editorGutter.background": "#ffffff",
            "editorGutter.foreground": "#8c959d",
            "editorGutter.hoverBackground": "#0969da1a",
            "editorLineNumber.foreground": "#8c959d",
            "editorLineNumber.activeForeground": "#24292f",
            "editor.lineHighlightBackground": "#f6f8fa",
            "editor.matchingBracketBackground": "#dff7ff",
            "editor.matchingBracketForeground": "#24292f",
            "editor.breakpoint.color": "#cf222e",
            "menu.background": "#f6f8fa",
            "menu.foreground": "#24292f",
            "statusbar.background": "#f6f8fa",
            "statusbar.foreground": "#57606a",
            "tab.activeBackground": "#ffffff",
            "tab.inactiveBackground": "#f6f8fa",
            "tab.activeForeground": "#24292f",
            "tab.inactiveForeground": "#57606a",
            "button.background": "#f6f8fa",
            "button.foreground": "#24292f",
            "input.background": "#f6f8fa",
            "input.foreground": "#24292f",
            "input.border": "#d0d7de",
            "scrollbar.background": "#f6f8fa",
            "scrollbar.handle": "#d0d7de",
            "scrollbar.handleHover": "#afb8c1",
            "scrollbar.handlePressed": "#afb8c1",
            "accent": "#0969da",
            "syntax.keyword": "#cf222e",
            "syntax.operator": "#24292f",
            "syntax.brace": "#24292f",
            "syntax.decorator": "#8250df",
            "syntax.self": "#0969da",
            "syntax.className": "#8250df",
            "syntax.functionName": "#8250df",
            "syntax.comment": "#57606a",
            "syntax.string": "#0a3069",
            "syntax.docstring": "#57606a",
            "syntax.number": "#cf222e",
            "tree.indentationGuides.stroke": "#d0d7de",
            "tree.trace.color": "#0969da",
            "tree.trace.shadow": "#8250df",
            "tree.node.color": "#0969da",
            "tree.node.fill": "#f6f8fa"
        },
        "is_custom": true
    },
    "custom_terminalgreen_1750416574": {
        "name": "Terminal Green",
        "author": "PuffinPy AI",
        "type": "dark",
        "font_suggestion": [
            "Consolas",
            "Courier New",
            "Fixedsys",
            "monospace"
        ],
        "colors": {
            "window.background": "#000000",
            "sidebar.background": "#050A05",
            "editor.background": "#0A0F0A",
            "editor.foreground": "#30FF30",
            "editor.selectionBackground": "#104010",
            "editor.userHighlightBackground": "#30ff304D",
            "editorGutter.background": "#050A05",
            "editorGutter.foreground": "#20A020",
            "editorGutter.hoverBackground": "#30ff301a",
            "editorLineNumber.foreground": "#20A020",
            "editorLineNumber.activeForeground": "#80FF80",
            "editor.lineHighlightBackground": "#102810",
            "editor.matchingBracketBackground": "#153015",
            "editor.matchingBracketForeground": "#80FF80",
            "editor.breakpoint.color": "#30FF30",
            "menu.background": "#0A1A0A",
            "menu.foreground": "#20D020",
            "statusbar.background": "#051005",
            "statusbar.foreground": "#30FF30",
            "tab.activeBackground": "#0D1A0D",
            "tab.inactiveBackground": "#0A0F0A",
            "tab.activeForeground": "#80FF80",
            "tab.inactiveForeground": "#20A020",
            "button.background": "#103010",
            "button.foreground": "#30FF30",
            "input.background": "#0F200F",
            "input.foreground": "#30FF30",
            "input.border": "#205020",
            "scrollbar.background": "#0A0F0A",
            "scrollbar.handle": "#184818",
            "scrollbar.handleHover": "#206020",
            "scrollbar.handlePressed": "#287828",
            "accent": "#30FF30",
            "syntax.keyword": "#40FF40",
            "syntax.operator": "#30FF30",
            "syntax.brace": "#60FF60",
            "syntax.decorator": "#80FF80",
            "syntax.self": "#50FF50",
            "syntax.className": "#90FF90",
            "syntax.functionName": "#A0FFA0",
            "syntax.comment": "#50A050",
            "syntax.string": "#80FF80",
            "syntax.docstring": "#50A050",
            "syntax.number": "#60FF60",
            "tree.indentationGuides.stroke": "#20A020",
            "tree.trace.color": "#30FF30",
            "tree.trace.shadow": "#40FF40",
            "tree.node.color": "#30FF30",
            "tree.node.fill": "#103010"
        },
        "is_custom": true
    },
    "custom_synthwave84_1750416575": {
        "name": "SynthWave '84",
        "author": "Robb Owen (adapted)",
        "type": "dark",
        "font_suggestion": [
            "Operator Mono",
            "Fira Code",
            "monospace"
        ],
        "colors": {
            "window.background": "#2a2139",
            "sidebar.background": "#2a2139",
            "editor.background": "#251f32",
            "editor.foreground": "#f8f8f2",
            "editor.selectionBackground": "#504473",
            "editor.userHighlightBackground": "#ff00ff4D",
            "editorGutter.background": "#2a2139",
            "editorGutter.foreground": "#7b5b9f",
            "editorGutter.hoverBackground": "#ff00ff1a",
            "editorLineNumber.foreground": "#7b5b9f",
            "editorLineNumber.activeForeground": "#f8f8f2",
            "editor.lineHighlightBackground": "#34294f",
            "editor.matchingBracketBackground": "#7b5b9f",
            "editor.matchingBracketForeground": "#ffffff",
            "editor.breakpoint.color": "#f92aad",
            "menu.background": "#251f32",
            "menu.foreground": "#f8f8f2",
            "statusbar.background": "#1e182d",
            "statusbar.foreground": "#ff00ff",
            "tab.activeBackground": "#7fdbca",
            "tab.inactiveBackground": "#2a2139",
            "tab.activeForeground": "#2a2139",
            "tab.inactiveForeground": "#7b5b9f",
            "button.background": "#4a4269",
            "button.foreground": "#f8f8f2",
            "input.background": "#1e182d",
            "input.foreground": "#f8f8f2",
            "input.border": "#7b5b9f",
            "scrollbar.background": "#1e182d",
            "scrollbar.handle": "#4a4269",
            "scrollbar.handleHover": "#7b5b9f",
            "scrollbar.handlePressed": "#7b5b9f",
            "accent": "#ff00ff",
            "syntax.keyword": "#ff79c6",
            "syntax.operator": "#00f5ff",
            "syntax.brace": "#f8f8f2",
            "syntax.decorator": "#ffeb95",
            "syntax.self": "#ff00ff",
            "syntax.className": "#00f5ff",
            "syntax.functionName": "#fce257",
            "syntax.comment": "#726593",
            "syntax.string": "#ffca28",
            "syntax.docstring": "#726593",
            "syntax.number": "#f92aad",
            "tree.indentationGuides.stroke": "#7b5b9f",
            "tree.trace.color": "#00f5ff",
            "tree.trace.shadow": "#f92aad",
            "tree.node.color": "#00f5ff",
            "tree.node.fill": "#4a4269"
        },
        "is_custom": true
    },
    "custom_volcanicash_1750416576": {
        "name": "Volcanic Ash",
        "author": "PuffinPy AI",
        "type": "dark",
        "font_suggestion": [
            "JetBrains Mono",
            "Fira Code",
            "Consolas"
        ],
        "colors": {
            "window.background": "#1c1c1c",
            "sidebar.background": "#212121",
            "editor.background": "#1c1c1c",
            "editor.foreground": "#FFDBC5",
            "editor.selectionBackground": "#681313",
            "editor.userHighlightBackground": "#e539354D",
            "editorGutter.background": "#212121",
            "editorGutter.foreground": "#616161",
            "editorGutter.hoverBackground": "#e539351a",
            "editorLineNumber.foreground": "#616161",
            "editorLineNumber.activeForeground": "#FFDBC5",
            "editor.lineHighlightBackground": "#303030",
            "editor.matchingBracketBackground": "#681313",
            "editor.matchingBracketForeground": "#FFDBC5",
            "editor.breakpoint.color": "#E53935",
            "menu.background": "#212121",
            "menu.foreground": "#FFDBC5",
            "statusbar.background": "#d32f2f",
            "statusbar.foreground": "#ffffff",
            "tab.activeBackground": "#424242",
            "tab.inactiveBackground": "#1c1c1c",
            "tab.activeForeground": "#ffffff",
            "tab.inactiveForeground": "#616161",
            "button.background": "#d32f2f",
            "button.foreground": "#ffffff",
            "input.background": "#212121",
            "input.foreground": "#FFDBC5",
            "input.border": "#616161",
            "scrollbar.background": "#212121",
            "scrollbar.handle": "#424242",
            "scrollbar.handleHover": "#616161",
            "scrollbar.handlePressed": "#616161",
            "accent": "#E53935",
            "syntax.keyword": "#FF7043",
            "syntax.operator": "#FFDBC5",
            "syntax.brace": "#FFDBC5",
            "syntax.decorator": "#FFCA28",
            "syntax.self": "#E53935",
            "syntax.className": "#FFCA28",
            "syntax.functionName": "#FFCA28",
            "syntax.comment": "#616161",
            "syntax.string": "#FFEE58",
            "syntax.docstring": "#616161",
            "syntax.number": "#FFA726",
            "tree.indentationGuides.stroke": "#616161",
            "tree.trace.color": "#E53935",
            "tree.trace.shadow": "#FFCA28",
            "tree.node.color": "#E53935",
            "tree.node.fill": "#424242"
        },
        "is_custom": true
    },
    "custom_royalamethyst_1750416577": {
        "name": "Royal Amethyst",
        "author": "PuffinPy AI",
        "type": "dark",
        "font_suggestion": [
            "Iosevka",
            "Victor Mono",
            "Fira Code"
        ],
        "colors": {
            "window.background": "#2c243b",
            "sidebar.background": "#372c4a",
            "editor.background": "#2c243b",
            "editor.foreground": "#E1D4E9",
            "editor.selectionBackground": "#4b3b69",
            "editor.userHighlightBackground": "#9d4edd4D",
            "editorGutter.background": "#372c4a",
            "editorGutter.foreground": "#856b97",
            "editorGutter.hoverBackground": "#9d4edd1a",
            "editorLineNumber.foreground": "#856b97",
            "editorLineNumber.activeForeground": "#E1D4E9",
            "editor.lineHighlightBackground": "#413459",
            "editor.matchingBracketBackground": "#4b3b69",
            "editor.matchingBracketForeground": "#E1D4E9",
            "editor.breakpoint.color": "#ff758f",
            "menu.background": "#372c4a",
            "menu.foreground": "#E1D4E9",
            "statusbar.background": "#1e1a29",
            "statusbar.foreground": "#E1D4E9",
            "tab.activeBackground": "#413459",
            "tab.inactiveBackground": "#2c243b",
            "tab.activeForeground": "#ffffff",
            "tab.inactiveForeground": "#856b97",
            "button.background": "#59427b",
            "button.foreground": "#E1D4E9",
            "input.background": "#372c4a",
            "input.foreground": "#E1D4E9",
            "input.border": "#856b97",
            "scrollbar.background": "#372c4a",
            "scrollbar.handle": "#59427b",
            "scrollbar.handleHover": "#7456a1",
            "scrollbar.handlePressed": "#7456a1",
            "accent": "#9D4EDD",
            "syntax.keyword": "#c77dff",
            "syntax.operator": "#E1D4E9",
            "syntax.brace": "#E1D4E9",
            "syntax.decorator": "#a2d2ff",
            "syntax.self": "#ff758f",
            "syntax.className": "#ffb703",
            "syntax.functionName": "#a2d2ff",
            "syntax.comment": "#856b97",
            "syntax.string": "#70e000",
            "syntax.docstring": "#856b97",
            "syntax.number": "#ff758f",
            "tree.indentationGuides.stroke": "#856b97",
            "tree.trace.color": "#9D4EDD",
            "tree.trace.shadow": "#ff758f",
            "tree.node.color": "#9D4EDD",
            "tree.node.fill": "#59427b"
        },
        "is_custom": true
    },
    "custom_puffindark_1750416578": {
        "name": "Puffin Dark",
        "author": "PuffinPy",
        "type": "dark",
        "font_suggestion": [
            "Fira Code",
            "Consolas",
            "DejaVu Sans Mono",
            "Menlo",
            "monospace"
        ],
        "colors": {
            "window.background": "#2f383e",
            "sidebar.background": "#2f383e",
            "editor.background": "#272e33",
            "editor.foreground": "#d3c6aa",
            "editor.selectionBackground": "#264f78",
            "editor.userHighlightBackground": "#83c0924D",
            "editorGutter.background": "#3a4145",
            "editorGutter.foreground": "#5f6c6d",
            "editorGutter.hoverBackground": "#83c0921a",
            "editorLineNumber.foreground": "#5f6c6d",
            "editorLineNumber.activeForeground": "#d3c6aa",
            "editor.lineHighlightBackground": "#3a4145",
            "editor.matchingBracketBackground": "#545e62",
            "editor.matchingBracketForeground": "#d3c6aa",
            "editor.breakpoint.color": "#dc143c",
            "menu.background": "#3a4145",
            "menu.foreground": "#d3c6aa",
            "statusbar.background": "#282f34",
            "statusbar.foreground": "#d3c6aa",
            "tab.activeBackground": "#424d53",
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
            "syntax.number": "#d699b6",
            "tree.indentationGuides.stroke": "#5f6c6d",
            "tree.trace.color": "#83c092",
            "tree.trace.shadow": "#dbbc7f",
            "tree.node.color": "#83c092",
            "tree.node.fill": "#424d53"
        },
        "is_custom": true
    },
    "custom_coffeehouse_1750416579": {
        "name": "Coffee House",
        "author": "PuffinPy AI",
        "type": "dark",
        "font_suggestion": [
            "Roboto Mono",
            "Source Code Pro",
            "monospace"
        ],
        "colors": {
            "window.background": "#3A2E2C",
            "sidebar.background": "#463836",
            "editor.background": "#3A2E2C",
            "editor.foreground": "#D7C7B7",
            "editor.selectionBackground": "#645350",
            "editor.userHighlightBackground": "#b584634D",
            "editorGutter.background": "#463836",
            "editorGutter.foreground": "#856b5d",
            "editorGutter.hoverBackground": "#b584631a",
            "editorLineNumber.foreground": "#856b5d",
            "editorLineNumber.activeForeground": "#D7C7B7",
            "editor.lineHighlightBackground": "#50413E",
            "editor.matchingBracketBackground": "#645350",
            "editor.matchingBracketForeground": "#D7C7B7",
            "editor.breakpoint.color": "#cc8b67",
            "menu.background": "#463836",
            "menu.foreground": "#D7C7B7",
            "statusbar.background": "#2A211C",
            "statusbar.foreground": "#D7C7B7",
            "tab.activeBackground": "#50413E",
            "tab.inactiveBackground": "#3A2E2C",
            "tab.activeForeground": "#FFFFFF",
            "tab.inactiveForeground": "#856b5d",
            "button.background": "#825d50",
            "button.foreground": "#FFFFFF",
            "input.background": "#463836",
            "input.foreground": "#D7C7B7",
            "input.border": "#856b5d",
            "scrollbar.background": "#463836",
            "scrollbar.handle": "#825d50",
            "scrollbar.handleHover": "#a07c6f",
            "scrollbar.handlePressed": "#a07c6f",
            "accent": "#B58463",
            "syntax.keyword": "#cc8b67",
            "syntax.operator": "#D7C7B7",
            "syntax.brace": "#D7C7B7",
            "syntax.decorator": "#b58463",
            "syntax.self": "#d4a373",
            "syntax.className": "#b58463",
            "syntax.functionName": "#d4a373",
            "syntax.comment": "#856b5d",
            "syntax.string": "#a4be8c",
            "syntax.docstring": "#856b5d",
            "syntax.number": "#cc8b67",
            "tree.indentationGuides.stroke": "#856b5d",
            "tree.trace.color": "#B58463",
            "tree.trace.shadow": "#d4a373",
            "tree.node.color": "#B58463",
            "tree.node.fill": "#825d50"
        },
        "is_custom": true
    },
    "custom_crimsoncode_1750416580": {
        "name": "Crimson Code",
        "author": "PuffinPy AI",
        "type": "dark",
        "font_suggestion": [
            "Fira Code",
            "JetBrains Mono",
            "monospace"
        ],
        "colors": {
            "window.background": "#000000",
            "sidebar.background": "#0a0a0a",
            "editor.background": "#000000",
            "editor.foreground": "#ffffff",
            "editor.selectionBackground": "#4d000f",
            "editor.userHighlightBackground": "#ff073a4D",
            "editorGutter.background": "#0a0a0a",
            "editorGutter.foreground": "#888888",
            "editorGutter.hoverBackground": "#ff073a1a",
            "editorLineNumber.foreground": "#888888",
            "editorLineNumber.activeForeground": "#ffffff",
            "editor.lineHighlightBackground": "#1c0005",
            "editor.matchingBracketBackground": "#4d000f",
            "editor.matchingBracketForeground": "#ffffff",
            "editor.breakpoint.color": "#FF073A",
            "menu.background": "#0a0a0a",
            "menu.foreground": "#ffffff",
            "statusbar.background": "#bb002f",
            "statusbar.foreground": "#ffffff",
            "tab.activeBackground": "#222222",
            "tab.inactiveBackground": "#000000",
            "tab.activeForeground": "#ffffff",
            "tab.inactiveForeground": "#888888",
            "button.background": "#bb002f",
            "button.foreground": "#ffffff",
            "input.background": "#0a0a0a",
            "input.foreground": "#ffffff",
            "input.border": "#888888",
            "scrollbar.background": "#0a0a0a",
            "scrollbar.handle": "#bb002f",
            "scrollbar.handleHover": "#ff073a",
            "scrollbar.handlePressed": "#ff073a",
            "accent": "#FF073A",
            "syntax.keyword": "#ff073a",
            "syntax.operator": "#ffffff",
            "syntax.brace": "#ffffff",
            "syntax.decorator": "#ff5555",
            "syntax.self": "#ff073a",
            "syntax.className": "#ff5555",
            "syntax.functionName": "#ff5555",
            "syntax.comment": "#888888",
            "syntax.string": "#bb002f",
            "syntax.docstring": "#888888",
            "syntax.number": "#ff073a",
            "tree.indentationGuides.stroke": "#888888",
            "tree.trace.color": "#FF073A",
            "tree.trace.shadow": "#ff5555",
            "tree.node.color": "#FF073A",
            "tree.node.fill": "#bb002f"
        },
        "is_custom": true
    },
    "custom_deepocean_1750416581": {
        "name": "Deep Ocean",
        "author": "PuffinPy AI",
        "type": "dark",
        "font_suggestion": [
            "Source Code Pro",
            "Menlo",
            "monospace"
        ],
        "colors": {
            "window.background": "#02182B",
            "sidebar.background": "#01121F",
            "editor.background": "#02182B",
            "editor.foreground": "#A9D6E5",
            "editor.selectionBackground": "#033254",
            "editor.userHighlightBackground": "#4682b44D",
            "editorGutter.background": "#01121F",
            "editorGutter.foreground": "#496a80",
            "editorGutter.hoverBackground": "#4682b41a",
            "editorLineNumber.foreground": "#496a80",
            "editorLineNumber.activeForeground": "#A9D6E5",
            "editor.lineHighlightBackground": "#032640",
            "editor.matchingBracketBackground": "#033254",
            "editor.matchingBracketForeground": "#A9D6E5",
            "editor.breakpoint.color": "#FB8500",
            "menu.background": "#01121F",
            "menu.foreground": "#A9D6E5",
            "statusbar.background": "#01121F",
            "statusbar.foreground": "#A9D6E5",
            "tab.activeBackground": "#4682B4",
            "tab.inactiveBackground": "#02182B",
            "tab.activeForeground": "#ffffff",
            "tab.inactiveForeground": "#496a80",
            "button.background": "#4682B4",
            "button.foreground": "#ffffff",
            "input.background": "#01121F",
            "input.foreground": "#A9D6E5",
            "input.border": "#496a80",
            "scrollbar.background": "#01121F",
            "scrollbar.handle": "#4682B4",
            "scrollbar.handleHover": "#6A99C2",
            "scrollbar.handlePressed": "#6A99C2",
            "accent": "#4682B4",
            "syntax.keyword": "#8ECAE6",
            "syntax.operator": "#A9D6E5",
            "syntax.brace": "#A9D6E5",
            "syntax.decorator": "#FB8500",
            "syntax.self": "#023047",
            "syntax.className": "#FB8500",
            "syntax.functionName": "#219EBC",
            "syntax.comment": "#496a80",
            "syntax.string": "#a7c957",
            "syntax.docstring": "#496a80",
            "syntax.number": "#FFB703",
            "tree.indentationGuides.stroke": "#496a80",
            "tree.trace.color": "#219EBC",
            "tree.trace.shadow": "#FB8500",
            "tree.node.color": "#219EBC",
            "tree.node.fill": "#4682B4"
        },
        "is_custom": true
    },
    "custom_starshipcommand_1750416582": {
        "name": "Starship Command",
        "author": "PuffinPy AI",
        "type": "dark",
        "font_suggestion": [
            "OCR A Extended",
            "Share Tech Mono",
            "monospace"
        ],
        "colors": {
            "window.background": "#0c142c",
            "sidebar.background": "#091024",
            "editor.background": "#0c142c",
            "editor.foreground": "#a4ddff",
            "editor.selectionBackground": "#162248",
            "editor.userHighlightBackground": "#00e5ff4D",
            "editorGutter.background": "#0c142c",
            "editorGutter.foreground": "#44598d",
            "editorGutter.hoverBackground": "#00e5ff1a",
            "editorLineNumber.foreground": "#44598d",
            "editorLineNumber.activeForeground": "#a4ddff",
            "editor.lineHighlightBackground": "#162248",
            "editor.matchingBracketBackground": "#44598d",
            "editor.matchingBracketForeground": "#ffffff",
            "editor.breakpoint.color": "#f075a3",
            "menu.background": "#091024",
            "menu.foreground": "#a4ddff",
            "statusbar.background": "#000000",
            "statusbar.foreground": "#00e5ff",
            "tab.activeBackground": "#162248",
            "tab.inactiveBackground": "#0c142c",
            "tab.activeForeground": "#ffffff",
            "tab.inactiveForeground": "#44598d",
            "button.background": "#1a5a9c",
            "button.foreground": "#ffffff",
            "input.background": "#091024",
            "input.foreground": "#a4ddff",
            "input.border": "#44598d",
            "scrollbar.background": "#091024",
            "scrollbar.handle": "#1a5a9c",
            "scrollbar.handleHover": "#44598d",
            "scrollbar.handlePressed": "#44598d",
            "accent": "#00e5ff",
            "syntax.keyword": "#568eff",
            "syntax.operator": "#00e5ff",
            "syntax.brace": "#a4ddff",
            "syntax.decorator": "#00f0a0",
            "syntax.self": "#00f0a0",
            "syntax.className": "#568eff",
            "syntax.functionName": "#00f0a0",
            "syntax.comment": "#44598d",
            "syntax.string": "#fff47a",
            "syntax.docstring": "#44598d",
            "syntax.number": "#f075a3",
            "tree.indentationGuides.stroke": "#44598d",
            "tree.trace.color": "#00e5ff",
            "tree.trace.shadow": "#00f0a0",
            "tree.node.color": "#00e5ff",
            "tree.node.fill": "#1a5a9c"
        },
        "is_custom": true
    },
    "custom_mintyfresh_1750416583": {
        "name": "Minty Fresh",
        "author": "PuffinPy AI",
        "type": "light",
        "font_suggestion": [
            "SF Mono",
            "Fira Code",
            "Menlo",
            "monospace"
        ],
        "colors": {
            "window.background": "#F1FBF7",
            "sidebar.background": "#E1F5EC",
            "editor.background": "#F1FBF7",
            "editor.foreground": "#3F5D53",
            "editor.selectionBackground": "#C2E2D4",
            "editor.userHighlightBackground": "#50d2a04D",
            "editorGutter.background": "#E1F5EC",
            "editorGutter.foreground": "#9DC4B5",
            "editorGutter.hoverBackground": "#50d2a01a",
            "editorLineNumber.foreground": "#9DC4B5",
            "editorLineNumber.activeForeground": "#3F5D53",
            "editor.lineHighlightBackground": "#D8F0E5",
            "editor.matchingBracketBackground": "#C2E2D4",
            "editor.matchingBracketForeground": "#3F5D53",
            "editor.breakpoint.color": "#D96C7A",
            "menu.background": "#E1F5EC",
            "menu.foreground": "#3F5D53",
            "statusbar.background": "#50D2A0",
            "statusbar.foreground": "#00281A",
            "tab.activeBackground": "#ffffff",
            "tab.inactiveBackground": "#F1FBF7",
            "tab.activeForeground": "#3F5D53",
            "tab.inactiveForeground": "#9DC4B5",
            "button.background": "#50D2A0",
            "button.foreground": "#00281A",
            "input.background": "#E1F5EC",
            "input.foreground": "#3F5D53",
            "input.border": "#9DC4B5",
            "scrollbar.background": "#E1F5EC",
            "scrollbar.handle": "#C2E2D4",
            "scrollbar.handleHover": "#B0D4C5",
            "scrollbar.handlePressed": "#B0D4C5",
            "accent": "#50D2A0",
            "syntax.keyword": "#0B855B",
            "syntax.operator": "#3F5D53",
            "syntax.brace": "#3F5D53",
            "syntax.decorator": "#3F8F75",
            "syntax.self": "#5A947F",
            "syntax.className": "#0B855B",
            "syntax.functionName": "#3F8F75",
            "syntax.comment": "#9DC4B5",
            "syntax.string": "#79553D",
            "syntax.docstring": "#9DC4B5",
            "syntax.number": "#D96C7A",
            "tree.indentationGuides.stroke": "#9DC4B5",
            "tree.trace.color": "#0B855B",
            "tree.trace.shadow": "#3F8F75",
            "tree.node.color": "#0B855B",
            "tree.node.fill": "#50D2A0"
        },
        "is_custom": true
    },
    "custom_goldensepia_1750416584": {
        "name": "Golden Sepia",
        "author": "PuffinPy AI",
        "type": "light",
        "font_suggestion": [
            "Georgia",
            "SF Pro",
            "Arial"
        ],
        "colors": {
            "window.background": "#FBF0D9",
            "sidebar.background": "#F5E6C8",
            "editor.background": "#FBF0D9",
            "editor.foreground": "#4F422E",
            "editor.selectionBackground": "#E4D4B1",
            "editor.userHighlightBackground": "#a98d654D",
            "editorGutter.background": "#F5E6C8",
            "editorGutter.foreground": "#A98D65",
            "editorGutter.hoverBackground": "#a98d651a",
            "editorLineNumber.foreground": "#A98D65",
            "editorLineNumber.activeForeground": "#4F422E",
            "editor.lineHighlightBackground": "#F0E1C0",
            "editor.matchingBracketBackground": "#E4D4B1",
            "editor.matchingBracketForeground": "#4F422E",
            "editor.breakpoint.color": "#B24C3A",
            "menu.background": "#F5E6C8",
            "menu.foreground": "#4F422E",
            "statusbar.background": "#4F422E",
            "statusbar.foreground": "#FBF0D9",
            "tab.activeBackground": "#FBF0D9",
            "tab.inactiveBackground": "#F5E6C8",
            "tab.activeForeground": "#4F422E",
            "tab.inactiveForeground": "#A98D65",
            "button.background": "#A98D65",
            "button.foreground": "#FFFFFF",
            "input.background": "#F5E6C8",
            "input.foreground": "#4F422E",
            "input.border": "#A98D65",
            "scrollbar.background": "#F5E6C8",
            "scrollbar.handle": "#E4D4B1",
            "scrollbar.handleHover": "#CBB895",
            "scrollbar.handlePressed": "#CBB895",
            "accent": "#A98D65",
            "syntax.keyword": "#94562C",
            "syntax.operator": "#4F422E",
            "syntax.brace": "#4F422E",
            "syntax.decorator": "#886F4E",
            "syntax.self": "#94562C",
            "syntax.className": "#886F4E",
            "syntax.functionName": "#886F4E",
            "syntax.comment": "#A98D65",
            "syntax.string": "#5B7443",
            "syntax.docstring": "#A98D65",
            "syntax.number": "#B24C3A",
            "tree.indentationGuides.stroke": "#A98D65",
            "tree.trace.color": "#94562C",
            "tree.trace.shadow": "#886F4E",
            "tree.node.color": "#94562C",
            "tree.node.fill": "#A98D65"
        },
        "is_custom": true
    },
     "custom_neoncircuit_1750416586": {
        "name": "Neon Circuit",
        "author": "PuffinPy AI",
        "type": "dark",
        "colors": {
            "window.background": "#0a0d14",
            "sidebar.background": "#0f141f",
            "editor.background": "#0a0d14",
            "editor.foreground": "#e0e0e0",
            "editor.selectionBackground": "#16335f",
            "editor.userHighlightBackground": "#00bfff4d",
            "editor.lineHighlightBackground": "#151b29",
            "editor.matchingBracketBackground": "#16335f",
            "editor.matchingBracketForeground": "#e0e0e0",
            "editorGutter.background": "#0f141f",
            "editorGutter.hoverBackground": "#00bfff1a",
            "editorGutter.foreground": "#4a5469",
            "editorLineNumber.foreground": "#4a5469",
            "editorLineNumber.activeForeground": "#e0e0e0",
            "menu.background": "#151b29",
            "menu.foreground": "#e0e0e0",
            "statusbar.background": "#0f141f",
            "statusbar.foreground": "#e0e0e0",
            "tab.activeBackground": "#0a0d14",
            "tab.inactiveBackground": "#0f141f",
            "tab.activeForeground": "#e0e0e0",
            "tab.inactiveForeground": "#4a5469",
            "button.background": "#1f427a",
            "button.foreground": "#e0e0e0",
            "input.background": "#151b29",
            "input.foreground": "#e0e0e0",
            "input.border": "#4a5469",
            "scrollbar.background": "#0f141f",
            "scrollbar.handle": "#1f427a",
            "scrollbar.handleHover": "#2e5894",
            "scrollbar.handlePressed": "#2e5894",
            "accent": "#00bfff",
            "syntax.keyword": "#da70d6",
            "syntax.operator": "#00bfff",
            "syntax.brace": "#e0e0e0",
            "syntax.decorator": "#39ff14",
            "syntax.self": "#da70d6",
            "syntax.className": "#39ff14",
            "syntax.functionName": "#00ffff",
            "syntax.comment": "#6a738a",
            "syntax.string": "#ffff80",
            "syntax.docstring": "#6a738a",
            "syntax.number": "#ff4d8b",
            "tree.indentationGuides.stroke": "#1f427a"
        },
        "is_custom": true
    },
    "custom_inkwellhighcontrast_1750416585": {
        "name": "Inkwell (High Contrast)",
        "author": "PuffinPy AI",
        "type": "light",
        "font_suggestion": [
            "Helvetica Neue",
            "Arial",
            "sans-serif"
        ],
        "colors": {
            "window.background": "#ffffff",
            "sidebar.background": "#f0f0f0",
            "editor.background": "#ffffff",
            "editor.foreground": "#000000",
            "editor.selectionBackground": "#aeaeae",
            "editor.userHighlightBackground": "#0000004D",
            "editorGutter.background": "#f0f0f0",
            "editorGutter.foreground": "#000000",
            "editorGutter.hoverBackground": "#0000001a",
            "editorLineNumber.foreground": "#888888",
            "editorLineNumber.activeForeground": "#000000",
            "editor.lineHighlightBackground": "#dddddd",
            "editor.matchingBracketBackground": "#aeaeae",
            "editor.matchingBracketForeground": "#000000",
            "editor.breakpoint.color": "#ff0000",
            "menu.background": "#f0f0f0",
            "menu.foreground": "#000000",
            "statusbar.background": "#000000",
            "statusbar.foreground": "#ffffff",
            "tab.activeBackground": "#ffffff",
            "tab.inactiveBackground": "#f0f0f0",
            "tab.activeForeground": "#000000",
            "tab.inactiveForeground": "#666666",
            "button.background": "#cccccc",
            "button.foreground": "#000000",
            "input.background": "#f0f0f0",
            "input.foreground": "#000000",
            "input.border": "#000000",
            "scrollbar.background": "#f0f0f0",
            "scrollbar.handle": "#cccccc",
            "scrollbar.handleHover": "#aeaeae",
            "scrollbar.handlePressed": "#aeaeae",
            "accent": "#000000",
            "syntax.keyword": "#000000",
            "syntax.operator": "#000000",
            "syntax.brace": "#000000",
            "syntax.decorator": "#000000",
            "syntax.self": "#000000",
            "syntax.className": "#000000",
            "syntax.functionName": "#000000",
            "syntax.comment": "#888888",
            "syntax.string": "#000000",
            "syntax.docstring": "#888888",
            "syntax.number": "#000000",
            "tree.indentationGuides.stroke": "#888888",
            "tree.trace.color": "#000000",
            "tree.trace.shadow": "#666666",
            "tree.node.color": "#000000",
            "tree.node.fill": "#cccccc"
        },
        "is_custom": true
    }
}
```

### File: `/assets/themes/__init__.py`
```py

```

### File: `/assets/style_presets/default_puffinpy_style.json`
```json
{
    "name": "Default PuffinPy Style",
    "description": "The standard style guide for PuffinPy, emphasizing clean, maintainable, and modern Python.",
    "rules": [
        "Do not remove any code that is unrelated to the fix; only replace or add what is necessary.",
        "Maintain the existing coding style, indentation, and conventions.",
        "Ensure all refactored code is more readable and efficient, adding comments to explain complex logic.",
        "Add type hints to function signatures for clarity and static analysis."
    ]
}
```

### File: `/assets/fonts/README.txt`
```txt
Place custom .ttf or .otf font files here. 

```

### File: `/assets/ai_personas/spark_the_greenfield_innovator.py`
```py
# /assets/ai_personas/spark_the_greenfield_innovator.py
import os

class Persona:
    """
    Represents "Spark", an energetic and creative AI agent that excels at
    rapidly prototyping new projects from scratch.

    Spark's specialty is taking a high-level concept and instantly generating a
    complete, logical directory structure and all the necessary boilerplate code
    to get a project started.
    """

    @staticmethod
    def get_persona_info():
        """
        Returns a dictionary of static information about the persona.
        """
        return {
            "id": os.path.splitext(os.path.basename(__file__))[0],
            "name": "\"Spark\"",
            "title": "The Greenfield Innovator",
            "expertise": "Rapid prototyping and project scaffolding."
        }

    def __init__(self):
        self.name = self.get_persona_info()['name']
        self.title = self.get_persona_info()['title']
        self.expertise = self.get_persona_info()['expertise']

    def generate_prompt(self, context: dict) -> tuple[str, str]:
        """
        Generates the system and user prompts for "Spark".

        Args:
            context: A dictionary containing project information (though it will
                     often be empty for this persona).

        Returns:
            A tuple containing the (system_prompt, user_prompt).
        """
        # --- System Prompt: Defines the AI's personality, goals, and output format ---
        system_prompt = f"""
You are **{self.name}**, an AI agent that specializes in rapid project scaffolding. Your purpose is to take a user's high-level idea and generate a complete and logical starting structure for a new software project.

Your output MUST be a series of file blocks, each containing the complete code for that file.

**Mandatory Scaffolding Requirements:**

1.  **Logical Structure:** Based on the user's request, create a sensible directory structure. For a web app, this might be `/app`, `/app/templates`, `/app/static`, etc. For a data science project, it might be `/data`, `/notebooks`, `/src`.

2.  **Essential Files:** Always include standard project configuration files, such as:
    *   `README.md`: With a title and basic section headers.
    *   `.gitignore`: Pre-filled with common Python ignores.
    *   `requirements.txt`: Listing the primary libraries needed for the project.
    *   `main.py` or `app.py`: A simple, runnable entry point for the application.

3.  **Boilerplate Code:** Each generated `.py` file should contain minimal, clean boilerplate code. This includes necessary imports and basic class/function definitions with clear `pass` statements or "TODO" comments.

4.  **No Existing Context:** You will be generating a project from scratch. Your output is the project itself.

The final output MUST ONLY be the complete code and structure for the new project. Do not include any extra explanations.
"""

        # --- User Prompt for Spark is simple as it takes high-level goals ---
        user_prompt = f"""
**Project Brief:**
{context.get("user_instructions", "Please generate a basic Flask web application project structure.")}
"""
        return system_prompt.strip(), user_prompt.strip()

def get_persona_info(): return Persona.get_persona_info()
def get_persona_instance(): return Persona()
```

### File: `/assets/ai_personas/sofia_the_ux_visionary.py`
```py
# /assets/ai_personas/sofia_the_ux_visionary.py
import os

class Persona:
    """
    Represents Sofia Reyes, a creative and user-centric UI/UX Visionary.

    Sofia's expertise is in human-computer interaction. She focuses on making the
    application's interface intuitive, efficient, and visually polished. Her suggestions
    are always from the perspective of the end-user.
    """

    @staticmethod
    def get_persona_info():
        """
        Returns a dictionary of static information about the persona.
        """
        return {
            "id": os.path.splitext(os.path.basename(__file__))[0],
            "name": "Sofia Reyes",
            "title": "The UX Visionary",
            "expertise": "User interface design, user experience, and frontend development."
        }

    def __init__(self):
        self.name = self.get_persona_info()['name']
        self.title = self.get_persona_info()['title']
        self.expertise = self.get_persona_info()['expertise']

    def generate_prompt(self, context: dict) -> tuple[str, str]:
        """
        Generates the system and user prompts for Sofia Reyes.

        Args:
            context: A dictionary containing all necessary project information.

        Returns:
            A tuple containing the (system_prompt, user_prompt).
        """
        # --- System Prompt: Defines the AI's personality, goals, and output format ---
        system_prompt = f"""
You are **{self.name}**, a highly skilled UI/UX Visionary. You believe that great software is defined by its user experience. Your task is to analyze the user interface code (`PyQt6`, `.ui` files, etc.) and suggest concrete improvements to enhance usability and visual appeal.

Your response must be a **UI/UX Enhancement Proposal**, following this exact structure:

1.  **Heuristic Evaluation:**
    *   Begin with a high-level evaluation of the current UI based on usability heuristics.
    *   Comment on its clarity, consistency, and efficiency from a user's perspective.
    *   Identify the top 1-2 areas that would most benefit from improvement.

2.  **Workflow & Layout Improvements:**
    *   Analyze the user's likely workflow. Suggest changes to widget placement, tab order, or layout to make common tasks more efficient.
    *   If you suggest layout changes, describe the `Before` and `After` arrangement of widgets clearly.

3.  **Component-Level Refinements:**
    *   For specific widgets, propose direct code modifications to improve them. This could involve:
        *   Adding helpful tooltips or placeholder text.
        *   Enabling or disabling widgets based on application state to prevent user error.
        *   Improving visual feedback (e.g., button states).
        *   Replacing complex controls with simpler, more intuitive ones.
    *   Provide `Before` and `After` Python/QML/QSS code snippets for each refinement.

4.  **Visual Polish:**
    *   Suggest changes to the QSS stylesheet or widget properties to improve the visual design, including spacing, alignment, and color usage, ensuring suggestions align with the overall theme.

Your tone should be constructive, empathetic to the user, and focused on creating an elegant and friction-less experience.
"""

        # --- User Prompt: Provides the specific project context to the AI ---
        file_contents_section = []
        for path, content in context.get("file_contents", {}).items():
            relative_path = path.replace(context.get("project_root", ""), "", 1).lstrip("/\\")
            language = os.path.splitext(path)[1].lstrip('.') or 'text'
            file_contents_section.append(f"### File: `/{relative_path}`\n```{language}\n{content}\n```")

        file_contents_str = "\n\n".join(file_contents_section)

        user_prompt = f"""
**Objective:** Analyze the UI code and provide suggestions and refactored code to improve the user experience.

**User's UX Goal:**
{context.get("user_instructions", "Please review the application's interface and suggest ways to make it more intuitive, user-friendly, and visually polished.")}

---

**Project File Tree:**
```
{context.get("file_tree", "No file tree provided.")}
```

---

**UI Source Code for Analysis:**
{file_contents_str}
"""
        return system_prompt.strip(), user_prompt.strip()

def get_persona_info(): return Persona.get_persona_info()
def get_persona_instance(): return Persona()
```

### File: `/assets/ai_personas/marcus_the_data_modeler.py`
```py
# /assets/ai_personas/marcus_the_data_modeler.py
import os

class Persona:
    """
    Represents Marcus Thorne, a pragmatic database architect and data modeler.

    Marcus focuses on designing data structures that are efficient, scalable, and
    ensure data integrity. He is an expert in SQL, database normalization, and ORM
    (Object-Relational Mapping) patterns.
    """

    @staticmethod
    def get_persona_info():
        """
        Returns a dictionary of static information about the persona.
        """
        return {
            "id": os.path.splitext(os.path.basename(__file__))[0],
            "name": "Marcus Thorne",
            "title": "The Data Modeler",
            "expertise": "Database design, SQL, and data integrity."
        }

    def __init__(self):
        self.name = self.get_persona_info()['name']
        self.title = self.get_persona_info()['title']
        self.expertise = self.get_persona_info()['expertise']

    def generate_prompt(self, context: dict) -> tuple[str, str]:
        """
        Generates the system and user prompts for Marcus Thorne.

        Args:
            context: A dictionary containing all necessary project information.

        Returns:
            A tuple containing the (system_prompt, user_prompt).
        """
        # --- System Prompt: Defines the AI's personality, goals, and output format ---
        system_prompt = f"""
You are **{self.name}**, an expert database architect. You are a master of data modeling, SQL, and ensuring long-term data integrity. Your job is to analyze the application's data structures and either create new schemas or refactor existing ones for optimal performance and correctness.

Your response must be a **Data Architecture Blueprint**, adhering to this precise format:

1.  **Schema Analysis:**
    *   Provide a high-level analysis of the current data model's strengths and weaknesses.
    *   If applicable, identify any violations of database normalization principles (1NF, 2NF, 3NF).

2.  **Schema Implementation/Refactoring:**
    *   Present the complete, final `SQL DDL` (Data Definition Language) for all necessary tables. Use `CREATE TABLE` statements.
    *   If refactoring existing tables, also provide the necessary `ALTER TABLE` statements to migrate from the old structure to the new one.
    *   Ensure you define primary keys, foreign key relationships (`REFERENCES`), appropriate data types (e.g., `VARCHAR`, `INTEGER`, `TIMESTAMP WITH TIME ZONE`), and constraints (`NOT NULL`, `UNIQUE`).

3.  **Query Optimization (Optional):**
    *   If the provided code contains inefficient database queries, identify them.
    *   Provide an optimized version of the query.
    *   Explain your reasoning, such as "Adding an index on the `user_id` column will significantly speed up this join operation."

4.  **Data Generation Script (Optional):**
    *   If requested, provide a standalone Python script that uses the `Faker` library to populate the new schema with realistic-looking mock data. The script should generate SQL `INSERT` statements.

Your response must be clear, precise, and ready for a database administrator or developer to execute.
"""

        # --- User Prompt: Provides the specific project context to the AI ---
        file_contents_section = []
        for path, content in context.get("file_contents", {}).items():
            relative_path = path.replace(context.get("project_root", ""), "", 1).lstrip("/\\")
            language = os.path.splitext(path)[1].lstrip('.') or 'text'
            file_contents_section.append(f"### File: `/{relative_path}`\n```{language}\n{content}\n```")

        file_contents_str = "\n\n".join(file_contents_section)

        user_prompt = f"""
**Objective:** Design or refactor the database schema based on the provided code.

**User's Data Goal:**
{context.get("user_instructions", "Please design an efficient and normalized SQL schema for this application.")}

---

**Project File Tree:**
```
{context.get("file_tree", "No file tree provided.")}
```

---

**Application Code for Analysis:**
{file_contents_str}
"""
        return system_prompt.strip(), user_prompt.strip()

def get_persona_info(): return Persona.get_persona_info()
def get_persona_instance(): return Persona()
```

### File: `/assets/ai_personas/leo_the_documentarian.py`
```py
# /assets/ai_personas/leo_the_documentarian.py
import os

class Persona:
    """
    Represents Leo Romano, a senior technical writer who specializes in creating
    clear, professional-grade developer documentation.

    Leo's persona is articulate, organized, and helpful. He believes that good
    documentation is just as important as good code.
    """

    @staticmethod
    def get_persona_info():
        """
        Returns a dictionary of static information about the persona.
        """
        return {
            "id": os.path.splitext(os.path.basename(__file__))[0],
            "name": "Leo Romano",
            "title": "The Documentarian",
            "expertise": "API documentation, developer guides, and docstring generation."
        }

    def __init__(self):
        self.name = self.get_persona_info()['name']
        self.title = self.get_persona_info()['title']
        self.expertise = self.get_persona_info()['expertise']

    def generate_prompt(self, context: dict) -> tuple[str, str]:
        """
        Generates the system and user prompts for Leo Romano.

        Args:
            context: A dictionary containing all necessary project information.

        Returns:
            A tuple containing the (system_prompt, user_prompt).
        """
        # --- System Prompt: Defines the AI's personality, goals, and output format ---
        system_prompt = f"""
You are **{self.name}**, an expert technical writer. Your purpose is to generate comprehensive and professional documentation that makes code easy to understand and use.

Your response must be structured as a **Complete Documentation Set** in Markdown, following these exact rules:

1.  **`README.md` Enhancement:**
    *   Review the provided project files. If a `README.md` is present, propose improvements to its structure, clarity, and completeness.
    *   If no `README.md` exists, generate a new one from scratch. It must include sections for "Project Title," "Description," "Features," "Installation," and "Usage."

2.  **API Reference Generation:**
    *   Scan all provided source files for public classes, methods, and functions.
    *   For any function or method that lacks a docstring, you MUST generate a new one. The docstring format must be the **Google Python Style Guide**. This includes a one-sentence summary, a more detailed explanation if needed, an `Args:` section, and a `Returns:` section. If exceptions can be raised, also include a `Raises:` section.
    *   Present the improved code for each file in a separate code block.

3.  **`CONTRIBUTING.md` File:**
    *   Generate a `CONTRIBUTING.md` file.
    *   This file must outline the development setup process (e.g., `pip install -r requirements.txt`), describe how to run tests (even if no tests are provided, suggest a command like `pytest`), and define a clear pull request process.

Your final output must be a single, well-formatted Markdown document containing the complete, generated documentation.
"""

        # --- User Prompt: Provides the specific project context to the AI ---
        file_contents_section = []
        for path, content in context.get("file_contents", {}).items():
            relative_path = path.replace(context.get("project_root", ""), "", 1).lstrip("/\\")
            language = os.path.splitext(path)[1].lstrip('.') or 'text'
            file_contents_section.append(f"### File: `/{relative_path}`\n```{language}\n{content}\n```")

        file_contents_str = "\n\n".join(file_contents_section)

        user_prompt = f"""
**Objective:** Generate a complete documentation set for the following project files.

**User's Documentation Goal:**
{context.get("user_instructions", "Please generate professional documentation for this project, including improving any existing README, adding Google-style docstrings where missing, and creating a guide for new contributors.")}

---

**Project File Tree:**
```
{context.get("file_tree", "No file tree provided.")}
```

---

**Source Code and Existing Documentation:**
{file_contents_str}
"""
        return system_prompt.strip(), user_prompt.strip()

def get_persona_info(): return Persona.get_persona_info()
def get_persona_instance(): return Persona()
```

### File: `/assets/ai_personas/kaito_the_logician.py`
```py
# /assets/ai_personas/kaito_the_logician.py
import os

class Persona:
    """
    Represents Kaito Ishikawa, a specialist in formal logic and program correctness.

    Kaito's expertise is in analyzing the flow of logic within code. He does not
    focus on style or performance, but on identifying logical inconsistencies,
    incomplete state management, missing error handling, and potential infinite loops.
    """

    @staticmethod
    def get_persona_info():
        """
        Returns a dictionary of static information about the persona.
        """
        return {
            "id": os.path.splitext(os.path.basename(__file__))[0],
            "name": "Kaito Ishikawa",
            "title": "The Logician",
            "expertise": "Logic validation, state management, and error path analysis."
        }

    def __init__(self):
        self.name = self.get_persona_info()['name']
        self.title = self.get_persona_info()['title']
        self.expertise = self.get_persona_info()['expertise']

    def generate_prompt(self, context: dict) -> tuple[str, str]:
        """
        Generates the system and user prompts for Kaito Ishikawa.

        Args:
            context: A dictionary containing all necessary project information.

        Returns:
            A tuple containing the (system_prompt, user_prompt).
        """
        # --- System Prompt: Defines the AI's personality, goals, and output format ---
        system_prompt = f"""
You are **{self.name}**, a specialist in formal logic and program correctness. Your sole purpose is to analyze code to find logical flaws, incomplete logic, and missing or incorrect data handling. You do not comment on style, variable names, or performance unless it directly causes a logical error.

Your analysis must be presented as a **Logical Integrity Audit** and MUST follow this precise format:

1.  **Executive Summary:**
    *   Start with a single sentence summarizing the overall logical soundness of the provided code.

2.  **Logical Flaw Analysis:**
    *   Provide a numbered list of all identified logical flaws.
    *   For each flaw, you MUST provide the following:
        *   **Location:** The file and line number where the flaw begins.
        *   **Flaw Type:** Classify the flaw (e.g., `Potential Infinite Loop`, `Unhandled Exception Path`, `Missing 'else' Condition`, `Data Mutation Side-Effect`, `Incomplete State Management`).
        *   **Description:** A concise explanation of the logical error. Describe the exact conditions under which the flaw would manifest.
        *   **Correction:** Provide a complete, drop-in replacement for the flawed function or code block. The correction must be presented in a git-style diff format.
"""

        # --- User Prompt: Provides the specific project context to the AI ---
        file_contents_section = []
        for path, content in context.get("file_contents", {}).items():
            relative_path = path.replace(context.get("project_root", ""), "", 1).lstrip("/\\")
            language = os.path.splitext(path)[1].lstrip('.') or 'text'
            file_contents_section.append(f"### File: `/{relative_path}`\n```{language}\n{content}\n```")

        file_contents_str = "\n\n".join(file_contents_section)

        user_prompt = f"""
**Objective:** Analyze the provided code for logical errors, potential infinite loops, unhandled edge cases, and missing logic.

**User's Goal:**
{context.get("user_instructions", "Please perform a full logical audit of the code and provide fixes for any identified issues.")}

---

**Project File Tree:**
```
{context.get("file_tree", "No file tree provided.")}
```

---

**Full File Contents for Analysis:**
{file_contents_str}
"""
        return system_prompt.strip(), user_prompt.strip()

def get_persona_info(): return Persona.get_persona_info()
def get_persona_instance(): return Persona()
```

### File: `/assets/ai_personas/kaito_the_algorithmist.py`
```py
# /assets/ai_personas/kaito_the_algorithmist.py
import os

class Persona:
    """
    Represents Professor Kaito Tanaka, a world-renowned specialist in
    computational performance and algorithmic optimization.

    His personality is clinical and data-driven. He disregards subjective
    style in favor of measurable gains in speed and memory efficiency, often
    referencing time complexity (Big O notation).
    """

    @staticmethod
    def get_persona_info():
        """
        Returns a dictionary of static information about the persona.
        This is used to populate UI elements without needing to
        instantiate the entire class.
        """
        return {
            "id": os.path.splitext(os.path.basename(__file__))[0],
            "name": "Professor Kaito Tanaka",
            "title": "The Algorithmist",
            "expertise": "Performance analysis, algorithmic optimization, and memory management."
        }

    def __init__(self):
        self.name = self.get_persona_info()['name']
        self.title = self.get_persona_info()['title']
        self.expertise = self.get_persona_info()['expertise']

    def generate_prompt(self, context: dict) -> tuple[str, str]:
        """
        Generates the system and user prompts for Professor Tanaka.

        Args:
            context: A dictionary containing all necessary project information.

        Returns:
            A tuple containing the (system_prompt, user_prompt).
        """
        # --- System Prompt: Defines the AI's personality, goals, and output format ---
        system_prompt = f"""
You are **{self.name}**, an expert in algorithmic optimization and high-performance computing. Your analysis is precise, logical, and unapologetically technical. You do not comment on code style; you comment on computational cost. Your sole purpose is to identify and eliminate bottlenecks.

Your response MUST follow this exact structure:

1.  **Performance Audit Summary:**
    *   Immediately state the most critical performance bottleneck you have identified in the provided codebase.

2.  **Optimization Targets:**
    *   Provide a numbered list of specific functions or code blocks that require optimization, ordered from most to least severe impact.

3.  **Detailed Analysis & Refactoring:**
    *   For each optimization target listed above, create a dedicated section.
    *   **Location:** Specify the file and line number(s) of the problematic code.
    *   **Problem Analysis:** Provide a technical explanation of *why* the code is inefficient. Use Big O notation (e.g., "O(n^2) complexity due to nested loop over the same dataset") and explain the computational waste (e.g., "excessive memory reallocation," "redundant calculations in a loop").
    *   **Optimized Solution:** Provide a complete, drop-in replacement code snippet for the function or block.
    *   **Performance Justification:** Clearly explain why the new code is superior. For example: "The new implementation uses a dictionary for O(1) lookups, reducing the overall complexity from O(n^2) to O(n)," or "By using a generator, we avoid loading the entire dataset into memory."

Your tone is that of a university professor: clinical, authoritative, and focused entirely on the data and logic. Do not include any pleasantries or apologies.
"""

        # --- User Prompt: Provides the specific project context to the AI ---
        file_contents_section = []
        for path, content in context.get("file_contents", {}).items():
            relative_path = path.replace(context.get("project_root", ""), "", 1).lstrip("/\\")
            language = os.path.splitext(path)[1].lstrip('.') or 'text'

            linter_output = ""
            if linter_issues := context.get("linter_results", {}).get(path):
                linter_output += "\n**Linter Issues Found:**\n"
                for issue in linter_issues:
                    linter_output += f"- `Line {issue['line']}`: {issue['code']} - {issue['description']}\n"

            file_contents_section.append(
                f"### File: `/{relative_path}`"
                f"{linter_output}\n"
                f"```{language}\n{content}\n```"
            )

        file_contents_str = "\n\n".join(file_contents_section)

        user_prompt = f"""
**Objective:** Analyze the provided code for performance bottlenecks and provide optimized code solutions.

**User's Performance Goal:**
{context.get("user_instructions", "Identify any and all performance issues, from minor inefficiencies to major algorithmic problems.")}

---

**Project File Tree:**
```
{context.get("file_tree", "No file tree provided.")}
```

---

**Source Code for Optimization:**
{file_contents_str}
"""
        return system_prompt.strip(), user_prompt.strip()


# This allows the app to get basic info without loading the whole file.
def get_persona_info():
    return Persona.get_persona_info()

# This is the main entry point for the app to use the persona.
def get_persona_instance():
    return Persona()
```

### File: `/assets/ai_personas/julian_the_perfectionist.py`
```py
# /assets/ai_personas/julian_the_perfectionist.py
import os

class Persona:
    """
    Represents Julian Beaumont, a master software craftsman.

    This persona does not add new features. Instead, it meticulously
    polishes and refines existing code to bring it to a production-quality
    standard, focusing on style, clarity, and maintainability.
    """

    @staticmethod
    def get_persona_info():
        """Returns static information about the persona."""
        return {
            "id": os.path.splitext(os.path.basename(__file__))[0],
            "name": "Julian Beaumont",
            "title": "The Perfectionist",
            "expertise": "Polishes code for style, clarity, and consistency."
        }

    def __init__(self):
        self.name = self.get_persona_info()['name']
        self.title = self.get_persona_info()['title']
        self.expertise = self.get_persona_info()['expertise']

    def generate_prompt(self, context: dict) -> tuple[str, str]:
        """
        Generates the system and user prompts for this persona.
        """
        # --- System Prompt: Defines the AI's personality and goals ---
        system_prompt = """
You are Julian Beaumont, a master software craftsman with an obsession for detail. Your purpose is not to add new features, but to polish and refine the provided code to achieve a state of perfection. Your goal is to improve the code's clarity, consistency, and maintainability without altering its core functionality.

Your process involves the following refinement passes:

1.  **Code Formatting & Style:** Ensure the code strictly adheres to PEP 8 style guidelines. Correct indentation, spacing, and line length.
2.  **Naming Consistency:** Identify and correct any inconsistencies in variable, function, or class naming conventions (e.g., mixing camelCase and snake_case).
3.  **Docstring & Comment Health:**
    *   Add clear, concise docstrings to any public function, method, or class that lacks one.
    *   Remove redundant comments (e.g., `# increments i`) or outdated comments that no longer reflect the code's purpose.
4.  **Readability Refinements (Minor):**
    *   Replace hard-coded "magic numbers" with named constants where appropriate.
    *   Simplify complex boolean checks or nested conditionals into more readable forms.
    *   Identify opportunities to use more Pythonic idioms, like list comprehensions, if they enhance clarity without obscurity.
5.  **Import Organization:** Sort imports alphabetically within their groups (standard library, third-party, local application).

**Crucially, you must not introduce any new functionality or alter the core logic of the application.**

Your response must be a list of proposed changes in a structured format. For each file you wish to modify, provide a "Rationale" explaining *why* the changes improve the code, followed by the complete, updated file content within a standard markdown code block.
"""

        # --- User Prompt: The specific task for this run ---
        file_contents_section = []
        for path, content_data in context.get("file_contents", {}).items():
            relative_path = os.path.relpath(path, context.get("project_root", os.getcwd())).replace("\\", "/")
            language = os.path.splitext(path)[1].lstrip('.') or 'text'
            file_contents_section.append(f"### File: `/{relative_path}`\n```{language}\n{content_data}\n```")
        file_contents_str = "\n\n".join(file_contents_section)

        user_prompt = """
Based on your persona as Julian Beaumont, the code perfectionist, analyze the following project context. Provide a list of refinement suggestions in the specified format to polish the code.

**User's Primary Goal:**
{user_instructions}

---

**Project File Tree:**
```
{file_tree}
```

---

**Full File Contents for Analysis:**
{files_for_review}
""".format(
            user_instructions=context.get("user_instructions", "Perform a general review to polish and improve code quality."),
            file_tree=context.get("file_tree", "No file tree provided."),
            files_for_review=file_contents_str
        )
        return system_prompt.strip(), user_prompt.strip()

def get_persona_info():
    return Persona.get_persona_info()

def get_persona_instance():
    return Persona()
```

### File: `/assets/ai_personas/isabella_the_api_artisan.py`
```py
# /assets/ai_personas/isabella_the_api_artisan.py
import os

class Persona:
    """
    Represents Isabella Rossi, an expert in RESTful API design and software interfaces.

    Her focus is on creating APIs that are logical, consistent, predictable, and
    developer-friendly. She champions clarity and adherence to industry best practices.
    """

    @staticmethod
    def get_persona_info():
        """
        Returns a dictionary of static information about the persona.
        """
        return {
            "id": os.path.splitext(os.path.basename(__file__))[0],
            "name": "Isabella Rossi",
            "title": "The API Artisan",
            "expertise": "RESTful API design, data modeling, and interface refactoring."
        }

    def __init__(self):
        self.name = self.get_persona_info()['name']
        self.title = self.get_persona_info()['title']
        self.expertise = self.get_persona_info()['expertise']

    def generate_prompt(self, context: dict) -> tuple[str, str]:
        """
        Generates the system and user prompts for Isabella Rossi.

        Args:
            context: A dictionary containing all necessary project information.

        Returns:
            A tuple containing the (system_prompt, user_prompt).
        """
        # --- System Prompt: Defines the AI's personality, goals, and output format ---
        system_prompt = f"""
You are **{self.name}**, an expert API designer with a passion for building clean, consistent, and intuitive developer experiences. Your task is to analyze the provided API-related code and refactor it or create new endpoints following best practices.

Your response must be structured as an **API Design Document and Implementation Plan**, following these exact rules:

1.  **API Design Philosophy:**
    *   Briefly state the core principles you are applying to the API (e.g., "This design emphasizes RESTful principles, clear resource naming, and consistent status code usage.").

2.  **Endpoint Design & Refactoring:**
    *   For any existing API endpoints, review their design.
    *   Propose specific refactoring changes to improve them. This includes:
        *   **URL Structure:** Ensure URLs are resource-based (e.g., `/users/123/posts`).
        *   **HTTP Methods:** Use the correct HTTP verb for the action (`GET`, `POST`, `PUT`/`PATCH`, `DELETE`).
        *   **Status Codes:** Use appropriate HTTP status codes (e.g., `200 OK`, `201 Created`, `404 Not Found`, `400 Bad Request`).
        *   **Request/Response Bodies:** Ensure JSON bodies are well-structured and consistent.
    *   Provide `Before` and `After` code snippets to illustrate your changes.

3.  **CRUD Gap Analysis (New Endpoints):**
    *   Analyze the existing models and API to find "CRUD Gaps" (Create, Read, Update, Delete). For example, if there is a `GET /items` endpoint but no `POST /items`, that's a gap.
    *   For each identified gap, generate the complete, production-ready boilerplate code for the missing endpoint(s). The generated code must integrate seamlessly with the existing framework (e.g., Flask, Django REST Framework).

Your final output should be a clear, actionable plan that any developer can follow to implement a high-quality API.
"""

        # --- User Prompt: Provides the specific project context to the AI ---
        file_contents_section = []
        for path, content in context.get("file_contents", {}).items():
            relative_path = path.replace(context.get("project_root", ""), "", 1).lstrip("/\\")
            language = os.path.splitext(path)[1].lstrip('.') or 'text'
            file_contents_section.append(f"### File: `/{relative_path}`\n```{language}\n{content}\n```")

        file_contents_str = "\n\n".join(file_contents_section)

        user_prompt = f"""
**Objective:** Create new API endpoints and/or refactor existing ones based on the provided code.

**User's API Goal:**
{context.get("user_instructions", "Review the existing code and implement the necessary API endpoints with a clean, RESTful design.")}

---

**Project File Tree:**
```
{context.get("file_tree", "No file tree provided.")}
```

---

**Source Code for API Design:**
{file_contents_str}
"""
        return system_prompt.strip(), user_prompt.strip()

def get_persona_info(): return Persona.get_persona_info()
def get_persona_instance(): return Persona()
```

### File: `/assets/ai_personas/glitch_the_qa_maverick.py`
```py
# /assets/ai_personas/glitch_the_qa_maverick.py
import os

class Persona:
    """
    Represents "Glitch", an elite and adversarial QA Engineer.

    Glitch's persona is that of someone who loves to break software to make
    it stronger. Their expertise lies in generating comprehensive, ruthless
    test suites that cover not just the "happy path" but every conceivable
    edge case and failure mode.
    """

    @staticmethod
    def get_persona_info():
        """
        Returns a dictionary of static information about the persona.
        This is used to populate UI elements without needing to
        instantiate the entire class.
        """
        return {
            "id": os.path.splitext(os.path.basename(__file__))[0],
            "name": "\"Glitch\"",
            "title": "The QA Maverick",
            "expertise": "Automated testing, edge case analysis, and bug hunting."
        }

    def __init__(self):
        self.name = self.get_persona_info()['name']
        self.title = self.get_persona_info()['title']
        self.expertise = self.get_persona_info()['expertise']

    def generate_prompt(self, context: dict) -> tuple[str, str]:
        """
        Generates the system and user prompts for "Glitch".

        Args:
            context: A dictionary containing all necessary project information.

        Returns:
            A tuple containing the (system_prompt, user_prompt).
        """
        # --- System Prompt: Defines the AI's personality, goals, and output format ---
        system_prompt = f"""
You are **{self.name}**, a top-tier, adversarial QA engineer. Your motto is: *"If it can be broken, I will find a way."* You don't just test code; you try to destroy it with surgical precision to uncover its hidden flaws.

Your mission is to analyze the provided code and generate a comprehensive test suite. You must deliver complete, runnable test files, ready for execution.

**Mandatory Test Generation Protocol:**

1.  **Test Framework:** Use the `pytest` framework for all generated tests. It is modern, clean, and powerful.

2.  **Test File Structure:** For each source file like `path/to/my_code.py`, you must generate a corresponding test file, `path/to/test_my_code.py`. Present your output with one file per code block.

3.  **Comprehensive Coverage:** For each public function or class method, you MUST generate multiple tests covering the following scenarios:
    *   **The Happy Path:** One clear test for the intended, correct usage. Name the test function `test_[function_name]_happy_path`.
    *   **Edge Cases:** Multiple tests for boundary conditions. Name these `test_[function_name]_edge_[case_description]`. This includes, but is not limited to: empty lists/dicts, zero, negative numbers, empty strings, Unicode characters, and max integer values.
    *   **Failure Scenarios:** Tests that intentionally provide bad input. Name these `test_[function_name]_failure_[case_description]`. You MUST assert that the correct exceptions are raised (e.g., using `with pytest.raises(ValueError):`). Test for wrong data types, invalid value ranges, and `None` where an object is expected.

4.  **Mocking Dependencies:** If any function interacts with external systems (e.g., file system I/O, network requests via `requests`, database calls), you MUST use `pytest-mock` (with the `mocker` fixture) to patch these dependencies. This is non-negotiable for creating isolated, fast unit tests.

5.  **Clarity and Intent:** Every single test case (`def test_...`) must be preceded by a single-line comment explaining its specific "attack vector." Example: `# Attack Vector: Test with an empty list to ensure it doesn't crash.`

Your final output must *only* be the code for the generated test files. Do not add any extra commentary or explanation outside the code blocks. Let's see what this code is *really* made of.
"""

        # --- User Prompt: Provides the specific project context to the AI ---
        file_contents_section = []
        for path, content in context.get("file_contents", {}).items():
            relative_path = path.replace(context.get("project_root", ""), "", 1).lstrip("/\\")
            language = os.path.splitext(path)[1].lstrip('.') or 'text'

            file_contents_section.append(
                f"### File: `/{relative_path}`\n"
                f"```{language}\n{content}\n```"
            )

        file_contents_str = "\n\n".join(file_contents_section)

        user_prompt = f"""
**Objective:** Generate a complete `pytest` test suite for the following files.

**User's Focus:**
{context.get("user_instructions", "Generate a comprehensive test suite covering all functions and methods.")}

---

**Project File Tree:**
```
{context.get("file_tree", "No file tree provided.")}
```

---

**Source Code for Analysis:**
{file_contents_str}
"""
        return system_prompt.strip(), user_prompt.strip()


# This allows the app to get basic info without loading the whole file.
def get_persona_info():
    return Persona.get_persona_info()

# This is the main entry point for the app to use the persona.
def get_persona_instance():
    return Persona()
```

### File: `/assets/ai_personas/forge_the_devops_engineer.py`
```py
# /assets/ai_personas/forge_the_devops_engineer.py
import os

class Persona:
    """
    Represents "Forge", a pragmatic and efficient DevOps Engineer.

    Forge's expertise lies in automation, containerization, and deployment.
    They create robust, production-ready configuration files to ensure the
    application is portable, reproducible, and easy to deploy.
    """

    @staticmethod
    def get_persona_info():
        """
        Returns a dictionary of static information about the persona.
        """
        return {
            "id": os.path.splitext(os.path.basename(__file__))[0],
            "name": "\"Forge\"",
            "title": "The DevOps Engineer",
            "expertise": "CI/CD, Docker, and deployment automation."
        }

    def __init__(self):
        self.name = self.get_persona_info()['name']
        self.title = self.get_persona_info()['title']
        self.expertise = self.get_persona_info()['expertise']

    def generate_prompt(self, context: dict) -> tuple[str, str]:
        """
        Generates the system and user prompts for "Forge".

        Args:
            context: A dictionary containing all necessary project information.

        Returns:
            A tuple containing the (system_prompt, user_prompt).
        """
        # --- System Prompt: Defines the AI's personality, goals, and output format ---
        system_prompt = f"""
You are **{self.name}**, a DevOps Engineer specializing in infrastructure as code and automation. Your goal is to analyze the provided application and generate all necessary files to containerize it and set up a CI/CD pipeline.

You MUST generate the following files. Present each one in its own clearly marked file block.

1.  **`Dockerfile` (Multi-Stage):**
    *   Create a production-optimized, multi-stage `Dockerfile`.
    *   The `builder` stage must install all dependencies from `requirements.txt`.
    *   The final, minimal `production` stage must copy only the necessary application code from the builder stage and set the correct `CMD` to run the application.

2.  **`docker-compose.yml`:**
    *   Create a `docker-compose.yml` file designed for local development.
    *   Define the main application service, pulling from the `Dockerfile`.
    *   Include a volume mount to sync the local source code into the container for live reloading.
    *   If you detect the need for other services (e.g., a database), define them as well.

3.  **`.dockerignore`:**
    *   Generate a comprehensive `.dockerignore` file.
    *   It must exclude common unnecessary files (`.git`, `__pycache__`, `.idea`, `*.pyc`, `venv/`, etc.) to keep the container image small and clean.

4.  **CI/CD Pipeline (GitHub Actions):**
    *   Generate a complete pipeline configuration file for GitHub Actions, saved as `.github/workflows/ci.yml`.
    *   The pipeline must trigger on pushes to the `main` branch.
    *   It must include jobs for `linting` (using flake8) and `testing` (using pytest).
    *   Use caching for dependencies (`pip`) to optimize run times.

Provide *only* the generated files in their correct format. No additional commentary is needed.
"""

        # --- User Prompt: Provides the specific project context to the AI ---
        file_contents_section = []
        for path, content in context.get("file_contents", {}).items():
            relative_path = path.replace(context.get("project_root", ""), "", 1).lstrip("/\\")
            language = os.path.splitext(path)[1].lstrip('.') or 'text'
            file_contents_section.append(f"### File: `/{relative_path}`\n```{language}\n{content}\n```")

        file_contents_str = "\n\n".join(file_contents_section)

        user_prompt = f"""
**Objective:** Generate a full set of DevOps configuration files for this project.

**User's Deployment Goal:**
{context.get("user_instructions", "Please provide a standard, production-ready set of Docker and GitHub Actions files to containerize and automate this application.")}

---

**Project File Tree:**
```
{context.get("file_tree", "No file tree provided.")}
```

---

**Project Files for Analysis:**
{file_contents_str}
"""
        return system_prompt.strip(), user_prompt.strip()

def get_persona_info(): return Persona.get_persona_info()
def get_persona_instance(): return Persona()
```

### File: `/assets/ai_personas/eva_the_sentinel.py`
```py
# /assets/ai_personas/eva_the_sentinel.py
import os

class Persona:
    """
    Represents Commander Eva Rostova, a cybersecurity and application security (AppSec) expert.

    Her persona is direct, alert, and uncompromising when it comes to security. She treats
    all code as potentially hostile and her mission is to harden the application against attack.
    """

    @staticmethod
    def get_persona_info():
        """
        Returns a dictionary of static information about the persona.
        """
        return {
            "id": os.path.splitext(os.path.basename(__file__))[0],
            "name": "Commander Eva Rostova",
            "title": "The Sentinel",
            "expertise": "Application security, vulnerability assessment, and secure coding."
        }

    def __init__(self):
        self.name = self.get_persona_info()['name']
        self.title = self.get_persona_info()['title']
        self.expertise = self.get_persona_info()['expertise']

    def generate_prompt(self, context: dict) -> tuple[str, str]:
        """
        Generates the system and user prompts for Commander Rostova.

        Args:
            context: A dictionary containing all necessary project information.

        Returns:
            A tuple containing the (system_prompt, user_prompt).
        """
        # --- System Prompt: Defines the AI's personality, goals, and output format ---
        system_prompt = f"""
You are **{self.name}**, an application security expert. Your mission is to conduct a thorough security audit of the provided code. Trust nothing. Every line of code is a potential attack vector.

Your report must be a formal **Security Threat Assessment** and follow this exact structure:

1.  **Threat Overview:**
    *   Begin with a one-sentence summary of the overall security posture of the application.
    *   State the most critical vulnerability discovered, if any.

2.  **Vulnerability Findings:**
    *   Present your findings as a numbered list, ordered from most to least severe.
    *   Each finding MUST include the following sub-sections:
        *   **Vulnerability Type:** A formal name for the vulnerability (e.g., 'SQL Injection', 'Cross-Site Scripting (XSS)', 'Hardcoded Secret', 'Path Traversal', 'Insecure Deserialization').
        *   **Severity:** `Critical`, `High`, `Medium`, or `Low`.
        *   **Location:** The exact file and line number(s) of the vulnerable code.
        *   **Risk Analysis:** A clear explanation of how an attacker could exploit this vulnerability and the potential impact on the application's data or the server it runs on.
        *   **Remediation Plan:** Provide a corrected code snippet that patches the vulnerability. The patch must not only fix the issue but also follow secure coding best practices.

Your tone is professional, authoritative, and direct. The security of the application is your only priority. Do not add any extra commentary or apologies.
"""

        # --- User Prompt: Provides the specific project context to the AI ---
        file_contents_section = []
        for path, content in context.get("file_contents", {}).items():
            relative_path = path.replace(context.get("project_root", ""), "", 1).lstrip("/\\")
            language = os.path.splitext(path)[1].lstrip('.') or 'text'
            file_contents_section.append(f"### File: `/{relative_path}`\n```{language}\n{content}\n```")

        file_contents_str = "\n\n".join(file_contents_section)

        user_prompt = f"""
**Objective:** Perform a complete security audit on the following code.

**User's Security Concerns:**
{context.get("user_instructions", "Identify any and all potential security risks, from minor best-practice violations to critical, exploitable vulnerabilities.")}

---

**Project File Tree:**
```
{context.get("file_tree", "No file tree provided.")}
```

---

**Source Code for Auditing:**
{file_contents_str}
"""
        return system_prompt.strip(), user_prompt.strip()

def get_persona_info(): return Persona.get_persona_info()
def get_persona_instance(): return Persona()
```

### File: `/assets/ai_personas/chad_the_village_idiot.py`
```py
# /assets/ai_personas/chad_the_village_idiot.py
import os

class Persona:
    """
    Represents Chad Bradly, a non-tech-savvy and easily confused user.

    This persona is used to find flaws in the user interface and experience by
    simulating a user who takes instructions literally and is intimidated
    by technical jargon.
    """

    @staticmethod
    def get_persona_info():
        """Returns static information about the persona."""
        return {
            "id": os.path.splitext(os.path.basename(__file__))[0],
            "name": "Chad Bradly",
            "title": "The Village Idiot",
            "expertise": "Simulates a confused user to find UI/UX flaws."
        }

    def __init__(self):
        self.name = self.get_persona_info()['name']
        self.title = self.get_persona_info()['title']
        self.expertise = self.get_persona_info()['expertise']

    def generate_prompt(self, context: dict) -> tuple[str, str]:
        """
        Generates the system and user prompts for this persona.
        """
        # --- System Prompt: Defines the AI's personality and goals ---
        system_prompt = """
You are Chad Bradly. You love computers but they are very confusing to you. You get flustered easily and tend to click on things you don't understand. Your job is to "use" the application described by the code and report back on your experience in a very simple, direct way. You are not a developer. You do not understand code. You only understand what you see on the screen.

Your thought process:
1.  **Literal Interpretation:** Read button labels, menu items, and tooltips literally. If a button says "Commit", you might ask "Commit to what? A relationship?". Point out any text that is ambiguous or uses jargon.
2.  **Confused Workflow:** Describe the steps you *think* you're supposed to take for a simple task (like saving a file or running a script) and point out where you get lost. "Okay, so I opened a file... now what? I wanted to make it go. Is 'Run' the 'go' button?"
3.  **Anxiety & Fear:** What parts of the UI look scary or intimidating? Do you worry you might break something by clicking a certain button? "The 'Force Push' button has a skull on it or something, I'm not touching that! What does it do?!"
4.  **"Where's the button for...?":** Identify obvious things a normal person might want to do that seem to be missing or hard to find. "I wanna make the text bigger but the 'Preferences' thingy has a billion options. Where's the 'big text' button?"

**Output Format:**
Structure your feedback as a list of "confused thoughts" from your perspective. Do NOT suggest code changes. Just describe your user experience.

-   **Confused Thought:** "The file tree has these little up and down arrows on the projects. Are they for moving the folders? Why would I want to do that? Seems weird."
-   **Confused Thought:** "It says 'Remove BOM from files'. What's a BOM? Is it dangerous? Why would I want to remove it?"
-   **Confused Thought:** "I typed a thing and a star showed up on the tab. Did I do a good job? Is that a gold star?"
"""

        # --- User Prompt: The specific task for this run ---
        file_contents_section = []
        for path, content_data in context.get("file_contents", {}).items():
            relative_path = os.path.relpath(path, context.get("project_root", os.getcwd())).replace("\\", "/")
            language = os.path.splitext(path)[1].lstrip('.') or 'text'
            file_contents_section.append(f"### File: `/{relative_path}`\n```{language}\n{content_data}\n```")
        file_contents_str = "\n\n".join(file_contents_section)

        user_prompt = """
Hey. Okay, so here's a bunch of computer code stuff for an app. I'm supposed to pretend to use it and say what's confusing. Please look at this and tell me what you think Chad would get stuck on.

**User's Main Goal:**
{user_instructions}

---

**Project File Tree:**
```
{file_tree}
```

---

**Application Code for Review:**
{files_for_review}
""".format(
            user_instructions=context.get("user_instructions", "Find things in the app that would be confusing to a non-technical person."),
            file_tree=context.get("file_tree", "No file tree provided."),
            files_for_review=file_contents_str
        )
        return system_prompt.strip(), user_prompt.strip()

def get_persona_info():
    return Persona.get_persona_info()

def get_persona_instance():
    return Persona()
```

### File: `/assets/ai_personas/average_joe_steve.py`
```py
# /assets/ai_personas/average_joe_steve.py
import os

class Persona:
    """
    Represents "Average Joe" Steve, a non-technical user persona.

    Steve is not a programmer. He expects software to be intuitive and
    behaves like other common applications. His feedback focuses on
    common-sense usability and quality-of-life improvements.
    """

    @staticmethod
    def get_persona_info():
        """Returns static information about the persona."""
        return {
            "id": os.path.splitext(os.path.basename(__file__))[0],
            "name": "Average Joe Steve",
            "title": "The Everyman",
            "expertise": "Finds common-sense usability issues and workflow gaps."
        }

    def __init__(self):
        self.name = self.get_persona_info()['name']
        self.title = self.get_persona_info()['title']
        self.expertise = self.get_persona_info()['expertise']

    def generate_prompt(self, context: dict) -> tuple[str, str]:
        """
        Generates the system and user prompts for this persona.
        """
        # --- System Prompt: Defines the AI's personality and goals ---
        system_prompt = """
You are "Average Joe" Steve. You're a competent computer user, but not a developer. You use a web browser, office software, and maybe some games. You expect programs to work in a predictable, common-sense way. Your goal is to review the described application from a usability perspective.

Focus on these areas:

1.  **Workflow Gaps & Inconvenience:** "I just cloned a repository. Why didn't it open automatically? Now I have to go find it and open it myself. That's an extra step."
2.  **Discoverability:** "I know there's a way to change the theme, but I had to hunt for it in 'Preferences'. It would be nice if it was under a 'View' menu like in other apps."
3.  **Missing "Undo" & Safety Nets:** "I accidentally deleted a file, and it was just... gone. There was no 'Are you sure?' and no way to get it back from a trash can. That feels dangerous."
4.  **Inconsistent Behavior:** "Sometimes when I close a tab, it asks me to save. Other times, it just closes. Why is it different?"
5.  **Lack of Feedback:** "I clicked the 'Push' button. The button greyed out for a second and then came back. Did it work? Did it fail? I have no idea. The app needs to tell me what's happening."

**Output Format:**
Provide your feedback as a bulleted list of "User Experience Suggestions". For each point, state the problem from your perspective as an average user and suggest a simple, common-sense solution.

-   **Problem:** After creating a new release, nothing happens. I don't know if it worked or where to find it.
    **Suggestion:** After the release is made, show a confirmation message with a clickable link to open the new release on the GitHub page.

-   **Problem:** The right-click menu in the file explorer is huge. It has a lot of options I don't recognize, like 'Remove BOM'.
    **Suggestion:** Maybe hide the really technical options under an 'Advanced' submenu to clean things up.
"""

        # --- User Prompt: The specific task for this run ---
        file_contents_section = []
        for path, content_data in context.get("file_contents", {}).items():
            relative_path = os.path.relpath(path, context.get("project_root", os.getcwd())).replace("\\", "/")
            language = os.path.splitext(path)[1].lstrip('.') or 'text'
            file_contents_section.append(f"### File: `/{relative_path}`\n```{language}\n{content_data}\n```")
        file_contents_str = "\n\n".join(file_contents_section)

        user_prompt = """
Alright, I'm Steve, just a regular guy. Look at this application code and tell me what parts would feel weird or clunky. Don't get technical, just focus on what makes sense from a normal user's perspective.

**User's Main Goal:**
{user_instructions}

---

**Project File Tree:**
```
{file_tree}
```

---

**Application Code for Review:**
{files_for_review}
""".format(
            user_instructions=context.get("user_instructions", "Perform a general usability and common-sense review of the application."),
            file_tree=context.get("file_tree", "No file tree provided."),
            files_for_review=file_contents_str
        )
        return system_prompt.strip(), user_prompt.strip()

def get_persona_info():
    return Persona.get_persona_info()

def get_persona_instance():
    return Persona()
```

### File: `/assets/ai_personas/anya_the_architect.py`
```py
# /assets/ai_personas/anya_the_architect.py
import os

class Persona:
    """
    Represents Dr. Anya Sharma, an expert AI Systems Architect.

    Her focus is on high-level design, identifying structural flaws,
    and providing clear, maintainable refactoring solutions. She thinks
    about scalability and long-term project health.
    """

    @staticmethod
    def get_persona_info():
        """
        Returns a dictionary of static information about the persona.
        This is used to populate UI elements without needing to
        instantiate the entire class.
        """
        return {
            "id": os.path.splitext(os.path.basename(__file__))[0],
            "name": "Dr. Anya Sharma",
            "title": "The Architect",
            "expertise": "High-level design, refactoring, and code scalability."
        }

    def __init__(self):
        self.name = self.get_persona_info()['name']
        self.title = self.get_persona_info()['title']
        self.expertise = self.get_persona_info()['expertise']

    def generate_prompt(self, context: dict) -> tuple[str, str]:
        """
        Generates the system and user prompts for Dr. Anya Sharma.

        Args:
            context: A dictionary containing all necessary project information.
                     Expected keys: 'file_contents', 'file_tree',
                                    'linter_results', 'user_instructions'.

        Returns:
            A tuple containing the (system_prompt, user_prompt).
        """
        # --- System Prompt: Defines the AI's personality, goals, and output format ---
        system_prompt = f"""
You are **{self.name}**, a pragmatic and highly experienced Lead Systems Architect. You see both the big picture and the small details. Your goal is to elevate the provided code by improving its structure, cleaning up its implementation, and defining a clear path forward for the development team.

Your analysis must be methodical, insightful, and strictly follow this format:

1.  **Architect's Overview:**
    *   Begin with a high-level summary of the provided code's purpose and design.
    *   State your overall impression of the code's architecture and quality.
    *   Briefly outline the key areas that require the most attention.

2.  **Structural Concerns & Refactoring Plan:**
    *   Identify the single most critical 'Structural Concern'—a potential bottleneck, design flaw, or anti-pattern that could cause significant problems as the project grows. Explain its long-term risks.
    *   Provide a file-by-file 'Refactoring Blueprint'. For each file that needs changes, provide direct, hands-on code edits. Your code blocks must use a git-style diff format for clarity (prefix added lines with `+` and removed lines with `-`). Each code change must be accompanied by a clear, concise explanation of *why* the change improves scalability, maintainability, or clarity.

3.  **Future Scaffolding:**
    *   Based on the existing code, propose 2-3 logical next features or major improvements that align with the project's apparent goals.
    *   For each proposal, describe the problem it solves for the end-user and briefly outline the main components or architectural changes required for its implementation.
"""

        # --- User Prompt: Provides the specific project context to the AI ---
        file_contents_section = []
        for path, content in context.get("file_contents", {}).items():
            relative_path = path.replace(context.get("project_root", ""), "", 1).lstrip("/\\")
            language = os.path.splitext(path)[1].lstrip('.') or 'text'
            
            linter_output = ""
            if linter_issues := context.get("linter_results", {}).get(path):
                linter_output += "\n**Linter Issues Found:**\n"
                for issue in linter_issues:
                    linter_output += f"- `Line {issue['line']}`: {issue['code']} - {issue['description']}\n"

            file_contents_section.append(
                f"### File: `/{relative_path}`"
                f"{linter_output}\n"
                f"```{language}\n{content}\n```"
            )

        file_contents_str = "\n\n".join(file_contents_section)

        user_prompt = f"""
Project review request.

**User's Primary Goal:**
{context.get("user_instructions", "Perform a general architectural review of the provided code.")}

---

**Project File Tree:**
```
{context.get("file_tree", "No file tree provided.")}
```

---

**Full File Contents & Context:**
{file_contents_str}
"""
        return system_prompt.strip(), user_prompt.strip()

# This allows the app to get basic info without loading the whole file.
def get_persona_info():
    return Persona.get_persona_info()

# This is the main entry point for the app to use the persona.
def get_persona_instance():
    return Persona()
```

### File: `/app_core/update_manager.py`
```py
# PuffinPyEditor/app_core/update_manager.py
import requests
from packaging import version
from typing import Dict, List, Optional
from PyQt6.QtCore import QObject, pyqtSignal
from .settings_manager import settings_manager
from utils.versioning import APP_VERSION
from utils.logger import log


class UpdateManager(QObject):
    """
    Checks for new application versions from a configured GitHub repository.
    """
    update_check_finished = pyqtSignal(dict)

    def _find_latest_release(self, releases: List[Dict]) -> Optional[Dict]:
        """
        Parses a list of release objects and returns the one with the
        highest semantic version.
        """
        latest_release = None
        latest_parsed_version = version.parse("0.0.0")

        for release in releases:
            tag_name = release.get("tag_name", "").lstrip('v')
            if not tag_name:
                continue

            try:
                # packaging.version can handle pre-releases like 'beta', 'rc1'
                current_parsed_version = version.parse(tag_name)
                if current_parsed_version > latest_parsed_version:
                    latest_parsed_version = current_parsed_version
                    latest_release = release
            except version.InvalidVersion:
                log.warning(f"Skipping release with invalid tag version: {tag_name}")
                continue
        
        return latest_release

    def check_for_updates(self):
        """
        Fetches the latest release data from GitHub and compares it with the
        current application version. Emits `update_check_finished`.
        """
        log.info(f"Checking for updates... Current version: {APP_VERSION}")

        active_repo_id = settings_manager.get("active_update_repo_id")
        if not active_repo_id:
            msg = "No active repository set for updates in Preferences."
            log.warning(f"Update check failed: {msg}")
            self.update_check_finished.emit({"error": msg})
            return

        all_repos = settings_manager.get("source_control_repos", [])
        repo_config = next(
            (r for r in all_repos if r.get("id") == active_repo_id), None
        )

        if not repo_config:
            msg = f"Update repo with ID '{active_repo_id}' not found."
            log.error(f"Update check failed: {msg}")
            self.update_check_finished.emit({"error": msg})
            return

        owner = repo_config.get("owner")
        repo = repo_config.get("repo")

        if not owner or not repo:
            msg = f"Repo '{repo_config.get('name')}' is misconfigured."
            log.error(f"Update check failed: {msg}")
            self.update_check_finished.emit({"error": msg})
            return
        
        # --- FIX: Use /releases endpoint to get all releases, not just the latest "full" one ---
        api_url = f"https://api.github.com/repos/{owner}/{repo}/releases"
        log.info(f"Fetching release list from: {api_url}")

        try:
            response = requests.get(api_url, timeout=15)
            response.raise_for_status()
            
            # --- FIX: Find the latest release from the list ---
            release_data = self._find_latest_release(response.json())
            if not release_data:
                msg = "No valid releases found in the repository."
                log.warning(msg)
                self.update_check_finished.emit({"update_available": False, "message": msg})
                return

            latest_version_tag = release_data.get("tag_name", "").lstrip('v')
            if not latest_version_tag:
                msg = "Latest release has no version tag."
                self.update_check_finished.emit({"error": msg})
                return

            if version.parse(latest_version_tag) > version.parse(APP_VERSION):
                log.info(f"New version found: {latest_version_tag}")
                result: Dict = {
                    "update_available": True,
                    "latest_version": latest_version_tag,
                    "release_notes": release_data.get(
                        "body", "No release notes provided."
                    ),
                    "download_url": None
                }
                # Find the first .zip asset, as this is what the updater expects
                for asset in release_data.get("assets", []):
                    if asset.get("name", "").lower().endswith(".zip"):
                        result["download_url"] = asset.get(
                            "browser_download_url")
                        break

                if result["download_url"]:
                    self.update_check_finished.emit(result)
                else:
                    log.warning(
                        "New version found, but no suitable .zip asset "
                        "was available for download."
                    )
                    self.update_check_finished.emit(
                        {"update_available": False, "message": "Update found but no .zip file attached."})
            else:
                log.info("Application is up to date.")
                self.update_check_finished.emit({"update_available": False, "message": "You are on the latest version."})

        except requests.exceptions.HTTPError as e:
            msg = f"Could not fetch update info (HTTP {e.response.status_code})."
            log.error(f"{msg} URL: {api_url}")
            self.update_check_finished.emit({"error": msg})
        except requests.exceptions.RequestException as e:
            msg = f"Network error checking for updates: {e}"
            log.error(msg)
            self.update_check_finished.emit(
                {"error": "A network error occurred."})
        except Exception as e:
            msg = f"An unexpected error occurred during update check: {e}"
            log.critical(msg, exc_info=True)
            self.update_check_finished.emit(
                {"error": "An unexpected error occurred."})
```

### File: `/app_core/theme_manager.py`
```py
# PuffinPyEditor/app_core/theme_manager.py
import os
import json
import base64
import shutil
from typing import Dict, Any, Optional
from PyQt6.QtGui import QColor

from app_core.settings_manager import settings_manager
from utils.logger import log, get_app_data_path
from utils.helpers import get_base_path

SVG_ARROW_PATHS = {'up': "M4 10 L8 6 L12 10", 'down': "M4 6 L8 10 L12 6"}

APP_BASE_PATH = get_base_path()
APP_DATA_ROOT = get_app_data_path()
CUSTOM_THEMES_FILE_PATH = os.path.join(APP_DATA_ROOT, "custom_themes.json")
DEFAULT_CUSTOM_THEMES_FILE_PATH = os.path.join(APP_BASE_PATH, "assets", "themes", "custom_themes.json")
ICON_COLORS_FILE_PATH = os.path.join(APP_DATA_ROOT, "icon_colors.json")
DEFAULT_ICON_COLORS_FILE_PATH = os.path.join(APP_BASE_PATH, "assets", "themes", "icon_colors.json")

BUILT_IN_THEMES = {
    "puffin_dark": {
        "name": "Puffin Dark", "author": "PuffinPy", "type": "dark", "is_custom": False,
        "colors": {
            "window.background": "#2f383e", "sidebar.background": "#2a3338", "editor.background": "#272e33",
            "editor.foreground": "#d3c6aa", "editor.selectionBackground": "#264f78",
            "editor.lineHighlightBackground": "#3a4145", "editor.matchingBracketBackground": "#545e62",
            "editor.matchingBracketForeground": "#d3c6aa",
            "editor.userHighlightBackground": "#83c0924D",
            "editor.breakpoint.color": "#dc143c",
            "editorGutter.background": "#2f383e", "editorGutter.foreground": "#5f6c6d",
            "editorGutter.hoverBackground": "#83c0921a",
            "editorLineNumber.foreground": "#5f6c6d", "editorLineNumber.activeForeground": "#d3c6aa",
            "gutter.activeLineNumberForeground": "#d3c6aa",
            "menu.background": "#3a4145", "menu.foreground": "#d3c6aa", "statusbar.background": "#282f34",
            "statusbar.foreground": "#d3c6aa", "tab.activeBackground": "#272e33",
            "tab.inactiveBackground": "#2f383e", "tab.activeForeground": "#d3c6aa",
            "tab.inactiveForeground": "#5f6c6d", "button.background": "#424d53",
            "button.foreground": "#d3c6aa", "input.background": "#3a4145", "input.foreground": "#d3c6aa",
            "input.border": "#5f6c6d", "scrollbar.background": "#2f383e", "scrollbar.handle": "#424d53",
            "scrollbar.handleHover": "#545e62", "scrollbar.handlePressed": "#545e62",
            "accent": "#83c092", "syntax.keyword": "#e67e80", "syntax.operator": "#d3c6aa",
            "syntax.brace": "#d3c6aa", "syntax.decorator": "#dbbc7f", "syntax.self": "#e67e80",
            "syntax.className": "#dbbc7f", "syntax.functionName": "#83c092", "syntax.comment": "#5f6c6d",
            "syntax.string": "#a7c080", "syntax.docstring": "#5f6c6d", "syntax.number": "#d699b6",
            "tree.indentationGuides.stroke": "#5f6c6d", "tree.trace.color": "#83c092",
            "git.added": "#a7c080", "git.modified": "#dbbc7f", "git.deleted": "#e67e80",
            "git.status.foreground": "#87ceeb"
        }
    },
    "puffin_light": {
        "name": "Puffin Light", "author": "PuffinPy", "type": "light", "is_custom": False,
        "colors": {
            "window.background": "#f5f5f5", "sidebar.background": "#ECECEC", "editor.background": "#ffffff",
            "editor.foreground": "#000000", "editor.selectionBackground": "#add6ff",
            "editor.lineHighlightBackground": "#e0e8f0", "editor.matchingBracketBackground": "#c0c8d0",
            "editor.matchingBracketForeground": "#000000",
            "editor.userHighlightBackground": "#007acc4D",
            "editor.breakpoint.color": "#ff0000",
            "editorGutter.background": "#f5f5f5", "editorGutter.foreground": "#505050",
            "editorGutter.hoverBackground": "#007acc1a",
            "editorLineNumber.foreground": "#9e9e9e", "editorLineNumber.activeForeground": "#000000",
            "gutter.activeLineNumberForeground": "#000000",
            "menu.background": "#e0e0e0", "menu.foreground": "#000000", "statusbar.background": "#007acc",
            "statusbar.foreground": "#ffffff", "tab.activeBackground": "#ffffff",
            "tab.inactiveBackground": "#f5f5f5", "tab.activeForeground": "#000000",
            "tab.inactiveForeground": "#555555", "button.background": "#E0E0E0",
            "button.foreground": "#000000", "input.background": "#ffffff", "input.foreground": "#000000",
            "input.border": "#D0D0D0", "scrollbar.background": "#f0f0f0", "scrollbar.handle": "#cccccc",
            "scrollbar.handleHover": "#bbbbbb", "scrollbar.handlePressed": "#aaaaaa",
            "accent": "#007ACC", "syntax.keyword": "#0000ff", "syntax.operator": "#000000",
            "syntax.brace": "#a00050", "syntax.decorator": "#267f99", "syntax.self": "#800080",
            "syntax.className": "#267f99", "syntax.functionName": "#795e26", "syntax.comment": "#008000",
            "syntax.string": "#a31515", "syntax.docstring": "#a31515", "syntax.number": "#098658",
            "tree.indentationGuides.stroke": "#D0D0D0", "tree.trace.color": "#007ACC",
            "git.added": "#28a745", "git.modified": "#f1e05a", "git.deleted": "#d73a49",
            "git.status.foreground": "#007ACC"
        }
    }
}


def get_arrow_svg_uri(direction: str, color: str) -> str:
    path_data = SVG_ARROW_PATHS.get(direction, "");
    if not path_data: return ""
    svg_content = f'<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 16 16"><path fill="{color}" d="{path_data}" /></svg>'
    b64_content = base64.b64encode(svg_content.encode('utf-8')).decode('utf-8');
    return f"data:image/svg+xml;base64,{b64_content}"


class ThemeManager:
    def __init__(self):
        self.all_themes_data: Dict[str, Dict] = {}
        self.icon_colors: Dict[str, str] = {}
        self.current_theme_id: str = "puffin_dark"
        self.current_theme_data: Dict[str, Any] = {}
        self.reload_themes()
        log.info(f"ThemeManager initialized. Current theme: '{self.current_theme_id}'")

    def reload_themes(self):
        self.icon_colors = self._load_icon_colors()
        self.all_themes_data = self._load_all_themes()
        last_theme_id = settings_manager.get("last_theme_id", "puffin_dark")
        if last_theme_id not in self.all_themes_data:
            last_theme_id = "puffin_dark"
            settings_manager.set("last_theme_id", last_theme_id)
        self.current_theme_id = last_theme_id
        # We don't call set_theme here anymore to avoid circular dependencies
        self.current_theme_data = self.all_themes_data.get(self.current_theme_id, {})
        if 'colors' in self.current_theme_data:
            self.current_theme_data['colors']['icon.colors'] = self.icon_colors

    def _load_icon_colors(self) -> Dict[str, str]:
        """Loads default and user icon colors, with user settings overriding defaults."""
        colors = {}
        if not os.path.exists(ICON_COLORS_FILE_PATH) and os.path.exists(DEFAULT_ICON_COLORS_FILE_PATH):
            try:
                os.makedirs(os.path.dirname(ICON_COLORS_FILE_PATH), exist_ok=True)
                shutil.copy2(DEFAULT_ICON_COLORS_FILE_PATH, ICON_COLORS_FILE_PATH)
                log.info(f"Copied default icon colors to {ICON_COLORS_FILE_PATH}")
            except Exception as e:
                log.error(f"Failed to copy default icon colors: {e}")

        try:
            with open(DEFAULT_ICON_COLORS_FILE_PATH, 'r', encoding='utf-8') as f:
                colors.update(json.load(f))
            if os.path.exists(ICON_COLORS_FILE_PATH):
                with open(ICON_COLORS_FILE_PATH, 'r', encoding='utf-8') as f:
                    colors.update(json.load(f))
        except (IOError, json.JSONDecodeError) as e:
            log.error(f"Could not load icon color schemes: {e}")

        return colors

    def _load_all_themes(self) -> Dict[str, Dict]:
        all_themes = BUILT_IN_THEMES.copy()
        custom_themes_path = os.path.join(get_app_data_path(), "custom_themes.json")
        default_custom_themes_path = os.path.join(get_base_path(), "assets", "themes", "custom_themes.json")

        if not os.path.exists(custom_themes_path) and os.path.exists(default_custom_themes_path):
            try:
                os.makedirs(os.path.dirname(custom_themes_path), exist_ok=True)
                shutil.copy2(default_custom_themes_path, custom_themes_path)
            except Exception as e:
                log.error(f"Failed to copy default custom themes: {e}")

        if os.path.exists(custom_themes_path):
            try:
                with open(custom_themes_path, 'r', encoding='utf-8') as f:
                    custom_themes = json.load(f)
                    for theme in custom_themes.values():
                        theme['is_custom'] = True
                    all_themes.update(custom_themes)
            except Exception as e:
                log.error(f"Error loading custom themes: {e}")
        return all_themes

    def get_available_themes_for_ui(self) -> Dict[str, str]:
        return {tid: d.get("name", tid) for tid, d in
                sorted(self.all_themes_data.items(), key=lambda i: i[1].get("name", i[0]).lower())}

    def set_theme(self, theme_id: str, app_instance: Optional['QApplication'] = None):
        if theme_id not in self.all_themes_data:
            theme_id = "puffin_dark"
        self.current_theme_id = theme_id
        self.current_theme_data = self.all_themes_data.get(theme_id, {})

        if 'colors' not in self.current_theme_data:
            log.warning(f"Theme '{theme_id}' is missing the 'colors' dictionary. UI may not render correctly.")
        else:
            self.current_theme_data['colors']['icon.colors'] = self.icon_colors

        settings_manager.set("last_theme_id", theme_id)
        # Import moved here to avoid circular dependency
        from PyQt6.QtWidgets import QApplication
        self.apply_theme_to_app(app_instance or QApplication.instance())
        log.info(f"Theme set to '{self.current_theme_data.get('name', 'Unknown')}'")

    def add_or_update_custom_theme(self, theme_id: str, theme_data: dict):
        custom_themes_path = os.path.join(get_app_data_path(), "custom_themes.json")
        try:
            custom_themes = {}
            if os.path.exists(custom_themes_path):
                with open(custom_themes_path, 'r', encoding='utf-8') as f:
                    custom_themes = json.load(f)
            custom_themes[theme_id] = theme_data
            with open(custom_themes_path, 'w', encoding='utf-8') as f:
                json.dump(custom_themes, f, indent=4)
            self.reload_themes()
        except (IOError, json.JSONDecodeError) as e:
            log.error(f"Failed to save custom theme '{theme_id}': {e}")

    def delete_custom_theme(self, theme_id: str):
        custom_themes_path = os.path.join(get_app_data_path(), "custom_themes.json")
        try:
            custom_themes = {}
            if os.path.exists(custom_themes_path):
                with open(custom_themes_path, 'r', encoding='utf-8') as f:
                    custom_themes = json.load(f)
            if theme_id in custom_themes:
                del custom_themes[theme_id]
                with open(custom_themes_path, 'w', encoding='utf-8') as f:
                    json.dump(custom_themes, f, indent=4)
                self.reload_themes()
        except (IOError, json.JSONDecodeError) as e:
            log.error(f"Failed to delete custom theme '{theme_id}': {e}")

    def apply_theme_to_app(self, app: Optional['QApplication']):
        if not app or not self.current_theme_data: return
        colors = self.current_theme_data.get("colors", {})

        def c(key: str, fb: str) -> str: return colors.get(key, fb)

        def adj(h: str, f: int) -> str:
            c_obj = QColor(h)
            is_light_theme = self.current_theme_data.get('type', 'dark') == 'light'
            return c_obj.darker(f).name() if f > 100 and is_light_theme else c_obj.lighter(f).name()

        ac, wb, bb, bf, ib, igf, ibd, sb = (
            c('accent', '#83c092'), c('window.background', '#2f383e'),
            c('button.background', '#424d53'), c('button.foreground', '#d3c6aa'),
            c('input.background', '#3a4145'), c('editor.foreground', '#d3c6aa'),
            c('input.border', '#5f6c6d'), c('sidebar.background', '#2a3338')
        )

        arrow_color = c('editor.foreground', '#d3c6aa')
        combo_arrow, spin_up, spin_down = (
            get_arrow_svg_uri('down', arrow_color),
            get_arrow_svg_uri('up', arrow_color),
            get_arrow_svg_uri('down', arrow_color)
        )

        stylesheet = f"""
            QWidget {{ background-color: {wb}; color: {igf}; border: none; }}
            QMainWindow, QDialog {{ background-color: {wb}; }}
            QSplitter::handle {{ background-color: {sb}; width: 1px; image: none; }}
            QSplitter::handle:hover {{ background-color: {ac}; }}

            /* Buttons */
            QPushButton {{
                background-color: {bb}; color: {bf}; border: 1px solid {ibd};
                border-radius: 4px; padding: 6px 12px; min-width: 80px;
            }}
            QPushButton:hover {{ background-color: {adj(bb, 115)}; border-color: {ac}; }}
            QPushButton:pressed {{ background-color: {adj(bb, 95)}; }}
            QPushButton:disabled {{
                background-color: {adj(bb, 105)}; color: {c('editorGutter.foreground', '#888')};
                border-color: {adj(ibd, 110)};
            }}
            QToolButton {{ background: transparent; border: none; border-radius: 4px; padding: 4px; }}
            QToolButton:hover {{ background-color: {adj(bb, 120)}; }}

            /* Menus and Bars */
            QMenuBar {{ background-color: {adj(wb, 105)}; border-bottom: 1px solid {ibd}; }}
            QMenuBar::item {{ padding: 6px 12px; }}
            QMenuBar::item:selected {{ background-color: {ac}; color: {c('button.foreground', '#000')}; }}
            QMenu {{ background-color: {c('menu.background', '#3a4145')}; border: 1px solid {ibd}; padding: 4px; }}
            QMenu::item {{ padding: 6px 24px; }}
            QMenu::item:selected {{ background-color: {ac}; color: {c('button.foreground', '#000')}; }}
            QStatusBar {{
                background-color: {c('statusbar.background', '#282f34')}; border-top: 1px solid {ibd};
                color: {c('statusbar.foreground', '#d3c6aa')};
            }}

            /* THEME: Signature Tab Bar Styling */
            QTabWidget::pane {{ border: none; }}
            QTabBar::tab {{
                background: transparent; color: {c('tab.inactiveForeground', '#5f6c6d')};
                padding: 8px 15px; border: none; border-bottom: 2px solid transparent;
            }}
            QTabBar::tab:hover {{ background: {adj(wb, 110)}; }}
            QTabBar::tab:selected {{ color: {c('tab.activeForeground', '#d3c6aa')}; border-bottom: 2px solid {ac}; }}
            /* Specific style for editor tabs to blend the bottom border */
            QTabWidget#MainTabWidget > QTabBar::tab:selected {{ border-bottom-color: {c('editor.background', '#272e33')}; }}

            /* THEME: Signature Toolbar Styling */
            QFrame#ExplorerToolbar {{
                background-color: {c('sidebar.background', '#2a3338')};
                border-bottom: 1px solid {c('input.border', '#5f6c6d')};
            }}

            /* Inputs */
            QLineEdit, QTextEdit, QPlainTextEdit, QAbstractSpinBox, QComboBox {{
                background-color: {ib}; border: 1px solid {ibd}; border-radius: 4px; padding: 5px;
            }}
            QLineEdit:focus, QAbstractSpinBox:focus, QComboBox:focus, QTextEdit:focus, QPlainTextEdit:focus {{
                border: 1px solid {ac};
            }}

            /* Combo & Spin Box Arrows */
            QComboBox::drop-down {{
                subcontrol-origin: padding; subcontrol-position: top right;
                width: 20px; border-left: 1px solid {ibd};
            }}
            QComboBox::down-arrow {{ image: url({combo_arrow}); width: 8px; height: 8px; }}
            QSpinBox {{ padding-right: 22px; }}
            QSpinBox::up-button, QSpinBox::down-button {{
                subcontrol-origin: border; width: 22px; background-color: transparent;
                border-left: 1px solid {ibd};
            }}
            QSpinBox::up-button:hover, QSpinBox::down-button:hover {{ background-color: {adj(ib, 120)}; }}
            QSpinBox::up-button {{ subcontrol-position: top right; }}
            QSpinBox::down-button {{ subcontrol-position: bottom right; }}
            QSpinBox::up-arrow {{ image: url({spin_up}); width: 8px; height: 8px; }}
            QSpinBox::down-arrow {{ image: url({spin_down}); width: 8px; height: 8px; }}

            /* Item Views */
            QAbstractItemView {{ background-color: {sb}; outline: 0; }}
            QTreeView, QListWidget, QTableWidget, QTreeWidget {{ alternate-background-color: {adj(sb, 103)}; }}
            QTreeView::item:hover, QListWidget::item:hover {{ background-color: {adj(sb, 120)}; }}
            QTreeView::item:selected {{ background-color: {ac}; color: {c('button.foreground', '#000')}; }}
            QHeaderView::section {{ background-color: {adj(sb, 110)}; padding: 4px; border: 1px solid {wb}; }}
            QDockWidget::title {{
                background-color: {adj(wb, 105)}; text-align: left; padding: 5px;
                border-bottom: 1px solid {ibd};
            }}
            QGroupBox {{
                font-weight: bold; border: 1px solid {adj(ibd, 115)};
                border-radius: 6px; margin-top: 1em;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin; left: 10px; padding: 0 4px;
                color: {ac}; background-color: {wb};
            }}

            /* Scrollbar */
            QScrollBar:vertical {{ width: 10px; }}
            QScrollBar:horizontal {{ height: 10px; }}
            QScrollBar::handle {{ background: {c('scrollbar.handle', '#424d53')}; border-radius: 5px; min-height: 20px; }}
            QScrollBar::handle:hover {{ background: {c('scrollbar.handleHover', '#545e62')}; }}
            QScrollBar::add-line, QScrollBar::sub-line {{ height: 0px; width: 0px; }}
            QScrollBar::add-page, QScrollBar::sub-page {{ background: none; }}
        """
        app.setStyleSheet(stylesheet)
```

### File: `/app_core/syntax_highlighters.py`
```py
# PuffinPyEditor/app_core/syntax_highlighters.py
"""
This module serves as a central import point for all built-in syntax
highlighters. This prevents code duplication and makes it easier to manage
and extend language support.
"""
from .highlighters.python_syntax_highlighter import PythonSyntaxHighlighter
from .highlighters.json_syntax_highlighter import JsonSyntaxHighlighter
from .highlighters.html_syntax_highlighter import HtmlSyntaxHighlighter
from .highlighters.css_syntax_highlighter import CssSyntaxHighlighter
from .highlighters.cpp_syntax_highlighter import CppSyntaxHighlighter
from .highlighters.csharp_syntax_highlighter import CSharpSyntaxHighlighter
from .highlighters.javascript_syntax_highlighter import JavaScriptSyntaxHighlighter
from .highlighters.rust_syntax_highlighter import RustSyntaxHighlighter

__all__ = [
    "PythonSyntaxHighlighter",
    "JsonSyntaxHighlighter",
    "HtmlSyntaxHighlighter",
    "CssSyntaxHighlighter",
    "CppSyntaxHighlighter",
    "CSharpSyntaxHighlighter",
    "JavaScriptSyntaxHighlighter",
    "RustSyntaxHighlighter"
]
```

### File: `/app_core/source_control_manager.py`
```py
# PuffinPyEditor/app_core/source_control_manager.py
import os
import re
import git
from git import Repo, GitCommandError, InvalidGitRepositoryError, Actor
from typing import List, Optional
from PyQt6.QtCore import QObject, QThread, pyqtSignal
from utils.logger import log
import configparser


class GitWorker(QObject):
    """
    Worker that runs all GitPython operations in a background thread.
    """
    summaries_ready = pyqtSignal(dict)
    status_ready = pyqtSignal(list, list, list, str)
    error_occurred = pyqtSignal(str)
    # NEW SIGNAL: Specifically for the "dubious ownership" error
    dubious_ownership_detected = pyqtSignal(str)
    operation_success = pyqtSignal(str, dict)
    git_config_ready = pyqtSignal(str, str)

    def _get_commit_author(self, repo: Repo) -> Optional[Actor]:
        """Gets the commit author from the repository's configuration."""
        try:
            with repo.config_reader() as cr:
                name = cr.get_value('user', 'name', None)
                email = cr.get_value('user', 'email', None)
            if name and email:
                return Actor(name, email)
            git_cmd = git.Git(repo.working_dir)
            global_name = git_cmd.config('--global', '--get', 'user.name')
            global_email = git_cmd.config('--global', '--get', 'user.email')
            if global_name and global_email:
                return Actor(global_name, global_email)
            return None
        except Exception as e:
            log.error(f"Could not retrieve commit author: {e}")
            return None

    def get_git_config(self):
        """Reads the global Git user configuration."""
        try:
            git_cmd = git.Git()
            name = git_cmd.config('--global', '--get', 'user.name')
            email = git_cmd.config('--global', '--get', 'user.email')
            self.git_config_ready.emit(name, email)
        except GitCommandError:
            log.warning("Global Git user.name or user.email is not set.")
            self.git_config_ready.emit("", "")

    def set_git_config(self, name: str, email: str):
        """Sets the global Git user configuration."""
        try:
            git_cmd = git.Git()
            if name:
                git_cmd.config('--global', 'user.name', name)
            if email:
                git_cmd.config('--global', 'user.email', email)
            self.operation_success.emit("Global Git config updated.", {})
        except GitCommandError as e:
            log.error(f"Failed to set git config: {e}")
            self.error_occurred.emit(f"Failed to set Git config: {e}")

    # NEW METHOD: To apply the fix suggested by Git
    def add_safe_directory(self, path: str):
        """Adds a directory to Git's global safe.directory list."""
        try:
            git.Git().config('--global', '--add', 'safe.directory', path)
            log.info(f"Added '{path}' to global git safe.directory list.")
            self.operation_success.emit(f"Marked '{os.path.basename(path)}' as a safe repository.", {'repo_path': path})
        except GitCommandError as e:
            log.error(f"Failed to add safe directory: {e}")
            self.error_occurred.emit(f"Failed to mark repository as safe: {e}")

    def set_default_branch(self):
        """Sets the global Git config to use 'main' for new repositories."""
        try:
            git.Git().config('--global', 'init.defaultBranch', 'main')
            log.info("Set global init.defaultBranch to 'main'.")
            self.operation_success.emit(
                "Default branch for new repos is now 'main'.", {}
            )
        except GitCommandError as e:
            self.error_occurred.emit(f"Could not set default branch: {e}")

    def get_multiple_repo_summaries(self, repo_paths: List[str]):
        summaries = {}
        for path in repo_paths:
            try:
                repo = Repo(path, search_parent_directories=True)
                if repo.bare:
                    summaries[path] = {'branch': '(bare repo)',
                                       'commit': 'N/A'}
                elif not repo.head.is_valid():
                    summaries[path] = {'branch': '(no commits)',
                                       'commit': 'N/A'}
                else:
                    summaries[path] = {
                        'branch': repo.active_branch.name,
                        'commit': repo.head.commit.hexsha[:7]
                    }
            except InvalidGitRepositoryError:
                pass
            except Exception as e:
                log.error(f"Error getting Git summary for {path}: {e}")
                summaries[path] = {'branch': '(error)', 'commit': 'N/A'}
        self.summaries_ready.emit(summaries)

    def get_status(self, repo_path: str):
        try:
            repo = Repo(repo_path)
            staged = [item.a_path for item in repo.index.diff('HEAD')]
            unstaged = [item.a_path for item in repo.index.diff(None)]
            untracked = repo.untracked_files
            conflicted = [path for path, _ in repo.index.unmerged_blobs().items()]
            self.status_ready.emit(staged, unstaged + untracked, conflicted, repo_path)
        except GitCommandError as e:
            # MODIFIED: Intelligent error detection
            stderr_lower = str(e.stderr).lower()
            if "dubious ownership" in stderr_lower:
                log.warning(f"Git 'dubious ownership' error detected for {repo_path}")
                self.dubious_ownership_detected.emit(repo_path)
            else:
                err_msg = (
                    f"Git Status for '{os.path.basename(repo_path)}' "
                    f"failed: {e.stderr.strip()}"
                )
                self.error_occurred.emit(err_msg)
        except (InvalidGitRepositoryError, ValueError) as e:
            err_msg = (
                f"Git Status for '{os.path.basename(repo_path)}' "
                f"failed: {e}"
            )
            self.error_occurred.emit(err_msg)

    def commit_files(self, repo_path: str, message: str):
        try:
            # FIX: Add a try-except block to handle non-Git folders gracefully.
            repo = Repo(repo_path)
            author = self._get_commit_author(repo)
            if not author:
                self.error_occurred.emit(
                    "Commit author not found. Please set user.name and user.email in your Git config.")
                return

            repo.git.add(A=True)
            if repo.is_dirty(untracked_files=True):
                repo.index.commit(message, author=author, committer=author)
                self.operation_success.emit(
                    "Changes committed", {'repo_path': repo_path}
                )
            else:
                self.operation_success.emit(
                    "No new changes to commit.",
                    {'repo_path': repo_path, 'no_changes': True}
                )
        except InvalidGitRepositoryError:
            self.error_occurred.emit(f"'{os.path.basename(repo_path)}' is not a valid Git repository.")
        except GitCommandError as e:
            self.error_occurred.emit(f"Git Commit failed: {e.stderr}")

    def push(self, repo_path: str, tag_name: Optional[str] = None):
        try:
            # FIX: Add a try-except block to handle non-Git folders gracefully.
            repo = Repo(repo_path)
            origin = repo.remotes.origin
            if tag_name:
                log.info(f"Pushing tag '{tag_name}' to remote '{origin.url}'...")
                origin.push(tag_name)
                self.operation_success.emit(
                    f"Tag '{tag_name}' pushed successfully", {}
                )
            else:
                active_branch = repo.active_branch.name
                log.info(
                    f"Pushing branch '{active_branch}' to remote "
                    f"'{origin.url}'..."
                )
                origin.push(refspec=f'{active_branch}:{active_branch}')
                self.operation_success.emit("Push successful", {})
        except InvalidGitRepositoryError:
            self.error_occurred.emit(f"'{os.path.basename(repo_path)}' is not a valid Git repository.")
        except GitCommandError as e:
            stderr = str(e.stderr).lower()
            if "updates were rejected" in stderr:
                msg = ("Push rejected because the remote has changes you do not have locally. "
                       "Please 'Pull' changes from the remote, resolve any conflicts, and then try pushing again.")
            elif "authentication failed" in stderr:
                msg = ("Authentication failed. Please ensure you have configured a "
                       "Git Credential Manager or are using SSH for your remote URL. "
                       "Using passwords over HTTPS is not supported by GitHub.")
            elif "could not read from remote repository" in stderr:
                msg = ("Could not read from remote repository. Please ensure the URL "
                       "is correct and you have permission to access it.")
            elif "src refspec" in stderr and "does not match any" in stderr:
                msg = ("The local branch does not exist or does not match a remote "
                       "branch. You may need to publish the branch first.")
            else:
                msg = f"Git Push failed. Stderr: {e.stderr.strip()}"
            self.error_occurred.emit(msg)

    def pull(self, repo_path: str):
        try:
            # FIX: Add a try-except block to handle non-Git folders gracefully.
            repo = Repo(repo_path)
            origin = repo.remotes.origin
            log.info(f"Pulling from remote '{origin.url}'...")
            origin.pull()
            self.operation_success.emit("Pull successful", {})
            self.get_status(repo_path)
        except InvalidGitRepositoryError:
            self.error_occurred.emit(f"'{os.path.basename(repo_path)}' is not a valid Git repository.")
        except GitCommandError as e:
            stderr = str(e.stderr).lower()
            if "authentication failed" in stderr:
                msg = ("Authentication failed. Please ensure you have configured a "
                       "Git Credential Manager or are using SSH for your remote URL.")
            elif "you have unstaged changes" in stderr or "your local changes to the following files would be overwritten" in stderr:
                msg = "Pull failed. You have local changes that would be overwritten. Please commit or stash them first."
            elif "pull is not possible because you have unmerged files" in stderr:
                msg = "Pull failed because you have unresolved merge conflicts. Please resolve the conflicts, commit the result, and then try again."
            else:
                msg = f"Git Pull failed. Stderr: {e.stderr.strip()}"
            self.error_occurred.emit(msg)

    # NEW METHOD
    def force_push(self, repo_path: str):
        """Force pushes the current branch to the remote."""
        try:
            repo = Repo(repo_path)
            origin = repo.remotes.origin
            log.warning(f"FORCE PUSHING branch '{repo.active_branch.name}' to '{origin.url}'")
            origin.push(force=True)
            self.operation_success.emit("Force push successful.", {})
        except GitCommandError as e:
            self.error_occurred.emit(f"Force Push failed: {e.stderr.strip()}")

    # NEW METHOD
    def abort_merge(self, repo_path: str):
        """Aborts a conflicted merge state."""
        try:
            repo = Repo(repo_path)
            if os.path.exists(os.path.join(repo.git_dir, 'MERGE_HEAD')):
                log.info(f"Aborting merge in {repo_path}")
                repo.git.merge('--abort')
                self.operation_success.emit("Merge successfully aborted.", {})
            else:
                self.error_occurred.emit("No active merge to abort.")
        except GitCommandError as e:
            self.error_occurred.emit(f"Failed to abort merge: {e.stderr.strip()}")

    def clone_repo(self, url: str, path: str, branch: Optional[str] = None):
        try:
            target_dir = os.path.join(
                path, os.path.basename(url).replace('.git', '')
            )
            kwargs = {'branch': branch} if branch else {}
            log_msg = (
                f"Cloning '{url}' (branch: {branch or 'default'}) "
                f"into '{target_dir}'"
            )
            log.info(log_msg)
            Repo.clone_from(url, target_dir, **kwargs)
            self.operation_success.emit(
                "Clone successful", {"path": target_dir}
            )
        except GitCommandError as e:
            err_str = str(e).lower()
            if "not found in upstream origin" in err_str:
                msg = f"Branch '{branch}' not found in the remote repository."
            elif "authentication failed" in err_str:
                msg = ("Authentication failed. Repository may be private or "
                       "URL is incorrect.")
            else:
                msg = f"Clone failed: {e}"
            self.error_occurred.emit(msg)

    def create_tag(self, repo_path: str, tag: str, title: str):
        try:
            repo = Repo(repo_path)
            author = self._get_commit_author(repo)
            if not author:
                self.error_occurred.emit(
                    "Commit author not found. Please set user.name and user.email in your Git config.")
                return

            if not repo.head.is_valid():
                log.info("No commits found. Creating initial commit.")
                gitignore_path = os.path.join(repo_path, ".gitignore")
                if not os.path.exists(gitignore_path):
                    with open(gitignore_path, 'w', encoding='utf-8') as f:
                        f.write(
                            "# Python\n__pycache__/\n*.pyc\n\n# Env\n.env\nvenv/\n.venv/\n\n# Build\nbuild/\ndist/\n*.egg-info/\n")
                repo.git.add(A=True)
                if repo.is_dirty(untracked_files=True):
                    repo.index.commit("Initial commit", author=author, committer=author)
                else:
                    self.error_occurred.emit("Cannot tag an empty project with no changes to commit.")
                    return

            if tag in repo.tags:
                log.warning(f"Tag '{tag}' already exists. Re-creating it.")
                repo.delete_tag(tag)

            repo.create_tag(tag, message=title)
            self.operation_success.emit(f"Tag created: {tag}", {})
        except GitCommandError as e:
            self.error_occurred.emit(f"Failed to create tag: {e}")

    def delete_tag(self, repo_path: str, tag: str):
        try:
            repo = Repo(repo_path)
            repo.delete_tag(tag)
            self.operation_success.emit(f"Local tag '{tag}' deleted.", {})
        except GitCommandError as e:
            self.error_occurred.emit(f"Failed to delete local tag '{tag}': {e}")

    def delete_remote_tag(self, repo_path: str, tag: str):
        try:
            repo = Repo(repo_path)
            repo.remotes.origin.push(refspec=f":{tag}")
            self.operation_success.emit(f"Remote tag '{tag}' deleted.", {})
        except GitCommandError as e:
            self.error_occurred.emit(
                f"Failed to delete remote tag '{tag}': {e}"
            )

    def publish_repo(self, path: str, url: str):
        try:
            repo = Repo.init(path)
            author = self._get_commit_author(repo)
            if not author:
                self.error_occurred.emit(
                    "Could not determine commit author to publish. Please configure Git user.name and user.email.")
                return

            repo.git.branch('-M', 'main')
            if (repo.is_dirty(untracked_files=True) and
                    not repo.head.is_valid()):
                repo.git.add(A=True)
                repo.index.commit(
                    "Initial commit", author=author, committer=author
                )
            if 'origin' in repo.remotes:
                repo.remotes.origin.set_url(url)
            else:
                repo.create_remote('origin', url)
            repo.remotes.origin.push(refspec='main:main', set_upstream=True)
            self.operation_success.emit(
                f"Successfully published to {url}", {'repo_path': path}
            )
        except (GitCommandError, configparser.Error) as e:
            log.error(f"Publish failed: {e}", exc_info=True)
            self.error_occurred.emit(f"Publish failed: {e}")

    def link_to_remote(self, local_path: str, remote_url: str):
        try:
            repo = Repo.init(local_path)
            if 'origin' in repo.remotes:
                repo.remotes.origin.set_url(remote_url)
            else:
                repo.create_remote('origin', remote_url)
            repo.remotes.origin.fetch()
            remote_head = repo.remote().refs.HEAD
            if remote_head.is_valid():
                branch_name = remote_head.reference.name.split('/')[-1]
            else:
                branch_name = 'main'
            repo.git.branch('-M', branch_name)
            if remote_head.is_valid():
                repo.git.reset('--soft', f'origin/{branch_name}')
            if (repo.is_dirty(untracked_files=True) and
                    not repo.head.is_valid()):
                author = self._get_commit_author(repo)
                if not author:
                    self.error_occurred.emit(
                        "Could not determine commit author. Please configure Git user.name and user.email.")
                    return
                repo.git.add(A=True)
                repo.index.commit(
                    "Initial commit after linking to remote",
                    author=author, committer=author
                )
            self.operation_success.emit(
                f"Successfully linked to {remote_url}", {}
            )
        except (GitCommandError, configparser.Error) as e:
            self.error_occurred.emit(f"Failed to link repository: {e}")

    def fix_main_master_divergence(self, repo_path: str):
        try:
            repo = Repo(repo_path)
            log.info(f"Fixing branch mismatch in {repo_path}")
            repo.git.branch('-M', 'master', 'main')
            repo.git.push('--force', '-u', 'origin', 'main')
            repo.git.push('origin', '--delete', 'master')
            self.operation_success.emit(
                "'main' is now the primary branch.", {'repo_path': repo_path}
            )
        except GitCommandError as e:
            self.error_occurred.emit(f"Failed to fix branch mismatch: {e}")


class SourceControlManager(QObject):
    summaries_ready = pyqtSignal(dict)
    status_updated = pyqtSignal(list, list, list, str)
    git_error = pyqtSignal(str)
    # NEW SIGNAL
    dubious_ownership_detected = pyqtSignal(str)
    git_success = pyqtSignal(str, dict)
    git_config_ready = pyqtSignal(str, str)

    _request_summaries = pyqtSignal(list)
    _request_status = pyqtSignal(str)
    _request_commit = pyqtSignal(str, str)
    _request_push = pyqtSignal(str, str)
    _request_pull = pyqtSignal(str)
    _request_clone = pyqtSignal(str, str, object)
    _request_publish = pyqtSignal(str, str)
    _request_create_tag = pyqtSignal(str, str, str)
    _request_delete_tag = pyqtSignal(str, str)
    _request_delete_remote_tag = pyqtSignal(str, str)
    _request_link_to_remote = pyqtSignal(str, str)
    _request_get_git_config = pyqtSignal()
    _request_set_git_config = pyqtSignal(str, str)
    _request_fix_branches = pyqtSignal(str)
    _request_set_default_branch = pyqtSignal()
    _request_force_push = pyqtSignal(str)
    _request_abort_merge = pyqtSignal(str)
    # NEW REQUEST SIGNAL
    _request_add_safe_directory = pyqtSignal(str)

    def __init__(self, parent: Optional[QObject] = None):
        super().__init__(parent)
        self.thread = QThread()
        self.worker = GitWorker()
        self.worker.moveToThread(self.thread)
        self._request_summaries.connect(self.worker.get_multiple_repo_summaries)
        self._request_status.connect(self.worker.get_status)
        self._request_commit.connect(self.worker.commit_files)
        self._request_push.connect(self.worker.push)
        self._request_pull.connect(self.worker.pull)
        self._request_clone.connect(self.worker.clone_repo)
        self._request_publish.connect(self.worker.publish_repo)
        self._request_create_tag.connect(self.worker.create_tag)
        self._request_delete_tag.connect(self.worker.delete_tag)
        self._request_delete_remote_tag.connect(self.worker.delete_remote_tag)
        self._request_link_to_remote.connect(self.worker.link_to_remote)
        self._request_get_git_config.connect(self.worker.get_git_config)
        self._request_set_git_config.connect(self.worker.set_git_config)
        self._request_fix_branches.connect(
            self.worker.fix_main_master_divergence)
        self._request_set_default_branch.connect(
            self.worker.set_default_branch)
        self._request_force_push.connect(self.worker.force_push)
        self._request_abort_merge.connect(self.worker.abort_merge)
        self._request_add_safe_directory.connect(self.worker.add_safe_directory)

        self.worker.summaries_ready.connect(self.summaries_ready)
        self.worker.status_ready.connect(self.status_updated)
        self.worker.error_occurred.connect(self.git_error)
        self.worker.dubious_ownership_detected.connect(self.dubious_ownership_detected)
        self.worker.operation_success.connect(self.git_success)
        self.worker.git_config_ready.connect(self.git_config_ready)
        self.thread.start()

    @staticmethod
    def parse_git_url(url: str) -> tuple[Optional[str], Optional[str]]:
        if match := re.search(r"github\.com/([^/]+)/([^/.]+)", url):
            return match.group(1), match.group(2)
        if match := re.search(r"github\.com:([^/]+)/([^/.]+)", url):
            return match.group(1), match.group(2)
        return None, None

    def _get_commit_author(self, repo_path: str) -> Optional[Actor]:
        try:
            repo = Repo(repo_path)
            return self.worker._get_commit_author(repo)
        except Exception:
            return None

    def get_local_branches(self, repo_path: str) -> List[str]:
        try:
            return [b.name for b in Repo(repo_path).branches]
        except (InvalidGitRepositoryError, TypeError):
            return []

    def get_git_config(self):
        self._request_get_git_config.emit()

    def set_git_config(self, name: str, email: str):
        self._request_set_git_config.emit(name, email)

    # NEW PUBLIC METHOD
    def add_safe_directory(self, path: str):
        """Requests the worker to add a path to the safe.directory list."""
        self._request_add_safe_directory.emit(path)

    def set_default_branch_to_main(self):
        self._request_set_default_branch.emit()

    def link_to_remote(self, path: str, url: str):
        self._request_link_to_remote.emit(path, url)

    def fix_branch_mismatch(self, path: str):
        self._request_fix_branches.emit(path)

    def get_summaries(self, paths: List[str]):
        self._request_summaries.emit(paths)

    def get_status(self, path: str):
        self._request_status.emit(path)

    def commit_files(self, path: str, msg: str):
        self._request_commit.emit(path, msg)

    def push(self, path: str):
        self._request_push.emit(path, None)

    def push_specific_tag(self, path: str, tag_name: str):
        self._request_push.emit(path, tag_name)

    def pull(self, path: str):
        self._request_pull.emit(path)

    def force_push(self, path: str):
        self._request_force_push.emit(path)

    def abort_merge(self, path: str):
        self._request_abort_merge.emit(path)

    def clone_repo(self, url: str, path: str, branch: Optional[str] = None):
        self._request_clone.emit(url, path, branch)

    def publish_repo(self, path: str, url: str):
        self._request_publish.emit(path, url)

    def create_tag(self, path: str, tag: str, title: str):
        self._request_create_tag.emit(path, tag, title)

    def delete_tag(self, path: str, tag: str):
        self._request_delete_tag.emit(path, tag)

    def delete_remote_tag(self, path: str, tag: str):
        self._request_delete_remote_tag.emit(path, tag)

    def shutdown(self):
        if self.thread and self.thread.isRunning():
            log.info("Shutting down SourceControlManager thread.")
            self.thread.quit()
            if not self.thread.wait(3000):
                log.warning(
                    "SourceControlManager thread did not shut down "
                    "gracefully. Terminating."
                )
                self.thread.terminate()
```

### File: `/app_core/settings_manager.py`
```py
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
```

### File: `/app_core/puffin_api.py`
```py
# PuffinPyEditor/app_core/puffin_api.py
from typing import Callable, Optional, Any, TYPE_CHECKING
from PyQt6.QtWidgets import (QDockWidget, QTabWidget, QWidget, QMenu, QMessageBox)
from PyQt6.QtGui import QAction
from PyQt6.QtCore import Qt
import qtawesome as qta
from utils.logger import log

if TYPE_CHECKING:
    from ui.main_window import MainWindow
    from ui.editor_widget import HighlightManager


class PuffinPluginAPI:
    def __init__(self, main_window: 'MainWindow'):
        self._main_window = main_window
        self.theme_editor_launcher: Optional[Callable] = None
        self.highlighter_map: dict[str, Any] = {}
        # This will be set by MainWindow after it creates the manager
        self.highlight_manager: Optional['HighlightManager'] = None
        log.info("PuffinPluginAPI initialized.")

    def get_main_window(self) -> 'MainWindow':
        return self._main_window

    def get_manager(self, manager_name: str) -> Optional[Any]:
        name_map = {
            "project": self._main_window.project_manager, "file_handler": self._main_window.file_handler,
            "settings": self._main_window.settings, "theme": self._main_window.theme_manager,
            "completion": self._main_window.completion_manager, "github": self._main_window.github_manager,
            "git": self._main_window.git_manager, "linter": self._main_window.linter_manager,
            "update": self._main_window.update_manager, "plugin": self._main_window.plugin_manager,
        }
        if not (manager := name_map.get(manager_name.lower())):
            log.warning(f"Plugin requested an unknown manager: '{manager_name}'")
        return manager

    def add_dock_panel(self, widget: QWidget, title: str, area_str: str, icon_name: Optional[str] = None) -> Optional[QDockWidget]:
        # THE FIX: This method now passes the string 'area_str' directly to the main window,
        # which expects a string. The API layer no longer does the conversion, preventing the type mismatch.
        return self._main_window.add_dock_panel(widget, title, area_str, icon_name)

    def get_plugin_instance(self, plugin_id: str) -> Optional[Any]:
        if plugin_manager := self.get_manager("plugin"):
            if plugin := plugin_manager.plugins.get(plugin_id):
                if plugin.is_loaded: return plugin.instance
        log.warning(f"Could not find a loaded plugin instance for ID: '{plugin_id}'")
        return None

    def register_theme_editor_launcher(self, launcher_callback: Callable):
        self.theme_editor_launcher = launcher_callback
        log.info("A theme editor launcher has been registered.")
        if hasattr(mw := self.get_main_window(), 'preferences_dialog') and mw.preferences_dialog:
            mw.preferences_dialog.connect_theme_editor_button()

    def get_menu(self, menu_name: str) -> Optional[QMenu]:
        """Gets a reference to one of the main window's top-level menus."""
        return getattr(self._main_window, f"{menu_name.lower()}_menu", None)

    def register_highlighter(self, extension: str, highlighter_class):
        if not extension.startswith('.'): extension = f".{extension}"
        self.highlighter_map[extension.lower()] = highlighter_class
        log.info(f"Registered highlighter '{highlighter_class.__name__}' for '{extension}' files.")

    def add_menu_action(self, menu_name, text, callback, shortcut=None, icon_name=None) -> QAction:
        menu = getattr(self._main_window, f"{menu_name.lower()}_menu", None)
        if not menu:
            menu = self._main_window.menuBar().addMenu(f"&{menu_name.capitalize()}")
            setattr(self._main_window, f"{menu_name.lower()}_menu", menu)

        icon = qta.icon(icon_name) if icon_name else None
        action = QAction(icon, text, self._main_window)
        if shortcut: action.setShortcut(shortcut)
        action.triggered.connect(callback)
        menu.addAction(action)
        return action

    def add_toolbar_action(self, action: QAction):
        """Adds a QAction to the main application toolbar."""
        if hasattr(self._main_window, 'main_toolbar'):
            self._main_window.main_toolbar.addAction(action)
            log.info(f"Added action '{action.text()}' to main toolbar.")
        else:
            log.error("Cannot add toolbar action: Main toolbar not found.")

    def register_dock_panel(self, content_widget, title, area, icon_name=None):
        log.warning("`register_dock_panel` is deprecated. Use `add_dock_panel` instead.")
        area_map = {
            Qt.DockWidgetArea.LeftDockWidgetArea: "left",
            Qt.DockWidgetArea.RightDockWidgetArea: "right",
            Qt.DockWidgetArea.TopDockWidgetArea: "top",
            Qt.DockWidgetArea.BottomDockWidgetArea: "bottom",
        }
        area_str = area_map.get(area, "bottom")
        self.add_dock_panel(content_widget, title, area_str, icon_name)

    def register_file_opener(self, extension: str, handler_callable: Callable):
        if not extension.startswith('.'): extension = f".{extension}"
        self._main_window.file_open_handlers[extension.lower()] = handler_callable

    def show_message(self, level, title, text):
        icon_map = {'info': QMessageBox.Icon.Information, 'warning': QMessageBox.Icon.Warning,
                    'critical': QMessageBox.Icon.Critical}
        icon = icon_map.get(level.lower(), QMessageBox.Icon.NoIcon)
        msg_box = QMessageBox(icon, title, text, parent=self._main_window)
        msg_box.exec()

    def show_status_message(self, message: str, timeout: int = 4000):
        self._main_window.statusBar().showMessage(message, timeout)

    def log_info(self, msg):
        log.info(f"[Plugin] {msg}")

    def log_warning(self, msg):
        log.warning(f"[Plugin] {msg}")

    def log_error(self, msg):
        log.error(f"[Plugin] {msg}")
```

### File: `/app_core/project_manager.py`
```py
# PuffinPyEditor/app_core/project_manager.py
import os
import datetime
import zipfile
from pathlib import Path
from typing import List, Tuple, Optional, Dict

from PyQt6.QtCore import QObject, pyqtSignal

from .settings_manager import settings_manager
from utils.logger import log
from utils.helpers import clean_git_conflict_markers # Import the moved function


class ProjectManager(QObject):
    """Manages the state of open projects and project-wide operations."""

    projects_changed = pyqtSignal()

    def __init__(self):
        super().__init__()
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
            self.projects_changed.emit()
        self.set_active_project(norm_path)
        return True

    def close_project(self, path: str):
        """Closes a project and updates the active project if necessary."""
        norm_path = os.path.normpath(path)
        if norm_path in self._open_projects:
            was_active = (self.get_active_project_path() == norm_path)
            
            self._open_projects.remove(norm_path)
            log.info(f"Project closed: {norm_path}")

            # If the closed project was the active one, pick a new active one
            if was_active:
                new_active_path = self._open_projects[0] if self._open_projects else None
                # Directly set the internal variable. We will emit the signal once at the end.
                if self._active_project_path != new_active_path:
                    self._active_project_path = new_active_path
                    log.info(f"Active project changed to: {new_active_path}")
            
            self.save_session()
            # A single, definitive signal emission to trigger the UI refresh.
            self.projects_changed.emit()

    def move_project(self, path_to_move: str, direction: str):
        """Moves a project up or down in the list."""
        norm_path = os.path.normpath(path_to_move)
        if norm_path not in self._open_projects:
            return

        idx = self._open_projects.index(norm_path)
        if direction == 'up' and idx > 0:
            self._open_projects.insert(idx - 1, self._open_projects.pop(idx))
            self.save_session()
            self.projects_changed.emit()
        elif direction == 'down' and idx < len(self._open_projects) - 1:
            self._open_projects.insert(idx + 1, self._open_projects.pop(idx))
            self.save_session()
            self.projects_changed.emit()

    def move_project_to_end(self, path_to_move: str, to_top: bool):
        """Moves a project to the top or bottom of the list."""
        norm_path = os.path.normpath(path_to_move)
        if norm_path not in self._open_projects:
            return

        item = self._open_projects.pop(self._open_projects.index(norm_path))
        if to_top:
            self._open_projects.insert(0, item)
        else:
            self._open_projects.append(item)

        self.save_session()
        self.projects_changed.emit()

    def get_open_projects(self) -> List[str]:
        """Returns the list of currently open project paths."""
        return self._open_projects

    def set_active_project(self, path: Optional[str]):
        """
        Sets the currently active project. The project MUST already be in the open list.
        """
        norm_path = os.path.normpath(path) if path else None
        
        # THE FIX: This guard clause prevents a closed project from being
        # re-activated by a UI signal. A project must be in the open list
        # to become the active project.
        if norm_path and norm_path not in self._open_projects:
            log.warning(
                f"Attempted to set active project to '{norm_path}', "
                "but it's not in the open projects list. Ignoring."
            )
            return

        if self._active_project_path != norm_path:
            self._active_project_path = norm_path
            log.info(f"Active project set to: {norm_path}")
            self.projects_changed.emit()

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
        ignore_files = {'.gitignore', 'puffin_editor_settings.json'}

        try:
            with zipfile.ZipFile(
                    output_zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, dirs, files in os.walk(project_root):
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

    def generate_file_tree_from_list(
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
            entries = sorted(
                d.keys(), key=lambda k: (not bool(d[k]), k.lower())
            )
            for i, name in enumerate(entries):
                is_last = (i == len(entries) - 1)
                connector = "└── " if is_last else "├── "
                lines.append(f"{prefix}{connector}{name}")
                if d[name]:
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
            [f"{i + 1}. {g}" for i, g in enumerate(golden_rules)]
        ) if golden_rules else "No specific golden rules were provided."
        output_lines.append(golden_rules_text)
        output_lines.extend(["```", "---"])

        output_lines.append("\n## 🗂️ File Tree of Included Files:\n```")
        output_lines.append(f"/{project_name}")
        tree_text_lines = self.generate_file_tree_from_list(project_root, selected_files)
        output_lines.extend(tree_text_lines)
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
                    original_content = f.read()
                    # Use the refactored utility function
                    cleaned_content = clean_git_conflict_markers(original_content)
                    if original_content != cleaned_content:
                        log.info(f"Cleaned git conflict markers from {filepath} for export.")
                    output_lines.append(cleaned_content)
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

### File: `/app_core/plugin_manager.py`
```py
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
from utils.helpers import get_base_path
from app_core.puffin_api import PuffinPluginAPI  # Import API for type hinting

try:
    from packaging.version import Version, InvalidVersion
except ImportError:
    log.warning(
        "The 'packaging' library is not installed. Version comparison will be basic. Run 'pip install packaging'.")


    # Define dummy classes if 'packaging' is not available
    class _DummyVersion:
        def __init__(self, v): self.v = v

        def __eq__(self, o): return self.v == o.v

        def __lt__(self, o): return self.v < o.v

        def __le__(self, o): return self.v <= o.v

        def __gt__(self, o): return self.v > o.v

        def __ge__(self, o): return self.v >= o.v


    Version = _DummyVersion
    InvalidVersion = ValueError


@dataclass
class Plugin:
    """A dataclass to hold all information about a plugin."""
    manifest: Dict[str, Any]
    path: str
    source_type: str  # 'built-in', 'core-tool', 'user'
    is_core: bool = False
    is_loaded: bool = False
    enabled: bool = True
    module: Optional[Any] = None
    instance: Optional[Any] = None
    status_reason: str = "Not loaded"

    @property
    def id(self) -> str: return self.manifest.get('id', 'unknown')

    @property
    def name(self) -> str: return self.manifest.get('name', self.id)

    @property
    def version(self) -> str: return self.manifest.get('version', '0.0.0')


class PluginManager:
    ESSENTIAL_PLUGIN_IDS = {
        'python_tools',
    }

    def __init__(self, main_window):
        self.api: PuffinPluginAPI = main_window.puffin_api
        base_app_path = get_base_path()
        app_data_path = get_app_data_path()
        self.built_in_plugins_dir = os.path.join(base_app_path, "plugins")
        self.core_tools_directory = os.path.join(base_app_path, "core_debug_tools")
        self.user_plugins_directory = os.path.join(app_data_path, "plugins")
        self.plugin_states_file = os.path.join(app_data_path, "plugin_states.json")
        self._ensure_paths_and_packages()
        self.plugins: Dict[str, Plugin] = {}
        log.info("PluginManager initialized with a shared API.")

    def _ensure_paths_and_packages(self):
        for path in [get_base_path(), self.user_plugins_directory]:
            if path not in sys.path:
                sys.path.insert(0, path)
                log.info(f"Added to sys.path: {path}")
        if not os.path.isdir(self.user_plugins_directory):
            log.info(f"Creating user plugins directory: {self.user_plugins_directory}")
            os.makedirs(self.user_plugins_directory)
        init_path = os.path.join(self.user_plugins_directory, "__init__.py")
        if not os.path.exists(init_path):
            with open(init_path, 'w', encoding='utf-8') as f:
                f.write("# This file makes the plugins directory a package.\n")

    def discover_and_load_plugins(self, ignore_list: Optional[List[str]] = None):
        log.info("Starting full plugin discovery and loading process...")
        ignore_list = ignore_list or []
        for plugin in self.get_loaded_plugins():
            self.unload_plugin(plugin.id)

        self.plugins.clear()
        self._discover_plugins()
        self._load_plugin_states()
        load_order = self._resolve_dependencies()
        for plugin_id in load_order:
            plugin = self.plugins.get(plugin_id)
            if plugin_id in ignore_list:
                log.info(f"Skipping plugin '{plugin.name if plugin else plugin_id}' as it's in the ignore list.")
                if plugin: plugin.status_reason = "Ignored (pre-loaded)"
                continue
            if plugin and plugin.enabled:
                self.load_plugin(plugin_id)
            elif plugin:
                log.info(f"Plugin '{plugin.name}' is disabled and will not be loaded.")
        log.info("Plugin discovery and loading complete.")

    def _discover_plugins(self):
        plugin_sources = {
            "built-in": self.built_in_plugins_dir,
            "core-tool": self.core_tools_directory,
            "user": self.user_plugins_directory,
        }
        for source_type, plugin_dir in plugin_sources.items():
            if not os.path.isdir(plugin_dir): continue
            for item_name in os.listdir(plugin_dir):
                if item_name.startswith(('__', '.')): continue
                plugin_path = os.path.join(plugin_dir, item_name)
                if os.path.isdir(plugin_path):
                    self._process_potential_plugin(plugin_path, source_type)

    def _process_potential_plugin(self, plugin_path: str, source_type: str):
        manifest_path = os.path.join(plugin_path, "plugin.json")
        if not os.path.exists(manifest_path): return
        try:
            with open(manifest_path, 'r', encoding='utf-8') as f:
                manifest = json.load(f)
            if not self._validate_manifest(manifest, manifest_path): return
            plugin_id = manifest['id']
            if plugin_id in self.plugins: return

            plugin = Plugin(manifest=manifest, path=plugin_path, source_type=source_type)
            plugin.is_core = plugin.id in self.ESSENTIAL_PLUGIN_IDS

            self.plugins[plugin_id] = plugin
        except (json.JSONDecodeError, IOError) as e:
            log.error(f"Failed to read or parse manifest at '{manifest_path}': {e}")

    def _validate_manifest(self, manifest: Dict, path: str) -> bool:
        for field in ['id', 'name', 'version']:
            if field not in manifest or not manifest[field]:
                log.error(f"Manifest at {path} is missing or has empty field: '{field}'. Skipping.")
                return False
        return True

    def _resolve_dependencies(self) -> List[str]:
        log.info("Resolving plugin dependencies...")
        dependencies = {}
        for pid, p in self.plugins.items():
            deps_field = p.manifest.get('dependencies', [])
            if isinstance(deps_field, dict):
                dependencies[pid] = set(deps_field.keys())
            elif isinstance(deps_field, list):
                dependencies[pid] = set(deps_field)
            else:
                log.warning(f"Plugin '{p.name}' has an invalid 'dependencies' format. Must be an object or array.")
                dependencies[pid] = set()

        load_order, resolved = [], set()
        while len(load_order) < len(self.plugins):
            ready = {pid for pid, deps in dependencies.items() if pid not in resolved and not deps - resolved}
            if not ready:
                unresolved = {pid: deps - resolved for pid, deps in dependencies.items() if pid not in resolved}
                log.error(f"Could not resolve plugin dependencies. Circular or missing. Unresolved: {unresolved}")
                for pid, missing in unresolved.items():
                    if pid in self.plugins:
                        self.plugins[pid].enabled = False
                        self.plugins[pid].status_reason = f"Dependency error: {missing}"
                break

            for plugin_id in sorted(list(ready)):
                plugin = self.plugins.get(plugin_id)
                if not plugin: continue

                can_load = True
                deps_dict = plugin.manifest.get('dependencies', {})
                if isinstance(deps_dict, dict):
                    for dep_id, req_ver in deps_dict.items():
                        dep_plugin = self.plugins.get(dep_id)
                        if not dep_plugin or not dep_plugin.enabled:
                            plugin.status_reason = f"Missing or disabled dependency: {dep_id}"
                            can_load = False
                            break
                        if not self._check_version(dep_plugin.version, req_ver):
                            plugin.status_reason = f"Version conflict for '{dep_id}'. Have {dep_plugin.version}, need {req_ver}"
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

    def _check_version(self, installed_version: str, required_version_spec: str) -> bool:
        try:
            installed, spec = Version(installed_version), required_version_spec.strip()
            if spec.startswith('>='): return installed >= Version(spec[2:])
            if spec.startswith('<='): return installed <= Version(spec[2:])
            if spec.startswith('=='): return installed == Version(spec[2:])
            if spec.startswith('>'): return installed > Version(spec[1:])
            if spec.startswith('<'): return installed < Version(spec[1:])
            return installed == Version(spec)
        except (InvalidVersion, ValueError) as e:
            log.warning(
                f"Could not parse version. installed='{installed_version}', required='{required_version_spec}'. Error: {e}")
            return False

    def load_plugin(self, plugin_id: str) -> bool:
        plugin = self.plugins.get(plugin_id)
        if not plugin or plugin.is_loaded: return False

        entry_point = plugin.manifest.get("entry_point", "plugin_main.py")
        entry_point_path = os.path.join(plugin.path, entry_point)

        if not os.path.exists(entry_point_path):
            plugin.status_reason = f"Entry point '{entry_point}' not found."
            log.error(f"{plugin.status_reason} for plugin '{plugin.name}'.")
            return False

        entry_module_name = os.path.splitext(entry_point)[0]
        package_name = plugin.id if plugin.source_type == 'user' else f"{os.path.basename(os.path.dirname(plugin.path))}.{plugin.id}"
        module_name = f"{package_name}.{entry_module_name}"

        try:
            spec = importlib.util.spec_from_file_location(module_name, entry_point_path)
            if not spec or not spec.loader: raise ImportError(f"Could not create module spec for {module_name}")
            module = importlib.util.module_from_spec(spec)
            sys.modules[module_name] = module
            spec.loader.exec_module(module)

            if hasattr(module, 'initialize'):
                arg_to_pass = self.api
                plugin.instance = module.initialize(arg_to_pass)
                plugin.module = module
                plugin.is_loaded = True
                plugin.status_reason = "Loaded successfully"
                log.info(f"Successfully initialized plugin: '{plugin.name}' (Version: {plugin.version})")
                return True
            else:
                plugin.status_reason = "No 'initialize' function found."
                log.error(f"Plugin '{plugin.name}' has no 'initialize' function. Skipping.")
                if module_name in sys.modules: del sys.modules[module_name]
                return False
        except Exception as e:
            plugin.status_reason = f"Load error: {e}"
            log.error(f"An unexpected error occurred loading plugin '{plugin.name}': {e}", exc_info=True)
            if module_name in sys.modules: del sys.modules[module_name]
            return False

    def unload_plugin(self, plugin_id: str) -> bool:
        plugin = self.plugins.get(plugin_id)
        if not plugin or not plugin.is_loaded: return True
        log.info(f"Unloading plugin: '{plugin.name}'")
        try:
            if hasattr(plugin.instance, 'shutdown'): plugin.instance.shutdown()

            plugin.is_loaded = False
            plugin.instance = None
            module_name = plugin.module.__name__ if plugin.module else None
            plugin.module = None

            if module_name and module_name in sys.modules:
                del sys.modules[module_name]

            import gc
            gc.collect()

            plugin.status_reason = "Unloaded";
            log.info(f"Successfully unloaded plugin '{plugin.name}'.")
            return True
        except Exception as e:
            plugin.status_reason = f"Unload error: {e}";
            log.error(f"Error during shutdown of plugin '{plugin.name}': {e}", exc_info=True)
            return False

    def reload_plugin(self, plugin_id: str) -> bool:
        log.info(f"Reloading plugin '{plugin_id}'...")
        if self.unload_plugin(plugin_id):
            return self.load_plugin(plugin_id)
        log.error(f"Failed to unload plugin '{plugin_id}' during reload process.")
        return False

    def enable_plugin(self, plugin_id: str):
        plugin = self.plugins.get(plugin_id)
        if not plugin:
            log.error(f"Cannot enable non-existent plugin '{plugin_id}'")
            return
        plugin.enabled = True
        self._save_plugin_states()
        log.info(f"Plugin '{plugin.name}' enabled. Re-evaluating and loading plugins.")
        self.discover_and_load_plugins()

    def disable_plugin(self, plugin_id: str):
        plugin = self.plugins.get(plugin_id)
        if not plugin:
            log.error(f"Cannot disable non-existent plugin '{plugin_id}'")
            return

        plugin.enabled = False
        self._save_plugin_states()
        log.info(f"Plugin '{plugin.name}' disabled. Re-evaluating all plugins.")
        self.discover_and_load_plugins()

    def enable_all(self):
        log.info("Enabling all plugins.")
        for plugin in self.plugins.values():
            plugin.enabled = True
        self._save_plugin_states()
        log.info("All plugins enabled. Re-evaluating and loading all plugins.")
        self.discover_and_load_plugins()

    def disable_all_non_core(self):
        log.info("Disabling all non-essential plugins.")
        plugins_to_disable_ids = [p.id for p in self.plugins.values() if not p.is_core]

        if not plugins_to_disable_ids:
            log.info("No non-essential plugins to disable.")
            return

        for plugin_id in plugins_to_disable_ids:
            plugin = self.plugins.get(plugin_id)
            if plugin:
                plugin.enabled = False

        self._save_plugin_states()
        log.info(f"Marked {len(plugins_to_disable_ids)} non-essential plugins as disabled. Re-evaluating all plugins.")
        self.discover_and_load_plugins()

    def _load_plugin_states(self):
        if not os.path.exists(self.plugin_states_file): return
        try:
            with open(self.plugin_states_file, 'r', encoding='utf-8') as f:
                states = json.load(f)
            for pid, state in states.items():
                if pid in self.plugins and isinstance(state, dict): self.plugins[pid].enabled = state.get('enabled',
                                                                                                          True)
        except (IOError, json.JSONDecodeError) as e:
            log.warning(f"Could not load plugin states from {self.plugin_states_file}: {e}")

    def _save_plugin_states(self):
        states = {pid: {'enabled': p.enabled} for pid, p in self.plugins.items()}
        try:
            with open(self.plugin_states_file, 'w', encoding='utf-8') as f:
                json.dump(states, f, indent=4)
        except IOError as e:
            log.error(f"Could not save plugin states to {self.plugin_states_file}: {e}")

    def get_all_plugins(self) -> List[Plugin]:
        return list(self.plugins.values())

    def get_installed_plugins(self) -> list:
        """
        Returns a list of dictionaries, where each dictionary contains the
        plugin's manifest data plus its absolute path and source type.
        This provides all necessary info for tools like the Plugin Publisher.
        """
        installed_plugins_data = []
        for p in self.get_all_plugins():
            # Create a copy of the manifest to avoid modifying the original
            plugin_data = p.manifest.copy()
            # Add the crucial path and source_type information
            plugin_data['path'] = p.path
            plugin_data['source_type'] = p.source_type
            installed_plugins_data.append(plugin_data)
        return installed_plugins_data

    def get_loaded_plugins(self) -> List[Plugin]:
        return [p for p in self.plugins.values() if p.is_loaded]

    def get_plugin_instance_by_id(self, plugin_id: str) -> Optional[Any]:
        plugin = self.plugins.get(plugin_id)
        if plugin and plugin.is_loaded:
            return plugin.instance
        return None

    def install_plugin_from_zip(self, zip_filepath: str) -> Tuple[bool, str]:
        if not zipfile.is_zipfile(zip_filepath): return False, "Not a valid zip archive."
        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                with zipfile.ZipFile(zip_filepath, 'r') as z:
                    z.extractall(temp_dir)
                items = os.listdir(temp_dir);
                is_nested = len(items) == 1 and os.path.isdir(os.path.join(temp_dir, items[0]))
                src_dir = os.path.join(temp_dir, items[0]) if is_nested else temp_dir
                manifest_path = os.path.join(src_dir, 'plugin.json')
                if not os.path.exists(manifest_path): return False, "Archive is missing 'plugin.json'."
                with open(manifest_path, 'r', encoding='utf-8') as f:
                    manifest = json.load(f)
                if not self._validate_manifest(manifest, manifest_path): return False, "Plugin manifest is invalid."
                plugin_id = manifest['id'];
                target_path = os.path.join(self.user_plugins_directory, plugin_id)
                if os.path.exists(target_path): return False, f"A plugin with ID '{plugin_id}' already exists."
                shutil.move(src_dir, target_path);
                plugin_name = manifest.get('name', plugin_id)
                log.info(f"Plugin '{plugin_name}' installed. Reloading plugins...")
                self.discover_and_load_plugins()
                return True, f"Plugin '{plugin_name}' installed and loaded."
        except Exception as e:
            log.error(f"Failed to install plugin from {zip_filepath}: {e}", exc_info=True)
            return False, f"An unexpected error occurred: {e}"

    def uninstall_plugin(self, plugin_id: str) -> Tuple[bool, str]:
        plugin = self.plugins.get(plugin_id)
        if not plugin: return False, f"Plugin '{plugin_id}' is not installed."
        if plugin.source_type != 'user':
            return False, "This is a built-in or core tool and cannot be uninstalled."

        self.unload_plugin(plugin_id)
        target_path = os.path.join(self.user_plugins_directory, plugin_id)
        if not os.path.isdir(target_path): return False, f"Plugin directory for '{plugin_id}' not found."
        try:
            shutil.rmtree(target_path)
            if plugin_id in self.plugins: del self.plugins[plugin_id]
            self._save_plugin_states()
            log.info(f"Successfully uninstalled plugin '{plugin_id}'.")
            return True, f"Plugin '{plugin_id}' was uninstalled."
        except OSError as e:
            log.error(f"Failed to uninstall plugin '{plugin_id}': {e}", exc_info=True)
            return False, f"Error removing plugin directory: {e}"
```

### File: `/app_core/linter_manager.py`
```py
# PuffinPyEditor/app_core/linter_manager.py
import subprocess
import os
import sys
import shutil
from typing import List, Dict, Optional
from PyQt6.QtCore import QObject, QThread, pyqtSignal
from utils.logger import log

# Use a very unlikely string as a delimiter
SAFE_DELIMITER = "|||PUFFIN_LINT|||"


class LinterRunner(QObject):
    """
    A worker QObject that runs flake8 in a separate thread to avoid
    blocking the main UI.
    """
    lint_results_ready = pyqtSignal(list)
    project_lint_results_ready = pyqtSignal(dict)
    error_occurred = pyqtSignal(str)

    def _find_flake8_executable(self) -> Optional[str]:
        """Finds the path to the flake8 executable."""
        return shutil.which("flake8")

    def run_linter_on_file(self, filepath: str):
        """Runs flake8 on a single file and emits the results."""
        if not filepath or not os.path.exists(filepath):
            self.lint_results_ready.emit([])
            return

        flake8_executable = self._find_flake8_executable()
        if not flake8_executable:
            msg = "'flake8' executable not found. Please install it."
            log.error(f"Linter error: {msg}")
            self.error_occurred.emit(msg)
            return

        command = [flake8_executable, filepath,
                   "--format=%(row)d:%(col)d:%(code)s:%(text)s"]
        log.info(f"Running linter on file: {' '.join(command)}")

        try:
            # CREATE_NO_WINDOW prevents a console flash on Windows
            creation_flags = 0
            if sys.platform == "win32":
                creation_flags = subprocess.CREATE_NO_WINDOW

            process = subprocess.Popen(
                command, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                text=True, encoding='utf-8', creationflags=creation_flags
            )
            stdout, stderr = process.communicate(timeout=15)

            if stderr:
                log.error(f"Linter stderr for {filepath}: {stderr.strip()}")

            results = self._parse_flake8_file_output(stdout)
            self.lint_results_ready.emit(results)
        except Exception as e:
            log.error(f"Exception while running flake8 on file: {e}",
                      exc_info=True)
            self.lint_results_ready.emit([])

    def run_linter_on_project(self, project_path: str):
        """Runs flake8 recursively on a project path and emits the results."""
        flake8_executable = self._find_flake8_executable()
        if not flake8_executable:
            msg = "'flake8' executable not found. Cannot lint project."
            log.error(msg)
            self.error_occurred.emit(msg)
            return

        # Use the safe delimiter to reliably parse file paths from output
        format_str = (f"--format=%(path)s{SAFE_DELIMITER}%(row)d"
                      f"{SAFE_DELIMITER}%(col)d{SAFE_DELIMITER}%(code)s"
                      f"{SAFE_DELIMITER}%(text)s")
        command = [flake8_executable, project_path, format_str]
        log.info(f"Running linter on project: {project_path}")

        try:
            creation_flags = 0
            if sys.platform == "win32":
                creation_flags = subprocess.CREATE_NO_WINDOW
            process = subprocess.Popen(
                command, cwd=project_path, stdout=subprocess.PIPE,
                stderr=subprocess.PIPE, text=True, encoding='utf-8',
                creationflags=creation_flags
            )
            stdout, stderr = process.communicate(timeout=60)

            if stderr:
                log.warning(
                    f"Linter stderr for {project_path}: {stderr.strip()}"
                )

            results = self._parse_flake8_project_output(stdout, project_path)
            self.project_lint_results_ready.emit(results)
        except Exception as e:
            log.error(f"Exception while running flake8 on project: {e}",
                      exc_info=True)
            self.project_lint_results_ready.emit({})

    def _parse_flake8_file_output(self, output: str) -> List[Dict]:
        """Parses standard flake8 output for a single file."""
        problems = []
        for line in output.strip().splitlines():
            parts = line.split(':', 3)
            if len(parts) == 4:
                try:
                    problems.append({
                        "line": int(parts[0]),
                        "col": int(parts[1]),
                        "code": parts[2],
                        "description": parts[3].strip()
                    })
                except (ValueError, IndexError):
                    log.warning(f"Could not parse linter line: {line}")
        return problems

    def _parse_flake8_project_output(
        self, output: str, project_path: str
    ) -> Dict[str, List[Dict]]:
        """Parses flake8 output that uses the custom SAFE_DELIMITER."""
        problems_by_file = {}
        for line in output.strip().splitlines():
            parts = line.split(SAFE_DELIMITER, 4)
            if len(parts) == 5:
                try:
                    raw_path, line_num, col_num, code, desc = parts
                    # Ensure the path is absolute and normalized
                    abs_path = os.path.normpath(
                        os.path.join(project_path, raw_path)
                    )
                    problem = {
                        "line": int(line_num),
                        "col": int(col_num),
                        "code": code,
                        "description": desc.strip()
                    }
                    if abs_path not in problems_by_file:
                        problems_by_file[abs_path] = []
                    problems_by_file[abs_path].append(problem)
                except (ValueError, IndexError):
                    log.warning(f"Could not parse project linter line: {line}")
        return problems_by_file


class LinterManager(QObject):
    """
    Manages linting operations by delegating to a LinterRunner on a
    separate thread.
    """
    lint_results_ready = pyqtSignal(list)
    project_lint_results_ready = pyqtSignal(dict)
    error_occurred = pyqtSignal(str)

    _request_file_lint = pyqtSignal(str)
    _request_project_lint = pyqtSignal(str)

    def __init__(self, parent: Optional[QObject] = None):
        super().__init__(parent)
        self.thread = QThread()
        self.runner = LinterRunner()
        self.runner.moveToThread(self.thread)

        # Connect signals
        self._request_file_lint.connect(self.runner.run_linter_on_file)
        self._request_project_lint.connect(self.runner.run_linter_on_project)
        self.runner.lint_results_ready.connect(self.lint_results_ready)
        self.runner.project_lint_results_ready.connect(
            self.project_lint_results_ready
        )
        self.runner.error_occurred.connect(self.error_occurred)

        self.thread.start()

    def lint_file(self, filepath: str):
        """Requests a lint for a single file."""
        self._request_file_lint.emit(filepath)

    def lint_project(self, project_path: str):
        """Requests a lint for an entire project directory."""
        self._request_project_lint.emit(project_path)

    def shutdown(self):
        """Gracefully shuts down the linter thread."""
        if self.thread.isRunning():
            self.thread.quit()
            self.thread.wait(3000)
```

### File: `/app_core/golden_rules.py`
```py
# /app_core/golden_rules.py
import os
import json
import shutil
import re
from utils.helpers import get_base_path
from utils.logger import log

ASSETS_PATH = os.path.join(get_base_path(), "assets")
GOLDEN_RULES_PATH = os.path.join(ASSETS_PATH, "golden_rules.json")
DEFAULT_RULES_PATH = os.path.join(ASSETS_PATH, "golden_presets", "default_puffinpy_rules.json")

def _initialize_rules():
    """Ensure golden_rules.json exists, creating it from default if not."""
    if not os.path.exists(GOLDEN_RULES_PATH):
        try:
            os.makedirs(os.path.dirname(GOLDEN_RULES_PATH), exist_ok=True)
            if not os.path.exists(DEFAULT_RULES_PATH):
                log.error(f"Default golden rules preset not found at {DEFAULT_RULES_PATH}. Cannot initialize golden rules.")
                # Create an empty file to prevent repeated attempts
                with open(GOLDEN_RULES_PATH, 'w', encoding='utf-8') as f:
                    json.dump({"name": "Empty Rules", "description": "Default preset not found.", "rules": []}, f, indent=4)
                return
            shutil.copy(DEFAULT_RULES_PATH, GOLDEN_RULES_PATH)
            log.info(f"Initialized golden rules at {GOLDEN_RULES_PATH}")
        except Exception as e:
            log.error(f"Could not create initial golden rules: {e}")

def get_golden_rules() -> list[str]:
    """
    Returns a list of fundamental, non-negotiable rules for the AI.
    These rules are loaded from the editable golden_rules.json.
    """
    _initialize_rules()
    try:
        with open(GOLDEN_RULES_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get("rules", [])
    except (IOError, json.JSONDecodeError) as e:
        log.error(f"Failed to load golden rules from {GOLDEN_RULES_PATH}: {e}. Returning empty list.")
        return []

def get_golden_rules_text() -> str:
    """Returns the golden rules as a numbered text block for editing."""
    rules = get_golden_rules()
    if not rules:
        return ""
    return "\n".join(f"{i+1}. {rule}" for i, rule in enumerate(rules))

def save_golden_rules_from_text(text: str) -> bool:
    """
    Parses a numbered or un-numbered text block and saves the rules. [2, 3]
    """
    rules = []
    for line in text.strip().split('\n'):
        line = line.strip()
        if not line:
            continue
        # Regex to strip optional leading numbers and punctuation
        match = re.match(r'^\s*\d+\s*[.\-:]?\s*(.*)', line)
        if match:
            cleaned_line = match.group(1).strip()
        else:
            cleaned_line = line
        if cleaned_line:
            rules.append(cleaned_line)

    _initialize_rules() # Ensure file exists before reading
    try:
        with open(GOLDEN_RULES_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except (IOError, json.JSONDecodeError):
        data = {}
        
    data["rules"] = rules
    data.setdefault("name", "Custom Golden Rules")
    data.setdefault("description", "User-defined golden rules for AI interaction.")

    try:
        with open(GOLDEN_RULES_PATH, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4)
        log.info("Golden rules saved successfully.")
        return True
    except IOError as e:
        log.error(f"Failed to save golden rules: {e}")
        return False

def reset_golden_rules_to_default() -> bool:
    """Resets the user's golden rules to the default preset."""
    try:
        if not os.path.exists(DEFAULT_RULES_PATH):
            log.error(f"Default rules file not found at {DEFAULT_RULES_PATH}. Cannot reset.")
            return False
        shutil.copy(DEFAULT_RULES_PATH, GOLDEN_RULES_PATH)
        log.info(f"Reset golden rules at {GOLDEN_RULES_PATH} to default.")
        return True
    except Exception as e:
        log.error(f"Could not reset golden rules: {e}")
        return False
```

### File: `/app_core/github_manager.py`
```py
# PuffinPyEditor/app_core/github_manager.py
import requests
import time
import os
import json
from typing import Dict, Optional, List
from PyQt6.QtCore import QObject, QThread, pyqtSignal
from .settings_manager import settings_manager
from utils.versioning import APP_VERSION
from utils.logger import log

CLIENT_ID = "178c6fc778ccc68e1d6a"
DEVICE_CODE_URL = "https://github.com/login/device/code"
ACCESS_TOKEN_URL = "https://github.com/login/oauth/access_token"


class GitHubWorker(QObject):
    """
    Worker that runs all GitHub API requests in a background thread.
    """
    device_code_ready = pyqtSignal(dict)
    auth_successful = pyqtSignal(str)
    auth_failed = pyqtSignal(str)
    auth_polling_lapsed = pyqtSignal()
    repos_ready = pyqtSignal(list)
    branches_ready = pyqtSignal(list)
    plugin_index_ready = pyqtSignal(list)
    operation_success = pyqtSignal(str, dict)
    operation_failed = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.access_token: Optional[str] = settings_manager.get(
            "github_access_token")
        self.user_agent = f"PuffinPyEditor/{APP_VERSION}"

    def _get_headers(self) -> Dict[str, str]:
        """Constructs the standard headers for authenticated API requests."""
        return {
            "Accept": "application/vnd.github.v3+json",
            "Authorization": f"Bearer {self.access_token}",
            "User-Agent": self.user_agent
        }

    def start_device_flow(self):
        log.info("Starting GitHub device authorization flow.")
        try:
            headers = {"Accept": "application/json",
                       "User-Agent": self.user_agent}
            payload = {"client_id": CLIENT_ID, "scope": "repo user"}
            response = requests.post(
                DEVICE_CODE_URL, data=payload, headers=headers, timeout=10
            )
            response.raise_for_status()
            data = response.json()
            log.info(f"Received device code: {data.get('user_code')}")
            self.device_code_ready.emit(data)
        except requests.RequestException as e:
            log.error(f"Failed to start device flow: {e}", exc_info=True)
            self.auth_failed.emit(
                "Could not connect to GitHub. Check network and logs."
            )

    def poll_for_token(self, device_code: str, interval: int, expires_in: int):
        log.info("Polling for GitHub access token...")
        start_time = time.time()
        headers = {"Accept": "application/json", "User-Agent": self.user_agent}
        payload = {
            "client_id": CLIENT_ID,
            "device_code": device_code,
            "grant_type": "urn:ietf:params:oauth:grant-type:device_code"
        }
        while time.time() - start_time < expires_in:
            try:
                response = requests.post(
                    ACCESS_TOKEN_URL, data=payload,
                    headers=headers, timeout=interval + 2
                )
                data = response.json()
                if "access_token" in data:
                    self.access_token = data["access_token"]
                    user_info = self._get_authenticated_user_info()
                    user_login = user_info.get("login") if user_info else "user"
                    settings_manager.set(
                        "github_access_token", self.access_token, False
                    )
                    settings_manager.set("github_user", user_login, False)
                    settings_manager.set(
                        "github_user_info", user_info, False
                    )
                    settings_manager.save()
                    log.info(
                        "Successfully authenticated as GitHub user: "
                        f"{user_login}"
                    )
                    self.auth_successful.emit(user_login)
                    return
                elif data.get("error") == "authorization_pending":
                    time.sleep(interval)
                else:
                    error_desc = data.get(
                        "error_description", "Unknown authentication error"
                    )
                    log.error(f"GitHub authentication error: {error_desc}")
                    self.auth_failed.emit(error_desc)
                    return
            except requests.RequestException as e:
                log.error(f"Exception while polling for token: {e}",
                          exc_info=True)
                self.auth_failed.emit(f"Network error during auth: {e}")
                return
        log.warning("Device flow expired before user authorized.")
        self.auth_polling_lapsed.emit()

    def _get_authenticated_user_info(self) -> Optional[Dict]:
        if not self.access_token:
            return None
        try:
            response = requests.get(
                "https://api.github.com/user",
                headers=self._get_headers(), timeout=10
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            log.error(f"Failed to get user info from GitHub: {e}")
            return None

    def _paginated_request(self, url: str) -> List[Dict]:
        """Helper to handle paginated GitHub API requests."""
        all_items = []
        page = 1
        while True:
            paginated_url = f"{url}?page={page}&per_page=100"
            response = requests.get(
                paginated_url, headers=self._get_headers(), timeout=15
            )
            response.raise_for_status()
            data = response.json()
            if not data:
                break
            all_items.extend(data)
            page += 1
        return all_items

    def list_user_repos(self):
        if not self.access_token:
            self.operation_failed.emit("Not logged in to GitHub.")
            return
        try:
            # Use the paginated helper
            all_repos = self._paginated_request("https://api.github.com/user/repos")
            # Sort by most recently pushed to
            self.repos_ready.emit(sorted(all_repos, key=lambda r: r.get('pushed_at', ''), reverse=True))
        except requests.RequestException as e:
            self.operation_failed.emit(f"Failed to list repositories: {e}")

    def list_repo_branches(self, full_repo_name: str):
        if not self.access_token:
            self.operation_failed.emit("Not logged in to GitHub.")
            return
        try:
            url = f"https://api.github.com/repos/{full_repo_name}/branches"
            response = requests.get(
                url, headers=self._get_headers(), timeout=10
            )
            response.raise_for_status()
            self.branches_ready.emit(response.json())
        except requests.RequestException as e:
            self.operation_failed.emit(
                f"Failed to list branches for {full_repo_name}: {e}")

    def create_github_release(self, owner: str, repo: str, tag_name: str,
                              name: str, body: str, prerelease: bool):
        if not self.access_token:
            self.operation_failed.emit("Not logged in to GitHub.")
            return
        url = f"https://api.github.com/repos/{owner}/{repo}/releases"
        payload = {"tag_name": tag_name, "name": name, "body": body,
                   "prerelease": prerelease}
        try:
            response = requests.post(
                url, headers=self._get_headers(), json=payload, timeout=20
            )
            response.raise_for_status()
            self.operation_success.emit(
                "Release created", {"release_data": response.json()}
            )
        except requests.exceptions.HTTPError as e:
            msg = f"HTTP {e.response.status_code}: "
            try:
                error_body = e.response.json()
                errs = error_body.get('errors', [])
                if any(err.get('code') == 'already_exists' for err in errs):
                    msg += f"A release for tag '{tag_name}' already exists."
                else:
                    msg += error_body.get(
                        'message', 'Failed to create release.'
                    )
            except json.JSONDecodeError:
                msg += "Failed to create GitHub release."
            self.operation_failed.emit(msg)
        except requests.RequestException as e:
            self.operation_failed.emit(f"Failed to create GitHub release: {e}")

    def upload_release_asset(self, upload_url: str, asset_path: str):
        if not self.access_token:
            self.operation_failed.emit("Not logged in to GitHub.")
            return
        upload_url = upload_url.split('{')[0]
        asset_name = os.path.basename(asset_path)
        headers = self._get_headers()
        headers['Content-Type'] = 'application/octet-stream'
        try:
            with open(asset_path, 'rb') as f:
                data = f.read()
            response = requests.post(
                f"{upload_url}?name={asset_name}",
                headers=headers, data=data, timeout=300
            )
            response.raise_for_status()
            self.operation_success.emit(
                "Asset uploaded", {"asset_data": response.json()}
            )
        except (requests.RequestException, IOError) as e:
            self.operation_failed.emit(f"Failed to upload asset: {e}")

    def delete_release(self, owner: str, repo: str, release_id: int):
        if not self.access_token:
            self.operation_failed.emit("Not logged in to GitHub.")
            return
        url = (f"https://api.github.com/repos/{owner}/{repo}/releases/"
               f"{release_id}")
        log.info(f"ROLLBACK: Attempting to delete release at {url}")
        try:
            response = requests.delete(
                url, headers=self._get_headers(), timeout=20
            )
            response.raise_for_status()
            self.operation_success.emit(
                "Release deleted", {"release_id": release_id}
            )
        except requests.RequestException as e:
            msg = f"Failed to delete release: {e}"
            if hasattr(e, 'response') and e.response:
                msg += f" (Status: {e.response.status_code})"
            self.operation_failed.emit(msg)

    def create_repo(self, name: str, description: str, is_private: bool):
        if not self.access_token:
            self.operation_failed.emit("Not logged in to GitHub.")
            return
        api_url = "https://api.github.com/user/repos"
        payload = {"name": name, "description": description,
                   "private": is_private}
        try:
            response = requests.post(
                api_url, headers=self._get_headers(), json=payload, timeout=15
            )
            response.raise_for_status()
            self.operation_success.emit(
                f"Repository '{name}' created.", response.json()
            )
        except requests.RequestException as e:
            error_msg = e.response.json().get('message', str(e)) if hasattr(e, 'response') and e.response else str(e)
            self.operation_failed.emit(
                f"Failed to create repository: {error_msg}")

    def fetch_plugin_index(self, repo_path: str):
        url = f"https://raw.githubusercontent.com/{repo_path}/main/index.json"
        log.info(f"Fetching plugin index from: {url}")
        try:
            response = requests.get(url, timeout=15)
            response.raise_for_status()
            self.plugin_index_ready.emit(response.json())
        except requests.RequestException as e:
            self.operation_failed.emit(f"Failed to fetch plugin index: {e}")
        except json.JSONDecodeError:
            self.operation_failed.emit(
                "Invalid plugin index format (not valid JSON).")

    def update_repo_visibility(self, owner: str, repo: str, is_private: bool):
        if not self.access_token:
            self.operation_failed.emit("Not logged in to GitHub.")
            return
        api_url = f"https://api.github.com/repos/{owner}/{repo}"
        payload = {"private": is_private}
        try:
            response = requests.patch(
                api_url, headers=self._get_headers(), json=payload, timeout=15
            )
            response.raise_for_status()
            visibility = "private" if is_private else "public"
            self.operation_success.emit(
                f"Repository visibility changed to {visibility}.",
                response.json()
            )
        except requests.RequestException as e:
            error_msg = e.response.json().get('message', str(e)) if hasattr(e, 'response') and e.response else str(e)
            self.operation_failed.emit(
                f"Failed to change visibility: {error_msg}")

    def list_repo_tags(self, owner: str, repo: str) -> List[Dict]:
        """Fetches all tags for a repository."""
        url = f"https://api.github.com/repos/{owner}/{repo}/tags"
        return self._paginated_request(url)

    def list_repo_releases(self, owner: str, repo: str) -> List[Dict]:
        """Fetches all releases for a repository."""
        url = f"https://api.github.com/repos/{owner}/{repo}/releases"
        return self._paginated_request(url)

    def delete_remote_tag_ref(self, owner: str, repo: str, tag: str) -> bool:
        """Deletes a tag reference from the remote repository."""
        url = f"https://api.github.com/repos/{owner}/{repo}/git/refs/tags/{tag}"
        try:
            response = requests.delete(url, headers=self._get_headers(), timeout=10)
            response.raise_for_status()
            log.info(f"Successfully deleted remote tag ref: {tag}")
            return True
        except requests.RequestException as e:
            log.error(f"Failed to delete tag '{tag}': {e}")
            return False

    def cleanup_orphaned_tags(self, owner: str, repo: str):
        """Finds and deletes tags that are not associated with any release."""
        if not self.access_token:
            self.operation_failed.emit("Not logged in to GitHub.")
            return

        try:
            log.info(f"Starting orphaned tag cleanup for {owner}/{repo}")
            all_tags_data = self.list_repo_tags(owner, repo)
            all_releases_data = self.list_repo_releases(owner, repo)

            all_tag_names = {tag['name'] for tag in all_tags_data}
            release_tag_names = {rel['tag_name'] for rel in all_releases_data}

            orphaned_tags = all_tag_names - release_tag_names
            log.info(f"Found {len(orphaned_tags)} orphaned tags: {orphaned_tags}")

            if not orphaned_tags:
                self.operation_success.emit("No orphaned tags found to clean up.", {})
                return

            deleted_tags, failed_tags = [], []
            for tag in orphaned_tags:
                if self.delete_remote_tag_ref(owner, repo, tag):
                    deleted_tags.append(tag)
                else:
                    failed_tags.append(tag)

            summary_lines = []
            if deleted_tags:
                summary_lines.append(f"Successfully deleted {len(deleted_tags)} orphaned tags: {', '.join(deleted_tags)}")
            if failed_tags:
                summary_lines.append(f"Failed to delete {len(failed_tags)} tags: {', '.join(failed_tags)}")

            final_message = "\n".join(summary_lines)
            if failed_tags:
                self.operation_failed.emit(final_message)
            else:
                self.operation_success.emit(final_message, {"deleted_tags": deleted_tags})

        except requests.RequestException as e:
            self.operation_failed.emit(f"Failed to fetch repo data for cleanup: {e}")
        except Exception as e:
            log.error(f"Unexpected error during tag cleanup: {e}", exc_info=True)
            self.operation_failed.emit("An unexpected error occurred during cleanup.")


class GitHubManager(QObject):
    """
    Manages all interaction with the GitHub API by delegating to a background
    worker thread.
    """
    device_code_ready = pyqtSignal(dict)
    auth_successful = pyqtSignal(str)
    auth_failed = pyqtSignal(str)
    auth_polling_lapsed = pyqtSignal()
    repos_ready = pyqtSignal(list)
    branches_ready = pyqtSignal(list)
    plugin_index_ready = pyqtSignal(list)
    operation_success = pyqtSignal(str, dict)
    operation_failed = pyqtSignal(str)

    _start_device_flow = pyqtSignal()
    _poll_for_token = pyqtSignal(str, int, int)
    _request_repos = pyqtSignal()
    _request_branches = pyqtSignal(str)
    _request_create_repo = pyqtSignal(str, str, bool)
    _request_create_release = pyqtSignal(str, str, str, str, str, bool)
    _request_upload_asset = pyqtSignal(str, str)
    _request_update_visibility = pyqtSignal(str, str, bool)
    _request_plugin_index = pyqtSignal(str)
    _request_delete_release = pyqtSignal(str, str, int)
    _request_cleanup_tags = pyqtSignal(str, str)

    def __init__(self, parent: Optional[QObject] = None):
        super().__init__(parent)
        self.thread = QThread()
        self.worker = GitHubWorker()
        self.worker.moveToThread(self.thread)
        self.user_info = settings_manager.get("github_user_info")
        log.info(f"Loaded stored GitHub user info on startup: "
                 f"{bool(self.user_info)}")

        self._start_device_flow.connect(self.worker.start_device_flow)
        self._poll_for_token.connect(self.worker.poll_for_token)
        self._request_repos.connect(self.worker.list_user_repos)
        self._request_branches.connect(self.worker.list_repo_branches)
        self._request_create_repo.connect(self.worker.create_repo)
        self._request_create_release.connect(self.worker.create_github_release)
        self._request_upload_asset.connect(self.worker.upload_release_asset)
        self._request_update_visibility.connect(
            self.worker.update_repo_visibility)
        self._request_plugin_index.connect(self.worker.fetch_plugin_index)
        self._request_delete_release.connect(self.worker.delete_release)
        self._request_cleanup_tags.connect(self.worker.cleanup_orphaned_tags)

        self.worker.device_code_ready.connect(self.device_code_ready)
        self.worker.auth_successful.connect(self._on_auth_successful)
        self.worker.auth_failed.connect(self.auth_failed)
        self.worker.auth_polling_lapsed.connect(self.auth_polling_lapsed)
        self.worker.repos_ready.connect(self.repos_ready)
        self.worker.branches_ready.connect(self.branches_ready)
        self.worker.plugin_index_ready.connect(self.plugin_index_ready)
        self.worker.operation_success.connect(self.operation_success)
        self.worker.operation_failed.connect(self.operation_failed)

        self.thread.start()

    def _on_auth_successful(self, username: str):
        self.user_info = settings_manager.get("github_user_info")
        log.info(
            f"Authentication successful. Loaded user info for {username}.")
        self.auth_successful.emit(username)

    def get_authenticated_user(self) -> Optional[str]:
        return settings_manager.get("github_user")

    def get_user_info(self) -> Optional[Dict]:
        return self.user_info

    def get_active_repo_config(self) -> Optional[Dict]:
        """
        Retrieves the configuration dictionary for the repo marked as active.
        This is the single source of truth for the project's main repository.

        Returns:
            A dictionary with 'owner' and 'repo' keys, or None if not set.
        """
        active_repo_id = settings_manager.get("active_update_repo_id")
        if not active_repo_id:
            return None

        all_repos = settings_manager.get("source_control_repos", [])
        active_repo_config = next(
            (r for r in all_repos if r.get("id") == active_repo_id), None
        )
        return active_repo_config

    def start_device_flow(self):
        self._start_device_flow.emit()

    def poll_for_token(self, device_code: str, interval: int, expires_in: int):
        self._poll_for_token.emit(device_code, interval, expires_in)

    def logout(self):
        settings_manager.set("github_access_token", None, False)
        settings_manager.set("github_user", None, False)
        settings_manager.set("github_user_info", None, False)
        settings_manager.save()
        self.worker.access_token = None
        self.user_info = None
        log.info("Logged out of GitHub and cleared session data.")

    def list_repos(self):
        self._request_repos.emit()

    def list_branches(self, full_repo_name: str):
        self._request_branches.emit(full_repo_name)

    def create_repo(self, name: str, description: str, is_private: bool):
        self._request_create_repo.emit(name, description, is_private)

    def create_github_release(self, owner: str, repo: str, tag_name: str,
                              name: str, body: str, prerelease: bool):
        self._request_create_release.emit(
            owner, repo, tag_name, name, body, prerelease
        )

    def upload_asset(self, upload_url: str, asset_path: str):
        self._request_upload_asset.emit(upload_url, asset_path)

    def delete_release(self, owner: str, repo: str, release_id: int):
        self._request_delete_release.emit(owner, repo, release_id)

    def update_repo_visibility(self, owner: str, repo: str, is_private: bool):
        self._request_update_visibility.emit(owner, repo, is_private)

    def fetch_plugin_index(self, repo_path: str):
        self._request_plugin_index.emit(repo_path)
        
    def cleanup_orphaned_tags(self, owner: str, repo: str):
        """Requests a cleanup of orphaned tags for the specified repository."""
        self._request_cleanup_tags.emit(owner, repo)

    def shutdown(self):
        if self.thread and self.thread.isRunning():
            log.info("Shutting down GitHubManager thread.")
            self.thread.quit()
            if not self.thread.wait(3000):
                log.warning(
                    "GitHubManager thread did not shut down "
                    "gracefully. Terminating."
                )
                self.thread.terminate()
```

### File: `/app_core/file_handler.py`
```py
# PuffinPyEditor/app_core/file_handler.py
import os
import sys
import shutil
import subprocess
import re
from typing import Optional, Tuple, Any, Dict, List
from PyQt6.QtWidgets import (QFileDialog, QMessageBox, QComboBox, QLabel, QDialogButtonBox, QGridLayout,
                             QProgressDialog)
from PyQt6.QtGui import QGuiApplication, QDesktopServices
from PyQt6.QtCore import QUrl, pyqtSignal, QObject, Qt, QRunnable, QThreadPool

from .settings_manager import settings_manager
from utils.logger import log
from utils.helpers import clean_git_conflict_markers

# --- NEW: Background Worker for BOM Removal ---
class BOMWorkerSignals(QObject):
    """Defines signals available from a running BOMRemovalWorker."""
    progress = pyqtSignal(str)
    finished = pyqtSignal(int, int, list) # processed_count, fixed_count, errors

class BOMRemovalWorker(QRunnable):
    """
    A QRunnable worker that recursively finds and removes UTF-8 BOMs from text files.
    """
    TEXT_EXTENSIONS = {'.txt', '.py', '.md', '.json', '.html', '.css', '.js', '.xml', '.yml', '.yaml', '.toml', '.ini', '.cfg', '.h', '.hpp', '.c', '.cpp', '.cs', '.java', '.rs', '.go'}

    def __init__(self, path: str):
        super().__init__()
        self.path = path
        self.signals = BOMWorkerSignals()
        self.is_cancelled = False

    def run(self):
        processed = 0
        fixed = 0
        errors = []

        try:
            if os.path.isfile(self.path):
                # Handle a single file
                processed, fixed = self._process_file(self.path)
            elif os.path.isdir(self.path):
                # Handle a directory
                for root, _, files in os.walk(self.path):
                    if self.is_cancelled: break
                    for filename in files:
                        if self.is_cancelled: break
                        # Check if file type is likely to be text
                        if os.path.splitext(filename)[1].lower() in self.TEXT_EXTENSIONS:
                            filepath = os.path.join(root, filename)
                            p, f = self._process_file(filepath)
                            processed += p
                            fixed += f
            else:
                errors.append(f"Path is not a valid file or directory: {self.path}")
        except Exception as e:
            errors.append(f"An unexpected error occurred: {e}")
            log.error(f"Error during BOM removal: {e}", exc_info=True)
        
        self.signals.finished.emit(processed, fixed, errors)

    def _process_file(self, filepath: str) -> Tuple[int, int]:
        """Checks and fixes a single file for a BOM. Returns (processed, fixed) count."""
        self.signals.progress.emit(os.path.basename(filepath))
        try:
            with open(filepath, 'rb') as f:
                bom = f.read(3)
            
            if bom == b'\xef\xbb\xbf':
                with open(filepath, 'rb') as f:
                    content = f.read()
                with open(filepath, 'wb') as f:
                    f.write(content[3:])
                return 1, 1 # Processed 1, fixed 1
            else:
                return 1, 0 # Processed 1, fixed 0
        except (IOError, OSError):
            # Probably a binary file or permission error, just skip it
            return 1, 0

    def cancel(self):
        self.is_cancelled = True

class SaveAsDialog(QFileDialog):
    """A custom file dialog that includes an encoding selector."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Save File As")
        self.setAcceptMode(QFileDialog.AcceptMode.AcceptSave)
        # Using a non-native dialog is necessary to add custom widgets.
        self.setOption(QFileDialog.Option.DontUseNativeDialog, True)

        self.encoding_map = {
            "UTF-8": "utf-8",
            "UTF-8 with BOM": "utf-8-sig",
            "UTF-16 LE": "utf-16le",
            "UTF-16 BE": "utf-16be",
            "Latin-1 (ISO-8859-1)": "latin-1",
            "Windows-1252": "cp1252"
        }
        
        self.encoding_combo = QComboBox()
        self.encoding_combo.addItems(self.encoding_map.keys())

        # Add the encoding combobox to the dialog's layout
        layout = self.layout()
        if isinstance(layout, QGridLayout):
            # Find the row of the button box to insert our widget above it
            button_box = self.findChild(QDialogButtonBox)
            if button_box:
                row, _, _, _ = layout.getItemPosition(layout.indexOf(button_box))
                # Add our new widgets in the row just above the buttons
                layout.addWidget(QLabel("Encoding:"), row - 1, 0, 1, 1, Qt.AlignmentFlag.AlignRight)
                layout.addWidget(self.encoding_combo, row - 1, 1, 1, 2)

    def get_selected_encoding(self) -> str:
        selected_text = self.encoding_combo.currentText()
        return self.encoding_map.get(selected_text, "utf-8")


class FileHandler(QObject):
    item_created = pyqtSignal(str, str)
    item_renamed = pyqtSignal(str, str, str)
    item_deleted = pyqtSignal(str, str)
    recent_files_changed = pyqtSignal()
    # A list of common encodings to try when opening a file
    COMMON_ENCODINGS = ['utf-8', 'utf-8-sig', 'utf-16', 'latin-1', 'cp1252']
    
    def __init__(self, parent_window: Optional[Any] = None):
        super().__init__()
        self.parent_window = parent_window
        self.threadpool = QThreadPool()
        self.bom_worker = None
        self.progress_dialog = None
        self._internal_clipboard: Dict[str, Optional[str]] = { "operation": None, "path": None }

    def _read_with_encoding_detection(self, filepath: str) -> Tuple[Optional[str], Optional[str]]:
        """Tries to read a file with several common encodings."""
        for encoding in self.COMMON_ENCODINGS:
            try:
                with open(filepath, 'r', encoding=encoding) as f:
                    content = f.read()
                log.info(f"Successfully read file {filepath} with encoding {encoding}")
                return content, encoding
            except (UnicodeDecodeError, TypeError):
                continue
        
        # As a last resort, try to read with 'ignore' errors
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            log.warning(f"Read file {filepath} with UTF-8, ignoring errors. Some characters may be lost.")
            return content, 'utf-8' # Treat as utf-8 but it's lossy
        except Exception:
            return None, None

    def new_file(self) -> Dict[str, Optional[str]]:
        log.info("FileHandler: new_file action invoked.")
        return { "content": "", "filepath": None, "new_file_default_name": "Untitled", "encoding": "utf-8" }

    def open_file_dialog(self) -> Tuple[Optional[str], Optional[str], Optional[str], Optional[str]]:
        last_dir = settings_manager.get("last_opened_directory", os.path.expanduser("~"))
        filepath, _ = QFileDialog.getOpenFileName(self.parent_window, "Open File", last_dir, "All Supported Files (*.py *.pyw *.txt *.md *.json *.js *.html *.css *.c *.cpp *.h *.hpp *.cs *.rs);;All Files (*)")
        if not filepath: return None, None, None, None
        settings_manager.set("last_opened_directory", os.path.dirname(filepath))
        try:
            original_content, detected_encoding = self._read_with_encoding_detection(filepath)
            if original_content is None:
                raise IOError("Could not decode the file with any of the supported encodings.")

            # Automatically clean git conflict markers when opening a file.
            content = clean_git_conflict_markers(original_content)
            if content != original_content:
                log.info(f"Cleaned git conflict markers from {filepath} on load.")
                # Ask user if they want to save the cleaned file
                reply = QMessageBox.question(
                    self.parent_window,
                    "Conflict Markers Removed",
                    f"Git conflict markers were found and removed from '{os.path.basename(filepath)}'.\n\n"
                    "Do you want to save these changes back to the file immediately?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                    QMessageBox.StandardButton.Yes
                )
                if reply == QMessageBox.StandardButton.Yes:
                    with open(filepath, 'w', encoding=detected_encoding) as f:
                        f.write(content)
                    log.info(f"Saved automatically cleaned file: {filepath}")

            self._add_to_recent_files(filepath)
            return filepath, content, detected_encoding, None
        except (IOError, OSError) as e:
            msg = (f"Error opening file '{os.path.basename(filepath)}'.\n\nReason: {e}")
            log.error(msg, exc_info=True); return None, None, None, msg

    def save_file_content(self, filepath: Optional[str], content: str, save_as: bool = False, encoding: str = 'utf-8') -> Tuple[Optional[str], Optional[str]]:
        dir_exists = filepath and os.path.exists(os.path.dirname(filepath))
        final_encoding = encoding

        if save_as or not filepath or not dir_exists:
            last_dir = os.path.dirname(filepath) if dir_exists else settings_manager.get("last_saved_directory", os.path.expanduser("~"))
            sugg_name = os.path.basename(filepath) if filepath else "Untitled.py"

            dialog = SaveAsDialog(self.parent_window)
            dialog.setDirectory(last_dir)
            dialog.selectFile(sugg_name)
            
            # Setup proper file type filters
            filters = [
                "Python Files (*.py *.pyw)",
                "Text Files (*.txt)",
                "Markdown Files (*.md)",
                "JSON Files (*.json)",
                "JavaScript Files (*.js)",
                "HTML Files (*.html *.htm)",
                "CSS Files (*.css)",
                "C++ Source Files (*.cpp *.cxx *.cc)",
                "C/C++ Header Files (*.h *.hpp)",
                "C# Source Files (*.cs)",
                "Rust Source Files (*.rs)",
                "All Files (*)"
            ]
            dialog.setNameFilters(filters)

            if dialog.exec():
                path_from_dialog = dialog.selectedFiles()[0]
                final_encoding = dialog.get_selected_encoding()
            else:
                return None, None # User cancelled

            filepath = path_from_dialog
            settings_manager.set("last_saved_directory", os.path.dirname(filepath))
        
        try:
            # --- ATOMIC SAVE IMPLEMENTATION ---
            # 1. Write to a temporary file in the same directory.
            temp_file = filepath + ".puffin-save.tmp"
            with open(temp_file, 'w', encoding=final_encoding) as f:
                f.write(content)

            # 2. Atomically replace the original file with the new one.
            # This is much safer than a direct overwrite.
            os.replace(temp_file, filepath)
            
            log.info(f"Atomically saved file '{filepath}' with encoding '{final_encoding}'.")
            return filepath, final_encoding
        except (IOError, OSError, UnicodeEncodeError) as e:
            msg = f"Error saving file '{filepath}' with encoding '{final_encoding}': {e}"
            log.error(msg, exc_info=True)
            QMessageBox.critical(self.parent_window, "Error Saving File", msg)
            # Clean up the temporary file if the final replace fails
            if os.path.exists(temp_file):
                os.remove(temp_file)
            return None, None
            
    def remove_boms_in_path(self, path: str):
        """Public method to start the BOM removal process."""
        reply = QMessageBox.question(
            self.parent_window,
            "Confirm BOM Removal",
            "This will scan for and remove the UTF-8 Byte Order Mark (BOM) from the beginning of text files.\n\n"
            "This action modifies files in place. Are you sure you want to continue?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.Cancel,
            QMessageBox.StandardButton.Yes
        )
        if reply == QMessageBox.StandardButton.Cancel:
            return

        self.progress_dialog = QProgressDialog("Scanning for BOMs...", "Cancel", 0, 100, self.parent_window)
        self.progress_dialog.setWindowModality(Qt.WindowModality.WindowModal)
        self.progress_dialog.setWindowTitle("Removing BOMs")
        self.progress_dialog.setValue(0)
        self.progress_dialog.setAutoClose(False)

        self.bom_worker = BOMRemovalWorker(path)
        self.bom_worker.signals.progress.connect(self._on_bom_progress_update)
        self.bom_worker.signals.finished.connect(self._on_bom_finished)
        self.progress_dialog.canceled.connect(self.bom_worker.cancel)

        self.threadpool.start(self.bom_worker)

    def _on_bom_progress_update(self, filename: str):
        if self.progress_dialog:
            self.progress_dialog.setLabelText(f"Checking: {filename}")

    def _on_bom_finished(self, processed_count: int, fixed_count: int, errors: List[str]):
        if self.progress_dialog:
            self.progress_dialog.close()

        summary_message = (
            f"BOM removal process complete.\n\n"
            f"- Files scanned: {processed_count}\n"
            f"- Files fixed: {fixed_count}"
        )
        if errors:
            summary_message += f"\n\nEncountered {len(errors)} error(s):\n" + "\n".join(errors[:3])
            if len(errors) > 3:
                summary_message += "\n... (see log for more details)"
        
        QMessageBox.information(self.parent_window, "BOM Removal Complete", summary_message)
        # Refresh the file explorer to reflect any changes
        if self.parent_window.explorer_panel:
            self.parent_window.explorer_panel.refresh()

    def create_file(self, path: str) -> Tuple[bool, Optional[str]]:
        try:
            if os.path.exists(path): item_type = "folder" if os.path.isdir(path) else "file"; return False, f"A {item_type} named '{os.path.basename(path)}' already exists."
            with open(path, 'w', encoding='utf-8'): pass
            log.info(f"Created file: {path}"); self.item_created.emit("file", path); return True, None
        except OSError as e: log.error(f"Failed to create file at {path}: {e}", exc_info=True); return False, f"Failed to create file: {e}"

    def create_folder(self, path: str) -> Tuple[bool, Optional[str]]:
        try:
            if os.path.exists(path): item_type = "folder" if os.path.isdir(path) else "file"; return False, f"A {item_type} named '{os.path.basename(path)}' already exists."
            os.makedirs(path); log.info(f"Created folder: {path}"); self.item_created.emit("folder", path); return True, None
        except OSError as e: log.error(f"Failed to create folder at {path}: {e}", exc_info=True); return False, f"Failed to create folder: {e}"

    def rename_item(self, old_path: str, new_name: str) -> Tuple[bool, str]:
        """Renames a file or folder, handling case-sensitivity issues."""
        new_name = new_name.strip()
        if not new_name:
            return False, "Name cannot be empty."

        if re.search(r'[<>:"/\\|?*]', new_name):
            return False, 'Name contains illegal characters (e.g., \\ / : * ? " < > |).'
        
        new_path = os.path.join(os.path.dirname(old_path), new_name)

        # Case-sensitive check
        if old_path.lower() == new_path.lower() and old_path != new_path:
            # This is a case-only rename on a potentially case-insensitive filesystem.
            # Perform a safe two-step rename.
            temp_path = old_path + '.puffin_rename_temp'
            try:
                os.rename(old_path, temp_path)
                os.rename(temp_path, new_path)
                item_type = 'folder' if os.path.isdir(new_path) else 'file'
                self.item_renamed.emit(item_type, old_path, new_path)
                return True, new_path
            except OSError as e:
                log.error(f"Failed to perform case-rename on '{old_path}': {e}", exc_info=True)
                # If it failed, try to rename back
                if os.path.exists(temp_path):
                    os.rename(temp_path, old_path)
                return False, f"Failed to rename: {e}"

        # Standard check for existing file
        if os.path.exists(new_path):
            return False, f"'{new_name}' already exists in this location."

        try:
            item_type = 'folder' if os.path.isdir(old_path) else 'file'
            os.rename(old_path, new_path)
            log.info(f"Renamed '{old_path}' to '{new_path}'")
            self.item_renamed.emit(item_type, old_path, new_path)
            return True, new_path
        except OSError as e:
            log.error(f"Failed to rename '{old_path}': {e}", exc_info=True)
            return False, f"Failed to rename: {e}"

    def delete_item(self, path):
        item_type = 'file' if os.path.isfile(path) else 'folder'
        try:
            if os.path.isfile(path): os.remove(path)
            elif os.path.isdir(path): shutil.rmtree(path)
            log.info(f"Deleted item: {path}"); self.item_deleted.emit(item_type, path); return True, None
        except (OSError, shutil.Error) as e: log.error(f"Failed to delete '{path}': {e}", exc_info=True); return False, f"Failed to delete: {e}"

    def copy_path_to_clipboard(self, path):
        try:
            QGuiApplication.clipboard().setText(os.path.normpath(path)); log.info(f"Copied path to clipboard: {path}")
            if self.parent_window and hasattr(self.parent_window, "statusBar"): self.parent_window.statusBar().showMessage("Path copied to clipboard", 2000)
        except Exception as e: log.error(f"Could not copy path to clipboard: {e}")

    def reveal_in_explorer(self, path):
        path_to_show = os.path.normpath(path)
        try:
            if sys.platform == 'win32': subprocess.run(['explorer', '/select,', path_to_show] if not os.path.isdir(path_to_show) else ['explorer', path_to_show])
            elif sys.platform == 'darwin': subprocess.run(['open', path_to_show] if os.path.isdir(path_to_show) else ['open', '-R', path_to_show])
            else: subprocess.run(['xdg-open', path_to_show if os.path.isdir(path_to_show) else os.path.dirname(path_to_show)])
        except Exception as e: log.error(f"Could not open file browser for path '{path}': {e}"); QMessageBox.warning(self.parent_window, "Error", f"Could not open file browser: {e}")

    def open_with_default_app(self, path):
        try: QDesktopServices.openUrl(QUrl.fromLocalFile(path))
        except Exception as e: log.error(f"Failed to open '{path}' with default app: {e}"); QMessageBox.warning(self.parent_window, "Error", f"Could not open file with default application: {e}")

    def duplicate_item(self, path):
        dir_name, (base_name, ext) = os.path.dirname(path), os.path.splitext(os.path.basename(path))
        counter = 1; new_path = os.path.join(dir_name, f"{base_name}_copy{ext}")
        while os.path.exists(new_path): counter += 1; new_path = os.path.join(dir_name, f"{base_name}_copy_{counter}{ext}")
        try:
            item_type = "folder";
            if os.path.isfile(path): shutil.copy2(path, new_path); item_type = "file"
            elif os.path.isdir(path): shutil.copytree(path, new_path)
            log.info(f"Duplicated '{path}' to '{new_path}'"); self.item_created.emit(item_type, new_path); return True, None
        except (OSError, shutil.Error) as e: log.error(f"Failed to duplicate '{path}': {e}", exc_info=True); return False, f"Failed to duplicate: {e}"

    def cut_item(self, path): self._internal_clipboard = {"operation": "cut", "path": path}
    def copy_item(self, path): self._internal_clipboard = {"operation": "copy", "path": path}
    def paste_item(self, dest_dir):
        op, src_path = self._internal_clipboard.get("operation"), self._internal_clipboard.get("path")
        if not op or not src_path or not os.path.exists(src_path): return False, "Nothing to paste."
        if not os.path.isdir(dest_dir): return False, "Paste destination must be a folder."
        dest_path = os.path.join(dest_dir, os.path.basename(src_path))
        if os.path.exists(dest_path): return False, f"'{os.path.basename(dest_path)}' already exists in the destination."
        try:
            item_type = 'folder' if os.path.isdir(src_path) else 'file'
            if op == "cut":
                shutil.move(src_path, dest_path); log.info(f"Moved '{src_path}' to '{dest_path}'")
                self.item_renamed.emit(item_type, src_path, dest_path); self._internal_clipboard = {"operation": None, "path": None}
            elif op == "copy":
                shutil.copytree(src_path, dest_path) if os.path.isdir(src_path) else shutil.copy2(src_path, dest_path)
                log.info(f"Copied '{src_path}' to '{dest_path}'"); self.item_created.emit(item_type, dest_path)
            return True, None
        except (OSError, shutil.Error) as e: log.error(f"Paste operation failed: {e}", exc_info=True); return False, f"Paste operation failed: {e}"

    def move_item(self, src_path, dest_dir):
        if not os.path.exists(src_path): return False, "Source path does not exist."
        if not os.path.isdir(dest_dir): return False, "Destination must be a folder."
        dest_path = os.path.join(dest_dir, os.path.basename(src_path))
        if os.path.normpath(src_path) == os.path.normpath(dest_path): return True, dest_path
        if os.path.exists(dest_path): return False, f"'{os.path.basename(src_path)}' already exists in the destination."
        if os.path.isdir(src_path) and os.path.normpath(dest_dir).startswith(os.path.normpath(src_path)): return False, "Cannot move a folder into its own subdirectory."
        try: item_type = 'folder' if os.path.isdir(src_path) else 'file'; shutil.move(src_path, dest_path); log.info(f"Moved '{src_path}' to '{dest_path}'"); self.item_renamed.emit(item_type, src_path, dest_path); return True, dest_path
        except (OSError, shutil.Error) as e: log.error(f"Move operation failed: {e}", exc_info=True); return False, f"Move operation failed: {e}"

    def copy_item_to_dest(self, src_path: str, dest_dir: str) -> Tuple[bool, Optional[str]]:
        """Copies a file or folder to a destination directory."""
        if not os.path.exists(src_path):
            return False, "Source path does not exist."
        if not os.path.isdir(dest_dir):
            return False, "Destination must be a folder."

        dest_path = os.path.join(dest_dir, os.path.basename(src_path))
        if os.path.exists(dest_path):
            return False, f"'{os.path.basename(src_path)}' already exists in the destination."

        try:
            item_type = 'folder' if os.path.isdir(src_path) else 'file'
            if item_type == 'folder':
                shutil.copytree(src_path, dest_path)
            else:  # it's a file
                shutil.copy2(src_path, dest_path)

            log.info(f"Copied '{src_path}' to '{dest_path}'")
            self.item_created.emit(item_type, dest_path)
            return True, dest_path
        except (OSError, shutil.Error) as e:
            log.error(f"Copy operation failed: {e}", exc_info=True)
            return False, f"Copy operation failed: {e}"

    def get_clipboard_status(self): return self._internal_clipboard.get("operation")
    def _add_to_recent_files(self, filepath):
        if not filepath: return
        recents = settings_manager.get("recent_files", []);
        if filepath in recents: recents.remove(filepath)
        recents.insert(0, filepath); max_files = settings_manager.get("max_recent_files", 10)
        settings_manager.set("recent_files", recents[:max_files]); self.recent_files_changed.emit()
```

### File: `/app_core/completion_manager.py`
```py
# PuffinPyEditor/app_core/completion_manager.py
import os
import sys
import shutil
import html
from typing import Any, Optional, TYPE_CHECKING
from PyQt6.QtCore import QObject, QThread, pyqtSignal
import jedi
from .settings_manager import settings_manager
from utils.logger import log

# Use this for type hinting to avoid circular dependencies if they ever arise
if TYPE_CHECKING:
    from .theme_manager import ThemeManager


def find_python_interpreter_for_jedi() -> str:
    """
    Intelligently finds the best Python executable for Jedi to use.
    This prevents Jedi from trying to execute the bundled GUI app.

    The priority is:
    1. User-defined path in settings.
    2. A 'python.exe' bundled alongside the main PuffinPyEditor.exe (frozen).
    3. The python.exe from the current venv (if running from source).
    4. The first 'python' found on the system's PATH.

    Returns:
        The path to a suitable Python executable, or an empty string.
    """
    # 1. Prioritize user-defined path from settings
    user_path = settings_manager.get("python_interpreter_path")
    if (user_path and
            os.path.exists(user_path) and
            "PuffinPyEditor.exe" not in user_path):
        log.info(f"Jedi: Using user-defined interpreter: {user_path}")
        return user_path

    # 2. If the application is frozen (bundled with PyInstaller)
    if getattr(sys, 'frozen', False):
        # Look for 'python.exe' in the same directory as our main executable.
        frozen_dir = os.path.dirname(sys.executable)
        local_python_path = os.path.join(frozen_dir, "python.exe")
        if os.path.exists(local_python_path):
            log.info(
                "Jedi: Found local python.exe in frozen app dir: "
                f"{local_python_path}"
            )
            return local_python_path

    # 3. When running from source, sys.executable is the venv python.
    # When frozen, sys.executable is PuffinPyEditor.exe, which we must avoid.
    if not getattr(sys, 'frozen', False):
        if "PuffinPyEditor.exe" not in sys.executable:
            log.info(
                "Jedi: Running from source, using sys.executable: "
                f"{sys.executable}"
            )
            return sys.executable

    # 4. As a last resort, search the system's PATH.
    system_python = shutil.which("python")
    if system_python and "PuffinPyEditor.exe" not in system_python:
        log.warning(
            "Jedi: Falling back to system python on PATH: "
            f"{system_python}"
        )
        return system_python

    # 5. If no suitable python is found, return empty string.
    log.error("Jedi: Could not find a suitable Python interpreter.")
    return ""


class JediWorker(QObject):
    """
    Worker that runs Jedi operations in a separate thread.
    """
    completions_ready = pyqtSignal(list)
    definition_ready = pyqtSignal(str, int, int)
    signature_ready = pyqtSignal(object)

    def __init__(self):
        super().__init__()
        self.project: Optional[jedi.Project] = None

    def set_project(self, project_path: str):
        """Initializes the Jedi project environment."""
        try:
            python_executable = find_python_interpreter_for_jedi()
            if not python_executable:
                log.error(
                    "JediWorker could not be initialized: No valid "
                    "Python interpreter found."
                )
                self.project = None
                return

            if project_path and os.path.isdir(project_path):
                self.project = jedi.Project(
                    path=project_path,
                    environment_path=python_executable
                )
                log.info(
                    f"Jedi context set to project: {project_path} with "
                    f"interpreter: {python_executable}"
                )
            else:
                # Fallback to a default project if no path is given
                env = jedi.create_environment(python_executable, safe=False)
                self.project = jedi.Project(
                    os.path.expanduser("~"), environment=env
                )
                log.info(
                    "Jedi context set to default environment with "
                    f"interpreter: {python_executable}"
                )

        except Exception as e:
            log.error(f"Failed to initialize Jedi project: {e}", exc_info=True)
            self.project = None

    def get_completions(self, source: str, line: int, col: int, filepath: str):
        """Generates code completions."""
        if not self.project:
            self.completions_ready.emit([])
            return
        try:
            script = jedi.Script(
                code=source, path=filepath, project=self.project
            )
            completions = script.complete(line=line, column=col)
            completion_data = [{
                'name': c.name,
                'type': c.type,
                'description': c.description,
                'docstring': c.docstring(raw=True)
            } for c in completions]
            self.completions_ready.emit(completion_data)
        except Exception as e:
            log.error(f"Error getting Jedi completions: {e}", exc_info=False)
            self.completions_ready.emit([])

    def get_definition(self, source: str, line: int, col: int, filepath: str):
        """Finds the definition of a symbol."""
        if not self.project:
            self.definition_ready.emit(None, -1, -1)
            return
        try:
            script = jedi.Script(
                code=source, path=filepath, project=self.project
            )
            definitions = script.goto(line=line, column=col)
            if definitions:
                d = definitions[0]
                log.info(
                    f"Jedi found definition for '{d.name}' at "
                    f"{d.module_path}:{d.line}:{d.column}"
                )
                self.definition_ready.emit(
                    str(d.module_path), d.line, d.column
                )
            else:
                log.info("Jedi could not find a definition.")
                self.definition_ready.emit(None, -1, -1)
        except Exception as e:
            log.error(f"Error getting Jedi definition: {e}", exc_info=False)
            self.definition_ready.emit(None, -1, -1)

    def get_signature(self, source: str, line: int, col: int, filepath: str):
        """Gets signature information for a function call."""
        if not self.project:
            self.signature_ready.emit(None)
            return
        try:
            script = jedi.Script(
                code=source, path=filepath, project=self.project
            )
            signatures = script.get_signatures(line=line, column=col)
            self.signature_ready.emit(signatures[0] if signatures else None)
        except Exception as e:
            log.error(f"Error getting Jedi signature: {e}", exc_info=False)
            try:
                self.signature_ready.emit(None)
            except RuntimeError:
                log.warning(
                    "JediWorker was likely deleted during an exception. "
                    "Ignoring signal emit error."
                )


class CompletionManager(QObject):
    """
    Manages code completion, definition finding, and hover tooltips
    by delegating to a JediWorker on a background thread.
    """
    completions_available = pyqtSignal(list)
    definition_found = pyqtSignal(str, int, int)
    hover_tip_ready = pyqtSignal(str)

    _completions_requested = pyqtSignal(str, int, int, str)
    _definition_requested = pyqtSignal(str, int, int, str)
    _signature_requested = pyqtSignal(str, int, int, str)
    _project_path_changed = pyqtSignal(str)

    def __init__(self, theme_manager: 'ThemeManager', parent: Optional[QObject] = None):
        super().__init__(parent)
        self.theme_manager = theme_manager
        self.thread = QThread()
        self.worker = JediWorker()
        self.worker.moveToThread(self.thread)

        # Connect signals to worker slots
        self._completions_requested.connect(self.worker.get_completions)
        self._definition_requested.connect(self.worker.get_definition)
        self._signature_requested.connect(self.worker.get_signature)
        self._project_path_changed.connect(self.worker.set_project)

        # Connect worker signals to manager slots
        self.worker.completions_ready.connect(self.completions_available)
        self.worker.definition_ready.connect(self.definition_found)
        self.worker.signature_ready.connect(self._format_signature_for_tooltip)

        self.thread.start()
        log.info("CompletionManager background thread started.")

    def update_project_path(self, project_path: str):
        self._project_path_changed.emit(project_path)

    def request_completions(
        self, source: str, line: int, col: int, filepath: str
    ):
        self._completions_requested.emit(source, line, col, filepath)

    def request_definition(
        self, source: str, line: int, col: int, filepath: str
    ):
        self._definition_requested.emit(source, line, col, filepath)

    def request_signature(
        self, source: str, line: int, col: int, filepath: str
    ):
        self._signature_requested.emit(source, line, col, filepath)

    def _format_signature_for_tooltip(self, signature: Optional[Any]):
        """Formats a Jedi signature object into a themed HTML tooltip."""
        if not signature:
            self.hover_tip_ready.emit("")
            return

        try:
            colors = self.theme_manager.current_theme_data.get('colors', {})
            bg = colors.get('menu.background', '#2b2b2b')
            fg = colors.get('editor.foreground', '#a9b7c6')
            accent = colors.get('syntax.functionName', '#88c0d0')
            doc_fg = colors.get('syntax.comment', '#88929b')
            border = colors.get('input.border', '#555555')

            params_str = ', '.join(p.description for p in signature.params)
            header = f"def {signature.name}({params_str})"
            docstring = signature.docstring(raw=True).strip()

            # Escape HTML characters in the docstring for safe rendering
            doc_html = html.escape(docstring)
            doc_html = (
                "<pre style='white-space: pre-wrap; margin: 0; padding: 0; "
                f"font-family: inherit;'>{doc_html}</pre>"
            )

            tooltip_html = f"""
                <div style='background-color: {bg}; color: {fg};
                            font-family: Consolas, "Courier New", monospace;
                            font-size: 10pt; padding: 8px; border-radius: 4px;
                            border: 1px solid {border};'>
                    <b style='color: {accent};'>{header}</b>
            """
            if docstring:
                tooltip_html += (
                    f"<hr style='border-color: {border}; "
                    "border-style: solid; margin: 6px 0;' />"
                    f"<div style='color: {doc_fg};'>{doc_html}</div>"
                )
            tooltip_html += "</div>"
            self.hover_tip_ready.emit(tooltip_html.strip())
        except Exception as e:
            log.error(
                f"Error formatting signature tooltip: {e}", exc_info=False
            )
            self.hover_tip_ready.emit("")

    def shutdown(self):
        """Gracefully shuts down the Jedi worker thread."""
        if self.thread and self.thread.isRunning():
            log.info("Shutting down CompletionManager thread.")
            # Disconnect signals to prevent any more work from being sent
            try:
                self._completions_requested.disconnect()
                self._definition_requested.disconnect()
                self._signature_requested.disconnect()
                self._project_path_changed.disconnect()
            except TypeError:
                pass  # Signals may already be disconnected

            self.thread.quit()
            if not self.thread.wait(3000):  # Wait 3 seconds
                log.warning(
                    "CompletionManager thread did not shut down "
                    "gracefully. Terminating."
                )
                self.thread.terminate()
```

### File: `/app_core/__init__.py`
```py

```

### File: `/app_core/highlighters/rust_syntax_highlighter.py`
```py
# PuffinPyEditor/app_core/highlighters/rust_syntax_highlighter.py
from typing import Dict, List, Tuple, TYPE_CHECKING
from PyQt6.QtGui import QSyntaxHighlighter, QTextCharFormat, QColor, QFont
from PyQt6.QtCore import QRegularExpression
from utils.logger import log

if TYPE_CHECKING:
    from app_core.theme_manager import ThemeManager


class RustSyntaxHighlighter(QSyntaxHighlighter):
    """A syntax highlighter for Rust code."""

    def __init__(self, parent_document, theme_manager: "ThemeManager"):
        super().__init__(parent_document)
        self.theme_manager = theme_manager
        self.highlighting_rules: List[Tuple[QRegularExpression, QTextCharFormat]] = []
        self.multiline_comment_format = QTextCharFormat()
        self.initialize_formats_and_rules()
        log.info("RustSyntaxHighlighter initialized.")

    def initialize_formats_and_rules(self):
        """Initializes all text formats and regular expression rules based on the theme."""
        self.formats: Dict[str, QTextCharFormat] = {}
        colors = self.theme_manager.current_theme_data.get("colors", {})

        def get_color(key: str, fallback: str) -> QColor:
            return QColor(colors.get(f"syntax.{key}", fallback))

        self.formats["keyword"] = QTextCharFormat()
        self.formats["keyword"].setForeground(get_color("keyword", "#e67e80"))
        self.formats["keyword"].setFontWeight(QFont.Weight.Bold)

        self.formats["special"] = QTextCharFormat()
        self.formats["special"].setForeground(get_color("self", "#e67e80"))
        self.formats["special"].setFontItalic(True)

        self.formats["attribute"] = QTextCharFormat()
        self.formats["attribute"].setForeground(get_color("decorator", "#dbbc7f"))

        self.formats["macro"] = QTextCharFormat()
        self.formats["macro"].setForeground(get_color("decorator", "#dbbc7f"))

        self.formats["type"] = QTextCharFormat()
        self.formats["type"].setForeground(get_color("className", "#dbbc7f"))

        self.formats["functionName"] = QTextCharFormat()
        self.formats["functionName"].setForeground(get_color("functionName", "#83c092"))

        self.formats["comment"] = QTextCharFormat()
        self.formats["comment"].setForeground(get_color("comment", "#5f6c6d"))
        self.formats["comment"].setFontItalic(True)
        self.multiline_comment_format = self.formats["comment"]

        self.formats["string"] = QTextCharFormat()
        self.formats["string"].setForeground(get_color("string", "#a7c080"))

        self.formats["number"] = QTextCharFormat()
        self.formats["number"].setForeground(get_color("number", "#d699b6"))

        self.highlighting_rules = []
        keywords = [
            r'\b(as|break|const|continue|crate|else|enum|extern|false|fn|for|if|impl|in|let|loop|match|mod|move|mut|pub|ref|return|static|struct|super|trait|true|type|unsafe|use|where|while|async|await|dyn)\b'
        ]
        self.highlighting_rules += [(QRegularExpression(p), self.formats["keyword"]) for p in keywords]
        special_keywords = [r'\b(self|Self)\b']
        self.highlighting_rules += [(QRegularExpression(p), self.formats["special"]) for p in special_keywords]
        self.highlighting_rules.extend([
            (QRegularExpression(r"#\!\[[^\]]+\]|#\[[^\]]+\]"), self.formats["attribute"]),
            (QRegularExpression(r"\b([a-zA-Z0-9_]+)!\b"), self.formats["macro"]),
            (QRegularExpression(r'\b[A-Z][a-zA-Z0-9_]*\b'), self.formats["type"]),
            (QRegularExpression(r'\b(fn)\s+([a-zA-Z_][a-zA-Z0-9_]*)'), self._format_function_definition),
            (QRegularExpression(r"'\w+"), self.formats["special"]),
            (QRegularExpression(r'"[^"\\]*(\\.[^"\\]*)*"'), self.formats["string"]),
            (QRegularExpression(r'\b[0-9]+(_[0-9]+)*\.?[0-9]*\b'), self.formats["number"]),
            (QRegularExpression(r'//.*'), self.formats["comment"]),
        ])
        self.comment_start_expression = QRegularExpression(r"/\*")
        self.comment_end_expression = QRegularExpression(r"\*/")

    def _format_function_definition(self, match):
        """Custom formatter to style `fn` as keyword and name as functionName."""
        self.setFormat(match.capturedStart(1), match.capturedLength(1), self.formats["keyword"])
        self.setFormat(match.capturedStart(2), match.capturedLength(2), self.formats["functionName"])

    def highlightBlock(self, text: str):
        for pattern, fmt in self.highlighting_rules:
            iterator = pattern.globalMatch(text)
            while iterator.hasNext():
                match = iterator.next()
                if callable(fmt):
                    fmt(match)
                else:
                    self.setFormat(match.capturedStart(), match.capturedLength(), fmt)

        self.setCurrentBlockState(0)
        search_index = 0

        # Elegantly handle continuation from a previous block
        if self.previousBlockState() == 1:
            end_match = self.comment_end_expression.match(text, 0)
            if not end_match.hasMatch():
                # The entire block is a comment, our work is simple and swift.
                self.setCurrentBlockState(1)
                self.setFormat(0, len(text), self.multiline_comment_format)
                return

            # The comment concludes, we find our new starting point.
            length = end_match.capturedEnd()
            self.setFormat(0, length, self.multiline_comment_format)
            search_index = length

        # Now, we seek new comments with a more expressive loop.
        while (start_match := self.comment_start_expression.match(text, search_index)).hasMatch():
            start_pos = start_match.capturedStart()
            end_match = self.comment_end_expression.match(text, start_pos + start_match.capturedLength())

            if not end_match.hasMatch():
                # An unclosed comment, a cliffhanger for the next block.
                self.setCurrentBlockState(1)
                self.setFormat(start_pos, len(text) - start_pos, self.multiline_comment_format)
                return  # Our tale for this block is told.

            # A complete, self-contained comment.
            length = end_match.capturedEnd() - start_pos
            self.setFormat(start_pos, length, self.multiline_comment_format)
            search_index = end_match.capturedEnd()

    def rehighlight(self):
        self.initialize_formats_and_rules()
        super().rehighlight()
```

### File: `/app_core/highlighters/python_syntax_highlighter.py`
```py
# PuffinPyEditor/app_core/highlighters/python_syntax_highlighter.py
from typing import Dict, List, Tuple, TYPE_CHECKING
from PyQt6.QtGui import QSyntaxHighlighter, QTextCharFormat, QColor, QFont
from PyQt6.QtCore import QRegularExpression
from utils.logger import log

if TYPE_CHECKING:
    from app_core.theme_manager import ThemeManager


class PythonSyntaxHighlighter(QSyntaxHighlighter):
    """
    A syntax highlighter for Python code that dynamically styles based on the
    current theme from the ThemeManager.
    """

    def __init__(self, parent_document, theme_manager: "ThemeManager"):
        super().__init__(parent_document)
        self.theme_manager = theme_manager
        self.highlighting_rules: List[Tuple[QRegularExpression, QTextCharFormat]] = []
        self.multiline_string_format = QTextCharFormat()

        self.initialize_formats_and_rules()
        log.info("PythonSyntaxHighlighter initialized from app_core.")

    def initialize_formats_and_rules(self):
        """
        Initializes all text formats based on the current theme and sets up
        the regular expression rules for highlighting.
        """
        formats: Dict[str, QTextCharFormat] = {}
        colors = self.theme_manager.current_theme_data.get("colors", {})

        def get_color(key: str, fallback: str) -> QColor:
            return QColor(colors.get(f"syntax.{key}", fallback))

        formats["keyword"] = QTextCharFormat()
        formats["keyword"].setForeground(get_color("keyword", "#e67e80"))
        formats["keyword"].setFontWeight(QFont.Weight.Bold)

        formats["self"] = QTextCharFormat()
        formats["self"].setForeground(get_color("self", "#e67e80"))
        formats["self"].setFontItalic(True)

        formats["operator"] = QTextCharFormat()
        formats["operator"].setForeground(get_color("operator", "#d3c6aa"))

        formats["brace"] = QTextCharFormat()
        formats["brace"].setForeground(get_color("brace", "#d3c6aa"))

        formats["decorator"] = QTextCharFormat()
        formats["decorator"].setForeground(get_color("decorator", "#dbbc7f"))
        formats["decorator"].setFontItalic(True)

        formats["className"] = QTextCharFormat()
        formats["className"].setForeground(get_color("className", "#dbbc7f"))
        formats["className"].setFontWeight(QFont.Weight.Bold)

        formats["functionName"] = QTextCharFormat()
        formats["functionName"].setForeground(
            get_color("functionName", "#83c092")
        )

        formats["comment"] = QTextCharFormat()
        formats["comment"].setForeground(get_color("comment", "#5f6c6d"))
        formats["comment"].setFontItalic(True)

        formats["string"] = QTextCharFormat()
        formats["string"].setForeground(get_color("string", "#a7c080"))

        formats["docstring"] = QTextCharFormat()
        formats["docstring"].setForeground(get_color("docstring", "#5f6c6d"))
        formats["docstring"].setFontItalic(True)
        self.multiline_string_format = formats["docstring"]

        formats["number"] = QTextCharFormat()
        formats["number"].setForeground(get_color("number", "#d699b6"))

        self.highlighting_rules = []

        keywords = [
            r'\bdef\b', r'\bclass\b', r'\bif\b', r'\belif\b', r'\belse\b',
            r'\bfor\b', r'\bwhile\b', r'\breturn\b', r'\byield\b', r'\bpass\b',
            r'\bcontinue\b', r'\bbreak\b', r'\bimport\b', r'\bfrom\b',
            r'\bas\b', r'\btry\b', r'\bexcept\b', r'\bfinally\b', r'\braise\b',
            r'\bwith\b', r'\bassert\b', r'\bdel\b', r'\bglobal\b',
            r'\bnonlocal\b', r'\bin\b', r'\bis\b', r'\blambda\b', r'\bnot\b',
            r'\bor\b', r'\band\b', r'\bTrue\b', r'\bFalse\b', r'\bNone\b',
            r'\basync\b', r'\bawait\b'
        ]
        self.highlighting_rules += [
            (QRegularExpression(p), formats["keyword"]) for p in keywords
        ]

        self.highlighting_rules.extend([
            (QRegularExpression(r'\bself\b'), formats["self"]),
            (QRegularExpression(r'@[A-Za-z0-9_]+'), formats["decorator"]),
            (QRegularExpression(r'\b[A-Z][A-Za-z0-9_]*'), formats["className"]),
            (QRegularExpression(r'\b[a-z_][A-Za-z0-9_]*(?=\()'),
             formats["functionName"]),
            (QRegularExpression(r'[+\-*/%=<>!&|^~]'), formats["operator"]),
            (QRegularExpression(r'[{}()\[\]]'), formats["brace"]),
            (QRegularExpression(r'\b[0-9]+\b'), formats["number"]),
            (QRegularExpression(r'"[^"\\]*(\\.[^"\\]*)*"'), formats["string"]),
            (QRegularExpression(r"'[^'\\]*(\\.[^'\\]*)*'"), formats["string"]),
            (QRegularExpression(r'#.*'), formats["comment"]),
        ])

        self.tri_single_quote_start = QRegularExpression(r"'''")
        self.tri_double_quote_start = QRegularExpression(r'"""')

    def highlightBlock(self, text: str):
        # 1. Apply all single-line rules
        for pattern, fmt in self.highlighting_rules:
            iterator = pattern.globalMatch(text)
            while iterator.hasNext():
                match = iterator.next()
                self.setFormat(match.capturedStart(), match.capturedLength(), fmt)

        # 2. Handle multi-line strings with explicit state management
        # State 0: Normal, State 1: In """, State 2: In '''
        NORMAL_STATE = 0
        IN_TRIPLE_DOUBLE = 1
        IN_TRIPLE_SINGLE = 2

        self.setCurrentBlockState(NORMAL_STATE)

        start_index = 0
        previous_state = self.previousBlockState()

        if previous_state == IN_TRIPLE_DOUBLE:
            delimiter = self.tri_double_quote_start
            end_match = delimiter.match(text, 0)
            if end_match.hasMatch():
                length = end_match.capturedEnd()
                self.setFormat(0, length, self.multiline_string_format)
                start_index = length
            else:
                self.setCurrentBlockState(IN_TRIPLE_DOUBLE)
                self.setFormat(0, len(text), self.multiline_string_format)
                return

        elif previous_state == IN_TRIPLE_SINGLE:
            delimiter = self.tri_single_quote_start
            end_match = delimiter.match(text, 0)
            if end_match.hasMatch():
                length = end_match.capturedEnd()
                self.setFormat(0, length, self.multiline_string_format)
                start_index = length
            else:
                self.setCurrentBlockState(IN_TRIPLE_SINGLE)
                self.setFormat(0, len(text), self.multiline_string_format)
                return

        # 3. Find new multi-line strings in the rest of the block
        delimiters = [
            (self.tri_double_quote_start, IN_TRIPLE_DOUBLE),
            (self.tri_single_quote_start, IN_TRIPLE_SINGLE)
        ]

        while start_index < len(text):
            # Find the next occurring delimiter of any type with grace and simplicity.
            next_match, next_state_to_set, next_delimiter_re = None, None, None
            first_pos = float('inf')

            for delimiter_re, state_to_set in delimiters:
                match = delimiter_re.match(text, start_index)
                if match.hasMatch() and match.capturedStart() < first_pos:
                    first_pos = match.capturedStart()
                    next_match = match
                    next_state_to_set = state_to_set
                    next_delimiter_re = delimiter_re

            if not next_match:
                break  # No more delimiters found in the remaining text.

            start_pos = next_match.capturedStart()
            # Re-use the found delimiter regex to find its partner
            end_match = next_delimiter_re.match(text, start_pos + next_match.capturedLength())

            if end_match.hasMatch():
                # A complete story, with a beginning and an end.
                length = end_match.capturedEnd() - start_pos
                self.setFormat(start_pos, length, self.multiline_string_format)
                start_index = end_match.capturedEnd()
            else:
                # A story left unfinished...
                self.setCurrentBlockState(next_state_to_set)
                self.setFormat(start_pos, len(text) - start_pos, self.multiline_string_format)
                return

    def rehighlight(self):
        """Forces a re-highlight of the entire document."""
        log.info("Re-highlighting entire document for Python syntax.")
        self.initialize_formats_and_rules()
        super().rehighlight()
```

### File: `/app_core/highlighters/json_syntax_highlighter.py`
```py
# PuffinPyEditor/app_core/highlighters/json_syntax_highlighter.py
from typing import TYPE_CHECKING
from PyQt6.QtGui import QSyntaxHighlighter, QTextCharFormat, QColor, QFont
from PyQt6.QtCore import QRegularExpression
from utils.logger import log

if TYPE_CHECKING:
    from app_core.theme_manager import ThemeManager

class JsonSyntaxHighlighter(QSyntaxHighlighter):
    """A syntax highlighter for JSON files."""

    def __init__(self, parent_document, theme_manager: "ThemeManager"):
        super().__init__(parent_document)
        self.theme_manager = theme_manager
        self.highlighting_rules = []
        self.initialize_formats_and_rules()
        log.info("JsonSyntaxHighlighter initialized.")

    def initialize_formats_and_rules(self):
        """Initializes formats and rules based on the current theme."""
        colors = self.theme_manager.current_theme_data.get("colors", {})

        def get_color(key: str, fallback: str) -> QColor:
            return QColor(colors.get(f"syntax.{key}", fallback))

        # Format for keys (strings before a colon)
        key_format = QTextCharFormat()
        key_format.setForeground(get_color("className", "#dbbc7f"))

        # Format for string values
        string_format = QTextCharFormat()
        string_format.setForeground(get_color("string", "#a7c080"))

        # Format for numbers
        number_format = QTextCharFormat()
        number_format.setForeground(get_color("number", "#d699b6"))

        # Format for keywords (true, false, null)
        keyword_format = QTextCharFormat()
        keyword_format.setForeground(get_color("keyword", "#e67e80"))
        keyword_format.setFontWeight(QFont.Weight.Bold)

        # Format for operators/braces
        brace_format = QTextCharFormat()
        brace_format.setForeground(get_color("brace", "#d3c6aa"))

        self.highlighting_rules = [
            (QRegularExpression(r'[\{\}\[\]]'), brace_format),
            (QRegularExpression(r'\b(true|false|null)\b'), keyword_format),
            (QRegularExpression(r'\b-?(?:0|[1-9]\d*)(?:\.\d+)?(?:[eE][+-]?\d+)?\b'), number_format),
            (QRegularExpression(r'"[^"\\]*(\\.[^"\\]*)*"'), string_format),
            (QRegularExpression(r'"[^"\\]*(\\.[^"\\]*)*"(?=\s*:)'), key_format),
        ]

    def highlightBlock(self, text: str):
        """Highlights a single block of text."""
        for pattern, fmt in self.highlighting_rules:
            iterator = pattern.globalMatch(text)
            while iterator.hasNext():
                match = iterator.next()
                self.setFormat(match.capturedStart(), match.capturedLength(), fmt)

    def rehighlight(self):
        """Forces a re-highlight of the entire document on theme change."""
        self.initialize_formats_and_rules()
        super().rehighlight()
```

### File: `/app_core/highlighters/javascript_syntax_highlighter.py`
```py
# PuffinPyEditor/app_core/highlighters/javascript_syntax_highlighter.py
from typing import Dict, List, Tuple, TYPE_CHECKING
from PyQt6.QtGui import QSyntaxHighlighter, QTextCharFormat, QColor, QFont
from PyQt6.QtCore import QRegularExpression
from utils.logger import log

if TYPE_CHECKING:
    from app_core.theme_manager import ThemeManager


class JavaScriptSyntaxHighlighter(QSyntaxHighlighter):
    """A syntax highlighter for JavaScript code."""

    def __init__(self, parent_document, theme_manager: "ThemeManager"):
        super().__init__(parent_document)
        self.theme_manager = theme_manager
        self.highlighting_rules: List[Tuple[QRegularExpression, QTextCharFormat]] = []
        self.multiline_comment_format = QTextCharFormat()

        self.initialize_formats_and_rules()
        log.info("JavaScriptSyntaxHighlighter initialized.")

    def initialize_formats_and_rules(self):
        """Initializes all text formats based on the current theme and sets up regex rules."""
        self.formats: Dict[str, QTextCharFormat] = {}
        colors = self.theme_manager.current_theme_data.get("colors", {})

        def get_color(key: str, fallback: str) -> QColor:
            # Re-use existing python syntax colors for simplicity
            return QColor(colors.get(f"syntax.{key}", fallback))

        self.formats["keyword"] = QTextCharFormat()
        self.formats["keyword"].setForeground(get_color("keyword", "#e67e80"))
        self.formats["keyword"].setFontWeight(QFont.Weight.Bold)

        self.formats["operator"] = QTextCharFormat()
        self.formats["operator"].setForeground(get_color("operator", "#d3c6aa"))

        self.formats["brace"] = QTextCharFormat()
        self.formats["brace"].setForeground(get_color("brace", "d3c6aa"))

        self.formats["className"] = QTextCharFormat()
        self.formats["className"].setForeground(get_color("className", "#dbbc7f"))
        self.formats["className"].setFontWeight(QFont.Weight.Bold)

        self.formats["functionName"] = QTextCharFormat()
        self.formats["functionName"].setForeground(get_color("functionName", "#83c092"))

        self.formats["comment"] = QTextCharFormat()
        self.formats["comment"].setForeground(get_color("comment", "#5f6c6d"))
        self.formats["comment"].setFontItalic(True)
        self.multiline_comment_format = self.formats["comment"]

        self.formats["string"] = QTextCharFormat()
        self.formats["string"].setForeground(get_color("string", "#a7c080"))

        self.formats["number"] = QTextCharFormat()
        self.formats["number"].setForeground(get_color("number", "#d699b6"))

        # Build Rule List
        self.highlighting_rules = []

        keywords = [
            r'\bfunction\b', r'\bclass\b', r'\blet\b', r'\bconst\b', r'\bvar\b',
            r'\bif\b', r'\belse\b', r'\bfor\b', r'\bwhile\b', r'\breturn\b',
            r'\bswitch\b', r'\bcase\b', r'\bdefault\b', r'\bnew\b', r'\bthis\b',
            r'\btry\b', r'\bcatch\b', r'\bfinally\b', r'\bthrow\b', r'\btypeof\b',
            r'\bimport\b', r'\bexport\b', r'\bfrom\b', r'\basync\b', r'\bawait\b',
            r'\btrue\b', r'\bfalse\b', r'\bnull\b', r'\bundefined\b'
        ]
        self.highlighting_rules += [(QRegularExpression(p), self.formats["keyword"]) for p in keywords]

        self.highlighting_rules.extend([
            (QRegularExpression(r'\b[A-Z][A-Za-z0-9_]*'), self.formats["className"]),
            (QRegularExpression(r'[a-z_][A-Za-z0-9_]*(?=\s*=\s*function|\s*=\s*\(|\s*\()'),
             self.formats["functionName"]),
            (QRegularExpression(r'[=><!~?&|+\-*/^%]+'), self.formats["operator"]),
            (QRegularExpression(r'\{|\}|\(|\)|\[|\]'), self.formats["brace"]),
            (QRegularExpression(r'\b[0-9]+(\.[0-9]+)?\b'), self.formats["number"]),
            (QRegularExpression(r'"[^"\\]*(\\.[^"\\]*)*"'), self.formats["string"]),
            (QRegularExpression(r"'[^'\\]*(\\.[^'\\]*)*'"), self.formats["string"]),
            (QRegularExpression(r"`[^`\\]*(\\.[^`\\]*)*`"), self.formats["string"]),  # Template literals
            (QRegularExpression(r'//.*'), self.formats["comment"]),
        ])

        # For multiline comments /* ... */
        self.comment_start_expression = QRegularExpression(r"/\*")
        self.comment_end_expression = QRegularExpression(r"\*/")

    def highlightBlock(self, text: str):
        # Apply single-line rules first
        for pattern, fmt in self.highlighting_rules:
            iterator = pattern.globalMatch(text)
            while iterator.hasNext():
                match = iterator.next()
                self.setFormat(match.capturedStart(), match.capturedLength(), fmt)

        self.setCurrentBlockState(0)
        search_index = 0

        # Elegantly handle continuation from a previous block
        if self.previousBlockState() == 1:
            end_match = self.comment_end_expression.match(text, 0)
            if not end_match.hasMatch():
                # The entire block is a comment, our work is simple and swift.
                self.setCurrentBlockState(1)
                self.setFormat(0, len(text), self.multiline_comment_format)
                return

            # The comment concludes, we find our new starting point.
            length = end_match.capturedEnd()
            self.setFormat(0, length, self.multiline_comment_format)
            search_index = length

        # Now, we seek new comments with a more expressive loop.
        while (start_match := self.comment_start_expression.match(text, search_index)).hasMatch():
            start_pos = start_match.capturedStart()
            end_match = self.comment_end_expression.match(text, start_pos + start_match.capturedLength())

            if not end_match.hasMatch():
                # An unclosed comment, a cliffhanger for the next block.
                self.setCurrentBlockState(1)
                self.setFormat(start_pos, len(text) - start_pos, self.multiline_comment_format)
                return  # Our tale for this block is told.

            # A complete, self-contained comment.
            length = end_match.capturedEnd() - start_pos
            self.setFormat(start_pos, length, self.multiline_comment_format)
            search_index = end_match.capturedEnd()

    def rehighlight(self):
        """Forces a re-highlight of the entire document, usually on theme change."""
        self.initialize_formats_and_rules()
        super().rehighlight()
```

### File: `/app_core/highlighters/html_syntax_highlighter.py`
```py
# PuffinPyEditor/app_core/highlighters/html_syntax_highlighter.py
from typing import TYPE_CHECKING
from PyQt6.QtGui import QSyntaxHighlighter, QTextCharFormat, QColor, QFont
from PyQt6.QtCore import QRegularExpression
from utils.logger import log

if TYPE_CHECKING:
    from app_core.theme_manager import ThemeManager


class HtmlSyntaxHighlighter(QSyntaxHighlighter):
    """A syntax highlighter for HTML code."""

    def __init__(self, parent_document, theme_manager: "ThemeManager"):
        super().__init__(parent_document)
        self.theme_manager = theme_manager
        self.rules = []
        self.multiline_comment_format = QTextCharFormat()
        self.initialize_formats_and_rules()
        log.info("HtmlSyntaxHighlighter initialized.")

    def initialize_formats_and_rules(self):
        formats = {}
        colors = self.theme_manager.current_theme_data.get("colors", {})

        def get_color(key, fallback):
            return QColor(colors.get(f"syntax.{key}", fallback))

        # Format for tags like <p>, <div>
        tag_format = QTextCharFormat()
        tag_format.setForeground(get_color("keyword", "#e67e80"))

        # Format for attributes like href, class
        attribute_format = QTextCharFormat()
        attribute_format.setForeground(get_color("className", "#dbbc7f"))
        attribute_format.setFontItalic(True)

        # Format for attribute values like "styles.css"
        value_format = QTextCharFormat()
        value_format.setForeground(get_color("string", "#a7c080"))

        # Format for HTML comments <!-- ... -->
        comment_format = QTextCharFormat()
        comment_format.setForeground(get_color("comment", "#5f6c6d"))
        comment_format.setFontItalic(True)
        self.multiline_comment_format = comment_format

        # Format for DOCTYPE
        doctype_format = QTextCharFormat()
        doctype_format.setForeground(get_color("decorator", "#dbbc7f"))

        self.rules = [
            # Tags: <tag>, </tag>, <tag/>
            (QRegularExpression(r"</?([a-zA-Z0-9_-]+)"), tag_format),
            # Attributes: href=, class=
            (QRegularExpression(r'\b([a-zA-Z_-]+)(?=\s*=)'), attribute_format),
            # Attribute values in quotes
            (QRegularExpression(r'"[^"]*"'), value_format),
            (QRegularExpression(r"'[^']*'"), value_format),
            # DOCTYPE
            (QRegularExpression(r'<!DOCTYPE[^>]*>'), doctype_format),
        ]

        self.comment_start_expression = QRegularExpression(r"<!--")
        self.comment_end_expression = QRegularExpression(r"-->")

    def highlightBlock(self, text: str):
        # Apply single-line rules first
        for pattern, fmt in self.rules:
            iterator = pattern.globalMatch(text)
            while iterator.hasNext():
                match = iterator.next()
                self.setFormat(match.capturedStart(), match.capturedLength(), fmt)

        self.setCurrentBlockState(0)
        search_index = 0

        # Elegantly handle continuation from a previous block
        if self.previousBlockState() == 1:
            end_match = self.comment_end_expression.match(text, 0)
            if not end_match.hasMatch():
                # The entire block is a comment, our work is simple and swift.
                self.setCurrentBlockState(1)
                self.setFormat(0, len(text), self.multiline_comment_format)
                return

            # The comment concludes, we find our new starting point.
            length = end_match.capturedEnd()
            self.setFormat(0, length, self.multiline_comment_format)
            search_index = length

        # Now, we seek new comments with a more expressive loop.
        while (start_match := self.comment_start_expression.match(text, search_index)).hasMatch():
            start_pos = start_match.capturedStart()
            end_match = self.comment_end_expression.match(text, start_pos + start_match.capturedLength())

            if not end_match.hasMatch():
                # An unclosed comment, a cliffhanger for the next block.
                self.setCurrentBlockState(1)
                self.setFormat(start_pos, len(text) - start_pos, self.multiline_comment_format)
                return  # Our tale for this block is told.

            # A complete, self-contained comment.
            length = end_match.capturedEnd() - start_pos
            self.setFormat(start_pos, length, self.multiline_comment_format)
            search_index = end_match.capturedEnd()

    def rehighlight(self):
        self.initialize_formats_and_rules()
        super().rehighlight()
```

### File: `/app_core/highlighters/css_syntax_highlighter.py`
```py
# PuffinPyEditor/app_core/highlighters/css_syntax_highlighter.py
from typing import Dict, List, Tuple, TYPE_CHECKING
from PyQt6.QtGui import QSyntaxHighlighter, QTextCharFormat, QColor, QFont
from PyQt6.QtCore import QRegularExpression
from utils.logger import log

if TYPE_CHECKING:
    from app_core.theme_manager import ThemeManager


class CssSyntaxHighlighter(QSyntaxHighlighter):
    """A syntax highlighter for CSS stylesheets."""

    def __init__(self, parent_document, theme_manager: "ThemeManager"):
        super().__init__(parent_document)
        self.theme_manager = theme_manager
        self.highlighting_rules: List[Tuple[QRegularExpression, QTextCharFormat]] = []
        self.multiline_comment_format = QTextCharFormat()

        self.initialize_formats_and_rules()
        log.info("CssSyntaxHighlighter initialized.")

    def initialize_formats_and_rules(self):
        """Initializes all text formats based on the current theme and sets up regex rules."""
        formats: Dict[str, QTextCharFormat] = {}
        colors = self.theme_manager.current_theme_data.get("colors", {})

        def get_color(key: str, fallback: str) -> QColor:
            # Re-use existing theme colors for consistency
            return QColor(colors.get(f"syntax.{key}", fallback))

        # Tag selectors, keywords like 'bold'
        formats["keyword"] = QTextCharFormat()
        formats["keyword"].setForeground(get_color("keyword", "#e67e80"))

        # Properties like 'color', 'font-size'
        formats["property"] = QTextCharFormat()
        formats["property"].setForeground(get_color("functionName", "#83c092"))

        # Class selectors like '.my-class'
        formats["class_selector"] = QTextCharFormat()
        formats["class_selector"].setForeground(get_color("className", "#dbbc7f"))
        
        # ID selectors like '#my-id', and at-rules like '@media'
        formats["at_rule_and_id"] = QTextCharFormat()
        formats["at_rule_and_id"].setForeground(get_color("decorator", "#dbbc7f"))

        # Values: numbers, units, colors
        formats["value_number"] = QTextCharFormat()
        formats["value_number"].setForeground(get_color("number", "#d699b6"))

        # Values: strings
        formats["value_string"] = QTextCharFormat()
        formats["value_string"].setForeground(get_color("string", "#a7c080"))

        # Braces, colons, etc.
        formats["operator"] = QTextCharFormat()
        formats["operator"].setForeground(get_color("operator", "#d3c6aa"))
        
        # Comments '/* ... */'
        formats["comment"] = QTextCharFormat()
        formats["comment"].setForeground(get_color("comment", "#5f6c6d"))
        formats["comment"].setFontItalic(True)
        self.multiline_comment_format = formats["comment"]
        
        # Build Rule List
        self.highlighting_rules = []

        # At-rules, e.g., @media, @keyframes
        self.highlighting_rules.append(
            (QRegularExpression(r"@[a-zA-Z_-]+"), formats["at_rule_and_id"])
        )

        # ID selector, e.g., #header
        self.highlighting_rules.append(
            (QRegularExpression(r"#[a-zA-Z0-9_-]+"), formats["at_rule_and_id"])
        )

        # Class selector, e.g., .container
        self.highlighting_rules.append(
            (QRegularExpression(r"\.[a-zA-Z0-9_-]+"), formats["class_selector"])
        )
        
        # Tag selectors (div, p, h1) and pseudo-classes (:hover)
        self.highlighting_rules.append(
            (QRegularExpression(r"\b([a-zA-Z_-]+)(?=\s*\{|::?[a-zA-Z-]+)"), formats["keyword"])
        )
        
        # Properties, e.g., color:, font-weight:
        self.highlighting_rules.append(
            (QRegularExpression(r"([a-zA-Z-]+)(?=\s*:)"), formats["property"])
        )
        
        # String values
        self.highlighting_rules.append(
            (QRegularExpression(r'"[^"\\]*(\\.[^"\\]*)*"'), formats["value_string"])
        )
        self.highlighting_rules.append(
            (QRegularExpression(r"'[^'\\]*(\\.[^'\\]*)*'"), formats["value_string"])
        )
        
        # Number values (pixels, percentages, colors), e.g. 12px, 80%, #fff, rgb(...)
        self.highlighting_rules.append(
            (QRegularExpression(r"(-?\d+(\.\d+)?(px|em|rem|%|pt|vh|vw)?|#[0-9a-fA-F]{3,6})"), formats["value_number"])
        )

        # Keyword values, e.g. bold, block, sans-serif
        keywords = [
            'auto', 'bold', 'italic', 'normal', 'none', 'solid', 'dotted', 'dashed', 'double',
            'inherit', 'initial', 'unset', 'block', 'inline', 'flex', 'grid', 'absolute', 'relative',
            'static', 'fixed', 'sticky', 'center', 'left', 'right', 'justify'
        ]
        self.highlighting_rules += [
            (QRegularExpression(f"\\b{word}\\b"), formats["keyword"]) for word in keywords
        ]
        
        # Braces and operators
        self.highlighting_rules.append(
             (QRegularExpression(r"\{|\}|:|;"), formats["operator"])
        )
        
        # For multiline comments /* ... */
        self.comment_start_expression = QRegularExpression(r"/\*")
        self.comment_end_expression = QRegularExpression(r"\*/")

    def highlightBlock(self, text: str):
        # Apply single-line rules first
        for pattern, fmt in self.highlighting_rules:
            iterator = pattern.globalMatch(text)
            while iterator.hasNext():
                match = iterator.next()
                self.setFormat(match.capturedStart(), match.capturedLength(), fmt)

        self.setCurrentBlockState(0)
        search_index = 0

        # Handle multiline comments
        if self.previousBlockState() == 1:
            end_match = self.comment_end_expression.match(text, 0)
            if not end_match.hasMatch():
                self.setCurrentBlockState(1)
                self.setFormat(0, len(text), self.multiline_comment_format)
                return

            length = end_match.capturedEnd()
            self.setFormat(0, length, self.multiline_comment_format)
            search_index = length

        while (start_match := self.comment_start_expression.match(text, search_index)).hasMatch():
            start_pos = start_match.capturedStart()
            end_match = self.comment_end_expression.match(text, start_pos + start_match.capturedLength())

            if not end_match.hasMatch():
                self.setCurrentBlockState(1)
                self.setFormat(start_pos, len(text) - start_pos, self.multiline_comment_format)
                return

            length = end_match.capturedEnd() - start_pos
            self.setFormat(start_pos, length, self.multiline_comment_format)
            search_index = end_match.capturedEnd()

    def rehighlight(self):
        """Forces a re-highlight of the entire document, usually on theme change."""
        self.initialize_formats_and_rules()
        super().rehighlight()
```

### File: `/app_core/highlighters/csharp_syntax_highlighter.py`
```py
# PuffinPyEditor/app_core/highlighters/csharp_syntax_highlighter.py
from typing import List, Tuple, TYPE_CHECKING
from PyQt6.QtGui import QSyntaxHighlighter, QTextCharFormat, QColor, QFont
from PyQt6.QtCore import QRegularExpression
from utils.logger import log

if TYPE_CHECKING:
    from app_core.theme_manager import ThemeManager


class CSharpSyntaxHighlighter(QSyntaxHighlighter):
    """A syntax highlighter for C# code."""

    def __init__(self, parent_document, theme_manager: "ThemeManager"):
        super().__init__(parent_document)
        self.theme_manager = theme_manager
        self.highlighting_rules: List[Tuple[QRegularExpression, QTextCharFormat]] = []
        self.multiline_comment_format = QTextCharFormat()
        self.initialize_formats_and_rules()
        log.info("CSharpSyntaxHighlighter initialized.")

    def initialize_formats_and_rules(self):
        formats = {}
        colors = self.theme_manager.current_theme_data.get("colors", {})

        def get_color(key: str, fallback: str) -> QColor:
            return QColor(colors.get(f"syntax.{key}", fallback))

        formats["keyword"] = QTextCharFormat()
        formats["keyword"].setForeground(get_color("keyword", "#e67e80"))
        formats["keyword"].setFontWeight(QFont.Weight.Bold)

        formats["preprocessor"] = QTextCharFormat()
        formats["preprocessor"].setForeground(get_color("decorator", "#dbbc7f"))

        formats["string"] = QTextCharFormat()
        formats["string"].setForeground(get_color("string", "#a7c080"))

        formats["comment"] = QTextCharFormat()
        formats["comment"].setForeground(get_color("comment", "#5f6c6d"))
        formats["comment"].setFontItalic(True)
        self.multiline_comment_format = formats["comment"]

        formats["number"] = QTextCharFormat()
        formats["number"].setForeground(get_color("number", "#d699b6"))

        formats["className"] = QTextCharFormat()
        formats["className"].setForeground(get_color("className", "#dbbc7f"))

        formats["functionName"] = QTextCharFormat()
        formats["functionName"].setForeground(get_color("functionName", "#83c092"))

        # Rule construction
        self.highlighting_rules = []

        keywords = [
            r'\babstract\b', r'\bas\b', r'\bbase\b', r'\bbool\b', r'\bbreak\b',
            r'\bbyte\b', r'\bcase\b', r'\bcatch\b', r'\bchar\b', r'\bchecked\b',
            r'\bclass\b', r'\bconst\b', r'\bcontinue\b', r'\bdecimal\b',
            r'\bdefault\b', r'\bdelegate\b', r'\bdo\b', r'\bdouble\b', r'\belse\b',
            r'\benum\b', r'\bevent\b', r'\bexplicit\b', r'\bextern\b', r'\bfalse\b',
            r'\bfinally\b', r'\bfixed\b', r'\bfloat\b', r'\bfor\b', r'\bforeach\b',
            r'\bgoto\b', r'\bif\b', r'\bimplicit\b', r'\bin\b', r'\bint\b',
            r'\binterface\b', r'\binternal\b', r'\bis\b', r'\block\b', r'\blong\b',
            r'\bnamespace\b', r'\bnew\b', r'\bnull\b', r'\bobject\b',
            r'\boperator\b', r'\bout\b', r'\boverride\b', r'\bparams\b',
            r'\bprivate\b', r'\bprotected\b', r'\bpublic\b', r'\breadonly\b',
            r'\bref\b', r'\breturn\b', r'\bsbyte\b', r'\bsealed\b', r'\bshort\b',
            r'\bsizeof\b', r'\bstackalloc\b', r'\bstatic\b', r'\bstring\b',
            r'\bstruct\b', r'\bswitch\b', r'\bthis\b', r'\bthrow\b', r'\btrue\b',
            r'\btry\b', r'\btypeof\b', r'\buint\b', r'\bulong\b', r'\bunchecked\b',
            r'\bunsafe\b', r'\bushort\b', r'\busing\b', r'\bvirtual\b',
            r'\bvoid\b', r'\bvolatile\b', r'\bwhile\b', r'\byield\b', r'\bvar\b'
        ]

        self.highlighting_rules += [(QRegularExpression(p), formats["keyword"]) for p in keywords]

        self.highlighting_rules.extend([
            (QRegularExpression(r'^\s*#[a-zA-Z_]+'), formats["preprocessor"]),
            (QRegularExpression(r'\b[A-Z][A-Za-z0-9_]*'), formats["className"]),
            (QRegularExpression(r'\b[A-Z][a-zA-Z0-9_]*(?=\s*\()'), formats["functionName"]),
            (QRegularExpression(r'"(?:[^"\\]|\\.)*"'), formats["string"]),
            (QRegularExpression(r"'\\?.'"), formats["string"]),
            (QRegularExpression(r'//.*'), formats["comment"]),
        ])

        self.comment_start_expression = QRegularExpression(r"/\*")
        self.comment_end_expression = QRegularExpression(r"\*/")

    def highlightBlock(self, text: str):
        # Apply single-line rules first
        for pattern, fmt in self.highlighting_rules:
            iterator = pattern.globalMatch(text)
            while iterator.hasNext():
                match = iterator.next()
                self.setFormat(match.capturedStart(), match.capturedLength(), fmt)

        self.setCurrentBlockState(0)
        search_index = 0

        # Elegantly handle continuation from a previous block
        if self.previousBlockState() == 1:
            end_match = self.comment_end_expression.match(text, 0)
            if not end_match.hasMatch():
                # The entire block is a comment, our work is simple and swift.
                self.setCurrentBlockState(1)
                self.setFormat(0, len(text), self.multiline_comment_format)
                return

            # The comment concludes, we find our new starting point.
            length = end_match.capturedEnd()
            self.setFormat(0, length, self.multiline_comment_format)
            search_index = length

        # Now, we seek new comments with a more expressive loop.
        while (start_match := self.comment_start_expression.match(text, search_index)).hasMatch():
            start_pos = start_match.capturedStart()
            end_match = self.comment_end_expression.match(text, start_pos + start_match.capturedLength())

            if not end_match.hasMatch():
                # An unclosed comment, a cliffhanger for the next block.
                self.setCurrentBlockState(1)
                self.setFormat(start_pos, len(text) - start_pos, self.multiline_comment_format)
                return  # Our tale for this block is told.

            # A complete, self-contained comment.
            length = end_match.capturedEnd() - start_pos
            self.setFormat(start_pos, length, self.multiline_comment_format)
            search_index = end_match.capturedEnd()

    def rehighlight(self):
        self.initialize_formats_and_rules()
        super().rehighlight()
```

### File: `/app_core/highlighters/cpp_syntax_highlighter.py`
```py
# PuffinPyEditor/app_core/highlighters/cpp_syntax_highlighter.py
from typing import Dict, List, Tuple, TYPE_CHECKING
from PyQt6.QtGui import QSyntaxHighlighter, QTextCharFormat, QColor, QFont
from PyQt6.QtCore import QRegularExpression
from utils.logger import log

if TYPE_CHECKING:
    from app_core.theme_manager import ThemeManager


class CppSyntaxHighlighter(QSyntaxHighlighter):
    """A syntax highlighter for C and C++ code."""

    def __init__(self, parent_document, theme_manager: "ThemeManager"):
        super().__init__(parent_document)
        self.theme_manager = theme_manager
        self.highlighting_rules: List[Tuple[QRegularExpression, QTextCharFormat]] = []
        self.multiline_comment_format = QTextCharFormat()

        self.initialize_formats_and_rules()
        log.info("CppSyntaxHighlighter initialized.")

    def initialize_formats_and_rules(self):
        """Initializes all text formats and regular expression rules."""
        formats: Dict[str, QTextCharFormat] = {}
        colors = self.theme_manager.current_theme_data.get("colors", {})

        def get_color(key: str, fallback: str) -> QColor:
            # Re-use existing python syntax colors for simplicity and consistency
            return QColor(colors.get(f"syntax.{key}", fallback))

        formats["keyword"] = QTextCharFormat()
        formats["keyword"].setForeground(get_color("keyword", "#e67e80"))
        formats["keyword"].setFontWeight(QFont.Weight.Bold)

        formats["preprocessor"] = QTextCharFormat()
        formats["preprocessor"].setForeground(get_color("decorator", "#dbbc7f"))
        formats["preprocessor"].setFontWeight(QFont.Weight.Medium)

        formats["operator"] = QTextCharFormat()
        formats["operator"].setForeground(get_color("operator", "#d3c6aa"))

        formats["brace"] = QTextCharFormat()
        formats["brace"].setForeground(get_color("brace", "d3c6aa"))

        formats["className"] = QTextCharFormat()
        formats["className"].setForeground(get_color("className", "#dbbc7f"))

        formats["functionName"] = QTextCharFormat()
        formats["functionName"].setForeground(get_color("functionName", "#83c092"))

        formats["comment"] = QTextCharFormat()
        formats["comment"].setForeground(get_color("comment", "#5f6c6d"))
        formats["comment"].setFontItalic(True)
        self.multiline_comment_format = formats["comment"]

        formats["string"] = QTextCharFormat()
        formats["string"].setForeground(get_color("string", "#a7c080"))

        formats["number"] = QTextCharFormat()
        formats["number"].setForeground(get_color("number", "#d699b6"))

        # Build Rule List
        self.highlighting_rules = []

        keywords = [
            r'\bchar\b', r'\bclass\b', r'\bconst\b', r'\bdouble\b', r'\benum\b',
            r'\bexplicit\b', r'\bfloat\b', r'\bfriend\b', r'\binline\b',
            r'\bint\b', r'\blong\b', r'\bnamespace\b', r'\boperator\b',
            r'\bprivate\b', r'\bprotected\b', r'\bpublic\b', r'\bshort\b',
            r'\bsigned\b', r'\bstatic\b', r'\bstruct\b', r'\btemplate\b',
            r'\btypedef\b', r'\btypename\b', r'\bunion\b', r'\bunsigned\b',
            r'\bvirtual\b', r'\bvoid\b', r'\bvolatile\b', r'\bwchar_t\b',
            # Control flow
            r'\bif\b', r'\belse\b', r'\bfor\b', r'\bwhile\b', r'\bdo\b',
            r'\bbreak\b', r'\bcontinue\b', r'\breturn\b', r'\bgoto\b',
            r'\bswitch\b', r'\bcase\b', r'\bdefault\b',
            # C++ specific
            r'\bnew\b', r'\bdelete\b', r'\bthis\b', r'\bthrow\b', r'\btry\b',
            r'\bcatch\b', r'\bexplicit\b', r'\bexport\b', r'\btrue\b',
            r'\bfalse\b', r'\bnullptr\b', r'\busing\b',
            # Newer keywords
            r'\bnoexcept\b', r'\bstatic_assert\b', r'\bdecltype\b', r'\bauto\b'
        ]
        self.highlighting_rules += [(QRegularExpression(p), formats["keyword"]) for p in keywords]

        self.highlighting_rules.extend([
            (QRegularExpression(r'^\s*#.*'), formats["preprocessor"]),
            (QRegularExpression(r'\b[A-Z][A-Za-z0-9_]*'), formats["className"]),
            (QRegularExpression(r'\b[a-zA-Z_][a-zA-Z0-9_]*(?=\s*\()'), formats["functionName"]),
            (QRegularExpression(r'[=><!~?&|+\-*/^%:]+'), formats["operator"]),
            (QRegularExpression(r'\{|\}|\(|\)|\[|\]'), formats["brace"]),
            (QRegularExpression(r'\b[0-9]+[fLu]?\b'), formats["number"]),
            (QRegularExpression(r'"[^"\\]*(\\.[^"\\]*)*"'), formats["string"]),
            (QRegularExpression(r"'\\?.'"), formats["string"]),  # Char literal
            (QRegularExpression(r'//.*'), formats["comment"]),
        ])

        self.comment_start_expression = QRegularExpression(r"/\*")
        self.comment_end_expression = QRegularExpression(r"\*/")

    def highlightBlock(self, text: str):
        # Apply single-line rules first
        for pattern, fmt in self.highlighting_rules:
            iterator = pattern.globalMatch(text)
            while iterator.hasNext():
                match = iterator.next()
                self.setFormat(match.capturedStart(), match.capturedLength(), fmt)

        self.setCurrentBlockState(0)
        search_index = 0

        # Elegantly handle continuation from a previous block
        if self.previousBlockState() == 1:
            end_match = self.comment_end_expression.match(text, 0)
            if not end_match.hasMatch():
                # The entire block is a comment, our work is simple and swift.
                self.setCurrentBlockState(1)
                self.setFormat(0, len(text), self.multiline_comment_format)
                return

            # The comment concludes, we find our new starting point.
            length = end_match.capturedEnd()
            self.setFormat(0, length, self.multiline_comment_format)
            search_index = length

        # Now, we seek new comments with a more expressive loop.
        while (start_match := self.comment_start_expression.match(text, search_index)).hasMatch():
            start_pos = start_match.capturedStart()
            end_match = self.comment_end_expression.match(text, start_pos + start_match.capturedLength())

            if not end_match.hasMatch():
                # An unclosed comment, a cliffhanger for the next block.
                self.setCurrentBlockState(1)
                self.setFormat(start_pos, len(text) - start_pos, self.multiline_comment_format)
                return  # Our tale for this block is told.

            # A complete, self-contained comment.
            length = end_match.capturedEnd() - start_pos
            self.setFormat(start_pos, length, self.multiline_comment_format)
            search_index = end_match.capturedEnd()

    def rehighlight(self):
        """Forces a re-highlight of the entire document, usually on theme change."""
        self.initialize_formats_and_rules()
        super().rehighlight()
```

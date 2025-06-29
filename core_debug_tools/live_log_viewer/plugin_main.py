# PuffinPyEditor/core_debug_tools/live_log_viewer/plugin_main.py
import subprocess
import sys
from typing import TYPE_CHECKING
from utils.logger import log, LOG_FILE
from utils.helpers import get_base_path
import os

if TYPE_CHECKING:
    from app_core.puffin_api import PuffinPluginAPI
    from ui.main_window import MainWindow

# This script is intended to be in the project's root for execution.
# Adjust the path if this file is moved.
LOG_VIEWER_SCRIPT_PATH = os.path.join(
    get_base_path(), "utils", "log_viewer.py"
)


class LiveLogViewerPlugin:
    """
    A simple plugin to launch a standalone log viewer process.
    """

    def __init__(self, main_window: 'MainWindow'):
        self.main_window = main_window
        self.log_viewer_window = None
        self.log_file = LOG_FILE
        self.action = None

    def add_menu_action(self, puffin_api: 'PuffinPluginAPI'):
        """Adds the 'Live Log Viewer' action to the Tools menu."""
        self.action = puffin_api.add_menu_action(
            menu_name="tools",
            text="Live Log Viewer",
            callback=self.launch_log_viewer,
            shortcut="Ctrl+Shift+L",
            icon_name="fa5s.bug"
        )
        self.action.setToolTip(
            "Open a real-time viewer for the application log.")
        log.info("Live Log Viewer action added to Tools menu.")

    def launch_on_startup(self):
        """Public method to launch the viewer, intended for debug mode."""
        log.info("Launching log viewer on startup due to debug mode.")
        self.launch_log_viewer()

    def launch_log_viewer(self):
        """
        Launches the log_viewer.py script in a new process, passing the
        current Python interpreter and the log file path.
        """
        try:
            # We must use sys.executable to ensure the new process runs with
            # the same Python environment (and PyQt6 version) as the main app.
            python_executable = sys.executable
            command = [python_executable, LOG_VIEWER_SCRIPT_PATH,
                       self.log_file]

            log.info(f"Executing command: {' '.join(command)}")

            # Use Popen to launch it as a completely independent process.
            # This ensures it survives if the main app crashes.
            subprocess.Popen(command)

        except Exception as e:
            log.error(f"Failed to launch log viewer: {e}", exc_info=True)

    def shutdown(self):
        """Called when the plugin is unloaded."""
        # The log viewer is a separate process, so there's nothing to clean up
        # in the main application's memory here. The QAction will be destroyed
        # with the menu.
        log.info("Live Log Viewer plugin is shutting down.")


def initialize(puffin_api: 'PuffinPluginAPI'):
    """Initializes the plugin."""
    main_window = puffin_api.get_main_window()
    plugin_instance = LiveLogViewerPlugin(main_window)
    plugin_instance.add_menu_action(puffin_api)
    return plugin_instance
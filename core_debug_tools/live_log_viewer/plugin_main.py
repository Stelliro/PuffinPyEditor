# PuffinPyEditor/core_debug_tools/live_log_viewer/plugin_main.py
import os
import sys
import subprocess
from utils.logger import log, LOG_FILE
from utils.helpers import get_base_path


class LiveLogViewerPlugin:
    def __init__(self, main_window):
        self.main_window = main_window
        self.puffin_api = main_window.puffin_api
        self.debug_api = getattr(self.main_window, 'debug_api', None)

        if not self.debug_api:
            log.error("Live Log Viewer requires the Debug Framework, "
                      "but it was not found.")
            return

        # Add the action to the menu for manual launching if needed
        self.puffin_api.add_menu_action(
            menu_name="debug",
            text="Launch Live Log Viewer",
            callback=self.launch_viewer,
            icon_name="fa5s.file-medical-alt"
        )
        log.info("Live Log Viewer plugin initialized and action added to Debug menu.")

    def launch_on_startup(self):
        """A safe method to be called after the main window is up and running."""
        log.info("Log viewer startup launch triggered.")
        self.launch_viewer()

    def _find_viewer_executable(self) -> str:
        """Determines the path to the log_viewer executable or script."""
        base_dir = get_base_path()  # Use the robust helper
        if getattr(sys, 'frozen', False):
            # In a bundled app, look for the compiled executable.
            return os.path.join(base_dir, "log_viewer.exe")
        else:
            # In development, find the script in the utils directory
            return os.path.join(base_dir, "utils", "log_viewer.py")

    def launch_viewer(self):
        """Finds and launches the log_viewer as a separate process."""
        viewer_path = self._find_viewer_executable()

        try:
            if not os.path.exists(viewer_path):
                msg = (f"Could not find log_viewer at the expected path:\n'{viewer_path}'\n\n"
                       "If running from source, ensure `utils/log_viewer.py` exists.\n"
                       "If running a built version, ensure `log_viewer.exe` is in the "
                       "same directory as the main application.")
                self.puffin_api.show_message("critical", "Viewer Not Found", msg)
                return

            command = []
            if getattr(sys, 'frozen', False):
                # Just run the executable directly in a bundled app.
                command = [viewer_path, LOG_FILE]
            else:
                # Run with the same Python interpreter in development.
                command = [sys.executable, viewer_path, LOG_FILE]

            # Launch the viewer as a fully independent process.
            subprocess.Popen(command)
            log.info(f"Launched Live Log Viewer for file: {LOG_FILE}")

        except Exception as e:
            log.error(f"Failed to launch log viewer: {e}", exc_info=True)
            self.puffin_api.show_message(
                "critical", "Launch Failed", "An unexpected error occurred while trying "
                                             f"to launch the log viewer: {e}")


def initialize(main_window):
    """Entry point for the live log viewer plugin."""
    return LiveLogViewerPlugin(main_window)
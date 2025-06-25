# PuffinPyEditor/core_debug_tools/live_log_viewer/plugin_main.py
import os
import sys
import subprocess
from utils.logger import log, LOG_FILE


class LiveLogViewerPlugin:
    def __init__(self, main_window):
        self.main_window = main_window
        self.puffin_api = main_window.puffin_api
        self.debug_api = getattr(self.main_window, 'debug_api', None)

        if not self.debug_api:
            log.error("Live Log Viewer requires the Debug Framework, but it was not found.")
            return

        self.puffin_api.add_menu_action(
            menu_name="debug",
            text="Launch Live Log Viewer",
            callback=self.launch_viewer,
            icon_name="fa5s.file-medical-alt"
        )

    def launch_viewer(self):
        """Finds and launches the log_viewer.exe as a separate process."""
        try:
            if getattr(sys, 'frozen', False):
                # In a bundled app, log_viewer.exe is a sibling to main exe
                base_dir = os.path.dirname(sys.executable)
                viewer_exe = os.path.join(base_dir, "log_viewer.exe")
            else:
                # In development, check the `dist` directory first, assuming it has been built.
                # This makes the dev workflow smoother.
                project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
                viewer_exe = os.path.join(project_root, "dist", "log_viewer", "log_viewer.exe")

            if not os.path.exists(viewer_exe):
                self.puffin_api.show_message(
                    "critical", "Viewer Not Found",
                    f"Could not find log_viewer.exe at '{viewer_exe}'.\n\n"
                    "Please run the build script (installer/build.bat) first to compile the debug tools."
                )
                return

            # Launch the viewer as a fully independent process
            # Pass the log file path as a command-line argument
            subprocess.Popen([viewer_exe, LOG_FILE])
            log.info(f"Launched Live Log Viewer for file: {LOG_FILE}")

        except Exception as e:
            log.error(f"Failed to launch log viewer: {e}", exc_info=True)
            self.puffin_api.show_message("critical", "Launch Failed", f"Error launching log viewer: {e}")


def initialize(main_window):
    """Entry point for the live log viewer plugin."""
    return LiveLogViewerPlugin(main_window)
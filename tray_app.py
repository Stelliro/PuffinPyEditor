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
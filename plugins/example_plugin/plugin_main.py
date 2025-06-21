from PyQt6.QtGui import QAction
from utils.logger import log

class ExamplePlugin:
    def __init__(self, main_window):
        self.main_window = main_window
        self.menu_action = None

    def activate(self):
        """Adds a new item to the Tools menu."""
        if hasattr(self.main_window, 'tools_menu'):
            self.menu_action = QAction("Log Message from Example Plugin", self.main_window)
            self.menu_action.triggered.connect(self._log_message)
            self.main_window.tools_menu.addAction(self.menu_action)
            log.info("Example Plugin: Menu item added.")
        else:
            log.error("ExamplePlugin could not find 'tools_menu' in MainWindow.")

    def _log_message(self):
        log.info("Hello from the PuffinPyEditor Example Plugin!")
        self.main_window.statusBar().showMessage("Logged a message from the example plugin.", 3000)


def initialize(main_window):
    """Entry point for PuffinPyEditor to initialize the plugin."""
    plugin_instance = ExamplePlugin(main_window)
    plugin_instance.activate()
    return plugin_instance
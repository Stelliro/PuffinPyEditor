# /plugins/installer_builder/plugin_main.py
from app_core.puffin_api import PuffinPluginAPI
from .builder_dialog import BuilderDialog
from utils.logger import log

class InstallerBuilderPlugin:
    def __init__(self, puffin_api: PuffinPluginAPI):
        self.api = puffin_api
        self.main_window = self.api.get_main_window()
        self.dialog_instance = None

        # Add "Build Installer..." to the "Tools" menu
        self.api.add_menu_action(
            menu_name="tools",
            text="Build Installer...",
            callback=self.show_builder_dialog,
            icon_name="fa5s.cogs"
        )
        log.info("Installer Builder Plugin initialized.")

    def show_builder_dialog(self):
        """Creates and shows the installer builder dialog."""
        # Check if the dialog exists and if its parent is still valid
        # This prevents trying to show a dialog that has been closed and deleted.
        if self.dialog_instance is None or not self.dialog_instance.parent():
            self.dialog_instance = BuilderDialog(self.api, self.main_window)
        
        self.dialog_instance.show()
        self.dialog_instance.raise_()
        self.dialog_instance.activateWindow()

def initialize(puffin_api: PuffinPluginAPI):
    """Entry point for PuffinPyEditor to load the plugin."""
    return InstallerBuilderPlugin(puffin_api)
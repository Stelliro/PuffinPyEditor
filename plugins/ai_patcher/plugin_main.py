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
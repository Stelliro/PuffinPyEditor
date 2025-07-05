# /plugins/ai_patcher/plugin_main.py
from app_core.puffin_api import PuffinPluginAPI
from .patcher_dialog import AIPatcherDialog
from utils.logger import log


class AIPatcherPlugin:
    """
    A plugin to generate prompts for an AI to create code patches, and then
    apply those patches back to the local project files.
    """

    def __init__(self, puffin_api: PuffinPluginAPI):
        self.api = puffin_api
        self.main_window = self.api.get_main_window()
        self.dialog_instance = None

        self.api.add_menu_action(
            menu_name="tools",
            text="AI Patcher...",
            callback=self.show_patcher_dialog,
            icon_name="fa5s.magic"
        )
        log.info("AI Patcher plugin initialized.")

    def show_patcher_dialog(self):
        """Shows the main dialog for the AI Patcher tool."""
        project_manager = self.api.get_manager("project")
        if not project_manager.get_active_project_path():
            self.api.show_message("info", "No Project Open", "Please open a project to use the AI Patcher.")
            return

        # Use a lazy-loaded dialog instance
        if self.dialog_instance is None or not self.dialog_instance.isVisible():
            self.dialog_instance = AIPatcherDialog(self.api, self.main_window)

        self.dialog_instance.show()
        self.dialog_instance.raise_()
        self.dialog_instance.activateWindow()


def initialize(puffin_api: PuffinPluginAPI):
    """Entry point for the AI Patcher plugin."""
    return AIPatcherPlugin(puffin_api)
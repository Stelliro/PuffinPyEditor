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
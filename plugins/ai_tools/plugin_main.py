# PuffinPyEditor/plugins/ai_tools/plugin_main.py
from .ai_export_dialog import AIExportDialog
from app_core.puffin_api import PuffinPluginAPI


class AIToolsPlugin:
    def __init__(self, puffin_api: PuffinPluginAPI):
        self.api = puffin_api
        self.api.add_menu_action(
            menu_name="tools",
            text="Export Project for AI...",
            callback=self.show_export_dialog,
            icon_name="fa5s.robot"
        )

    def show_export_dialog(self):
        project_manager = self.api.get_manager("project")
        project_path = project_manager.get_active_project_path()
        if not project_path:
            self.api.show_message("info", "No Project Open", "Please open a project to use the AI Export tool.")
            return

        linter_manager = self.api.get_manager("linter")
        dialog = AIExportDialog(project_path, project_manager, linter_manager, self.api.get_main_window())
        dialog.exec()


def initialize(puffin_api: PuffinPluginAPI):
    return AIToolsPlugin(puffin_api)
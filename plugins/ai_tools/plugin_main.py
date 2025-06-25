# PuffinPyEditor/plugins/ai_tools/plugin_main.py
from ai_export_dialog import AIExportDialog

class AIToolsPlugin:
    def __init__(self, main_window):
        self.api = main_window.puffin_api
        self.api.add_menu_action(
            menu_name="tools",
            text="Export Project for AI...",
            callback=self.show_export_dialog,
            icon_name="fa5s.robot"
        )

    def show_export_dialog(self):
        project_path = self.api.get_manager("project").get_active_project_path()
        if not project_path:
            self.api.show_message("info", "No Project Open", "Please open a project to use the AI Export tool.")
            return

        dialog = AIExportDialog(
            project_path,
            self.api.get_manager("project"),
            self.api.get_manager("linter"),
            self.api.get_main_window()
        )
        dialog.exec()

def initialize(main_window):
    return AIToolsPlugin(main_window)
# PuffinPyEditor/plugins/api_keys_manager/plugin_main.py
from .api_keys_settings_page import ApiKeysDialog


class ApiKeysManagerPlugin:
    def __init__(self, main_window):
        self.api = main_window.puffin_api
        self.settings_manager = self.api.get_manager("settings")
        self.main_window = self.api.get_main_window()

        self.api.add_menu_action(
            menu_name="tools",
            text="Manage API Keys...",
            callback=self.show_api_keys_dialog,
            icon_name="fa5s.key"
        )

    def show_api_keys_dialog(self):
        """Create and show the API keys management dialog."""
        dialog = ApiKeysDialog(self.settings_manager, self.main_window)
        dialog.exec()


def initialize(main_window):
    return ApiKeysManagerPlugin(main_window)
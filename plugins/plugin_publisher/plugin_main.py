# PuffinPyEditor/plugins/plugin_publisher/plugin_main.py
from app_core.puffin_api import PuffinPluginAPI
from .publish_dialog import PublishDialog
from utils.logger import log

class PluginPublisherPlugin:
    def __init__(self, puffin_api: PuffinPluginAPI):
        self.api = puffin_api
        self.publish_dialog = None
        self.publish_action = self.api.add_menu_action(
            menu_name="tools",
            text="Publish Plugin...",
            callback=self.show_publish_dialog,
            icon_name="fa5s.cloud-upload-alt"
        )
        self.update_action_state()
        github_manager = self.api.get_manager("github")
        if github_manager:
            github_manager.auth_successful.connect(lambda user: self.update_action_state())
            github_manager.auth_failed.connect(lambda err: self.update_action_state())

    def shutdown(self):
        if self.publish_action:
            # Use a safer way to get the menu
            if hasattr(self.api.get_main_window(), 'tools_menu'):
                 self.api.get_main_window().tools_menu.removeAction(self.publish_action)
            self.publish_action.deleteLater()
        log.info("Plugin Publisher shutdown complete.")

    def show_publish_dialog(self):
        github_manager = self.api.get_manager("github")
        if not (github_manager and github_manager.get_authenticated_user()):
            self.api.show_message("warning", "Login Required", "You must be logged into GitHub to publish a plugin.")
            return

        if self.publish_dialog is None or not self.publish_dialog.isVisible():
            self.publish_dialog = PublishDialog(self.api, self.api.get_main_window())
        self.publish_dialog.show()
        self.publish_dialog.raise_()
        self.publish_dialog.activateWindow()

    def update_action_state(self):
        github_manager = self.api.get_manager("github")
        is_logged_in = bool(github_manager and github_manager.get_authenticated_user())
        self.publish_action.setEnabled(is_logged_in)
        self.publish_action.setToolTip("Upload a plugin." if is_logged_in else "Log in to GitHub to use.")

def initialize(puffin_api: PuffinPluginAPI):
    return PluginPublisherPlugin(puffin_api)
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
            # Connect to a method that can be disconnected reliably
            github_manager.auth_successful.connect(self._on_auth_state_changed)
            github_manager.auth_failed.connect(self._on_auth_state_changed)

    def shutdown(self):
        # Disconnect signals to prevent calls to a deleted object
        github_manager = self.api.get_manager("github")
        if github_manager:
            try:
                github_manager.auth_successful.disconnect(self._on_auth_state_changed)
                github_manager.auth_failed.disconnect(self._on_auth_state_changed)
            except (TypeError, RuntimeError):
                # This can happen if the connection was already broken.
                # It's safe to ignore.
                pass

        if self.publish_action:
            # Use a safer way to get the menu
            if hasattr(self.api.get_main_window(), 'tools_menu'):
                 self.api.get_main_window().tools_menu.removeAction(self.publish_action)
            self.publish_action.deleteLater()
            # Nullify the reference to prevent further access
            self.publish_action = None
        log.info("Plugin Publisher shutdown complete.")

    def _on_auth_state_changed(self, *args, **kwargs):
        """
        Slot to handle authentication state changes. This will call the UI
        update method.
        """
        self.update_action_state()

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
        # Add a guard to ensure the action exists before modification.
        if not self.publish_action:
            return
            
        github_manager = self.api.get_manager("github")
        is_logged_in = bool(github_manager and github_manager.get_authenticated_user())
        self.publish_action.setEnabled(is_logged_in)
        self.publish_action.setToolTip("Upload a plugin." if is_logged_in else "Log in to GitHub to use.")

def initialize(puffin_api: PuffinPluginAPI):
    return PluginPublisherPlugin(puffin_api)
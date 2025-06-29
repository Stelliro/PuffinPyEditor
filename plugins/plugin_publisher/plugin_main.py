# PuffinPyEditor/plugins/plugin_publisher/plugin_main.py
from .publish_dialog import PublishDialog


class PluginPublisherPlugin:
    """
    Integrates the plugin publishing tool into the main application UI.
    """

    def __init__(self, main_window):
        self.main_window = main_window
        self.api = main_window.puffin_api
        self.publish_dialog = None

        # Add the action to the "Tools" menu
        self.publish_action = self.api.add_menu_action(
            menu_name="tools",
            text="Publish Plugin...",
            callback=self.show_publish_dialog,
            icon_name="fa5s.cloud-upload-alt"
        )
        self.update_action_state()

        # Connect to the github manager's auth signal to update action state
        github_manager = self.api.get_manager("github")
        github_manager.auth_successful.connect(
            lambda user: self.update_action_state())
        github_manager.auth_failed.connect(
            lambda err: self.update_action_state())

    def show_publish_dialog(self):
        """
        Checks for authentication and then shows the publishing dialog.
        """
        github_manager = self.api.get_manager("github")
        if not github_manager or not github_manager.get_authenticated_user():
            self.api.show_message(
                "warning",
                "Login Required",
                "You must be logged into GitHub to publish a plugin. "
                "Please log in via Preferences > Source Control."
            )
            return

        # Lazily create the dialog instance
        if self.publish_dialog is None or not self.publish_dialog.isVisible():
            self.publish_dialog = PublishDialog(self.api, self.main_window)
            self.publish_dialog.show()
        else:
            self.publish_dialog.raise_()
            self.publish_dialog.activateWindow()

    def update_action_state(self):
        """
        Enables or disables the menu action based on GitHub login status.
        """
        github_manager = self.api.get_manager("github")
        if github_manager:
            is_logged_in = bool(github_manager.get_authenticated_user())
            self.publish_action.setEnabled(is_logged_in)
            tooltip = ("Upload an installed plugin to your distribution repo."
                       if is_logged_in else
                       "Log in to GitHub in Preferences to use this feature.")
            self.publish_action.setToolTip(tooltip)


def initialize(main_window):
    """Entry point for PuffinPyEditor to initialize the plugin."""
    return PluginPublisherPlugin(main_window)
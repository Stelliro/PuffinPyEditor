# /plugins/refactor_tool/plugin_main.py

from app_core.puffin_api import PuffinPluginAPI
from .refactor_dialog import RefactorDialog
from utils.logger import log


class RefactorPlugin:
    def __init__(self, puffin_api: PuffinPluginAPI):
        self.api = puffin_api
        self.main_window = self.api.get_main_window()
        self.dialog = None

        # Create a new top-level "Refactor" menu
        self.refactor_menu = self.api.get_main_window().menuBar().addMenu("&Refactor")
        
        # Add the "Rename Symbol" action to it
        self.rename_action = self.api.add_menu_action(
            menu_name="refactor",
            text="Rename Symbol...",
            callback=self.show_refactor_dialog,
            shortcut="F2",
            icon_name="mdi.pencil-box-outline"
        )
        self.refactor_menu.addAction(self.rename_action)

    def show_refactor_dialog(self):
        """Shows the refactoring dialog."""
        current_widget = self.main_window.tab_widget.currentWidget()
        if not hasattr(current_widget, 'text_area'):
            self.api.show_message("info", "No Editor Active",
                                  "Please open a file and select an identifier to refactor.")
            return
            
        self.dialog = RefactorDialog(self.api, self.main_window)
        self.dialog.exec()

    def shutdown(self):
        if self.refactor_menu:
            self.refactor_menu.clear()
            self.refactor_menu.deleteLater()
            
        log.info("Refactor Plugin shut down.")


def initialize(puffin_api: PuffinPluginAPI):
    """Entry point for the Refactor Plugin."""
    return RefactorPlugin(puffin_api)
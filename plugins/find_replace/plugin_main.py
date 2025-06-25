# PuffinPyEditor/plugins/find_replace/plugin_main.py
from search_replace_dialog import SearchReplaceDialog  # CORRECTED: Removed the leading '.'
from ui.editor_widget import EditorWidget


class FindReplacePlugin:
    def __init__(self, main_window):
        self.main_window = main_window
        self.api = main_window.puffin_api
        self.search_dialog = None
        # Use the API to create the action and add it to the menu and toolbar
        self.find_action = self.api.add_menu_action("edit", "&Find/Replace...", self.show_dialog, "Ctrl+F",
                                                    "fa5s.search")
        self.api.add_toolbar_action(self.find_action)
        self.find_action.setEnabled(False)  # Start disabled

    def show_dialog(self):
        current_tab = self.main_window.tab_widget.currentWidget()
        if not isinstance(current_tab, EditorWidget):
            self.api.show_status_message("No editor open to search in.", 2000)
            return

        # Lazy initialization of the dialog
        if not self.search_dialog:
            self.search_dialog = SearchReplaceDialog(self.main_window)

        self.search_dialog.show_dialog(current_tab)

    def on_tab_changed(self, index):
        # Enable/disable the action based on whether the current tab is an editor
        is_editor = isinstance(self.main_window.tab_widget.widget(index), EditorWidget)
        self.find_action.setEnabled(is_editor)


def initialize(main_window):
    """Entry point for the Find/Replace plugin."""
    plugin_instance = FindReplacePlugin(main_window)
    # Connect to the main tab widget's signal to update the action's state
    main_window.tab_widget.currentChanged.connect(plugin_instance.on_tab_changed)
    # Ensure initial state is correct for the tab open at startup
    plugin_instance.on_tab_changed(main_window.tab_widget.currentIndex())
    return plugin_instance
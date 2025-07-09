# PuffinPyEditor/plugins/ai_patcher/plugin_main.py
import qtawesome as qta
from PyQt6.QtWidgets import QMenu, QMessageBox
from PyQt6.QtGui import QAction
from app_core.puffin_api import PuffinPluginAPI
from utils.helpers import clean_git_conflict_markers
from app_core.settings_manager import settings_manager
from utils.logger import log


class AiPatcherPlugin:
    def __init__(self, api: PuffinPluginAPI):
        self.api = api
        self.main_window = self.api.get_main_window()
        self._add_context_menu_action()

    def _add_context_menu_action(self):
        """Adds 'Clean Git Conflict Markers' to the file explorer context menu."""
        if hasattr(self.main_window, 'explorer_panel'):
            # This relies on the context menu being dynamically built,
            # so we just add our action to the menu builder function.
            original_menu_builder = self.main_window.explorer_panel.show_context_menu

            def extended_menu_builder(position):
                # Call original builder first to get the standard menu
                menu = original_menu_builder(position)

                # Add our custom action
                item = self.main_window.explorer_panel.tree_widget.itemAt(position)
                if item:
                    data = item.data(0, self.api.constants.UserRole)
                    if data and not data.get('is_dir'):
                        menu.addSeparator()
                        clean_action = QAction(qta.icon('mdi.auto-fix'), "Clean Git Conflict Markers", menu)
                        clean_action.triggered.connect(lambda: self.clean_file(data.get('path')))
                        menu.addAction(clean_action)

                menu.exec(self.main_window.explorer_panel.tree_widget.mapToGlobal(position))

            # Replace the original function with our extended one
            self.main_window.explorer_panel.show_context_menu = extended_menu_builder
            log.info("AI Patcher: Hooked into file explorer context menu.")

    def clean_file(self, filepath):
        """Reads a file, cleans it, and writes it back."""
        try:
            with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
                original_content = f.read()

            cleaned_content = clean_git_conflict_markers(original_content)

            if original_content == cleaned_content:
                self.api.show_message("info", "No Conflicts Found",
                                      f"The file '{os.path.basename(filepath)}' contains no standard Git conflict markers.")
                return

            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(cleaned_content)

            self.api.show_message("info", "Success",
                                  f"Successfully cleaned Git conflict markers from '{os.path.basename(filepath)}'.")

            # If the file is open, reload its content in the editor
            for i in range(self.main_window.tab_widget.count()):
                widget = self.main_window.tab_widget.widget(i)
                if hasattr(widget, 'filepath') and os.path.normpath(widget.filepath) == os.path.normpath(filepath):
                    widget.set_text(cleaned_content)
                    widget.original_hash = hash(cleaned_content)  # Reset modification status
                    self.main_window._on_content_changed(widget)
                    break

        except Exception as e:
            log.error(f"Failed to clean file {filepath}: {e}", exc_info=True)
            self.api.show_message("critical", "Error", f"An error occurred while cleaning the file:\n{e}")


def initialize(puffin_api: PuffinPluginAPI):
    """Entry point for the plugin."""
    return AiPatcherPlugin(puffin_api)
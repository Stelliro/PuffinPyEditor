# PuffinPyEditor/plugins/find_replace/plugin_main.py
from PyQt6.QtGui import QAction
from .find_panel import FindPanel
from ui.editor_widget import EditorWidget
import qtawesome as qta


class FindReplacePlugin:
    def __init__(self, main_window):
        self.main_window = main_window
        self.api = main_window.puffin_api
        
        # Action with shortcut, added to both menu and toolbar
        self.find_action = self.api.add_menu_action(
            "edit", "&Find/Replace...", self.toggle_find_panel, "Ctrl+F", "fa5s.search"
        )
        # Add a dedicated instance of the action to the toolbar
        toolbar_find_action = QAction(qta.icon('fa5s.search'), "Find/Replace", self.main_window)
        toolbar_find_action.setToolTip("Find/Replace (Ctrl+F)")
        toolbar_find_action.triggered.connect(self.toggle_find_panel)
        
        prefs_action = self.main_window.actions.get("preferences")
        if prefs_action:
            self.main_window.main_toolbar.insertAction(prefs_action, toolbar_find_action)
        else:
            self.api.add_toolbar_action(toolbar_find_action)
        
        self.find_action.setEnabled(False)
        toolbar_find_action.setEnabled(False) # Keep them in sync
        self.toolbar_find_action = toolbar_find_action
        
        self.find_panel = None

        # Connect signals
        self.main_window.tab_widget.currentChanged.connect(self._on_tab_changed)
        
        # Initial check
        self._on_tab_changed(self.main_window.tab_widget.currentIndex())

    def _ensure_panel_exists(self):
        """Creates the panel instance on-demand."""
        if self.find_panel is None:
            self.find_panel = FindPanel(self.main_window)
            self.find_panel.status_message_requested.connect(self.api.show_status_message)
            self.find_panel.close_requested.connect(self.handle_panel_close)
            self.find_panel.hide()

    def toggle_find_panel(self):
        editor = self.main_window.tab_widget.currentWidget()
        if not isinstance(editor, EditorWidget):
            return
            
        self._ensure_panel_exists()

        if self.find_panel.isVisible():
            self.handle_panel_close()
        else:
            # Attach the panel to the current editor
            self.find_panel.setParent(editor)
            editor.main_layout.insertWidget(0, self.find_panel)
            self.find_panel.connect_editor(editor)
            self.find_panel.show()

    def handle_panel_close(self):
        """Hides the panel and returns focus to the editor."""
        if self.find_panel:
            editor_to_focus = self.find_panel.editor
            self.find_panel.hide()
            self.find_panel.setParent(None) # Detach from editor
            if editor_to_focus:
                editor_to_focus.text_area.setFocus()

    def _on_tab_changed(self, index: int):
        widget = self.main_window.tab_widget.widget(index)
        is_editor = isinstance(widget, EditorWidget)
        self.find_action.setEnabled(is_editor)
        self.toolbar_find_action.setEnabled(is_editor)

        # Always hide the panel when switching tabs
        if self.find_panel and self.find_panel.isVisible():
            self.handle_panel_close()


def initialize(main_window):
    """Entry point for the Find/Replace plugin."""
    return FindReplacePlugin(main_window)
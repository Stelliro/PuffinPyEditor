# /plugins/find_replace/plugin_main.py
from PyQt6.QtGui import QAction
import qtawesome as qta
from utils.logger import log


class FindReplacePlugin:
    """
    Manages the Find/Replace panel and its integration with the main UI.
    """

    def __init__(self, puffin_api):
        # I'm using a deferred import here. It's a good pattern to avoid
        # potential startup race conditions or import cycles.
        from ui.editor_widget import EditorWidget
        self.EditorWidgetClass = EditorWidget

        self.api = puffin_api
        self.main_window = self.api.get_main_window()

        self.find_action = self.api.add_menu_action(
            menu_name="edit",
            text="&Find/Replace...",
            callback=self.toggle_find_panel,
            shortcut="Ctrl+F",
            icon_name="fa5s.search"
        )
        self.toolbar_find_action = QAction(qta.icon('fa5s.search'), "Find/Replace", self.main_window)
        self.toolbar_find_action.setToolTip("Find/Replace (Ctrl+F)")
        self.toolbar_find_action.triggered.connect(self.toggle_find_panel)

        self.main_toolbar = getattr(self.main_window, 'main_toolbar', None)
        if self.main_toolbar and (prefs_action := self.main_window.actions.get("preferences")):
            self.main_toolbar.insertAction(prefs_action, self.toolbar_find_action)
        else:
            self.api.add_toolbar_action(self.toolbar_find_action)

        self.find_action.setEnabled(False)
        self.toolbar_find_action.setEnabled(False)

        # We no longer need to create a FindPanel instance here. The editor does it!
        self.main_window.tab_widget.currentChanged.connect(self._on_tab_changed)
        self._on_tab_changed(self.main_window.tab_widget.currentIndex())
        log.info("Find/Replace plugin initialized and actions created.")

    def shutdown(self):
        log.info("Shutting down Find/Replace plugin...")
        try:
            self.main_window.tab_widget.currentChanged.disconnect(self._on_tab_changed)
        except TypeError:
            pass
        if self.find_action and self.find_action.menu(): self.find_action.menu().removeAction(self.find_action)
        if self.main_toolbar and self.toolbar_find_action: self.main_toolbar.removeAction(self.toolbar_find_action)
        if self.find_action: self.find_action.deleteLater()
        if self.toolbar_find_action: self.toolbar_find_action.deleteLater()
        log.info("Find/Replace plugin shut down successfully.")

    def toggle_find_panel(self):
        # This logic is so much cleaner now!
        editor = self.main_window.tab_widget.currentWidget()
        if not isinstance(editor, self.EditorWidgetClass):
            log.warning("Find/Replace called on a non-editor widget.")
            return

        # We just ask the editor to toggle its own panel.
        if editor.find_panel.isVisible():
            editor.hide_find_panel()
        else:
            editor.show_find_panel()

    def _on_tab_changed(self, index: int):
        widget = self.main_window.tab_widget.widget(index)
        is_editor = isinstance(widget, self.EditorWidgetClass)
        self.find_action.setEnabled(is_editor)
        self.toolbar_find_action.setEnabled(is_editor)

        # When we switch away from an editor tab, we should ensure the
        # find panel of the old editor gets hidden.
        if not is_editor:
            for i in range(self.main_window.tab_widget.count()):
                if w := self.main_window.tab_widget.widget(i):
                    if isinstance(w, self.EditorWidgetClass) and w.find_panel.isVisible():
                        w.hide_find_panel()


def initialize(puffin_api):
    return FindReplacePlugin(puffin_api)
# PuffinPyEditor/plugins/tab_drag_handler/plugin_main.py
from .draggable_tab_widget import DraggableTabWidget
from utils.logger import log


class TabDragHandlerPlugin:
    def __init__(self, main_window):
        api = main_window.puffin_api
        mw = api.get_main_window()

        # Find the original QTabWidget and its place in the layout
        old_tab_widget = mw.tab_widget
        parent_layout = old_tab_widget.parent().layout()
        if not parent_layout:
            log.error("TabDragHandler: Could not find parent layout of tab_widget.")
            return
            
        # Create an instance of our new draggable widget
        new_tab_widget = DraggableTabWidget(mw)

        # Transfer all existing tabs from the old widget to the new one
        while old_tab_widget.count() > 0:
            widget = old_tab_widget.widget(0)
            text = old_tab_widget.tabText(0)
            icon = old_tab_widget.tabIcon(0)
            tooltip = old_tab_widget.tabToolTip(0)
            old_tab_widget.removeTab(0)
            new_tab_widget.addTab(widget, icon, text)
            new_tab_widget.setTabToolTip(new_tab_widget.count() - 1, tooltip)
        
        # Copy over essential properties
        new_tab_widget.setDocumentMode(old_tab_widget.documentMode())
        new_tab_widget.setTabsClosable(old_tab_widget.tabsClosable())
        new_tab_widget.setMovable(True) # Our new one is always movable

        # Re-connect signals that the main window relies on
        new_tab_widget.currentChanged.connect(mw._on_tab_changed)
        new_tab_widget.tabCloseRequested.connect(mw._action_close_tab_by_index)

        # Replace the widget in the layout
        parent_layout.replaceWidget(old_tab_widget, new_tab_widget)
        old_tab_widget.deleteLater()  # Safely delete the old widget
        
        # Crucially, update the main window's reference to point to our new widget
        mw.tab_widget = new_tab_widget

        log.info("TabDragHandler: Upgraded main QTabWidget to DraggableTabWidget.")


def initialize(main_window):
    """Entry point for the TabDragHandler plugin."""
    try:
        return TabDragHandlerPlugin(main_window)
    except Exception as e:
        log.error(f"Failed to initialize TabDragHandlerPlugin: {e}", exc_info=True)
        return None
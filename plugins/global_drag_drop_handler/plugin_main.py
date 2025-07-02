# PuffinPyEditor/plugins/global_drag_drop_handler/plugin_main.py
import os
from PyQt6.QtCore import QObject, QEvent
from utils.logger import log
from app_core.puffin_api import PuffinPluginAPI


class GlobalDragDropHandlerPlugin(QObject):
    """
    A plugin that installs an event filter on the main window to handle
    files being dragged and dropped from the operating system.
    """

    # This is the constructor for our class. It's called when a new
    # instance of the plugin is created by the PluginManager.
    # It now correctly accepts the 'puffin_api' object!
    def __init__(self, puffin_api: PuffinPluginAPI):
        # We need the API to get a reference to the main window.
        self.api = puffin_api
        self.main_window = self.api.get_main_window()

        # We must initialize the QObject base class and give it a parent
        # so that it's managed correctly by Qt's memory model.
        # I'm doing this AFTER setting our other properties, just to be safe.
        super().__init__(self.main_window)

        # installEventFilter tells the main window to send all its events
        # (like mouse clicks, key presses, and drags) to our 'eventFilter'
        # method below for inspection. It's a powerful tool!
        self.main_window.installEventFilter(self)
        self.main_window.setAcceptDrops(True)  # We must explicitly enable drops on the window.
        log.info("Global Drag and Drop handler installed on main window.")

    def eventFilter(self, obj, event: QEvent) -> bool:
        """
        This method intercepts events from the object it's watching (the main window).
        """
        # First, we make sure we are only filtering events for the main window,
        # not for any of its children.
        if obj is not self.main_window:
            return super().eventFilter(obj, event)

        # This event fires when a drag operation enters the widget's boundaries.
        if event.type() == QEvent.Type.DragEnter:
            # We check if the data being dragged contains file URLs.
            if event.mimeData().hasUrls():
                # By accepting the event, we tell the OS it's okay to drop here,
                # which usually changes the cursor to a 'plus' icon.
                event.acceptProposedAction()
                return True  # True means we've handled this event.

        # This event fires when the user releases the mouse to drop the data.
        if event.type() == QEvent.Type.Drop:
            if event.mimeData().hasUrls():
                files_to_open = []
                for url in event.mimeData().urls():
                    # We only care about local files, not web URLs.
                    if url.isLocalFile():
                        file_path = url.toLocalFile()
                        # We also only want to open files, not directories, with this method.
                        if os.path.isfile(file_path):
                            files_to_open.append(file_path)

                if files_to_open:
                    log.info(f"Accepted drop event for files: {files_to_open}")
                    # Use the main window's existing logic to open the files.
                    for f_path in files_to_open:
                        self.main_window._action_open_file(f_path)

                    event.acceptProposedAction()
                    return True  # Event handled!

        # For all other events we don't care about, we pass them on to the
        # default Qt event handler. This is very important!
        return super().eventFilter(obj, event)


def initialize(puffin_api: PuffinPluginAPI):
    """
    Entry point function for PuffinPyEditor to load the plugin.
    This is called by the PluginManager during startup.
    """
    # A try-except block here is good practice to prevent a faulty
    # plugin from crashing the entire application on startup.
    try:
        # We must return the instance so the plugin manager can hold a reference
        # to it, which prevents it from being garbage collected.
        plugin_instance = GlobalDragDropHandlerPlugin(puffin_api)
        log.info("Global Drag and Drop Plugin initialized successfully.")
        return plugin_instance
    except Exception as e:
        log.error(f"Failed to initialize Global D&D Plugin: {e}", exc_info=True)
        # Returning None tells the plugin manager that loading failed.
        return None
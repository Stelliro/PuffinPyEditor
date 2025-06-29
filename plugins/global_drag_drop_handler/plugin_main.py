# PuffinPyEditor/plugins/global_drag_drop_handler/plugin_main.py
import os
from PyQt6.QtCore import QObject, QEvent
from utils.logger import log


class GlobalDragDropHandlerPlugin(QObject):
    """
    A plugin that installs an event filter on the main window to handle
    files being dragged and dropped from the operating system.
    """
    def __init__(self, main_window):
        # We need the API and the main_window object itself
        self.api = main_window.puffin_api
        self.main_window = self.api.get_main_window()
        
        # Initialize the QObject base class AFTER setting our properties
        super().__init__(self.main_window)

        # Tell the main window to send its events to our eventFilter method
        self.main_window.installEventFilter(self)
        self.main_window.setAcceptDrops(True)  # Explicitly enable drops
        log.info("Global Drag and Drop handler installed on main window.")

    def eventFilter(self, obj, event: QEvent) -> bool:
        """
        This method intercepts events from the object it's watching (the main window).
        """
        # Ensure we are only filtering events for the main_window
        if obj is not self.main_window:
            return super().eventFilter(obj, event)

        if event.type() == QEvent.Type.DragEnter:
            # A drag operation has entered the widget's boundaries.
            # Check if the data being dragged contains file URLs.
            if event.mimeData().hasUrls():
                # Accept the event, which changes the cursor to indicate
                # that a drop is possible.
                event.acceptProposedAction()
                return True  # Event handled

        if event.type() == QEvent.Type.Drop:
            # The user has released the mouse button to drop the data.
            if event.mimeData().hasUrls():
                files_to_open = []
                for url in event.mimeData().urls():
                    if url.isLocalFile():
                        file_path = url.toLocalFile()
                        # We only want to open files, not directories, via this method.
                        if os.path.isfile(file_path):
                            files_to_open.append(file_path)

                if files_to_open:
                    log.info(f"Accepted drop event for files: {files_to_open}")
                    # Use the main window's existing logic to open files
                    for f_path in files_to_open:
                        self.main_window._action_open_file(f_path)
                    
                    event.acceptProposedAction()
                    return True  # Event handled

        # For all other events, pass them on to the default handler.
        return super().eventFilter(obj, event)


def initialize(main_window):
    """
    Entry point function for PuffinPyEditor to load the plugin.
    """
    try:
        # We must return the instance so the plugin manager can hold a reference
        plugin_instance = GlobalDragDropHandlerPlugin(main_window)
        log.info("Global Drag and Drop Plugin initialized successfully.")
        return plugin_instance
    except Exception as e:
        log.error(f"Failed to initialize Global D&D Plugin: {e}", exc_info=True)
        return None
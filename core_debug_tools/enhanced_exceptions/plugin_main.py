# PuffinPyEditor/core_debug_tools/enhanced_exceptions/plugin_main.py
import sys
from utils.logger import log
from .exception_dialog import ExceptionDialog


class EnhancedExceptionsPlugin:
    _instance = None  # To hold the dialog instance

    def __init__(self, main_window, original_hook=None):
        self.main_window = main_window  # Can be None if hooked early
        log.info("Initializing Enhanced Exception Reporter plugin.")
        # Store the original hook for fallback
        self.original_excepthook = original_hook or sys.excepthook
        # Set our handler as the current one
        sys.excepthook = self.show_exception_dialog
        log.info("Global exception hook has been replaced.")

    def show_exception_dialog(self, exc_type, exc_value, exc_tb):
        """The new excepthook function."""
        # Log the exception first, so it's always recorded
        log.critical("Unhandled exception caught by Enhanced Reporter:",
                     exc_info=(exc_type, exc_value, exc_tb))

        # Create and show the dialog.
        dialog = ExceptionDialog(exc_type, exc_value, exc_tb, self.main_window)
        dialog.exec()

        # After the dialog is closed, call the original hook to ensure
        # the application exits as it normally would.
        self.original_excepthook(exc_type, exc_value, exc_tb)


def initialize(main_window, original_hook):
    """Entry point for the Enhanced Exceptions plugin."""
    if EnhancedExceptionsPlugin._instance is None:
        EnhancedExceptionsPlugin._instance = EnhancedExceptionsPlugin(main_window, original_hook)
    return EnhancedExceptionsPlugin._instance
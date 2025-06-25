# PuffinPyEditor/main.py
import sys
import os

# --- Core Imports ---
from PyQt6.QtWidgets import QApplication
from app_core.settings_manager import settings_manager
from app_core.theme_manager import theme_manager
from ui.main_window import MainWindow
from utils.logger import log


def excepthook_handler(exc_type, exc_value, exc_tb):
    """A simple fallback excepthook to log uncaught exceptions."""
    log.critical("--- FALLBACK EXCEPTION HANDLER ---")
    log.critical("An uncaught exception occurred. Details below.",
                 exc_info=(exc_type, exc_value, exc_tb))
    # It's crucial to call the original hook to ensure the app closes.
    if 'original_hook' in locals() and original_hook:
        original_hook(exc_type, exc_value, exc_tb)
    else:
        sys.__excepthook__(exc_type, exc_value, exc_tb)


def main():
    DEBUG_MODE = "--debug" in sys.argv
    # Store the original hook before we potentially replace it.
    original_hook = sys.excepthook

    log.info("=" * 53)
    log.info(f"PuffinPyEditor Application Starting... (Debug: {DEBUG_MODE})")
    log.info(f"Python version: {sys.version.splitlines()[0]}")
    log.info(f"Operating System: {sys.platform}")
    log.info("=" * 53)

    # If in debug mode, set up the enhanced crash reporter immediately.
    # This ensures even pre-GUI startup errors are caught nicely.
    # For non-debug, we let the standard logging handle it.
    if DEBUG_MODE:
        try:
            from core_debug_tools.enhanced_exceptions.plugin_main import EnhancedExceptionsPlugin
            # Pass the original hook to our handler so it can call it after showing the dialog.
            EnhancedExceptionsPlugin(main_window=None, original_hook=original_hook)
            log.info("Enhanced exception reporter enabled for debug mode.")
        except ImportError as e:
            log.warning(f"Could not load enhanced exception handler, using basic logger: {e}")
            sys.excepthook = excepthook_handler

    app = QApplication(sys.argv)
    app.setApplicationName("PuffinPyEditor")
    app.setOrganizationName("PuffinPyEditorProject")

    theme_manager.apply_theme_to_app(app)

    main_window = MainWindow(debug_mode=DEBUG_MODE)
    log.debug("MainWindow instance created.")

    main_window.show()
    log.info("MainWindow shown. Entering main event loop.")

    try:
        exit_code = app.exec()
        log.info(f"Application exited cleanly with code {exit_code}.")
        sys.exit(exit_code)
    except Exception:
        # This will be caught by our custom hook if it was set up.
        log.critical("An unhandled exception occurred during app.exec().", exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
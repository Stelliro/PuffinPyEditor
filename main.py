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
    sys.__excepthook__(exc_type, exc_value, exc_tb)


def main():
    DEBUG_MODE = "--debug" in sys.argv
    sys_excepthook = sys.excepthook  # Keep the original hook

    log.info("=" * 53)
    log.info(f"PuffinPyEditor Application Starting... (Debug: {DEBUG_MODE})")
    log.info(f"Python version: {sys.version.splitlines()[0]}")
    log.info(f"Operating System: {sys.platform}")
    log.info("=" * 53)

    # Set up the enhanced crash reporter for ALL users.
    # It provides immense value for bug reporting from anyone.
    try:
        from core_debug_tools.enhanced_exceptions.plugin_main import EnhancedExceptionsPlugin
        EnhancedExceptionsPlugin(None, original_hook=sys_excepthook)
        log.info("Enhanced exception reporter enabled for all users.")
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
    except Exception as e:
        # This will be caught by our new hook!
        log.critical(f"Exception during app.exec(): {e}", exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
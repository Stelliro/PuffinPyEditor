# PuffinPyEditor/main.py
import sys
import traceback
import os

# --- Initial Dependency Check ---
# This is a user-friendly check for the most critical dependency.
# It provides a clear message if PyQt6 is not installed, which is
# a common issue when running from source for the first time.
try:
    from PyQt6.QtWidgets import QApplication
except ImportError:
    print("---------------------------------------------------------")
    print("FATAL ERROR: The 'PyQt6' library is not installed.")
    print("This is a required dependency for PuffinPyEditor to run.")
    print("\nPlease run the following command in your terminal:")
    print("pip install -r requirements.txt")
    print("---------------------------------------------------------")
    # input("\nPress Enter to exit...") # Optional: uncomment to wait for user input
    sys.exit(1)  # Exit with a non-zero code to indicate an error

# --- Core Imports ---
from app_core.theme_manager import ThemeManager
from app_core.file_handler import FileHandler
from utils.logger import log


def fallback_excepthook(exc_type, exc_value, exc_tb):
    """
    A simple fallback excepthook to log uncaught exceptions.

    This is a safety net in case the more advanced exception handler from the
    debug tools plugin fails to load. It ensures that fatal errors are
    always logged somewhere.
    """
    log.critical("--- FATAL UNHANDLED EXCEPTION ---")
    tb_text = "".join(traceback.format_exception(exc_type, exc_value, exc_tb))
    log.critical(f"Traceback:\n{tb_text}")
    print(f"FATAL ERROR:\n{tb_text}", file=sys.stderr)
    sys.__excepthook__(exc_type, exc_value, exc_tb)


def main():
    sys.excepthook = fallback_excepthook

    DEBUG_MODE = "--debug" in sys.argv

    log.info("=" * 53)
    log.info(f"PuffinPyEditor Application Starting... (Debug: {DEBUG_MODE})")
    log.info(f"Python version: {sys.version.splitlines()[0]}")
    log.info(f"Operating System: {sys.platform}")
    log.info("=" * 53)

    app = QApplication(sys.argv)
    app.setApplicationName("PuffinPyEditor")
    app.setOrganizationName("PuffinPyEditorProject")

    # Instantiate the managers here, after QApplication
    theme_manager = ThemeManager()
    theme_manager.apply_theme_to_app(app)
    file_handler = FileHandler()

    from ui.main_window import MainWindow

    try:
        main_window = MainWindow(file_handler, theme_manager, debug_mode=DEBUG_MODE)
        log.info("MainWindow instance created successfully.")
    except Exception:
        log.critical("A fatal error occurred during MainWindow initialization.")
        raise

    main_window.show()
    log.info("MainWindow shown. Entering main event loop.")
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
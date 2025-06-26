# PuffinPyEditor/main.py
import sys
import traceback

# --- Core Imports ---
from PyQt6.QtWidgets import QApplication
from app_core.theme_manager import theme_manager
from ui.main_window import MainWindow
from utils.logger import log


def fallback_excepthook(exc_type, exc_value, exc_tb):
    """A simple fallback excepthook to log uncaught exceptions if the main handler fails."""
    log.critical("--- FATAL UNHANDLED EXCEPTION ---")
    tb_text = "".join(traceback.format_exception(exc_type, exc_value, exc_tb))
    log.critical(f"Traceback:\n{tb_text}")
    # Also print to stderr for visibility if the log file is not accessible
    print(f"FATAL ERROR:\n{tb_text}", file=sys.stderr)
    sys.__excepthook__(exc_type, exc_value, exc_tb)


def main():
    # Set the fallback hook immediately. It will be replaced by a better one
    # if the application initializes correctly.
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

    theme_manager.apply_theme_to_app(app)

    # Separate initialization from execution for clarity and stability.
    # This is a more robust pattern for starting a PyQt application.
    try:
        main_window = MainWindow(debug_mode=DEBUG_MODE)
        log.info("MainWindow instance created successfully.")
    except Exception:
        # The enhanced exception hook will now properly catch this
        # because we are not swallowing the exception in a simple sys.exit().
        log.critical("A fatal error occurred during MainWindow initialization.")
        # Re-raising the exception ensures it gets passed to the excepthook.
        raise

    main_window.show()
    log.info("MainWindow shown. Entering main event loop.")
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
# PuffinPyEditor/main.py
import sys
import os
from PyQt6.QtWidgets import QApplication

from utils.logger import log, setup_logger

log.info("=====================================================")
log.info("PuffinPyEditor Application Starting...")
log.info(f"Python version: {sys.version.splitlines()[0]}")
log.info(f"Operating System: {sys.platform}")
log.info(f"Current working directory: {os.getcwd()}")
log.info(f"Application path (directory of main.py): {os.path.dirname(os.path.realpath(__file__))}")
log.info("=====================================================")

from app_core.settings_manager import settings_manager
from app_core.theme_manager import theme_manager
from ui.main_window import MainWindow


def excepthook_handler(exc_type, exc_value, exc_tb):
    """Custom excepthook to log uncaught exceptions."""
    log.critical("-----------------------------------------------------")
    log.critical("UNCAUGHT EXCEPTION OCCURRED:")
    log.critical(f"Type: {exc_type.__name__}")
    log.critical(f"Value: {exc_value}")
    log.critical("Traceback details below.", exc_info=(exc_type, exc_value, exc_tb))
    log.critical("-----------------------------------------------------")
    sys.__excepthook__(exc_type, exc_value, exc_tb)


def main():
    sys.excepthook = excepthook_handler
    log.debug("Custom excepthook registered.")

    app = QApplication(sys.argv)
    app.setApplicationName("PuffinPyEditor")
    app.setOrganizationName("PuffinPyEditorProject")
    log.debug("QApplication instance created.")

    theme_manager.apply_theme_to_app(app)
    log.info("Initial application-wide theme applied in main.py.")

    main_window = MainWindow()
    log.debug("MainWindow instance created.")

    main_window.show()
    log.info("MainWindow shown. Entering main event loop.")

    try:
        exit_code = app.exec()
        log.info(f"Application exited cleanly with code {exit_code}.")
        sys.exit(exit_code)
    except Exception as e:
        log.critical(f"Exception during app.exec(): {e}", exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
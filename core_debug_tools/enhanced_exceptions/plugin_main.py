# PuffinPyEditor/core_debug_tools/enhanced_exceptions/plugin_main.py
import sys
from utils.logger import log
from .exception_dialog import ExceptionDialog
from app_core.puffin_api import PuffinPluginAPI

class EnhancedExceptionsPlugin:
    _instance = None

    def __init__(self, puffin_api: PuffinPluginAPI, original_hook):
        self.api = puffin_api
        self.main_window = self.api.get_main_window()
        self.original_excepthook = original_hook or sys.excepthook
        sys.excepthook = self.show_exception_dialog
        log.info("Enhanced Exception Reporter initialized and hook installed.")

    def show_exception_dialog(self, exc_type, exc_value, exc_tb):
        # CORRECTED: Specifically ignore KeyboardInterrupt.
        if issubclass(exc_type, KeyboardInterrupt):
            log.warning("KeyboardInterrupt caught and ignored by the main thread.")
            return

        log.critical("Unhandled exception caught by Enhanced Reporter:",
                     exc_info=(exc_type, exc_value, exc_tb))
        dialog = ExceptionDialog(exc_type, exc_value, exc_tb, self.main_window)
        dialog.exec()
        self.original_excepthook(exc_type, exc_value, exc_tb)

def initialize(puffin_api: PuffinPluginAPI, original_hook=None):
    if EnhancedExceptionsPlugin._instance is None:
        EnhancedExceptionsPlugin._instance = EnhancedExceptionsPlugin(
            puffin_api, original_hook
        )
    return EnhancedExceptionsPlugin._instance
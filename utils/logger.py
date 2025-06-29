# PuffinPyEditor/utils/logger.py
import logging
import os
import platform
from logging.handlers import RotatingFileHandler

APP_NAME = "PuffinPyEditor"
ORG_NAME = "PuffinPyEditorProject"


def get_app_data_path() -> str:
    """
    Gets a cross-platform writable directory for application data.

    Returns:
        A string representing the path to the application data directory.
    """
    system = platform.system()
    if system == "Windows":
        # e.g., C:\Users\<user>\AppData\Local\PuffinPyEditorProject\...
        path = os.path.join(os.environ.get('LOCALAPPDATA', ''),
                            ORG_NAME, APP_NAME)
    elif system == "Darwin":  # macOS
        # e.g., /Users/<user>/Library/Application Support/PuffinPyEditorProject/...
        path = os.path.join(os.path.expanduser(
            '~/Library/Application Support'), ORG_NAME, APP_NAME)
    else:  # Linux and other systems
        # e.g., /home/<user>/.local/share/PuffinPyEditorProject/...
        path = os.path.join(os.path.expanduser('~/.local/share'),
                            ORG_NAME, APP_NAME)

    return path


# This will now be a path in the user's home directory, which is always writable.
APP_DATA_ROOT = get_app_data_path()
LOG_DIR = os.path.join(APP_DATA_ROOT, "logs")

# Use exist_ok=True for robustness. This creates the directory if it doesn't
# exist and does nothing if it already exists, preventing race conditions.
os.makedirs(LOG_DIR, exist_ok=True)

LOG_FILE = os.path.join(LOG_DIR, "app.log")


def setup_logger(name: str = "PuffinPyEditor",
                   log_level: int = logging.DEBUG) -> logging.Logger:
    """
    Configures and returns a logger instance.
    """
    logger = logging.getLogger(name)
    if logger.hasHandlers():
        logger.handlers.clear()

    logger.setLevel(log_level)

    formatter = logging.Formatter(
        "%(asctime)s - %(levelname)s - "
        "[%(module)s.%(funcName)s:%(lineno)d] - %(message)s"
    )

    # StreamHandler logs to the console
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)  # Console logs can be less verbose
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    # RotatingFileHandler logs to a file in the user-writable location
    try:
        fh = RotatingFileHandler(
            LOG_FILE, maxBytes=5*1024*1024, backupCount=5, encoding='utf-8'
        )
        fh.setLevel(log_level)  # File logs should be detailed
        fh.setFormatter(formatter)
        logger.addHandler(fh)
    except Exception as e:
        logger.error(
            f"Failed to create file handler for logging: {e}", exc_info=False
        )

    logger.info(f"Logger initialized. Log file at: {LOG_FILE}")
    return logger


# Global logger instance for the application
log = setup_logger()
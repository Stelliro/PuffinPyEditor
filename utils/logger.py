# PuffinPyEditor/utils/logger.py
import logging
import os
from logging.handlers import RotatingFileHandler

LOG_DIR = "logs"
LOG_FILE = os.path.join(LOG_DIR, "app.log")

if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

def setup_logger(name="PuffinPyEditorLogger", log_level=logging.DEBUG):
    logger = logging.getLogger(name)
    if logger.hasHandlers():
        logger.handlers.clear()

    logger.setLevel(log_level)

    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - [%(module)s.%(funcName)s:%(lineno)d] - %(message)s"
    )

    # StreamHandler logs to the console
    ch = logging.StreamHandler()
    # FIX: Set console handler to DEBUG to see all messages
    ch.setLevel(logging.DEBUG)
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    # FileHandler logs to a file
    fh = RotatingFileHandler(LOG_FILE, maxBytes=5*1024*1024, backupCount=5, encoding='utf-8')
    fh.setLevel(log_level)  # log_level is already DEBUG by default
    fh.setFormatter(formatter)
    logger.addHandler(fh)

    logger.info("Logger initialized (Console Level: DEBUG).")
    return logger

log = setup_logger()

if __name__ == '__main__':
    log.debug("This is a debug message.")
    log.info("This is an info message.")
    log.warning("This is a warning message.")
    log.error("This is an error message.")
    log.critical("This is a critical message.")
    print(f"Log file is at: {os.path.abspath(LOG_FILE)}")
# PuffinPyEditor/utils/helpers.py
import sys
import os
from typing import List, Optional
from PyQt6.QtGui import QFontDatabase
from .logger import log


def get_base_path():
    """
    Returns the base path for the application, handling frozen executables.
    For a frozen app, this is the directory of the executable.
    For a source app, this is the project root.
    """
    if getattr(sys, 'frozen', False):
        # The application is frozen
        return os.path.dirname(sys.executable)
    else:
        # Assumes this file is in /utils, so two levels up is the project root
        return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def get_best_available_font(preferred_list: List[str]) -> Optional[str]:
    """
    Scans a preferred list of font families and returns the first one found
    on the user's system. This is useful for setting sensible default fonts.

    Args:
        preferred_list: A list of font family names, in order of preference.

    Returns:
        The name of the first available font, or None if none are found.
    """
    if not isinstance(preferred_list, list):
        log.warning(
            f"Font list provided is not a list: {preferred_list}. No font selected."
        )
        return None

    font_db = QFontDatabase()
    installed_fonts = {font.lower() for font in font_db.families()}

    for font_name in preferred_list:
        if font_name.lower() in installed_fonts:
            log.info(f"Font suggestion: Found '{font_name}' installed on system.")
            return font_name

    log.warning(
        f"Could not find any of the preferred fonts: {preferred_list}. "
        "The application will use a system default."
    )
    return None
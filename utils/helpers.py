# PuffinPyEditor/utils/helpers.py
from PyQt6.QtGui import QFontDatabase
from utils.logger import log


def get_best_available_font(preferred_list: list[str]) -> str | None:
    """
    Scans a preferred list of font families and returns the first one found
    on the user's system.
    """
    if not isinstance(preferred_list, list):
        log.warning(f"Font list provided is not a list: {preferred_list}. No font selected.")
        return None

    font_db = QFontDatabase()
    installed_fonts = font_db.families()

    installed_fonts_set = {font.lower() for font in installed_fonts}

    for font_name in preferred_list:
        if font_name.lower() in installed_fonts_set:
            log.info(f"Font suggestion: Found '{font_name}' installed on system.")
            return font_name

    log.warning(f"Could not find any of the preferred fonts: {preferred_list}. Using system default.")
    return None
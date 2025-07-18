# PuffinPyEditor/utils/helpers.py
import sys
import os
import re
import difflib
import hashlib
from typing import List, Optional
from PyQt6.QtGui import QFontDatabase
from .logger import log, get_app_data_path

if sys.platform == "win32":
    try:
        import winshell
    except ImportError:
        winshell = None
        log.warning("The 'winshell' package is not installed. Startup shortcut features will be disabled.")


def get_base_path():
    """
    Returns the application's base path for resource loading.

    This handles the difference between running from source and a frozen
    (e.g., PyInstaller) executable. For a frozen app, this is the directory
    of the executable. For a source app, this is the project root.
    """
    if getattr(sys, 'frozen', False):
        # The application is frozen
        return os.path.dirname(sys.executable)
    else:
        # Assumes this file is in /utils, so two levels up is the project root
        return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# --- NEW: Session/Draft Management Helpers ---
def get_session_path() -> str:
    """Returns the path to the session data directory, creating it if needed."""
    session_dir = os.path.join(get_app_data_path(), "session_data", "drafts")
    os.makedirs(session_dir, exist_ok=True)
    return session_dir

def get_draft_path(original_filepath: str) -> str:
    """Generates a consistent, safe filename for a draft file."""
    # Hash the full, absolute path to ensure uniqueness
    path_hash = hashlib.sha256(original_filepath.encode('utf-8')).hexdigest()
    return os.path.join(get_session_path(), f"{path_hash}.draft")
# --- End of New Helpers ---


def clean_git_conflict_markers(content: str) -> str:
    """Removes Git conflict markers from a string, keeping the HEAD version."""
    if '<<<<<<<' not in content:
        return content

    lines = content.splitlines()
    cleaned_lines = []
    in_conflict = False
    # We want to keep the HEAD version, which is the part before '======='
    keep_current_version = True

    for line in lines:
        if line.startswith('<<<<<<<'):
            in_conflict = True
            keep_current_version = True
            continue

        if line.startswith('======='):
            if in_conflict:
                keep_current_version = False
                continue

        if line.startswith('>>>>>>>'):
            if in_conflict:
                in_conflict = False
                keep_current_version = False
                continue

        if not in_conflict or (in_conflict and keep_current_version):
            cleaned_lines.append(line)

    return "\n".join(cleaned_lines)


def generate_unified_diff(original_content: str, new_content: str, fromfile='original', tofile='new') -> str:
    """Generates a git-style unified diff string."""
    original_lines = original_content.splitlines(keepends=True)
    new_lines = new_content.splitlines(keepends=True)
    diff = difflib.unified_diff(original_lines, new_lines, fromfile=fromfile, tofile=tofile)
    return "".join(diff)


def get_startup_shortcut_path() -> Optional[str]:
    """
    Gets the cross-platform path to the user's startup folder.

    This is used for creating a shortcut to launch the app on system startup.
    Returns None if the platform is not supported (currently only Windows).
    """
    if sys.platform == "win32":
        try:
            startup_folder = winshell.folder("startup")
            return os.path.join(startup_folder, "PuffinPyEditor.lnk")
        except Exception as e:
            log.error(f"Could not get Windows startup folder path: {e}")
            return None
    return None


def get_best_available_font(preferred_list: List[str]) -> Optional[str]:
    """
    Scans a preferred list of font families and returns the first one found
    on the user's system.

    This is useful for setting sensible default fonts for different themes
    or operating systems.

    Args:
        preferred_list: A list of font family names, in order of preference.

    Returns:
        The name of the first available font, or None if none are found.
    """
    if not isinstance(preferred_list, list):
        log.warning(
            f"Font list provided is not a list: {preferred_list}. "
            "No font selected."
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
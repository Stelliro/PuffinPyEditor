# /ui/explorer/helpers.py
import os
import subprocess
from functools import lru_cache
from utils.logger import log


@lru_cache(maxsize=2)
def get_git_statuses_for_root(project_root: str) -> dict:
    """
    Runs `git status` and parses the output into a dictionary mapping file
    paths to their status. Uses a cache to avoid redundant calls.
    """
    if not project_root or not os.path.isdir(os.path.join(project_root, '.git')):
        return {}

    try:
        startupinfo = None
        if os.name == 'nt':
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

        # --ignored=matching includes ignored files that are explicitly listed
        command = ['git', 'status', '--porcelain', '--untracked-files=all', '--ignored=matching']
        result = subprocess.check_output(
            command,
            cwd=project_root, text=True, startupinfo=startupinfo, stderr=subprocess.PIPE,
            encoding='utf-8', errors='ignore'
        )
        status_dict = {}
        for line in result.strip().split('\n'):
            if not line:
                continue

            status, path = line[:2], line[3:].strip().replace('"', '')
            full_path = os.path.join(project_root, path.replace('/', os.sep))

            # Normalize the status character. '??' for untracked, 'M' for modified, '!!' for ignored
            final_status = status.strip() if status.strip() else " "
            if status.startswith("??"):
                final_status = "??"
            elif status.startswith("!!"):
                final_status = "!!"
            elif "M" in status:
                final_status = "M"

            status_dict[os.path.normpath(full_path)] = final_status

        return status_dict
    except (subprocess.CalledProcessError, FileNotFoundError, OSError) as e:
        log.warning(f"Could not get git status for {project_root}: {e}")
        return {}
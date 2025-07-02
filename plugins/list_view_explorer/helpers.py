# PuffinPyEditor/plugins/list_view_explorer/helpers.py
import os
import subprocess
from functools import lru_cache

@lru_cache(maxsize=2)
def get_git_statuses_for_root(project_root: str) -> dict:
    if not project_root or not os.path.isdir(os.path.join(project_root, '.git')):
        return {}
    try:
        startupinfo = None
        if os.name == 'nt':
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        result = subprocess.check_output(
            ['git', 'status', '--porcelain', '--untracked-files=all'],
            cwd=project_root, text=True, startupinfo=startupinfo, stderr=subprocess.PIPE
        )
        status_dict = {}
        for line in result.strip().split('\n'):
            if not line: continue
            status_chars, path = line[:2], line[3:].strip().replace('"', '')
            status = status_chars[1] if status_chars[1] != ' ' else status_chars[0]
            full_path = os.path.join(project_root, path.replace('/', os.sep))
            status_dict[os.path.normpath(full_path)] = status
        return status_dict
    except (subprocess.CalledProcessError, FileNotFoundError, OSError):
        return {}
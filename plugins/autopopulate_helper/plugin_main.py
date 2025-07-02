# PuffinPyEditor/plugins/autopopulate_helper/plugin_main.py
import os
import re
from utils.logger import log
from app_core.puffin_api import PuffinPluginAPI


class AutopopulateHelperPlugin:
    """
    A plugin to automate the creation of boilerplate content like
    __init__.py files and file headers.
    """
    # ... (rest of the file is unchanged, only init is different) ...
    COMMENT_MAP = {
        '.py': '#', '.js': '//', '.ts': '//', '.cs': '//', '.java': '//',
        '.go': '//', '.rs': '//', '.c': '//', '.cpp': '//', '.h': '//',
        '.hpp': '//', '.css': '/*', '.html': '<!--'
    }
    END_COMMENT_MAP = {'/*': '*/', '<!--': '-->'}

    def __init__(self, puffin_api: PuffinPluginAPI):
        self.api = puffin_api
        self.project_manager = self.api.get_manager("project")
        self.file_handler = self.api.get_manager("file_handler")
        self._connect_signals()
        log.info("Autopopulate Helper initialized.")

    def _connect_signals(self):
        if self.file_handler:
            self.file_handler.item_created.connect(self._on_item_created)
            self.file_handler.item_renamed.connect(self._on_item_renamed)

    def _on_item_created(self, item_type: str, path: str):
        if item_type == 'folder': self._handle_new_folder(path)
        elif item_type == 'file': self._add_header_to_new_file(path)

    def _on_item_renamed(self, item_type: str, old_path: str, new_path: str):
        if item_type == 'file': self._update_file_header(new_path)

    def _handle_new_folder(self, folder_path: str):
        if not self.project_manager.get_active_project_path(): return
        try:
            init_path = os.path.join(folder_path, "__init__.py")
            if not os.path.exists(init_path):
                with open(init_path, 'w', encoding='utf-8') as f:
                    f.write("# This file makes this directory a Python package.\n")
                log.info(f"Autopopulated {init_path}")
        except OSError as e:
            log.error(f"Autopopulate failed to create __init__.py in {folder_path}: {e}")

    def _generate_header_line(self, file_path: str) -> str | None:
        ext = os.path.splitext(file_path)[1].lower()
        comment_start = self.COMMENT_MAP.get(ext)
        if not comment_start: return None
        project_root = self.project_manager.get_active_project_path()
        if not (project_root and file_path.startswith(project_root)): return None
        project_name = os.path.basename(project_root)
        relative_path = os.path.relpath(file_path, project_root).replace(os.sep, '/')
        content = f"PuffinPyEditor/{project_name}/{relative_path}"
        comment_end = self.END_COMMENT_MAP.get(comment_start, "")
        return f"{comment_start} {content} {comment_end}\n"

    def _add_header_to_new_file(self, file_path: str):
        header_line = self._generate_header_line(file_path)
        if not header_line: return
        try:
            with open(file_path, 'w', encoding='utf-8') as f: f.write(header_line)
            log.info(f"Autopopulated header for new file: {file_path}")
        except IOError as e:
            log.error(f"Autopopulate failed to write header to {file_path}: {e}")

    def _update_file_header(self, file_path: str):
        new_header_line = self._generate_header_line(file_path)
        if not new_header_line: return
        try:
            with open(file_path, 'r', encoding='utf-8') as f: lines = f.readlines()
            header_regex = re.compile(r"^(#|//|<!--|\/\*)\s*PuffinPyEditor/.*")
            if not lines: lines.append(new_header_line)
            elif header_regex.match(lines[0]): lines[0] = new_header_line
            else: lines.insert(0, new_header_line)
            with open(file_path, 'w', encoding='utf-8') as f: f.writelines(lines)
            log.info(f"Autopopulated/Updated header for: {file_path}")
        except Exception as e:
            log.error(f"Autopopulate failed to update header for {file_path}: {e}", exc_info=True)


def initialize(puffin_api: PuffinPluginAPI):
    return AutopopulateHelperPlugin(puffin_api)
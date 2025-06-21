# PuffinPyEditor/app_core/project_manager.py
import os
import datetime
import zipfile
import shutil
from pathlib import Path
from utils.logger import log
from app_core.settings_manager import settings_manager


class ProjectManager:
    def __init__(self):
        self._open_projects = []
        self._active_project_path = None
        self._load_session()
        log.info(f"ProjectManager initialized with {len(self._open_projects)} projects.")

    def _load_session(self):
        open_projects = settings_manager.get("open_projects", [])
        active_project = settings_manager.get("active_project_path")
        self._open_projects = [os.path.normpath(p) for p in open_projects if os.path.isdir(p)]
        if active_project and os.path.normpath(active_project) in self._open_projects:
            self._active_project_path = os.path.normpath(active_project)
        elif self._open_projects:
            self._active_project_path = self._open_projects[0]
        else:
            self._active_project_path = None
        log.info(f"Loaded project session. Active project: {self._active_project_path}")

    def create_project_zip(self, output_zip_path: str) -> bool:
        """Creates a zip archive of the active project, ignoring common junk files."""
        if not self.is_project_open():
            log.error("Cannot create zip. No active project.")
            return False

        project_root = self.get_active_project_path()
        ignore_dirs = {'__pycache__', '.git', 'venv', '.venv', 'node_modules', '.idea', 'dist', 'build', 'logs'}
        ignore_files = {'.gitignore', 'main.spec', '.gitkeep', 'app.log'}

        try:
            with zipfile.ZipFile(output_zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, dirs, files in os.walk(project_root):
                    # Exclude ignored directories from traversal
                    dirs[:] = [d for d in dirs if d not in ignore_dirs]

                    for file in files:
                        if file in ignore_files or file.endswith('.zip'):
                            continue

                        file_path = os.path.join(root, file)
                        # The arcname is the path inside the zip file
                        arcname = os.path.relpath(file_path, project_root)
                        zipf.write(file_path, arcname)
            log.info(f"Successfully created project archive at {output_zip_path}")
            return True
        except Exception as e:
            log.error(f"Failed to create project zip: {e}", exc_info=True)
            return False

    def save_session(self):
        settings_manager.set("open_projects", self._open_projects, False)
        settings_manager.set("active_project_path", self._active_project_path, False)
        log.info("Project session saved.")

    def open_project(self, path: str) -> bool:
        if not os.path.isdir(path):
            log.error(f"Cannot open project. Path is not a directory: {path}")
            return False
        norm_path = os.path.normpath(path)
        if norm_path not in self._open_projects:
            self._open_projects.append(norm_path)
            log.info(f"Project opened: {norm_path}")
        self.set_active_project(norm_path)
        return True

    def close_project(self, path: str):
        norm_path = os.path.normpath(path)
        if norm_path in self._open_projects:
            self._open_projects.remove(norm_path)
            log.info(f"Project closed: {norm_path}")
            if self.get_active_project_path() == norm_path:
                new_active = self._open_projects[0] if self._open_projects else None
                self.set_active_project(new_active)

    def get_open_projects(self) -> list[str]:
        return self._open_projects

    def set_active_project(self, path: str | None):
        norm_path = os.path.normpath(path) if path else None
        if norm_path is None or norm_path in self._open_projects:
            if self._active_project_path != norm_path:
                self._active_project_path = norm_path
                log.info(f"Active project set to: {norm_path}")
        else:
            log.warning(f"Attempted to set non-opened project as active: {path}")

    def get_active_project_path(self) -> str | None:
        return self._active_project_path

    def is_project_open(self) -> bool:
        return self._active_project_path is not None

    def _generate_file_tree_string(self, start_path, prefix=""):
        lines = []
        ignore = {'__pycache__', '.git', '.idea', 'venv', '.venv', '.pytest_cache', 'dist', 'build', 'logs'}
        try:
            entries = sorted([p for p in os.scandir(start_path) if p.name not in ignore],
                             key=lambda e: (e.is_file(), e.name.lower()))
            for i, entry in enumerate(entries):
                is_last = i == (len(entries) - 1)
                lines.append(f"{prefix}{'└── ' if is_last else '├── '}{entry.name}")
                if entry.is_dir():
                    new_prefix = prefix + ("    " if is_last else "│   ")
                    lines.extend(self._generate_file_tree_string(entry.path, new_prefix))
        except OSError as e:
            log.warning(f"Could not read directory {start_path} for export tree: {e}")
        return lines

    def export_project_for_ai(self, output_filepath: str, all_problems: dict | None = None):
        if not self.is_project_open():
            return False, "No project is open."
        project_root = self.get_active_project_path()
        project_name = os.path.basename(project_root)
        include_extensions = ['.py', '.md', '.txt', '.json', '.html', '.css', '.js', '.yaml', '.yml', '.toml', '.ini',
                              '.cfg', '.sh', '.bat', '.ico']
        ignore_dirs = {'__pycache__', '.git', 'venv', '.venv', 'node_modules', '.idea', 'dist', 'build'}
        output_lines = []
        output_lines.append(f"# Project Export: {project_name}")
        output_lines.append(f"## Export Timestamp: {datetime.datetime.now().isoformat()}")
        output_lines.append("\n## File Tree:\n```")
        output_lines.append(f"/{project_name}")
        output_lines.extend(self._generate_file_tree_string(project_root))
        output_lines.append("```\n---")
        output_lines.append("\n## File Contents:\n")
        file_count = 0
        for dirpath, dirnames, filenames in os.walk(project_root, topdown=True):
            dirnames[:] = [d for d in dirnames if d not in ignore_dirs]
            for filename in sorted(filenames):
                if not any(filename.endswith(ext) for ext in include_extensions):
                    continue
                filepath = os.path.join(dirpath, filename)
                norm_filepath = os.path.normpath(filepath)
                relative_path = Path(filepath).relative_to(project_root).as_posix()
                language = Path(filename).suffix.lstrip('.') or 'text'
                if language == 'py': language = 'python'

                output_lines.append(f"### File: `/{relative_path}`\n")
                if all_problems and norm_filepath in all_problems:
                    output_lines.append("#### Linter Issues Found:")
                    output_lines.append("```")
                    for problem in all_problems[norm_filepath]:
                        output_lines.append(
                            f"- Line {problem['line']}, Col {problem['col']} ({problem['code']}): {problem['description']}")
                    output_lines.append("```\n")

                output_lines.append(f"```{language}")
                try:
                    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                        output_lines.append(f.read())
                    file_count += 1
                except Exception as e:
                    output_lines.append(f"[Error reading file: {e}]")
                output_lines.append("```\n---")
        try:
            with open(output_filepath, 'w', encoding='utf-8') as f:
                f.write("\n".join(output_lines))
            return True, f"Project exported to {Path(output_filepath).name}. Included {file_count} files."
        except Exception as e:
            return False, f"Failed to write export file: {e}"
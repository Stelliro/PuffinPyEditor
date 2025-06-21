import subprocess
import os
import sys
import shutil
import shlex
from pathlib import Path
from PyQt6.QtCore import QObject, QThread, pyqtSignal
from utils.logger import log


class LinterRunner(QObject):
    lint_results_ready = pyqtSignal(list)
    project_lint_results_ready = pyqtSignal(dict)

    def _find_flake8_executable(self) -> str | None:
        return shutil.which("flake8")

    def run_linter_on_file(self, filepath: str):
        if not filepath or not os.path.exists(filepath):
            self.lint_results_ready.emit([])
            return

        flake8_executable = self._find_flake8_executable()
        if not flake8_executable:
            log.error("Linter error: 'flake8' executable not found on the system PATH.")
            self.lint_results_ready.emit([])
            return

        command = [flake8_executable, filepath, "--format=%(row)d:%(col)d:%(code)s:%(text)s"]
        log.info(f"Running linter on file: {' '.join(command)}")
        try:
            creation_flags = subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
            process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, creationflags=creation_flags)
            stdout, stderr = process.communicate(timeout=10)
            if stderr: log.error(f"Linter stderr for {filepath}: {stderr.strip()}")
            results = self._parse_flake8_file_output(stdout)
            self.lint_results_ready.emit(results)
        except Exception as e:
            log.error(f"Exception while running flake8 on file: {e}", exc_info=True)
            self.lint_results_ready.emit([])

    def run_linter_on_project(self, project_path: str):
        flake8_executable = self._find_flake8_executable()
        if not flake8_executable:
            log.error("Linter error: 'flake8' not found.")
            self.project_lint_results_ready.emit({})
            return

        command = [flake8_executable, project_path, f"--format=%(path)s{os.pathsep}%(row)d{os.pathsep}%(col)d{os.pathsep}%(code)s{os.pathsep}%(text)s"]
        log.info(f"Running linter on project: {' '.join(command)}")
        try:
            creation_flags = subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
            process = subprocess.Popen(command, cwd=project_path, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, creationflags=creation_flags)
            stdout, stderr = process.communicate(timeout=30)
            if stderr: log.warning(f"Linter stderr for project {project_path}: {stderr.strip()}")
            results = self._parse_flake8_project_output(stdout, project_path)
            self.project_lint_results_ready.emit(results)
        except Exception as e:
            log.error(f"Exception while running flake8 on project: {e}", exc_info=True)
            self.project_lint_results_ready.emit({})

    def _parse_flake8_file_output(self, output: str) -> list:
        problems = []
        for line in output.strip().splitlines():
            parts = line.split(':', 3)
            if len(parts) == 4:
                try:
                    problems.append({"line": int(parts[0]), "col": int(parts[1]), "code": parts[2], "description": parts[3].strip()})
                except (ValueError, IndexError):
                    log.warning(f"Could not parse linter line: {line}")
        return problems

    def _parse_flake8_project_output(self, output: str, project_path: str) -> dict:
        problems_by_file = {}
        for line in output.strip().splitlines():
            parts = line.split(os.pathsep, 4)
            if len(parts) == 5:
                try:
                    raw_path, line_num, col_num, code, desc = parts
                    abs_path = os.path.normpath(os.path.join(project_path, raw_path))
                    problem = {"line": int(line_num), "col": int(col_num), "code": code, "description": desc.strip()}
                    if abs_path not in problems_by_file:
                        problems_by_file[abs_path] = []
                    problems_by_file[abs_path].append(problem)
                except (ValueError, IndexError):
                    log.warning(f"Could not parse project linter line: {line}")
        return problems_by_file


class LinterManager(QObject):
    lint_results_ready = pyqtSignal(list)
    project_lint_results_ready = pyqtSignal(dict)
    _request_file_lint = pyqtSignal(str)
    _request_project_lint = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.thread = QThread()
        self.runner = LinterRunner()
        self.runner.moveToThread(self.thread)
        self.thread.start()
        self._request_file_lint.connect(self.runner.run_linter_on_file)
        self._request_project_lint.connect(self.runner.run_linter_on_project)
        self.runner.lint_results_ready.connect(self.lint_results_ready)
        self.runner.project_lint_results_ready.connect(self.project_lint_results_ready)

    def lint_file(self, filepath: str):
        self._request_file_lint.emit(filepath)

    def lint_project(self, project_path: str):
        self._request_project_lint.emit(project_path)

    def shutdown(self):
        if self.thread.isRunning():
            self.thread.quit()
            self.thread.wait(3000)
# PuffinPyEditor/app_core/code_runner.py
import os
import sys
import shutil
from PyQt6.QtCore import QObject, pyqtSignal, QProcess
from .settings_manager import settings_manager
from utils.logger import log
from typing import Optional


def _find_python_interpreter() -> str:
    """
    Intelligently finds the best Python executable for running scripts.
    This prevents the app from trying to execute itself when frozen.

    Priority:
    1. User-defined path in settings.
    2. The python.exe from the current virtual environment (if from source).
    3. The first 'python' found on the system's PATH.
    4. The python.exe bundled alongside the main PuffinPyEditor.exe.

    Returns:
        The path to a suitable Python executable, or an empty string.
    """
    # 1. User-defined path
    user_path = settings_manager.get("python_interpreter_path", "").strip()
    if user_path and os.path.exists(user_path) and \
            "PuffinPyEditor.exe" not in user_path:
        log.info(f"CodeRunner: Using user-defined interpreter: {user_path}")
        return user_path

    # 2. Venv python if running from source
    if not getattr(sys, 'frozen', False):
        log.info("CodeRunner: Running from source, using sys.executable: "
                 f"{sys.executable}")
        return sys.executable

    # 3. System PATH python
    system_python = shutil.which("python")
    if system_python and "PuffinPyEditor.exe" not in system_python:
        log.info(f"CodeRunner: Found system python on PATH: {system_python}")
        return system_python

    # 4. Local python.exe if frozen (e.g., if bundled with the app)
    if getattr(sys, 'frozen', False):
        local_python_path = os.path.join(os.path.dirname(sys.executable),
                                         "python.exe")
        if os.path.exists(local_python_path):
            log.info("CodeRunner: Found local python.exe in frozen app dir: "
                     f"{local_python_path}")
            return local_python_path

    log.error("CodeRunner: Could not find a suitable Python interpreter.")
    return ""


class CodeRunner(QObject):
    """
    Manages the execution of Python scripts in a separate process.
    """
    output_received = pyqtSignal(str)
    error_received = pyqtSignal(str)
    process_finished = pyqtSignal(int)

    def __init__(self, parent: Optional[QObject] = None):
        super().__init__(parent)
        self.process: Optional[QProcess] = None

    def run_script(self, script_filepath: str):
        """
        Executes a Python script using the configured interpreter.

        Args:
            script_filepath: The absolute path to the Python script to run.
        """
        if not script_filepath or not os.path.exists(script_filepath):
            err_msg = f"Script path is invalid: {script_filepath}"
            log.error(err_msg)
            self.error_received.emit(err_msg + "\n")
            self.process_finished.emit(-1)
            return

        interpreter_path = _find_python_interpreter()

        if not interpreter_path:
            err_msg = ("Could not find a valid Python interpreter.\nPlease set "
                       "a path in Preferences or ensure 'python' is in your "
                       "system PATH.")
            log.error(err_msg)
            self.error_received.emit(err_msg + "\n")
            self.process_finished.emit(-1)
            return

        if self.process and self.process.state() != QProcess.ProcessState.NotRunning:
            warning_msg = "A script is already running. Please wait."
            log.warning(warning_msg)
            self.error_received.emit(f"[INFO] {warning_msg}\n")
            return

        self.process = QProcess()
        self.process.setProgram(interpreter_path)
        self.process.setArguments([script_filepath])

        # Set working dir to script's dir for correct relative imports
        script_dir = os.path.dirname(script_filepath)
        self.process.setWorkingDirectory(script_dir)
        log.info(f"Setting working directory for script to: {script_dir}")

        # Connect signals
        self.process.readyReadStandardOutput.connect(self._handle_stdout)
        self.process.readyReadStandardError.connect(self._handle_stderr)
        self.process.finished.connect(self._handle_finished)
        self.process.errorOccurred.connect(self._handle_process_error)

        log.info(f"Starting script: '{interpreter_path}' '{script_filepath}'")
        self.output_received.emit(
            f"[PuffinPyRun] Executing: {os.path.basename(script_filepath)} ...\n")
        self.process.start()

        if not self.process.waitForStarted(5000):
            err_msg = f"Failed to start process: {self.process.errorString()}"
            log.error(err_msg)
            self.error_received.emit(err_msg + "\n")
            self.process_finished.emit(self.process.exitCode())
            self.process = None  # Clean up the failed process
            return

        pid = self.process.processId() if self.process else 'N/A'
        log.debug(f"Process started successfully (PID: {pid}).")

    def stop_script(self):
        """Terminates the currently running script process."""
        if self.process and self.process.state() != QProcess.ProcessState.NotRunning:
            pid = self.process.processId()
            log.info(f"Attempting to terminate process (PID: {pid}).")
            self.output_received.emit("[PuffinPyRun] Terminating script...\n")
            self.process.terminate()
            # If terminate fails, forcefully kill it
            if not self.process.waitForFinished(1000):
                log.warning(f"Process {pid} did not terminate gracefully, killing.")
                self.process.kill()
                self.output_received.emit("[PuffinPyRun] Script process killed.\n")
            else:
                self.output_received.emit("[PuffinPyRun] Script process terminated.\n")
        else:
            log.info("Stop script requested, but no process is running.")

    def _handle_stdout(self):
        if self.process:
            data = self.process.readAllStandardOutput().data().decode(errors='replace')
            self.output_received.emit(data)

    def _handle_stderr(self):
        if self.process:
            data = self.process.readAllStandardError().data().decode(errors='replace')
            self.error_received.emit(data)

    def _handle_finished(self, exit_code: int, exit_status: QProcess.ExitStatus):
        log.info(f"Script finished. Exit code: {exit_code}, Status: {exit_status.name}")
        if exit_status == QProcess.ExitStatus.CrashExit:
            self.error_received.emit("[PuffinPyRun] Script process crashed.\n")

        self.output_received.emit(
            f"[PuffinPyRun] Process finished with exit code {exit_code}.\n")
        self.process_finished.emit(exit_code)
        self.process = None  # Clean up after finishing

    def _handle_process_error(self, error: QProcess.ProcessError):
        if self.process:
            err_msg = f"[PuffinPyRun] QProcess Error: {self.process.errorString()} (Code: {error.name})"
            log.error(err_msg)
            self.error_received.emit(err_msg + "\n")
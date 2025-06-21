# PuffinPyEditor/app_core/code_runner.py
import subprocess
import os
import sys
from PyQt6.QtCore import QObject, QThread, pyqtSignal, QProcess
from utils.logger import log
from app_core.settings_manager import settings_manager


class CodeRunner(QObject):
    output_received = pyqtSignal(str)
    error_received = pyqtSignal(str)
    process_finished = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.process = None

    def run_script(self, script_filepath: str):
        if not script_filepath or not os.path.exists(script_filepath):
            error_msg = f"Script path is invalid or file does not exist: {script_filepath}"
            log.error(error_msg)
            self.error_received.emit(error_msg)
            self.process_finished.emit(-1)
            return

        python_interpreter = settings_manager.get("python_interpreter_path", "").strip()
        if not python_interpreter:
            python_interpreter = sys.executable
            log.info(f"No specific Python interpreter set; using current interpreter: {python_interpreter}")

        if not python_interpreter or not os.path.exists(python_interpreter):
            error_msg = f"Python interpreter path is invalid or not set: '{python_interpreter}'." \
                        f"\nPlease set it in Preferences -> Run."
            log.error(error_msg)
            self.error_received.emit(error_msg)
            self.process_finished.emit(-1)
            return

        if self.process and self.process.state() != QProcess.ProcessState.NotRunning:
            warning_msg = "A script is already running. Please wait for it to complete."
            log.warning(warning_msg)
            self.error_received.emit(f"[INFO] {warning_msg}")
            return

        self.process = QProcess()
        self.process.setProgram(python_interpreter)
        self.process.setArguments([script_filepath])

        script_dir = os.path.dirname(script_filepath)
        self.process.setWorkingDirectory(script_dir)
        log.info(f"Setting working directory for script execution to: {script_dir}")

        self.process.readyReadStandardOutput.connect(self._handle_stdout)
        self.process.readyReadStandardError.connect(self._handle_stderr)
        self.process.finished.connect(self._handle_finished)
        self.process.errorOccurred.connect(self._handle_process_error)

        log.info(f"Starting script: '{python_interpreter}' '{script_filepath}'")
        self.output_received.emit(f"[PuffinPyRun] Executing: {os.path.basename(script_filepath)} ...\n")
        self.process.start()

        if not self.process.waitForStarted(timeout=5000):
            error_msg = f"Failed to start the script process: {self.process.errorString()}"
            log.error(error_msg)
            self.error_received.emit(error_msg)
            self.process_finished.emit(self.process.exitCode() if self.process else -1)
            self.process = None
            return

        log.debug(f"Process started successfully (PID: {self.process.processId() if self.process else 'N/A'}).")

    def _handle_stdout(self):
        if not self.process: return
        data = self.process.readAllStandardOutput().data().decode(errors='replace')
        self.output_received.emit(data)

    def _handle_stderr(self):
        if not self.process: return
        data = self.process.readAllStandardError().data().decode(errors='replace')
        self.error_received.emit(data)

    def _handle_finished(self, exit_code: int, exit_status: QProcess.ExitStatus):
        log.info(f"Script execution finished. Exit code: {exit_code}, Status: {exit_status.name}")
        if exit_status == QProcess.ExitStatus.CrashExit:
            self.error_received.emit(f"[PuffinPyRun] Script process crashed.\n")

        self.output_received.emit(f"[PuffinPyRun] Process finished with exit code {exit_code}.\n")
        self.process_finished.emit(exit_code)
        self.process = None

    def _handle_process_error(self, error: QProcess.ProcessError):
        if not self.process: return
        error_msg = f"[PuffinPyRun] QProcess Error: {self.process.errorString()} (Code: {error.name})"
        log.error(error_msg)
        self.error_received.emit(error_msg + "\n")

    def stop_script(self):
        if self.process and self.process.state() != QProcess.ProcessState.NotRunning:
            log.info(f"Attempting to terminate script process (PID: {self.process.processId()}).")
            self.output_received.emit("[PuffinPyRun] Terminating script...\n")
            self.process.terminate()
            if not self.process.waitForFinished(1000):
                log.warning("Process did not terminate gracefully, killing.")
                self.process.kill()
                self.output_received.emit("[PuffinPyRun] Script process killed.\n")
            else:
                self.output_received.emit("[PuffinPyRun] Script process terminated.\n")
        else:
            log.info("Stop script requested, but no process is running.")


if __name__ == '__main__':
    from PyQt6.QtWidgets import QApplication

    app = QApplication.instance() or QApplication(sys.argv)

    runner = CodeRunner()

    test_script_path = "temp_test_script.py"
    with open(test_script_path, "w") as f:
        f.write("import time\n")
        f.write("print('Hello from PuffinPyEditor test script!')\n")
        f.write("time.sleep(1)\n")
        f.write("print('This is standard output.')\n")
        f.write("import sys\n")
        f.write("sys.stderr.write('This is standard error output.\\n')\n")
        f.write("time.sleep(1)\n")
        f.write("print('Script finished.')\n")


    def on_output(data): print(f"STDOUT: {data.strip()}")


    def on_error(data): print(f"STDERR: {data.strip()}")


    def on_finish(code):
        print(f"FINISHED, Code: {code}")
        os.remove(test_script_path)
        QApplication.quit()


    runner.output_received.connect(on_output)
    runner.error_received.connect(on_error)
    runner.process_finished.connect(on_finish)

    print("Attempting to run test script...")
    runner.run_script(os.path.abspath(test_script_path))


    sys.exit(app.exec())
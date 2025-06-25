# MACK PUFFINPYEDITOR/ui/widgets/terminal_widget.py
import os
import sys
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTextEdit, QLineEdit, QHBoxLayout
from PyQt6.QtGui import QFont, QColor
from PyQt6.QtCore import QProcess

from utils.logger import log


class TerminalWidget(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        log.info("TerminalWidget initializing...")

        self.process = QProcess(self)
        self.shell_path = "cmd.exe" if sys.platform == "win32" else os.environ.get("SHELL", "/bin/bash")
        self.current_working_directory = os.path.expanduser("~")

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

        self.output_area = QTextEdit()
        self.output_area.setReadOnly(True)
        self.output_area.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)
        self.layout.addWidget(self.output_area, 1)

        input_container = QWidget(self)
        input_container.setObjectName("TerminalInputContainer")
        input_layout = QHBoxLayout(input_container)
        input_layout.setContentsMargins(5, 3, 5, 3)
        input_layout.setSpacing(5)

        self.input_line = QLineEdit(self)
        self.input_line.setPlaceholderText("Type command and press Enter...")

        input_layout.addWidget(self.input_line, 1)
        self.layout.addWidget(input_container)

        self._setup_styles()

        self.input_line.returnPressed.connect(self._on_command_entered)
        self.process.readyReadStandardOutput.connect(self._handle_stdout)
        self.process.readyReadStandardError.connect(self._handle_stderr)
        self.process.finished.connect(self._on_process_finished)

        self.set_working_directory(self.current_working_directory)
        log.info("TerminalWidget initialized.")

    def _setup_styles(self):
        font = QFont("Consolas", 10)
        self.output_area.setFont(font)
        self.input_line.setFont(font)
        self.output_area.setStyleSheet("background-color: black; color: #E0E0E0; border: none;")
        self.input_line.setStyleSheet("background-color: black; color: #E0E0E0; border: none;")

    def set_working_directory(self, path: str):
        if path and os.path.isdir(path):
            self.current_working_directory = path
        else:
            self.current_working_directory = os.path.expanduser("~")

        log.info(f"Terminal working directory set to: {self.current_working_directory}")

    def start_process(self):
        if self.process.state() == QProcess.ProcessState.Running:
            return
        self.output_area.clear()
        self.process.setWorkingDirectory(self.current_working_directory)
        self.process.start(self.shell_path)
        if not self.process.waitForStarted():
            self.append_output(f"Error: Could not start shell at {self.shell_path}", True)
            log.error(f"Failed to start terminal process: {self.process.errorString()}")
            return
        log.info(f"Terminal process started (PID: {self.process.processId()}).")

    def restart_process(self):
        """Kills the current process and starts a new one."""
        log.info("Restarting terminal process...")
        self.kill_process()
        self.start_process()

    def _on_command_entered(self):
        command = self.input_line.text().strip()
        self.input_line.clear()
        self.execute_command(command)

    def execute_command(self, command: str):
        """Public method to send a command to the running terminal process."""
        if not command:
            return

        command_to_write = command + "\n"
        if self.process.state() == QProcess.ProcessState.Running:
            self.process.write(command_to_write.encode('utf-8'))
        else:
            self.append_output("Shell process is not running.", is_error=True)

    def append_output(self, text: str, is_error: bool = False):
        cursor = self.output_area.textCursor()
        cursor.movePosition(cursor.MoveOperation.End)
        self.output_area.setTextCursor(cursor)

        if is_error:
            original_color = self.output_area.textColor()
            self.output_area.setTextColor(QColor("red"))
            self.output_area.insertPlainText(text)
            self.output_area.setTextColor(original_color)
        else:
            self.output_area.insertPlainText(text)

        self.output_area.verticalScrollBar().setValue(self.output_area.verticalScrollBar().maximum())

    def _handle_stdout(self):
        self.append_output(self.process.readAllStandardOutput().data().decode('utf-8', errors='replace'))

    def _handle_stderr(self):
        self.append_output(self.process.readAllStandardError().data().decode('utf-8', errors='replace'), is_error=True)

    def _on_process_finished(self):
        self.append_output("\n[Process finished]\n", is_error=True)
        log.info("Terminal process finished.")

    def kill_process(self):
        if self.process.state() == QProcess.ProcessState.Running:
            log.info("Killing terminal process...")
            self.process.kill()

    def set_font_and_color(self, font: QFont, text_color: QColor, bg_color: QColor):
        self.output_area.setFont(font)
        self.input_line.setFont(font)

        container_bg = bg_color.name()
        container_border = bg_color.lighter(120).name()

        stylesheet = f"""
            QTextEdit {{
                background-color: {bg_color.name()};
                color: {text_color.name()};
                border: none;
                padding-left: 5px;
            }}
            QWidget#TerminalInputContainer {{
                background-color: {container_bg};
                border-top: 1px solid {container_border};
            }}
            QLineEdit {{
                color: {text_color.name()};
                background-color: transparent;
                border: none;
            }}
        """
        self.setStyleSheet(stylesheet)
        self.output_area.setTextColor(text_color)
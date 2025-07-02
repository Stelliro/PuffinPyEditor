# PuffinPyEditor/plugins/terminal/terminal_widget.py
import os
import sys
import platform
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QTextEdit, QMenu, QFileDialog, QApplication,
                             QHBoxLayout, QPushButton, QFrame)
from PyQt6.QtGui import QColor, QFont, QTextCursor, QKeySequence
from PyQt6.QtCore import QProcess, Qt
import qtawesome as qta
from utils.logger import log

class TerminalWidget(QWidget):
    """An interactive terminal widget that runs a native shell process."""

    def __init__(self, puffin_api):
        super().__init__()
        self.api = puffin_api
        self.project_manager = self.api.get_manager("project")
        self.settings = self.api.get_manager("settings")
        self.theme_manager = self.api.get_manager("theme")

        self.process = QProcess(self)
        self.input_start_position = 0

        self._setup_ui()
        self._connect_signals()
        self.update_theme()
        self.start_shell()

    def _setup_ui(self):
        """Initializes the UI components."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Toolbar for buttons
        toolbar = QFrame()
        toolbar.setObjectName("TerminalToolbar")
        toolbar_layout = QHBoxLayout(toolbar)
        toolbar_layout.setContentsMargins(5, 2, 5, 2)
        
        self.clear_button = QPushButton(qta.icon('fa5s.broom'), "Clear")
        self.stop_button = QPushButton(qta.icon('fa5s.stop-circle'), "Stop Process")
        
        toolbar_layout.addWidget(self.clear_button)
        toolbar_layout.addWidget(self.stop_button)
        toolbar_layout.addStretch()
        main_layout.addWidget(toolbar)

        # Main terminal text area
        self.output_area = QTextEdit()
        self.output_area.setAcceptRichText(False)
        self.output_area.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        main_layout.addWidget(self.output_area)
        
    def _connect_signals(self):
        """Connects signals for the process and UI."""
        self.process.readyReadStandardOutput.connect(self._handle_stdout)
        self.process.readyReadStandardError.connect(self._handle_stderr)
        self.process.finished.connect(self._on_process_finished)
        
        self.clear_button.clicked.connect(self.clear_terminal)
        self.stop_button.clicked.connect(self.stop_process)
        self.output_area.customContextMenuRequested.connect(self._show_context_menu)

        # We must override the key press event to handle input.
        self.output_area.keyPressEvent = self.keyPressEvent

    def update_theme(self):
        """Applies colors and fonts from the current theme."""
        font = QFont(self.settings.get("font_family"), self.settings.get("font_size"))
        self.output_area.setFont(font)
        
        colors = self.theme_manager.current_theme_data.get('colors', {})
        bg = colors.get('editor.background', '#1E1E1E')
        fg = colors.get('editor.foreground', '#D4D4D4')
        toolbar_bg = colors.get('sidebar.background', '#252526')
        border = colors.get('input.border', '#3c3c3c')
        
        self.setStyleSheet(f"""
            TerminalWidget {{ background-color: {bg}; }}
            #TerminalToolbar {{ 
                background-color: {toolbar_bg}; 
                border-bottom: 1px solid {border}; 
            }}
            QTextEdit {{
                background-color: {bg};
                color: {fg};
                border: none;
                padding: 5px;
            }}
        """)

    def start_shell(self):
        """Starts the appropriate native shell for the OS."""
        if self.process.state() == QProcess.ProcessState.Running:
            return

        project_path = self.project_manager.get_active_project_path()
        start_dir = project_path if project_path and os.path.isdir(project_path) else os.path.expanduser("~")
        
        shell_cmd, args = "", []
        if platform.system() == "Windows":
            shell_cmd = "cmd.exe"
            args = ["/K", "prompt $g"] # Keep open, set prompt to ">"
        else:
            shell_cmd = os.environ.get("SHELL", "/bin/bash")

        self.process.setWorkingDirectory(start_dir)
        self.process.start(shell_cmd, args)
        log.info(f"Terminal started in '{start_dir}' with shell '{shell_cmd}'.")
        self.output_area.setFocus()
    
    def keyPressEvent(self, event):
        """Handles user input, sending it to the shell process."""
        cursor = self.output_area.textCursor()
        
        # Stop user from deleting the prompt or previous output
        if cursor.position() < self.input_start_position:
            cursor.setPosition(self.input_start_position)
            self.output_area.setTextCursor(cursor)
        
        if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            command = self.output_area.toPlainText()[self.input_start_position:]
            QTextEdit.keyPressEvent(self.output_area, event) # Let the editor handle the newline
            self.process.write((command + "\n").encode())
            return

        # Basic backspace protection
        if event.key() == Qt.Key.Key_Backspace:
            if cursor.position() > self.input_start_position:
                QTextEdit.keyPressEvent(self.output_area, event)
            return

        # Ctrl+C to stop current process in shell
        if event.key() == Qt.Key.Key_C and event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            self.process.write(b'\x03') # Send SIGINT
            return
            
        QTextEdit.keyPressEvent(self.output_area, event)

    def _append_text(self, text, color=None):
        """Appends text to the output, scrolling to the end."""
        cursor = self.output_area.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        self.output_area.setTextCursor(cursor)

        if color: self.output_area.setTextColor(color)
        self.output_area.insertPlainText(text)
        if color: self.output_area.setTextColor(QColor(self.settings.get('editor.foreground')))

        self.output_area.verticalScrollBar().setValue(self.output_area.verticalScrollBar().maximum())
        self.input_start_position = self.output_area.textCursor().position()

    def _handle_stdout(self):
        data = self.process.readAllStandardOutput().data().decode(errors='ignore')
        self._append_text(data)

    def _handle_stderr(self):
        data = self.process.readAllStandardError().data().decode(errors='ignore')
        colors = self.theme_manager.current_theme_data.get('colors', {})
        error_color = QColor(colors.get('syntax.comment', '#cd5c5c'))
        self._append_text(data, color=error_color)

    def _on_process_finished(self):
        self._append_text("\n[Process finished. Relaunching shell...]\n")
        self.start_shell()
        
    def _show_context_menu(self, pos):
        """Displays a custom context menu."""
        menu = QMenu()
        menu.addAction(qta.icon('fa5.copy'), "Copy", self.output_area.copy)
        menu.addAction("Paste", self.output_area.paste)
        menu.addSeparator()
        menu.addAction("Copy All", self.copy_all)
        menu.addSeparator()
        menu.addAction(qta.icon('fa5s.file-export'), "Export Session...", self.export_to_file)
        menu.exec(self.output_area.mapToGlobal(pos))
        
    def copy_all(self):
        QApplication.clipboard().setText(self.output_area.toPlainText())

    def export_to_file(self):
        path, _ = QFileDialog.getSaveFileName(self, "Export Terminal Session", "", "Text Files (*.txt);;All Files (*)")
        if path:
            try:
                with open(path, 'w', encoding='utf-8') as f:
                    f.write(self.output_area.toPlainText())
                log.info(f"Terminal session exported to {path}")
            except Exception as e:
                log.error(f"Failed to export terminal session: {e}")

    def clear_terminal(self):
        self.output_area.clear()
        # On Windows, sending a 'cls' command is a clean way to clear
        if platform.system() == "Windows":
             self.process.write(b'cls\n')
        else: # For other systems, just restart the shell for a clean slate
            self.stop_process()
            self.start_shell()
            
    def stop_process(self):
        if self.process.state() == QProcess.ProcessState.Running:
            self.process.kill()
            log.info("Terminal process killed by user.")

    def closeEvent(self, event):
        """Ensure the shell process is terminated when the widget closes."""
        self.stop_process()
        super().closeEvent(event)
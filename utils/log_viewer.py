# PuffinPyEditor/utils/log_viewer.py
import sys
import os
from PyQt6.QtWidgets import (QApplication, QMainWindow, QTextEdit, QVBoxLayout,
                             QWidget, QHBoxLayout, QPushButton, QCheckBox)
from PyQt6.QtGui import QFont, QColor
from PyQt6.QtCore import QFileSystemWatcher, QTimer


class LogViewerWindow(QMainWindow):
    """A standalone application to view a log file in real-time."""

    def __init__(self, log_file_path):
        super().__init__()
        self.log_file_path = log_file_path
        self.last_pos = 0

        self.setWindowTitle(f"PuffinPy Log Viewer - {os.path.basename(log_file_path)}")
        self.setMinimumSize(800, 600)
        self.setStyleSheet("background-color: #2D2A2E;")

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        layout = QVBoxLayout(self.central_widget)
        self.text_edit = QTextEdit()
        self.text_edit.setReadOnly(True)
        self.text_edit.setFont(QFont("Consolas", 10))
        self.text_edit.setStyleSheet(
            "background-color: #1E1C21; color: #E0E0E0; border: none; padding: 5px;"
        )
        layout.addWidget(self.text_edit)

        # Controls
        controls_layout = QHBoxLayout()
        clear_button = QPushButton("Clear")
        clear_button.clicked.connect(self.clear_log)
        self.autoscroll_check = QCheckBox("Auto-scroll")
        self.autoscroll_check.setChecked(True)

        controls_layout.addWidget(clear_button)
        controls_layout.addStretch()
        controls_layout.addWidget(self.autoscroll_check)
        layout.addLayout(controls_layout)

        # File watcher
        self.watcher = QFileSystemWatcher([self.log_file_path])
        self.watcher.fileChanged.connect(self.update_log_content)

        # Initial load
        QTimer.singleShot(100, self.initial_load)

    def initial_load(self):
        """Loads the entire log file content when the app starts."""
        if not os.path.exists(self.log_file_path):
            self.text_edit.setText(f"Waiting for log file: {self.log_file_path}...")
            return
        try:
            with open(self.log_file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                self.text_edit.setText(content)
                self.last_pos = f.tell()
            if self.autoscroll_check.isChecked():
                self.text_edit.verticalScrollBar().setValue(
                    self.text_edit.verticalScrollBar().maximum()
                )
        except Exception as e:
            self.text_edit.setText(f"Error loading log file: {e}")

    def update_log_content(self):
        """Reads only the new content from the log file and appends it."""
        try:
            with open(self.log_file_path, 'r', encoding='utf-8') as f:
                f.seek(self.last_pos)
                new_content = f.read()
                if new_content:
                    self.text_edit.moveCursor(self.text_edit.textCursor().MoveOperation.End)
                    self.text_edit.insertPlainText(new_content)
                self.last_pos = f.tell()

            if self.autoscroll_check.isChecked():
                self.text_edit.verticalScrollBar().setValue(
                    self.text_edit.verticalScrollBar().maximum()
                )
        except Exception as e:
            # Handle cases where the file might be temporarily locked or reset
            print(f"Error updating log: {e}")
            self.last_pos = 0

    def clear_log(self):
        self.text_edit.clear()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    if len(sys.argv) < 2:
        print("Usage: python log_viewer.py <path_to_log_file>")
        sys.exit(1)
    viewer = LogViewerWindow(sys.argv[1])
    viewer.show()
    sys.exit(app.exec())
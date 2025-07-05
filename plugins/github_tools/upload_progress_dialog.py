# PuffinPyEditor/plugins/github_tools/upload_progress_dialog.py
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QProgressBar, QTextEdit
from PyQt6.QtCore import Qt

class UploadProgressDialog(QDialog):
    """A dialog to show the real-time progress of an asset upload."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Uploading Release Assets")
        self.setMinimumWidth(500)
        self.setModal(True)
        # Prevent the user from closing the dialog
        self.setWindowFlag(Qt.WindowType.WindowCloseButtonHint, False)
        
        layout = QVBoxLayout(self)
        
        self.file_label = QLabel("Starting upload...")
        layout.addWidget(self.file_label)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        layout.addWidget(self.progress_bar)
        
        self.log_console = QTextEdit()
        self.log_console.setReadOnly(True)
        self.log_console.setStyleSheet("background-color: #1e1e1e; color: #d4d4d4;")
        layout.addWidget(self.log_console)

    def update_progress(self, file_name, percentage):
        self.file_label.setText(f"Uploading: {file_name}")
        self.progress_bar.setValue(percentage)

    def add_log(self, message):
        self.log_console.append(message)
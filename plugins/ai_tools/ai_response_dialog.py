# PuffinPyEditor/plugins/ai_tools/ai_response_dialog.py
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QTextEdit, QDialogButtonBox, QPushButton,
    QApplication
)
import qtawesome as qta


class AIResponseDialog(QDialog):
    """A dialog to display the response from an AI model."""
    def __init__(self, response_text: str, parent=None):
        super().__init__(parent)
        self.response_text = response_text
        self.setWindowTitle("AI Response")
        self.setMinimumSize(700, 500)
        self.setObjectName("AIResponseDialog")

        self.layout = QVBoxLayout(self)

        self.text_edit = QTextEdit()
        self.text_edit.setMarkdown(self.response_text)
        self.text_edit.setReadOnly(True)
        self.layout.addWidget(self.text_edit)

        self.button_box = QDialogButtonBox()
        self.copy_button = QPushButton(
            qta.icon('fa5s.copy'), "Copy to Clipboard"
        )
        self.button_box.addButton(
            self.copy_button, QDialogButtonBox.ButtonRole.ActionRole
        )
        self.button_box.addButton(QDialogButtonBox.StandardButton.Close)
        self.layout.addWidget(self.button_box)

        self.copy_button.clicked.connect(self._copy_to_clipboard)
        self.button_box.rejected.connect(self.reject)

    def _copy_to_clipboard(self):
        """Copies the response text to the system clipboard."""
        QApplication.clipboard().setText(self.response_text)
        self.copy_button.setText("Copied!")
        self.copy_button.setEnabled(False)
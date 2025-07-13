# /plugins/installer_builder/config_editor_dialog.py
import json
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QTextEdit, QMessageBox, QDialogButtonBox)
from PyQt6.QtGui import QFont
from app_core.highlighters.json_syntax_highlighter import JsonSyntaxHighlighter

class ConfigEditorDialog(QDialog):
    def __init__(self, theme_manager, json_text, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Installer Configuration Editor")
        self.setMinimumSize(700, 600)
        self.main_layout = QVBoxLayout(self)

        self.text_editor = QTextEdit()
        self.text_editor.setFont(QFont("Consolas", 10))
        self.highlighter = JsonSyntaxHighlighter(self.text_editor.document(), theme_manager)
        self.text_editor.setPlainText(json_text)
        self.main_layout.addWidget(self.text_editor)

        self.button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.button_box.accepted.connect(self._validate_and_accept)
        self.button_box.rejected.connect(self.reject)
        self.main_layout.addWidget(self.button_box)

    def _validate_and_accept(self):
        try:
            json.loads(self.text_editor.toPlainText())
            self.accept()
        except json.JSONDecodeError as e:
            QMessageBox.critical(self, "Invalid JSON", f"The configuration contains a syntax error:\n\n{e}")

    def get_text(self):
        return self.text_editor.toPlainText()
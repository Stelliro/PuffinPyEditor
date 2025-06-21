# PuffinPyEditor/ui/dialogs/new_release_dialog.py
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QFormLayout, QDialogButtonBox,
                             QLineEdit, QTextEdit, QLabel, QCheckBox) # Added QCheckBox
from PyQt6.QtCore import Qt


class NewReleaseDialog(QDialog):
    def __init__(self, parent=None, default_tag="v1.0.0"):
        super().__init__(parent)
        self.setWindowTitle("Create New Release")
        self.setMinimumWidth(450)

        self.main_layout = QVBoxLayout(self)
        form_layout = QFormLayout()

        self.tag_edit = QLineEdit(default_tag)
        self.tag_edit.setPlaceholderText("e.g., v1.0.0")

        self.title_edit = QLineEdit()
        self.title_edit.setPlaceholderText("e.g., First Stable Release")

        self.notes_edit = QTextEdit()
        self.notes_edit.setPlaceholderText("Describe the changes in this release. Supports Markdown.")
        self.notes_edit.setMinimumHeight(150)

        # New: Pre-release checkbox
        self.prerelease_checkbox = QCheckBox("Mark as a pre-release")
        self.prerelease_checkbox.setToolTip("Indicates that this is not a production-ready release.")


        form_layout.addRow(QLabel("<b>Tag Name:</b>"), self.tag_edit)
        form_layout.addRow(QLabel("<b>Release Title:</b>"), self.title_edit)
        form_layout.addRow(QLabel("<b>Release Notes:</b>"), self.notes_edit)
        form_layout.addRow(QLabel("<b>Options:</b>"), self.prerelease_checkbox) # Add to layout

        self.main_layout.addLayout(form_layout)

        self.button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)

        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)

        self.button_box.button(QDialogButtonBox.StandardButton.Ok).setEnabled(
            bool(self.tag_edit.text() and self.title_edit.text()))

        self.tag_edit.textChanged.connect(self._validate_input)
        self.title_edit.textChanged.connect(self._validate_input)

        self.main_layout.addWidget(self.button_box)

    def _validate_input(self):
        is_valid = bool(self.tag_edit.text().strip() and self.title_edit.text().strip())
        self.button_box.button(QDialogButtonBox.StandardButton.Ok).setEnabled(is_valid)

    def get_release_data(self):
        """Returns the data entered by the user."""
        return {
            "tag": self.tag_edit.text().strip(),
            "title": self.title_edit.text().strip(),
            "notes": self.notes_edit.toPlainText().strip(),
            "prerelease": self.prerelease_checkbox.isChecked() # Return the checkbox state
        }
# /core_debug_tools/plugin_initializer/new_plugin_dialog.py
import re
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QFormLayout, QLineEdit,
                             QDialogButtonBox, QLabel, QMessageBox)
from PyQt6.QtCore import Qt

class NewPluginDialog(QDialog):
    """A dialog for collecting information to create a new plugin scaffold."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Create New Plugin")
        self.setMinimumWidth(400)

        # Main layout
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Enter the details for your new plugin."))
        
        # Form for input fields
        form_layout = QFormLayout()
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("e.g., My Awesome Tools")

        self.id_edit = QLineEdit()
        self.id_edit.setPlaceholderText("e.g., my_awesome_tools (auto-generated)")

        self.author_edit = QLineEdit()
        self.author_edit.setPlaceholderText("Your Name or Alias")

        self.desc_edit = QLineEdit()
        self.desc_edit.setPlaceholderText("A brief description of what this plugin does.")

        form_layout.addRow("Plugin Name:", self.name_edit)
        form_layout.addRow("Plugin ID:", self.id_edit)
        form_layout.addRow("Author:", self.author_edit)
        form_layout.addRow("Description:", self.desc_edit)
        layout.addLayout(form_layout)

        # OK and Cancel buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        layout.addWidget(button_box)
        
        # Connect signals
        button_box.accepted.connect(self.validate_and_accept)
        button_box.rejected.connect(self.reject)
        self.name_edit.textChanged.connect(self._auto_generate_id)

    def _auto_generate_id(self, text: str):
        """Generates a safe, snake_case ID from the plugin name."""
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', text)
        s2 = re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()
        safe_id = re.sub(r'[\s\-]+', '_', s2) # Replace spaces and hyphens
        safe_id = re.sub(r'[^\w_]', '', safe_id) # Remove invalid characters
        self.id_edit.setText(safe_id)

    def validate_and_accept(self):
        """Ensures required fields are filled before closing."""
        if not self.name_edit.text() or not self.id_edit.text() or not self.author_edit.text():
            QMessageBox.warning(self, "Missing Information",
                                "Plugin Name, ID, and Author are required fields.")
            return
        
        # If validation passes, accept the dialog
        self.accept()

    def get_plugin_data(self) -> dict:
        """Returns the entered data as a dictionary."""
        return {
            "name": self.name_edit.text().strip(),
            "id": self.id_edit.text().strip(),
            "author": self.author_edit.text().strip(),
            "description": self.desc_edit.text().strip(),
            "version": "1.0.0",  # Default starting version
            "entry_point": "plugin_main.py"
        }
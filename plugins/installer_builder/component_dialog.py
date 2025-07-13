# /plugins/installer_builder/component_dialog.py
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QFormLayout, QLineEdit,
                             QDialogButtonBox, QMessageBox, QCheckBox,
                             QPushButton, QHBoxLayout)
from PyQt6.QtCore import Qt

class ComponentDialog(QDialog):
    """A dialog for adding or editing an optional installer component."""
    def __init__(self, component_data=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Edit Installer Component")
        
        layout = QVBoxLayout(self)
        form = QFormLayout()

        self.id_edit = QLineEdit()
        self.id_edit.setPlaceholderText("e.g., extra_themes (no spaces/special chars)")
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("e.g., Extra Themes Pack")
        self.desc_edit = QLineEdit()
        self.desc_edit.setPlaceholderText("e.g., Installs additional themes for customization.")
        self.path_edit = QLineEdit()
        self.path_edit.setPlaceholderText("e.g., assets/extra_themes (relative to source dir)")
        
        form.addRow("Component ID:", self.id_edit)
        form.addRow("Display Name:", self.name_edit)
        form.addRow("Description:", self.desc_edit)
        form.addRow("Source Folder Path:", self.path_edit)

        self.required_check = QCheckBox("Component is required (cannot be unchecked by user)")
        form.addRow(self.required_check)

        layout.addLayout(form)
        
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self.validate_and_accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

        if component_data:
            self.id_edit.setText(component_data.get('id', ''))
            self.name_edit.setText(component_data.get('name', ''))
            self.desc_edit.setText(component_data.get('description', ''))
            self.path_edit.setText(component_data.get('source_path', ''))
            self.required_check.setChecked(component_data.get('required', False))
            
    def validate_and_accept(self):
        for field in [self.id_edit, self.name_edit, self.desc_edit, self.path_edit]:
            if not field.text().strip():
                QMessageBox.warning(self, "Missing Information", "All fields are required.")
                return
        self.accept()
        
    def get_data(self):
        return {
            "id": self.id_edit.text().strip(),
            "name": self.name_edit.text().strip(),
            "description": self.desc_edit.text().strip(),
            "source_path": self.path_edit.text().strip().replace('\\', '/'),
            "required": self.required_check.isChecked()
        }
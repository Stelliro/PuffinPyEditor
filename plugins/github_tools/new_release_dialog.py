# PuffinPyEditor/plugins/github_tools/new_release_dialog.py
from typing import Optional, Dict, Any
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QFormLayout, QDialogButtonBox,
                             QLineEdit, QTextEdit, QLabel, QCheckBox, QComboBox,
                             QHBoxLayout, QWidget, QGroupBox)
from PyQt6.QtCore import Qt
from app_core.source_control_manager import SourceControlManager
from utils.versioning import suggest_next_version


class NewReleaseDialog(QDialog):
    """
    A dialog for creating a new GitHub release. It collects tag name, title,
    notes, and other release options.
    """

    def __init__(self, project_path: str, git_manager: SourceControlManager,
                 parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.project_path = project_path
        self.git_manager = git_manager

        self.setWindowTitle("Create New Release")
        self.setMinimumWidth(500)

        self._setup_ui()
        self._connect_signals()
        self._populate_branches()
        self._validate_input()

    def _setup_ui(self):
        """Creates the main UI layout and widgets."""
        self.main_layout = QVBoxLayout(self)
        form_layout = QFormLayout()
        form_layout.setRowWrapPolicy(QFormLayout.RowWrapPolicy.WrapAllRows)
        self.main_layout.addLayout(form_layout)

        tag_layout = QHBoxLayout()
        suggested_tag = suggest_next_version()
        self.tag_edit = QLineEdit(suggested_tag)
        self.tag_edit.setPlaceholderText("e.g., v1.2.1")
        self.branch_combo = QComboBox()
        self.branch_combo.setToolTip(
            "Select the branch to create the release from.")
        tag_layout.addWidget(self.tag_edit, 2)
        tag_layout.addWidget(QLabel("on branch:"))
        tag_layout.addWidget(self.branch_combo, 1)
        tag_label = QLabel("<b>Tag Name:</b>")
        tag_label.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        form_layout.addRow(tag_label, tag_layout)

        self.title_edit = QLineEdit()
        self.title_edit.setText(suggested_tag)
        self.title_edit.setPlaceholderText(
            "e.g., Feature Update and Bug Fixes")
        form_layout.addRow(QLabel("<b>Release Title:</b>"), self.title_edit)

        self.notes_edit = QTextEdit()
        self.notes_edit.setPlaceholderText(
            "Describe the changes in this release (Markdown is supported).")
        self.notes_edit.setMinimumHeight(150)
        notes_label = QLabel("<b>Release Notes:</b>")
        notes_label.setAlignment(Qt.AlignmentFlag.AlignTop)
        form_layout.addRow(notes_label, self.notes_edit)

        options_group = QGroupBox("Options")
        options_layout = QVBoxLayout(options_group)
        self.prerelease_checkbox = QCheckBox("Mark as a pre-release")
        self.prerelease_checkbox.setToolTip(
            "Indicates that this is not a production-ready release.")
        options_layout.addWidget(self.prerelease_checkbox)
        options_layout.addStretch()
        form_layout.addRow(options_group)

        assets_group = QGroupBox("Release Assets")
        assets_layout = QVBoxLayout(assets_group)
        self.build_installer_checkbox = QCheckBox("Build and attach installer")
        self.build_installer_checkbox.setToolTip(
            "Runs the project's build script and uploads the setup file.")
        self.build_installer_checkbox.setChecked(True)
        assets_layout.addWidget(self.build_installer_checkbox)
        assets_layout.addStretch()
        form_layout.addRow(assets_group)

        self.button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok |
            QDialogButtonBox.StandardButton.Cancel
        )
        self.main_layout.addWidget(self.button_box)

    def _connect_signals(self):
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        self.tag_edit.textChanged.connect(self._validate_input)
        self.title_edit.textChanged.connect(self._validate_input)

    def _populate_branches(self):
        branches = self.git_manager.get_local_branches(self.project_path)
        self.branch_combo.addItems(branches)
        if 'main' in branches:
            self.branch_combo.setCurrentText('main')
        elif 'master' in branches:
            self.branch_combo.setCurrentText('master')

    def _validate_input(self):
        is_valid = bool(
            self.tag_edit.text().strip() and
            self.title_edit.text().strip() and
            self.branch_combo.currentText()
        )
        self.button_box.button(QDialogButtonBox.StandardButton.Ok).setEnabled(
            is_valid)

    def get_release_data(self) -> Dict[str, Any]:
        return {
            "tag": self.tag_edit.text().strip(),
            "title": self.title_edit.text().strip(),
            "notes": self.notes_edit.toPlainText().strip(),
            "prerelease": self.prerelease_checkbox.isChecked(),
            "target_branch": self.branch_combo.currentText(),
            "build_installer": self.build_installer_checkbox.isChecked()
        }
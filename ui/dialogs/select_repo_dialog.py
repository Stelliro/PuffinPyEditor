# PuffinPyEditor/ui/dialogs/select_repo_dialog.py
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QListWidget, QListWidgetItem,
                             QDialogButtonBox, QMessageBox, QLineEdit, QHBoxLayout, QLabel)
from PyQt6.QtCore import Qt
from app_core.github_manager import GitHubManager


class SelectRepoDialog(QDialog):
    def __init__(self, github_manager: GitHubManager, parent=None):
        super().__init__(parent)
        self.github_manager = github_manager
        self.selected_repo_data = None
        self.all_repos = []

        self.setWindowTitle("Select Target Repository")
        self.setMinimumSize(500, 400)
        self.main_layout = QVBoxLayout(self)

        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("Filter:"))
        self.filter_edit = QLineEdit()
        self.filter_edit.setPlaceholderText("Type to filter repositories...")
        search_layout.addWidget(self.filter_edit)
        self.main_layout.addLayout(search_layout)

        self.repo_list_widget = QListWidget()
        self.repo_list_widget.itemDoubleClicked.connect(self.accept)
        self.main_layout.addWidget(self.repo_list_widget)

        self.button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        self.main_layout.addWidget(self.button_box)

        self.button_box.button(QDialogButtonBox.StandardButton.Ok).setEnabled(False)

        self._connect_signals()
        self.github_manager.list_repos()

    def _connect_signals(self):
        self.github_manager.repos_ready.connect(self._handle_repos_loaded)
        self.github_manager.operation_failed.connect(self._on_load_failed)
        self.filter_edit.textChanged.connect(self._filter_repo_list)

    def _handle_repos_loaded(self, repos):
        self.all_repos = sorted(repos, key=lambda r: r['full_name'].lower())
        self._populate_repo_list()

        if self.repo_list_widget.count() > 0:
            self.button_box.button(QDialogButtonBox.StandardButton.Ok).setEnabled(True)
            self.repo_list_widget.setCurrentRow(0)

    def _filter_repo_list(self):
        filter_text = self.filter_edit.text().lower()
        self.repo_list_widget.clear()

        for repo in self.all_repos:
            if filter_text in repo['full_name'].lower():
                item = QListWidgetItem(repo['full_name'])
                item.setData(1, repo)
                self.repo_list_widget.addItem(item)

    def _populate_repo_list(self):
        self._filter_repo_list()

    def _on_load_failed(self, error_message):
        QMessageBox.critical(self, "Failed to Load Repositories", error_message)
        self.cleanup()
        self.reject()

    def accept(self):
        current_item = self.repo_list_widget.currentItem()
        if not current_item:
            QMessageBox.warning(self, "No Selection", "Please select a repository.")
            return

        self.selected_repo_data = current_item.data(1)
        super().accept()

    def cleanup(self):
        """Disconnect signals to avoid issues if dialog is reused."""
        try:
            self.github_manager.repos_ready.disconnect(self._handle_repos_loaded)
            self.github_manager.operation_failed.disconnect(self._on_load_failed)
        except TypeError:
            pass  # Signal was already disconnected
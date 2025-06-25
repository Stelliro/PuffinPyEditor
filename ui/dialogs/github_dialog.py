# PuffinPyEditor/ui/dialogs/github_dialog.py
import os
from typing import Optional, List, Dict, Any
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QWidget,
                             QSplitter, QLabel, QListWidget, QListWidgetItem,
                             QPushButton, QMessageBox, QFileDialog)
from PyQt6.QtCore import Qt, pyqtSignal
from app_core.github_manager import GitHubManager
from app_core.source_control_manager import SourceControlManager
import qtawesome as qta


class GitHubDialog(QDialog):
    """
    A dialog for browsing and cloning a user's GitHub repositories.
    """
    project_cloned = pyqtSignal(str)

    def __init__(self, github_manager: GitHubManager,
                 git_manager: SourceControlManager, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.github_manager = github_manager
        self.git_manager = git_manager

        self.setWindowTitle("GitHub Repository Management")
        self.setMinimumSize(800, 600)

        self._setup_ui()
        self._connect_signals()

    def _setup_ui(self):
        """Creates the main UI layout and widgets."""
        layout = QVBoxLayout(self)
        splitter = QSplitter(Qt.Orientation.Horizontal)
        layout.addWidget(splitter)

        left_pane = self._create_repo_list_pane()
        right_pane = self._create_details_pane()

        splitter.addWidget(left_pane)
        splitter.addWidget(right_pane)
        splitter.setSizes([300, 500])

    def _create_repo_list_pane(self) -> QWidget:
        """Creates the left pane for listing repositories."""
        pane = QWidget()
        layout = QVBoxLayout(pane)
        layout.setContentsMargins(0, 0, 0, 0)

        toolbar_layout = QHBoxLayout()
        self.refresh_button = QPushButton("Refresh List")
        self.refresh_button.setIcon(qta.icon('fa5s.sync-alt'))
        toolbar_layout.addWidget(self.refresh_button)
        toolbar_layout.addStretch()

        self.repo_list = QListWidget()

        layout.addLayout(toolbar_layout)
        layout.addWidget(self.repo_list)
        return pane

    def _create_details_pane(self) -> QWidget:
        """Creates the right pane for showing repository details and branches."""
        pane = QWidget()
        layout = QVBoxLayout(pane)

        self.repo_details_label = QLabel("<i>Select a repository...</i>")
        self.repo_details_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.repo_details_label.setWordWrap(True)
        layout.addWidget(self.repo_details_label, 1)

        layout.addWidget(QLabel("<b>Branches:</b>"))
        self.branch_list = QListWidget()
        layout.addWidget(self.branch_list, 2)

        self.clone_button = QPushButton("Clone Selected Branch")
        self.clone_button.setIcon(qta.icon('fa5s.download'))
        self.clone_button.setEnabled(False)
        layout.addWidget(self.clone_button)
        return pane

    def _connect_signals(self):
        """Connects widget signals to their slots."""
        self.github_manager.repos_ready.connect(self.populate_repo_list)
        self.github_manager.branches_ready.connect(self.populate_branch_list)
        self.github_manager.operation_failed.connect(self._on_operation_failed)
        self.repo_list.currentItemChanged.connect(self.on_repo_selected)
        self.refresh_button.clicked.connect(self.github_manager.list_repos)
        self.clone_button.clicked.connect(self.on_clone_clicked)

    def showEvent(self, event):
        """Overridden to auto-refresh the repo list when shown."""
        super().showEvent(event)
        self.refresh_button.click()

    def closeEvent(self, event):
        """Overridden to disconnect signals and prevent memory leaks."""
        try:
            self.github_manager.repos_ready.disconnect(self.populate_repo_list)
            self.github_manager.branches_ready.disconnect(self.populate_branch_list)
            self.github_manager.operation_failed.disconnect(self._on_operation_failed)
        except TypeError:
            # Signals might already be disconnected
            pass
        super().closeEvent(event)

    def populate_repo_list(self, repos: List[Dict[str, Any]]):
        """Fills the repository list widget with data from the API."""
        self.repo_list.clear()
        for repo in sorted(repos, key=lambda r: r['name'].lower()):
            item = QListWidgetItem(repo['name'])
            item.setToolTip(repo['full_name'])
            item.setData(Qt.ItemDataRole.UserRole, repo)
            self.repo_list.addItem(item)

    def populate_branch_list(self, branches: List[Dict[str, Any]]):
        """Fills the branch list widget."""
        self.branch_list.clear()
        for branch in branches:
            item = QListWidgetItem(branch['name'])
            item.setData(Qt.ItemDataRole.UserRole, branch)
            self.branch_list.addItem(item)
        if branches:
            self.branch_list.setCurrentRow(0)

    def on_repo_selected(self, current_item: QListWidgetItem):
        """Handles the user selecting a repository from the list."""
        self.branch_list.clear()
        self.clone_button.setEnabled(False)

        if not current_item:
            self.repo_details_label.setText("<i>Select a repository...</i>")
            return

        repo_data = current_item.data(Qt.ItemDataRole.UserRole)
        desc = repo_data.get('description') or 'No description provided.'
        self.repo_details_label.setText(
            f"<b>{repo_data['full_name']}</b><br/><small>{desc}</small>"
        )
        self.github_manager.list_branches(repo_data['full_name'])
        self.clone_button.setEnabled(True)

    def on_clone_clicked(self):
        """Handles the clone button click."""
        repo_item = self.repo_list.currentItem()
        branch_item = self.branch_list.currentItem()
        if not repo_item or not branch_item:
            QMessageBox.warning(self, "Selection Required", "Please select a repository and a branch.")
            return

        repo_data = repo_item.data(Qt.ItemDataRole.UserRole)
        branch_data = branch_item.data(Qt.ItemDataRole.UserRole)

        path = QFileDialog.getExistingDirectory(self, f"Select Folder to Clone '{repo_data['name']}' Into")
        if not path:
            return

        clone_path = os.path.join(path, repo_data['name'])
        if os.path.exists(clone_path):
            QMessageBox.critical(self, "Folder Exists", f"The folder '{repo_data['name']}' already exists at this location.")
            return

        # Delegate the actual git operation to the git_manager
        self.git_manager.clone_repo(repo_data['clone_url'], path, branch_data['name'])
        QMessageBox.information(self, "Clone Started",
                                "Cloning has started. The project will open automatically when complete.")
        self.project_cloned.emit(clone_path)
        self.accept()

    def _on_operation_failed(self, error_message: str):
        """Shows a critical error message box."""
        QMessageBox.critical(self, "GitHub Error", error_message)
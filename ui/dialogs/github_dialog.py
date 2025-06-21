# PuffinPyEditor/ui/dialogs/github_dialog.py
import os  # <<< FIX: Added the missing import
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QWidget, QSplitter,
                             QLabel, QListWidget, QListWidgetItem, QPushButton, QMessageBox, QFileDialog)
from PyQt6.QtCore import Qt, pyqtSignal
from app_core.github_manager import GitHubManager
from app_core.source_control_manager import SourceControlManager
import qtawesome as qta


class GitHubDialog(QDialog):
    project_cloned = pyqtSignal(str)

    def __init__(self, github_manager: GitHubManager, git_manager: SourceControlManager, parent=None):
        super().__init__(parent)
        self.github_manager = github_manager
        self.git_manager = git_manager
        self.setWindowTitle("GitHub Repository Management")
        self.setMinimumSize(800, 600)
        self._setup_ui()
        self._connect_signals()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        splitter = QSplitter(Qt.Orientation.Horizontal)
        layout.addWidget(splitter)
        left_pane = QWidget()
        left_layout = QVBoxLayout(left_pane)
        left_layout.setContentsMargins(0, 0, 0, 0)
        right_pane = QWidget()
        right_layout = QVBoxLayout(right_pane)
        splitter.addWidget(left_pane)
        splitter.addWidget(right_pane)

        repo_actions_layout = QHBoxLayout()
        self.refresh_button = QPushButton("Refresh List")
        self.refresh_button.setIcon(qta.icon('fa5s.sync-alt'))
        repo_actions_layout.addWidget(self.refresh_button)
        repo_actions_layout.addStretch()
        self.repo_list = QListWidget()
        left_layout.addLayout(repo_actions_layout)
        left_layout.addWidget(self.repo_list)

        self.repo_details_label = QLabel("<i>Select a repository to see details.</i>")
        self.repo_details_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.repo_details_label.setWordWrap(True)
        right_layout.addWidget(self.repo_details_label, 1)
        right_layout.addWidget(QLabel("<b>Branches:</b>"))
        self.branch_list = QListWidget()
        self.clone_button = QPushButton("Clone Selected Branch")
        self.clone_button.setIcon(qta.icon('fa5s.download'))
        right_layout.addWidget(self.branch_list, 2)
        right_layout.addWidget(self.clone_button)
        self.clone_button.setEnabled(False)

    def _connect_signals(self):
        self.github_manager.repos_ready.connect(self.populate_repo_list)
        self.github_manager.branches_ready.connect(self.populate_branch_list)
        self.github_manager.operation_failed.connect(lambda msg: QMessageBox.critical(self, "GitHub Error", msg))

        self.repo_list.currentItemChanged.connect(self.on_repo_selected)
        self.refresh_button.clicked.connect(self.github_manager.list_repos)
        self.clone_button.clicked.connect(self.on_clone_clicked)

    def showEvent(self, event):
        super().showEvent(event)
        self.refresh_button.click()

    def populate_repo_list(self, repos):
        self.repo_list.clear()
        for repo in sorted(repos, key=lambda r: r['name'].lower()):
            item = QListWidgetItem(repo['name'])
            item.setData(Qt.ItemDataRole.UserRole, repo)
            self.repo_list.addItem(item)

    def populate_branch_list(self, branches):
        self.branch_list.clear()
        for branch in branches:
            item = QListWidgetItem(branch['name'])
            item.setData(Qt.ItemDataRole.UserRole, branch)
            self.branch_list.addItem(item)
        if branches:
            self.branch_list.setCurrentRow(0)

    def on_repo_selected(self, item):
        self.branch_list.clear()
        self.clone_button.setEnabled(False)
        if not item:
            self.repo_details_label.setText("<i>Select a repository to see details.</i>")
            return

        repo_data = item.data(Qt.ItemDataRole.UserRole)
        self.repo_details_label.setText(
            f"<b>{repo_data['full_name']}</b><br/><small>{repo_data.get('description') or 'No description'}</small>")
        self.github_manager.list_branches(repo_data['full_name'])
        self.clone_button.setEnabled(True)

    def on_clone_clicked(self):
        repo_item = self.repo_list.currentItem()
        branch_item = self.branch_list.currentItem()
        if not repo_item or not branch_item:
            QMessageBox.warning(self, "Error", "Select a repository and a branch.")
            return

        repo_data = repo_item.data(Qt.ItemDataRole.UserRole)
        branch_data = branch_item.data(Qt.ItemDataRole.UserRole)

        path = QFileDialog.getExistingDirectory(self, f"Select folder to clone '{repo_data['name']}' into")
        if not path:
            return

        clone_path = os.path.join(path, repo_data['name'])
        if os.path.exists(clone_path):
            QMessageBox.critical(self, "Error",
                                 f"A folder named '{repo_data['name']}' already exists in the selected directory.")
            return

        self.git_manager.clone_repo(repo_data['clone_url'], path, branch_data['name'])
        QMessageBox.information(self, "Clone Started",
                                "Repository cloning has started. The project will open automatically when complete.")
        self.project_cloned.emit(clone_path)
        self.accept()
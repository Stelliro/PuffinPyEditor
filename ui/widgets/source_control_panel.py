# PuffinPyEditor/ui/widgets/source_control_panel.py
import os
from typing import List, Dict, Optional
from git import Repo, InvalidGitRepositoryError, Actor
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTreeWidget,
                             QTreeWidgetItem, QMenu, QMessageBox, QLabel, QHeaderView, QLineEdit)
from PyQt6.QtGui import QColor
from PyQt6.QtCore import Qt, pyqtSignal, QPoint
import qtawesome as qta

from app_core.project_manager import ProjectManager
from app_core.source_control_manager import SourceControlManager
from app_core.github_manager import GitHubManager
from app_core.puffin_api import PuffinPluginAPI


class ProjectSourceControlPanel(QWidget):
    """
    A widget that displays the Git status for all open projects and provides
    controls for common Git operations.
    """
    publish_repo_requested = pyqtSignal(str)
    create_release_requested = pyqtSignal(str)
    link_to_remote_requested = pyqtSignal(str)
    change_visibility_requested = pyqtSignal(str)

    def __init__(self, project_manager: ProjectManager,
                 git_manager: SourceControlManager,
                 github_manager: GitHubManager,
                 puffin_api: PuffinPluginAPI, parent=None):
        super().__init__(parent)
        self.project_manager = project_manager
        self.git_manager = git_manager
        self.github_manager = github_manager
        self.api = puffin_api
        self.staged_color = QColor("#A7C080")
        self.unstaged_color = QColor("#DBBC7F")
        self._setup_ui()
        self._connect_signals()
        self.update_icons()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        toolbar_layout = QHBoxLayout()
        self.refresh_all_button = QPushButton("Refresh")
        self.pull_button = QPushButton("Pull")
        self.push_button = QPushButton("Push")
        self.new_release_button = QPushButton("New Release...")
        self.cleanup_tags_button = QPushButton("Cleanup Tags")
        self.cleanup_tags_button.setToolTip("Delete remote tags that are not part of a release.")
        
        toolbar_layout.addWidget(self.refresh_all_button)
        toolbar_layout.addWidget(self.pull_button)
        toolbar_layout.addWidget(self.push_button)
        toolbar_layout.addStretch()
        toolbar_layout.addWidget(self.cleanup_tags_button)
        toolbar_layout.addWidget(self.new_release_button)
        layout.addLayout(toolbar_layout)

        self.project_tree = QTreeWidget()
        self.project_tree.setHeaderLabels(["Project / Changes", ""])
        self.project_tree.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        header = self.project_tree.header()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        layout.addWidget(self.project_tree)

        self.commit_message_edit = QLineEdit()
        self.commit_message_edit.setPlaceholderText("Commit message...")
        self.commit_button = QPushButton("Commit All")
        commit_layout = QHBoxLayout()
        commit_layout.addWidget(self.commit_message_edit)
        commit_layout.addWidget(self.commit_button)
        layout.addLayout(commit_layout)
        self.status_label = QLabel("Ready.")
        layout.addWidget(self.status_label)

        self.action_buttons = [self.refresh_all_button, self.pull_button, self.push_button,
                               self.new_release_button, self.commit_button, self.cleanup_tags_button]

    def _connect_signals(self):
        self.git_manager.summaries_ready.connect(self._populate_tree)
        self.git_manager.status_updated.connect(self._update_project_files)
        self.git_manager.git_error.connect(self._handle_git_error)
        self.git_manager.git_success.connect(self._handle_git_success)
        self.github_manager.operation_success.connect(self._handle_git_success)
        self.github_manager.operation_failed.connect(self._handle_git_error)
        
        self.refresh_all_button.clicked.connect(self.refresh_all_projects)
        self.push_button.clicked.connect(self._on_push_clicked)
        self.pull_button.clicked.connect(self._on_pull_clicked)
        self.new_release_button.clicked.connect(self._on_new_release_clicked)
        self.cleanup_tags_button.clicked.connect(self._on_cleanup_tags_clicked)
        self.commit_button.clicked.connect(self._on_commit_clicked)
        self.project_tree.customContextMenuRequested.connect(self._show_context_menu)

    def set_ui_locked(self, locked: bool, message: str = ""):
        for button in self.action_buttons:
            button.setEnabled(not locked)
        self.commit_message_edit.setEnabled(not locked)
        self.status_label.setText(message)

    def update_icons(self):
        self.refresh_all_button.setIcon(qta.icon('mdi.refresh'))
        self.pull_button.setIcon(qta.icon('mdi.arrow-down-bold-outline'))
        self.push_button.setIcon(qta.icon('mdi.arrow-up-bold-outline'))
        self.new_release_button.setIcon(qta.icon('mdi.tag-outline'))
        self.cleanup_tags_button.setIcon(qta.icon('mdi.tag-remove-outline'))
        self.commit_button.setIcon(qta.icon('mdi.check'))

    def _get_selected_project_path(self) -> Optional[str]:
        item = self.project_tree.currentItem()
        if not item:
            return self.project_manager.get_active_project_path()
        while parent := item.parent():
            item = parent
        data = item.data(0, Qt.ItemDataRole.UserRole)
        return data.get('path') if data else None

    def _on_push_clicked(self):
        if path := self._get_selected_project_path():
            self.set_ui_locked(True, f"Pushing {os.path.basename(path)}...")
            self.git_manager.push(path)

    def _on_pull_clicked(self):
        if path := self._get_selected_project_path():
            self.set_ui_locked(True, f"Pulling {os.path.basename(path)}...")
            self.git_manager.pull(path)

    def _on_new_release_clicked(self):
        if path := self._get_selected_project_path():
            self.create_release_requested.emit(path)

    def _on_commit_clicked(self):
        path = self._get_selected_project_path()
        message = self.commit_message_edit.text().strip()
        if not path or not message:
            QMessageBox.warning(self, "Commit Failed", "A project must be selected "
                                "and a commit message must be provided.")
            return

        gh_tools = self.api.get_plugin_instance("github_tools")
        if not gh_tools or not gh_tools.ensure_git_identity(path):
            return  # The ensure_git_identity method will show its own error message.

        # Now that we know the identity is correct, we can get the Actor and commit.
        try:
            repo = Repo(path)
            with repo.config_reader() as cr:
                name = cr.get_value('user', 'name')
                email = cr.get_value('user', 'email')
            author = Actor(name, email)
        except Exception as e:
            self.api.show_message("critical", "Commit Failed", f"Could not read Git author info to create commit: {e}")
            return

        self.set_ui_locked(True, f"Committing changes in {os.path.basename(path)}...")
        self.git_manager.commit_files(path, message, author)

    def _on_cleanup_tags_clicked(self):
        """Handles the logic when the 'Cleanup Tags' button is clicked."""
        path = self._get_selected_project_path()
        if not path:
            QMessageBox.warning(self, "No Project Selected", "Please select a Git project.")
            return

        try:
            repo = Repo(path)
            if not repo.remotes:
                QMessageBox.warning(self, "No Remote", "The selected project does not have a remote configured.")
                return
            remote_url = repo.remotes.origin.url
            owner, repo_name = self.git_manager.parse_git_url(remote_url)
            if not owner or not repo_name:
                QMessageBox.critical(self, "Error", "Could not parse owner/repo from the remote URL.")
                return
        except Exception as e:
            QMessageBox.critical(self, "Git Error", f"Could not analyze repository: {e}")
            return
            
        reply = QMessageBox.question(
            self,
            "Confirm Tag Cleanup",
            "This will permanently delete all tags from the remote repository "
            f"<b>{owner}/{repo_name}</b> that are NOT associated with a GitHub Release.\n\n"
            "This action cannot be undone. Are you sure you want to continue?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.Cancel,
            QMessageBox.StandardButton.Cancel
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.set_ui_locked(True, f"Cleaning up tags for {owner}/{repo_name}...")
            self.github_manager.cleanup_orphaned_tags(owner, repo_name)
    
    def _on_fix_branch_mismatch_clicked(self, path: str):
        reply = QMessageBox.warning(
            self, "Confirm Branch Fix", "This will perform a force-push and delete "
            "the 'master' branch from the remote. Are you sure?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.Cancel,
            QMessageBox.StandardButton.Cancel
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.set_ui_locked(True, f"Fixing branch mismatch for {os.path.basename(path)}...")
            self.git_manager.fix_branch_mismatch(path)

    def _handle_git_success(self, message: str, data: dict):
        if data.get("deleted_tags") is not None:
             QMessageBox.information(self, "Cleanup Complete", message)

        self.set_ui_locked(False, f"Success: {message}")
        self.refresh_all_projects()
        if "committed" in message.lower() and not data.get('no_changes'):
            self.commit_message_edit.clear()

    def _handle_git_error(self, error_message: str):
        self.set_ui_locked(False, f"Error: {error_message}")
        QMessageBox.critical(self, "Operation Failed", error_message)
        self.refresh_all_projects()

    def refresh_all_projects(self):
        self.set_ui_locked(True, "Fetching project statuses...")
        all_projects = self.project_manager.get_open_projects()
        if all_projects:
            self.git_manager.get_summaries(all_projects)
        else:
            self.project_tree.clear()
            self.set_ui_locked(False, "No projects open.")

    def _populate_tree(self, summaries: Dict[str, Dict]):
        self.project_tree.clear()
        git_project_paths = summaries.keys()
        for path in self.project_manager.get_open_projects():
            project_name = os.path.basename(path)
            if path in git_project_paths:
                summary = summaries[path]
                item = QTreeWidgetItem(self.project_tree, [project_name, f"Branch: {summary.get('branch', 'N/A')}"])
                item.setData(0, Qt.ItemDataRole.UserRole, {'type': 'project', 'path': path})
                item.setIcon(0, qta.icon('mdi.git'))
                self.git_manager.get_status(path)
            else:
                item = QTreeWidgetItem(self.project_tree, [project_name])
                item.setData(0, Qt.ItemDataRole.UserRole, {'type': 'non-git-project', 'path': path})
                item.setIcon(0, qta.icon('mdi.folder-outline', color='gray'))
                actions_widget = QWidget()
                actions_layout = QHBoxLayout(actions_widget)
                actions_layout.setContentsMargins(0, 0, 0, 0)
                link_button = QPushButton("Link...")
                link_button.setToolTip("Link this local folder to an existing GitHub repository")
                link_button.clicked.connect(lambda _, p=path: self.link_to_remote_requested.emit(p))
                publish_button = QPushButton("Publish...")
                publish_button.setToolTip("Create a new repository on GitHub from this project")
                publish_button.clicked.connect(lambda _, p=path: self.publish_repo_requested.emit(p))
                actions_layout.addStretch()
                actions_layout.addWidget(link_button)
                actions_layout.addWidget(publish_button)
                self.project_tree.setItemWidget(item, 1, actions_widget)
        self.set_ui_locked(False, "Ready.")
        if self.project_tree.topLevelItemCount() > 0:
            self.project_tree.setCurrentItem(self.project_tree.topLevelItem(0))

    def _update_project_files(self, staged: List[str], unstaged: List[str], repo_path: str):
        root = self.project_tree.invisibleRootItem()
        for i in range(root.childCount()):
            project_item = root.child(i)
            item_data = project_item.data(0, Qt.ItemDataRole.UserRole)
            if item_data and item_data.get('path') == repo_path:
                project_item.takeChildren()
                for f in sorted(list(set(staged + unstaged))):
                    child = QTreeWidgetItem(project_item, [f])
                    child.setForeground(0, self.staged_color if f in staged else self.unstaged_color)
                project_item.setExpanded(True)
                break

    def _show_context_menu(self, position: QPoint):
        item = self.project_tree.itemAt(position)
        if not item:
            return
        data = item.data(0, Qt.ItemDataRole.UserRole)
        if not (data and (path := data.get('path'))):
            return

        menu = QMenu()
        if data['type'] == 'project':
            menu.addAction(qta.icon('mdi.refresh'), "Refresh Status",
                           lambda: self.git_manager.get_status(path))
            vis_action = menu.addAction(qta.icon('mdi.eye-outline'), "Change GitHub Visibility...")
            vis_action.triggered.connect(lambda: self.change_visibility_requested.emit(path))
            try:
                branches = [b.name for b in Repo(path).branches]
                if 'main' in branches and 'master' in branches:
                    menu.addSeparator()
                    fix_action = menu.addAction(qta.icon('mdi.alert-outline',
                                                         color='orange'), "Fix Branch Mismatch...")
                    fix_action.triggered.connect(lambda: self._on_fix_branch_mismatch_clicked(path))
            except (InvalidGitRepositoryError, TypeError):
                pass
        elif data['type'] == 'non-git-project':
            menu.addAction(qta.icon('mdi.link-variant'), "Link to GitHub Repo...",
                           lambda: self.link_to_remote_requested.emit(path))
            menu.addAction(qta.icon('mdi.cloud-upload-outline'), "Publish to GitHub...",
                           lambda: self.publish_repo_requested.emit(path))

        if menu.actions():
            menu.exec(self.project_tree.viewport().mapToGlobal(position))
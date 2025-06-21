# PuffinPyEditor/ui/widgets/project_source_control_panel.py
import os
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTreeWidget,
                             QTreeWidgetItem, QMenu, QMessageBox, QLabel, QHeaderView, QLineEdit)
from PyQt6.QtGui import QAction, QColor
from PyQt6.QtCore import Qt, pyqtSignal
import qtawesome as qta

from app_core.project_manager import ProjectManager
from app_core.source_control_manager import SourceControlManager
from utils.logger import log


class ProjectSourceControlPanel(QWidget):
    manage_remotes_requested = pyqtSignal()
    publish_repo_requested = pyqtSignal(str)
    create_release_requested = pyqtSignal(str)
    link_to_remote_requested = pyqtSignal(str)
    change_visibility_requested = pyqtSignal(str)

    def __init__(self, project_manager: ProjectManager, git_manager: SourceControlManager, parent=None):
        super().__init__(parent)
        self.project_manager = project_manager
        self.git_manager = git_manager
        self.staged_color = QColor("#A7C080")
        self.unstaged_color = QColor("#DBBC7F")
        self.repo_states = {}
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
        toolbar_layout.addWidget(self.refresh_all_button)
        toolbar_layout.addWidget(self.pull_button)
        toolbar_layout.addWidget(self.push_button)
        toolbar_layout.addStretch()
        toolbar_layout.addWidget(self.new_release_button)
        layout.addLayout(toolbar_layout)

        self.project_tree = QTreeWidget()
        self.project_tree.setHeaderLabels(["Project / Changes", ""])
        header = self.project_tree.header()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        layout.addWidget(self.project_tree)

        self.commit_message_edit = QLineEdit()
        self.commit_message_edit.setPlaceholderText("Commit message...")
        self.commit_button = QPushButton("Commit All and Push")
        commit_layout = QHBoxLayout()
        commit_layout.addWidget(self.commit_message_edit)
        commit_layout.addWidget(self.commit_button)
        layout.addLayout(commit_layout)

        self.status_label = QLabel("Ready.")
        layout.addWidget(self.status_label)

    def _connect_signals(self):
        self.git_manager.summaries_ready.connect(self._populate_tree)
        self.git_manager.status_updated.connect(self._update_project_files)
        self.git_manager.git_error.connect(lambda err: self.status_label.setText(f"Error: {err}"))
        self.git_manager.git_success.connect(self._handle_git_success)

        self.refresh_all_button.clicked.connect(self.refresh_all_projects)
        self.push_button.clicked.connect(self._on_push_clicked)
        self.pull_button.clicked.connect(self._on_pull_clicked)
        self.new_release_button.clicked.connect(self._on_new_release_clicked)
        self.commit_button.clicked.connect(self._on_commit_and_push_clicked)
        self.project_tree.customContextMenuRequested.connect(self._show_context_menu)

    def update_icons(self):
        self.refresh_all_button.setIcon(qta.icon('fa5s.sync-alt'))
        self.pull_button.setIcon(qta.icon('fa5s.arrow-down'))
        self.push_button.setIcon(qta.icon('fa5s.arrow-up'))
        self.new_release_button.setIcon(qta.icon('fa5s.tag'))
        self.commit_button.setIcon(qta.icon('fa5s.check'))

    def _get_active_project_path(self):
        item = self.project_tree.currentItem()
        if not item: return self.project_manager.get_active_project_path()
        while item.parent():
            item = item.parent()
        data = item.data(0, Qt.ItemDataRole.UserRole)
        return data.get('path') if data else None

    def _on_push_clicked(self):
        path = self._get_active_project_path()
        if path: self.git_manager.push(path)

    def _on_pull_clicked(self):
        path = self._get_active_project_path()
        if path: self.git_manager.pull(path)

    def _on_new_release_clicked(self):
        path = self._get_active_project_path()
        if path: self.create_release_requested.emit(path)

    def _on_commit_and_push_clicked(self):
        path = self._get_active_project_path()
        if not path: return
        message = self.commit_message_edit.text().strip()
        if not message:
            QMessageBox.warning(self, "Commit Failed", "Commit message cannot be empty.")
            return
        self.git_manager.commit_files(path, message)

    def _handle_git_success(self, message, data):
        self.status_label.setText(f"Success: {message}")
        if data.get('no_changes'):
            return

        if "Committed" in message:
            self.commit_message_edit.clear()
            path = data.get('repo_path')
            if path: self.git_manager.push(path)
        else:
            self.refresh_all_projects()

    def refresh_all_projects(self):
        self.repo_states.clear()
        self.status_label.setText("Fetching project statuses...")
        all_projects = self.project_manager.get_open_projects()
        if all_projects:
            self.git_manager.get_summaries(all_projects)
        else:
            self.project_tree.clear()
            self.status_label.setText("No projects open.")

    def _populate_tree(self, summaries: dict):
        self.project_tree.clear()
        all_projects = self.project_manager.get_open_projects()
        git_project_paths = summaries.keys()
        self.project_tree.setCurrentItem(None)

        for path in all_projects:
            project_name = os.path.basename(path)
            if path in git_project_paths:
                summary = summaries[path]
                branch = summary.get('branch', 'N/A')
                item = QTreeWidgetItem(self.project_tree, [project_name, f"Branch: {branch}"])
                item.setData(0, Qt.ItemDataRole.UserRole, {'type': 'project', 'path': path})
                item.setIcon(0, qta.icon('fa5b.git-alt'))
                self.git_manager.get_status(path)
            else:
                item = QTreeWidgetItem(self.project_tree, [project_name])
                item.setData(0, Qt.ItemDataRole.UserRole, {'type': 'non-git-project', 'path': path})
                item.setIcon(0, qta.icon('fa5.folder', color='gray'))
                actions_widget = QWidget()
                actions_layout = QHBoxLayout(actions_widget)
                actions_layout.setContentsMargins(0, 0, 0, 0)
                actions_layout.setSpacing(5)
                link_button = QPushButton("Link...")
                link_button.setIcon(qta.icon('fa5s.link'))
                link_button.setToolTip("Link this local folder to an existing GitHub repository")
                link_button.clicked.connect(lambda checked, p=path: self.link_to_remote_requested.emit(p))
                publish_button = QPushButton("Publish...")
                publish_button.setIcon(qta.icon('fa5s.cloud-upload-alt'))
                publish_button.setToolTip("Create a new repository on GitHub from this project")
                publish_button.clicked.connect(lambda checked, p=path: self.publish_repo_requested.emit(p))
                actions_layout.addStretch()
                actions_layout.addWidget(link_button)
                actions_layout.addWidget(publish_button)
                self.project_tree.setItemWidget(item, 1, actions_widget)

        self.status_label.setText("Ready.")
        if self.project_tree.topLevelItemCount() > 0:
            self.project_tree.setCurrentItem(self.project_tree.topLevelItem(0))

    def _update_project_files(self, staged, unstaged, repo_path):
        all_changes = sorted(list(set(staged + unstaged)))
        is_clean = not all_changes
        self.repo_states[repo_path] = {'is_clean': is_clean, 'all_changes': all_changes}

        root = self.project_tree.invisibleRootItem()
        for i in range(root.childCount()):
            project_item = root.child(i)
            item_data = project_item.data(0, Qt.ItemDataRole.UserRole)
            if item_data and item_data.get('path') == repo_path:
                project_item.takeChildren()
                for f in all_changes:
                    child = QTreeWidgetItem(project_item, [f])
                    child.setForeground(0, self.unstaged_color if f in unstaged else self.staged_color)
                project_item.setExpanded(True)
                break

    def _show_context_menu(self, position):
        item = self.project_tree.itemAt(position)
        if not item: return
        data = item.data(0, Qt.ItemDataRole.UserRole) if item else None
        if not data: return

        path = data['path']
        menu = QMenu()

        if data['type'] == 'project':
            menu.addAction(qta.icon('fa5s.sync-alt'), "Refresh Status", lambda: self.git_manager.get_status(path))
            menu.addSeparator()
            vis_action = menu.addAction(qta.icon('fa5s.eye'), "Change Visibility...")
            vis_action.triggered.connect(lambda: self.change_visibility_requested.emit(path))
        elif data['type'] == 'non-git-project':
            menu.addAction(qta.icon('fa5s.link'), "Link to Existing GitHub Repo...",
                           lambda: self.link_to_remote_requested.emit(path))
            menu.addAction(qta.icon('fa5s.cloud-upload-alt'), "Publish as New GitHub Repo...",
                           lambda: self.publish_repo_requested.emit(path))

        if menu.actions():
            menu.exec(self.project_tree.viewport().mapToGlobal(position))
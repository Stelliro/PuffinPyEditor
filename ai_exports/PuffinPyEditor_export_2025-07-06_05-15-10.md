# Project Export: PuffinPyEditor
## Export Timestamp: 2025-07-06T05:15:10.316243
---

## AI Instructions
You are Inspector Val, a world-renowned digital detective. Code is your crime scene. A bug has been reported, and you've been called in to solve the case. Your approach is methodical, logical, and evidence-based. You will analyze the provided code and context (like a traceback) to find the root cause and prescribe a definitive fix.

## Guidelines & Rules
- Begin your report with a 'Case File Summary', clearly stating the reported issue (the bug) and its user-facing impact.
- Present 'The Evidence'. This section must include the problematic code snippets and the full stack trace or error message.
- Identify 'The Suspects'. List the specific variables, functions, or expressions that are potentially responsible for the bug.
- Formulate the 'Primary Hypothesis'. In a clear, step-by-step narrative, explain exactly how you believe the bug is occurring.
- Provide 'The Solution'. Offer a corrected code snippet that fixes the bug, with comments explaining the change.
- Conclude with a 'Case Closed' statement, briefly explaining how the fix prevents the issue from recurring and any lessons learned.

## Golden Rules
1. Only edit and add features, the only features should stay unless asked to be removed, or may be completely redundant.
2. any scripts over 1000 lines, please write in a new response.
3. multiple scripts together exceeding 2000 lines together need to be separated into smaller responses, (example: these scripts have 2340 lines together I'm going to separate it into 2 messages that way i dont lose formatting and dont accidentally remove any features)
4. Do not remove any code that is unrelated to the fix, only remove code if it is being substituted or is not needed anymore.

---

## Project Files

Here is the project context you need to work with.
## File Tree
```
/PuffinPyEditor
 ├── app_core
 │   └── project_manager.py
 └── plugins
     └── github_tools
         ├── __init__.py
         ├── github_dialog.py
         ├── new_release_dialog.py
         ├── plugin.json
         ├── plugin_main.py
         └── select_repo_dialog.py

```
## File Contents
### File: `/app_core/project_manager.py`

```python
# PuffinPyEditor/app_core/project_manager.py
import os
import datetime
import zipfile
from pathlib import Path
from typing import List, Tuple, Optional, Dict

# NEW: Import QObject and pyqtSignal for signals
from PyQt6.QtCore import QObject, pyqtSignal

from .settings_manager import settings_manager
from utils.logger import log


class ProjectManager(QObject):  # MODIFIED: Inherit from QObject
    """Manages the state of open projects and project-wide operations."""

    # NEW: Add the required signal
    projects_changed = pyqtSignal()

    def __init__(self):
        super().__init__()  # NEW: Call the QObject constructor
        self._open_projects: List[str] = []
        self._active_project_path: Optional[str] = None
        self._load_session()
        log.info(
            f"ProjectManager initialized with {len(self._open_projects)} "
            "projects."
        )

    def _load_session(self):
        """Loads the list of open projects from the settings."""
        open_projects = settings_manager.get("open_projects", [])
        active_project = settings_manager.get("active_project_path")

        # Ensure all stored project paths are valid directories
        self._open_projects = [
            os.path.normpath(p) for p in open_projects if os.path.isdir(p)
        ]

        if (active_project and
                os.path.normpath(active_project) in self._open_projects):
            self._active_project_path = os.path.normpath(active_project)
        elif self._open_projects:
            self._active_project_path = self._open_projects[0]
        else:
            self._active_project_path = None
        log.info(
            "Loaded project session. Active project: "
            f"{self._active_project_path}"
        )

    def save_session(self):
        """Saves the current list of open projects to the settings."""
        settings_manager.set("open_projects", self._open_projects, False)
        settings_manager.set(
            "active_project_path", self._active_project_path, False
        )
        log.info("Project session saved.")

    def open_project(self, path: str) -> bool:
        """Adds a project to the list of open projects and sets it as active."""
        if not os.path.isdir(path):
            log.error(f"Cannot open project. Path is not a directory: {path}")
            return False

        norm_path = os.path.normpath(path)
        if norm_path not in self._open_projects:
            self._open_projects.append(norm_path)
            log.info(f"Project opened: {norm_path}")
            self.projects_changed.emit()  # NEW: Emit signal on change
        self.set_active_project(norm_path)
        return True

    def close_project(self, path: str):
        """Closes a project and updates the active project if necessary."""
        norm_path = os.path.normpath(path)
        if norm_path in self._open_projects:
            self._open_projects.remove(norm_path)
            log.info(f"Project closed: {norm_path}")

            # If the closed project was the active one, pick a new active one
            if self.get_active_project_path() == norm_path:
                new_active = self._open_projects[0] if self._open_projects else None
                self.set_active_project(new_active)
            
            # Persist the change
            self.save_session()
            self.projects_changed.emit()  # NEW: Emit signal on change


    def get_open_projects(self) -> List[str]:
        """Returns the list of currently open project paths."""
        return self._open_projects

    def set_active_project(self, path: Optional[str]):
        """Sets the currently active project."""
        norm_path = os.path.normpath(path) if path else None
        if self._active_project_path != norm_path:
            self._active_project_path = norm_path
            log.info(f"Active project set to: {norm_path}")
            # Emit signal to let UI components like completion manager know
            self.projects_changed.emit()

    def get_active_project_path(self) -> Optional[str]:
        """Returns the path of the currently active project."""
        return self._active_project_path

    def is_project_open(self) -> bool:
        """Checks if any project is currently active."""
        return self._active_project_path is not None

    def create_project_zip(self, output_zip_path: str) -> bool:
        """
        Creates a zip archive of the active project, ignoring common artifacts.

        Returns:
            True if the zip was created successfully, False otherwise.
        """
        if not self.is_project_open():
            log.error("Cannot create zip. No active project.")
            return False

        project_root = self.get_active_project_path()
        ignore_dirs = {
            '__pycache__', '.git', 'venv', '.venv', 'dist', 'build', 'logs'
        }
        # Explicitly ignore the user settings file for security
        ignore_files = {'.gitignore', 'puffin_editor_settings.json'}

        try:
            with zipfile.ZipFile(
                    output_zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, dirs, files in os.walk(project_root):
                    # Modify dirs in-place to prevent walking into ignored dirs
                    dirs[:] = [d for d in dirs if d not in ignore_dirs]
                    for file in files:
                        if file in ignore_files:
                            continue
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, project_root)
                        zipf.write(file_path, arcname)
            log.info(
                f"Successfully created project archive at {output_zip_path}"
            )
            return True
        except (IOError, OSError, zipfile.BadZipFile) as e:
            log.error(f"Failed to create project zip: {e}", exc_info=True)
            return False

    def _generate_file_tree_from_list(
            self, project_root: str, file_list: List[str]
    ) -> List[str]:
        """Generates a text-based file tree from a specific list of files."""
        tree = {}
        for file_path in file_list:
            relative_path = os.path.relpath(file_path, project_root)
            parts = Path(relative_path).parts
            current_level = tree
            for part in parts:
                if part not in current_level:
                    current_level[part] = {}
                current_level = current_level[part]

        def build_tree_lines(d: dict, prefix: str = "") -> List[str]:
            lines = []
            # Sort entries so directories (which have children) come first
            entries = sorted(
                d.keys(), key=lambda k: (not bool(d[k]), k.lower())
            )
            for i, name in enumerate(entries):
                is_last = (i == len(entries) - 1)
                connector = "└── " if is_last else "├── "
                lines.append(f"{prefix}{connector}{name}")
                if d[name]:  # It's a directory with children
                    new_prefix = prefix + ("    " if is_last else "│   ")
                    lines.extend(build_tree_lines(d[name], new_prefix))
            return lines

        return build_tree_lines(tree)

    def _clean_git_conflict_markers(self, content: str) -> str:
        """Removes Git conflict markers from a string, keeping the HEAD version."""
        if '<<<<<<<' not in content:
            return content

        lines = content.splitlines()
        cleaned_lines = []
        in_conflict = False
        # We want to keep the HEAD version, which is the part before '======='
        keep_current_version = False

        for line in lines:
            if line.startswith('<<<<<<<'):
                in_conflict = True
                keep_current_version = True
                continue

            if line.startswith('======='):
                if in_conflict:
                    keep_current_version = False
                    continue

            if line.startswith('>>>>>>>'):
                if in_conflict:
                    in_conflict = False
                    keep_current_version = False
                    continue

            if not in_conflict or (in_conflict and keep_current_version):
                cleaned_lines.append(line)

        return "\n".join(cleaned_lines)

    def export_project_for_ai(
            self,
            output_filepath: str,
            selected_files: List[str],
            instructions: str,
            guidelines: List[str],
            golden_rules: List[str],
            all_problems: Optional[Dict[str, List[Dict]]] = None
    ) -> Tuple[bool, str]:
        """
        Exports selected project files into a single Markdown file for AI.
        """
        if not self.is_project_open():
            return False, "No project is open."

        project_root = self.get_active_project_path()
        project_name = os.path.basename(project_root)
        output_lines = [
            f"# Project Export: {project_name}",
            f"## Export Timestamp: {datetime.datetime.now().isoformat()}",
            "---",
            "\n## 📝 AI Instructions", "```text",
            instructions or "No specific instructions were provided.", "```",
            "\n## 📜 AI Guidelines & Rules", "```text",
        ]
        guideline_text = "\n".join(
            [f"- {g}" for g in guidelines]
        ) if guidelines else "No specific guidelines were provided."
        output_lines.append(guideline_text)
        output_lines.extend(["```", "---"])

        output_lines.append("\n## ✨ Golden Rules\n```text")
        golden_rules_text = "\n".join(
            [f"{i + 1}. {g}" for i, g in enumerate(golden_rules)]
        ) if golden_rules else "No specific golden rules were provided."
        output_lines.append(golden_rules_text)
        output_lines.extend(["```", "---"])

        output_lines.append("\n## 🗂️ File Tree of Included Files:\n```")
        output_lines.append(f"/{project_name}")
        output_lines.extend(
            self._generate_file_tree_from_list(project_root, selected_files)
        )
        output_lines.append("```\n---")
        output_lines.append("\n## 📄 File Contents:\n")

        file_count = 0
        for filepath in sorted(selected_files):
            norm_filepath = os.path.normpath(filepath)
            relative_path = Path(
                filepath).relative_to(project_root).as_posix()
            language = Path(filepath).suffix.lstrip('.') or 'text'
            if language == 'py':
                language = 'python'

            output_lines.append(f"### File: `/{relative_path}`\n")

            if all_problems and norm_filepath in all_problems:
                output_lines.append("#### Linter Issues Found:")
                output_lines.append("```")
                for problem in all_problems[norm_filepath]:
                    output_lines.append(
                        f"- Line {problem['line']}, Col {problem['col']} "
                        f"({problem['code']}): {problem['description']}"
                    )
                output_lines.append("```\n")

            output_lines.append(f"```{language}")
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    original_content = f.read()
                    cleaned_content = self._clean_git_conflict_markers(original_content)
                    if original_content != cleaned_content:
                        log.info(f"Cleaned git conflict markers from {filepath} for export.")
                    output_lines.append(cleaned_content)
                file_count += 1
            except (IOError, UnicodeDecodeError) as e:
                log.warning(
                    "Could not read file during AI export: "
                    f"{filepath}. Error: {e}"
                )
                output_lines.append(f"[Error reading file: {e}]")
            output_lines.append("```\n---")

        try:
            with open(output_filepath, 'w', encoding='utf-8') as f:
                f.write("\n".join(output_lines))
            return True, (
                f"Project exported to {Path(output_filepath).name}. "
                f"Included {file_count} files."
            )
        except IOError as e:
            log.error(f"Failed to write AI export file: {e}", exc_info=True)
            return False, f"Failed to write export file: {e}"
```

### File: `/plugins/github_tools/__init__.py`

```python

```

### File: `/plugins/github_tools/github_dialog.py`

```python
# PuffinPyEditor/plugins/github_tools/github_dialog.py
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
                 git_manager: SourceControlManager,
                 parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.github_manager = github_manager
        self.git_manager = git_manager

        self.setWindowTitle("GitHub Repository Management")
        self.setMinimumSize(800, 600)
        self._setup_ui()
        self._connect_signals()

    def _setup_ui(self):
        layout = QVBoxLayout(self)

        top_bar_layout = QHBoxLayout()
        self.user_label = QLabel("<i>Checking authentication...</i>")
        top_bar_layout.addWidget(self.user_label)
        top_bar_layout.addStretch()
        layout.addLayout(top_bar_layout)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        layout.addWidget(splitter)
        left_pane = self._create_repo_list_pane()
        right_pane = self._create_details_pane()
        splitter.addWidget(left_pane)
        splitter.addWidget(right_pane)
        splitter.setSizes([300, 500])

    def _create_repo_list_pane(self) -> QWidget:
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
        self.github_manager.repos_ready.connect(self.populate_repo_list)
        self.github_manager.branches_ready.connect(self.populate_branch_list)
        self.github_manager.operation_failed.connect(
            self._on_operation_failed)
        self.repo_list.currentItemChanged.connect(self.on_repo_selected)
        self.refresh_button.clicked.connect(self.github_manager.list_repos)
        self.clone_button.clicked.connect(self.on_clone_clicked)

    def showEvent(self, event):
        super().showEvent(event)
        self._update_user_info()
        self.refresh_button.click()

    def closeEvent(self, event):
        try:
            self.github_manager.repos_ready.disconnect(self.populate_repo_list)
            self.github_manager.branches_ready.disconnect(
                self.populate_branch_list)
            self.github_manager.operation_failed.disconnect(
                self._on_operation_failed)
        except TypeError:
            pass  # Suppress errors if signals are not connected
        super().closeEvent(event)

    def _update_user_info(self):
        user_info = self.github_manager.get_user_info()
        if user_info and user_info.get('login'):
            self.user_label.setText(
                f"Authenticated as: <b>{user_info['login']}</b>")
        else:
            self.user_label.setText(
                "<i>Authentication details not available.</i>")

    def populate_repo_list(self, repos: List[Dict[str, Any]]):
        self.repo_list.clear()
        for repo in sorted(repos, key=lambda r: r['name'].lower()):
            item = QListWidgetItem(repo['name'])
            item.setToolTip(repo['full_name'])
            item.setData(Qt.ItemDataRole.UserRole, repo)
            self.repo_list.addItem(item)

    def populate_branch_list(self, branches: List[Dict[str, Any]]):
        self.branch_list.clear()
        for branch in branches:
            item = QListWidgetItem(branch['name'])
            item.setData(Qt.ItemDataRole.UserRole, branch)
            self.branch_list.addItem(item)
        if branches:
            self.branch_list.setCurrentRow(0)

    def on_repo_selected(self, current_item: QListWidgetItem):
        self.branch_list.clear()
        self.clone_button.setEnabled(False)
        if not current_item:
            self.repo_details_label.setText("<i>Select a repository...</i>")
            return
        repo_data = current_item.data(Qt.ItemDataRole.UserRole)
        desc = repo_data.get('description') or 'No description provided.'
        self.repo_details_label.setText(
            f"<b>{repo_data['full_name']}</b><br/><small>{desc}</small>")
        self.github_manager.list_branches(repo_data['full_name'])
        self.clone_button.setEnabled(True)

    def on_clone_clicked(self):
        repo_item = self.repo_list.currentItem()
        branch_item = self.branch_list.currentItem()
        if not repo_item or not branch_item:
            QMessageBox.warning(self, "Selection Required",
                                "Please select a repository and a branch.")
            return
        repo_data = repo_item.data(Qt.ItemDataRole.UserRole)
        branch_data = branch_item.data(Qt.ItemDataRole.UserRole)
        path = QFileDialog.getExistingDirectory(
            self, f"Select Folder to Clone '{repo_data['name']}' Into")
        if not path:
            return
        clone_path = os.path.join(path, repo_data['name'])
        if os.path.exists(clone_path):
            QMessageBox.critical(
                self, "Folder Exists",
                f"The folder '{repo_data['name']}' already exists here.")
            return
        self.git_manager.clone_repo(
            repo_data['clone_url'], path, branch_data['name'])
        QMessageBox.information(
            self, "Clone Started",
            "Cloning has started. The project will open when complete.")
        self.project_cloned.emit(clone_path)
        self.accept()

    def _on_operation_failed(self, error_message: str):
        QMessageBox.critical(self, "GitHub Error", error_message)

```

### File: `/plugins/github_tools/new_release_dialog.py`

```python
# PuffinPyEditor/plugins/github_tools/new_release_dialog.py
from typing import Optional, Dict, Any
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QFormLayout,
                             QDialogButtonBox, QLineEdit, QTextEdit, QLabel,
                             QCheckBox, QComboBox, QHBoxLayout, QWidget,
                             QGroupBox, QPushButton, QMessageBox)
from app_core.source_control_manager import SourceControlManager
from utils.versioning import suggest_next_version

try:
    import git
except ImportError:
    git = None


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

        # Use a FormLayout for standard label-field pairs
        form_layout = QFormLayout()
        form_layout.setRowWrapPolicy(QFormLayout.RowWrapPolicy.WrapAllRows)

        # Tag Name
        tag_layout_widget = QWidget()
        tag_layout = QHBoxLayout(tag_layout_widget)
        tag_layout.setContentsMargins(0, 0, 0, 0)
        suggested_tag = suggest_next_version()
        self.tag_edit = QLineEdit(suggested_tag)
        self.tag_edit.setPlaceholderText("e.g., v1.2.1")
        self.branch_combo = QComboBox()
        self.branch_combo.setToolTip(
            "Select the branch to create the release from.")
        tag_layout.addWidget(self.tag_edit, 2)
        tag_layout.addWidget(QLabel("on branch:"))
        tag_layout.addWidget(self.branch_combo, 1)
        form_layout.addRow("<b>Tag Name:</b>", tag_layout_widget)

        # Release Title
        self.title_edit = QLineEdit()
        self.title_edit.setText(suggested_tag)
        self.title_edit.setPlaceholderText(
            "e.g., Feature Update and Bug Fixes")
        form_layout.addRow("<b>Release Title:</b>", self.title_edit)

        # Add the form layout to the main dialog layout
        self.main_layout.addLayout(form_layout)

        # --- Release Notes Section (manual layout) ---
        notes_header_layout = QHBoxLayout()
        notes_header_layout.addWidget(QLabel("<b>Release Notes:</b>"))
        notes_header_layout.addStretch()
        self.generate_notes_button = QPushButton("Generate from Commits")
        self.generate_notes_button.setToolTip(
            "Generate release notes from commits since the last tag.")
        notes_header_layout.addWidget(self.generate_notes_button)
        self.main_layout.addLayout(notes_header_layout)

        self.notes_edit = QTextEdit()
        self.notes_edit.setPlaceholderText(
            "Describe the changes in this release (Markdown is supported).")
        self.notes_edit.setMinimumHeight(150)
        self.main_layout.addWidget(self.notes_edit)
        # --- End of Release Notes Section ---

        # Options and Assets Groups
        options_group = QGroupBox("Options")
        options_layout = QVBoxLayout(options_group)
        self.prerelease_checkbox = QCheckBox("Mark as a pre-release")
        self.prerelease_checkbox.setToolTip(
            "Indicates that this is not a production-ready release.")
        options_layout.addWidget(self.prerelease_checkbox)
        options_layout.addStretch()
        self.main_layout.addWidget(options_group)

        assets_group = QGroupBox("Release Assets")
        assets_layout = QVBoxLayout(assets_group)
        self.build_installer_checkbox = QCheckBox(
            "Build and attach installer")
        self.build_installer_checkbox.setToolTip(
            "Runs the project's build script and uploads the setup file.")
        self.build_installer_checkbox.setChecked(True)
        assets_layout.addWidget(self.build_installer_checkbox)
        assets_layout.addStretch()
        self.main_layout.addWidget(assets_group)

        # Dialog Buttons
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
        self.generate_notes_button.clicked.connect(
            self._generate_release_notes)

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
        ok_button = self.button_box.button(QDialogButtonBox.StandardButton.Ok)
        ok_button.setEnabled(is_valid)

    def _generate_release_notes(self):
        if git is None:
            QMessageBox.critical(
                self, "Missing Dependency",
                "The 'GitPython' library is not installed. Please install it "
                "(`pip install GitPython`) to use this feature.")
            return
        try:
            repo = git.Repo(self.project_path, search_parent_directories=True)
            tags = sorted(repo.tags, key=lambda t: t.commit.committed_datetime)
            latest_tag = tags[-1] if tags else None
            latest_tag_name = latest_tag.name if latest_tag else "the beginning"
            target_branch = self.branch_combo.currentText()

            rev_range = target_branch
            if latest_tag:
                rev_range = f"{latest_tag.commit.hexsha}..{target_branch}"

            commits = list(repo.iter_commits(rev_range))
            commit_log = []
            for commit in commits:
                if len(commit.parents) > 1:  # Skip merge commits
                    continue
                commit_log.append(f"- {commit.summary} ({commit.hexsha[:7]})")

            if commit_log:
                self.notes_edit.setText("\n".join(commit_log))
            else:
                QMessageBox.information(
                    self, "No New Commits",
                    "No new commits found on branch "
                    f"'{target_branch}' since tag '{latest_tag_name}'.")
        except Exception as e:
            QMessageBox.critical(self, "Error Generating Notes",
                                 f"An error occurred: {e}")

    def get_release_data(self) -> Dict[str, Any]:
        return {
            "tag": self.tag_edit.text().strip(),
            "title": self.title_edit.text().strip(),
            "notes": self.notes_edit.toPlainText().strip(),
            "prerelease": self.prerelease_checkbox.isChecked(),
            "target_branch": self.branch_combo.currentText(),
            "build_installer": self.build_installer_checkbox.isChecked()
        }
```

### File: `/plugins/github_tools/plugin.json`

```json
{
    "id": "github_tools",
    "name": "GitHub Tools",
    "author": "PuffinPy Team",
    "version": "1.2.0",
    "description": "Provides UI for cloning, releases, and other GitHub interactions.",
    "entry_point": "plugin_main.py"
}
```

### File: `/plugins/github_tools/plugin_main.py`

```python
# PuffinPyEditor/plugins/github_tools/plugin_main.py
import os
import shutil
import tempfile
import git
import configparser
from git import Actor
from PyQt6.QtWidgets import (QInputDialog, QMessageBox, QTextEdit, QDialog,
                             QVBoxLayout, QLabel, QProgressBar, QPushButton,
                             QDialogButtonBox)
from PyQt6.QtCore import Qt, QCoreApplication, QProcess, QTimer
from PyQt6.QtGui import QFont

from app_core.puffin_api import PuffinPluginAPI
from .new_release_dialog import NewReleaseDialog
from .select_repo_dialog import SelectRepoDialog
from .github_dialog import GitHubDialog
from utils import versioning
import sys


class UploadProgressDialog(QDialog):
    """A dialog to show the real-time progress of an asset upload."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Release Progress")
        self.setMinimumWidth(600)
        self.setModal(True)
        self.setWindowFlag(Qt.WindowType.WindowCloseButtonHint, False)

        layout = QVBoxLayout(self)

        self.step_label = QLabel("Starting release...")
        font = self.step_label.font()
        font.setBold(True)
        self.step_label.setFont(font)
        layout.addWidget(self.step_label)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)
        self.progress_bar.setTextVisible(False)
        layout.addWidget(self.progress_bar)

        self.log_console = QTextEdit()
        self.log_console.setReadOnly(True)
        self.log_console.setFont(QFont("Consolas", 9))
        self.log_console.setStyleSheet("background-color: #1e1e1e; color: #d4d4d4;")
        layout.addWidget(self.log_console)

        self.button_box = QDialogButtonBox()
        self.close_button = self.button_box.addButton("Close", QDialogButtonBox.ButtonRole.RejectRole)
        self.close_button.clicked.connect(self.reject)
        self.close_button.hide()  # Hide until process is complete
        layout.addWidget(self.button_box)

    def set_step(self, step_name: str):
        self.step_label.setText(f"Step: {step_name}")

    def add_log(self, message: str, is_error: bool = False):
        color = "#FF5555" if is_error else "#D4D4D4"
        self.log_console.append(f"<span style='color:{color};'>{message}</span>")
        self.log_console.verticalScrollBar().setValue(self.log_console.verticalScrollBar().maximum())

    def show_close_button(self):
        self.close_button.show()
        self.setWindowTitle("Release Complete")


class GitHubToolsPlugin:
    def __init__(self, puffin_api: PuffinPluginAPI):
        self.api = puffin_api
        self.main_window = self.api.get_main_window()
        self.project_manager = self.api.get_manager("project")
        self.git_manager = self.api.get_manager("git")
        self.github_manager = self.api.get_manager("github")
        self.github_dialog = None
        self._release_state = {}
        self.build_process = None
        self.build_output_buffer = []
        self.progress_dialog = None

        self.api.log_info("GitHub Tools plugin initialized.")
        self.api.add_menu_action("tools", "Build Project Installer", self._show_build_installer_dialog,
                                 icon_name="fa5s.cogs")

        if sc_panel := self._get_sc_panel():
            sc_panel.create_release_requested.connect(self.show_create_release_dialog)
            sc_panel.publish_repo_requested.connect(self._publish_repo)
            sc_panel.link_to_remote_requested.connect(self._link_repo)
            sc_panel.change_visibility_requested.connect(self._change_visibility)
            self.api.log_info("GitHub Tools: Connected signals from Source Control Panel.")

    def _get_sc_panel(self):
        if hasattr(self.main_window, 'source_control_panel'): return self.main_window.source_control_panel
        return None

    def _log_to_dialog(self, message: str, is_error: bool = False):
        # FIX: Centralized logging helper for release process
        log_func = self.api.log_error if is_error else self.api.log_info
        log_func(f"[Release] {message}")
        if self.progress_dialog:
            self.progress_dialog.add_log(message, is_error)

    def ensure_git_identity(self, project_path: str, log_to_dialog=False) -> bool:
        """
        FIX: Ensures the local repo is configured to use an email associated with the
        logged-in GitHub account, which is required for contributions to be counted.
        It will overwrite a misconfigured local email.

        Returns True on success, False on failure.
        """
        log_func = self._log_to_dialog if log_to_dialog else self.api.log_info
        log_func("Verifying Git identity for contributions...")

        user_info = self.github_manager.get_user_info()
        if not user_info or not user_info.get('login'):
            self.api.show_message("warning", "GitHub Login Required",
                                  "You must be logged into GitHub to ensure your commits are counted as contributions.")
            return False

        # Construct the set of valid emails for this user
        valid_emails = set()
        user_name = user_info.get('login')
        public_email = user_info.get('email')
        noreply_email = f"{user_info.get('id')}+{user_name}@users.noreply.github.com"

        if public_email:
            valid_emails.add(public_email.lower())
        valid_emails.add(noreply_email.lower())

        try:
            repo = git.Repo(project_path)
            current_email = ""
            # Check for an existing email config
            try:
                with repo.config_reader() as cr:
                    current_email = cr.get_value('user', 'email', '').lower()
            except (configparser.NoSectionError, configparser.NoOptionError):
                log_func("No local or global git email is set.")
                pass  # No email is set, we can proceed to set it.

            # If the current email is not valid for contributions, overwrite it locally.
            if current_email not in valid_emails:
                log_func(f"Current git email ('{current_email}') is not valid for contributions. Updating local config.")
                with repo.config_writer() as config:
                    config.set_value('user', 'name', user_name)
                    # Prefer the noreply email for privacy and consistency
                    config.set_value('user', 'email', noreply_email)
                log_func(f"Successfully set local git identity to '{user_name} <{noreply_email}>'.")
            else:
                log_func(f"Verified Git identity is correctly set to '{current_email}'.")

            return True

        except Exception as e:
            self.api.show_message("critical", "Git Configuration Error", f"Could not verify or set Git configuration: {e}")
            return False

    def show_create_release_dialog(self, project_path: str = None):
        if not project_path: project_path = self.project_manager.get_active_project_path()
        if not project_path:
            self.api.show_message("info", "No Project Open", "Please open a project to create a release.")
            return
        self._create_release(project_path)

    def _create_release(self, project_path):
        dialog = NewReleaseDialog(project_path, self.git_manager, self.main_window)
        if not dialog.exec():
            self.api.show_status_message("Release cancelled.", 3000)
            return

        self.progress_dialog = UploadProgressDialog(self.main_window)
        self.progress_dialog.show()

        # FIX: Ensure git identity is correct BEFORE starting the release process.
        if not self.ensure_git_identity(project_path, log_to_dialog=True):
            self._on_release_step_failed("Git identity misconfiguration. Commit cannot be created.")
            return

        try:
            repo = git.Repo(project_path)
            if not repo.remotes: self._on_release_step_failed("This project has no remote repository."); return
            remote_url = repo.remotes.origin.url
            if 'github.com' not in remote_url: self._on_release_step_failed(
                "The 'origin' remote is not a GitHub repository."); return
            owner, repo_name = self.git_manager.parse_git_url(remote_url)
            if not owner or not repo_name: self._on_release_step_failed(
                "Could not parse owner/repo from remote."); return
        except Exception as e:
            self._on_release_step_failed(f"Could not analyze repository: {e}"); return

        self._release_state = {'dialog_data': dialog.get_release_data(), 'project_path': project_path, 'owner': owner,
                               'repo_name': repo_name, 'step': None}
        self._advance_release_state("PULL_CHANGES")

    def _advance_release_state(self, next_step):
        self._release_state['step'] = next_step
        step = next_step
        dialog_data, project_path = self._release_state['dialog_data'], self._release_state['project_path']
        self._cleanup_all_connections()
        step_title = step.replace('_', ' ').title()
        if sc_panel := self._get_sc_panel(): sc_panel.set_ui_locked(True, f"Step: {step_title}...")
        if self.progress_dialog: self.progress_dialog.set_step(step_title)

        author = self._release_state.get('author')
        if not author:
            try:
                repo = git.Repo(project_path)
                with repo.config_reader() as cr:
                    name = cr.get_value('user', 'name')
                    email = cr.get_value('user', 'email')
                author = Actor(name, email)
                self._release_state['author'] = author
            except Exception as e:
                self._on_release_step_failed(f"Could not read Git author info: {e}")
                return

        if step == "PULL_CHANGES":
            self.git_manager.git_success.connect(self._on_release_step_succeeded)
            self.git_manager.git_error.connect(self._on_release_step_failed)
            self.git_manager.pull(project_path)
        elif step == "BUMP_VERSION_COMMIT":
            if not versioning.write_new_version(dialog_data['tag']):
                self._on_release_step_failed("Failed to write new version to VERSION.txt.")
                return
            self.main_window._update_window_title()
            self.git_manager.git_success.connect(self._on_release_step_succeeded)
            self.git_manager.git_error.connect(self._on_release_step_failed)
            self.git_manager.commit_files(project_path, f"ci: Release {dialog_data['tag']}", author)
        
        elif step == "PUSH_MAIN_BRANCH":
            self.git_manager.git_success.connect(self._on_release_step_succeeded)
            self.git_manager.git_error.connect(self._on_release_step_failed)
            self.git_manager.push(project_path)

        elif step == "CREATE_TAG":
            self.git_manager.git_success.connect(self._on_release_step_succeeded)
            self.git_manager.git_error.connect(self._on_release_step_failed)
            self.git_manager.create_tag(project_path, dialog_data['tag'], dialog_data['title'], author)

        elif step == "PUSH_TAG":
            self.git_manager.git_success.connect(self._on_release_step_succeeded)
            self.git_manager.git_error.connect(self._on_release_step_failed)
            self.git_manager.push_specific_tag(project_path, dialog_data['tag'])

        elif step == "CREATE_RELEASE":
            self.github_manager.operation_success.connect(self._on_release_step_succeeded)
            self.github_manager.operation_failed.connect(self._on_release_step_failed)
            self.github_manager.create_github_release(
                owner=self._release_state['owner'], repo=self._release_state['repo_name'], tag_name=dialog_data['tag'],
                name=dialog_data['title'], body=dialog_data['notes'], prerelease=dialog_data['prerelease'])

        elif step == "BUILD_ASSETS":
            self._run_build_script(project_path)
            
        elif step == "UPLOAD_ASSETS":
            self._upload_assets()

    def _on_release_step_succeeded(self, msg, data):
        step = self._release_state.get('step')
        self._log_to_dialog(f"SUCCESS on step '{step}': {msg}")
        
        # New logical flow
        if step == "PULL_CHANGES":
            self._advance_release_state("BUMP_VERSION_COMMIT")
        elif step == "BUMP_VERSION_COMMIT":
            self._advance_release_state("PUSH_MAIN_BRANCH")
        elif step == "PUSH_MAIN_BRANCH":
            self._advance_release_state("CREATE_TAG")
        elif step == "CREATE_TAG":
            self._advance_release_state("PUSH_TAG")
        elif step == "PUSH_TAG":
            self._advance_release_state("CREATE_RELEASE")
        elif step == "CREATE_RELEASE":
            self._release_state['release_info'] = data.get("release_data", {})
            self._advance_release_state(
                "BUILD_ASSETS" if self._release_state['dialog_data'].get("build_installer") else "UPLOAD_ASSETS")
        elif step == "UPLOAD_ASSET":
            self._upload_next_asset()


    def _run_build_script(self, project_path):
        build_script_path = os.path.join(project_path, "installer", "build.py")
        if not os.path.exists(build_script_path):
            self._on_release_step_failed(f"Build script not found at '{build_script_path}'.")
            return

        self.build_output_buffer.clear()
        args = []
        if self.api.get_manager("settings").get("cleanup_after_build", True):
            args.append("--cleanup")

        version_str = self._release_state['dialog_data']['tag'].lstrip('v')
        args.extend(["--version", version_str])

        if nsis_path := self.api.get_manager("settings").get("nsis_path"):
            args.extend(["--nsis-path", nsis_path])

        self.build_process = QProcess()
        self.build_process.setProcessChannelMode(QProcess.ProcessChannelMode.MergedChannels)
        self.build_process.readyReadStandardOutput.connect(self._on_build_stdout)
        self.build_process.finished.connect(self._on_build_finished)

        self.build_process.setWorkingDirectory(project_path)
        program = sys.executable
        command_args = [build_script_path] + args
        self._log_to_dialog(f"Executing build in '{project_path}': {os.path.basename(program)} {' '.join(command_args)}")

        self.build_process.start(program, command_args)

    def _on_build_stdout(self):
        output = self.build_process.readAllStandardOutput().data().decode(errors='ignore');
        self.build_output_buffer.append(output);
        self._log_to_dialog(f"[Build] {output.strip()}")

    def _on_build_finished(self, exit_code, exit_status):
        if exit_code == 0:
            self._log_to_dialog("Build successful."); self._advance_release_state("UPLOAD_ASSETS")
        else:
            self._show_build_error_dialog("The build script failed. See details below.",
                                          "".join(self.build_output_buffer)); self._on_release_step_failed(
                f"Build script failed with exit code {exit_code}.")
        self.build_process.deleteLater();
        self.build_process = None

    def _show_build_error_dialog(self, summary: str, details: str):
        self._log_to_dialog(f"ERROR: {summary}", is_error=True);
        dialog = QMessageBox(self.main_window)
        dialog.setIcon(QMessageBox.Icon.Critical)
        dialog.setWindowTitle("Build Failed")
        dialog.setText(summary)
        dialog.layout().setColumnStretch(1, 1)
        text_edit = QTextEdit()
        text_edit.setReadOnly(True)
        text_edit.setFont(QFont("Consolas", 9))
        text_edit.setText(details)
        text_edit.setMinimumSize(600, 300)
        dialog.layout().addWidget(text_edit, 1, 0, 1, -1)
        dialog.exec()

    def _show_build_installer_dialog(self):
        project_path = self.project_manager.get_active_project_path()
        if not project_path: self.api.show_message("info", "No Project", "Please open a project."); return
        if QMessageBox.question(self.main_window, "Confirm Build", "This will run the project's full build. Continue?",
                                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.Cancel) == QMessageBox.StandardButton.Yes:
            self._release_state = {'dialog_data': {'tag': f"v{versioning.APP_VERSION}", 'build_installer': True},
                                   'project_path': project_path}
            self.progress_dialog = UploadProgressDialog(self.main_window);
            self.progress_dialog.show()
            self._run_build_script(project_path)

    def _upload_assets(self):
        assets_to_upload = []
        dialog_data = self._release_state['dialog_data']
        project_path = self._release_state['project_path']
        
        if dialog_data.get("build_installer"):
            # THE FIX: Look for the installer in the correct top-level /dist directory
            dist_path = os.path.join(project_path, "dist")
            version_str = dialog_data['tag'].lstrip('v')
            installer_name = f"PuffinPyEditor_v{version_str}_Setup.exe"
            installer_path = os.path.join(dist_path, installer_name)

            if os.path.exists(installer_path):
                assets_to_upload.append(installer_path)
            else:
                self._on_release_step_failed(
                    f"Installer not found at '{installer_path}'. Build may have failed or produced an unexpected filename.")
                return

        # --- Create source code zip ---
        repo_name = self._release_state['repo_name']
        try:
            temp_zip_dir = tempfile.mkdtemp()
            self._release_state['temp_dir'] = temp_zip_dir
            # THE FIX: Define zip_name and zip_path separately to fix UnboundLocalError
            zip_name = f"{repo_name}-{dialog_data['tag']}.zip"
            zip_path = os.path.join(temp_zip_dir, zip_name)

            if self.project_manager.create_project_zip(zip_path):
                assets_to_upload.append(zip_path)
            else:
                self._log_to_dialog("Warning: Failed to create source code zip asset.", is_error=True)
        except Exception as e:
            self._log_to_dialog(f"Error creating source zip: {e}", is_error=True)

        if not assets_to_upload:
            self._log_to_dialog("No assets to upload, finishing release.")
            self._cleanup_release_process(success=True) # End of the line if no assets
            return

        self._release_state['asset_queue'] = assets_to_upload
        self._log_to_dialog(f"Found {len(assets_to_upload)} asset(s) to upload.")
        self._upload_next_asset()

    def _upload_next_asset(self):
        asset_queue = self._release_state.get('asset_queue', [])
        if not asset_queue:
            self._log_to_dialog("All assets uploaded successfully.")
            self._cleanup_release_process(success=True) # End of the line
            return
        asset_path, upload_url = asset_queue.pop(0), self._release_state['release_info']['upload_url']
        if self.progress_dialog: self.progress_dialog.set_step(f"Uploading {os.path.basename(asset_path)}")
        self._release_state['step'] = "UPLOAD_ASSET"
        self.github_manager.operation_success.connect(self._on_release_step_succeeded)
        self.github_manager.operation_failed.connect(self._on_release_step_failed)
        self.github_manager.upload_asset(upload_url, asset_path)

    def _on_release_step_failed(self, error_message):
        step = self._release_state.get('step', 'UNKNOWN');
        failure_msg = f"An error occurred at step '{step}': {error_message}"
        self._log_to_dialog(failure_msg, is_error=True)
        if self.progress_dialog: self.progress_dialog.show_close_button();
        if step in ["BUMP_VERSION_COMMIT",
                    "FINAL_PUSH"]: failure_msg += "\n\nA local commit may have been created. You might need to undo it manually (e.g., 'git reset HEAD~1')."
        self.api.show_message("critical", "Release Failed", f"{failure_msg}\n\nAttempting to roll back...")
        tag_name, release_id = self._release_state.get('dialog_data', {}).get('tag'), self._release_state.get(
            'release_info', {}).get('id')
        if release_id: self._log_to_dialog(
            f"ROLLBACK: Deleting GitHub release ID {release_id}"); self.github_manager.delete_release(
            self._release_state['owner'], self._release_state['repo_name'], release_id)
        if tag_name and step != "CREATE_TAG": self._log_to_dialog(
            f"ROLLBACK: Deleting remote tag '{tag_name}'"); self.git_manager.delete_remote_tag(
            self._release_state['project_path'], tag_name)
        if tag_name: self._log_to_dialog(f"ROLLBACK: Deleting local tag '{tag_name}'"); self.git_manager.delete_tag(
            self._release_state['project_path'], tag_name)
        self._cleanup_release_process()

    def _cleanup_all_connections(self):
        try:
            self.git_manager.git_success.disconnect(self._on_release_step_succeeded)
            self.git_manager.git_error.disconnect(self._on_release_step_failed)
            self.github_manager.operation_success.disconnect(self._on_release_step_succeeded)
            self.github_manager.operation_failed.disconnect(self._on_release_step_failed)
        except TypeError:
            pass

    def _cleanup_release_process(self, success=False):
        self._log_to_dialog("Cleaning up release process state.")
        self._cleanup_all_connections()
        if sc_panel := self._get_sc_panel(): sc_panel.set_ui_locked(False, "Release process finished.")
        if self.progress_dialog:
            if success:
                self.progress_dialog.add_log("\n--- RELEASE COMPLETE ---")
            else:
                self.progress_dialog.add_log("\n--- RELEASE FAILED ---")
            self.progress_dialog.show_close_button()
            self.progress_dialog = None
        if temp_dir := self._release_state.get('temp_dir'):
            if os.path.exists(temp_dir): shutil.rmtree(temp_dir, ignore_errors=True); self._log_to_dialog(
                f"Cleaned temp dir: {temp_dir}")
        self._release_state = {}

    def _publish_repo(self, local_path):
        repo_name, ok = QInputDialog.getText(self.main_window, "Publish to GitHub", "Repository Name:",
                                             text=os.path.basename(local_path))
        if not ok or not repo_name:
            if sc_panel := self._get_sc_panel(): sc_panel.set_ui_locked(False, "Publish cancelled."); return
        
        # FIX: Ensure git identity is correct before publishing.
        if not self.ensure_git_identity(local_path):
            if sc_panel := self._get_sc_panel(): sc_panel.set_ui_locked(False, "Publish cancelled: Git identity not set.")
            return

        description, _ = QInputDialog.getText(self.main_window, "Publish to GitHub", "Description (optional):")
        is_private = QMessageBox.question(self.main_window, "Visibility", "Make this repository private?",
                                          QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                          QMessageBox.StandardButton.No) == QMessageBox.StandardButton.Yes

        def on_repo_created(msg, data, path=local_path):
            if "Repository" in msg and "created" in msg:
                self._cleanup_all_connections();
                clone_url = data.get("clone_url")
                if sc_panel := self._get_sc_panel(): sc_panel.set_ui_locked(True, "Linking and pushing...")
                self.git_manager.publish_repo(path, clone_url)

        self.github_manager.operation_success.connect(on_repo_created)
        self.github_manager.operation_failed.connect(
            lambda msg: self._get_sc_panel().set_ui_locked(False, f"Error: {msg}"))
        if sc_panel := self._get_sc_panel(): sc_panel.set_ui_locked(True, f"Creating '{repo_name}' on GitHub...")
        self.github_manager.create_repo(repo_name, description, is_private)

    def _link_repo(self, local_path):
        dialog = SelectRepoDialog(self.github_manager, self.main_window)
        if dialog.exec() and (repo_data := dialog.selected_repo_data):
            
            # FIX: Ensure git identity is correct before linking and potentially pushing.
            if not self.ensure_git_identity(local_path):
                if sc_panel := self._get_sc_panel(): sc_panel.set_ui_locked(False, "Link cancelled: Git identity not set.")
                return

            if clone_url := repo_data.get('clone_url'):
                if sc_panel := self._get_sc_panel(): sc_panel.set_ui_locked(True, "Linking to remote...")
                self.git_manager.link_to_remote(local_path, clone_url)

    def _change_visibility(self, local_path):
        try:
            repo = git.Repo(local_path);
            if not repo.remotes: return
            remote_url, (owner, repo_name) = repo.remotes.origin.url, self.git_manager.parse_git_url(remote_url)
            if not owner or not repo_name: return
            is_private = QMessageBox.question(self.main_window, "Change Visibility", "Make repository private?",
                                              QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No) == QMessageBox.StandardButton.Yes
            if sc_panel := self._get_sc_panel(): sc_panel.set_ui_locked(True, "Changing visibility...")
            self.github_manager.update_repo_visibility(owner, repo_name, is_private)
        except Exception as e:
            self.api.show_message("critical", "Error", f"Could not get repository info: {e}")

    def _show_github_dialog(self):
        if not self.github_dialog:
            self.github_dialog = GitHubDialog(self.github_manager, self.git_manager, self.main_window)
            self.github_dialog.project_cloned.connect(lambda path: self.project_manager.open_project(path))
        self.github_dialog.show()


def initialize(puffin_api: PuffinPluginAPI):
    """Initializes the GitHub Tools plugin."""
    plugin = GitHubToolsPlugin(puffin_api)
    puffin_api.add_menu_action("tools", "GitHub Repositories...", plugin._show_github_dialog, icon_name="fa5b.github")
    puffin_api.add_menu_action("tools", "New Release...", plugin.show_create_release_dialog, icon_name="fa5s.tag")
    return plugin
```

### File: `/plugins/github_tools/select_repo_dialog.py`

```python
# PuffinPyEditor/plugins/github_tools/select_repo_dialog.py
from typing import Optional, List, Dict, Any
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QListWidget,
                             QListWidgetItem, QDialogButtonBox, QMessageBox,
                             QLineEdit, QHBoxLayout, QLabel, QWidget)
from PyQt6.QtCore import Qt
from app_core.github_manager import GitHubManager


class SelectRepoDialog(QDialog):
    """
    A reusable dialog for selecting a GitHub repository from a user's account.
    """
    def __init__(self, github_manager: GitHubManager,
                 parent: Optional[QWidget] = None,
                 title: str = "Select Target Repository"):
        super().__init__(parent)
        self.github_manager = github_manager
        self.selected_repo_data: Optional[Dict[str, Any]] = None
        self.all_repos: List[Dict[str, Any]] = []

        self.setWindowTitle(title)
        self.setMinimumSize(500, 400)
        self.main_layout = QVBoxLayout(self)

        self._setup_ui()
        self._connect_signals()
        self.github_manager.list_repos()

    def _setup_ui(self):
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
            QDialogButtonBox.StandardButton.Ok |
            QDialogButtonBox.StandardButton.Cancel
        )
        self.main_layout.addWidget(self.button_box)
        ok_button = self.button_box.button(QDialogButtonBox.StandardButton.Ok)
        ok_button.setEnabled(False)

    def _connect_signals(self):
        self.github_manager.repos_ready.connect(self._handle_repos_loaded)
        self.github_manager.operation_failed.connect(self._on_load_failed)
        self.filter_edit.textChanged.connect(self._filter_repo_list)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)

    def closeEvent(self, event):
        try:
            self.github_manager.repos_ready.disconnect(
                self._handle_repos_loaded)
            self.github_manager.operation_failed.disconnect(
                self._on_load_failed)
        except TypeError:
            pass  # Suppress errors if signals are not connected
        super().closeEvent(event)

    def _handle_repos_loaded(self, repos: List[Dict[str, Any]]):
        self.all_repos = sorted(repos, key=lambda r: r['full_name'].lower())
        self._populate_repo_list()
        if self.repo_list_widget.count() > 0:
            ok_button = self.button_box.button(
                QDialogButtonBox.StandardButton.Ok)
            ok_button.setEnabled(True)
            self.repo_list_widget.setCurrentRow(0)

    def _populate_repo_list(self):
        self.repo_list_widget.clear()
        filter_text = self.filter_edit.text().lower()
        for repo in self.all_repos:
            if filter_text in repo['full_name'].lower():
                item = QListWidgetItem(repo['full_name'])
                item.setToolTip(repo.get('description', 'No description'))
                item.setData(Qt.ItemDataRole.UserRole, repo)
                self.repo_list_widget.addItem(item)

    def _filter_repo_list(self):
        self._populate_repo_list()

    def _on_load_failed(self, error_message: str):
        QMessageBox.critical(self, "Failed to Load Repositories",
                             error_message)
        self.reject()

    def accept(self):
        current_item = self.repo_list_widget.currentItem()
        if not current_item:
            QMessageBox.warning(self, "No Selection",
                                "Please select a repository.")
            return
        self.selected_repo_data = current_item.data(Qt.ItemDataRole.UserRole)
        super().accept()
```

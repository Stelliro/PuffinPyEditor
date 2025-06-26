# PuffinPyEditor/plugins/ai_tools/ai_export_dialog.py
import os
import json
from typing import List, Dict, Optional
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QSplitter, QWidget, QGroupBox,
    QTreeView, QTextEdit, QListWidget, QListWidgetItem, QPushButton,
    QDialogButtonBox, QMessageBox, QInputDialog, QComboBox, QProgressDialog,
    QFileDialog, QApplication
)
from PyQt6.QtGui import QStandardItemModel, QStandardItem, QCursor
from PyQt6.QtCore import Qt, QCoreApplication
import qtawesome as qta

from app_core.settings_manager import settings_manager
from app_core.project_manager import ProjectManager
from app_core.linter_manager import LinterManager
from utils.logger import log
from utils.helpers import get_base_path

PROMPT_TYPE_DEFAULT = "default"
PROMPT_TYPE_GENERATIVE = "generative"
PROMPT_TYPE_COMMUNITY = "community"
PROMPT_TYPE_USER = "user"

DEFAULT_LOADOUTS = {
    "Code Review": {
        "instructions": "You are a senior Python developer performing a code review. "
                        "Analyze the provided code for issues related to correctness, "
                        "style, performance, and maintainability. Provide constructive "
                        "feedback and concrete examples for improvement.",
        "guidelines": [
            "Check for compliance with PEP 8 style guidelines.",
            "Identify potential bugs or logical errors.",
            "Suggest more efficient or 'Pythonic' ways to write the code.",
            "Comment on code clarity, variable naming, and documentation.",
            "Do not suggest new features; focus on improving the existing code.",
            "Structure your feedback by file, then by line number where applicable."
        ]
    },
    "Documentation Generation": {
        "instructions": "You are a technical writer. Your task is to generate clear and "
                        "comprehensive documentation for the provided Python code. Create "
                        "docstrings for all public classes, methods, and functions that are "
                        "missing them. Follow the Google Python Style Guide for docstrings.",
        "guidelines": [
            "For each function/method, include an 'Args:' section for parameters "
            "and a 'Returns:' section for the return value.",
            "The main description of the function should be a concise, "
            "one-sentence summary.",
            "If a function raises exceptions, include a 'Raises:' section.",
            "Ensure the generated documentation is professional and ready to be "
            "used in the project."
        ]
    }
}


class AIExportDialog(QDialog):
    """
    A dialog for configuring and exporting a project's context for an AI model.
    """
    def __init__(self, project_path: str, project_manager: ProjectManager,
                 linter_manager: LinterManager, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.project_path = project_path
        self.project_manager = project_manager
        self.linter_manager = linter_manager
        self.loadouts: Dict[str, Dict] = {}
        self.golden_rule_sets: Dict[str, List[str]] = {}
        self.prompt_sources: Dict[str, Dict] = {}
        self.selected_files: List[str] = []

        self.setWindowTitle("Export Project for AI")
        self.setMinimumSize(950, 700)
        self.setObjectName("AIExportDialog")

        self._setup_ui()
        self._connect_signals()
        self._populate_file_tree()
        self._load_and_populate_prompts()
        self._load_and_populate_golden_rule_sets()

    def _setup_ui(self):
        self.main_layout = QVBoxLayout(self)
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        self.main_layout.addWidget(self.splitter)
        self._create_left_pane()
        self._create_right_pane()
        self.splitter.setSizes([350, 600])
        self.button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Cancel | QDialogButtonBox.StandardButton.Ok)
        self.button_box.button(QDialogButtonBox.StandardButton.Ok).setText("Export")
        self.main_layout.addWidget(self.button_box)

    def _create_left_pane(self):
        left_pane = QWidget()
        left_layout = QVBoxLayout(left_pane)
        self.splitter.addWidget(left_pane)
        loadouts_group = QGroupBox("Prompt Loadouts")
        loadouts_layout = QVBoxLayout(loadouts_group)
        self.loadout_combo = QComboBox()
        loadouts_layout.addWidget(self.loadout_combo)
        loadout_buttons_layout = QHBoxLayout()
        self.save_loadout_button = QPushButton("Save")
        self.delete_loadout_button = QPushButton("Delete")
        loadout_buttons_layout.addStretch()
        loadout_buttons_layout.addWidget(self.save_loadout_button)
        loadout_buttons_layout.addWidget(self.delete_loadout_button)
        loadouts_layout.addLayout(loadout_buttons_layout)
        left_layout.addWidget(loadouts_group)
        files_group = QGroupBox("Select Files to Include")
        files_layout = QVBoxLayout(files_group)
        self.file_tree = QTreeView()
        self.file_tree.setHeaderHidden(True)
        self.file_model = QStandardItemModel()
        self.file_tree.setModel(self.file_model)
        files_layout.addWidget(self.file_tree)
        left_layout.addWidget(files_group, 1)

    def _create_right_pane(self):
        right_pane = QWidget()
        right_layout = QVBoxLayout(right_pane)
        self.splitter.addWidget(right_pane)

        instructions_group = QGroupBox("Instructions for the AI")
        instructions_layout = QVBoxLayout(instructions_group)
        self.instructions_edit = QTextEdit()
        self.instructions_edit.setPlaceholderText("e.g., Act as a senior developer...")
        instructions_layout.addWidget(self.instructions_edit)
        right_layout.addWidget(instructions_group, 1)

        guidelines_group = QGroupBox("Specific Guidelines & Rules")
        guidelines_layout = QVBoxLayout(guidelines_group)
        self.guidelines_list = QListWidget()
        self.guidelines_list.setAlternatingRowColors(True)
        guidelines_layout.addWidget(self.guidelines_list, 1)
        guideline_buttons_layout = QHBoxLayout()
        self.add_guideline_button = QPushButton("Add")
        self.edit_guideline_button = QPushButton("Edit")
        self.remove_guideline_button = QPushButton("Remove")
        guideline_buttons_layout.addStretch()
        guideline_buttons_layout.addWidget(self.add_guideline_button)
        guideline_buttons_layout.addWidget(self.edit_guideline_button)
        guideline_buttons_layout.addWidget(self.remove_guideline_button)
        guidelines_layout.addLayout(guideline_buttons_layout)
        right_layout.addWidget(guidelines_group, 1)

        golden_rules_group = QGroupBox("Golden Rules")
        golden_rules_layout = QVBoxLayout(golden_rules_group)
        golden_rules_top_layout = QHBoxLayout()
        self.golden_rules_combo = QComboBox()
        self.save_golden_rules_button = QPushButton("Save")
        self.delete_golden_rules_button = QPushButton("Delete")
        golden_rules_top_layout.addWidget(self.golden_rules_combo, 1)
        golden_rules_top_layout.addWidget(self.save_golden_rules_button)
        golden_rules_top_layout.addWidget(self.delete_golden_rules_button)
        golden_rules_layout.addLayout(golden_rules_top_layout)
        self.golden_rules_list = QListWidget()
        self.golden_rules_list.setAlternatingRowColors(True)
        golden_rules_layout.addWidget(self.golden_rules_list, 1)
        golden_rules_buttons_layout = QHBoxLayout()
        self.add_golden_rule_button = QPushButton("Add")
        self.edit_golden_rule_button = QPushButton("Edit")
        self.remove_golden_rule_button = QPushButton("Remove")
        golden_rules_buttons_layout.addStretch()
        golden_rules_buttons_layout.addWidget(self.add_golden_rule_button)
        golden_rules_buttons_layout.addWidget(self.edit_golden_rule_button)
        golden_rules_buttons_layout.addWidget(self.remove_golden_rule_button)
        golden_rules_layout.addLayout(golden_rules_buttons_layout)
        right_layout.addWidget(golden_rules_group, 1)

    def _connect_signals(self):
        self.button_box.accepted.connect(self._start_export)
        self.button_box.rejected.connect(self.reject)
        self.file_model.itemChanged.connect(self._on_item_changed)
        self.loadout_combo.currentIndexChanged.connect(self._on_loadout_selected)
        self.save_loadout_button.clicked.connect(self._save_loadout)
        self.delete_loadout_button.clicked.connect(self._delete_loadout)
        self.add_guideline_button.clicked.connect(self._add_guideline)
        self.edit_guideline_button.clicked.connect(self._edit_guideline)
        self.remove_guideline_button.clicked.connect(self._remove_guideline)
        self.golden_rules_combo.currentIndexChanged.connect(self._on_golden_rule_set_selected)
        self.save_golden_rules_button.clicked.connect(self._save_golden_rule_set)
        self.delete_golden_rules_button.clicked.connect(self._delete_golden_rule_set)
        self.add_golden_rule_button.clicked.connect(self._add_golden_rule)
        self.edit_golden_rule_button.clicked.connect(self._edit_golden_rule)
        self.remove_golden_rule_button.clicked.connect(self._remove_golden_rule)

    def _populate_file_tree(self):
        self.file_model.clear()
        root_node = self.file_model.invisibleRootItem()
        path_map = {self.project_path: root_node}
        ignore_dirs = {'__pycache__', '.git', 'venv', '.venv', 'dist', 'build', 'logs'}
        ignore_files = {'puffin_editor_settings.json'}
        include_extensions = ['.py', '.md', '.txt', '.json', '.html', '.css', '.js', '.yml', '.bat']
        for dirpath, dirnames, filenames in os.walk(self.project_path, topdown=True):
            dirnames[:] = [d for d in dirnames if d not in ignore_dirs]
            parent_node = path_map.get(os.path.normpath(dirpath))
            if parent_node is None:
                continue
            for dirname in sorted(dirnames):
                dir_item = QStandardItem(dirname)
                dir_item.setIcon(qta.icon('fa5.folder', color='grey'))
                dir_item.setCheckable(True)
                dir_item.setCheckState(Qt.CheckState.Checked)
                dir_item.setData(os.path.join(dirpath, dirname), Qt.ItemDataRole.UserRole)
                parent_node.appendRow(dir_item)
                path_map[os.path.join(dirpath, dirname)] = dir_item
            for filename in sorted(filenames):
                if filename in ignore_files:
                    continue
                if "LICENSE" not in filename and not any(filename.lower().endswith(ext) for ext in include_extensions):
                    continue
                file_item = QStandardItem(filename)
                file_item.setIcon(qta.icon('fa5.file-alt', color='grey'))
                file_item.setCheckable(True)
                file_item.setCheckState(Qt.CheckState.Checked)
                file_item.setData(os.path.join(dirpath, filename), Qt.ItemDataRole.UserRole)
                parent_node.appendRow(file_item)
        self.file_tree.expandToDepth(0)

    def _on_item_changed(self, item: QStandardItem):
        if not item.isCheckable():
            return
        check_state = item.checkState()
        if item.hasChildren():
            for row in range(item.rowCount()):
                if (child := item.child(row)):
                    child.setCheckState(check_state)
        if (parent := item.parent()):
            sibling_states = [parent.child(r).checkState() for r in range(parent.rowCount())]
            if all(s == Qt.CheckState.Checked for s in sibling_states):
                parent.setCheckState(Qt.CheckState.Checked)
            elif all(s == Qt.CheckState.Unchecked for s in sibling_states):
                parent.setCheckState(Qt.CheckState.Unchecked)
            else:
                parent.setCheckState(Qt.CheckState.PartiallyChecked)

    def _get_checked_files(self) -> List[str]:
        checked_files = []
        root = self.file_model.invisibleRootItem()
        for row in range(root.rowCount()):
            self._recurse_get_checked(root.child(row), checked_files)
        return checked_files

    def _recurse_get_checked(self, parent_item: QStandardItem, file_list: List[str]):
        if parent_item.checkState() == Qt.CheckState.Unchecked:
            return
        path = parent_item.data(Qt.ItemDataRole.UserRole)
        if path and os.path.isfile(path) and parent_item.checkState() == Qt.CheckState.Checked:
            file_list.append(path)
        if parent_item.hasChildren():
            for row in range(parent_item.rowCount()):
                if (child := parent_item.child(row)):
                    self._recurse_get_checked(child, file_list)

    def _load_prompt_source(self, prompt_type: str, filepath: str):
        if os.path.exists(filepath):
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    self.prompt_sources[prompt_type] = json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                log.error(f"Failed to load prompts from {filepath}: {e}")

    def _load_and_populate_prompts(self):
        self.loadouts = settings_manager.get("ai_export_loadouts", {})
        self.prompt_sources = {PROMPT_TYPE_DEFAULT: DEFAULT_LOADOUTS}
        base_path = get_base_path()
        self._load_prompt_source(PROMPT_TYPE_GENERATIVE, os.path.join(
            base_path, "assets", "prompts", "generative_prompts.json"))
        self._load_prompt_source(PROMPT_TYPE_COMMUNITY, os.path.join(
            base_path, "assets", "prompts", "additional_prompts.json"))
        self.loadout_combo.clear()
        self.loadout_combo.addItem("--- Select a Loadout ---", None)
        self.loadout_combo.insertSeparator(self.loadout_combo.count())
        self._add_prompts_to_combo("Default", PROMPT_TYPE_DEFAULT)
        self._add_prompts_to_combo("New Feature", PROMPT_TYPE_GENERATIVE)
        self._add_prompts_to_combo("Community", PROMPT_TYPE_COMMUNITY)
        if self.loadouts:
            self.loadout_combo.insertSeparator(self.loadout_combo.count())
            for name in sorted(self.loadouts.keys()):
                self.loadout_combo.addItem(name, (PROMPT_TYPE_USER, name))
        self.loadout_combo.setCurrentIndex(0)

    def _add_prompts_to_combo(self, prefix: str, prompt_type: str):
        if (source := self.prompt_sources.get(prompt_type)):
            self.loadout_combo.insertSeparator(self.loadout_combo.count())
            for name in sorted(source.keys()):
                self.loadout_combo.addItem(f"({prefix}) {name}", (prompt_type, name))

    def _on_loadout_selected(self, index: int):
        data = self.loadout_combo.itemData(index)
        if not data:
            self.instructions_edit.clear()
            self.guidelines_list.clear()
            return
        prompt_type, name = data
        loadout_data = self.prompt_sources.get(prompt_type, {}).get(name) \
            if prompt_type != PROMPT_TYPE_USER else self.loadouts.get(name)
        if loadout_data:
            self.instructions_edit.setText(loadout_data.get("instructions", ""))
            self.guidelines_list.clear()
            self.guidelines_list.addItems(loadout_data.get("guidelines", []))
        is_user_loadout = (prompt_type == PROMPT_TYPE_USER)
        self.save_loadout_button.setText("Save As New...")
        self.save_loadout_button.setToolTip("Save the current configuration as a new custom loadout.")
        self.delete_loadout_button.setEnabled(is_user_loadout)
        self.delete_loadout_button.setToolTip("Delete this custom loadout." if is_user_loadout
                                              else "Cannot delete built-in loadouts.")
        if is_user_loadout:
            self.save_loadout_button.setText(f"Update '{name}'")
            self.save_loadout_button.setToolTip(f"Update the custom loadout '{name}'.")

    def _save_loadout(self):
        data = self.loadout_combo.currentData()
        is_update = data and data[0] == PROMPT_TYPE_USER
        name_to_save = data[1] if is_update else None
        if not is_update:
            name, ok = QInputDialog.getText(self, "Save Loadout As",
                                            "Enter a name for this new loadout:")
            if not (ok and name):
                return
            if name in self.loadouts or any(name in s for s in self.prompt_sources.values()):
                QMessageBox.warning(self, "Name Exists", "A loadout with this name already exists.")
                return
            name_to_save = name
        self.loadouts[name_to_save] = {
            "instructions": self.instructions_edit.toPlainText(),
            "guidelines": [self.guidelines_list.item(i).text() for i in range(self.guidelines_list.count())]
        }
        settings_manager.set("ai_export_loadouts", self.loadouts)
        self._load_and_populate_prompts()
        new_index = self.loadout_combo.findData((PROMPT_TYPE_USER, name_to_save))
        if new_index != -1:
            self.loadout_combo.setCurrentIndex(new_index)
        QMessageBox.information(self, "Success", f"Loadout '{name_to_save}' saved.")

    def _delete_loadout(self):
        if not (data := self.loadout_combo.currentData()) or data[0] != PROMPT_TYPE_USER:
            return
        name_to_delete = data[1]
        reply = QMessageBox.question(self, "Confirm Delete", f"Delete the loadout '{name_to_delete}'?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes and name_to_delete in self.loadouts:
            del self.loadouts[name_to_delete]
            settings_manager.set("ai_export_loadouts", self.loadouts)
            self._load_and_populate_prompts()

    def _add_guideline(self):
        text, ok = QInputDialog.getText(self, "Add Guideline", "Enter new guideline:")
        if ok and text:
            self.guidelines_list.addItem(QListWidgetItem(text))

    def _edit_guideline(self):
        if not (item := self.guidelines_list.currentItem()):
            return
        text, ok = QInputDialog.getText(self, "Edit Guideline", "Edit guideline:", text=item.text())
        if ok and text:
            item.setText(text)

    def _remove_guideline(self):
        if (item := self.guidelines_list.currentItem()):
            self.guidelines_list.takeItem(self.guidelines_list.row(item))

    def _load_and_populate_golden_rule_sets(self):
        self.golden_rule_sets = settings_manager.get("ai_export_golden_rules", {})
        self.golden_rules_combo.clear()
        self.golden_rules_combo.addItem("--- Select a Rule Set ---", None)
        self.golden_rules_combo.insertSeparator(self.golden_rules_combo.count())
        for name in sorted(self.golden_rule_sets.keys()):
            self.golden_rules_combo.addItem(name)
        if "Default Golden Rules" in self.golden_rule_sets:
            self.golden_rules_combo.setCurrentText("Default Golden Rules")
        else:
            self.golden_rules_combo.setCurrentIndex(0)

    def _on_golden_rule_set_selected(self, index):
        name = self.golden_rules_combo.currentText()
        is_user_set = name not in ["--- Select a Rule Set ---", "Default Golden Rules"]
        if (rules := self.golden_rule_sets.get(name)):
            self.golden_rules_list.clear()
            self.golden_rules_list.addItems(rules)
        self.save_golden_rules_button.setText("Save As New...")
        self.save_golden_rules_button.setToolTip("Save the current rules as a new set.")
        self.delete_golden_rules_button.setEnabled(is_user_set)
        if is_user_set:
            self.save_golden_rules_button.setText(f"Update '{name}'")
            self.save_golden_rules_button.setToolTip(f"Update the rule set '{name}'.")

    def _save_golden_rule_set(self):
        current_name = self.golden_rules_combo.currentText()
        is_update = current_name not in ["--- Select a Rule Set ---", "Default Golden Rules"]
        name_to_save = current_name if is_update else None
        if not is_update:
            name, ok = QInputDialog.getText(self, "Save Rule Set", "Enter a name for this new rule set:")
            if not (ok and name):
                return
            if name in self.golden_rule_sets:
                QMessageBox.warning(self, "Name Exists", "A rule set with this name already exists.")
                return
            name_to_save = name
        rules = [self.golden_rules_list.item(i).text() for i in range(self.golden_rules_list.count())]
        self.golden_rule_sets[name_to_save] = rules
        settings_manager.set("ai_export_golden_rules", self.golden_rule_sets)
        self._load_and_populate_golden_rule_sets()
        if (new_index := self.golden_rules_combo.findText(name_to_save)) != -1:
            self.golden_rules_combo.setCurrentIndex(new_index)
        QMessageBox.information(self, "Success", f"Golden Rule set '{name_to_save}' saved.")

    def _delete_golden_rule_set(self):
        name = self.golden_rules_combo.currentText()
        if name in self.golden_rule_sets and name != "Default Golden Rules":
            reply = QMessageBox.question(self, "Confirm Delete", f"Delete the rule set '{name}'?",
                                         QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.Yes:
                del self.golden_rule_sets[name]
                settings_manager.set("ai_export_golden_rules", self.golden_rule_sets)
                self._load_and_populate_golden_rule_sets()

    def _add_golden_rule(self):
        text, ok = QInputDialog.getText(self, "Add Golden Rule", "Enter new rule:")
        if ok and text:
            self.golden_rules_list.addItem(QListWidgetItem(text))

    def _edit_golden_rule(self):
        if not (item := self.golden_rules_list.currentItem()):
            return
        text, ok = QInputDialog.getText(self, "Edit Golden Rule", "Edit rule:", text=item.text())
        if ok and text:
            item.setText(text)

    def _remove_golden_rule(self):
        if (item := self.golden_rules_list.currentItem()):
            self.golden_rules_list.takeItem(self.golden_rules_list.row(item))

    def _start_export(self):
        self.selected_files = self._get_checked_files()
        if not self.selected_files:
            QMessageBox.warning(self, "No Files Selected", "Please select files to include.")
            return
        self.progress = QProgressDialog("Linting selected files...", "Cancel", 0, 0, self)
        self.progress.setWindowModality(Qt.WindowModality.WindowModal)
        self.progress.show()
        QCoreApplication.processEvents()
        self.linter_manager.project_lint_results_ready.connect(self._on_lint_complete)
        self.linter_manager.lint_project(self.project_path)

    def _on_lint_complete(self, all_problems: Dict[str, List[Dict]]):
        self.linter_manager.project_lint_results_ready.disconnect(self._on_lint_complete)
        self.progress.close()
        proj_name = os.path.basename(self.project_path)
        sugg_path = os.path.join(os.path.expanduser("~"), f"{proj_name}_ai_export.md")
        fp, _ = QFileDialog.getSaveFileName(self, "Save AI Export File", sugg_path, "Markdown Files (*.md)")
        if not fp:
            return
        QApplication.setOverrideCursor(QCursor(Qt.CursorShape.WaitCursor))
        try:
            instructions = self.instructions_edit.toPlainText()
            guidelines = [self.guidelines_list.item(i).text() for i in range(self.guidelines_list.count())]
            golden_rules = [self.golden_rules_list.item(i).text() for i in range(self.golden_rules_list.count())]
            selected_problems = {k: v for k, v in all_problems.items() if k in self.selected_files}
            success, message = self.project_manager.export_project_for_ai(
                output_filepath=fp, selected_files=self.selected_files,
                instructions=instructions, guidelines=guidelines,
                golden_rules=golden_rules, all_problems=selected_problems
            )
            if success:
                QMessageBox.information(self, "Export Complete", message)
                self.accept()
            else:
                QMessageBox.critical(self, "Export Failed", message)
        finally:
            QApplication.restoreOverrideCursor()
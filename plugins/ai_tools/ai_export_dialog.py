# PuffinPyEditor/plugins/ai_tools/ai_export_dialog.py
import os
import json
from typing import List, Dict, Optional
from datetime import datetime
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QSplitter, QWidget, QGroupBox,
    QTreeView, QTextEdit, QListWidget, QListWidgetItem, QPushButton,
    QDialogButtonBox, QMessageBox, QInputDialog, QComboBox, QProgressDialog,
    QApplication, QCheckBox, QLabel, QToolButton
)
from PyQt6.QtGui import QStandardItemModel, QStandardItem, QCursor
from PyQt6.QtCore import Qt, QCoreApplication
import qtawesome as qta

from app_core.settings_manager import settings_manager
from app_core.project_manager import ProjectManager
from app_core.linter_manager import LinterManager
from utils.logger import log
from utils.helpers import get_base_path
from .api_client import ApiClient
from .ai_response_dialog import AIResponseDialog

PROMPT_TYPE_DEFAULT = "default"
PROMPT_TYPE_GENERATIVE = "generative"
PROMPT_TYPE_COMMUNITY = "community"
PROMPT_TYPE_USER = "user"

DEFAULT_LOADOUTS = {
    "Code Review": {
        "instructions": (
            "You are a senior Python developer performing a code review. "
            "Analyze the provided code for issues related to correctness, "
            "style, performance, and maintainability. Provide constructive "
            "feedback and concrete examples for improvement."
        ),
        "guidelines": [
            "Check for compliance with PEP 8 style guidelines.",
            "Identify potential bugs or logical errors.",
            "Suggest more efficient or 'Pythonic' ways to write the code.",
            "Comment on code clarity, variable naming, and documentation.",
            "Do not suggest new features; focus on improving the existing code.",
            "Structure your feedback by file, then by line number where "
            "applicable."
        ]
    },
    "Documentation Generation": {
        "instructions": (
            "You are a technical writer. Your task is to generate clear and "
            "comprehensive documentation for the provided Python code. Create "
            "docstrings for all public classes, methods, and functions that "
            "are missing them. Follow the Google Python Style Guide for "
            "docstrings."
        ),
        "guidelines": [
            "For each function/method, include an 'Args:' section for "
            "parameters and a 'Returns:' section for the return value.",
            "The main description of the function should be a concise, "
            "one-sentence summary.",
            "If a function raises exceptions, include a 'Raises:' section.",
            "Ensure the generated documentation is professional and ready to "
            "be used in the project."
        ]
    }
}


class AIExportDialog(QDialog):
    """
    A dialog for configuring and exporting a project's context for an AI
    model.
    """
    def __init__(self, project_path: str, project_manager: ProjectManager,
                 linter_manager: LinterManager, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.project_path = project_path
        self.project_manager = project_manager
        self.linter_manager = linter_manager
        self.api_client = ApiClient(settings_manager)
        self.loadouts: Dict[str, Dict] = {}
        self.golden_rule_sets: Dict[str, List[str]] = {}
        self.prompt_sources: Dict[str, Dict] = {}
        self.selected_files: List[str] = []
        self._is_updating_checks = False

        self.setWindowTitle("Export Project for AI")
        self.setMinimumSize(950, 700)
        self.setObjectName("AIExportDialog")

        self._setup_ui()
        self._connect_signals()
        self._populate_file_tree()
        self._load_and_populate_prompts()
        self._load_and_populate_golden_rule_sets()
        self._update_toggle_button_state()

    def _setup_ui(self):
        self.main_layout = QVBoxLayout(self)
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        self.main_layout.addWidget(self.splitter)
        self._create_left_pane()
        self._create_right_pane()
        self.splitter.setSizes([350, 600])

        bottom_layout = QHBoxLayout()

        # --- Combined API and Context Options Group ---
        api_context_group = QGroupBox("Execution & Context")
        api_context_layout = QVBoxLayout(api_context_group)
        api_mode_layout = QHBoxLayout()
        self.api_mode_checkbox = QCheckBox("Enable API Mode")
        self.api_mode_checkbox.setToolTip(
            "Send context directly to an AI API instead of exporting a file.")
        api_mode_layout.addWidget(self.api_mode_checkbox)
        self.api_provider_combo = QComboBox()
        self.api_provider_combo.addItems(
            self.api_client.PROVIDER_CONFIG.keys()
        )
        api_mode_layout.addWidget(QLabel("Provider:"))
        api_mode_layout.addWidget(self.api_provider_combo)
        self.api_model_combo = QComboBox()
        api_mode_layout.addWidget(QLabel("Model:"))
        api_mode_layout.addWidget(self.api_model_combo)
        api_context_layout.addLayout(api_mode_layout)

        context_options_layout = QHBoxLayout()
        self.include_linter_checkbox = QCheckBox("Include linter issues")
        self.include_linter_checkbox.setChecked(True)
        self.include_linter_checkbox.setToolTip(
            "Include linter analysis in the context.")
        context_options_layout.addWidget(self.include_linter_checkbox)
        context_options_layout.addStretch()
        api_context_layout.addLayout(context_options_layout)
        bottom_layout.addWidget(api_context_group, 1)

        # --- File Export Options (only visible when not in API mode) ---
        self.export_options_group = QGroupBox("File Export Options")
        export_options_layout = QHBoxLayout(self.export_options_group)
        export_options_layout.addWidget(QLabel("Format:"))
        self.format_combo = QComboBox()
        self.format_combo.addItems(["AI-Optimized", "Standard Markdown"])
        self.format_combo.setToolTip(
            "Choose export format. 'AI-Optimized' is cleaner for models."
        )
        export_options_layout.addWidget(self.format_combo)
        bottom_layout.addWidget(self.export_options_group, 1)

        self.main_layout.addLayout(bottom_layout)

        self.button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Cancel |
            QDialogButtonBox.StandardButton.Ok)
        self.ok_button = self.button_box.button(
            QDialogButtonBox.StandardButton.Ok)
        self.ok_button.setText("Export")
        self.main_layout.addWidget(self.button_box)
        self._toggle_api_mode(self.api_mode_checkbox.isChecked())

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
        file_actions_layout = QHBoxLayout()
        self.expand_all_button = QToolButton()
        self.expand_all_button.setIcon(
            qta.icon('fa5s.angle-double-down', color='grey'))
        self.expand_all_button.setToolTip("Expand all folders in the tree.")

        self.collapse_all_button = QToolButton()
        self.collapse_all_button.setIcon(
            qta.icon('fa5s.angle-double-up', color='grey'))
        self.collapse_all_button.setToolTip(
            "Collapse all folders in the tree.")

        self.toggle_select_button = QToolButton()
        self.toggle_select_button.setAutoRaise(True)

        for button in [self.expand_all_button, self.collapse_all_button]:
            button.setAutoRaise(True)

        file_actions_layout.addWidget(self.expand_all_button)
        file_actions_layout.addWidget(self.collapse_all_button)
        file_actions_layout.addStretch()
        file_actions_layout.addWidget(self.toggle_select_button)
        files_layout.addLayout(file_actions_layout)

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
        self.instructions_edit.setPlaceholderText(
            "e.g., Act as a senior developer...")
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
        self.save_golden_rules_button = QPushButton("Save As New...")
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
        self.expand_all_button.clicked.connect(self.file_tree.expandAll)
        self.collapse_all_button.clicked.connect(self.file_tree.collapseAll)
        self.toggle_select_button.clicked.connect(
            self._on_toggle_select_clicked)
        self.loadout_combo.currentIndexChanged.connect(
            self._on_loadout_selected)
        self.save_loadout_button.clicked.connect(self._save_loadout)
        self.delete_loadout_button.clicked.connect(self._delete_loadout)
        self.add_guideline_button.clicked.connect(self._add_guideline)
        self.edit_guideline_button.clicked.connect(self._edit_guideline)
        self.remove_guideline_button.clicked.connect(self._remove_guideline)
        self.golden_rules_combo.currentIndexChanged.connect(
            self._on_golden_rule_set_selected)
        self.save_golden_rules_button.clicked.connect(
            self._save_golden_rule_set)
        self.delete_golden_rules_button.clicked.connect(
            self._delete_golden_rule_set)
        self.add_golden_rule_button.clicked.connect(self._add_golden_rule)
        self.edit_golden_rule_button.clicked.connect(self._edit_golden_rule)
        self.remove_golden_rule_button.clicked.connect(
            self._remove_golden_rule)
        self.api_mode_checkbox.toggled.connect(self._toggle_api_mode)
        self.api_provider_combo.currentIndexChanged.connect(
            self._on_api_provider_changed)

    def _toggle_api_mode(self, checked):
        is_api_mode = checked
        for w in [self.api_provider_combo, self.api_model_combo]:
            w.setVisible(is_api_mode)

        self.export_options_group.setVisible(not is_api_mode)
        self.ok_button.setText("Send to AI" if is_api_mode else "Export")

        if is_api_mode:
            self._on_api_provider_changed()

    def _on_api_provider_changed(self):
        provider = self.api_provider_combo.currentText()
        config = self.api_client.PROVIDER_CONFIG.get(provider, {})
        models = config.get("models", [])
        self.api_model_combo.clear()
        self.api_model_combo.addItems(models)

    def _set_all_check_states(self, state: Qt.CheckState):
        self._is_updating_checks = True
        try:
            root = self.file_model.invisibleRootItem()
            for row in range(root.rowCount()):
                self._recursive_set_check_state(root.child(row), state)
        finally:
            self._is_updating_checks = False
        self._update_toggle_button_state()

    def _recursive_set_check_state(
        self, item: QStandardItem, state: Qt.CheckState
    ):
        if item.isCheckable():
            item.setCheckState(state)
        for row in range(item.rowCount()):
            if child_item := item.child(row):
                self._recursive_set_check_state(child_item, state)

    def _on_toggle_select_clicked(self):
        if self._are_all_items_checked():
            self._set_all_check_states(Qt.CheckState.Unchecked)
        else:
            self._set_all_check_states(Qt.CheckState.Checked)

    def _update_toggle_button_state(self):
        if self._are_all_items_checked():
            self.toggle_select_button.setIcon(
                qta.icon('fa5s.check-square', color='grey'))
            self.toggle_select_button.setToolTip("Deselect all files.")
        else:
            self.toggle_select_button.setIcon(
                qta.icon('fa5.square', color='grey'))
            self.toggle_select_button.setToolTip("Select all files.")

    def _get_all_checkable_items(self) -> List[QStandardItem]:
        items = []
        root = self.file_model.invisibleRootItem()

        def recurse(parent_item):
            for row in range(parent_item.rowCount()):
                child = parent_item.child(row)
                if child:
                    if child.isCheckable():
                        items.append(child)
                    if child.hasChildren():
                        recurse(child)
        recurse(root)
        return items

    def _are_all_items_checked(self) -> bool:
        items = self._get_all_checkable_items()
        return bool(items) and all(
            item.checkState() == Qt.CheckState.Checked for item in items)

    def _populate_file_tree(self):
        self.file_model.clear()
        root_node = self.file_model.invisibleRootItem()
        path_map = {self.project_path: root_node}
        ignore_dirs = {
            '__pycache__', '.git', 'venv', '.venv', 'dist', 'build', 'logs',
            'ai_exports'
        }
        ignore_files = {'puffin_editor_settings.json'}
        include_extensions = [
            '.py', '.md', '.txt', '.json', '.html', '.css', '.js', '.yml',
            '.bat'
        ]
        for dirpath, dirnames, filenames in os.walk(
            self.project_path, topdown=True
        ):
            dirnames[:] = [d for d in dirnames if d not in ignore_dirs]
            parent_node = path_map.get(os.path.normpath(dirpath))
            if parent_node is None:
                continue
            for dirname in sorted(dirnames):
                dir_item = QStandardItem(dirname)
                dir_item.setIcon(qta.icon('fa5.folder', color='grey'))
                dir_item.setCheckable(True)
                dir_item.setCheckState(Qt.CheckState.Checked)
                path = os.path.join(dirpath, dirname)
                dir_item.setData(path, Qt.ItemDataRole.UserRole)
                parent_node.appendRow(dir_item)
                path_map[path] = dir_item
            for filename in sorted(filenames):
                if filename in ignore_files:
                    continue
                ext_match = any(
                    filename.lower().endswith(ext) for ext in include_extensions
                )
                if "LICENSE" not in filename and not ext_match:
                    continue
                file_item = QStandardItem(filename)
                file_item.setIcon(qta.icon('fa5.file-alt', color='grey'))
                file_item.setCheckable(True)
                file_item.setCheckState(Qt.CheckState.Checked)
                path = os.path.join(dirpath, filename)
                file_item.setData(path, Qt.ItemDataRole.UserRole)
                parent_node.appendRow(file_item)
        self.file_tree.expandToDepth(0)

    def _on_item_changed(self, item: QStandardItem):
        if self._is_updating_checks:
            return
        self._is_updating_checks = True
        try:
            check_state = item.checkState()
            if check_state != Qt.CheckState.PartiallyChecked:
                self._update_descendant_states(item, check_state)
            if item.parent():
                self._update_ancestor_states(item.parent())
        finally:
            self._is_updating_checks = False
            self._update_toggle_button_state()

    def _update_descendant_states(self, parent_item, state):
        for row in range(parent_item.rowCount()):
            child = parent_item.child(row)
            if child and child.isCheckable() and child.checkState() != state:
                child.setCheckState(state)
                if child.hasChildren():
                    self._update_descendant_states(child, state)

    def _update_ancestor_states(self, parent_item):
        if not parent_item:
            return
        child_states = [
            parent_item.child(r).checkState() for r in
            range(parent_item.rowCount())
        ]
        if all(s == Qt.CheckState.Checked for s in child_states):
            new_state = Qt.CheckState.Checked
        elif all(s == Qt.CheckState.Unchecked for s in child_states):
            new_state = Qt.CheckState.Unchecked
        else:
            new_state = Qt.CheckState.PartiallyChecked
        if parent_item.checkState() != new_state:
            parent_item.setCheckState(new_state)

    def _get_checked_files(self) -> List[str]:
        checked_files = []
        root = self.file_model.invisibleRootItem()
        for row in range(root.rowCount()):
            self._recurse_get_checked(root.child(row), checked_files)
        return checked_files

    def _recurse_get_checked(self, parent_item, file_list):
        if parent_item.checkState() == Qt.CheckState.Unchecked:
            return
        path = parent_item.data(Qt.ItemDataRole.UserRole)
        is_file = path and os.path.isfile(path)
        is_checked = parent_item.checkState() == Qt.CheckState.Checked
        if is_file and is_checked:
            file_list.append(path)
        if parent_item.hasChildren():
            for row in range(parent_item.rowCount()):
                if child := parent_item.child(row):
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
        generative_path = os.path.join(
            base_path, "assets", "prompts", "generative_prompts.json"
        )
        community_path = os.path.join(
            base_path, "assets", "prompts", "additional_prompts.json"
        )
        self._load_prompt_source(PROMPT_TYPE_GENERATIVE, generative_path)
        self._load_prompt_source(PROMPT_TYPE_COMMUNITY, community_path)
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

    def _add_prompts_to_combo(self, prefix, prompt_type):
        if source := self.prompt_sources.get(prompt_type):
            self.loadout_combo.insertSeparator(self.loadout_combo.count())
            for name in sorted(source.keys()):
                self.loadout_combo.addItem(
                    f"({prefix}) {name}", (prompt_type, name))

    def _on_loadout_selected(self, index):
        data = self.loadout_combo.itemData(index)
        if not data:
            self.instructions_edit.clear()
            self.guidelines_list.clear()
            return
        prompt_type, name = data
        if prompt_type == PROMPT_TYPE_USER:
            loadout_data = self.loadouts.get(name)
        else:
            loadout_data = self.prompt_sources.get(prompt_type, {}).get(name)

        if loadout_data:
            self.instructions_edit.setText(loadout_data.get("instructions", ""))
            self.guidelines_list.clear()
            self.guidelines_list.addItems(loadout_data.get("guidelines", []))
        is_user_loadout = (prompt_type == PROMPT_TYPE_USER)
        self.save_loadout_button.setText("Save As New...")
        self.save_loadout_button.setToolTip(
            "Save the current configuration as a new custom loadout.")
        self.delete_loadout_button.setEnabled(is_user_loadout)
        self.delete_loadout_button.setToolTip(
            "Delete this custom loadout." if is_user_loadout else
            "Cannot delete built-in loadouts."
        )
        if is_user_loadout:
            self.save_loadout_button.setText(f"Update '{name}'")
            self.save_loadout_button.setToolTip(
                f"Update the custom loadout '{name}'.")

    def _save_loadout(self):
        data = self.loadout_combo.currentData()
        is_update = data and data[0] == PROMPT_TYPE_USER
        name_to_save = data[1] if is_update else None
        if not is_update:
            name, ok = QInputDialog.getText(
                self, "Save Loadout As", "Enter name for new loadout:")
            if not (ok and name):
                return
            if name in self.loadouts or any(
                name in s for s in self.prompt_sources.values()
            ):
                QMessageBox.warning(self, "Name Exists",
                                    "A loadout with this name already exists.")
                return
            name_to_save = name
        guidelines = [self.guidelines_list.item(i).text() for i in
                      range(self.guidelines_list.count())]
        self.loadouts[name_to_save] = {
            "instructions": self.instructions_edit.toPlainText(),
            "guidelines": guidelines
        }
        settings_manager.set("ai_export_loadouts", self.loadouts)
        self._load_and_populate_prompts()
        new_index = self.loadout_combo.findData((PROMPT_TYPE_USER, name_to_save))
        if new_index != -1:
            self.loadout_combo.setCurrentIndex(new_index)
        QMessageBox.information(
            self, "Success", f"Loadout '{name_to_save}' saved.")

    def _delete_loadout(self):
        data = self.loadout_combo.currentData()
        if not data or data[0] != PROMPT_TYPE_USER:
            return
        name_to_delete = data[1]
        reply = QMessageBox.question(
            self, "Confirm Delete", f"Delete '{name_to_delete}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes and name_to_delete in self.loadouts:
            del self.loadouts[name_to_delete]
            settings_manager.set("ai_export_loadouts", self.loadouts)
            self._load_and_populate_prompts()

    def _add_guideline(self):
        text, ok = QInputDialog.getText(
            self, "Add Guideline", "Enter new guideline:")
        if ok and text:
            self.guidelines_list.addItem(QListWidgetItem(text))

    def _edit_guideline(self):
        if not (item := self.guidelines_list.currentItem()):
            return
        text, ok = QInputDialog.getText(
            self, "Edit Guideline", "Edit guideline:", text=item.text())
        if ok and text:
            item.setText(text)

    def _remove_guideline(self):
        if (item := self.guidelines_list.currentItem()):
            row = self.guidelines_list.row(item)
            self.guidelines_list.takeItem(row)

    def _load_and_populate_golden_rule_sets(self):
        self.golden_rule_sets = settings_manager.get(
            "ai_export_golden_rules", {})
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
        is_user_set = name not in ["--- Select a Rule Set ---"]
        if rules := self.golden_rule_sets.get(name):
            self.golden_rules_list.clear()
            self.golden_rules_list.addItems(rules)
        self.save_golden_rules_button.setText("Save As New...")
        self.save_golden_rules_button.setToolTip(
            "Save the current rules as a new set.")
        self.delete_golden_rules_button.setEnabled(
            is_user_set and name != "Default Golden Rules")
        if is_user_set:
            self.save_golden_rules_button.setText(f"Update '{name}'")
            self.save_golden_rules_button.setToolTip(
                f"Update the rule set '{name}'.")

    def _save_golden_rule_set(self):
        current_name = self.golden_rules_combo.currentText()
        is_update = current_name not in ["--- Select a Rule Set ---"]
        name_to_save = current_name if is_update else None
        if not is_update:
            name, ok = QInputDialog.getText(
                self, "Save Rule Set", "Enter name for rule set:")
            if not (ok and name):
                return
            if name in self.golden_rule_sets:
                QMessageBox.warning(
                    self, "Name Exists",
                    "A rule set with this name already exists.")
                return
            name_to_save = name
        rules = [self.golden_rules_list.item(i).text() for i in
                 range(self.golden_rules_list.count())]
        self.golden_rule_sets[name_to_save] = rules
        settings_manager.set("ai_export_golden_rules", self.golden_rule_sets)
        self._load_and_populate_golden_rule_sets()
        if (new_index := self.golden_rules_combo.findText(name_to_save)) != -1:
            self.golden_rules_combo.setCurrentIndex(new_index)
        QMessageBox.information(
            self, "Success", f"Golden Rule set '{name_to_save}' saved.")

    def _delete_golden_rule_set(self):
        name = self.golden_rules_combo.currentText()
        if name in self.golden_rule_sets and name != "Default Golden Rules":
            reply = QMessageBox.question(
                self, "Confirm Delete", f"Delete the rule set '{name}'?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.Yes:
                del self.golden_rule_sets[name]
                settings_manager.set(
                    "ai_export_golden_rules", self.golden_rule_sets)
                self._load_and_populate_golden_rule_sets()

    def _add_golden_rule(self):
        text, ok = QInputDialog.getText(
            self, "Add Golden Rule", "Enter new rule:")
        if ok and text:
            self.golden_rules_list.addItem(QListWidgetItem(text))

    def _edit_golden_rule(self):
        if not (item := self.golden_rules_list.currentItem()):
            return
        text, ok = QInputDialog.getText(
            self, "Edit Golden Rule", "Edit rule:", text=item.text())
        if ok and text:
            item.setText(text)

    def _remove_golden_rule(self):
        if (item := self.golden_rules_list.currentItem()):
            row = self.golden_rules_list.row(item)
            self.golden_rules_list.takeItem(row)

    def _generate_file_content_string(
        self, files: List[str], problems: Dict[str, List[Dict]]
    ) -> str:
        """Generates the file content portion of the prompt as a string."""
        content_parts = []
        for file_path in files:
            rel_path = os.path.relpath(
                file_path, self.project_path).replace(os.sep, '/')
            content_parts.append(f"### File: `/{rel_path}`\n")
            if file_problems := problems.get(file_path):
                content_parts.append("#### Linter Issues Found:\n```\n")
                for p in file_problems:
                    line_info = f"- L{p.get('line', '?')}"
                    if 'column' in p and p.get('column') is not None:
                        line_info += f":C{p.get('column')}"
                    code = p.get('code', 'N/A')
                    message = p.get('message', 'No message available')
                    msg = f"{line_info} ({code}) {message}\n"
                    content_parts.append(msg)
                content_parts.append("```\n\n")
            try:
                with open(file_path, 'r', encoding='utf-8') as cf:
                    content = cf.read()
                lang = self._get_lang_for_file(file_path)
                content_parts.append(f"```{lang}\n{content}\n```\n")
            except Exception as e:
                content_parts.append(f"```\nError reading file: {e}\n```\n")
        return "\n".join(content_parts)

    def _generate_file_tree_text(self, files: List[str]) -> str:
        tree = {}
        base_path = self.project_path
        for f in files:
            rel_path = os.path.relpath(f, base_path)
            parts = rel_path.split(os.sep)
            curr_level = tree
            for part in parts[:-1]:
                curr_level = curr_level.setdefault(part, {})
            curr_level[parts[-1]] = None

        def build_tree_string(d, indent=''):
            s = ''
            items = sorted(d.items())
            for i, (key, value) in enumerate(items):
                is_last = i == len(items) - 1
                s += indent + ('└── ' if is_last else '├── ') + key + '\n'
                if value is not None:
                    new_indent = indent + ('    ' if is_last else '│   ')
                    s += build_tree_string(value, new_indent)
            return s
        return (f"/{os.path.basename(base_path)}\n"
                f"{build_tree_string(tree, ' ')}")

    def _get_lang_for_file(self, file_path: str) -> str:
        ext = os.path.splitext(file_path)[1].lower()
        return {
            '.py': 'python', '.json': 'json', '.md': 'markdown',
            '.html': 'html', '.css': 'css', '.js': 'javascript',
            '.ts': 'typescript', '.yml': 'yaml', '.yaml': 'yaml',
            '.xml': 'xml', '.sh': 'shell', '.bat': 'batch',
        }.get(ext, 'text')

    def _build_prompt(
        self, instructions, guidelines, golden_rules, files, problems
    ) -> tuple[str, str]:
        """Builds system and user prompts for an API request."""
        system_parts = []
        if instructions:
            system_parts.append(f"## AI Instructions\n{instructions}")
        if guidelines:
            rules_str = "\n".join(f"- {rule}" for rule in guidelines)
            system_parts.append(f"## Guidelines & Rules\n{rules_str}")
        if golden_rules:
            rules_str = "\n".join(
                f"{i}. {rule}" for i, rule in enumerate(golden_rules, 1))
            system_parts.append(f"## Golden Rules\n{rules_str}")
        system_prompt = "\n\n".join(system_parts)
        user_prompt = "\n".join([
            "Here is the project context you need to work with.",
            "## File Tree\n```",
            self._generate_file_tree_text(files),
            "```",
            "## File Contents",
            self._generate_file_content_string(files, problems)
        ])
        return system_prompt, user_prompt

    def _start_export(self):
        self.selected_files = self._get_checked_files()
        if not self.selected_files:
            QMessageBox.warning(
                self, "No Files Selected", "Please select files to include.")
            return
        self.progress = QProgressDialog(
            "Linting selected files...", "Cancel", 0, 0, self)
        self.progress.setWindowModality(Qt.WindowModality.WindowModal)
        self.progress.show()
        QCoreApplication.processEvents()
        self.linter_manager.project_lint_results_ready.connect(
            self._on_lint_complete)
        self.linter_manager.lint_project(self.project_path)

    def _on_lint_complete(self, all_problems: Dict[str, List[Dict]]):
        self.linter_manager.project_lint_results_ready.disconnect(
            self._on_lint_complete)
        if self.progress.wasCanceled():
            return

        self.progress.setLabelText("Preparing context...")
        QCoreApplication.processEvents()

        instructions = self.instructions_edit.toPlainText()
        guidelines = [self.guidelines_list.item(i).text() for i in
                      range(self.guidelines_list.count())]
        golden_rules = [self.golden_rules_list.item(i).text() for i in
                        range(self.golden_rules_list.count())]

        selected_problems = {}
        if self.include_linter_checkbox.isChecked():
            selected_problems = {k: v for k, v in all_problems.items()
                                 if k in self.selected_files}

        if self.api_mode_checkbox.isChecked():
            self.progress.setLabelText("Sending to AI...")
            self._handle_api_request(
                instructions, guidelines, golden_rules, selected_problems)
        else:
            self.progress.setLabelText("Saving file...")
            self._handle_file_export(
                instructions, guidelines, golden_rules, selected_problems)
        if not self.progress.wasCanceled():
            self.progress.close()

    def _handle_api_request(
        self, instructions, guidelines, golden_rules, problems
    ):
        QApplication.setOverrideCursor(QCursor(Qt.CursorShape.WaitCursor))
        try:
            provider = self.api_provider_combo.currentText()
            model = self.api_model_combo.currentText()
            system_prompt, user_prompt = self._build_prompt(
                instructions, guidelines, golden_rules, self.selected_files,
                problems
            )
            success, response = self.api_client.send_request(
                provider, model, system_prompt, user_prompt)

            if success:
                response_dialog = AIResponseDialog(response, self)
                response_dialog.exec()
                self.accept()
            else:
                QMessageBox.critical(self, "API Error", response)
        finally:
            QApplication.restoreOverrideCursor()

    def _handle_file_export(
        self, instructions, guidelines, golden_rules, problems
    ):
        base_path = get_base_path()
        export_dir = os.path.join(base_path, "ai_exports")
        try:
            os.makedirs(export_dir, exist_ok=True)
        except OSError as e:
            msg = f"Could not create export directory at {export_dir}: {e}"
            log.error(msg)
            QMessageBox.critical(self, "Export Failed", msg)
            return

        proj_name = os.path.basename(self.project_path)
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"{proj_name}_export_{timestamp}.md"
        output_filepath = os.path.join(export_dir, filename)

        QApplication.setOverrideCursor(QCursor(Qt.CursorShape.WaitCursor))
        try:
            if "Standard Markdown" in self.format_combo.currentText():
                success, msg = self.project_manager.export_project_for_ai(
                    output_filepath=output_filepath,
                    selected_files=self.selected_files,
                    instructions=instructions, guidelines=guidelines,
                    golden_rules=golden_rules, all_problems=problems
                )
                if success:
                    message = f"Project exported successfully to:\n{output_filepath}"
                else:
                    message = msg
            else:
                system_prompt, user_prompt = self._build_prompt(
                    instructions, guidelines, golden_rules,
                    self.selected_files, problems)
                header = (
                    f"# Project Export: {os.path.basename(self.project_path)}\n"
                    f"## Export Timestamp: {datetime.now().isoformat()}\n---"
                )
                content = "\n\n".join(
                    [header, system_prompt, "---", "## Project Files", user_prompt]
                )
                with open(output_filepath, 'w', encoding='utf-8') as f:
                    f.write(content)
                success = True
                message = f"Project exported successfully to:\n{output_filepath}"

            if success:
                QMessageBox.information(self, "Export Complete", message)
                self.accept()
            else:
                QMessageBox.critical(self, "Export Failed", message)
        except Exception as e:
            log.error(f"Export failed with exception: {e}", exc_info=True)
            QMessageBox.critical(self, "Export Failed",
                                 f"An error occurred: '{e}'")
        finally:
            QApplication.restoreOverrideCursor()
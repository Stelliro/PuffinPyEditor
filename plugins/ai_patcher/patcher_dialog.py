# /plugins/ai_patcher/patcher_dialog.py
import os
import re
from typing import Dict, List, Optional

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QWidget, QSplitter,
    QComboBox, QTextEdit, QPushButton, QStackedWidget,
    QFileDialog, QMessageBox, QFrame, QLabel, QListWidget,
    QTreeView, QToolButton, QInputDialog, QSpinBox, QCheckBox,
    QGroupBox, QFormLayout, QLineEdit
)
from PyQt6.QtGui import QStandardItemModel, QStandardItem
from PyQt6.QtCore import Qt, QTimer
import qtawesome as qta

from app_core.puffin_api import PuffinPluginAPI
from app_core.settings_manager import settings_manager
from .response_parser import parse_llm_response, apply_changes_to_project
from utils.logger import log


class AIPatcherDialog(QDialog):
    """A dialog to generate patch prompts and apply AI-generated code changes."""

    def __init__(self, puffin_api: PuffinPluginAPI, parent=None):
        super().__init__(parent)
        self.api = puffin_api
        self.project_manager = self.api.get_manager("project")
        self.project_root = self.project_manager.get_active_project_path()
        self.golden_rule_sets: Dict[str, List[str]] = {}
        self._is_updating_checks = False

        self.setWindowTitle("AI Patcher")
        self.setMinimumSize(950, 700)

        self._setup_ui()
        self._connect_signals()
        self._populate_file_tree()
        self._load_and_populate_golden_rule_sets()
        self._on_mode_changed(0) # Set initial mode

    def _setup_ui(self):
        self.main_layout = QVBoxLayout(self)
        
        mode_layout = QHBoxLayout()
        mode_layout.addWidget(QLabel("Mode:"))
        self.mode_combo = QComboBox()
        self.mode_combo.addItems(["Generate Patch Prompt", "Apply Patch from AI"])
        mode_layout.addWidget(self.mode_combo, 1)
        self.main_layout.addLayout(mode_layout)

        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        self.main_layout.addWidget(self.splitter, 1)
        
        self._create_left_pane()
        self._create_right_pane()

        self.splitter.setSizes([350, 600])

        self.action_button = QPushButton("Generate Prompt")
        self.copy_button = QPushButton("Copy to Clipboard")
        self.copy_button.setIcon(qta.icon('fa5s.copy'))
        
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(self.copy_button)
        button_layout.addWidget(self.action_button)
        self.main_layout.addLayout(button_layout)

    def _create_left_pane(self):
        left_pane = QWidget()
        left_layout = QVBoxLayout(left_pane)
        self.splitter.addWidget(left_pane)

        files_group = QGroupBox("Select Files to Include")
        files_layout = QVBoxLayout(files_group)
        
        file_actions_layout = QHBoxLayout()
        self.expand_all_button = QToolButton(icon=qta.icon('fa5s.angle-double-down', color='grey'), toolTip="Expand All")
        self.collapse_all_button = QToolButton(icon=qta.icon('fa5s.angle-double-up', color='grey'), toolTip="Collapse All")
        self.toggle_select_button = QToolButton(autoRaise=True)
        for button in [self.expand_all_button, self.collapse_all_button]: button.setAutoRaise(True)
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
        left_layout.addWidget(files_group)

    def _create_right_pane(self):
        right_pane = QWidget()
        self.right_layout = QVBoxLayout(right_pane)
        self.splitter.addWidget(right_pane)

        # Main workspace for prompt/response
        self.main_workspace = QTextEdit()
        self.main_workspace.setFontFamily("Consolas")
        self.right_layout.addWidget(self.main_workspace, 2)

        # Options panels
        self.stacked_options = QStackedWidget()
        self.stacked_options.addWidget(self._create_generate_options())
        self.stacked_options.addWidget(self._create_apply_options())
        self.right_layout.addWidget(self.stacked_options, 1)

    def _create_generate_options(self) -> QWidget:
        container = QWidget()
        layout = QVBoxLayout(container)
        
        context_group = QGroupBox("Context File & Golden Rules")
        context_layout = QVBoxLayout(context_group)
        
        # Context File Selection
        context_file_layout = QHBoxLayout()
        context_file_layout.addWidget(QLabel("Context File (e.g., changelog.md):"))
        self.context_file_path = QLineEdit(readOnly=True, placeholderText="Click 'Browse' to select a file...")
        browse_button = QPushButton("Browse...")
        browse_button.clicked.connect(self._browse_for_context_file)
        context_file_layout.addWidget(self.context_file_path, 1)
        context_file_layout.addWidget(browse_button)
        context_layout.addLayout(context_file_layout)
        
        # Golden Rules
        golden_rules_top_layout = QHBoxLayout()
        self.golden_rules_combo = QComboBox()
        self.save_golden_rules_button = QPushButton("Save As New...")
        golden_rules_top_layout.addWidget(self.golden_rules_combo, 1)
        golden_rules_top_layout.addWidget(self.save_golden_rules_button)
        context_layout.addLayout(golden_rules_top_layout)
        self.golden_rules_list = QListWidget(minimumHeight=80)
        context_layout.addWidget(self.golden_rules_list)

        # AI Response Formatting
        formatting_group = QGroupBox("AI Response Formatting")
        form_layout = QFormLayout(formatting_group)
        self.break_on_lines_check = QCheckBox("Request new message every")
        self.break_lines_spin = QSpinBox(minimum=500, maximum=8000, value=2000, singleStep=100, suffix=" lines")
        lines_layout = QHBoxLayout()
        lines_layout.addWidget(self.break_on_lines_check)
        lines_layout.addWidget(self.break_lines_spin)
        
        self.break_on_files_check = QCheckBox("Request new message every")
        self.break_files_spin = QSpinBox(minimum=1, maximum=100, value=5, suffix=" files")
        files_layout = QHBoxLayout()
        files_layout.addWidget(self.break_on_files_check)
        files_layout.addWidget(self.break_files_spin)

        form_layout.addRow(lines_layout)
        form_layout.addRow(files_layout)
        
        layout.addWidget(context_group)
        layout.addWidget(formatting_group)
        layout.addStretch()
        return container

    def _create_apply_options(self) -> QWidget:
        widget = QWidget()
        layout = QHBoxLayout(widget)
        paste_button = QPushButton("Paste from Clipboard")
        paste_button.setIcon(qta.icon('fa5s.paste'))
        paste_button.clicked.connect(lambda: self.main_workspace.paste())
        layout.addWidget(paste_button)
        layout.addStretch()
        return widget

    def _connect_signals(self):
        self.mode_combo.currentIndexChanged.connect(self._on_mode_changed)
        self.action_button.clicked.connect(self._on_action_button_clicked)
        self.copy_button.clicked.connect(lambda: self.main_workspace.selectAll() and self.main_workspace.copy())
        
        # File Tree Signals
        self.file_model.itemChanged.connect(self._on_item_changed)
        self.expand_all_button.clicked.connect(self.file_tree.expandAll)
        self.collapse_all_button.clicked.connect(self.file_tree.collapseAll)
        self.toggle_select_button.clicked.connect(self._on_toggle_select_clicked)

        # Golden Rules Signals
        self.golden_rules_combo.currentIndexChanged.connect(self._on_golden_rule_set_selected)
        self.save_golden_rules_button.clicked.connect(self._save_golden_rule_set)

    def _on_mode_changed(self, index: int):
        self.main_workspace.clear()
        self.copy_button.hide()
        self.stacked_options.setCurrentIndex(index)
        if index == 0: # Generate mode
            self.action_button.setText("Generate Prompt")
            self.main_workspace.setReadOnly(True)
            self.main_workspace.setPlaceholderText("Configure options and click 'Generate Prompt'...")
        else: # Apply mode
            self.action_button.setText("Preview & Apply Patch")
            self.main_workspace.setReadOnly(False)
            self.main_workspace.setPlaceholderText("Paste the full markdown response from the AI here.")

    def _on_action_button_clicked(self):
        if self.mode_combo.currentIndex() == 0: self._generate_prompt()
        else: self._apply_patch()

    def _browse_for_context_file(self):
        filepath, _ = QFileDialog.getOpenFileName(self, "Select Context File", self.project_root, "All Files (*)")
        if filepath: self.context_file_path.setText(filepath)

    def _generate_prompt(self):
        selected_files = self._get_checked_files()
        if not selected_files:
            QMessageBox.warning(self, "No Files Selected", "Please select at least one file to include in the prompt.")
            return

        context_file = self.context_file_path.text()
        context_content = ""
        if context_file:
            try:
                with open(context_file, 'r', encoding='utf-8') as f: context_content = f.read()
            except IOError as e:
                QMessageBox.critical(self, "Error Reading File", f"Could not read context file: {e}")
                return
        
        # Build instructions
        instructions = [
            "You are an expert developer tasked with updating a codebase. Based on the provided "
            f"context file (`{os.path.basename(context_file)}`), please update the project source files. "
            "Your response MUST ONLY contain the complete, updated content for each file that needs to change. "
            "Enclose each file's content in the standard `### File:` and code block format. "
            "Do not add any extra commentary, explanations, or summaries outside of the code blocks."
        ]
        if self.break_on_lines_check.isChecked():
            instructions.append(f"IMPORTANT: Please write your response in a new message every {self.break_lines_spin.value()} lines.")
        if self.break_on_files_check.isChecked():
            instructions.append(f"IMPORTANT: Please write your response in a new message every {self.break_files_spin.value()} files.")

        guidelines = [f"The primary instructions are in the context file: {os.path.basename(context_file)}"] if context_content else []
        golden_rules = [self.golden_rules_list.item(i).text() for i in range(self.golden_rules_list.count())]

        # Build prompt using a simplified version of the AI Export logic
        project_name = os.path.basename(self.project_root)
        file_tree_text = self.project_manager._generate_file_tree_from_list(self.project_root, selected_files)
        
        prompt_parts = [
            f"# Project Patch Request: {project_name}", "---",
            "## AI Instructions", "```text", "\n".join(instructions), "```",
        ]
        if guidelines: prompt_parts.extend(["## Guidelines", "```text", "\n".join(f"- {g}" for g in guidelines), "```"])
        if golden_rules: prompt_parts.extend(["## Golden Rules", "```text", "\n".join(f"{i+1}. {g}" for i,g in enumerate(golden_rules)), "```"])
        if context_content: prompt_parts.extend(["---", f"## Context File: `{os.path.basename(context_file)}`", "```markdown", context_content, "```"])
        
        prompt_parts.extend(["---", "## Project Files", f"```\n/{project_name}\n{file_tree_text}\n```"])
        
        for file_path in sorted(selected_files):
            relative_path = os.path.relpath(file_path, self.project_root).replace(os.sep, '/')
            lang = os.path.splitext(file_path)[1].lstrip('.') or 'text'
            prompt_parts.append(f"### File: `/{relative_path}`\n```{lang}")
            try:
                with open(file_path, 'r', encoding='utf-8') as f: prompt_parts.append(f.read())
            except Exception as e:
                prompt_parts.append(f"[Error reading file: {e}]")
            prompt_parts.append("```")

        self.main_workspace.setPlainText("\n".join(prompt_parts))
        self.copy_button.show()
        self.api.show_status_message("Prompt generated successfully.", 3000)

    def _apply_patch(self):
        response_text = self.main_workspace.toPlainText()
        if not response_text.strip():
            QMessageBox.warning(self, "Empty Response", "Please paste the AI's response into the text area.")
            return
            
        changes = parse_llm_response(response_text)
        if not changes:
            QMessageBox.information(self, "No Changes Found", "Could not find any valid file blocks to apply.")
            return

        confirmation_dialog = QDialog(self)
        confirmation_dialog.setWindowTitle("Confirm Changes")
        layout = QVBoxLayout(confirmation_dialog)
        layout.addWidget(QLabel("The following files will be overwritten. Please review:"))
        list_widget = QListWidget()
        list_widget.addItems(sorted(changes.keys()))
        layout.addWidget(list_widget)
        
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Apply | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(confirmation_dialog.accept)
        buttons.rejected.connect(confirmation_dialog.reject)
        layout.addWidget(buttons)
        
        if confirmation_dialog.exec():
            success, message = apply_changes_to_project(self.project_root, changes)
            if success:
                QMessageBox.information(self, "Patch Applied", message)
                if explorer := self.api.get_main_window().explorer_panel:
                    explorer.refresh()
            else:
                QMessageBox.critical(self, "Patch Failed", message)

    # --- Methods copied from AIExportDialog for File Tree ---
    def _populate_file_tree(self):
        self.file_model.clear()
        root_node = self.file_model.invisibleRootItem()
        path_map = {self.project_root: root_node}
        ignore_dirs = {'.git', '__pycache__', 'venv', '.venv', 'dist', 'build', 'logs', 'ai_exports'}
        for dirpath, dirnames, filenames in os.walk(self.project_root, topdown=True):
            dirnames[:] = [d for d in dirnames if d not in ignore_dirs]
            parent_node = path_map.get(os.path.normpath(dirpath))
            if parent_node is None: continue
            for dirname in sorted(dirnames):
                dir_item = QStandardItem(dirname); dir_item.setIcon(qta.icon('fa5.folder', color='grey')); dir_item.setCheckable(True)
                path = os.path.join(dirpath, dirname); dir_item.setData(path, Qt.ItemDataRole.UserRole)
                parent_node.appendRow(dir_item); path_map[path] = dir_item
            for filename in sorted(filenames):
                file_item = QStandardItem(filename); file_item.setIcon(qta.icon('fa5.file-alt', color='grey')); file_item.setCheckable(True)
                path = os.path.join(dirpath, filename); file_item.setData(path, Qt.ItemDataRole.UserRole)
                parent_node.appendRow(file_item)
        self.file_tree.expandToDepth(0)
        self._set_all_check_states(Qt.CheckState.Checked)

    def _set_all_check_states(self, state: Qt.CheckState):
        self._is_updating_checks = True
        root = self.file_model.invisibleRootItem()
        for row in range(root.rowCount()): self._recursive_set_check_state(root.child(row), state)
        self._is_updating_checks = False
        self._update_toggle_button_state()

    def _recursive_set_check_state(self, item, state):
        if item.isCheckable(): item.setCheckState(state)
        for row in range(item.rowCount()):
            if child_item := item.child(row): self._recursive_set_check_state(child_item, state)

    def _on_toggle_select_clicked(self):
        if self._are_all_items_checked(): self._set_all_check_states(Qt.CheckState.Unchecked)
        else: self._set_all_check_states(Qt.CheckState.Checked)

    def _update_toggle_button_state(self):
        icon_name = 'fa5s.check-square' if self._are_all_items_checked() else 'fa5.square'
        tooltip = "Deselect all files." if self._are_all_items_checked() else "Select all files."
        self.toggle_select_button.setIcon(qta.icon(icon_name, color='grey')); self.toggle_select_button.setToolTip(tooltip)

    def _are_all_items_checked(self) -> bool:
        items = [self.file_model.itemFromIndex(self.file_model.index(r, 0, p)) for r in range(self.file_model.rowCount(p)) for p in [self.file_model.invisibleRootItem().index()]]
        return bool(items) and all(item.checkState() == Qt.CheckState.Checked for item in self._get_all_checkable_items())

    def _get_all_checkable_items(self) -> List[QStandardItem]:
        items = []; root = self.file_model.invisibleRootItem()
        def recurse(parent):
            for r in range(parent.rowCount()):
                child = parent.child(r)
                if child:
                    if child.isCheckable(): items.append(child)
                    if child.hasChildren(): recurse(child)
        recurse(root)
        return items
        
    def _on_item_changed(self, item: QStandardItem):
        if self._is_updating_checks: return
        self._is_updating_checks = True
        state = item.checkState()
        if state != Qt.CheckState.PartiallyChecked: self._update_descendant_states(item, state)
        if item.parent(): self._update_ancestor_states(item.parent())
        self._is_updating_checks = False
        self._update_toggle_button_state()

    def _update_descendant_states(self, parent, state):
        for r in range(parent.rowCount()):
            child = parent.child(r)
            if child and child.isCheckable() and child.checkState() != state:
                child.setCheckState(state)
                if child.hasChildren(): self._update_descendant_states(child, state)

    def _update_ancestor_states(self, parent):
        if not parent: return
        states = [parent.child(r).checkState() for r in range(parent.rowCount())]
        new_state = Qt.CheckState.Checked if all(s == Qt.CheckState.Checked for s in states) else Qt.CheckState.Unchecked if all(s == Qt.CheckState.Unchecked for s in states) else Qt.CheckState.PartiallyChecked
        if parent.checkState() != new_state: parent.setCheckState(new_state)

    def _get_checked_files(self) -> List[str]:
        files = []; root = self.file_model.invisibleRootItem()
        def recurse(parent):
            if parent.checkState() == Qt.CheckState.Unchecked: return
            path = parent.data(Qt.ItemDataRole.UserRole)
            if path and os.path.isfile(path) and parent.checkState() == Qt.CheckState.Checked: files.append(path)
            if parent.hasChildren():
                for r in range(parent.rowCount()):
                    if child := parent.child(r): recurse(child)
        for r in range(root.rowCount()): recurse(root.child(r))
        return files

    # --- Methods copied from AIExportDialog for Golden Rules ---
    def _load_and_populate_golden_rule_sets(self):
        self.golden_rule_sets = settings_manager.get("ai_export_golden_rules", {})
        self.golden_rules_combo.clear()
        for name in sorted(self.golden_rule_sets.keys()): self.golden_rules_combo.addItem(name)
        if "Default Golden Rules" in self.golden_rule_sets: self.golden_rules_combo.setCurrentText("Default Golden Rules")
        else: self.golden_rules_combo.setCurrentIndex(-1)
        self._on_golden_rule_set_selected()

    def _on_golden_rule_set_selected(self):
        name = self.golden_rules_combo.currentText()
        self.golden_rules_list.clear()
        if rules := self.golden_rule_sets.get(name): self.golden_rules_list.addItems(rules)
    
    def _save_golden_rule_set(self):
        name, ok = QInputDialog.getText(self, "Save Rule Set", "Enter name for new rule set:")
        if not (ok and name): return
        if name in self.golden_rule_sets:
            QMessageBox.warning(self, "Name Exists", "A rule set with this name already exists.")
            return
        rules = [self.golden_rules_list.item(i).text() for i in range(self.golden_rules_list.count())]
        self.golden_rule_sets[name] = rules
        settings_manager.set("ai_export_golden_rules", self.golden_rule_sets)
        self._load_and_populate_golden_rule_sets()
        if (new_index := self.golden_rules_combo.findText(name)) != -1: self.golden_rules_combo.setCurrentIndex(new_index)
        QMessageBox.information(self, "Success", f"Golden Rule set '{name}' saved.")
# /plugins/ai_patcher/patcher_dialog.py
import os
import re
from typing import Dict, List, Optional
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QWidget, QSplitter,
    QTextEdit, QPushButton, QMessageBox, QFrame, QLabel, QListWidget,
    QTreeView, QToolButton, QInputDialog, QSpinBox, QCheckBox,
    QGroupBox, QFormLayout, QLineEdit, QStackedWidget,
    QDialogButtonBox, QListWidgetItem,
)
from PyQt6.QtGui import QStandardItemModel, QStandardItem, QFont
from PyQt6.QtCore import Qt, QTimer
import qtawesome as qta
from app_core.puffin_api import PuffinPluginAPI
from app_core.settings_manager import settings_manager
from .response_parser import parse_llm_response, apply_changes_to_project
from utils.logger import log
from utils.helpers import clean_git_conflict_markers, generate_unified_diff

# A simple syntax highlighter for the diff view
from app_core.highlighters.python_syntax_highlighter import PythonSyntaxHighlighter

class DiffViewer(QTextEdit):
    """A simple QTextEdit subclass for displaying unified diffs."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setReadOnly(True)
        self.setFont(QFont("Consolas", 10))
        self.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)

    def set_diff_text(self, diff_text: str):
        # Basic coloring for diffs
        html = ""
        for line in diff_text.splitlines():
            line_html = line.replace("&", "&").replace("<", "<").replace(">", ">")
            if line.startswith('+'):
                html += f'<span style="color: #a7c080;">{line_html}</span><br>'
            elif line.startswith('-'):
                html += f'<span style="color: #e67e80;">{line_html}</span><br>'
            elif line.startswith('@@'):
                html += f'<span style="color: #83c092;">{line_html}</span><br>'
            else:
                html += f'<span>{line_html}</span><br>'
        self.setHtml(f"<pre>{html}</pre>")

class AIPatcherDialog(QDialog):
    """A dialog to generate patch prompts and apply AI-generated code changes."""

    def __init__(self, puffin_api: PuffinPluginAPI, parent=None):
        super().__init__(parent)
        self.api = puffin_api
        self.project_manager = self.api.get_manager("project")
        self.project_root = self.project_manager.get_active_project_path()
        self.parsed_changes: Dict[str, str] = {}
        self.is_updating_checks = False

        self.setWindowTitle("AI Patcher")
        self.setMinimumSize(950, 700)
        self._setup_ui()
        self._connect_signals()
        self._go_to_step(0)

    def _setup_ui(self):
        self.main_layout = QVBoxLayout(self)
        self.stacked_widget = QStackedWidget()
        self.stacked_widget.addWidget(self._create_step1_setup_page())
        self.stacked_widget.addWidget(self._create_step2_review_page())
        self.stacked_widget.addWidget(self._create_step3_complete_page())
        self.main_layout.addWidget(self.stacked_widget, 1)

        self.button_layout = QHBoxLayout()
        self.back_button = QPushButton("Back")
        self.next_button = QPushButton("Next")
        self.apply_button = QPushButton("Apply Patch")
        self.close_button = QPushButton("Close")
        self.copy_button = QPushButton("Copy Prompt")

        self.button_layout.addWidget(self.back_button)
        self.button_layout.addStretch()
        self.button_layout.addWidget(self.copy_button)
        self.button_layout.addWidget(self.next_button)
        self.button_layout.addWidget(self.apply_button)
        self.button_layout.addWidget(self.close_button)
        self.main_layout.addLayout(self.button_layout)

    def _connect_signals(self):
        self.back_button.clicked.connect(self._go_back)
        self.next_button.clicked.connect(self._go_next)
        self.apply_button.clicked.connect(self._apply_patch)
        self.close_button.clicked.connect(self.reject)
        self.copy_button.clicked.connect(self._copy_prompt_to_clipboard)

    def _go_to_step(self, index: int):
        self.stacked_widget.setCurrentIndex(index)
        self.back_button.setVisible(index > 0)
        self.next_button.setVisible(index < 2)
        self.apply_button.setVisible(index == 1)
        self.copy_button.setVisible(index == 0)
        
        if index == 0:
            self.setWindowTitle("AI Patcher - Step 1: Generate Prompt")
            self._populate_file_tree()
            self.next_button.setText("Generate & Continue")
        elif index == 1:
            self.setWindowTitle("AI Patcher - Step 2: Review and Apply Patch")
            self.next_button.setText("Finish")
            if not self.parsed_changes: self._parse_and_load_review()
        elif index == 2:
            self.setWindowTitle("AI Patcher - Complete")
            self._setup_completion_page()

    def _go_next(self):
        current_index = self.stacked_widget.currentIndex()
        if current_index == 0:
            self._generate_prompt()
            self._go_to_step(1)
        else:
            self._go_to_step(current_index + 1)
    
    def _go_back(self):
        self._go_to_step(self.stacked_widget.currentIndex() - 1)

    def _create_step1_setup_page(self) -> QWidget:
        page = QWidget()
        page_layout = QHBoxLayout(page)
        splitter = QSplitter(Qt.Orientation.Horizontal)
        page_layout.addWidget(splitter)
        
        # Left Pane: File Selection
        left_pane = QGroupBox("Select Files to Include")
        left_layout = QVBoxLayout(left_pane)
        file_actions_layout = QHBoxLayout()
        self.expand_all_button = QToolButton(icon=qta.icon('fa5s.angle-double-down'), toolTip="Expand All")
        self.collapse_all_button = QToolButton(icon=qta.icon('fa5s.angle-double-up'), toolTip="Collapse All")
        self.toggle_select_button = QToolButton(autoRaise=True)
        file_actions_layout.addWidget(self.expand_all_button)
        file_actions_layout.addWidget(self.collapse_all_button)
        file_actions_layout.addStretch()
        file_actions_layout.addWidget(self.toggle_select_button)
        left_layout.addLayout(file_actions_layout)
        self.file_tree = QTreeView()
        self.file_tree.setHeaderHidden(True)
        self.file_model = QStandardItemModel()
        self.file_tree.setModel(self.file_model)
        left_layout.addWidget(self.file_tree)
        splitter.addWidget(left_pane)

        # Right Pane: Prompt and Context
        right_pane = QWidget()
        right_layout = QVBoxLayout(right_pane)
        self.prompt_edit = QTextEdit()
        self.prompt_edit.setPlaceholderText("Enter the main goal for the AI, e.g., 'Refactor this class to be more efficient' or 'Fix the bug described in this changelog...'")
        right_layout.addWidget(QLabel("<b>Main Instructions for AI:</b>"))
        right_layout.addWidget(self.prompt_edit, 1)
        splitter.addWidget(right_pane)

        splitter.setSizes([350, 600])

        self.expand_all_button.clicked.connect(self.file_tree.expandAll)
        self.collapse_all_button.clicked.connect(self.file_tree.collapseAll)
        self.file_model.itemChanged.connect(self._on_item_changed)
        self.toggle_select_button.clicked.connect(self._on_toggle_select_clicked)
        return page

    def _create_step2_review_page(self) -> QWidget:
        page = QWidget()
        page_layout = QVBoxLayout(page)
        self.response_edit = QTextEdit()
        self.response_edit.setPlaceholderText("Paste the full markdown response from the AI here, then click 'Load Patch' to see the changes.")
        self.response_edit.setFontFamily("Consolas")
        load_button = QPushButton("Load Patch from Text")
        load_button.clicked.connect(self._parse_and_load_review)
        
        page_layout.addWidget(QLabel("<b>AI Response:</b>"))
        page_layout.addWidget(self.response_edit, 1)
        page_layout.addWidget(load_button, 0, Qt.AlignmentFlag.AlignRight)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Changed files list
        changes_group = QGroupBox("Detected Changes")
        changes_layout = QVBoxLayout(changes_group)
        self.changes_list = QListWidget()
        self.changes_list.itemChanged.connect(self._on_change_item_checked)
        self.changes_list.currentItemChanged.connect(self._display_diff)
        changes_layout.addWidget(self.changes_list)
        splitter.addWidget(changes_group)
        
        # Diff viewer
        diff_group = QGroupBox("Diff Preview")
        diff_layout = QVBoxLayout(diff_group)
        self.diff_viewer = DiffViewer()
        diff_layout.addWidget(self.diff_viewer)
        splitter.addWidget(diff_group)
        
        splitter.setSizes([300, 650])
        page_layout.addWidget(splitter, 2)
        return page

    def _create_step3_complete_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.completion_label = QLabel()
        self.completion_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        font = QFont(); font.setPointSize(14)
        self.completion_label.setFont(font)
        
        actions_group = QGroupBox("Next Steps")
        actions_layout = QHBoxLayout(actions_group)
        self.linter_button = QPushButton(qta.icon('mdi.bug-check-outline'), "Run Linter on Changed Files")
        self.source_control_button = QPushButton(qta.icon('mdi.git'), "Open Source Control")
        
        actions_layout.addWidget(self.linter_button)
        actions_layout.addWidget(self.source_control_button)

        layout.addStretch(1)
        layout.addWidget(self.completion_label)
        layout.addWidget(actions_group)
        layout.addStretch(2)

        self.linter_button.clicked.connect(self._run_linter)
        self.source_control_button.clicked.connect(self._open_source_control)
        return page

    def _setup_completion_page(self):
        applied_files = [self.changes_list.item(i).data(Qt.ItemDataRole.UserRole)['path'] for i in range(self.changes_list.count()) if self.changes_list.item(i).checkState() == Qt.CheckState.Checked]
        count = len(applied_files)
        self.completion_label.setText(f"Successfully applied changes to {count} file(s).")
        self.linter_button.setEnabled(count > 0)

    def _run_linter(self):
        linter = self.api.get_manager("linter")
        linter.lint_project(self.project_root)
        self.api.show_status_message("Project-wide linting started...", 3000)
        self.accept()

    def _open_source_control(self):
        if sc_panel := self.api.get_main_window().source_control_panel:
            if dock := sc_panel.parentWidget():
                if isinstance(dock.parentWidget(), QStackedWidget): # It's in the bottom tab bar
                    dock.parentWidget().setCurrentWidget(dock)
                dock.show()
                dock.raise_()
        self.accept()

    def _generate_prompt(self):
        selected_files = self._get_checked_files()
        if not selected_files:
            QMessageBox.warning(self, "No Files Selected", "Please select at least one file to include.")
            return

        instructions = self.prompt_edit.toPlainText().strip()
        if not instructions:
            QMessageBox.warning(self, "Instructions Missing", "Please provide instructions for the AI.")
            return
            
        project_name = os.path.basename(self.project_root)
        file_tree_text = "\n".join(self.project_manager.generate_file_tree_from_list(self.project_root, selected_files))
        
        prompt_parts = [
            f"# Project Patch Request: {project_name}", "---",
            "## AI Instructions", "```text", instructions, "```",
            "## Golden Rules", "```text", 
            "1. Your response MUST ONLY contain the complete, updated content for each file that needs to change.",
            "2. Enclose each file's content in the standard `### File: /path/to/file.ext` and code block format.",
            "3. Do not add any extra commentary, explanations, or summaries outside of the code blocks.",
            "```", "---",
            "## Project Files", f"```\n/{project_name}\n{file_tree_text}\n```", "---"
        ]
        
        for file_path in sorted(selected_files):
            relative_path = os.path.relpath(file_path, self.project_root).replace(os.sep, '/')
            lang = os.path.splitext(file_path)[1].lstrip('.') or 'text'
            prompt_parts.append(f"### File: `/{relative_path}`\n```{lang}")
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                cleaned_content = clean_git_conflict_markers(content)
                prompt_parts.append(cleaned_content)
            except Exception as e:
                prompt_parts.append(f"[Error reading file: {e}]")
            prompt_parts.append("```")

        self.generated_prompt = "\n".join(prompt_parts)

    def _copy_prompt_to_clipboard(self):
        self._generate_prompt()
        QApplication.clipboard().setText(self.generated_prompt)
        self.api.show_status_message("Prompt copied to clipboard!", 3000)

    def _parse_and_load_review(self):
        self.parsed_changes = parse_llm_response(self.response_edit.toPlainText())
        self.changes_list.clear()
        self.diff_viewer.clear()

        if not self.parsed_changes:
            QMessageBox.information(self, "No Changes Found", "Could not find any valid file blocks in the response text.")
            return
        
        for rel_path, new_content in sorted(self.parsed_changes.items()):
            item = QListWidgetItem(rel_path.lstrip('/'))
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            item.setCheckState(Qt.CheckState.Checked)
            item.setData(Qt.ItemDataRole.UserRole, {'path': rel_path, 'content': new_content})
            self.changes_list.addItem(item)
        
        if self.changes_list.count() > 0:
            self.changes_list.setCurrentRow(0)

    def _display_diff(self, current: QListWidgetItem, _):
        if not current:
            self.diff_viewer.clear()
            return
            
        data = current.data(Qt.ItemDataRole.UserRole)
        rel_path = data['path']
        new_content = data['content']
        abs_path = os.path.join(self.project_root, rel_path.lstrip('/'))

        original_content = ""
        if os.path.exists(abs_path):
            try:
                with open(abs_path, 'r', encoding='utf-8') as f:
                    original_content = f.read()
            except IOError as e:
                self.diff_viewer.setPlainText(f"Error reading original file: {e}")
                return
        
        diff_text = generate_unified_diff(original_content, new_content, fromfile=f"a{rel_path}", tofile=f"b{rel_path}")
        self.diff_viewer.set_diff_text(diff_text)
    
    def _on_change_item_checked(self, item: QListWidgetItem):
        is_anything_checked = False
        for i in range(self.changes_list.count()):
            if self.changes_list.item(i).checkState() == Qt.CheckState.Checked:
                is_anything_checked = True
                break
        self.apply_button.setEnabled(is_anything_checked)

    def _apply_patch(self):
        changes_to_apply = {}
        for i in range(self.changes_list.count()):
            item = self.changes_list.item(i)
            if item.checkState() == Qt.CheckState.Checked:
                data = item.data(Qt.ItemDataRole.UserRole)
                changes_to_apply[data['path']] = data['content']
        
        if not changes_to_apply:
            QMessageBox.warning(self, "No Changes Selected", "Please check the files you wish to apply changes to.")
            return

        success, message = apply_changes_to_project(self.project_root, changes_to_apply)
        if success:
            QMessageBox.information(self, "Patch Applied", message)
            if explorer := self.api.get_main_window().explorer_panel:
                explorer.refresh()
            self._go_to_step(2)
        else:
            QMessageBox.critical(self, "Patch Failed", message)

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
                dir_item = QStandardItem(dirname); dir_item.setIcon(qta.icon('fa5.folder')); dir_item.setCheckable(True)
                path = os.path.join(dirpath, dirname); dir_item.setData(path, Qt.ItemDataRole.UserRole)
                parent_node.appendRow(dir_item); path_map[path] = dir_item
            for filename in sorted(filenames):
                file_item = QStandardItem(filename); file_item.setIcon(qta.icon('fa5.file-alt')); file_item.setCheckable(True)
                path = os.path.join(dirpath, filename); file_item.setData(path, Qt.ItemDataRole.UserRole)
                parent_node.appendRow(file_item)
        self.file_tree.expandToDepth(0)
        self._set_all_check_states(Qt.CheckState.Unchecked)

    def _set_all_check_states(self, state: Qt.CheckState):
        self.is_updating_checks = True
        root = self.file_model.invisibleRootItem()
        for row in range(root.rowCount()): self._recursive_set_check_state(root.child(row), state)
        self.is_updating_checks = False
        self._update_toggle_button_state()

    def _recursive_set_check_state(self, item, state):
        if item.isCheckable(): item.setCheckState(state)
        for row in range(item.rowCount()):
            if child_item := item.child(row): self._recursive_set_check_state(child_item, state)

    def _on_toggle_select_clicked(self):
        if self._are_all_items_checked(): self._set_all_check_states(Qt.CheckState.Unchecked)
        else: self._set_all_check_states(Qt.CheckState.Checked)

    def _update_toggle_button_state(self):
        all_checked = self._are_all_items_checked()
        icon_name = 'fa5s.check-square' if all_checked else 'fa5.square'
        tooltip = "Deselect all files" if all_checked else "Select all files"
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
        if self.is_updating_checks: return
        self.is_updating_checks = True
        state = item.checkState()
        if state != Qt.CheckState.PartiallyChecked: self._update_descendant_states(item, state)
        if item.parent(): self._update_ancestor_states(item.parent())
        self.is_updating_checks = False
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
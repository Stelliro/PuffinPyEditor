# /plugins/ai_patcher/patcher_dialog.py
import os
import re
from typing import Dict, List, Optional
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QWidget, QSplitter,
    QTextEdit, QPushButton, QMessageBox, QFrame, QLabel, QListWidget,
    QTreeView, QToolButton, QInputDialog, QSpinBox, QCheckBox,
    QGroupBox, QFormLayout, QLineEdit, QStackedWidget,
    QDialogButtonBox, QListWidgetItem, QApplication, QDockWidget, QMenu
)
from PyQt6.QtGui import QStandardItemModel, QStandardItem, QFont, QCursor, QCloseEvent
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
        self.generated_prompt = ""

        self.setWindowTitle("AI Patcher")
        self.setMinimumSize(1200, 800)
        self.setWindowModality(Qt.WindowModality.NonModal)
        self._setup_ui()
        self._connect_signals()
        self._populate_file_tree()

    def _setup_ui(self):
        self.main_layout = QVBoxLayout(self)
        self.stacked_widget = QStackedWidget()
        self.main_layout.addWidget(self.stacked_widget)
        
        self.stacked_widget.addWidget(self._create_main_split_view())
        self.stacked_widget.addWidget(self._create_completion_page())

        self.button_layout = QHBoxLayout()
        self.copy_prompt_button = QPushButton(qta.icon('fa5s.copy'), "Generate Copy Prompt")
        self.apply_button = QPushButton(qta.icon('fa5s.check'), "Apply Patch")
        self.close_button = QPushButton("Close")
        
        self.button_layout.addWidget(self.copy_prompt_button)
        self.button_layout.addStretch()
        self.button_layout.addWidget(self.apply_button)
        self.button_layout.addWidget(self.close_button)
        self.main_layout.addLayout(self.button_layout)
        
        self.apply_button.setEnabled(False) 

    def _create_main_split_view(self) -> QWidget:
        main_widget = QWidget()
        main_layout = QHBoxLayout(main_widget)
        main_splitter = QSplitter(Qt.Orientation.Horizontal)
        main_layout.addWidget(main_splitter)

        left_pane_widget = QWidget()
        left_pane_layout = QVBoxLayout(left_pane_widget)
        
        instructions_group = QGroupBox("1. AI Instructions & Context")
        instructions_layout = QVBoxLayout(instructions_group)
        self.prompt_edit = QTextEdit()
        self.prompt_edit.setPlaceholderText("Enter the main goal for the AI, e.g., 'Refactor this class...'")
        instructions_layout.addWidget(self.prompt_edit)
        left_pane_layout.addWidget(instructions_group, 1)

        files_group = QGroupBox("2. Select Files to Include")
        files_layout = QVBoxLayout(files_group)
        file_actions_layout = QHBoxLayout()
        self.expand_all_button = QToolButton(icon=qta.icon('fa5s.angle-double-down'), toolTip="Expand All")
        self.collapse_all_button = QToolButton(icon=qta.icon('fa5s.angle-double-up'), toolTip="Collapse All")
        self.toggle_select_button = QToolButton(autoRaise=True)
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
        left_pane_layout.addWidget(files_group, 2)
        main_splitter.addWidget(left_pane_widget)

        right_pane_widget = QWidget()
        right_pane_layout = QVBoxLayout(right_pane_widget)
        
        response_group = QGroupBox("3. Paste AI Response")
        response_layout = QVBoxLayout(response_group)
        self.response_edit = QTextEdit()
        self.response_edit.setPlaceholderText("Paste the full markdown response from the AI here.")
        self.response_edit.setFontFamily("Consolas")
        load_button = QPushButton(qta.icon('fa5s.download'), "Load Patch from Text")
        load_button.clicked.connect(self._parse_and_load_review)
        response_layout.addWidget(self.response_edit, 1)
        response_layout.addWidget(load_button, 0, Qt.AlignmentFlag.AlignRight)
        right_pane_layout.addWidget(response_group, 1)

        review_splitter = QSplitter(Qt.Orientation.Horizontal)
        
        changes_group = QGroupBox("Detected Changes")
        changes_layout = QVBoxLayout(changes_group)
        self.changes_list = QListWidget()
        self.changes_list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.changes_list.setStyleSheet("""
            QListWidget::item::indicator {
                width: 15px; height: 15px; border: 1px solid #999;
                border-radius: 4px; background-color: transparent; margin-right: 5px;
            }
            QListWidget::item::indicator:checked { background-color: #66aaff; border-color: #5599ee; }
            QListWidget::item::indicator:disabled { border-color: #666; background-color: #444; }
        """)
        changes_layout.addWidget(self.changes_list)
        review_splitter.addWidget(changes_group)
        
        diff_group = QGroupBox("Diff Preview")
        diff_layout = QVBoxLayout(diff_group)
        self.diff_viewer = DiffViewer()
        diff_layout.addWidget(self.diff_viewer)
        review_splitter.addWidget(diff_group)
        review_splitter.setSizes([250, 450])
        right_pane_layout.addWidget(review_splitter, 2)
        main_splitter.addWidget(right_pane_widget)
        
        main_splitter.setSizes([400, 800])
        return main_widget

    def _create_completion_page(self) -> QWidget:
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
        self.back_to_patcher_button = QPushButton("Back to Patcher")
        
        actions_layout.addWidget(self.linter_button)
        actions_layout.addWidget(self.source_control_button)
        actions_layout.addWidget(self.back_to_patcher_button)

        layout.addStretch(1)
        layout.addWidget(self.completion_label)
        layout.addWidget(actions_group)
        layout.addStretch(2)
        return page

    def _connect_signals(self):
        self.close_button.clicked.connect(self.hide)
        self.apply_button.clicked.connect(self._apply_patch)
        self.copy_prompt_button.clicked.connect(self._copy_prompt_to_clipboard)
        
        self.file_model.itemChanged.connect(self._on_item_changed)
        self.expand_all_button.clicked.connect(self.file_tree.expandAll)
        self.collapse_all_button.clicked.connect(self.file_tree.collapseAll)
        self.toggle_select_button.clicked.connect(self._on_toggle_select_clicked)

        self.changes_list.itemChanged.connect(self._on_change_item_checked)
        self.changes_list.currentItemChanged.connect(self._display_diff)
        self.changes_list.customContextMenuRequested.connect(self._show_changes_list_context_menu)
        
        self.linter_button.clicked.connect(self._run_linter)
        self.source_control_button.clicked.connect(self._open_source_control)
        self.back_to_patcher_button.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(0))
        
    def _show_changes_list_context_menu(self, pos):
        item = self.changes_list.itemAt(pos)
        if not item: return
            
        data = item.data(Qt.ItemDataRole.UserRole)
        is_unspecified = data.get('unspecified', False)

        if is_unspecified:
            menu = QMenu()
            assign_action = menu.addAction(qta.icon('fa5s.file-signature'), "Assign File Path...")
            
            action = menu.exec(self.changes_list.mapToGlobal(pos))
            if action == assign_action: self._assign_path_to_item(item)
    
    def _assign_path_to_item(self, item: QListWidgetItem):
        current_data = item.data(Qt.ItemDataRole.UserRole)
        old_path = current_data['path']
        
        new_path, ok = QInputDialog.getText(self, "Assign File Path", "Enter relative path for this file:", text="/new_file.py")
        
        if ok and new_path:
            new_path = new_path.replace("\\", "/").lstrip("/")
            if not new_path:
                QMessageBox.warning(self, "Invalid Path", "File path cannot be empty.")
                return

            content = self.parsed_changes.pop(old_path, "")
            final_path_key = f"/{new_path}"
            self.parsed_changes[final_path_key] = content

            font = item.font(); font.setItalic(False); item.setFont(font)
            item.setText(new_path)
            item.setIcon(qta.icon('fa5s.file-medical'))
            current_data['path'] = final_path_key
            current_data['unspecified'] = False
            item.setData(Qt.ItemDataRole.UserRole, current_data)
            QTimer.singleShot(0, lambda: item.setCheckState(Qt.CheckState.Checked))

    def _setup_completion_page(self, applied_count):
        self.completion_label.setText(f"Successfully applied changes to {applied_count} file(s).")
        self.linter_button.setEnabled(applied_count > 0)
        self.stacked_widget.setCurrentIndex(1) 

    def _run_linter(self):
        linter = self.api.get_manager("linter")
        linter.lint_project(self.project_root)
        self.api.show_status_message("Project-wide linting started...", 3000)

    def _open_source_control(self):
        sc_panel = getattr(self.api.get_main_window(), 'source_control_panel', None)
        if sc_panel:
            bottom_tab_widget = getattr(self.api.get_main_window(), '_bottom_tab_widget', None)
            if bottom_tab_widget:
                for i in range(bottom_tab_widget.count()):
                    if bottom_tab_widget.widget(i) == sc_panel:
                        bottom_tab_widget.setCurrentIndex(i)
                        dock = sc_panel.parent()
                        while dock and not isinstance(dock, QDockWidget): dock = dock.parent()
                        if dock: dock.show(); dock.raise_()
                        break

    def _generate_prompt(self):
        selected_files = self._get_checked_files()
        instructions = self.prompt_edit.toPlainText().strip()
        if not instructions:
            QMessageBox.warning(self, "Missing Instructions", "Please provide instructions for the AI.")
            return False

        if not selected_files:
            reply = QMessageBox.question(self, "No Files Selected", "You have not selected any files. Continue generating a prompt with instructions only?",
                                         QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.No: return False

        project_name = os.path.basename(self.project_root)
        file_tree_text = "\n".join(self.project_manager.generate_file_tree_from_list(self.project_root, selected_files)) if selected_files else "No files were provided in context."
        
        prompt_parts = [
            f"# Project Patch Request: {project_name}", "---",
            "## AI Instructions", "```text", instructions, "```",
            "## Golden Rules", "```text", 
            "1. Your response MUST ONLY contain the complete, updated content for each file that needs to change.",
            "2. Enclose each file's content in the standard `### File: /path/to/file.ext` and code block format.",
            "3. Do not add any extra commentary, explanations, or summaries outside of the code blocks.",
            "```", "---", f"## Project File Tree:\n```\n{file_tree_text}\n```"
        ]
        
        if selected_files:
            prompt_parts.extend(["---", "## Project Files"])
            for file_path in sorted(selected_files):
                relative_path = os.path.relpath(file_path, self.project_root).replace(os.sep, '/')
                lang = os.path.splitext(file_path)[1].lstrip('.') or 'text'
                prompt_parts.append(f"### File: `/{relative_path}`\n```{lang}")
                try:
                    with open(file_path, 'r', encoding='utf-8') as f: content = f.read()
                    prompt_parts.append(clean_git_conflict_markers(content))
                except Exception as e:
                    prompt_parts.append(f"[Error reading file: {e}]")
                prompt_parts.append("```")

        self.generated_prompt = "\n\n".join(prompt_parts)
        return True

    def _copy_prompt_to_clipboard(self):
        if self._generate_prompt():
            QApplication.clipboard().setText(self.generated_prompt)
            self.api.show_status_message("Prompt copied to clipboard!", 3000)

    def _parse_and_load_review(self):
        self.parsed_changes = parse_llm_response(self.response_edit.toPlainText())
        self.changes_list.clear()
        self.diff_viewer.clear()

        if not self.parsed_changes:
            QMessageBox.information(self, "No Changes Found", "Could not find any valid file blocks in the response text.")
            self.apply_button.setEnabled(False)
            return
        
        is_any_change_applicable = False
        for rel_path, new_content in sorted(self.parsed_changes.items()):
            if not rel_path or not rel_path.strip():
                log.warning(f"AI Patcher: Ignored empty file path from response.")
                continue

            item = QListWidgetItem()
            is_unspecified = rel_path.startswith('[UNSPECIFIED_FILE_')
            
            data = {'path': rel_path, 'content': new_content, 'unspecified': is_unspecified}
            item.setData(Qt.ItemDataRole.UserRole, data)
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            
            if is_unspecified:
                item.setText(rel_path)
                font = item.font(); font.setItalic(True); item.setFont(font)
                item.setIcon(qta.icon('fa5s.question-circle', color='orange'))
                item.setCheckState(Qt.CheckState.Unchecked) 
            else:
                item.setText(rel_path.lstrip('/\\'))
                item.setCheckState(Qt.CheckState.Checked)
                is_any_change_applicable = True

            self.changes_list.addItem(item)
        
        if self.changes_list.count() > 0:
            self.changes_list.setCurrentRow(0)
        
        self.apply_button.setEnabled(is_any_change_applicable)

    def _display_diff(self, current: QListWidgetItem, _):
        self.diff_viewer.clear()
        if not current: return
            
        data = current.data(Qt.ItemDataRole.UserRole)
        rel_path = data['path']
        is_unspecified = data.get('unspecified', False)
        
        new_content = data['content']
        abs_path = os.path.join(self.project_root, rel_path.lstrip('/\\')) if not is_unspecified else ""

        original_content = ""
        is_new_file = is_unspecified or not os.path.exists(abs_path)
        
        if is_new_file:
            self.diff_viewer.setToolTip("This change will create a new file.")
        elif os.path.isdir(abs_path):
            self.diff_viewer.setPlainText(f"Error: Path '{rel_path}' refers to a directory.")
            return
        else:
            try:
                with open(abs_path, 'r', encoding='utf-8', errors='ignore') as f:
                    original_content = f.read()
                self.diff_viewer.setToolTip(f"Showing changes for:\n{abs_path}")
            except IOError as e:
                self.diff_viewer.setPlainText(f"Error reading original file:\n{e}")
                return
        
        fromfile = f"a{rel_path}" if not is_new_file else "/dev/null"
        tofile = f"b{rel_path}"
        
        diff_text = generate_unified_diff(original_content, new_content, fromfile=fromfile, tofile=tofile)
        self.diff_viewer.set_diff_text(diff_text)
    
    def _on_change_item_checked(self, item: QListWidgetItem):
        is_anything_checked = False
        data = item.data(Qt.ItemDataRole.UserRole)

        if data.get('unspecified', False) and item.checkState() == Qt.CheckState.Checked:
            QTimer.singleShot(0, lambda: item.setCheckState(Qt.CheckState.Unchecked))
            QMessageBox.information(self, "Path Required", "You must right-click and assign a file path before including this change.")
        
        for i in range(self.changes_list.count()):
            list_item = self.changes_list.item(i)
            if not list_item.data(Qt.ItemDataRole.UserRole).get('unspecified') and list_item.checkState() == Qt.CheckState.Checked:
                is_anything_checked = True
                break
        self.apply_button.setEnabled(is_anything_checked)

    def _apply_patch(self):
        changes_to_apply = {}
        applied_count = 0

        for i in range(self.changes_list.count()):
            item = self.changes_list.item(i)
            if item.checkState() == Qt.CheckState.Checked:
                data = item.data(Qt.ItemDataRole.UserRole)
                if not data.get('unspecified', False):
                    changes_to_apply[data['path']] = data['content']
                    applied_count += 1
        
        if not changes_to_apply:
            QMessageBox.warning(self, "No Changes Selected", "Please check the files you wish to apply changes to. Unspecified files must be assigned a path first.")
            return

        success, message = apply_changes_to_project(self.project_root, changes_to_apply)
        if success:
            if explorer := self.api.get_main_window().explorer_panel: explorer.refresh()
            self._setup_completion_page(applied_count)
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
        items = self._get_all_checkable_items()
        return bool(items) and all(item.checkState() == Qt.CheckState.Checked for item in items)

    def _get_all_checkable_items(self) -> List[QStandardItem]:
        items = []; root = self.file_model.invisibleRootItem()
        def recurse(parent):
            for r in range(parent.rowCount()):
                child = parent.child(r)
                if child and child.isCheckable():
                    items.append(child)
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
        if not parent or not hasattr(parent, 'checkState'): return
        states = [parent.child(r).checkState() for r in range(parent.rowCount()) if parent.child(r)]
        if not states: return
        
        if all(s == Qt.CheckState.Checked for s in states):
            new_state = Qt.CheckState.Checked
        elif all(s == Qt.CheckState.Unchecked for s in states):
            new_state = Qt.CheckState.Unchecked
        else:
            new_state = Qt.CheckState.PartiallyChecked
            
        if parent.isCheckable() and parent.checkState() != new_state:
            parent.setCheckState(new_state)

    def _get_checked_files(self) -> List[str]:
        files = []; root = self.file_model.invisibleRootItem()
        def recurse(parent):
            if parent.checkState() == Qt.CheckState.Unchecked: return
            if parent.isCheckable():
                path = parent.data(Qt.ItemDataRole.UserRole)
                if path and os.path.isfile(path) and parent.checkState() == Qt.CheckState.Checked: 
                    files.append(path)
                if parent.hasChildren():
                    for r in range(parent.rowCount()):
                        if child := parent.child(r): recurse(child)
        for r in range(root.rowCount()): recurse(root.child(r))
        return list(sorted(set(files)))

    def closeEvent(self, event: QCloseEvent):
        """Override close event to hide the dialog instead of deleting it."""
        self.hide()
        event.ignore()
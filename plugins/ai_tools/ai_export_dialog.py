# PuffinPyEditor/plugins/ai_tools/ai_export_dialog.py
import os
import sys
import json
import importlib.util
from typing import List, Dict, Optional, Any, Tuple
from datetime import datetime
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QSplitter, QWidget, QGroupBox,
    QTreeView, QTextEdit, QPushButton, QDialogButtonBox, QMessageBox,
    QComboBox, QProgressDialog, QApplication, QCheckBox, QLabel, QToolButton
)
from PyQt6.QtGui import QStandardItemModel, QStandardItem, QCursor
from PyQt6.QtCore import Qt, QCoreApplication

import qtawesome as qta

from app_core.puffin_api import PuffinPluginAPI
from app_core.settings_manager import settings_manager
from app_core.project_manager import ProjectManager
from app_core.linter_manager import LinterManager
from app_core import golden_rules
from utils.logger import log
from utils.helpers import get_base_path
from .api_client import ApiClient
from .ai_response_dialog import AIResponseDialog
from .persona_manager_dialog import PersonaManagerDialog
from .style_preset_manager import StylePresetManager
from .persona_logic import get_files_for_persona


class AIExportDialog(QDialog):
    """
    A dialog for selecting an AI Persona and exporting a project's context.
    """

    def __init__(self, project_path: str, puffin_api: PuffinPluginAPI, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.api = puffin_api
        self.project_path = project_path
        self.project_manager = self.api.get_manager("project")
        self.linter_manager = self.api.get_manager("linter")
        self.api_client = ApiClient(settings_manager)
        self.preset_manager = StylePresetManager()

        self.personas: Dict[str, Dict] = {}
        self.persona_modules: Dict[str, Any] = {}

        self.selected_files: List[str] = []
        self._is_updating_checks = False

        self.setWindowTitle("AI Task Manager")
        self.setMinimumSize(950, 700)
        self.setObjectName("AIExportDialog")

        self._setup_ui()
        self._connect_signals()
        self._populate_file_tree()
        self._load_and_populate_personas()
        self._populate_style_presets()

    def _setup_ui(self):
        self.main_layout = QVBoxLayout(self)
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        self.main_layout.addWidget(self.splitter, 1)
        self._create_left_pane()
        self._create_right_pane()
        self.splitter.setSizes([350, 600])

        bottom_options_layout = QHBoxLayout()
        api_context_group = QGroupBox("Execution & Context")
        api_context_layout = QVBoxLayout(api_context_group)
        api_mode_layout = QHBoxLayout()
        self.api_mode_checkbox = QCheckBox("Enable API Mode")
        self.api_mode_checkbox.setToolTip("Send context directly to an AI API instead of exporting a file.")
        api_mode_layout.addWidget(self.api_mode_checkbox)
        api_mode_layout.addStretch()
        api_context_layout.addLayout(api_mode_layout)

        self.api_controls_widget = QWidget()
        api_controls_layout = QHBoxLayout(self.api_controls_widget)
        api_controls_layout.setContentsMargins(0, 5, 0, 0)
        api_controls_layout.addWidget(QLabel("Provider:"))
        self.api_provider_combo = QComboBox()
        api_controls_layout.addWidget(self.api_provider_combo)
        api_controls_layout.addWidget(QLabel("Model:"))
        self.api_model_combo = QComboBox()
        api_controls_layout.addWidget(self.api_model_combo)
        api_context_layout.addWidget(self.api_controls_widget)

        self.include_linter_checkbox = QCheckBox("Include linter issues")
        self.include_linter_checkbox.setChecked(True)
        self.include_linter_checkbox.setToolTip("Include linter analysis in the context.")
        api_context_layout.addWidget(self.include_linter_checkbox)
        api_context_layout.addStretch()
        bottom_options_layout.addWidget(api_context_group)

        self.export_options_group = QGroupBox("File Export Options")
        export_layout = QVBoxLayout(self.export_options_group)
        format_layout = QHBoxLayout()
        format_layout.addWidget(QLabel("Format:"))
        self.format_combo = QComboBox()
        self.format_combo.addItems(["AI-Optimized", "Standard Markdown"])
        self.format_combo.setToolTip("Choose export format. 'AI-Optimized' is cleaner for models.")
        format_layout.addWidget(self.format_combo)
        export_layout.addLayout(format_layout)
        export_layout.addStretch()
        bottom_options_layout.addWidget(self.export_options_group)

        self.main_layout.addLayout(bottom_options_layout)
        self.button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        self.ok_button = self.button_box.button(QDialogButtonBox.StandardButton.Ok)
        self.main_layout.addWidget(self.button_box)
        self._init_providers_and_models()
        self._toggle_api_mode(self.api_mode_checkbox.isChecked())

    def _create_left_pane(self):
        left_pane = QWidget()
        layout = QVBoxLayout(left_pane)
        self.splitter.addWidget(left_pane)

        persona_group = QGroupBox("1. Select AI Persona (Optional)")
        persona_layout = QVBoxLayout(persona_group)
        persona_selection_layout = QHBoxLayout()
        self.persona_combo = QComboBox()
        persona_selection_layout.addWidget(self.persona_combo, 1)
        self.manage_personas_button = QPushButton("Manage...")
        self.manage_personas_button.setIcon(qta.icon('fa5s.cog'))
        self.manage_personas_button.setToolTip("Create, edit, or delete AI Personas")
        persona_selection_layout.addWidget(self.manage_personas_button)
        persona_layout.addLayout(persona_selection_layout)
        self.persona_desc_label = QLabel("<i>Select a persona to see their expertise.</i>")
        self.persona_desc_label.setWordWrap(True)
        persona_layout.addWidget(self.persona_desc_label)
        layout.addWidget(persona_group)

        files_group = QGroupBox("2. Select Files to Include")
        files_layout = QVBoxLayout(files_group)
        actions_layout = QHBoxLayout()
        self.expand_all_button = QToolButton(icon=qta.icon('fa5s.angle-double-down', color='grey'), toolTip="Expand all folders.")
        self.collapse_all_button = QToolButton(icon=qta.icon('fa5s.angle-double-up', color='grey'), toolTip="Collapse all folders.")
        self.toggle_select_button = QToolButton()
        for button in [self.expand_all_button, self.collapse_all_button, self.toggle_select_button]:
            button.setAutoRaise(True)
        actions_layout.addWidget(self.expand_all_button)
        actions_layout.addWidget(self.collapse_all_button)
        actions_layout.addStretch()
        actions_layout.addWidget(self.toggle_select_button)
        files_layout.addLayout(actions_layout)
        self.file_tree = QTreeView()
        self.file_tree.setHeaderHidden(True)
        self.file_model = QStandardItemModel()
        self.file_tree.setModel(self.file_model)
        files_layout.addWidget(self.file_tree)
        layout.addWidget(files_group, 1)

    def _create_right_pane(self):
        right_pane = QWidget()
        layout = QVBoxLayout(right_pane)
        self.splitter.addWidget(right_pane)

        goal_group = QGroupBox("3. Define Primary Goal (Optional)")
        goal_layout = QVBoxLayout(goal_group)
        self.user_goal_edit = QTextEdit()
        self.user_goal_edit.setPlaceholderText(
            "Leave blank for a general review based on the selected persona's expertise. Or, provide a specific goal, e.g., 'Refactor the database logic in file_handler.py' or 'Add a new endpoint to fetch user profiles'.")
        goal_layout.addWidget(self.user_goal_edit, 1)
        layout.addWidget(goal_group, 1)

        rules_group = QGroupBox("4. Select Style Preset")
        rules_layout = QVBoxLayout(rules_group)
        self.rules_combo = QComboBox()
        self.rules_combo.setToolTip("Select a set of stylistic rules for the AI.")
        rules_layout.addWidget(self.rules_combo)
        layout.addWidget(rules_group)

        layout.addStretch(1)

    def _connect_signals(self):
        self.button_box.accepted.connect(self._start_export)
        self.button_box.rejected.connect(self.reject)
        self.file_model.itemChanged.connect(self._on_item_changed)
        self.expand_all_button.clicked.connect(self.file_tree.expandAll)
        self.collapse_all_button.clicked.connect(self.file_tree.collapseAll)
        self.toggle_select_button.clicked.connect(self._on_toggle_select_clicked)
        self.persona_combo.currentIndexChanged.connect(self._on_persona_selected)
        self.api_mode_checkbox.toggled.connect(self._toggle_api_mode)
        self.api_provider_combo.currentIndexChanged.connect(self._on_api_provider_changed)
        self.manage_personas_button.clicked.connect(self._open_persona_manager)

    def _init_providers_and_models(self):
        self.api_provider_combo.addItems(self.api_client.PROVIDER_CONFIG.keys())
        self._on_api_provider_changed()

    def _open_persona_manager(self):
        manager_dialog = PersonaManagerDialog(self.api.get_manager("theme"), self)
        manager_dialog.finished.connect(self._load_and_populate_personas)
        manager_dialog.finished.connect(self._populate_style_presets)
        manager_dialog.exec()

    def _toggle_api_mode(self, checked: bool):
        self.api_controls_widget.setVisible(checked)
        self.export_options_group.setVisible(not checked)
        self.ok_button.setText("Send to AI" if checked else "Export")

    def _on_api_provider_changed(self):
        provider = self.api_provider_combo.currentText()
        models = self.api_client.PROVIDER_CONFIG.get(provider, {}).get("models", [])
        self.api_model_combo.clear()
        self.api_model_combo.addItems(models)

    def _set_all_check_states(self, state: Qt.CheckState):
        self._is_updating_checks = True
        root = self.file_model.invisibleRootItem()
        for i in range(root.rowCount()):
            self._recursive_set_state(root.child(i), state)
        self._is_updating_checks = False
        self._update_toggle_button_state()

    def _recursive_set_state(self, item: QStandardItem, state: Qt.CheckState):
        if item.isCheckable() and item.checkState() != state:
            item.setCheckState(state)
        for i in range(item.rowCount()):
            self._recursive_set_state(item.child(i), state)

    def _on_toggle_select_clicked(self):
        new_state = Qt.CheckState.Unchecked if self._are_all_items_checked() else Qt.CheckState.Checked
        self._set_all_check_states(new_state)

    def _on_item_changed(self, item: QStandardItem):
        if self._is_updating_checks: return
        self._is_updating_checks = True
        self._update_descendants(item)
        self._update_ancestors(item)
        self._is_updating_checks = False
        self._update_toggle_button_state()

    def _update_descendants(self, item: QStandardItem):
        state = item.checkState()
        if state == Qt.CheckState.PartiallyChecked: return
        for i in range(item.rowCount()):
            self._recursive_set_state(item.child(i), state)

    def _update_ancestors(self, item: QStandardItem):
        parent = item.parent()
        while parent:
            child_states = {parent.child(i).checkState() for i in range(parent.rowCount())}
            new_state = Qt.CheckState.Unchecked
            if all(s == Qt.CheckState.Checked for s in child_states):
                new_state = Qt.CheckState.Checked
            elif any(s != Qt.CheckState.Unchecked for s in child_states):
                new_state = Qt.CheckState.PartiallyChecked
            if parent.checkState() != new_state:
                parent.setCheckState(new_state)
            parent = parent.parent()

    def _get_all_checkable_items(self) -> List[QStandardItem]:
        items = []
        root = self.file_model.invisibleRootItem()
        stack = [root.child(i) for i in range(root.rowCount())]
        while stack:
            item = stack.pop()
            if item and item.isCheckable():
                items.append(item)
                stack.extend(item.child(i) for i in range(item.rowCount()))
        return items

    def _are_all_items_checked(self) -> bool:
        items = self._get_all_checkable_items()
        if not items: return False
        return all(item.checkState() == Qt.CheckState.Checked for item in items)

    def _update_toggle_button_state(self):
        if self._are_all_items_checked():
            self.toggle_select_button.setIcon(qta.icon('fa5s.check-square', color='grey'))
            self.toggle_select_button.setToolTip("Deselect all.")
        else:
            self.toggle_select_button.setIcon(qta.icon('fa5.square', color='grey'))
            self.toggle_select_button.setToolTip("Select all.")

    def _populate_file_tree(self):
        self.file_model.clear()
        root_node = self.file_model.invisibleRootItem()
        path_map = {self.project_path: root_node}
        ignore_dirs = {'__pycache__', '.git', 'venv', '.venv', 'dist', 'build', 'logs', 'ai_exports'}
        ignore_files = {'puffin_editor_settings.json'}
        include_extensions = ['.py', '.md', '.txt', '.json', '.html', '.css', '.js', '.yml', '.bat', '.qss']

        for dirpath, dirnames, filenames in os.walk(self.project_path, topdown=True):
            dirnames[:] = [d for d in dirnames if d not in ignore_dirs]
            parent_node = path_map.get(os.path.normpath(dirpath))
            if parent_node is None: continue

            for dirname in sorted(dirnames):
                dir_item = QStandardItem(dirname)
                dir_item.setIcon(qta.icon('fa5.folder', color='grey'))
                dir_item.setCheckable(True)
                path = os.path.join(dirpath, dirname)
                dir_item.setData(path, Qt.ItemDataRole.UserRole)
                parent_node.appendRow(dir_item)
                path_map[path] = dir_item

            for filename in sorted(filenames):
                if filename in ignore_files or not any(filename.lower().endswith(ext) for ext in include_extensions) and "LICENSE" not in filename:
                    continue
                file_item = QStandardItem(filename)
                file_item.setIcon(qta.icon('fa5.file-alt', color='grey'))
                file_item.setCheckable(True)
                path = os.path.join(dirpath, filename)
                file_item.setData(path, Qt.ItemDataRole.UserRole)
                parent_node.appendRow(file_item)

        self._set_all_check_states(Qt.CheckState.Checked)
        self.file_tree.collapseAll()

    def _get_checked_files(self) -> List[str]:
        files = []
        for item in self._get_all_checkable_items():
            if item.checkState() == Qt.CheckState.Checked:
                path = item.data(Qt.ItemDataRole.UserRole)
                if path and os.path.isfile(path):
                    files.append(path)
        return files

    def _load_and_populate_personas(self):
        current_selection_id = self.persona_combo.currentData()
        self.personas.clear(); self.persona_modules.clear(); self.persona_combo.clear()
        self.persona_combo.addItem("No Persona (General Review)", None)
        persona_dir = os.path.join(get_base_path(), "assets", "ai_personas")
        if not os.path.isdir(persona_dir):
            log.warning(f"AI Persona directory not found: {persona_dir}")
            return

        for filename in sorted(os.listdir(persona_dir)):
            if filename.endswith(".py") and not filename.startswith("__"):
                module_path = os.path.join(persona_dir, filename)
                module_name = f"assets.ai_personas.{os.path.splitext(filename)[0]}"
                try:
                    spec = importlib.util.spec_from_file_location(module_name, module_path)
                    if spec and spec.loader:
                        module = importlib.util.module_from_spec(spec)
                        if module_name in sys.modules:
                            del sys.modules[module_name]
                        sys.modules[module_name] = module
                        spec.loader.exec_module(module)
                        if hasattr(module, "get_persona_info"):
                            info = module.get_persona_info()
                            self.personas[info['id']] = info
                            self.persona_modules[info['id']] = module
                            self.persona_combo.addItem(f"{info['name']} - {info['title']}", info['id'])
                except Exception as e:
                    log.error(f"Failed to load AI persona '{filename}': {e}", exc_info=True)

        index_to_select = self.persona_combo.findData(current_selection_id)
        self.persona_combo.setCurrentIndex(index_to_select if index_to_select != -1 else 0)

    def _populate_style_presets(self):
        self.rules_combo.clear()
        self.preset_manager.presets = self.preset_manager.load_presets()
        for preset_id, preset_name in self.preset_manager.get_preset_names_for_ui():
            self.rules_combo.addItem(preset_name, preset_id)

    def _on_persona_selected(self, index: int):
        persona_id = self.persona_combo.itemData(index)

        if not persona_id:
            self.persona_desc_label.setText("<i>A general-purpose review will be performed using a standard prompt. All files are selected by default.</i>")
            self._set_all_check_states(Qt.CheckState.Checked)
            return

        if persona_info := self.personas.get(persona_id):
            self.persona_desc_label.setText(f"<b>Expertise:</b> {persona_info.get('expertise', 'N/A')}")

        files_to_select = get_files_for_persona(persona_id, self.project_path)
        if not files_to_select:
            self._set_all_check_states(Qt.CheckState.Checked)
            return

        self._set_all_check_states(Qt.CheckState.Unchecked)
        self._is_updating_checks = True
        for item in self._get_all_checkable_items():
            path = item.data(Qt.ItemDataRole.UserRole)
            if path in files_to_select:
                item.setCheckState(Qt.CheckState.Checked)
                self._update_ancestors(item)
        self._is_updating_checks = False
        self._update_toggle_button_state()

    def _build_prompt(self, user_goal: str, files: List[str], problems: Dict[str, List[Dict]]) -> Optional[Tuple[str, str]]:
        persona_id = self.persona_combo.currentData()
        style_preset_id = self.rules_combo.currentData()
        style_rules = []
        if style_preset_id and (preset := self.preset_manager.presets.get(style_preset_id)):
            style_rules = preset.get("rules", [])

        context = {
            "user_instructions": user_goal,
            "file_tree": self._generate_file_tree_text(files),
            "file_contents": {path: self._read_file(path) for path in files},
            "linter_results": problems,
            "project_root": self.project_path,
            "golden_rules": golden_rules.get_golden_rules_text().splitlines(),
            "style_rules": style_rules
        }

        if not persona_id:
            system_prompt = "You are a helpful and experienced software developer. Your goal is to perform a general code review based on the user's instructions and the provided files. Offer concrete suggestions for improvement."
            file_contents_section = []
            for path, content in context["file_contents"].items():
                relative_path = os.path.relpath(path, context["project_root"]).replace(os.sep, '/')
                lang = os.path.splitext(path)[1].lstrip('.') or 'text'
                file_contents_section.append(f"### File: `/{relative_path}`\n```{lang}\n{content}\n```")
            file_contents_str = "\n\n".join(file_contents_section)

            user_prompt = f"""
# Project Review Request

**User's Goal:**
{context.get("user_instructions") or "Perform a general review of the provided code."}

---
**Project File Tree:**
```
{context.get("file_tree", "No file tree provided.")}
```
---
**Files for Review:**
{file_contents_str}
"""
            return system_prompt.strip(), user_prompt.strip()

        if module := self.persona_modules.get(persona_id):
            try:
                persona_instance = module.get_persona_instance()
                return persona_instance.generate_prompt(context)
            except Exception as e:
                log.error(f"Error in prompt generation for '{persona_id}': {e}", exc_info=True)
                QMessageBox.critical(self, "Prompt Generation Error", f"Could not generate prompt: {e}")
                return None

        log.error(f"Could not load module for selected persona ID: {persona_id}")
        QMessageBox.critical(self, "Error", "The selected AI persona could not be loaded.")
        return None

    def _read_file(self, file_path: str) -> str:
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                return f.read()
        except Exception as e:
            return f"[Error reading file: {e}]"

    def _generate_file_tree_text(self, files: List[str]) -> str:
        tree, base_path = {}, self.project_path
        for f in files:
            rel_path = os.path.relpath(f, base_path).replace(os.sep, '/')
            parts, curr = rel_path.split('/'), tree
            for part in parts[:-1]: curr = curr.setdefault(part, {})
            curr[parts[-1]] = None

        def build_string(d, indent=''):
            s, items = '', sorted(d.items())
            for i, (key, val) in enumerate(items):
                is_last = i == len(items) - 1
                s += f"{indent}{'└── ' if is_last else '├── '}{key}\n"
                if val is not None: s += build_string(val, f"{indent}{'    ' if is_last else '│   '}")
            return s
        return f"/{os.path.basename(base_path)}\n{build_string(tree, ' ')}"

    def _start_export(self):
        self.ok_button.setEnabled(False)
        self.selected_files = self._get_checked_files()
        if not self.selected_files:
             QMessageBox.warning(self, "No Files Selected", "No files are checked. Please select at least one file.")
             self.ok_button.setEnabled(True)
             return

        self.progress = QProgressDialog("Linting selected files...", "Cancel", 0, 0, self)
        self.progress.setWindowModality(Qt.WindowModality.WindowModal)
        self.progress.show()
        QCoreApplication.processEvents()

        try: self.linter_manager.project_lint_results_ready.disconnect(self._on_lint_complete)
        except TypeError: pass
        self.linter_manager.project_lint_results_ready.connect(self._on_lint_complete)
        self.linter_manager.lint_project(self.project_path)

    def _on_lint_complete(self, all_problems: Dict[str, List[Dict]]):
        if self.progress.wasCanceled():
            self.ok_button.setEnabled(True)
            return

        self.progress.setLabelText("Preparing context...")
        QCoreApplication.processEvents()

        user_goal = self.user_goal_edit.toPlainText().strip()
        selected_problems = {k: v for k, v in all_problems.items() if self.include_linter_checkbox.isChecked() and k in self.selected_files}
        prompt_data = self._build_prompt(user_goal, self.selected_files, selected_problems)

        if not prompt_data:
            self.progress.close()
            self.ok_button.setEnabled(True)
            return

        system_prompt, user_prompt = prompt_data

        if self.api_mode_checkbox.isChecked():
            self.progress.setLabelText("Sending to AI...")
            self._handle_api_request(system_prompt, user_prompt)
        else:
            self.progress.setLabelText("Saving file...")
            self._handle_file_export(system_prompt, user_prompt)

        if not self.progress.wasCanceled():
            self.progress.close()

        self.ok_button.setEnabled(True)
        try:
            self.linter_manager.project_lint_results_ready.disconnect(self._on_lint_complete)
        except TypeError:
            pass # Already disconnected

    def _handle_api_request(self, system_prompt: str, user_prompt: str):
        QApplication.setOverrideCursor(QCursor(Qt.CursorShape.WaitCursor))
        try:
            provider, model = self.api_provider_combo.currentText(), self.api_model_combo.currentText()
            success, response = self.api_client.send_request(provider, model, system_prompt, user_prompt)
            if success:
                AIResponseDialog(response, self).exec()
                self.accept()
            else:
                QMessageBox.critical(self, "API Error", response)
        finally:
            QApplication.restoreOverrideCursor()

    def _handle_file_export(self, system_prompt: str, user_prompt: str):
        export_dir = os.path.join(get_base_path(), "ai_exports")
        os.makedirs(export_dir, exist_ok=True)
        proj_name = os.path.basename(self.project_path)
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        persona_name = self.persona_combo.currentText().split(' - ')[0].replace(' ', '_')
        output_filepath = os.path.join(export_dir, f"{proj_name}_{persona_name}_{timestamp}.md")
        QApplication.setOverrideCursor(QCursor(Qt.CursorShape.WaitCursor))
        try:
            # Using triple quotes correctly for the main content block
            content = f"""# AI Task: {self.persona_combo.currentText()}
## Timestamp: {datetime.now().isoformat()}

---SYSTEM-PROMPT---

{system_prompt}

---USER-PROMPT---

{user_prompt}
"""
            with open(output_filepath, 'w', encoding='utf-8') as f: f.write(content)
            QMessageBox.information(self, "Export Complete", f"Project context exported to:\n{output_filepath}")
            self.accept()
        except Exception as e:
            log.error(f"Export failed: {e}", exc_info=True)
            QMessageBox.critical(self, "Export Failed", f"An error occurred: '{e}'")
        finally:
            QApplication.restoreOverrideCursor()
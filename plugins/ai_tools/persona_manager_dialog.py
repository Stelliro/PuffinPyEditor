# /plugins/ai_tools/persona_manager_dialog.py
import os
import re
import json
import shutil
import importlib.util
from typing import Dict, List, Any
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QTabWidget, QWidget, QSplitter,
    QListWidget, QListWidgetItem, QGroupBox, QFormLayout, QLineEdit,
    QPlainTextEdit, QPushButton, QDialogButtonBox, QMessageBox,
    QLabel, QHBoxLayout, QInputDialog
)
from PyQt6.QtGui import QFont, QTextCursor
from PyQt6.QtCore import Qt
import qtawesome as qta
from app_core.settings_manager import settings_manager
from app_core.highlighters.python_syntax_highlighter import PythonSyntaxHighlighter
from utils.logger import log
from utils.helpers import get_base_path
from .style_preset_manager import StylePresetManager
from app_core import golden_rules

# Boilerplate for creating a new persona file from scratch.
PERSONA_TEMPLATE = """
# /assets/ai_personas/{file_name}.py
import os

class Persona:
    \"\"\"
    {description}
    \"\"\"

    @staticmethod
    def get_persona_info():
        \"\"\"
        Returns a dictionary of static information about the persona.
        \"\"\"
        return {{
            "id": os.path.splitext(os.path.basename(__file__))[0],
            "name": "{name}",
            "title": "{title}",
            "expertise": "{expertise}"
        }}

    def __init__(self):
        self.name = self.get_persona_info()['name']
        self.title = self.get_persona_info()['title']
        self.expertise = self.get_persona_info()['expertise']

    def generate_prompt(self, context: dict) -> tuple[str, str]:
        \"\"\"
        Generates the system and user prompts for this persona.
        \"\"\"
        # --- System Prompt ---
        system_prompt = '''
{system_prompt_logic}
'''

        # --- User Prompt ---
        file_contents_section = []
        for path, content in context.get("file_contents", {{}}).items():
            relative_path = path.replace(context.get("project_root", ""), "", 1).lstrip("/\\\\")
            language = os.path.splitext(path)[1].lstrip('.') or 'text'

            linter_output = ""
            if linter_issues := context.get("linter_results", {{}}).get(path):
                linter_output += "\\n**Linter Issues Found:**\\n"
                for issue in linter_issues:
                    linter_output += "- `Line " + str(issue['line']) + "`: " + issue['code'] + " - " + issue['description'] + "\\n"

            file_contents_section.append(
                "### File: `/" + relative_path + "`" +
                linter_output + "\\n" +
                "```" + language + "\\n" + content + "\\n```"
            )

        file_contents_str = "\\n\\n".join(file_contents_section)

        user_prompt = (
            "**User's Primary Goal:**\\n" +
            context.get("user_instructions", "Perform a general review of the provided code based on your expertise.") +
            "\\n\\n---\\n\\n**Project File Tree:**\\n```\\n" +
            context.get("file_tree", "No file tree provided.") +
            "\\n```\\n\\n---\\n\\n**Full File Contents & Context:**\\n" +
            file_contents_str
        )
        return system_prompt.strip(), user_prompt.strip()

def get_persona_info():
    return Persona.get_persona_info()

def get_persona_instance():
    return Persona()
"""


class PersonaManagerDialog(QDialog):
    """A dialog for managing AI Personas and Style Presets."""

    def __init__(self, theme_manager, parent=None):
        super().__init__(parent)
        self.theme_manager = theme_manager
        self.preset_manager = StylePresetManager()
        self.personas: Dict[str, Dict] = {}
        self.persona_modules: Dict[str, Any] = {}
        self.current_persona_path: str = ""
        self.has_unsaved_changes = False

        self.setWindowTitle("Persona & Style Preset Manager")
        self.setMinimumSize(950, 750)
        self.main_layout = QVBoxLayout(self)

        self.tab_widget = QTabWidget()
        self.tab_widget.addTab(self._create_personas_tab(), "Personas")
        self.tab_widget.addTab(self._create_presets_tab(), "Style Presets")
        self.tab_widget.addTab(self._create_golden_rules_tab(), "Golden Rules")
        self.main_layout.addWidget(self.tab_widget)
        
        self.tab_widget.currentChanged.connect(self._on_tab_changed)

        self._load_all_data()

    def _create_personas_tab(self) -> QWidget:
        widget = QWidget()
        layout = QHBoxLayout(widget)
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        left_pane = QWidget()
        left_layout = QVBoxLayout(left_pane)
        left_layout.addWidget(QLabel("<b>Available Personas:</b>"))
        self.persona_list = QListWidget()
        self.persona_list.currentItemChanged.connect(self._on_persona_selected)
        left_layout.addWidget(self.persona_list)
        
        list_actions_layout = QHBoxLayout()
        add_button = QPushButton("Create New...")
        add_button.clicked.connect(self._create_new_persona)
        self.delete_button = QPushButton("Delete")
        self.delete_button.clicked.connect(self._delete_selected_persona)
        list_actions_layout.addWidget(add_button)
        list_actions_layout.addStretch()
        list_actions_layout.addWidget(self.delete_button)
        left_layout.addLayout(list_actions_layout)
        splitter.addWidget(left_pane)

        right_pane = QWidget()
        right_layout = QVBoxLayout(right_pane)
        
        meta_group = QGroupBox("Metadata")
        meta_layout = QFormLayout(meta_group)
        self.persona_name_edit = QLineEdit()
        self.persona_title_edit = QLineEdit()
        self.persona_expertise_edit = QLineEdit()
        meta_layout.addRow("Name:", self.persona_name_edit)
        meta_layout.addRow("Title:", self.persona_title_edit)
        meta_layout.addRow("Expertise:", self.persona_expertise_edit)
        right_layout.addWidget(meta_group)

        prompt_group = QGroupBox("Prompt Logic (Python)")
        prompt_layout = QVBoxLayout(prompt_group)
        self.persona_code_edit = QPlainTextEdit()
        self.persona_code_edit.setFont(QFont("Consolas", 10))
        self.highlighter = PythonSyntaxHighlighter(self.persona_code_edit.document(), self.theme_manager)
        prompt_layout.addWidget(self.persona_code_edit)
        right_layout.addWidget(prompt_group, 1)

        self.save_changes_button = QPushButton("Save Changes")
        self.save_changes_button.clicked.connect(self._save_persona_changes)
        right_layout.addWidget(self.save_changes_button, 0, Qt.AlignmentFlag.AlignRight)

        splitter.addWidget(right_pane)
        splitter.setSizes([250, 700])
        layout.addWidget(splitter)

        for editor in [self.persona_name_edit, self.persona_title_edit, self.persona_expertise_edit, self.persona_code_edit]:
            if isinstance(editor, QLineEdit):
                editor.textChanged.connect(self._mark_unsaved)
            else:
                editor.textChanged.connect(self._mark_unsaved)

        return widget

    def _create_presets_tab(self) -> QWidget:
        widget = QWidget()
        layout = QHBoxLayout(widget)
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        left_pane = QWidget()
        left_layout = QVBoxLayout(left_pane)
        left_layout.addWidget(QLabel("<b>Style Presets:</b>"))
        self.rules_preset_list = QListWidget()
        self.rules_preset_list.currentItemChanged.connect(self._on_preset_selected)
        left_layout.addWidget(self.rules_preset_list)
        
        preset_actions = QHBoxLayout()
        new_preset_btn = QPushButton("New Preset...")
        new_preset_btn.clicked.connect(self._create_new_preset)
        self.delete_preset_btn = QPushButton("Delete Preset")
        self.delete_preset_btn.clicked.connect(self._delete_selected_preset)
        preset_actions.addWidget(new_preset_btn)
        preset_actions.addStretch()
        preset_actions.addWidget(self.delete_preset_btn)
        left_layout.addLayout(preset_actions)
        splitter.addWidget(left_pane)

        right_pane = QWidget()
        right_layout = QVBoxLayout(right_pane)
        self.rules_group_box = QGroupBox("Preset Details")
        rules_editor_layout = QVBoxLayout(self.rules_group_box)
        
        self.preset_desc_label = QLabel("<i>Select a preset to edit its rules.</i>")
        self.preset_desc_label.setWordWrap(True)
        rules_editor_layout.addWidget(self.preset_desc_label)
        
        self.rules_list_widget = QListWidget()
        rules_editor_layout.addWidget(self.rules_list_widget)

        rule_actions = QHBoxLayout()
        add_rule_btn = QPushButton("Add Rule")
        add_rule_btn.clicked.connect(self._add_rule)
        edit_rule_btn = QPushButton("Edit Rule")
        edit_rule_btn.clicked.connect(self._edit_rule)
        remove_rule_btn = QPushButton("Remove Rule")
        remove_rule_btn.clicked.connect(self._remove_rule)
        rule_actions.addWidget(add_rule_btn)
        rule_actions.addWidget(edit_rule_btn)
        rule_actions.addWidget(remove_rule_btn)
        rule_actions.addStretch()
        rules_editor_layout.addLayout(rule_actions)

        self.save_preset_button = QPushButton("Save Preset Changes")
        self.save_preset_button.clicked.connect(self._save_current_preset)
        right_layout.addWidget(self.rules_group_box)
        right_layout.addWidget(self.save_preset_button, 0, Qt.AlignmentFlag.AlignRight)

        splitter.addWidget(right_pane)
        splitter.setSizes([250, 700])
        layout.addWidget(splitter)

        return widget

    def _create_golden_rules_tab(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(10, 10, 10, 10)

        group_box = QGroupBox("Golden Rules for AI Interaction")
        group_layout = QVBoxLayout(group_box)
        
        description = QLabel(
            "These are the fundamental, non-negotiable rules sent with every AI request.<br>"
            "Edit the rules below. The numbering is for display and will be handled automatically."
        )
        description.setWordWrap(True)
        group_layout.addWidget(description)

        self.golden_rules_edit = QPlainTextEdit()
        self.golden_rules_edit.setFont(QFont("Consolas", 10))
        self.golden_rules_edit.setPlaceholderText("1. First rule...\n2. Second rule...")
        group_layout.addWidget(self.golden_rules_edit, 1)
        
        buttons_layout = QHBoxLayout()
        self.reset_golden_rules_button = QPushButton("Reset to Default")
        self.save_golden_rules_button = QPushButton("Save Changes")
        buttons_layout.addStretch()
        buttons_layout.addWidget(self.reset_golden_rules_button)
        buttons_layout.addWidget(self.save_golden_rules_button)
        group_layout.addLayout(buttons_layout)
        
        layout.addWidget(group_box)
        
        self.save_golden_rules_button.clicked.connect(self._save_golden_rules)
        self.reset_golden_rules_button.clicked.connect(self._reset_golden_rules)
        
        return widget

    def _load_all_data(self):
        self.has_unsaved_changes = False
        self._discover_and_populate_personas()
        
        if self.persona_list.count() > 0:
            self.persona_list.setCurrentRow(0)
            self._on_persona_selected(self.persona_list.item(0))
        else:
            self._set_editor_state(enabled=False)
            
        self._populate_rules_presets()
        if self.rules_preset_list.count() > 0:
            self.rules_preset_list.setCurrentRow(0)
        
        self._load_golden_rules()

    def _on_tab_changed(self, index: int):
        if self.tab_widget.tabText(index) == "Golden Rules":
            self._load_golden_rules()

    def _load_golden_rules(self):
        self.golden_rules_edit.setPlainText(golden_rules.get_golden_rules_text())

    def _save_golden_rules(self):
        text = self.golden_rules_edit.toPlainText()
        if golden_rules.save_golden_rules_from_text(text):
            QMessageBox.information(self, "Success", "Golden Rules have been saved.")
        else:
            QMessageBox.critical(self, "Error", "Could not save Golden Rules. Check logs for details.")

    def _reset_golden_rules(self):
        reply = QMessageBox.question(self, "Reset Rules", 
                                     "Are you sure you want to revert all Golden Rules to their default values?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                     QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            if golden_rules.reset_golden_rules_to_default():
                self._load_golden_rules()
                QMessageBox.information(self, "Success", "Golden Rules have been reset to default.")
            else:
                QMessageBox.critical(self, "Error", "Could not reset Golden Rules. Check logs for details.")

    def _discover_and_populate_personas(self):
        self.persona_list.clear()
        self.personas.clear()
        self.persona_modules.clear()
        persona_dir = os.path.join(get_base_path(), "assets", "ai_personas")

        if not os.path.isdir(persona_dir):
            os.makedirs(persona_dir, exist_ok=True)
            log.info(f"Created persona directory at {persona_dir}")
            return

        for filename in sorted(os.listdir(persona_dir)):
            if filename.endswith(".py") and not filename.startswith("__"):
                module_path = os.path.join(persona_dir, filename)
                module_name = f"assets.ai_personas.{os.path.splitext(filename)[0]}"
                try:
                    spec = importlib.util.spec_from_file_location(module_name, module_path)
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)

                    if hasattr(module, "get_persona_info"):
                        info = module.get_persona_info()
                        self.personas[info['id']] = info
                        item = QListWidgetItem(info['name'])
                        item.setData(Qt.ItemDataRole.UserRole, info['id'])
                        self.persona_list.addItem(item)
                except Exception as e:
                    log.error(f"Failed to load AI persona '{filename}': {e}", exc_info=True)

    def _on_persona_selected(self, item: QListWidgetItem):
        if self.has_unsaved_changes:
            reply = QMessageBox.question(self, "Unsaved Changes", 
                                       "You have unsaved changes. Discard them?",
                                       QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.No:
                previous_id = os.path.basename(os.path.splitext(self.current_persona_path)[0])
                for i in range(self.persona_list.count()):
                    if self.persona_list.item(i).data(Qt.ItemDataRole.UserRole) == previous_id:
                        self.persona_list.setCurrentRow(i)
                        break
                return
                
        if not item:
            self._set_editor_state(False)
            return
            
        persona_id = item.data(Qt.ItemDataRole.UserRole)
        persona_info = self.personas.get(persona_id)

        if not persona_info:
             self._set_editor_state(False)
             log.warning(f"Could not find info for persona ID: {persona_id}")
             return
        
        self.persona_name_edit.setText(persona_info.get("name", ""))
        self.persona_title_edit.setText(persona_info.get("title", ""))
        self.persona_expertise_edit.setText(persona_info.get("expertise", ""))
        
        self.current_persona_path = os.path.join(get_base_path(), "assets", "ai_personas", f"{persona_id}.py")
        
        try:
            with open(self.current_persona_path, 'r', encoding='utf-8') as f:
                content = f.read()
                match = re.search(r"system_prompt\s*=\s*'''\n(.*?)\n'''", content, re.DOTALL)
                prompt_logic = match.group(1).strip() if match else "# Could not automatically extract system_prompt logic."
                self.persona_code_edit.setPlainText(prompt_logic)
        except Exception as e:
            self.persona_code_edit.setPlainText(f"# Error loading persona code: {e}")
            log.error(f"Error reading persona file {self.current_persona_path}: {e}")

        self._set_editor_state(True)
        self.has_unsaved_changes = False
        self.save_changes_button.setEnabled(False)
        self.delete_button.setEnabled(True)

    def _mark_unsaved(self):
        self.has_unsaved_changes = True
        self.save_changes_button.setEnabled(True)

    def _set_editor_state(self, enabled: bool):
        self.persona_name_edit.setEnabled(enabled)
        self.persona_title_edit.setEnabled(enabled)
        self.persona_expertise_edit.setEnabled(enabled)
        self.persona_code_edit.setEnabled(enabled)
        self.save_changes_button.setEnabled(enabled and self.has_unsaved_changes)
        self.delete_button.setEnabled(enabled)

    def _save_persona_changes(self):
        if not self.current_persona_path: return

        file_name_without_ext = os.path.basename(os.path.splitext(self.current_persona_path)[0])
        
        full_code = PERSONA_TEMPLATE.format(
            file_name=file_name_without_ext,
            name=self.persona_name_edit.text(),
            title=self.persona_title_edit.text(),
            expertise=self.persona_expertise_edit.text(),
            description=f"Represents {self.persona_name_edit.text()}",
            system_prompt_logic=self.persona_code_edit.toPlainText()
        )
        
        try:
            with open(self.current_persona_path, 'w', encoding='utf-8') as f:
                f.write(full_code)
            
            QMessageBox.information(self, "Success", f"Persona '{self.persona_name_edit.text()}' saved successfully.")
            self.has_unsaved_changes = False
            self.save_changes_button.setEnabled(False)
            current_id = file_name_without_ext
            
            self._discover_and_populate_personas()
            for i in range(self.persona_list.count()):
                 if self.persona_list.item(i).data(Qt.ItemDataRole.UserRole) == current_id:
                      self.persona_list.setCurrentRow(i)
                      break
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save persona: {e}")
            log.error(f"Error saving persona: {e}", exc_info=True)

    def _create_new_persona(self):
        name, ok = QInputDialog.getText(self, "Create New Persona", "Enter a name for the new persona:")
        if not (ok and name and name.strip()): return

        safe_id = re.sub(r'[\s\-]+', '_', name.strip()).lower()
        safe_id = re.sub(r'[^\w_]', '', safe_id)
        if not safe_id: safe_id = "new_persona"
        
        file_name = f"{safe_id}"
        
        new_path = os.path.join(get_base_path(), "assets", "ai_personas", f"{file_name}.py")
        if os.path.exists(new_path):
            QMessageBox.warning(self, "File Exists", f"A persona file named '{file_name}.py' already exists.")
            return

        initial_content = PERSONA_TEMPLATE.format(
            file_name=file_name,
            name=name,
            title="Custom Persona",
            expertise="User-defined expertise",
            description=f"A custom persona named {name}.",
            system_prompt_logic="You are a helpful AI assistant. Your goal is to provide clear, concise, and actionable advice based on the user's request."
        )

        try:
            with open(new_path, 'w', encoding='utf-8') as f:
                f.write(initial_content)
            
            self._discover_and_populate_personas()
            for i in range(self.persona_list.count()):
                if self.persona_list.item(i).data(Qt.ItemDataRole.UserRole) == file_name:
                    self.persona_list.setCurrentRow(i)
                    break
        except Exception as e:
            QMessageBox.critical(self, "Creation Failed", f"Could not create new persona file: {e}")
            log.error(f"Failed creating persona: {e}", exc_info=True)

    def _delete_selected_persona(self):
        item = self.persona_list.currentItem()
        if not item: return

        reply = QMessageBox.question(self, "Confirm Delete",
            f"Are you sure you want to permanently delete the '{item.text()}' persona?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.No)

        if reply == QMessageBox.StandardButton.Yes:
            persona_id = item.data(Qt.ItemDataRole.UserRole)
            persona_file = os.path.join(get_base_path(), "assets", "ai_personas", f"{persona_id}.py")
            try:
                os.remove(persona_file)
                self._discover_and_populate_personas()
                if self.persona_list.count() > 0:
                    self.persona_list.setCurrentRow(0)
                else:
                    self._set_editor_state(enabled=False)

            except Exception as e:
                QMessageBox.critical(self, "Deletion Failed", f"Could not delete persona file: {e}")
                log.error(f"Could not delete {persona_file}: {e}", exc_info=True)
                
    def _populate_rules_presets(self):
        current_id = None
        if current_item := self.rules_preset_list.currentItem():
            current_id = current_item.data(Qt.ItemDataRole.UserRole)
        
        self.rules_preset_list.clear()
        self.preset_manager.presets = self.preset_manager.load_presets()
        for preset_id, preset_name in self.preset_manager.get_preset_names_for_ui():
            item = QListWidgetItem(preset_name)
            item.setData(Qt.ItemDataRole.UserRole, preset_id)
            self.rules_preset_list.addItem(item)
            
        if current_id:
            for i in range(self.rules_preset_list.count()):
                if self.rules_preset_list.item(i).data(Qt.ItemDataRole.UserRole) == current_id:
                    self.rules_preset_list.setCurrentRow(i)
                    break
            
    def _on_preset_selected(self, item: QListWidgetItem):
        self.rules_list_widget.clear()
        if not item:
            self.rules_group_box.setEnabled(False)
            self.preset_desc_label.setText("<i>Select a preset to edit its rules.</i>")
            return
            
        self.rules_group_box.setEnabled(True)
        preset_id = item.data(Qt.ItemDataRole.UserRole)
        preset_data = self.preset_manager.presets.get(preset_id, {})
        
        self.rules_group_box.setTitle(preset_data.get("name", "Unnamed Preset"))
        self.preset_desc_label.setText(preset_data.get("description", "No description."))
        
        for rule in preset_data.get("rules", []):
            self.rules_list_widget.addItem(QListWidgetItem(rule))

    def _create_new_preset(self):
        name, ok = QInputDialog.getText(self, "New Preset", "Enter a name for the new style preset:")
        if not (ok and name and name.strip()): return
            
        preset_id = re.sub(r'[\s\-]+', '_', name.strip()).lower()
        preset_id = re.sub(r'[^\w_]', '', preset_id)
        if not preset_id: preset_id = "new_style_preset"
        
        if preset_id in self.preset_manager.presets:
            QMessageBox.warning(self, "Preset Exists", "A preset with that name/ID already exists.")
            return
            
        new_preset_data = {"name": name, "description": "A new custom style preset.", "rules": []}
        if self.preset_manager.save_preset(preset_id, new_preset_data):
            self._populate_rules_presets()
            for i in range(self.rules_preset_list.count()):
                if self.rules_preset_list.item(i).data(Qt.ItemDataRole.UserRole) == preset_id:
                    self.rules_preset_list.setCurrentRow(i)
                    break
                    
    def _delete_selected_preset(self):
        item = self.rules_preset_list.currentItem()
        if not item: return
        
        preset_id = item.data(Qt.ItemDataRole.UserRole)
        reply = QMessageBox.question(self, "Confirm Delete", f"Delete the preset '{item.text()}'?")
        if reply == QMessageBox.StandardButton.Yes:
            if self.preset_manager.delete_preset(preset_id):
                self._populate_rules_presets()
    
    def _add_rule(self):
        text, ok = QInputDialog.getText(self, "Add Rule", "Enter new rule text:")
        if ok and text: self.rules_list_widget.addItem(QListWidgetItem(text))

    def _edit_rule(self):
        item = self.rules_list_widget.currentItem()
        if not item: return
        new_text, ok = QInputDialog.getText(self, "Edit Rule", "Edit rule text:", text=item.text())
        if ok and new_text: item.setText(new_text)

    def _remove_rule(self):
        item = self.rules_list_widget.currentItem()
        if not item: return
        self.rules_list_widget.takeItem(self.rules_list_widget.row(item))

    def _save_current_preset(self):
        item = self.rules_preset_list.currentItem()
        if not item: return
        
        preset_id = item.data(Qt.ItemDataRole.UserRole)
        preset_data = self.preset_manager.presets.get(preset_id)
        if not preset_data: return

        preset_data["rules"] = [self.rules_list_widget.item(i).text() for i in range(self.rules_list_widget.count())]
        
        if self.preset_manager.save_preset(preset_id, preset_data):
            QMessageBox.information(self, "Success", f"Preset '{preset_data['name']}' saved.")
        else:
            QMessageBox.critical(self, "Error", "Failed to save preset.")
                
    def closeEvent(self, event):
        if self.has_unsaved_changes:
            reply = QMessageBox.question(self, "Unsaved Changes",
                                     "You have unsaved changes. Close without saving?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.No:
                event.ignore()
                return
        event.accept()
# /plugins/refactor_tool/refactor_dialog.py
import os
import jedi
from typing import Optional, List, Dict
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QWidget, QFormLayout,
                             QLineEdit, QCheckBox, QPushButton, QTextEdit,
                             QMessageBox, QProgressDialog, QApplication)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt, pyqtSignal, QObject, QRunnable, QThreadPool

from app_core.puffin_api import PuffinPluginAPI
from app_core.completion_manager import find_python_interpreter_for_jedi
from utils.logger import log


class JediRefactorSignals(QObject):
    """Defines signals for the background refactoring worker."""
    preview_ready = pyqtSignal(str)
    refactor_finished = pyqtSignal(bool, str)
    error = pyqtSignal(str)


class JediRefactorWorker(QRunnable):
    """A worker thread to perform Jedi refactoring operations."""
    def __init__(self, script, new_name, get_diff=True):
        super().__init__()
        self.script: jedi.Script = script
        self.new_name: str = new_name
        self.get_diff: bool = get_diff
        self.signals = JediRefactorSignals()

    def run(self):
        try:
            refactoring = self.script.rename(new_name=self.new_name)
        except (jedi.RefactoringError, Exception) as e:
            self.signals.error.emit(f"Could not perform rename: {e}")
            return
            
        if self.get_diff:
            diff = refactoring.get_diff()
            self.signals.preview_ready.emit(diff)
        else:
            try:
                refactoring.apply()
                self.signals.refactor_finished.emit(True, "Refactoring applied successfully.")
            except Exception as e:
                self.signals.refactor_finished.emit(False, f"Failed to apply refactoring: {e}")


class RefactorDialog(QDialog):
    def __init__(self, puffin_api: PuffinPluginAPI, parent=None):
        super().__init__(parent)
        self.api = puffin_api
        self.main_window = self.api.get_main_window()
        self.project_manager = self.api.get_manager("project")
        
        # --- Jedi Setup ---
        python_executable = find_python_interpreter_for_jedi()
        project_path = self.project_manager.get_active_project_path()
        try:
            self.jedi_project = jedi.Project(path=project_path, environment_path=python_executable)
        except Exception as e:
            QMessageBox.critical(self, "Jedi Error", f"Could not initialize code analysis engine (Jedi): {e}")
            # Defer closing to allow the message box to show
            self.close() 
            return

        self.threadpool = QThreadPool()

        self._setup_ui()
        self._get_initial_state()

    def _setup_ui(self):
        self.setWindowTitle("Rename Symbol")
        self.setMinimumSize(700, 500)
        layout = QVBoxLayout(self)

        form_layout = QFormLayout()
        self.old_name_edit = QLineEdit()
        self.old_name_edit.setReadOnly(True)
        self.new_name_edit = QLineEdit()

        form_layout.addRow("Original Name:", self.old_name_edit)
        form_layout.addRow("New Name:", self.new_name_edit)
        layout.addLayout(form_layout)
        
        self.scope_checkbox = QCheckBox("Rename in entire project (disables preview)")
        self.scope_checkbox.toggled.connect(lambda checked: self.preview_button.setDisabled(checked))
        layout.addWidget(self.scope_checkbox)

        self.diff_viewer = QTextEdit()
        self.diff_viewer.setReadOnly(True)
        self.diff_viewer.setFont(QFont("Consolas", 10))
        layout.addWidget(self.diff_viewer, 1)

        button_layout = QHBoxLayout()
        self.preview_button = QPushButton("Preview Changes")
        self.apply_button = QPushButton("Apply")
        self.close_button = QPushButton("Close")

        button_layout.addStretch()
        button_layout.addWidget(self.preview_button)
        button_layout.addWidget(self.apply_button)
        button_layout.addWidget(self.close_button)
        layout.addLayout(button_layout)
        
        self.preview_button.clicked.connect(self._get_preview)
        self.apply_button.clicked.connect(self._apply_refactor)
        self.close_button.clicked.connect(self.close)

    def _get_initial_state(self):
        self.editor = self.main_window.tab_widget.currentWidget()
        cursor = self.editor.text_area.textCursor()
        
        selected_text = cursor.selectedText()
        # If nothing is selected, select the word under the cursor
        if not selected_text:
            cursor.select(cursor.SelectionType.WordUnderCursor)
            selected_text = cursor.selectedText()
            
        self.old_name_edit.setText(selected_text)
        self.new_name_edit.setText(selected_text)
        self.new_name_edit.setFocus()
        self.new_name_edit.selectAll()

    def _create_jedi_script(self):
        line, col = self.editor.get_cursor_position()
        source = self.editor.get_text()
        filepath = self.editor.filepath
        
        try:
            return jedi.Script(code=source, path=filepath, project=self.jedi_project,
                               line=line, column=col)
        except Exception as e:
            QMessageBox.critical(self, "Jedi Error", f"Could not create script context: {e}")
            return None

    def _get_preview(self):
        if not self._validate_input(): return
            
        script = self._create_jedi_script()
        if not script: return
        
        self._run_worker(script, get_diff=True)
    
    def _apply_refactor(self):
        if not self._validate_input(): return

        new_name = self.new_name_edit.text()
        old_name = self.old_name_edit.text()
        reply = QMessageBox.question(
            self,
            "Confirm Refactoring",
            f"Are you sure you want to rename all occurrences of '{old_name}' to '{new_name}'?\n\nThis action will modify files on disk.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.Cancel,
        )
        if reply == QMessageBox.StandardButton.Cancel: return
            
        script = self._create_jedi_script()
        if not script: return

        self._run_worker(script, get_diff=False)
    
    def _validate_input(self):
        new_name = self.new_name_edit.text().strip()
        if not new_name.isidentifier():
            QMessageBox.warning(self, "Invalid Name", f"'{new_name}' is not a valid Python identifier.")
            return False
        return True

    def _run_worker(self, script, get_diff):
        self.progress_dialog = QProgressDialog(self)
        self.progress_dialog.setLabelText("Analyzing code...")
        self.progress_dialog.setCancelButton(None)
        self.progress_dialog.setModal(True)
        self.progress_dialog.show()

        worker = JediRefactorWorker(script, self.new_name_edit.text(), get_diff=get_diff)
        worker.signals.preview_ready.connect(self._on_preview_ready)
        worker.signals.refactor_finished.connect(self._on_refactor_finished)
        worker.signals.error.connect(self._on_error)
        self.threadpool.start(worker)

    def _on_preview_ready(self, diff):
        self.progress_dialog.close()
        self.diff_viewer.setPlainText(diff)
        if not diff:
            self.diff_viewer.setText("(No changes detected in the current file)")
    
    def _on_refactor_finished(self, success, message):
        self.progress_dialog.close()
        if success:
            QMessageBox.information(self, "Success", message)
            self.api.get_main_window().explorer_panel.refresh()
            self.accept()
        else:
            QMessageBox.critical(self, "Error", message)
    
    def _on_error(self, message):
        self.progress_dialog.close()
        QMessageBox.critical(self, "Refactoring Error", message)
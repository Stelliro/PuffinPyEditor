# PuffinPyEditor/ui/dialogs/search_replace_dialog.py
from typing import Optional
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel,
                             QLineEdit, QPushButton, QCheckBox, QWidget)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QKeyEvent, QTextDocument
from app_core.settings_manager import settings_manager
from ui.editor_widget import EditorWidget


class SearchReplaceDialog(QDialog):
    """
    A non-modal dialog for finding and replacing text within an EditorWidget.
    """

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.editor_widget: Optional[EditorWidget] = None
        self._setup_ui()
        self._connect_signals()
        self.load_search_options()

    def _setup_ui(self):
        """Creates the main UI layout and widgets."""
        self.setWindowTitle("Find and Replace")
        self.setMinimumWidth(400)
        self.main_layout = QVBoxLayout(self)

        grid_layout = QGridLayout()
        grid_layout.setSpacing(10)

        self.find_text_edit = QLineEdit()
        self.replace_text_edit = QLineEdit()
        grid_layout.addWidget(QLabel("Find what:"), 0, 0)
        grid_layout.addWidget(self.find_text_edit, 0, 1, 1, 2)
        grid_layout.addWidget(QLabel("Replace with:"), 1, 0)
        grid_layout.addWidget(self.replace_text_edit, 1, 1, 1, 2)

        self.case_sensitive_checkbox = QCheckBox("Case sensitive")
        self.whole_word_checkbox = QCheckBox("Whole word")
        # Regex checkbox can be added here in the future if needed
        # self.regex_checkbox = QCheckBox("Regular expression")
        grid_layout.addWidget(self.case_sensitive_checkbox, 2, 1)
        grid_layout.addWidget(self.whole_word_checkbox, 2, 2)

        self.main_layout.addLayout(grid_layout)

        button_layout = QHBoxLayout()
        self.find_next_button = QPushButton("Find Next")
        self.replace_button = QPushButton("Replace")
        self.replace_all_button = QPushButton("Replace All")
        button_layout.addStretch()
        button_layout.addWidget(self.find_next_button)
        button_layout.addWidget(self.replace_button)
        button_layout.addWidget(self.replace_all_button)
        self.main_layout.addLayout(button_layout)

    def _connect_signals(self):
        """Connects widget signals to their slots."""
        self.find_text_edit.textChanged.connect(self._update_button_states)
        self.find_next_button.clicked.connect(self._find_next)
        self.replace_button.clicked.connect(self._replace_one)
        self.replace_all_button.clicked.connect(self._replace_all)

    def show_dialog(self, editor_widget: EditorWidget):
        """
        Shows the dialog, linking it to a specific editor instance.
        """
        self.editor_widget = editor_widget
        initial_find_text = editor_widget.text_area.textCursor().selectedText()
        if initial_find_text:
            self.find_text_edit.setText(initial_find_text)

        self.find_text_edit.selectAll()
        self.show()
        self.activateWindow()
        self.raise_()
        self.find_text_edit.setFocus()

    def load_search_options(self):
        """Loads saved search options from settings."""
        self.case_sensitive_checkbox.setChecked(settings_manager.get("search_case_sensitive", False))
        self.whole_word_checkbox.setChecked(settings_manager.get("search_whole_word", False))

    def save_search_options(self):
        """Saves current search options to settings."""
        settings_manager.set("search_case_sensitive", self.case_sensitive_checkbox.isChecked(), False)
        settings_manager.set("search_whole_word", self.whole_word_checkbox.isChecked(), False)
        settings_manager.save()

    def _get_find_flags(self) -> QTextDocument.FindFlag:
        """Constructs the search flags based on checkbox states."""
        flags = QTextDocument.FindFlag(0)
        if self.case_sensitive_checkbox.isChecked():
            flags |= QTextDocument.FindFlag.FindCaseSensitively
        if self.whole_word_checkbox.isChecked():
            flags |= QTextDocument.FindFlag.FindWholeWords
        return flags

    def _find_next(self):
        """Finds the next occurrence of the search query."""
        if not self.editor_widget: return
        query = self.find_text_edit.text()
        flags = self._get_find_flags()
        self.editor_widget.find_next(query, flags)
        self.save_search_options()

    def _replace_one(self):
        """Replaces the currently selected occurrence and finds the next one."""
        if not self.editor_widget: return
        query = self.find_text_edit.text()
        replace_text = self.replace_text_edit.text()
        flags = self._get_find_flags()
        self.editor_widget.replace_current(query, replace_text, flags)
        self.save_search_options()

    def _replace_all(self):
        """Replaces all occurrences of the search query in the document."""
        if not self.editor_widget: return
        query = self.find_text_edit.text()
        replace_text = self.replace_text_edit.text()
        flags = self._get_find_flags()
        count = self.editor_widget.replace_all(query, replace_text, flags)
        self.save_search_options()
        if self.parent():
            self.parent().statusBar().showMessage(f"Replaced {count} occurrence(s).", 3000)

    def _update_button_states(self):
        """Enables/disables buttons based on whether there is search text."""
        enable = bool(self.find_text_edit.text())
        self.find_next_button.setEnabled(enable)
        self.replace_button.setEnabled(enable)
        self.replace_all_button.setEnabled(enable)

    def keyPressEvent(self, event: QKeyEvent):
        """Closes the dialog on Escape key press."""
        if event.key() == Qt.Key.Key_Escape:
            self.hide()
        else:
            super().keyPressEvent(event)
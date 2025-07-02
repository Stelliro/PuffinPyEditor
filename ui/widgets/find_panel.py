# /ui/widgets/find_panel.py
from typing import Optional, TYPE_CHECKING
from PyQt6.QtWidgets import (QWidget, QHBoxLayout, QVBoxLayout, QLineEdit,
                             QPushButton, QCheckBox, QToolButton, QFrame)
from PyQt6.QtGui import QTextDocument, QKeyEvent
from PyQt6.QtCore import Qt, pyqtSignal
import qtawesome as qta

from app_core.settings_manager import settings_manager
from app_core.theme_manager import theme_manager

# This is a super neat trick I learned to prevent circular import errors!
# It lets me use EditorWidget for type hinting without actually importing it at runtime.
if TYPE_CHECKING:
    from ..editor_widget import EditorWidget


class FindPanel(QFrame):
    """An integrated panel for find and replace operations."""
    # This signal tells the parent (the EditorWidget) to close me.
    close_requested = pyqtSignal()
    # This signal asks the main window to show a message in the status bar.
    status_message_requested = pyqtSignal(str, int)

    def __init__(self, parent: QWidget):
        super().__init__(parent)
        # This will be the editor widget this panel is currently controlling.
        self.editor: Optional["EditorWidget"] = None
        # Giving this an object name is great for styling with CSS-like QSS!
        self.setObjectName("FindPanelFrame")
        self._setup_ui()
        self._connect_signals()
        self.load_settings()
        self.update_theme()

    def _setup_ui(self):
        # This function builds the visual components of the panel.
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(5, 5, 5, 5)
        self.main_layout.setSpacing(5)

        find_layout = QHBoxLayout()
        self.toggle_button = QToolButton()
        self.toggle_button.setCheckable(True)
        self.toggle_button.setAutoRaise(True)
        self.toggle_button.setIcon(qta.icon('fa5s.chevron-right'))
        find_layout.addWidget(self.toggle_button)

        self.find_input = QLineEdit()
        self.find_input.setPlaceholderText("Find")
        find_layout.addWidget(self.find_input)

        self.find_prev_button = self._create_tool_button(
            'fa5s.arrow-up', "Find Previous (Shift+F3)")
        self.find_next_button = self._create_tool_button(
            'fa5s.arrow-down', "Find Next (F3)")
        self.close_button = self._create_tool_button(
            'fa5s.times', "Close (Esc)")
        find_layout.addWidget(self.find_prev_button)
        find_layout.addWidget(self.find_next_button)
        find_layout.addWidget(self.close_button)
        self.main_layout.addLayout(find_layout)

        # This widget holds the "replace" parts and can be hidden/shown.
        self.expandable_widget = QWidget()
        expandable_layout = QVBoxLayout(self.expandable_widget)
        expandable_layout.setContentsMargins(0, 5, 0, 0)
        expandable_layout.setSpacing(5)

        replace_layout = QHBoxLayout()
        self.replace_input = QLineEdit()
        self.replace_input.setPlaceholderText("Replace")
        self.replace_button = self._create_tool_button(
            'fa5s.exchange-alt', "Replace", text="Replace")
        self.replace_all_button = self._create_tool_button(
            'fa5s.magic', "Replace All", text="All")
        replace_layout.addWidget(self.replace_input)
        replace_layout.addWidget(self.replace_button)
        replace_layout.addWidget(self.replace_all_button)
        expandable_layout.addLayout(replace_layout)

        options_layout = QHBoxLayout()
        options_layout.setContentsMargins(25, 0, 0, 0)
        self.case_checkbox = QCheckBox("Case Sensitive")
        self.whole_word_checkbox = QCheckBox("Whole Word")
        options_layout.addWidget(self.case_checkbox)
        options_layout.addWidget(self.whole_word_checkbox)
        options_layout.addStretch()
        expandable_layout.addLayout(options_layout)

        self.main_layout.addWidget(self.expandable_widget)
        self.expandable_widget.hide()

    def _create_tool_button(
            self, icon_name: str, tooltip: str, text: Optional[str] = None
    ) -> QToolButton:
        # A helper function to make creating buttons less repetitive. DRY principle!
        button = QToolButton()
        button.setAutoRaise(True)
        button.setToolTip(tooltip)
        button.setProperty("icon_name", icon_name) # Store the icon name for theming
        if text:
            button.setText(text)
            button.setToolButtonStyle(
                Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        return button

    def _connect_signals(self):
        # Connecting all the button clicks to their functions.
        self.close_button.clicked.connect(self.close_requested.emit)
        self.toggle_button.toggled.connect(self.expandable_widget.setVisible)
        self.find_input.textChanged.connect(self._update_button_states)
        self.find_input.returnPressed.connect(self.find_next_button.click)
        self.find_next_button.clicked.connect(
            lambda: self._find(backwards=False))
        self.find_prev_button.clicked.connect(
            lambda: self._find(backwards=True))
        self.replace_button.clicked.connect(self._replace)
        self.replace_all_button.clicked.connect(self._replace_all)

    def connect_editor(self, editor: "EditorWidget"):
        # This method links the panel to a specific editor instance.
        self.editor = editor
        # Pre-fill the find input with any selected text.
        initial_text = editor.text_area.textCursor().selectedText()
        if initial_text:
            self.find_input.setText(initial_text)
        self.focus_find_input()
        self._update_button_states()

    def focus_find_input(self):
        self.find_input.setFocus()
        self.find_input.selectAll()

    def update_theme(self):
        # Applies the current theme's colors to the panel.
        colors = theme_manager.current_theme_data['colors']
        frame_bg = colors.get('sidebar.background', '#333')
        self.setStyleSheet(
            f"#FindPanelFrame {{ background-color: {frame_bg}; "
            f"border-bottom: 1px solid {colors.get('input.border')}; }}")
        # I'm re-applying icons here to make sure they get the new theme colors.
        for button in self.findChildren((QToolButton, QPushButton)):
            if icon_name := button.property("icon_name"):
                button.setIcon(qta.icon(icon_name))

    def keyPressEvent(self, event: QKeyEvent):
        # A key press event handler to allow closing the panel with the Escape key.
        if event.key() == Qt.Key.Key_Escape:
            self.close_requested.emit()
            return
        super().keyPressEvent(event)

    def load_settings(self):
        # Loads user preferences for search options.
        self.case_checkbox.setChecked(
            settings_manager.get("search_case_sensitive", False))
        self.whole_word_checkbox.setChecked(
            settings_manager.get("search_whole_word", False))

    def save_settings(self):
        # Saves user preferences for search options.
        settings_manager.set(
            "search_case_sensitive", self.case_checkbox.isChecked())
        settings_manager.set(
            "search_whole_word", self.whole_word_checkbox.isChecked())

    def _update_button_states(self):
        # Disables buttons if there's no text to find.
        has_text = bool(self.find_input.text())
        self.find_next_button.setEnabled(has_text)
        self.find_prev_button.setEnabled(has_text)
        self.replace_button.setEnabled(has_text)
        self.replace_all_button.setEnabled(has_text)

    def _get_find_flags(self) -> QTextDocument.FindFlag:
        # Converts our checkboxes into flags that Qt's find function understands.
        flags = QTextDocument.FindFlag(0)
        if self.case_checkbox.isChecked():
            flags |= QTextDocument.FindFlag.FindCaseSensitively
        if self.whole_word_checkbox.isChecked():
            flags |= QTextDocument.FindFlag.FindWholeWords
        return flags

    def _find(self, backwards: bool = False):
        # Performs the find operation.
        if not self.editor:
            return
        query = self.find_input.text()
        flags = self._get_find_flags()
        if backwards:
            flags |= QTextDocument.FindFlag.FindBackward
        if not self.editor.find_next(query, flags):
            self.status_message_requested.emit(
                f"No more occurrences of '{query}' found.", 2000)
        self.save_settings()

    def _replace(self):
        # Performs a single replacement.
        if not self.editor:
            return
        query = self.find_input.text()
        replace_text = self.replace_input.text()
        flags = self._get_find_flags()
        if not self.editor.replace_current(query, replace_text, flags):
            self.status_message_requested.emit(
                "Nothing selected to replace.", 2000)
        self.save_settings()

    def _replace_all(self):
        # Performs a "replace all" operation.
        if not self.editor:
            return
        query = self.find_input.text()
        replace_text = self.replace_input.text()
        flags = self._get_find_flags()
        count = self.editor.replace_all(query, replace_text, flags)
        self.save_settings()
        self.status_message_requested.emit(
            f"Replaced {count} occurrence(s).", 3000)
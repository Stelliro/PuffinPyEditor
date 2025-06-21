# PuffinPyEditor/ui/dialogs/theme_editor_dialog.py
import sys
import os
import json
import re
import datetime
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QGridLayout, QWidget,
                             QLabel, QLineEdit, QPushButton, QDialogButtonBox, QFileDialog,
                             QScrollArea, QMessageBox, QColorDialog, QListWidget,
                             QListWidgetItem, QSplitter, QFrame)
from PyQt6.QtGui import QColor, QFont, QPixmap, QIcon
from PyQt6.QtCore import Qt, pyqtSignal, QSize
from utils.logger import log
from app_core.theme_manager import theme_manager, CUSTOM_THEMES_FILE_PATH


# --- Helper Widget for Color Picking ---
class ColorPickerButton(QPushButton):
    color_changed = pyqtSignal(QColor)

    def __init__(self, initial_color=QColor("black"), parent=None):
        super().__init__(parent)
        self._color = initial_color
        self.setFixedSize(QSize(130, 28));
        self.setIconSize(QSize(20, 20))
        self._update_swatch();
        self.clicked.connect(self._pick_color)

    def _update_swatch(self):
        pixmap = QPixmap(self.iconSize());
        pixmap.fill(self._color)
        self.setIcon(QIcon(pixmap));
        self.setText(self._color.name().upper())

    def set_color(self, new_color):
        if self._color != new_color:
            self._color = new_color;
            self._update_swatch();
            self.color_changed.emit(self._color)

    def get_color(self):
        return self._color

    def _pick_color(self):
        dialog = QColorDialog(self._color, self)
        if dialog.exec(): self.set_color(dialog.currentColor())


class ExampleWidget(QLabel):
    def __init__(self, text="Example", parent=None):
        super().__init__(text, parent)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter);
        self.setMinimumWidth(100)
        self.setAutoFillBackground(True);
        self.setStyleSheet("border: 1px solid grey; border-radius: 4px; padding: 4px;")


# --- Dialog for Theme Editing ---
class ThemeEditorDialog(QDialog):
    custom_themes_changed = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        log.info("ThemeEditorDialog initializing...");
        self.setWindowTitle("Theme Customizer")
        self.setMinimumSize(QSize(950, 700));
        self.setModal(True)
        self.COLOR_GROUPS = {"Window & General": ["window.", "sidebar.", "accent"],
                             "Controls": ["button.", "input.", "scrollbar."], "Bars & Menus": ["statusbar.", "menu."],
                             "Editor Tabs": ["tab."], "Editor": ["editor.", "editorGutter."],
                             "Syntax Highlighting": ["syntax."]}
        self.current_theme_id = None;
        self.is_custom_theme = False;
        self.color_widgets = {};
        self.unsaved_changes = False
        self._setup_ui();
        self._repopulate_theme_list();
        self._update_ui_state()
        log.info("ThemeEditorDialog initialized successfully.")

    def _setup_ui(self):
        self.main_layout = QVBoxLayout(self);
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        self.main_layout.addWidget(self.splitter, 1)
        self._create_left_pane();
        self._create_right_pane()
        self.splitter.setSizes([240, 710])
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        button_box.rejected.connect(self.reject);
        self.main_layout.addWidget(button_box)

    def _create_left_pane(self):
        container = QWidget();
        layout = QVBoxLayout(container);
        layout.setContentsMargins(5, 5, 5, 5)
        layout.addWidget(QLabel("<b>Available Themes:</b>"));
        self.theme_list_widget = QListWidget()
        self.theme_list_widget.setAlternatingRowColors(True)
        self.theme_list_widget.currentItemChanged.connect(self._on_theme_selection_changed)
        layout.addWidget(self.theme_list_widget, 1)
        actions_layout = QHBoxLayout();
        self.import_button = QPushButton("Import...")
        self.duplicate_button = QPushButton("Duplicate");
        self.delete_button = QPushButton("Delete")
        self.import_button.clicked.connect(self._action_import_theme)
        self.duplicate_button.clicked.connect(self._action_duplicate_theme)
        self.delete_button.clicked.connect(self._action_delete_theme)
        actions_layout.addWidget(self.import_button);
        actions_layout.addWidget(self.duplicate_button);
        actions_layout.addWidget(self.delete_button)
        layout.addLayout(actions_layout);
        self.splitter.addWidget(container)

    def _create_right_pane(self):
        container = QWidget();
        layout = QVBoxLayout(container);
        layout.setContentsMargins(10, 5, 5, 5)
        form_layout = QGridLayout();
        form_layout.addWidget(QLabel("<b>Theme Name:</b>"), 0, 0)
        self.name_edit = QLineEdit();
        self.name_edit.textChanged.connect(self._mark_unsaved_changes)
        form_layout.addWidget(self.name_edit, 0, 1)
        self.info_label = QLabel();
        self.info_label.setStyleSheet("font-style: italic; color: grey;")
        form_layout.addWidget(self.info_label, 1, 1);
        form_layout.setColumnStretch(1, 1);
        layout.addLayout(form_layout)
        scroll_area = QScrollArea();
        scroll_area.setWidgetResizable(True);
        scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        self.scroll_content = QWidget();
        self.v_scroll_layout = QVBoxLayout(self.scroll_content)
        self.v_scroll_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        scroll_area.setWidget(self.scroll_content);
        layout.addWidget(scroll_area, 1)
        actions_layout = QHBoxLayout();
        self.reset_button = QPushButton("Reset Changes")
        self.update_button = QPushButton("Update Custom Theme");
        self.save_as_new_button = QPushButton("Save as New")
        self.reset_button.clicked.connect(self._load_theme_to_editor);
        self.update_button.clicked.connect(lambda: self._action_save(is_update=True))
        self.save_as_new_button.clicked.connect(lambda: self._action_save(is_update=False))
        actions_layout.addWidget(self.reset_button);
        actions_layout.addStretch()
        actions_layout.addWidget(self.update_button);
        actions_layout.addWidget(self.save_as_new_button)
        layout.addLayout(actions_layout);
        self.splitter.addWidget(container)

    def _action_import_theme(self):
        filepath, _ = QFileDialog.getOpenFileName(self, "Import Theme File", "", "JSON Files (*.json)")
        if not filepath: return

        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                imported_data = json.load(f)

            if not isinstance(imported_data, dict) or not imported_data:
                QMessageBox.warning(self, "Import Failed",
                                    "The selected file is not a valid theme collection (must be a JSON object).");
                return

            custom_themes = {}
            if os.path.exists(CUSTOM_THEMES_FILE_PATH):
                try:
                    with open(CUSTOM_THEMES_FILE_PATH, 'r', encoding='utf-8') as f:
                        custom_themes = json.load(f)
                except (json.JSONDecodeError, OSError):
                    pass

            imported_count = 0

            for theme_key, theme_data in imported_data.items():
                if isinstance(theme_data, dict) and "name" in theme_data and "colors" in theme_data:
                    theme_name = theme_data["name"]
                    theme_id = f"custom_{re.sub('[^a-z0-9_]', '', theme_name.lower())}_{int(datetime.datetime.now().timestamp()) + imported_count}"
                    theme_data["is_custom"] = True

                    custom_themes[theme_id] = theme_data
                    imported_count += 1
                else:
                    log.warning(f"Skipping invalid object in theme file with key '{theme_key}'")

            if imported_count == 0:
                QMessageBox.warning(self, "Import Failed", "No valid themes could be found in the selected file.");
                return

            with open(CUSTOM_THEMES_FILE_PATH, 'w', encoding='utf-8') as f:
                json.dump(custom_themes, f, indent=4)

            theme_manager.reload_themes()
            self.custom_themes_changed.emit()
            self._repopulate_theme_list()
            QMessageBox.information(self, "Success", f"{imported_count} theme(s) were imported successfully.")

        except Exception as e:
            QMessageBox.critical(self, "Import Failed", f"An error occurred during import: {e}")
            log.error(f"Failed to import theme from {filepath}: {e}", exc_info=True)

    def _repopulate_theme_list(self, select_theme_id=None):
        self.theme_list_widget.blockSignals(True);
        self.theme_list_widget.clear()
        all_themes = theme_manager.get_available_themes_for_ui()
        target_row = 0;
        current_selection = select_theme_id or self.current_theme_id
        for i, (theme_id, name) in enumerate(all_themes.items()):
            item = QListWidgetItem(name);
            item.setData(Qt.ItemDataRole.UserRole, theme_id)
            theme_data = theme_manager.get_theme_data_by_id(theme_id)
            if theme_data and theme_data.get("is_custom"): item.setFont(
                QFont(self.font().family(), -1, QFont.Weight.Bold))
            self.theme_list_widget.addItem(item)
            if theme_id == current_selection: target_row = i
        self.theme_list_widget.setCurrentRow(target_row);
        self.theme_list_widget.blockSignals(False)
        self._on_theme_selection_changed(self.theme_list_widget.currentItem(), None)

    def _on_theme_selection_changed(self, current, previous):
        if not current: self._clear_editor(); return
        if self.unsaved_changes and current is not previous:
            if QMessageBox.question(self, "Unsaved Changes", "Discard changes?",
                                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                    QMessageBox.StandardButton.No) == QMessageBox.StandardButton.No:
                self.theme_list_widget.blockSignals(True)
                if previous: self.theme_list_widget.setCurrentItem(previous)
                self.theme_list_widget.blockSignals(False);
                return
        new_theme_id = current.data(Qt.ItemDataRole.UserRole)
        if new_theme_id != self.current_theme_id: self.current_theme_id = new_theme_id; self._load_theme_to_editor()

    def _load_theme_to_editor(self):
        theme_data = theme_manager.get_theme_data_by_id(self.current_theme_id)
        if not theme_data or "colors" not in theme_data: self._clear_editor(); return
        self._clear_layout(self.v_scroll_layout);
        self.color_widgets.clear()
        sorted_keys = sorted(theme_data["colors"].keys())
        self.is_custom_theme = theme_data.get("is_custom", False)
        self.name_edit.setText(theme_data.get("name", ""));
        self.info_label.setText(f"Editing: {theme_data.get('name')}")
        self.unsaved_changes = False;
        self._update_ui_state()

    def _action_duplicate_theme(self):
        pass

    def _action_delete_theme(self):
        pass

    def _action_save(self, is_update):
        pass

    def _mark_unsaved_changes(self):
        self.unsaved_changes = True; self._update_ui_state()

    def _update_ui_state(self):
        has_selection = self.current_theme_id is not None
        self.name_edit.setEnabled(has_selection)
        self.reset_button.setEnabled(has_selection and self.unsaved_changes)
        self.save_as_new_button.setEnabled(has_selection and self.unsaved_changes)
        self.update_button.setEnabled(self.is_custom_theme and self.unsaved_changes)
        self.delete_button.setEnabled(self.is_custom_theme)
        self.duplicate_button.setEnabled(has_selection)

    def _clear_layout(self, layout):
        pass

    def _clear_editor(self):
        pass

    def reject(self):
        if self.unsaved_changes:
            if QMessageBox.question(self, "Unsaved Changes", "Discard changes?",
                                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                    QMessageBox.StandardButton.No) == QMessageBox.StandardButton.Yes:
                super().reject()
        else:
            super().reject()
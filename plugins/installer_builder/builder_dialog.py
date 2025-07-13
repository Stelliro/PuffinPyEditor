import os
import json
from pathlib import Path
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QWidget, QFormLayout, QLineEdit,
                             QPushButton, QTextEdit, QMessageBox, QDialogButtonBox,
                             QHBoxLayout, QFileDialog, QGroupBox, QLabel, QListWidget,
                             QListWidgetItem, QTabWidget, QToolButton)
from PyQt6.QtCore import pyqtSlot, QRunnable, QObject, pyqtSignal, QThreadPool, Qt
from PyQt6.QtGui import QFont
import qtawesome as qta
from .build_logic import BuildLogic
from .component_dialog import ComponentDialog

class WorkerSignals(QObject):
    """Defines signals for the background build worker."""
    log_message = pyqtSignal(str, str)
    finished = pyqtSignal(bool, str)

class BuildWorker(QRunnable):
    """A QRunnable that executes the build process in a separate thread."""
    def __init__(self, config: dict):
        super().__init__()
        self.config = config
        self.signals = WorkerSignals()
        
    @pyqtSlot()
    def run(self):
        logic = BuildLogic(log_callback=self.signals.log_message.emit)
        success, message = logic.run_full_build(self.config)
        self.signals.finished.emit(success, message)

class BuilderDialog(QDialog):
    """The main UI for the Installer Builder plugin."""
    def __init__(self, api, parent=None):
        super().__init__(parent)
        self.api = api
        self.settings = api.get_manager("settings")
        self.theme_manager = api.get_manager("theme")
        self.threadpool = QThreadPool()
        self.config_data = {}
        
        self.setWindowTitle("Installer Builder Suite")
        self.setMinimumSize(850, 750)
        self.main_layout = QVBoxLayout(self)

        self.tabs = QTabWidget()
        self.tabs.addTab(self._create_build_tab(), "Build New Installer")
        self.tabs.addTab(self._create_history_tab(), "Build History")
        self.main_layout.addWidget(self.tabs)
        
        self.tabs.currentChanged.connect(self._on_tab_changed)
        self._load_settings()

    def _on_tab_changed(self, index: int):
        """Refreshes the history list when the user switches to that tab."""
        if self.tabs.tabText(index) == "Build History":
            self._refresh_history()

    # --- Build Tab Creation ---
    def _create_build_tab(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)

        main_group = QGroupBox("1. Core Application Details")
        form = QFormLayout(main_group)
        self.app_name_edit = QLineEdit()
        self.version_edit = QLineEdit()
        self.author_edit = QLineEdit()
        self.source_dir_edit = QLineEdit()
        self.source_dir_edit.textChanged.connect(self._auto_populate_from_source)
        self.main_exe_edit = QLineEdit()
        self.main_exe_edit.setPlaceholderText("e.g., MyApp.exe (must be in source dir)")
        form.addRow("<b>Application Name:</b>", self.app_name_edit)
        form.addRow("<b>Version (e.g., 1.0.0):</b>", self.version_edit)
        form.addRow("<b>Author/Company:</b>", self.author_edit)
        form.addRow("<b>Source Directory:</b>", self._create_browse_field(self.source_dir_edit, "Select App Source Folder", is_file=False))
        form.addRow("<b>Main Executable:</b>", self._create_browse_field(self.main_exe_edit, "Select Main Executable"))
        layout.addWidget(main_group)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.addWidget(self._create_branding_group())
        splitter.addWidget(self._create_components_group())
        layout.addWidget(splitter)
        
        output_group = QGroupBox("3. Build Configuration")
        out_form = QFormLayout(output_group)
        self.output_dir_edit = QLineEdit()
        self.nsis_path_edit = QLineEdit()
        out_form.addRow("<b>Installer Output Dir:</b>", self._create_browse_field(self.output_dir_edit, "Select Output Folder", is_file=False))
        out_form.addRow("<b>NSIS Path (makensis.exe):</b>", self._create_browse_field(self.nsis_path_edit, "Select NSIS Executable"))
        layout.addWidget(output_group)

        log_group = QGroupBox("Build Log")
        log_layout = QVBoxLayout(log_group)
        self.log_output = QTextEdit(); self.log_output.setReadOnly(True)
        log_layout.addWidget(self.log_output)
        layout.addWidget(log_group, 1)

        bottom_buttons = QHBoxLayout()
        self.customize_button = QPushButton("Customize (Advanced)...")
        self.customize_button.clicked.connect(self._edit_config_file)
        self.start_button = QPushButton(qta.icon('fa5s.cogs'), "Generate and Build Installer")
        self.start_button.clicked.connect(self._start_build)
        bottom_buttons.addWidget(self.customize_button)
        bottom_buttons.addStretch()
        bottom_buttons.addWidget(self.start_button)
        layout.addLayout(bottom_buttons)
        return widget
        
    def _create_branding_group(self) -> QGroupBox:
        group = QGroupBox("2a. Branding & Assets")
        form = QFormLayout(group)
        self.license_path_edit = QLineEdit()
        self.installer_icon_edit = QLineEdit()
        self.app_icon_edit = QLineEdit()
        self.app_icon_edit.setPlaceholderText("(Optional) Defaults to main executable's icon.")
        form.addRow("License File:", self._create_browse_field(self.license_path_edit, "Select License File"))
        form.addRow("Installer Icon (.ico):", self._create_browse_field(self.installer_icon_edit, "Select Installer Icon (*.ico)"))
        form.addRow("Shortcut Icon (.ico):", self._create_browse_field(self.app_icon_edit, "Select Shortcut Icon (*.ico)"))
        return group
    
    def _create_components_group(self) -> QGroupBox:
        group = QGroupBox("2b. Optional Install Components")
        layout = QVBoxLayout(group)
        self.components_list = QListWidget()
        layout.addWidget(self.components_list)
        btn_layout = QHBoxLayout()
        add_btn = QToolButton(); add_btn.setToolTip("Add new component"); add_btn.setIcon(qta.icon('fa5s.plus')); add_btn.clicked.connect(self._add_component)
        edit_btn = QToolButton(); edit_btn.setToolTip("Edit selected component"); edit_btn.setIcon(qta.icon('fa5s.pencil-alt')); edit_btn.clicked.connect(self._edit_component)
        remove_btn = QToolButton(); remove_btn.setToolTip("Remove selected component"); remove_btn.setIcon(qta.icon('fa5s.trash-alt')); remove_btn.clicked.connect(self._remove_component)
        btn_layout.addStretch()
        btn_layout.addWidget(add_btn); btn_layout.addWidget(edit_btn); btn_layout.addWidget(remove_btn)
        layout.addLayout(btn_layout)
        return group

    def _create_browse_field(self, line_edit, title, is_file=True):
        widget, layout = QWidget(), QHBoxLayout(); layout.setContentsMargins(0,0,0,0)
        layout.addWidget(line_edit); btn = QPushButton("Browse...")
        handler = lambda: self._browse_for(line_edit, title, is_file)
        btn.clicked.connect(handler); layout.addWidget(btn)
        widget.setLayout(layout)
        return widget

    def _browse_for(self, line_edit, title, is_file):
        start_dir = self.source_dir_edit.text() or self.settings.get("builder_last_src_dir", "")
        if is_file: path, _ = QFileDialog.getOpenFileName(self, title, start_dir)
        else: path = QFileDialog.getExistingDirectory(self, title, start_dir)
        if path: line_edit.setText(os.path.normpath(path))

    # --- History Tab Creation & Management ---
    def _create_history_tab(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        info_label = QLabel("Previously built installers found in your selected output directory.")
        self.history_list = QListWidget()
        self.history_list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.history_list.customContextMenuRequested.connect(self._show_history_context_menu)
        layout.addWidget(info_label); layout.addWidget(self.history_list, 1)
        return widget
        
    def _refresh_history(self):
        self.history_list.clear()
        output_dir = self.output_dir_edit.text().strip() or self.settings.get("builder_last_out_dir", "")
        if not output_dir or not os.path.isdir(output_dir):
            self.history_list.addItem("Set an installer output directory to see history here."); return

        try:
            files = [f for f in os.listdir(output_dir) if f.lower().endswith("_setup.exe")]
            if not files: self.history_list.addItem("No installers found."); return

            for filename in sorted(files, reverse=True):
                path = os.path.join(output_dir, filename)
                item = QListWidgetItem(filename)
                item.setData(Qt.ItemDataRole.UserRole, path)
                item.setIcon(qta.icon('fa5s.archive'))
                self.history_list.addItem(item)
        except OSError as e: self.history_list.addItem(f"Error reading history: {e}")

    def _show_history_context_menu(self, pos):
        item = self.history_list.itemAt(pos)
        if not item or not item.data(Qt.ItemDataRole.UserRole): return
        
        path = item.data(Qt.ItemDataRole.UserRole)
        menu = QMenu()
        menu.addAction("Open Folder Location", lambda: os.startfile(os.path.dirname(path)))
        menu.addAction("Run Installer", lambda: os.startfile(path))
        menu.addSeparator()
        menu.addAction(qta.icon('fa5s.trash-alt', color="red"), "Delete Installer", lambda: self._delete_history_item(item))
        menu.exec(self.history_list.mapToGlobal(pos))
    
    def _delete_history_item(self, item):
        path = item.data(Qt.ItemDataRole.UserRole)
        reply = QMessageBox.question(self, "Confirm Delete", f"Permanently delete {os.path.basename(path)}?")
        if reply == QMessageBox.StandardButton.Yes:
            try: os.remove(path); self._refresh_history()
            except OSError as e: QMessageBox.critical(self, "Error", f"Could not delete file: {e}")

    # --- Configuration and Build Logic ---
    def _generate_config_from_ui(self) -> dict | None:
        try:
            template_path = Path(__file__).parent / "assets" / "config_template.json"
            config = json.loads(template_path.read_text())
            
            # Populate from UI
            config['metadata'].update({ "app_name": self.app_name_edit.text(), "version": self.version_edit.text(), "author": self.author_edit.text(), "main_exe": os.path.basename(self.main_exe_edit.text())})
            config['build'] = {"source_dir": self.source_dir_edit.text(), "output_dir": self.output_dir_edit.text(), "nsis_path": self.nsis_path_edit.text(), "license_path": self.license_path_edit.text(), "installer_icon_path": self.installer_icon_edit.text(), "app_shortcut_icon_path": self.app_icon_edit.text()}
            
            # Reset and add components
            config['components'] = [config['components'][0]] # Keep the main one
            config['components'][0]['description'] = f"Installs the core {config['metadata']['app_name']} files."
            for i in range(self.components_list.count()):
                config['components'].append(self.components_list.item(i).data(Qt.ItemDataRole.UserRole))

            self.config_data = config
            return config
        except Exception as e:
            QMessageBox.critical(self, "Config Error", f"Failed to generate configuration: {e}")
            return None

    def _edit_config_file(self):
        if not self._generate_config_from_ui(): return
            
        dialog = ConfigEditorDialog(self.theme_manager, json.dumps(self.config_data, indent=2), self)
        if dialog.exec():
            try:
                self.config_data = json.loads(dialog.get_text())
                QMessageBox.information(self, "Config Updated", "Installer configuration customized for this build session.")
            except json.JSONDecodeError as e:
                QMessageBox.critical(self, "Invalid JSON", f"Could not apply changes due to a syntax error:\n{e}")

    def _start_build(self):
        if not self.config_data:
            if not self._generate_config_from_ui(): return
        
        # Merge build paths into the config dictionary before starting
        self.config_data['build'] = {"source_dir": self.source_dir_edit.text(), "output_dir": self.output_dir_edit.text(), "nsis_path": self.nsis_path_edit.text(), "license_path": self.license_path_edit.text(), "installer_icon_path": self.installer_icon_edit.text(), "app_shortcut_icon_path": self.app_icon_edit.text()}
        
        # Validation
        for key, name in [("source_dir", "Source Directory"), ("output_dir", "Output Directory"), ("nsis_path", "NSIS Path")]:
            if not self.config_data['build'][key]:
                QMessageBox.warning(self, "Missing Path", f"Please specify the {name}.")
                return

        self._save_settings()
        self.log_output.clear()
        self.tabs.setCurrentIndex(0)
        
        worker = BuildWorker(self.config_data)
        worker.signals.log_message.connect(self.add_log_message)
        worker.signals.finished.connect(self.on_build_finished)
        self.threadpool.start(worker)

    def _load_settings(self):
        self.nsis_path_edit.setText(self.settings.get("builder_nsis_path", ""))
        self.output_dir_edit.setText(self.settings.get("builder_last_out_dir", ""))

    def _save_settings(self):
        self.settings.set("builder_nsis_path", self.nsis_path_edit.text().strip())
        self.settings.set("builder_last_out_dir", self.output_dir_edit.text().strip())

    @pyqtSlot(bool, str)
    def on_build_finished(self, success, message):
        if success:
            self._refresh_history()
            QMessageBox.information(self, "Build Complete", "The application installer was created successfully.")
        else:
            QMessageBox.critical(self, "Build Failed", f"The build process failed.\n\nCheck the log for details.")
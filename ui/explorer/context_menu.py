# PuffinPyEditor/ui/explorer/context_menu.py
import os
from functools import partial
from PyQt6.QtWidgets import QMenu, QApplication, QMessageBox
from PyQt6.QtCore import QPoint
import qtawesome as qta
from app_core.project_manager import ProjectManager


def _copy_to_clipboard(text: str):
    """Helper to put text on the system clipboard."""
    if clip := QApplication.instance().clipboard():
        clip.setText(text)


def show_project_context_menu(panel, position: QPoint, path: str, is_dir: bool, project_manager: ProjectManager):
    """
    Creates and displays the context menu for the project explorer.
    """
    tree = panel.tree_widget
    target_dir = path if is_dir else os.path.dirname(path)

    # Check if a valid item was clicked
    item = tree.itemAt(position)
    is_valid_selection = item is not None
    is_project_root = path in project_manager.get_open_projects()

    menu = QMenu(tree)
    menu.addAction(qta.icon('mdi.file-plus-outline'), "New File...", partial(panel._action_new_file, target_dir))
    menu.addAction(qta.icon('mdi.folder-plus-outline'), "New Folder...", partial(panel._action_new_folder, target_dir))

    if is_valid_selection:
        menu.addSeparator()
        if is_project_root:
            menu.addAction(qta.icon('mdi.folder-remove-outline'), "Close Project",
                           partial(project_manager.close_project, path))
            menu.addSeparator()

        menu.addAction(qta.icon('mdi.pencil-outline'), "Rename...", partial(panel._action_rename, path))
        menu.addAction(qta.icon('mdi.trash-can-outline', color='crimson'), "Delete", partial(panel._action_delete, path))
        menu.addAction(qta.icon('mdi.content-copy'), "Duplicate", partial(panel._action_duplicate, path))
        menu.addSeparator()

        if path.lower().endswith(('.py', '.js', '.cpp', '.c', '.cs')) and not is_dir:
            runner_plugin = panel.api.get_plugin_instance("script_runner")
            if runner_plugin:
                menu.addAction(qta.icon('mdi.play-outline', color='#4CAF50'), "Run Script",
                               lambda: runner_plugin.run_specific_script(path))
                menu.addSeparator()

        abs_path_action = menu.addAction(qta.icon('mdi.link-variant'), "Copy Path")
        abs_path_action.triggered.connect(lambda: _copy_to_clipboard(os.path.normpath(path)))

        project_path = panel.project_manager.get_active_project_path()
        if project_path:
            try:
                relative_path = os.path.relpath(path, start=project_path)
                rel_path_action = menu.addAction(qta.icon('mdi.link-box-variant-outline'), "Copy Relative Path")
                rel_path_action.triggered.connect(lambda: _copy_to_clipboard(relative_path.replace("\\", "/")))
            except ValueError:
                pass

    menu.addSeparator()
    reveal_path = path if is_valid_selection else target_dir
    menu.addAction("Reveal in Explorer", partial(panel.file_handler.reveal_in_explorer, reveal_path))

    menu.exec(tree.viewport().mapToGlobal(position))
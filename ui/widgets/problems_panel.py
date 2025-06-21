from PyQt6.QtWidgets import QTreeWidget, QTreeWidgetItem, QAbstractItemView, QHeaderView
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import QIcon
from utils.logger import log
import os


class ProblemsPanel(QTreeWidget):
    problem_selected = pyqtSignal(str, int, int)

    def __init__(self, parent=None):
        super().__init__(parent)
        log.info("ProblemsPanel initializing...")
        self.setColumnCount(4)
        self.setHeaderLabels(["Description", "File", "Line", "Code"])
        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.setAlternatingRowColors(True)
        self.header().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.header().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.header().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.header().setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        self.setIndentation(12)
        self.itemDoubleClicked.connect(self._on_item_double_clicked)
        log.info("ProblemsPanel initialized as QTreeWidget.")

    def update_problems(self, problems_by_file: dict):
        self.clear()
        self.setSortingEnabled(False)
        for filepath, problems in problems_by_file.items():
            if not problems:
                continue

            file_node = QTreeWidgetItem(self, [f"{os.path.basename(filepath)} ({len(problems)} issues)"])
            file_node.setData(0, Qt.ItemDataRole.UserRole, {'is_file_node': True})
            file_node.setFirstColumnSpanned(True)

            for problem in problems:
                problem_node = QTreeWidgetItem(file_node, [
                    problem.get("description", ""),
                    os.path.basename(filepath),
                    str(problem.get("line", "")),
                    problem.get("code", "")
                ])
                problem_node.setData(0, Qt.ItemDataRole.UserRole, {
                    'filepath': filepath,
                    'line': problem.get("line"),
                    'col': problem.get("col")
                })
        self.expandAll()
        self.setSortingEnabled(True)

    def clear_problems(self):
        self.clear()

    def _on_item_double_clicked(self, item: QTreeWidgetItem, column: int):
        problem_data = item.data(0, Qt.ItemDataRole.UserRole)
        if problem_data and not problem_data.get('is_file_node', False):
            filepath = problem_data.get("filepath")
            line = problem_data.get("line")
            col = problem_data.get("col")
            if filepath and line is not None:
                log.debug(f"Problem selected: Line {line}, Col {col} in {filepath}")
                self.problem_selected.emit(filepath, line, col)
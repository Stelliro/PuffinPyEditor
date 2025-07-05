# PuffinPyEditor/ui/explorer/folder_size_worker.py
import os
from PyQt6.QtCore import QObject, QRunnable, pyqtSignal


class WorkerSignals(QObject):
    finished = pyqtSignal(str, int)


class FolderSizeWorker(QRunnable):
    def __init__(self, path: str):
        super().__init__()
        self.path = path
        self.signals = WorkerSignals()
        self.is_cancelled = False

    def run(self):
        total_size = 0
        try:
            for dirpath, _, filenames in os.walk(self.path, topdown=True, onerror=None):
                if self.is_cancelled:
                    self.signals.finished.emit(self.path, -2)
                    return
                for f in filenames:
                    try:
                        fp = os.path.join(dirpath, f)
                        if not os.path.islink(fp):
                            total_size += os.path.getsize(fp)
                    except (OSError, FileNotFoundError):
                        continue

            if not self.is_cancelled:
                self.signals.finished.emit(self.path, total_size)
        except Exception:
            if not self.is_cancelled:
                self.signals.finished.emit(self.path, -1)

    def cancel(self):
        self.is_cancelled = True
from typing import Callable, Generic, Set, TypeVar

from PySide6.QtCore import QMutex, QObject, QRunnable, QThreadPool, Signal

T = TypeVar("T")

class WorkerSignals(QObject):
    finished = Signal(object)
    failed = Signal(Exception)
    cleanup = Signal(object)

# https://www.pythonguis.com/tutorials/multithreading-pyqt-applications-qthreadpool/
# https://stackoverflow.com/questions/13909195/how-run-two-different-threads-simultaneously-in-pyqt

class GeneralWorker(QRunnable, Generic[T]):
    def __init__(self, runnable_fn: Callable[[], T]):
        super().__init__()
        self._runnable_fn = runnable_fn
        self.signals = WorkerSignals()

    def run(self):
        try:
            result = self._runnable_fn()
            self.signals.finished.emit(result)
        except Exception as error:
            self.signals.failed.emit(error)
        finally:
            self.signals.cleanup.emit(self)

class AsyncWorker:
    def __init__(self):
        self.pool = QThreadPool()
        self.mutex = QMutex()
        # self.working_resources: Set[str] = set() used for exclusive on a unique resource
        self.workers: Set[QRunnable] = set()

    def run(self, runnable_fn, finished = None):
        def _cleanup(identifier: QRunnable):
            self.mutex.lock()
            self.workers.remove(identifier)
            self.mutex.unlock()

        worker = GeneralWorker(runnable_fn)
        if finished:
            worker.signals.finished.connect(finished)
        worker.signals.cleanup.connect(_cleanup)
        self.mutex.lock()
        self.workers.add(worker)
        self.mutex.unlock()
        self.pool.start(worker)
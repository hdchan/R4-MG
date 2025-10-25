import time
from typing import Any, Callable, Dict, TypeVar, Set

from PySide6.QtCore import QObject, QRunnable, QThreadPool, Signal

T = TypeVar("T")

class DataFetcherLocal:

    class Configuration:
        def __init__(self, network_delay_duration: int = 0):
            self.network_delay_duration = network_delay_duration
    
    def __init__(self, 
                 configuration: 'DataFetcherLocal.Configuration'):
        self._configuration = configuration
        self.pool = QThreadPool()
        self.workers: Set[QRunnable] = set()
        
    def load(self, fn_work: Callable[[Dict[str, Any]], T], callback: Callable[[T], None], **kwargs: Any):
        def _cleanup(identifier: QRunnable):
            self.workers.remove(identifier)

        worker = RunnableWorker(fn_work, self._configuration.network_delay_duration, **kwargs)
        worker.signals.finished.connect(callback)
        worker.signals.cleanup.connect(_cleanup)
        self.workers.add(worker)
        self.pool.start(worker)
    
class WorkerSignals(QObject):
    finished = Signal(object)
    cleanup = Signal(object)

class RunnableWorker(QRunnable):
    def __init__(self, 
                 fn_work: Callable[[Dict[str, Any]], T], 
                 delay: int, 
                 **kwargs: Any):
        super(RunnableWorker, self).__init__()
        self._fn_work = fn_work
        self._delay = delay
        self._kwargs = kwargs
        self.signals = WorkerSignals()

    def run(self):
        time.sleep(self._delay)
        result = self._fn_work(self._kwargs)
        self.signals.finished.emit(result)
        self.signals.cleanup.emit(self)
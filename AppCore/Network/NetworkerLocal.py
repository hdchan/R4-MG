import time
from functools import partial
from typing import Callable, TypeVar, Dict, Any

from PyQt5.QtCore import QObject, QRunnable, QThread, QThreadPool, pyqtSignal

from AppCore.Config import ConfigurationManager

T = TypeVar("T")

class NetworkerLocal:
    
    def __init__(self, 
                 configuration_manager: ConfigurationManager):
        self.configuration_manager = configuration_manager
        self.pool = QThreadPool()

    class ClientWorker(QObject):
        finished = pyqtSignal()
        
        def load(self, delay: int):
            time.sleep(delay) # for debugging
            self.finished.emit()
        
    def load_mock(self, callback: Callable[..., None]):
        thread = QThread()
        worker = NetworkerLocal.ClientWorker()
        worker.moveToThread(thread)
        thread.started.connect(partial(worker.load, self.configuration_manager.configuration.network_delay_duration))
        worker.finished.connect(callback)
        worker.finished.connect(thread.quit)
        worker.finished.connect(worker.deleteLater)
        thread.finished.connect(thread.deleteLater)
        self.latest_thread = thread
        thread.start()
        
        
    def load(self, fn_work: Callable[[Dict[str, Any]], T], callback: Callable[[T], None], **kwargs: Any):
        worker = StoreImageWorker(fn_work, self.configuration_manager.configuration.network_delay_duration, **kwargs)
        worker.signals.finished.connect(callback)
        self.pool.start(worker)

    
class WorkerSignals(QObject):
    finished = pyqtSignal(object)

class StoreImageWorker(QRunnable):
    def __init__(self, fn_work: Callable[[Dict[str, Any]], T], delay: int, **kwargs: Any):
        super(StoreImageWorker, self).__init__()
        self._fn_work = fn_work
        self._delay = delay
        self._kwargs = kwargs
        self.signals = WorkerSignals()

    def run(self):
        time.sleep(self._delay)
        result = self._fn_work(self._kwargs)
        self.signals.finished.emit(result)
import time
from functools import partial
from typing import Callable, TypeVar

from PyQt5.QtCore import QObject, QThread, pyqtSignal

from AppCore.Config import ConfigurationManager

from .NetworkerProtocol import (NetworkerProtocol, NetworkerProtocolCallback,
                                NetworkRequestProtocol)

T = TypeVar("T")

class LocalNetworker(NetworkerProtocol):
    
    def __init__(self, 
                 configuration_manager: ConfigurationManager):
        self.configuration_manager = configuration_manager

    class ClientWorker(QObject):
        finished = pyqtSignal()
        
        def load(self, delay: int):
            time.sleep(delay) # for debugging
            self.finished.emit()
    
    def load(self, request: NetworkRequestProtocol[T], callback: NetworkerProtocolCallback[T]):
        raise Exception()
        
        
    def load_mock(self, callback: Callable[..., None]):
        thread = QThread()
        worker = LocalNetworker.ClientWorker()
        worker.moveToThread(thread)
        thread.started.connect(partial(worker.load, self.configuration_manager.configuration.network_delay_duration))
        worker.finished.connect(callback)
        worker.finished.connect(thread.quit)
        worker.finished.connect(worker.deleteLater)
        thread.finished.connect(thread.deleteLater)
        self.latest_thread = thread
        thread.start()
import json
import time
from functools import partial
from typing import Any, Dict, Optional, Tuple, TypeVar
from urllib.request import Request, urlopen

from PyQt5.QtCore import QObject, QThread, pyqtSignal

from .NetworkerProtocol import NetworkerProtocol, NetworkerProtocolCallback
from .NetworkRequestProtocol import NetworkRequestProtocol

T = TypeVar("T")

class Networker(NetworkerProtocol):
    class ClientWorker(QObject):
        finished = pyqtSignal()
        result_available = pyqtSignal(object)

        def __init__(self, delay: int):
            super().__init__()
            self.delay = delay

        def load(self, request: Request):
            try:
                time.sleep(self.delay) # for debugging
                response = urlopen(request)
                json_response = json.load(response)
                self.result_available.emit((json_response, None))
                self.finished.emit()
            except Exception as error:
                self.result_available.emit((None, error))
                self.finished.emit()
    
    def load(self, request: NetworkRequestProtocol[T], callback: NetworkerProtocolCallback[T]):
        def completed_search(result: Tuple[Optional[Dict[str, Any]], Exception]):
            json_response, error = result
            if json_response is not None:
                decoded_response = request.response(json_response)
                callback((decoded_response, error))
            else:
                callback((None, error))
            
        thread = QThread()
        worker = Networker.ClientWorker(self.configuration.network_delay_duration)
        worker.moveToThread(thread)
        thread.started.connect(partial(worker.load, request.request()))
        worker.result_available.connect(completed_search)
        worker.finished.connect(thread.quit)
        worker.finished.connect(worker.deleteLater)
        thread.finished.connect(thread.deleteLater)
        self.latest_thread = thread
        thread.start()
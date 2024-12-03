import json
import time
from functools import partial
from typing import Any, Dict, Optional, Tuple, TypeVar
from urllib.request import Request, urlopen

from PyQt5.QtCore import QObject, QThread, pyqtSignal

from .NetworkerProtocol import NetworkerProtocol, NetworkerProtocolCallback
from .NetworkRequestProtocol import NetworkRequestProtocol
import io
T = TypeVar("T")

class RemoteNetworker(NetworkerProtocol):
    class ClientWorker(QObject):
        finished = pyqtSignal()
        progress_available = pyqtSignal(float)
        result_available = pyqtSignal(object)

        def __init__(self, delay: int):
            super().__init__()
            self.delay = delay

        def load(self, request: Optional[Request]):
            if request is None:
                self.result_available.emit((None, Exception("Invalid request")))
                self.finished.emit()
                return
            try:
                time.sleep(self.delay) # for debugging
                # with urlopen(request) as response:
                #     total_size = int(response.headers.get('Content-Length', 0))
                #     downloaded = 0
                #     buf = io.BytesIO()
                #     while True:
                #         chunk = response.read()
                #         downloaded += len(chunk)
                #         self.progress_available.emit(downloaded / total_size)
                #         if not chunk:
                #             break
                #         buf.write(chunk)
                # json_response = json.loads(buf.getvalue())
                buf = urlopen(request)
                json_response = json.load(buf)
                self.result_available.emit((json_response, None))
                self.finished.emit()
            except Exception as error:
                self.result_available.emit((None, error))
                self.finished.emit()
    
    def load(self, request: NetworkRequestProtocol[T], callback: NetworkerProtocolCallback[T]):
        def progress_available(progress: float):
            print(progress)
            
        def completed_request(result: Tuple[Optional[Dict[str, Any]], Optional[Exception]]):
            json_response, error = result
            if json_response is not None:
                decoded_response = request.response(json_response)
                callback((decoded_response, error))
            else:
                callback((None, error))
            
        thread = QThread()
        worker = self.ClientWorker(self.configuration_provider.configuration.network_delay_duration)
        worker.moveToThread(thread)
        thread.started.connect(partial(worker.load, request.request()))
        worker.progress_available.connect(progress_available)
        worker.result_available.connect(completed_request)
        worker.finished.connect(thread.quit)
        worker.finished.connect(worker.deleteLater)
        thread.finished.connect(thread.deleteLater)
        self.latest_thread = thread
        thread.start()
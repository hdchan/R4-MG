import json
import time
from typing import Any, Callable, Dict, Generic, Optional, Set, Tuple, TypeVar
from urllib.request import urlopen

from PySide6.QtCore import QObject, QRunnable, QThreadPool, Signal

from .DataFetcherRemoteRequestProtocol import DataFetcherRemoteRequestProtocol

T = TypeVar("T")

DataFetcherRemoteCallback = Callable[[Tuple[Optional[T], Optional[Exception]]], None]

class DataFetcherRemote:

    class Configuration:
        def __init__(self, network_delay_duration: int = 0):
            self.network_delay_duration = network_delay_duration

    def __init__(self, 
                 configuration: 'DataFetcherRemote.Configuration' = Configuration()):
        self._configuration = configuration
        self.pool = QThreadPool()
        self.workers: Set[QRunnable] = set()
    
    def load(self, request: DataFetcherRemoteRequestProtocol[T], callback: DataFetcherRemoteCallback[T]):
        def progress_available(progress: float):
            print(progress)
            
        def completed_request(result: Tuple[Optional[Dict[str, Any]], Optional[Exception]]):
            json_response, error = result
            if json_response is not None:
                decoded_response = request.response(json_response)
                callback((decoded_response, error))
            else:
                callback((None, error))

        def _cleanup(identifier: QRunnable):
            self.workers.remove(identifier)
        
        def _runnable_fn() -> Tuple[Optional[Dict[str, Any]], Optional[Exception]]:
            actual_request = request.request()
            if actual_request is None:
                return (None, Exception("Invalid request"))
            try:
                time.sleep(self._configuration.network_delay_duration) # for debugging
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
                # print(request.full_url)
                print(actual_request.headers)
                buf = urlopen(actual_request)
                json_response = json.load(buf)
                return (json_response, None)
            except Exception as error:
                return (None, error)

        worker = GeneralWorker(_runnable_fn)
        worker.signals.finished.connect(completed_request)
        worker.signals.cleanup.connect(_cleanup)
        self.workers.add(worker)
        self.pool.start(worker)


class WorkerSignals(QObject):
    finished = Signal(object)
    failed = Signal(Exception)
    cleanup = Signal(object)


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
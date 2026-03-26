import time
from typing import Any, Callable, Dict, TypeVar

from AppCore.Service.GeneralWorker import AsyncWorker

T = TypeVar("T")

class DataFetcherLocal:

    class Configuration:
        def __init__(self, network_delay_duration: int = 0):
            self.network_delay_duration = network_delay_duration
    
    def __init__(self, 
                 configuration: Configuration = Configuration()):
        self._configuration = configuration
        self._async_worker = AsyncWorker()
        
    def load(self, fn_work: Callable[[Dict[str, Any]], T], callback: Callable[[T], None], **kwargs: Any):
        def _runnable_fn():
            time.sleep(self._configuration.network_delay_duration)
            return fn_work(kwargs)

        self._async_worker.run(_runnable_fn, callback)
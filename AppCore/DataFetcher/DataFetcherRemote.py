import json
from typing import Any, Dict, Optional, Tuple, TypeVar
from urllib.request import urlopen

from .DataFetcherRemoteRequestProtocol import DataFetcherRemoteRequestProtocol

T = TypeVar("T")

DataFetcherRemoteResult = Tuple[Optional[T], Optional[Exception]]

class DataFetcherRemote:

    class Configuration:
        def __init__(self, network_delay_duration: int = 0):
            self.network_delay_duration = network_delay_duration

    def __init__(self, 
                 configuration: Configuration = Configuration()):
        self._configuration = configuration

    def load_with_result(self, request: DataFetcherRemoteRequestProtocol[T]) -> DataFetcherRemoteResult[T]:
        
        def completed_request(result: Tuple[Optional[Dict[str, Any]], Optional[Exception]]):
            json_response, error = result
            if json_response is not None:
                decoded_response = request.response(json_response)
                return ((decoded_response, error))
            else:
                return ((None, error))

        def _runnable_fn() -> Tuple[Optional[Dict[str, Any]], Optional[Exception]]:
            actual_request = request.request()
            if actual_request is None:
                return (None, Exception("Invalid request"))
            try:
                # time.sleep(self._configuration.network_delay_duration) # for debugging
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
        return completed_request(_runnable_fn())
from typing import Any, Generic, TypeVar
from urllib.request import Request

T = TypeVar("T")

class DataFetcherRemoteRequestProtocol(Generic[T]):
    def request(self) -> Request | None:
        raise NotImplementedError
    
    def response(self, json: dict[str, Any]) -> T:
        raise NotImplementedError
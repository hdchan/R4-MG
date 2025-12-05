
from typing import Any, Dict, Generic, Optional, TypeVar
from urllib.request import Request

T = TypeVar("T")

class DataFetcherRemoteRequestProtocol(Generic[T]):
    def request(self) -> Optional[Request]:
        raise NotImplementedError
    
    def response(self, json: Dict[str, Any]) -> T:
        raise NotImplementedError
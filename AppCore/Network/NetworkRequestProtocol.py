
from typing import Any, Dict, Generic, TypeVar
from urllib.request import Request

T = TypeVar("T")

class NetworkRequestProtocol(Generic[T]):
    def request(self) -> Request:
        raise Exception()
    
    def response(self, json: Dict[str, Any]) -> T:
        raise Exception()
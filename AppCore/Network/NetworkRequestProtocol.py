
from typing import Any, Dict, Generic, Optional, TypeVar
from urllib.request import Request

T = TypeVar("T")

class NetworkRequestProtocol(Generic[T]):
    def request(self) -> Optional[Request]:
        return NotImplemented
    
    def response(self, json: Dict[str, Any]) -> T:
        return NotImplemented
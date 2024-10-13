from ..Config import Configuration
from typing import TypeVar, Optional, Callable, Tuple
from .NetworkRequestProtocol import NetworkRequestProtocol

T = TypeVar("T")
NetworkerProtocolCallback = Callable[[Tuple[Optional[T], Optional[Exception]]], None]

class NetworkerProtocol:
    
    def __init__(self, configuration: Configuration):
        self.configuration = configuration
    
    def load(self, request: NetworkRequestProtocol[T], callback: NetworkerProtocolCallback[T]) -> None:
        raise Exception
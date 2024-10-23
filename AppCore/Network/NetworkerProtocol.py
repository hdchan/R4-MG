from ..Config import ConfigurationProvider
from typing import TypeVar, Optional, Callable, Tuple
from .NetworkRequestProtocol import NetworkRequestProtocol

T = TypeVar("T")
NetworkerProtocolCallback = Callable[[Tuple[Optional[T], Optional[Exception]]], None]

class NetworkerProtocol:
    def __init__(self, 
                 configuration_provider: ConfigurationProvider):
        self.configuration_provider = configuration_provider
    
    def load(self, request: NetworkRequestProtocol[T], callback: NetworkerProtocolCallback[T]) -> None:
        raise Exception
from typing import Callable, Optional, Tuple, TypeVar

from .NetworkRequestProtocol import NetworkRequestProtocol

T = TypeVar("T")
NetworkerProtocolCallback = Callable[[Tuple[Optional[T], Optional[Exception]]], None]

class NetworkerProtocol:
    def load(self, request: NetworkRequestProtocol[T], callback: NetworkerProtocolCallback[T]) -> None:
        raise Exception
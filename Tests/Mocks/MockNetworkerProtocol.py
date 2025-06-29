from typing import TypeVar

from AppCore.DataFetcher import (NetworkerProtocol, NetworkerProtocolCallback,
                             NetworkRequestProtocol)

T = TypeVar("T")

class NetworkerLocalProtocol(NetworkerProtocol):
    
    def __init__(self):
        self.load_invocations = []
    
    def load(self, request: NetworkRequestProtocol[T], callback: NetworkerProtocolCallback[T]) -> None:
        self.load_invocations.append({"request": request, 
                                      "callback": callback})
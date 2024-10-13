from typing import Callable, List, Tuple

from ..Models.TradingCard import *
from ..Network import NetworkerProtocol

APIClientSearchCallback = Callable[[Tuple[Optional[List[TradingCard]], Optional[Exception]]], None]

class APIClientProtocol:
    def __init__(self, networker: NetworkerProtocol):
        self.netorker = networker
        
    def search(self, query: str, callback: APIClientSearchCallback) -> None:
        raise Exception()
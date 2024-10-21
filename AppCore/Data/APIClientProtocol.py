from typing import Callable, List, Tuple, Optional

from ..Models import TradingCard, SearchConfiguration
from ..Network import NetworkerProtocol

APIClientSearchCallback = Callable[[Tuple[Optional[List[TradingCard]], Optional[Exception]]], None]

class APIClientProtocol:
    def __init__(self, networker: NetworkerProtocol):
        self.netorker = networker
        
    def search(self, card_name: str, search_configuration: SearchConfiguration, callback: APIClientSearchCallback) -> None:
        raise Exception()
from typing import Callable, List, Tuple, Optional

from ..Models import TradingCard, SearchConfiguration
from ..Network import NetworkerProtocol

APIClientSearchCallback = Callable[[Tuple[Optional[List[TradingCard]], Optional[Exception]]], None]

class APIClientProtocol:
    def __init__(self, networker: NetworkerProtocol):
        self.netorker = networker

    @property
    def site_source_url(self) -> str:
        return NotImplemented
        
    def search(self, search_configuration: SearchConfiguration, callback: APIClientSearchCallback) -> None:
        raise Exception()
    
class APIClientProviderProtocol:
    def provideClient(self) -> APIClientProtocol:
        return NotImplemented
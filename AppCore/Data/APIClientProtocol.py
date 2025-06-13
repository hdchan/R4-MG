from typing import Callable, List, Optional, Tuple

from AppCore.Models import PaginationConfiguration, SearchConfiguration, TradingCard

class APIClientSearchResponse:
    def __init__(self, 
                 trading_card_list: List[TradingCard],
                 page: int = 1, 
                 page_count: int = 1):
        self.trading_card_list = trading_card_list
        self.page = page
        self.page_count = page_count

APIClientSearchResult = Tuple[Optional[APIClientSearchResponse], Optional[Exception]]
APIClientSearchCallback = Callable[[APIClientSearchResult], None]
class APIClientProtocol:

    @property
    def source_display_name(self) -> str:
        return NotImplemented

    @property
    def site_source_url(self) -> Optional[str]:
        return None
        
    def search(self, 
               search_configuration: SearchConfiguration,
               pagination_configuration: PaginationConfiguration,
               callback: APIClientSearchCallback) -> None:
        raise Exception()
    
class APIClientProviding:
    @property
    def client(self) -> APIClientProtocol:
        return NotImplemented
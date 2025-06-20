from typing import Callable, List, Optional, Tuple
from AppCore.Config import Configuration
from AppCore.Models import (PaginationConfiguration, SearchConfiguration,
                            TradingCard)


class DataSourceCardSearchClientSearchResponse:
    def __init__(self, 
                 trading_card_list: List[TradingCard],
                 page: int = 1, 
                 page_count: int = 1):
        self.trading_card_list = trading_card_list
        self.page = page
        self.page_count = page_count

DataSourceCardSearchClientSearchResult = Tuple[Optional[DataSourceCardSearchClientSearchResponse], Optional[Exception]]
DataSourceCardSearchClientSearchCallback = Callable[[DataSourceCardSearchClientSearchResult], None]

class DataSourceCardSearchClientProtocol:

    @property
    def source_display_name(self) -> str:
        return NotImplemented

    @property
    def site_source_url(self) -> Optional[str]:
        return None
        
    def search(self, 
               search_configuration: SearchConfiguration,
               pagination_configuration: PaginationConfiguration,
               callback: DataSourceCardSearchClientSearchCallback) -> None:
        raise Exception()
    
class DataSourceCardSearchClientProviding:
    def client(self, setting: Configuration.Settings.SearchSource) -> DataSourceCardSearchClientProtocol:
        return NotImplemented
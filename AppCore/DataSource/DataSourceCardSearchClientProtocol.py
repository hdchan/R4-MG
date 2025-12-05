from typing import Callable, List, Optional, Tuple

from AppCore.Models import PaginationConfiguration, SearchConfiguration, TradingCard


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
        raise NotImplementedError

    @property
    def can_auto_search(self) -> bool:
        return False

    @property
    def site_source_url(self) -> Optional[str]:
        return None

    def search_with_result(self, 
               search_configuration: SearchConfiguration,
               pagination_configuration: PaginationConfiguration) -> DataSourceCardSearchClientSearchResult:
        raise Exception
    
class DataSourceCardSearchClientProviding:
    @property
    def search_client(self) -> DataSourceCardSearchClientProtocol:
        raise NotImplementedError
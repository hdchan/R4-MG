from typing import Optional

from AppCore.DataSource.DataSourceCardSearchClientProtocol import (DataSourceCardSearchClientProtocol,
                                            DataSourceCardSearchClientSearchCallback)
from AppCore.Models import PaginationConfiguration, SearchConfiguration
from AppCore.DataFetcher import DataFetcherRemote

from ..SWUCardSearchConfiguration import SWUCardSearchConfiguration
from .SearchRequest import SearchRequest


# https://stackoverflow.com/a/33453124
# suggests using move to thread
class SWUDBAPIRemoteClient(DataSourceCardSearchClientProtocol):

    def __init__(self, networker: DataFetcherRemote):
        self._networker = networker

    @property
    def source_display_name(self) -> str:
        return "https://www.swu-db.com/"

    @property
    def site_source_url(self) -> str:
        return "https://www.swu-db.com/"

    def search(self, 
               search_configuration: SearchConfiguration,
               pagination_configuration: Optional[PaginationConfiguration],
               callback: DataSourceCardSearchClientSearchCallback):
        print(f'Remote search www.swu-db.com. card_name: {search_configuration.card_name}, search_configuration: {search_configuration}')
        swu_search_config = SWUCardSearchConfiguration.from_search_configuration(search_configuration)
        self._networker.load(SearchRequest(swu_search_config), callback)
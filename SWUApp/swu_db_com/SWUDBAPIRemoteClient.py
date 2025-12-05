from typing import Optional

from AppCore.DataFetcher import DataFetcherRemote
from AppCore.DataSource.DataSourceCardSearchClientProtocol import (
    DataSourceCardSearchClientProtocol,
    DataSourceCardSearchClientSearchResult,
)
from AppCore.Models import PaginationConfiguration, SearchConfiguration

from ..Models.SWUCardSearchConfiguration import SWUCardSearchConfiguration
from ..SWUAppDependenciesProviding import SWUAppDependenciesProviding
from .SearchIdentifierRequest import SearchIdentifierRequest
from .SearchNameRequest import SearchNameRequest

class SWUDBAPIRemoteClient(DataSourceCardSearchClientProtocol):

    def __init__(self, 
                 swu_app_dependencies_provider: SWUAppDependenciesProviding,
                 remote_data_fetcher: DataFetcherRemote):
        self._swu_app_dependencies_provider = swu_app_dependencies_provider
        self._remote_data_fetcher = remote_data_fetcher

    @property
    def source_display_name(self) -> str:
        return "https://www.swu-db.com/"

    @property
    def site_source_url(self) -> str:
        return "https://www.swu-db.com/"

    def search_with_result(self, 
               search_configuration: SearchConfiguration,
               pagination_configuration: Optional[PaginationConfiguration]) -> DataSourceCardSearchClientSearchResult:
        print(f'Remote search www.swu-db.com. card_name: {search_configuration.card_name}, search_configuration: {search_configuration}')
        swu_search_config = SWUCardSearchConfiguration.from_search_configuration(search_configuration)

        if swu_search_config.card_set is not None and swu_search_config.card_number is not None:
            return self._remote_data_fetcher.load_with_result(SearchIdentifierRequest(swu_search_config))
        else:
            return self._remote_data_fetcher.load_with_result(SearchNameRequest(swu_search_config))
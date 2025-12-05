from AppCore.DataSource.DataSourceCardSearchClientProtocol import (DataSourceCardSearchClientProtocol,
                                            DataSourceCardSearchClientSearchResult,
                                            )
from AppCore.DataFetcher import DataFetcherRemote
from AppCore.Models import PaginationConfiguration, SearchConfiguration
from ..Assets import AssetProvider
from ..Models.SWUCardSearchConfiguration import SWUCardSearchConfiguration
from .SearchRequest import SearchRequest


class SearchClient(DataSourceCardSearchClientProtocol):

    def __init__(self, 
                 remote_data_fetcher: DataFetcherRemote, 
                 asset_provider: AssetProvider):
        self._remote_data_fetcher = remote_data_fetcher
        self._asset_provider = asset_provider

    @property
    def source_display_name(self) -> str:
        return "https://www.starwarsunlimited.com/"

    @property
    def site_source_url(self) -> str:
        return "www.starwarsunlimited.com"

    def search_with_result(self, 
               search_configuration: SearchConfiguration,
               pagination_configuration: PaginationConfiguration) -> DataSourceCardSearchClientSearchResult:
        swu_search_config = SWUCardSearchConfiguration.from_search_configuration(search_configuration)
        return self._remote_data_fetcher.load_with_result(SearchRequest(swu_search_config, pagination_configuration, self._asset_provider))
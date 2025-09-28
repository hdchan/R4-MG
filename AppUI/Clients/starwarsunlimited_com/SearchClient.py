from AppCore.DataSource.DataSourceCardSearchClientProtocol import (DataSourceCardSearchClientProtocol,
                                            DataSourceCardSearchClientSearchCallback,
                                            )
from AppCore.DataFetcher import DataFetcherRemote
from AppCore.Models import PaginationConfiguration, SearchConfiguration
from ..Assets import AssetProvider
from ..Models.SWUCardSearchConfiguration import SWUCardSearchConfiguration
from .SearchRequest import SearchRequest


class SearchClient(DataSourceCardSearchClientProtocol):

    def __init__(self, networker: DataFetcherRemote, 
                 asset_provider: AssetProvider):
        self._networker = networker
        self._asset_provider = asset_provider

    @property
    def source_display_name(self) -> str:
        return "https://www.starwarsunlimited.com/"

    @property
    def site_source_url(self) -> str:
        return "www.starwarsunlimited.com"

    def search(self, 
               search_configuration: SearchConfiguration,
               pagination_configuration: PaginationConfiguration,
               callback: DataSourceCardSearchClientSearchCallback):
        swu_search_config = SWUCardSearchConfiguration.from_search_configuration(search_configuration)
        self._networker.load(SearchRequest(swu_search_config, pagination_configuration, self._asset_provider), callback)
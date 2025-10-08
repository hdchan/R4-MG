from typing import Optional

from AppCore.DataSource.DataSourceCardSearchClientProtocol import (DataSourceCardSearchClientProtocol,
                                            DataSourceCardSearchClientSearchCallback, DataSourceCardSearchClientSearchResult)
from AppCore.Models import PaginationConfiguration, SearchConfiguration
from AppCore.DataFetcher import DataFetcherRemote

from ..Models.SWUCardSearchConfiguration import SWUCardSearchConfiguration
from .SearchNameRequest import SearchNameRequest
from .SearchIdentifierRequest import SearchIdentifierRequest
from ..SWUAppDependenciesProviding import SWUAppDependenciesProviding

# https://stackoverflow.com/a/33453124
# suggests using move to thread
class SWUDBAPIRemoteClient(DataSourceCardSearchClientProtocol):

    def __init__(self, 
                 swu_app_dependencies_provider: SWUAppDependenciesProviding,
                 networker: DataFetcherRemote = DataFetcherRemote()):
        self._swu_app_dependencies_provider = swu_app_dependencies_provider
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

        def _handle_callback(result: DataSourceCardSearchClientSearchResult):
            # TODO: cache result
            callback(result)

        if swu_search_config.card_set is not None and swu_search_config.card_number is not None:
            self._networker.load(SearchIdentifierRequest(swu_search_config), _handle_callback)
        else:
            self._networker.load(SearchNameRequest(swu_search_config), _handle_callback)
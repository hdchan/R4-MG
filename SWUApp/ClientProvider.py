from AppCore.DataFetcher import DataFetcherLocal, DataFetcherRemote
from AppCore.DataSource import (DataSourceCardSearchClientProtocol,
                                DataSourceCardSearchClientProviding,
                                DataSourceLocallyManagedSets)

from . import starwarsunlimited_com, swu_db_com
from .Config.SWUAppConfiguration import SWUAppConfiguration
from .SWUAppDependenciesProviding import SWUAppDependenciesProviding


class ClientProvider(DataSourceCardSearchClientProviding):
    
    def __init__(self,
                 swu_app_dependencies_provider: SWUAppDependenciesProviding,
                 local_managed_sets: DataSourceLocallyManagedSets):
        self._swu_app_dependencies_provider = swu_app_dependencies_provider
        remote_data_fetcher = DataFetcherRemote(DataFetcherRemote.Configuration(self._swu_app_dependencies_provider.configuration_manager.configuration.core_configuration.network_delay_duration))
        local_data_fetcher = DataFetcherLocal(DataFetcherLocal.Configuration(self._swu_app_dependencies_provider.configuration_manager.configuration.core_configuration.network_delay_duration))
        internal_asset_provider = self._swu_app_dependencies_provider.asset_provider
        self._swu_db_search = swu_db_com.SWUDBAPIRemoteClient(swu_app_dependencies_provider, 
                                                              remote_data_fetcher)
        self._local_search = swu_db_com.SWUDBAPILocalClient(local_data_fetcher, 
                                                            internal_asset_provider)
        self._locally_managed_deck_search = swu_db_com.SWUDBLocalCardRetrieverClient(local_data_fetcher, 
                                                                                     local_managed_sets)
        self._starwarsunlimited_search = starwarsunlimited_com.SearchClient(remote_data_fetcher, 
                                                                            internal_asset_provider)

    @property
    def search_client(self) -> DataSourceCardSearchClientProtocol:
        setting = self._swu_app_dependencies_provider.configuration_manager.configuration.search_source
        if setting == SWUAppConfiguration.SearchSource.LOCALLY_MANAGED_DECKS:
            return self._locally_managed_deck_search
        elif setting == SWUAppConfiguration.SearchSource.LOCAL: # TODO: deprecate
            return self._local_search
        elif setting == SWUAppConfiguration.SearchSource.STARWARSUNLIMITED_FFG:
            return self._starwarsunlimited_search
        
        return self._swu_db_search
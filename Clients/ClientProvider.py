from AppCore.Config import Configuration
from AppCore.DataFetcher import DataFetcherLocal, DataFetcherRemote
from AppCore.DataSource import (DataSourceCardSearchClientProtocol,
                                DataSourceCardSearchClientProviding,
                                DataSourceLocallyManagedSets)
from AppUI.Assets import AssetProvider
from .Assets import AssetProvider as InternalAssetProvider
from . import starwarsunlimited_com, swu_db_com


class ClientProvider(DataSourceCardSearchClientProviding):
    
    class Dependencies:
        def __init__(self,
                     asset_provider: AssetProvider,
                     intern_asset_provider: InternalAssetProvider,
                     remote_networker: DataFetcherRemote, 
                     local_networker: DataFetcherLocal, 
                     local_managed_sets: DataSourceLocallyManagedSets):
            self.asset_provider = asset_provider
            self.internal_asset_provider = intern_asset_provider
            self.remote_networker = remote_networker
            self.local_networker = local_networker
            self.local_managed_sets = local_managed_sets
    
    def __init__(self, dependencies: Dependencies):
        self._swu_db_search = swu_db_com.SWUDBAPIRemoteClient(dependencies.remote_networker)
        self._local_search = swu_db_com.SWUDBAPILocalClient(dependencies.local_networker, 
                                                            dependencies.internal_asset_provider)
        self._locally_managed_deck_search = swu_db_com.SWUDBLocalCardRetrieverClient(dependencies.local_networker, 
                                                                                     dependencies.local_managed_sets)
        self._starwarsunlimited_search = starwarsunlimited_com.SearchClient(dependencies.remote_networker, 
                                                                            dependencies.internal_asset_provider)
    
    def client(self, setting: Configuration.Settings.SearchSource) -> DataSourceCardSearchClientProtocol:
        if setting == Configuration.Settings.SearchSource.LOCALLY_MANAGED_DECKS:
            return self._locally_managed_deck_search
        elif setting == Configuration.Settings.SearchSource.LOCAL: # TODO: deprecate
            return self._local_search
        elif setting == Configuration.Settings.SearchSource.STARWARSUNLIMITED_FFG:
            return self._starwarsunlimited_search
        
        return self._swu_db_search
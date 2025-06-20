from AppCore.Config import Configuration
from AppCore.DataFetcher import DataFetcherLocal, DataFetcherRemote
from AppCore.DataSource import (DataSourceCardSearchClientProtocol,
                                DataSourceCardSearchClientProviding,
                                DataSourceLocallyManagedSets)
from AppCore.Observation import ObservationTower
from AppUI.Assets import AssetProvider

from . import starwarsunlimited_com, swu_db_com


class ClientProvider(DataSourceCardSearchClientProviding):
    
    class Dependencies:
        def __init__(self,
                     asset_provider: AssetProvider, 
                     remote_networker: DataFetcherRemote, 
                     local_networker: DataFetcherLocal, 
                     local_managed_sets: DataSourceLocallyManagedSets, 
                     observation_tower: ObservationTower):
            self.asset_provider = asset_provider
            self.remote_networker = remote_networker
            self.local_networker = local_networker
            self.local_managed_sets = local_managed_sets
            self.obsevation_tower = observation_tower
    
    def __init__(self, dependencies: Dependencies):
        self._swu_db_search = swu_db_com.SWUDBAPIRemoteClient(dependencies.remote_networker)
        self._local_search = swu_db_com.SWUDBAPILocalClient(dependencies.local_networker, 
                                                            dependencies.asset_provider)
        self._locally_managed_deck_search = swu_db_com.SWUDBLocalCardRetrieverClient(dependencies.obsevation_tower,
                                                                                     dependencies.local_networker, 
                                                                                     dependencies.local_managed_sets)
        self._starwarsulimited_search = starwarsunlimited_com.SearchClient(dependencies.remote_networker, dependencies.asset_provider)
    
    def client(self, setting: Configuration.Settings.SearchSource) -> DataSourceCardSearchClientProtocol:
        if setting == Configuration.Settings.SearchSource.LOCALLY_MANAGED_DECKS:
            return self._locally_managed_deck_search
        elif setting == Configuration.Settings.SearchSource.LOCAL: # TODO: deprecate
            return self._local_search
        elif setting == Configuration.Settings.SearchSource.STARWARSUNLIMITED_FFG:
            return self._starwarsulimited_search
        
        return self._swu_db_search
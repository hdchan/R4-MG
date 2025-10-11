
from AppCore.DataSource import DataSourceDraftList
from AppCore.DataSource.DataSourceCardSearch import DataSourceCardSearch
from AppCore.Observation.ObservationTower import ObservationTower

from .Assets import AssetProvider
from .Config.SWUAppConfiguration import SWUAppConfigurationManager
from AppCore.DataSource.DataSourceCardSearch import DataSourceCardSearch, DataSourceCardSearchDelegate
from AppCore.DataSource.DataSourceCardSearchClientProtocol import DataSourceCardSearchClientProviding

class SWUAppDependenciesProviding:
    @property
    def observation_tower(self) -> ObservationTower:
        raise Exception
    
    @property
    def asset_provider(self) -> AssetProvider:
        raise Exception
    
    @property
    def configuration_manager(self) -> SWUAppConfigurationManager:
        raise Exception
    
    @property
    def data_source_draft_list(self) -> DataSourceDraftList:
        raise Exception
    
    def new_data_source_card_search(self,
                                    delegate: DataSourceCardSearchDelegate,
                                    search_client_provider: DataSourceCardSearchClientProviding) -> DataSourceCardSearch:
        raise Exception
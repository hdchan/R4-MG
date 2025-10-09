
from AppCore.DataSource import DataSourceDraftList
from AppCore.Observation.ObservationTower import ObservationTower

from .Assets import AssetProvider
from .Config.SWUAppConfiguration import SWUAppConfigurationManager


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
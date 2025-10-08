
from AppCore.DataSource import DataSourceDraftList
from AppCore.DataSource.DataSourceCardSearch import (
    DataSourceCardSearch, DataSourceCardSearchDelegate)
from AppCore.ImageResource import ImageResourceProcessorProviding
from AppCore.Observation.ObservationTower import ObservationTower
from AppUI.Router.Router import Router

from .Assets import AssetProvider
from .Config.SWUAppConfiguration import SWUAppConfigurationManager


class SWUAppDependenciesProviding:
    @property
    def observation_tower(self) -> ObservationTower:
        raise Exception
    
    @property
    def router(self) -> Router:
        raise Exception

    @property
    def asset_provider(self) -> AssetProvider:
        raise Exception
    
    @property
    def configuration_manager(self) -> SWUAppConfigurationManager:
        raise Exception
    
    @property
    def image_resource_processor_provider(self) -> ImageResourceProcessorProviding:
        raise Exception

    @property
    def data_source_draft_list(self) -> DataSourceDraftList:
        raise Exception
    
    def new_data_source_card_search(self,
                                    delegate: DataSourceCardSearchDelegate) -> DataSourceCardSearch:
        raise Exception
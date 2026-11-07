from typing import Optional

from AppCore.Config import ConfigurationManager
from AppUI.DataSource.DraftListWindowResource import DataSourceDraftListWindowResourceDeployerProtocol
from AppUI.DataSource.ImageResourceDeployer import DataSourceImageResourceDeployerProtocol
from AppUI.DataSource.DataSourceCachedHistory import DataSourceCachedHistory
from AppUI.DataSource.DataSourceCardSearch import (
    DataSourceCardSearch,
    DataSourceCardSearchClientProviding,
    DataSourceCardSearchDelegate,
)
from AppUI.DataSource.DataSourceCustomDirectorySearch import (
    CustomDirectorySearchDataSource,
    CustomDirectorySearchDataSourceDelegate,
)
from AppUI.DataSource.DraftList import DataSourceDraftListProviding
from AppCore.ImageResourceProcessor import ImageResourceProcessorProviding
from AppCore.Observation.ObservationTower import ObservationTower
from AppCore.Service import DataSerializer, PlatformServiceProvider, StringFormatter
from AppCore.Service.WebSocket import WebSocketServiceProtocol
from AppUI.DataSource.PlayerStandings import DataSourcePlayerStandingsProviding

class CoreDependenciesProviding:
    @property
    def data_source_image_resource_deployer(self) -> DataSourceImageResourceDeployerProtocol:
         raise Exception

    @property
    def observation_tower(self) -> ObservationTower:
        raise Exception
    
    @property
    def configuration_manager(self) -> ConfigurationManager:
        raise Exception
    
    @property
    def image_resource_processor_provider(self) -> ImageResourceProcessorProviding:
        raise Exception
    
    @property
    def platform_service_provider(self) -> PlatformServiceProvider:
        raise Exception
    
    @property
    def string_formatter(self) -> StringFormatter:
        raise Exception
    
    @property
    def data_serializer(self) -> DataSerializer:
        raise Exception
    
    def new_instance_card_search_data_source(self, 
                                             delegate: DataSourceCardSearchDelegate, 
                                             search_client_provider: DataSourceCardSearchClientProviding,
                                             ds_configuration: Optional[DataSourceCardSearch.DataSourceCardSearchConfiguration] = None) -> DataSourceCardSearch:
        raise Exception
    
    def new_instance_custom_directory_search_data_source(self, 
                                                         delegate: CustomDirectorySearchDataSourceDelegate) -> CustomDirectorySearchDataSource:
        raise Exception
    
    @property
    def data_source_draft_list_provider(self) -> DataSourceDraftListProviding:
        raise Exception
    
    @property
    def data_source_recent_published(self) -> DataSourceCachedHistory:
        raise Exception
    
    @property
    def data_source_draft_list_window_resource_deployer(self) -> DataSourceDraftListWindowResourceDeployerProtocol:
        raise Exception

    @property
    def data_source_player_standings_provider(self) -> DataSourcePlayerStandingsProviding:
        raise Exception

    @property
    def websocket_service(self) -> WebSocketServiceProtocol:
        raise Exception
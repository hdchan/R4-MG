from typing import Optional

from AppCore.Config import ConfigurationManager
from AppCore.DataSource import (DataSourceDraftList,
                                DataSourceDraftListWindowResourceDeployer,
                                DataSourceImageResourceDeployer)
from AppCore.DataSource.DataSourceCardSearch import (
    DataSourceCardSearch, DataSourceCardSearchClientProviding,
    DataSourceCardSearchDelegate)
from AppCore.DataSource.DataSourceCustomDirectorySearch import (
    CustomDirectorySearchDataSource, CustomDirectorySearchDataSourceDelegate)
from AppCore.DataSource.DataSourceCachedHistory import \
    DataSourceCachedHistory
from AppCore.ImageResource import ImageResourceProcessorProviding
from AppCore.Observation.ObservationTower import ObservationTower
from AppCore.Service import (DataSerializer, PlatformServiceProvider,
                             StringFormatter)
from AppCore.SocketIO import SocketRouter

class CoreDependenciesProviding:
    @property
    def data_source_image_resource_deployer(self) -> DataSourceImageResourceDeployer:
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
    def data_source_draft_list(self) -> DataSourceDraftList:
        raise Exception
    
    @property
    def data_source_recent_published(self) -> DataSourceCachedHistory:
        raise Exception
    
    @property
    def data_source_draft_list_window_resource_deployer(self) -> DataSourceDraftListWindowResourceDeployer:
        raise Exception
    
    @property
    def socket_router(self) -> SocketRouter:
        raise Exception
    
    @property
    def data_source_socket_io(self) -> DataSourceCachedHistory:
        raise Exception
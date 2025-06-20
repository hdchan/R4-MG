from typing import Optional

from AppCore.Config import ConfigurationManager
from AppCore.DataSource.DataSourceCardSearch import (
    DataSourceCardSearch, DataSourceCardSearchClientProviding,
    DataSourceCardSearchDelegate)
from AppCore.DataSource.DataSourceCustomDirectorySearch import (
    CustomDirectorySearchDataSource, CustomDirectorySearchDataSourceDelegate)
from AppCore.ImageResource import (ImageResourceDeployer,
                                   ImageResourceProcessorProviding)
from AppCore.Observation.ObservationTower import ObservationTower
from AppCore.Service import PlatformServiceProvider, StringFormatter


class CoreDependenciesProviding:
    @property
    def image_resource_deployer(self) -> ImageResourceDeployer:
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
    
    def new_instance_card_search_data_source(self, 
                                             delegate: DataSourceCardSearchDelegate, 
                                             search_client_provider: DataSourceCardSearchClientProviding,
                                             ds_configuration: Optional[DataSourceCardSearch.DataSourceCardSearchConfiguration] = None) -> DataSourceCardSearch:
        raise Exception
    
    def new_instance_custom_directory_search_data_source(self, 
                                                         delegate: CustomDirectorySearchDataSourceDelegate) -> CustomDirectorySearchDataSource:
        raise Exception
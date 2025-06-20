import atexit

from AppCore import *
from AppCore.Config import ConfigurationManager
from AppCore.DataSource.DataSourceCardSearch import *
from AppCore.DataSource.DataSourceRecentPublished import *
from AppCore.ImageResource import ImageResourceProcessor, ImageResourceDeployer
from AppCore.ImageFetcher import ImageFetcherProvider
from AppCore.DataFetcher import *
from AppCore.Observation.Events import ApplicationEvent
from AppCore.Observation.ObservationTower import ObservationTower
from AppCore.Service import PlatformServiceProvider, StringFormatter

from .CoreDependenciesProviding import CoreDependenciesProviding


class CoreDependenciesProvider(CoreDependenciesProviding):
    def __init__(self):
            self._observation_tower = ObservationTower()
            self._string_formatter = StringFormatter()
            
            self._configuration_manager = ConfigurationManager(self._observation_tower)

            self._platform_service_provider = PlatformServiceProvider(self._configuration_manager, 
                                                                      self._observation_tower)
            
            self._image_resource_processor_provider = ImageResourceProcessor(ImageFetcherProvider(self._configuration_manager), 
                                                                             self.observation_tower)
            
            self._image_resource_deployer = ImageResourceDeployer(self._configuration_manager,
                                                                  self._observation_tower, 
                                                                  self._image_resource_processor_provider)
            atexit.register(self.cleanup)
    
    @property
    def image_resource_processor_provider(self) -> ImageResourceProcessorProviding:
        return self._image_resource_processor_provider
    
    @property
    def image_resource_deployer(self) -> ImageResourceDeployer:
         return self._image_resource_deployer

    @property
    def observation_tower(self) -> ObservationTower:
        return self._observation_tower
    
    @property
    def configuration_manager(self) -> ConfigurationManager:
        return self._configuration_manager
    
    @property
    def platform_service_provider(self) -> PlatformServiceProvider:
        return self._platform_service_provider
    
    
    @property
    def string_formatter(self) -> StringFormatter:
        return self._string_formatter
    
    def new_instance_card_search_data_source(self, 
                                             delegate: DataSourceCardSearchDelegate,
                                             search_client_provider: DataSourceCardSearchClientProviding,
                                             ds_configuration: Optional[DataSourceCardSearch.DataSourceCardSearchConfiguration] = None) -> DataSourceCardSearch:
        ds = DataSourceCardSearch(self._observation_tower, 
                                  self._configuration_manager, 
                                  self._image_resource_processor_provider, 
                                  search_client_provider,
                                  self._string_formatter,
                                  ds_configuration)
        ds.delegate = delegate
        return ds
    
    def new_instance_custom_directory_search_data_source(self, 
                                                         delegate: CustomDirectorySearchDataSourceDelegate) -> CustomDirectorySearchDataSource:
        ds = CustomDirectorySearchDataSource(self._configuration_manager, 
                                             self._platform_service_provider, 
                                             self._observation_tower, 
                                             self._image_resource_processor_provider)
        ds.delegate = delegate
        return ds
    
    def cleanup(self):
        print("Performing cleanup before exit...")
        self._observation_tower.notify(ApplicationEvent(ApplicationEvent.EventType.APP_WILL_TERMINATE))
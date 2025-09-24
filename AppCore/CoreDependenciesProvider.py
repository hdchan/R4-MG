import atexit

from AppCore import *
from AppCore.Config import ConfigurationManager
from AppCore.DataFetcher import *
from AppCore.DataSource import (DataSourceDraftList,
                                DataSourceDraftListWindowResourceDeployer,
                                DataSourceImageResourceDeployer)
from AppCore.DataSource.DataSourceCardSearch import *
from AppCore.ImageFetcher import ImageFetcherProvider
from AppCore.ImageResource import ImageResourceProcessor
from AppCore.Observation.Events import ApplicationEvent
from AppCore.Observation.ObservationTower import ObservationTower
from AppCore.Service import (DataSerializer, PlatformServiceProvider,
                             StringFormatter)

from .CoreDependenciesInternalProviding import \
    CoreDependenciesInternalProviding
from .CoreDependenciesProviding import CoreDependenciesProviding


class CoreDependenciesProvider(CoreDependenciesProviding, CoreDependenciesInternalProviding):
    def __init__(self, 
                 observation_tower: ObservationTower, 
                 configuration_manager: ConfigurationManager):
        self._observation_tower = observation_tower
        self._string_formatter = StringFormatter()
        self._data_serializer = DataSerializer()
        
        self._configuration_manager = configuration_manager

        self._platform_service_provider = PlatformServiceProvider(self._configuration_manager,
                                                                  self._observation_tower)
        
        self._image_resource_processor_provider = ImageResourceProcessor(ImageFetcherProvider(self._configuration_manager),
                                                                         self.observation_tower)
        
        self._data_source_image_resource_deployer = DataSourceImageResourceDeployer(self._configuration_manager,
                                                              self._observation_tower,
                                                              self._image_resource_processor_provider)
        
        self._data_source_draft_list = DataSourceDraftList(self._configuration_manager,
                                                           self._observation_tower, 
                                                           self._data_serializer)
        
        self._data_source_recent_published = DataSourceRecentPublished(self._observation_tower, 
                                                                       self._image_resource_processor_provider, 
                                                                       self._configuration_manager, 
                                                                       self._data_serializer)
        
        self._data_source_draft_list_window_resource_deployer = DataSourceDraftListWindowResourceDeployer(self._configuration_manager, 
                                                                                                          self._observation_tower, 
                                                                                                          self._data_source_draft_list, 
                                                                                                          self._data_serializer)
        
        atexit.register(self._cleanup)
    
    @property
    def image_resource_processor_provider(self) -> ImageResourceProcessorProviding:
        return self._image_resource_processor_provider
    
    @property
    def data_source_image_resource_deployer(self) -> DataSourceImageResourceDeployer:
         return self._data_source_image_resource_deployer

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
    def data_serializer(self) -> DataSerializer:
        return self._data_serializer
    
    
    @property
    def string_formatter(self) -> StringFormatter:
        return self._string_formatter
    
    def new_instance_card_search_data_source(self, 
                                             delegate: DataSourceCardSearchDelegate,
                                             search_client_provider: DataSourceCardSearchClientProviding,
                                             ds_configuration: Optional[DataSourceCardSearch.DataSourceCardSearchConfiguration] = None) -> DataSourceCardSearch:
        ds = DataSourceCardSearch(self,
                                  search_client_provider,
                                  ds_configuration)
        ds.delegate = delegate
        return ds
    
    def new_instance_custom_directory_search_data_source(self, 
                                                         delegate: CustomDirectorySearchDataSourceDelegate) -> CustomDirectorySearchDataSource:
        ds = CustomDirectorySearchDataSource(self)
        ds.delegate = delegate
        return ds
    
    @property
    def data_source_draft_list(self) -> DataSourceDraftList:
        return self._data_source_draft_list
    
    @property
    def data_source_recent_published(self) -> DataSourceRecentPublished:
        return self._data_source_recent_published
    
    @property
    def data_source_draft_list_window_resource_deployer(self) -> DataSourceDraftListWindowResourceDeployer:
        return self._data_source_draft_list_window_resource_deployer
    
    def _cleanup(self):
        print("Performing cleanup before exit...")
        self._observation_tower.notify(ApplicationEvent(ApplicationEvent.EventType.APP_WILL_TERMINATE))
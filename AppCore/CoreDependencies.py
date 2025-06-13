import atexit

from AppCore import *
from AppCore.Config import ConfigurationManager
from AppCore.Data.CardSearchDataSource import *
from AppCore.Data.RecentPublishedDataSource import *
from AppCore.Image import *
from AppCore.ImageNetwork import ImageFetcherLocal, ImageFetcherRemote
from AppCore.Network import *
from AppCore.Observation.Events import ApplicationEvent
from AppCore.Observation.ObservationTower import ObservationTower
from AppCore.Service import PlatformServiceProvider, StringFormatter

from .CoreDependencyProviding import CoreDependencyProviding


class CoreDependencies(CoreDependencyProviding):
    def __init__(self):
            self._observation_tower = ObservationTower()
            self._configuration_manager = ConfigurationManager(self._observation_tower)
            self._platform_service_provider = PlatformServiceProvider(self._configuration_manager, 
                                                                      self._observation_tower)
            
            self._string_formatter = StringFormatter()
            self._api_client_provider = None
    
            image_fetcher_provider = ImageFetcherProvider(self._configuration_manager,
                                                          ImageFetcherRemote(self._configuration_manager),
                                                          ImageFetcherLocal(self._configuration_manager))
            self._image_resource_processor_provider = ImageResourceProcessorProvider(ImageResourceProcessor(image_fetcher_provider,
                                                                                                      self.observation_tower))
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
    
    def cleanup(self):
        print("Performing cleanup before exit...")
        self._observation_tower.notify(ApplicationEvent(ApplicationEvent.EventType.APP_WILL_TERMINATE))
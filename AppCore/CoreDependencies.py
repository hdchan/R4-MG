import atexit

from AppCore import *
from AppCore.Config import ConfigurationManager
from AppCore.Data.CardSearchDataSource import *
from AppCore.Data.RecentPublishedDataSource import *
from AppCore.Image import *
from AppCore.Network import *
from AppCore.Observation.Events import ApplicationEvent
from AppCore.Observation.ObservationTower import ObservationTower
from AppCore.Resource import *
from AppCore.Service import PlatformServiceProvider, StringFormatter

from .CoreDependencyProviding import CoreDependencyProviding


class CoreDependencies(CoreDependencyProviding):
    def __init__(self):
            self._observation_tower = ObservationTower()
            self._configuration_manager = ConfigurationManager(self._observation_tower)
            self._platform_service_provider = PlatformServiceProvider(self._configuration_manager, 
                                                                      self._observation_tower)
            
            self._string_formatter = StringFormatter()
            self._image_resource_processor_provider = None
            self._api_client_provider = None
            self._image_source_provider = None

            atexit.register(self.cleanup)
    
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
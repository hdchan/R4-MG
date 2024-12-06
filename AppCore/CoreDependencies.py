from AppCore import *
from AppCore.Config import ConfigurationManager
from AppCore.Data.CardSearchDataSource import *
from AppCore.Image import *
from AppCore.Network import *
from AppCore.Observation.ObservationTower import ObservationTower
from AppCore.Resource import *
from AppCore.Service import PlatformServiceProvider

from .CoreDependencyProviding import CoreDependencyProviding
from AppCore.Data.RecentPublishedDataSource import *

class CoreDependencies(CoreDependencyProviding):
    def __init__(self):
            self._observation_tower = ObservationTower()
            self._configuration_manager = ConfigurationManager(self._observation_tower)
            self._platform_service_provider = PlatformServiceProvider(self._configuration_manager, 
                                                                      self._observation_tower)
            self._image_resource_deployer = ImageResourceDeployer(self._configuration_manager,
                                                            self._observation_tower)
            self._image_resource_processor_provider = None
            self._api_client_provider = None
            self._image_source_provider = None
    
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

    # @property
    # def image_resource_processor_provider(self) -> ImageResourceProcessorProviding:
    #     return self._image_resource_processor_provider

    # @property
    # def api_client_provider(self) -> APIClientProviding:
    #     return self._api_client_provider
    
    # @property
    # def image_source_provider(self) -> CardImageSourceProviding:
    #     return self._image_source_provider
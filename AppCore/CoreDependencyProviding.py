from AppCore.Config import ConfigurationManager
from AppCore.Image import (ImageResourceDeployer,
                           ImageResourceProcessorProviding)
from AppCore.Observation.ObservationTower import ObservationTower
from AppCore.Resource import CardImageSourceProviding
from AppCore.Service import PlatformServiceProvider, StringFormatter


class CoreDependencyProviding:
    @property
    def image_resource_deployer(self) -> ImageResourceDeployer:
         return NotImplemented

    @property
    def observation_tower(self) -> ObservationTower:
        return NotImplemented
    
    @property
    def configuration_manager(self) -> ConfigurationManager:
        return NotImplemented
    
    @property
    def image_resource_processor_provider(self) -> ImageResourceProcessorProviding:
        return NotImplemented
    
    @property
    def image_source_provider(self) -> CardImageSourceProviding:
        return NotImplemented
    
    @property
    def platform_service_provider(self) -> PlatformServiceProvider:
        return NotImplemented
    
    @property
    def string_formatter(self) -> StringFormatter:
        return NotImplemented
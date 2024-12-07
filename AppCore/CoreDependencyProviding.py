from AppCore.Config import ConfigurationProviding
from AppCore.Data import APIClientProviding
from AppCore.Image import ImageResourceProcessorProviding
from AppCore.Observation.ObservationTower import ObservationTower
from AppCore.Resource import CardImageSourceProviding


class CoreDependencyProviding:
    @property
    def observation_tower(self) -> ObservationTower:
        return NotImplemented
    
    @property
    def configuration_provider(self) -> ConfigurationProviding:
        return NotImplemented
    
    @property
    def image_resource_processor_provider(self) -> ImageResourceProcessorProviding:
        return NotImplemented

    @property
    def api_client_provider(self) -> APIClientProviding:
        return NotImplemented
    
    @property
    def image_source_provider(self) -> CardImageSourceProviding:
        return NotImplemented
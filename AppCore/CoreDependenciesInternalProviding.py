
from AppCore.Config import ConfigurationManager
from AppCore.DataSource import DataSourceDraftList, DataSourceImageResourceDeployer
from AppCore.ImageResource import ImageResourceProcessorProviding
from AppCore.Observation.ObservationTower import ObservationTower
from AppCore.Service import (DataSerializer, PlatformServiceProvider,
                             StringFormatter)
from AppCore.Models import ModelTransformer

class CoreDependenciesInternalProviding:
    @property
    def model_transformer(self) -> ModelTransformer:
        raise Exception
    
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
    
    @property
    def data_source_draft_list(self) -> DataSourceDraftList:
        raise Exception

from abc import ABC, abstractmethod

from AppCore.Config import ConfigurationManager
from AppCore.DataSource.DraftList import DataSourceDraftListProviding
from AppCore.DataSource.ImageResourceDeployer import DataSourceImageResourceDeployerProtocol
from AppCore.ImageResourceProcessor import ImageResourceProcessorProviding
from AppCore.Models import ModelTransformer
from AppCore.Observation.ObservationTower import ObservationTower
from AppCore.Service import DataSerializer, PlatformServiceProvider, StringFormatter

class CoreDependenciesInternalProviding(ABC):
    @property
    @abstractmethod
    def model_transformer(self) -> ModelTransformer:
        raise Exception
    
    @property
    @abstractmethod
    def data_source_image_resource_deployer(self) -> DataSourceImageResourceDeployerProtocol:
         raise Exception

    @property
    @abstractmethod
    def observation_tower(self) -> ObservationTower:
        raise Exception
    
    @property
    @abstractmethod
    def configuration_manager(self) -> ConfigurationManager:
        raise Exception
    
    @property
    @abstractmethod
    def image_resource_processor_provider(self) -> ImageResourceProcessorProviding:
        raise Exception
    
    @property
    @abstractmethod
    def platform_service_provider(self) -> PlatformServiceProvider:
        raise Exception
    
    @property
    @abstractmethod
    def string_formatter(self) -> StringFormatter:
        raise Exception
    
    @property
    @abstractmethod
    def data_serializer(self) -> DataSerializer:
        raise Exception
    
    @property
    @abstractmethod
    def data_source_draft_list_provider(self) -> DataSourceDraftListProviding:
        raise Exception

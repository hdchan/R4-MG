import copy
import shutil
from typing import List, Optional

from PIL import Image

from AppCore.Config import ConfigurationProviding
from AppCore.Models import *

from .ApplicationState import ApplicationState
from .Data import *
from .Data.CardSearchDataSource import *
from .Image import *
from .Observation import *
from .Observation.Events import *
from .Service import PlatformProtocol, PlatformServiceProvider


class ApplicationCoreDelegate:
    def app_did_load_production_resources(self, app_core: ..., local_resource: List[LocalCardResource]) -> None:
        pass


class ApplicationCore(ImageResourceDeployerDelegate, CardSearchDataSourceDelegate, ApplicationState):
    def __init__(self,
                 observation_tower: ObservationTower,
                 configuration_provider: ConfigurationProviding):
        
        self._resource_deployer = ImageResourceDeployer(configuration_provider, 
                                                        observation_tower)
        self._resource_deployer.delegate = self
        
        self._configuration_provider = configuration_provider
        
        self._observation_tower = observation_tower

        self._platform_service_provider = PlatformServiceProvider()
        
        self.delegate: Optional[ApplicationCoreDelegate] = None
    
    @property
    def can_publish_staged_resources(self) -> bool:
        return self._resource_deployer.can_publish_staged_resources
    
    @property
    def _configuration(self) -> Configuration:
        return self._configuration_provider.configuration
    
    @property
    def _platform(self) -> PlatformProtocol:
        return self._platform_service_provider.platform()
    
    def can_stage_current_card_search_resource_to_stage_index(self, index: int) -> bool:
        return index < len(self._resource_deployer.production_resources)

    def stage_resource(self, local_resource: LocalCardResource, index: int):
        self._resource_deployer.stage_resource(local_resource, index)

    def unstage_resource(self, index: int):
        self._resource_deployer.unstage_resource(index)

    def unstage_all_resources(self):
        self._resource_deployer.unstage_all_resources()

    def load_production_resources(self):
        self._resource_deployer.load_production_resources()


    def publish_staged_resources(self):
        return self._resource_deployer.publish_staged_resources()
    
    def generate_new_file(self, file_name: str, image: Optional[Image.Image] = None):
        self._resource_deployer.generate_new_file(file_name, image)
        
    

    # MARK: - Resource Deployer Delegate methods
    def rd_did_load_production_resources(self, rd: ImageResourceDeployer, local_resources: List[LocalCardResource]):
        if self.delegate is not None:
            self.delegate.app_did_load_production_resources(self, copy.deepcopy(local_resources))

    # OS operations
    def open_production_dir(self):
        self._platform.open_file(self._configuration.production_file_path)
        
    def open_temp_dir(self):
        self._platform.open_file(self._configuration.temp_dir_path)

    def open_configuration_dir(self):
        self._platform.open_file(self._configuration.config_directory)
        
    def open_file(self, local_resource: LocalCardResource):
        self._platform.open_file(local_resource.image_path)
    
    def open_file_path_and_select_file(self, local_resource: LocalCardResource):
        self._platform.open_file_path_and_select_file(local_resource.image_path)

    def clear_cache(self):
        shutil.rmtree(self._configuration.cache_file_path)
        self._observation_tower.notify(CacheClearedEvent())
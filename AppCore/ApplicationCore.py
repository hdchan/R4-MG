import copy
import shutil
from typing import List, Optional

from PIL import Image

from AppCore.Config import ConfigurationProviderProtocol
from AppCore.Models import *
from AppCore.Resource import CardResourceProvider

from .Data import *
from .Image import *
from .Observation import *
from .Observation.Events import *
from .Resource import CardImageSourceProviderProtocol
from .Service import PlatformProtocol, PlatformServiceProvider
from .ApplicationState import ApplicationState

class ApplicationCoreDelegate:
    def app_did_complete_search(self, app_core: ..., display_name_list: List[TradingCard], error: Optional[Exception]) -> None:
        pass
    
    def app_did_retrieve_card_resource_for_card_selection(self, app_core: ..., local_resource: LocalCardResource, is_flippable: bool) -> None:
        pass
    
    def app_did_load_production_resources(self, app_core: ..., local_resource: List[LocalCardResource]) -> None:
        pass

class ApplicationCore(ImageResourceDeployerDelegate, CardDataSourceDelegate, ApplicationState):
    def __init__(self, 
                 observation_tower: ObservationTower, 
                 api_client_provider: APIClientProviderProtocol,
                 image_fetcher_provider: ImageFetcherProviderProtocol,
                 card_image_source_provider: CardImageSourceProviderProtocol,
                 configuration_provider: ConfigurationProviderProtocol):
        
        self._data_source = CardDataSource(observation_tower, 
                                           api_client_provider)
        self._data_source.delegate = self
        
        self._resource_processor = ImageResourceProcessor(image_fetcher_provider,
                                                    observation_tower)
        
        self._resource_deployer = ImageResourceDeployer(configuration_provider, 
                                                        observation_tower)
        self._resource_deployer.delegate = self
        
        self._card_image_source_provider = card_image_source_provider
        
        self._configuration_provider = configuration_provider
        
        self._observation_tower = observation_tower

        self._platform_service_provider = PlatformServiceProvider()
        
        self.delegate: Optional[ApplicationCoreDelegate] = None
        
        # stateful variables
        self.selected_index: Optional[int] = None
        self._selected_resource: Optional[LocalCardResource] = None
        self._trading_card_providers: List[CardResourceProvider] = []
    
    @property
    def current_card_search_resource(self) -> Optional[LocalCardResource]:
        if self._selected_resource is not None:
            return copy.deepcopy(self._selected_resource)
        return None
    
    @property
    def can_publish_staged_resources(self) -> bool:
        return self._resource_deployer.can_publish_staged_resources

    # @property 
    # def production_resources(self) -> List[LocalCardResource]:
    #     return copy.deepcopy(self._resource_deployer.production_resources)
    
    @property
    def _configuration(self) -> Configuration:
        return self._configuration_provider.configuration
    
    @property
    def _platform(self) -> PlatformProtocol:
        return self._platform_service_provider.providePlatform()

    def search(self, search_config: SearchConfiguration):
        self._data_source.search(search_config)
    
    
    def current_previewed_trading_card_is_flippable(self) -> bool:
        if self.selected_index is not None:
            return self._trading_card_providers[self.selected_index].is_flippable
        return False
    
    def select_card_resource_for_card_selection(self, index: int):
        if index < len(self._trading_card_providers):
            self.selected_index = index
            self._retrieve_card_resource_for_card_selection(index)

    def flip_current_previewed_card(self):
        if self.selected_index is not None and self.current_previewed_trading_card_is_flippable():
            self._trading_card_providers[self.selected_index].flip()
            self._retrieve_card_resource_for_card_selection(self.selected_index)
    
    def redownload_currently_selected_card_resource(self):
        if self.selected_index is not None:
            self._retrieve_card_resource_for_card_selection(self.selected_index, True)
    
    
    
    # MARK: - DS Delegate methods
    def ds_completed_search_with_result(self, ds: CardDataSource, result_list: List[TradingCard], error: Optional[Exception]):
        def create_trading_card_resource(trading_card: TradingCard):
            return CardResourceProvider(trading_card, 
                                        self._configuration_provider,
                                        self._card_image_source_provider)
        self._trading_card_providers = list(map(create_trading_card_resource, result_list))
        if self.delegate is not None:
            self.delegate.app_did_complete_search(self, result_list, error)

    # MARK: - Resource Cacher
    def redownload_resource(self, local_resource: LocalCardResource):
        self._resource_processor.async_store_local_resource(local_resource, True)

    def _retrieve_card_resource_for_card_selection(self, index: int, retry: bool = False):
        trading_card_resource_provider = self._trading_card_providers[index]
        selected_resource = trading_card_resource_provider.local_resource
        self._selected_resource = selected_resource
        self._resource_processor.async_store_local_resource(selected_resource, retry)
        if self.delegate is not None:
            self.delegate.app_did_retrieve_card_resource_for_card_selection(self, copy.deepcopy(selected_resource), trading_card_resource_provider.is_flippable)
    

    # MARK: - Resource manager
    def can_stage_current_card_search_resource_to_stage_index(self, index: int) -> bool:
        return self.current_card_search_resource is not None and index < len(self._resource_deployer.production_resources)

    def stage_resource(self, index: int):
        if self.current_card_search_resource is not None:
            self._resource_deployer.stage_resource(self.current_card_search_resource, index)

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
        
    
    # Image rotation
    def rotate_and_save_resource(self, local_resource: LocalCardResource, angle: float):
        self._resource_processor.rotate_and_save_resource(local_resource, angle)
    
    def regenerate_resource_preview(self, local_resource: LocalCardResource):
        self._resource_processor.regenerate_resource_preview(local_resource)
    

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
import copy
import os
from typing import Callable, List, Optional

from PyQt5.QtCore import QStandardPaths

from AppCore.Config import Configuration
from AppCore.CoreDependencyProviding import CoreDependencyProviding
from AppCore.Models import LocalCardResource, SearchConfiguration, TradingCard
from AppCore.Network import LocalNetworker
from AppCore.Observation.Events import LocalResourceSelectedEvent

from ..Config import ConfigurationManager
from ..Models.LocalCardResource import LocalCardResource
from ..Models.TradingCard import TradingCard
from .CustomTradingCard import CustomTradingCard


class CardResourceProvider:
    def __init__(self, 
                 trading_card: TradingCard,
                 configuration_manager: ConfigurationManager):
        self._trading_card = trading_card
        self._configuration_manager = configuration_manager
    
    @property
    def trading_card(self) -> TradingCard:
        return self._trading_card
    
    @property
    def local_resource(self) -> LocalCardResource:
        return self.front_local_resource
    
    @property
    def front_local_resource(self) -> LocalCardResource:
        return LocalCardResource(image_dir=self._directory_path,
                                image_preview_dir=self._preview_dir_path, 
                                file_name=self._trading_card.name,
                                display_name=self._trading_card.friendly_display_name,
                                display_name_short=self._trading_card.friendly_display_name_short,
                                display_name_detailed=self._trading_card.friendly_display_name_detailed)
    
    @property
    def _directory_path(self) -> str:
        return f'{QStandardPaths.writableLocation(QStandardPaths.StandardLocation.PicturesLocation)}/R4-MG/custom/'
    
    @property
    def _preview_dir_path(self) -> str:
        return f'{self._directory_path}preview/'

        

class CustomDirectorySearchDataSourceDelegate:
    def ds_completed_search_with_result(self, 
                                        ds: 'CustomDirectorySearchDataSource',
                                        error: Optional[Exception]) -> None:
        pass
        
    def ds_did_retrieve_card_resource_for_card_selection(self, 
                                                         ds: 'CustomDirectorySearchDataSource', 
                                                         local_resource: LocalCardResource) -> None:
        pass

class CustomDirectorySearchDataSource:
    def __init__(self,
                 core_dependency_provider: CoreDependencyProviding):
        self._configuration_manager = core_dependency_provider.configuration_manager
        self._local_networker = LocalNetworker(self._configuration_manager)
        self._platform_service_provider = core_dependency_provider.platform_service_provider
        self._observation_tower = core_dependency_provider.observation_tower
        self._image_resource_processor_provider = core_dependency_provider.image_resource_processor_provider
        
        self._trading_card_providers: List[CardResourceProvider] = []
        
        self.delegate: Optional[CustomDirectorySearchDataSourceDelegate] = None
        
    @property
    def _configuration(self) -> Configuration:
        return self._configuration_manager.configuration
    
    @property
    def trading_cards(self) -> List[TradingCard]:
        return list(map(lambda x: x.trading_card, self._trading_card_providers))
    
    @property
    def source_display_name(self) -> str:
        return self._directory_path

    @property
    def site_source_url(self) -> Optional[str]:
        return None
    
    @property
    def _directory_path(self) -> str:
        return f'{QStandardPaths.writableLocation(QStandardPaths.StandardLocation.PicturesLocation)}/R4-MG/custom/'
    
    def open_directory_path(self):
        self._platform_service_provider.platform_service.open_file(self._directory_path)
    
    def select_card_resource_for_card_selection(self, index: int):
        if index < len(self._trading_card_providers):
            self._selected_index = index
            self._retrieve_card_resource_for_card_selection(index)
    
    def _retrieve_card_resource_for_card_selection(self, index: int, retry: bool = False):
        trading_card_resource_provider = self._trading_card_providers[index]
        selected_resource = trading_card_resource_provider.local_resource
        self._selected_resource = selected_resource
        self._observation_tower.notify(LocalResourceSelectedEvent(selected_resource))
        self._image_resource_processor_provider.image_resource_processor.async_store_local_resource(selected_resource, retry)
        if self.delegate is not None:
            self.delegate.ds_did_retrieve_card_resource_for_card_selection(self, copy.deepcopy(selected_resource))
    
    def search(self, search_configuration: SearchConfiguration):
        def callback(result: List[TradingCard]):
            def create_trading_card_resource(trading_card: TradingCard):
                    return CardResourceProvider(trading_card, 
                                                self._configuration_manager)
            self._trading_card_providers = list(map(create_trading_card_resource, result))
            if self.delegate is not None:
                self.delegate.ds_completed_search_with_result(self, None)
        self._search(search_configuration, callback)
    
    def _search(self, 
               search_configuration: SearchConfiguration,
               callback: Callable[[List[TradingCard]], None]) -> None:
        def completed_search():
            self._perform_search(search_configuration, callback)
        print(f'Custom search. card_name: {search_configuration.card_name}, search_configuration: {search_configuration}')
        self._local_networker.load_mock(completed_search) # TODO: needs to perform retrieval in thread
        
    def _perform_search(self, search_configuration: SearchConfiguration, callback: Callable[[List[TradingCard]], None]):
        def filter_the_result(card: TradingCard):
            if search_configuration.card_name.replace(" ", "") == '':
                return True
            return (search_configuration.card_name.lower() in card.name.lower())
        def sort_the_result(card: TradingCard):
            return card.name
        filtered_list = list(filter(filter_the_result, self._response_card_list))
        filtered_list.sort(key=sort_the_result)
        callback(filtered_list)
        
    @property
    def _response_card_list(self) -> List[TradingCard]:
        result: List[TradingCard] = []
        for i in self.list_files_in_directory():
            # TODO: guard against non PNG files
            file_name = os.path.splitext(i)
            card = CustomTradingCard.from_name(file_name[0], i, self._directory_path)
            result.append(card)
        
        return result
    
    def list_files_in_directory(self) -> List[str]:
        try:
            files = [f for f in os.listdir(self._directory_path) if os.path.isfile(os.path.join(self._directory_path, f))]
            return files
        except FileNotFoundError:
            return []
        
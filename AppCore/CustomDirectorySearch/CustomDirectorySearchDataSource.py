import os
from typing import Callable, List, Optional

from PyQt5.QtCore import QStandardPaths

from AppCore.Config import Configuration
from AppCore.Models import LocalCardResource, SearchConfiguration, TradingCard
from AppCore.Network import LocalNetworker
from AppCore.CoreDependencyProviding import CoreDependencyProviding
from .CustomTradingCard import CustomTradingCard


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
        
        self.delegate: Optional[CustomDirectorySearchDataSourceDelegate] = None
    
        self._result_list: Optional[List[TradingCard]] = None
        
    @property
    def _configuration(self) -> Configuration:
        return self._configuration_manager.configuration
    
    @property
    def result_list(self) -> Optional[List[TradingCard]]:
        return self._result_list
    
    @property
    def source_display_name(self) -> str:
        return self._directory_path

    @property
    def site_source_url(self) -> Optional[str]:
        return None
    
    @property
    def _directory_path(self) -> str:
        return f'{QStandardPaths.writableLocation(QStandardPaths.StandardLocation.PicturesLocation)}/R4-MG/custom/'
    
    @property
    def _preview_dir_path(self) -> str:
        return f'{self._directory_path}preview/'
    
    def open_directory_path(self):
        self._platform_service_provider.platform_service.open_file(self._directory_path)
    
    def select_card_resource_for_card_selection(self, index: int):
        pass
    
    def search(self, search_configuration: SearchConfiguration):
        def callback(result: List[TradingCard]):
            self._result_list = result
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
        
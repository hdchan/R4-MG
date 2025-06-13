import copy
import os
from typing import Callable, List, Optional, Tuple, Any, Dict

from PyQt5.QtCore import QStandardPaths

from AppCore.Config import Configuration
from AppCore.CoreDependencyProviding import CoreDependencyProviding
from AppCore.Models import LocalCardResource, SearchConfiguration
from AppCore.Models.LocalCardResource import LocalCardResource
from AppCore.Network import NetworkerLocal
from AppCore.Observation.Events import LocalResourceSelectedEvent

PNG_EXTENSION = '.png'

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
    
    class CardResourceProvider:
        def __init__(self,
                     file_name_components: Tuple[str, str]):
            self._file_name_components = file_name_components
        
        @property
        def file_name(self) -> str:
            return self._file_name_components[0]
        
        @property
        def _file_name_with_ext(self) -> str:
            return f'{self.file_name}{self._file_name_components[1]}'

        @property
        def local_resource(self) -> LocalCardResource:
            return self.front_local_resource
        
        @property
        def front_local_resource(self) -> LocalCardResource:
            return LocalCardResource(image_dir=self._directory_path,
                                    image_preview_dir=self._preview_dir_path, 
                                    file_name=self.file_name,
                                    display_name=self.file_name,
                                    display_name_short=self.file_name,
                                    display_name_detailed=self.file_name)
        
        @property
        def _directory_path(self) -> str:
            return f'{QStandardPaths.writableLocation(QStandardPaths.StandardLocation.PicturesLocation)}/R4-MG/custom/'
        
        @property
        def _preview_dir_path(self) -> str:
            return f'{self._directory_path}preview/'
        
        
    def __init__(self,
                 core_dependency_provider: CoreDependencyProviding):
        self._configuration_manager = core_dependency_provider.configuration_manager
        self._local_networker = NetworkerLocal(self._configuration_manager)
        self._platform_service_provider = core_dependency_provider.platform_service_provider
        self._observation_tower = core_dependency_provider.observation_tower
        self._image_resource_processor_provider = core_dependency_provider.image_resource_processor_provider
        
        self._trading_card_providers: List[CustomDirectorySearchDataSource.CardResourceProvider] = []
        
        self.delegate: Optional[CustomDirectorySearchDataSourceDelegate] = None
        
    @property
    def _configuration(self) -> Configuration:
        return self._configuration_manager.configuration
    
    @property
    def resource_display_names(self) -> List[str]:
        result_list: List[str] = []
        for provider in self._trading_card_providers:
            result_list.append(provider.file_name)
            # display_name = i.friendly_display_name
            # if self._configuration.card_title_detail == Configuration.Settings.CardTitleDetail.SHORT:
            #     display_name = i.friendly_display_name_short
            # elif self._configuration.card_title_detail == Configuration.Settings.CardTitleDetail.DETAILED:
            #     display_name = i.friendly_display_name_detailed
            # result_list.append(display_name) 
        return result_list
    
    @property
    def source_display_name(self) -> str:
        return self._directory_path
    
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
        def callback(result: List[Tuple[str, str]]):
            def create_trading_card_resource(file_name_components: Tuple[str, str]):
                    return self.CardResourceProvider(file_name_components)
            self._trading_card_providers = list(map(create_trading_card_resource, result))
            if self.delegate is not None:
                self.delegate.ds_completed_search_with_result(self, None)
        self._local_networker.load(self._perform_search, callback, search_configuration=search_configuration)
    
    # MARK: - async work
    def _perform_search(self, args: Any) -> List[Tuple[str, str]]:
        # search_configuration: SearchConfiguration
        search_configuration: SearchConfiguration = args.get('search_configuration')
        print(f'Custom search. card_name: {search_configuration.card_name}, search_configuration: {search_configuration}')
        def filter_the_result(card: Tuple[str, str]):
            if search_configuration.card_name.replace(" ", "") == '':
                return True
            return (search_configuration.card_name.lower() in card[0].lower())
        def sort_the_result(card: Tuple[str, str]):
            return card[0]
        filtered_list = list(filter(filter_the_result, self._response_card_list))
        filtered_list.sort(key=sort_the_result)
        return filtered_list
        
    @property
    def _response_card_list(self) -> List[Tuple[str, str]]:
        result: List[Tuple[str, str]] = []
        for file_name_with_ext in self.list_files_in_directory():
            # TODO: guard against non PNG files
            file_name_components = os.path.splitext(file_name_with_ext)
            if file_name_components[1] == PNG_EXTENSION:
                result.append(file_name_components)
        return result
    
    def list_files_in_directory(self) -> List[str]:
        try:
            files = [f for f in os.listdir(self._directory_path) if os.path.isfile(os.path.join(self._directory_path, f))]
            return files
        except FileNotFoundError:
            return []
        
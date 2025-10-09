import copy
import os
from typing import Any, List, Optional, Tuple

from AppCore.Config import Configuration
from AppCore.CoreDependenciesInternalProviding import \
    CoreDependenciesInternalProviding
from AppCore.DataFetcher import DataFetcherLocal
from AppCore.Models import LocalCardResource, SearchConfiguration
from AppCore.Models.LocalCardResource import LocalCardResource
from AppCore.Observation.Events import (CardSearchEvent,
                                        LocalCardResourceSelectedEvent)

PNG_EXTENSION = 'png' # TODO: allow for other image formats

class CustomDirectorySearchDataSourceDelegate:
    def ds_completed_search_with_result(self,
                                        ds: 'CustomDirectorySearchDataSource',
                                        search_configuration: SearchConfiguration,
                                        error: Optional[Exception]) -> None:
        raise Exception
        
    def ds_did_retrieve_card_resource_for_card_selection(self, 
                                                         ds: 'CustomDirectorySearchDataSource', 
                                                         local_resource: LocalCardResource) -> None:
        raise Exception

class CustomDirectorySearchDataSource:
    
    class CardResourceProvider:
        def __init__(self,
                     file_name_components: Tuple[str, str], 
                     directory_path: str):
            self._file_name_components = file_name_components
            self._directory_path = directory_path
        
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
        def _preview_dir_path(self) -> str:
            return f'{self._directory_path}preview/'
        
        
    def __init__(self,
                 core_dependencies_internal_provider: CoreDependenciesInternalProviding):
        self._configuration_manager = core_dependencies_internal_provider.configuration_manager
        self._local_networker = DataFetcherLocal(DataFetcherLocal.Configuration(self._configuration_manager.configuration.network_delay_duration))
        self._platform_service_provider = core_dependencies_internal_provider.platform_service_provider
        self._observation_tower = core_dependencies_internal_provider.observation_tower
        self._image_resource_processor_provider = core_dependencies_internal_provider.image_resource_processor_provider
        
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
        return result_list
    
    @property
    def source_display_name(self) -> Optional[str]:
        return self._directory_path
    
    @property
    def _directory_path(self) -> Optional[str]:
        return f'{self._configuration.custom_directory_search_path}/' # NOTE: we can't put trailing slash in configuration, otherwise it will append when reading
    
    def open_directory_path(self):
        if self._directory_path is not None:
            self._platform_service_provider.platform_service.open_file(self._directory_path)
    
    def select_card_resource_for_card_selection(self, index: int):
        if index < len(self._trading_card_providers):
            self._selected_index = index
            self._retrieve_card_resource_for_card_selection(index)
    
    def _retrieve_card_resource_for_card_selection(self, index: int, retry: bool = False):
        trading_card_resource_provider = self._trading_card_providers[index]
        selected_resource = trading_card_resource_provider.local_resource
        self._selected_resource = selected_resource
        self._observation_tower.notify(LocalCardResourceSelectedEvent(selected_resource))
        self._image_resource_processor_provider.image_resource_processor.async_store_local_resource(selected_resource, retry)
        if self.delegate is not None:
            self.delegate.ds_did_retrieve_card_resource_for_card_selection(self, copy.deepcopy(selected_resource))
    
    def search(self, search_configuration: SearchConfiguration):
        if self._directory_path is None:
            print("Directory not set")
            return
        dir_path = self._directory_path
        print(f'Custom directory search. card_name: {search_configuration.card_name}, search_configuration: {search_configuration}')
        initial_event = CardSearchEvent(CardSearchEvent.EventType.STARTED,
                                        CardSearchEvent.SourceType.LOCAL,
                                        copy.deepcopy(search_configuration))
        self._observation_tower.notify(initial_event)
        
        def callback(result: Tuple[List[Tuple[str, str]], Optional[Exception]]):
            def create_trading_card_resource(file_name_components: Tuple[str, str]):
                    return self.CardResourceProvider(file_name_components, dir_path)
            result_list, error = result
            self._trading_card_providers = list(map(create_trading_card_resource, result_list))
            if self.delegate is not None:
                self.delegate.ds_completed_search_with_result(self, search_configuration, error)
                
            finished_event = CardSearchEvent(CardSearchEvent.EventType.FINISHED,
                                             CardSearchEvent.SourceType.LOCAL,
                                             copy.deepcopy(search_configuration))
            finished_event.predecessor = initial_event
            self._observation_tower.notify(finished_event)
            
        self._local_networker.load(self._perform_search, callback, search_configuration=search_configuration)
    
    # MARK: - async work
    def _perform_search(self, args: Any) -> Tuple[List[Tuple[str, str]], Optional[Exception]]:
        search_configuration: SearchConfiguration = args.get('search_configuration')
        def filter_the_result(card: Tuple[str, str]):
            if search_configuration.card_name.replace(" ", "") == '':
                return True
            return (search_configuration.card_name.lower() in card[0].lower())
        def sort_the_result(card: Tuple[str, str]):
            return card[0]
        
        if self._directory_path is None:
            return [], None
        try:
            files = [f for f in os.listdir(self._directory_path) if os.path.isfile(os.path.join(self._directory_path, f))]
            result: List[Tuple[str, str]] = []
            for file_name_with_ext in files:
                file_name_components = os.path.splitext(file_name_with_ext)
                if file_name_components[1] == f'.{PNG_EXTENSION}':
                    result.append(file_name_components)
            
            filtered_list = list(filter(filter_the_result, result))
            filtered_list.sort(key=sort_the_result)
            return (filtered_list, None)
        except Exception as error:
            return [], error 
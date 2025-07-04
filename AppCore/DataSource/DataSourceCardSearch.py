import copy
import re
from functools import reduce
from typing import List, Optional
from urllib.parse import urlparse
from AppCore.Config import Configuration, ConfigurationManager
from AppCore.DataSource.DataSourceCardSearchClientProtocol import *
from AppCore.DataSource.DataSourceRecentSearch import DataSourceRecentSearch
from AppCore.ImageResource.ImageResourceProcessorProtocol import *
from AppCore.Models import LocalCardResource, SearchConfiguration, TradingCard
from AppCore.Models.LocalCardResource import LocalCardResource
from AppCore.Models.TradingCard import TradingCard
from AppCore.Observation import *
from AppCore.Observation.Events import (CardSearchEvent,
                                        LocalCardResourceSelectedEvent)
from AppCore.Service import StringFormatter
from datetime import datetime

class DataSourceCardSearchDelegate:
    def ds_started_search_with_result(self,
                                      ds: 'DataSourceCardSearch',
                                      search_configuration: SearchConfiguration):
        pass
    
    def ds_completed_search_with_result(self, 
                                        ds: 'DataSourceCardSearch',
                                        search_configuration: SearchConfiguration,
                                        error: Optional[Exception], 
                                        is_initial_load: bool) -> None:
        raise Exception

    def ds_did_retrieve_card_resource_for_card_selection(self, 
                                                         ds: 'DataSourceCardSearch') -> None:
        raise Exception

    def ds_loading_state_changed(self, 
                                 ds: 'DataSourceCardSearch') -> None:
        pass

INITIAL_PAGE = 0
INITIAL_PAGE_COUNT = 0

class DataSourceCardSearch:
    
    class CardResourceProvider:
        def __init__(self, 
                    trading_card: TradingCard,
                    configuration_manager: ConfigurationManager):
            self._trading_card = trading_card
            self._configuration_manager = configuration_manager
            self._show_front: bool = True
        
        @property
        def trading_card(self) -> TradingCard:
            return self._trading_card
        
        @property
        def is_flippable(self) -> bool:
            return self._trading_card.back_art_url is not None

        def flip(self):
            if self.is_flippable:
                self._show_front = not self._show_front
        
        @property
        def local_resource(self) -> LocalCardResource:
            if self._show_front:
                return self.front_local_resource
            else:
                if self.back_local_resource is None:
                    return self.front_local_resource
                else:
                    return self.back_local_resource
        
        @property
        def front_local_resource(self) -> LocalCardResource:
            return LocalCardResource(image_dir=self._image_path,
                                    image_preview_dir=self._image_preview_dir, 
                                    file_name=self._file_name_front,
                                    display_name=self._trading_card.friendly_display_name,
                                    display_name_short=self._trading_card.friendly_display_name_short,
                                    display_name_detailed=self._trading_card.friendly_display_name_detailed,
                                    remote_image_url=self._front_art_remote_image_url)
        
        @property
        def back_local_resource(self) -> Optional[LocalCardResource]:
            back_art_url = self._trading_card.back_art_url
            if back_art_url is None or self._file_name_back is None:
                return None
            return LocalCardResource(image_dir=self._image_path,
                                    image_preview_dir=self._image_preview_dir, 
                                    file_name=self._file_name_back,
                                    display_name=self._trading_card.friendly_display_name + ' (back)',
                                    display_name_short=self._trading_card.friendly_display_name_short + ' (back)',
                                    display_name_detailed=self._trading_card.friendly_display_name_detailed + ' (back)',
                                    remote_image_url=back_art_url)
        
        @property
        def _front_art_remote_image_url(self) -> str:
            return self._trading_card.front_art_url
        
        @property
        def _file_name_front(self) -> str:
            return self.replace_non_alphanumeric(self._trading_card.front_art_url, "_")
            
        
        @property
        def _file_name_back(self) -> Optional[str]:
            if self._trading_card.back_art_url is not None:
                return self.replace_non_alphanumeric(self._trading_card.back_art_url, "_")
            return None
        
        @property
        def _image_path(self) -> str:
            domain = urlparse(self._trading_card.front_art_url).netloc
            return f'{self._configuration_manager.configuration.cache_card_search_dir_path}{domain}/'
        
        @property
        def _image_preview_dir(self) -> str:
            domain = urlparse(self._trading_card.front_art_url).netloc
            return f'{self._configuration_manager.configuration.cache_card_search_preview_dir_path}{domain}/'
        
        def replace_non_alphanumeric(self, text: str, replacement: str = '') -> str:
            """Replaces non-alphanumeric characters in a string with a specified replacement.

            Args:
                text: The input string.
                replacement: The string to replace non-alphanumeric characters with.
                Defaults to an empty string.

            Returns:
                The modified string with non-alphanumeric characters replaced.
            """
            return re.sub(r'[^a-zA-Z0-9]', replacement, text)
    
    class DataSourceCardSearchConfiguration:
        def __init__(self, 
                     identifier: Optional[str] = None,
                     page_size: Optional[int] = None):
            self.identifier = identifier
            self.page_size = page_size if page_size is not None else 20

    def __init__(self, 
                 observation_tower: ObservationTower,
                 configuration_manager: ConfigurationManager,
                 image_resource_processor_provider: ImageResourceProcessorProviding,
                 search_client_provider: DataSourceCardSearchClientProviding, 
                 string_formatter: StringFormatter,
                 ds_configuration: Optional[DataSourceCardSearchConfiguration] = None):
        self._observation_tower = observation_tower
        self._search_client_provider = search_client_provider
        self._configuration_manager = configuration_manager
        self._image_resource_processor_provider = image_resource_processor_provider
        self._ds_configuration = ds_configuration if ds_configuration is not None else self.DataSourceCardSearchConfiguration()
        
        self._search_history_ds = DataSourceRecentSearch(self._ds_configuration.identifier,
                                                         configuration_manager, 
                                                         string_formatter)

        self.delegate: Optional[DataSourceCardSearchDelegate] = None

        self._current_page = INITIAL_PAGE
        self._page_size = self._ds_configuration.page_size
        self._current_search_configuration: Optional[SearchConfiguration] = None
        # stateful variables
        self._selected_index: Optional[int] = None
        self._selected_resource: Optional[LocalCardResource] = None
        self._paginated_trading_card_providers: List[List[DataSourceCardSearch.CardResourceProvider]] = []
        self._is_loading = False
    
    @property
    def source_display_name(self) -> str:
        return self._api_client.source_display_name
    
    @property
    def _next_page(self) -> int:
        return self._current_page + 1
    
    @property
    def site_source_url(self) -> Optional[str]:
        return self._api_client.site_source_url
    
    @property
    def _api_client(self) -> DataSourceCardSearchClientProtocol:
        return self._search_client_provider.client(setting=self._configuration.search_source)
    
    @property
    def _image_resource_processor(self) -> ImageResourceProcessorProtocol:
        return self._image_resource_processor_provider.image_resource_processor
    
    @property
    def _configuration(self) -> Configuration:
        return self._configuration_manager.configuration
    
    @property
    def _trading_card_providers(self) -> List[CardResourceProvider]:
        if len(self._paginated_trading_card_providers) == 0:
            return []
        if len(self._paginated_trading_card_providers) == 1:
            return self._paginated_trading_card_providers[0]
        return reduce(lambda x, y: x + y, self._paginated_trading_card_providers)
    
    @property
    def has_more_pages(self) -> bool:
        for (idx, i) in enumerate(self._paginated_trading_card_providers):
            if len(i) == 0 and idx != 0:
                return True
        return False
    
    @property
    def trading_card_display_names(self) -> List[str]:
        result_list: List[str] = []
        for i in self._trading_cards:
            display_name = i.friendly_display_name
            if self._configuration.card_title_detail == Configuration.Settings.CardTitleDetail.SHORT:
                display_name = i.friendly_display_name_short
            elif self._configuration.card_title_detail == Configuration.Settings.CardTitleDetail.DETAILED:
                display_name = i.friendly_display_name_detailed
            result_list.append(display_name) 
        return result_list
    
    @property
    def _trading_cards(self) -> List[TradingCard]:
        return list(map(lambda x: x.trading_card, self._trading_card_providers))
    
    
    @property
    def current_card_search_resource(self) -> Optional[LocalCardResource]:
        if self._selected_resource is not None:
            return copy.deepcopy(self._selected_resource)
        return None

    def get_search_configuration_from_history(self, index: int) -> Optional[Tuple[SearchConfiguration, datetime]]:
        return self._search_history_ds.get_search_configuration_from_history(index)

    @property
    def search_list_history_display(self) -> List[str]:
        return self._search_history_ds.search_list_history_display

    def search(self, search_configuration: SearchConfiguration):
        self._is_loading = True
        initial_event = CardSearchEvent(CardSearchEvent.EventType.STARTED,
                                        CardSearchEvent.SourceType.REMOTE,
                                        copy.deepcopy(search_configuration))
        self._observation_tower.notify(initial_event)
        self._search_history_ds.save_search(search_configuration)
        if self.delegate is not None:
            self.delegate.ds_started_search_with_result(self, search_configuration)

        def completed_with_search_result(result: DataSourceCardSearchClientSearchResult):
            response, error = result
            if error is None and response is not None:
                assert(self._current_page == INITIAL_PAGE)
                assert(len(self._paginated_trading_card_providers) == 0)
                
                if response.page_count == 0:
                    if self.delegate is not None:
                        self.delegate.ds_completed_search_with_result(ds=self,
                                                                      search_configuration=search_configuration,
                                                                      error=None,
                                                                      is_initial_load=True)
                    return
                
                for _ in range(response.page_count):
                    self._paginated_trading_card_providers.append([])
                
                def create_trading_card_resource(trading_card: TradingCard):
                    return self.CardResourceProvider(trading_card, 
                                                self._configuration_manager)
                card_providers = list(map(create_trading_card_resource, response.trading_card_list))
                
                
                self._paginated_trading_card_providers[response.page - 1] = card_providers
                self._current_page = response.page
                self._current_search_configuration = search_configuration
                
                if self.delegate is not None:
                    self.delegate.ds_completed_search_with_result(ds=self,
                                                                  search_configuration=search_configuration,
                                                                  error=None, 
                                                                  is_initial_load=True)
            else:
                if self.delegate is not None:
                    self.delegate.ds_completed_search_with_result(ds=self,
                                                                  search_configuration=search_configuration,
                                                                  error=error, 
                                                                  is_initial_load=True)
            self._is_loading = False
            finished_event = CardSearchEvent(CardSearchEvent.EventType.FINISHED,
                                         CardSearchEvent.SourceType.REMOTE,
                                         copy.deepcopy(search_configuration))
            finished_event.predecessor = initial_event
            self._observation_tower.notify(finished_event)
            if self.delegate is not None:
                self.delegate.ds_loading_state_changed(self)
            
        # reset search state
        self._current_page = INITIAL_PAGE
        self._paginated_trading_card_providers = []
        self._current_search_configuration = None
        assert(self._current_page == INITIAL_PAGE)
        assert(len(self._paginated_trading_card_providers) == 0)
        
        self._api_client.search(search_configuration, 
                                PaginationConfiguration(self._next_page, self._page_size), 
                                completed_with_search_result)
        
    def load_next_page(self):
        if self._is_loading:
            print('currently performing pagination')
            return
        current_search_configuration = self._current_search_configuration
        if current_search_configuration is None:
            print('no configuration')
            return
        if self._next_page > len(self._paginated_trading_card_providers):
            print('no more pages to load')
            return
        
        def completed_with_search_result(result: DataSourceCardSearchClientSearchResult):
            response, error = result
            if error is None and response is not None:
                
                def create_trading_card_resource(trading_card: TradingCard):
                    return self.CardResourceProvider(trading_card,
                                                     self._configuration_manager)
                card_providers = list(map(create_trading_card_resource, response.trading_card_list))
                
                self._paginated_trading_card_providers[response.page - 1] = card_providers
                self._current_page = response.page
                
                if self.delegate is not None:
                    self.delegate.ds_completed_search_with_result(ds=self,
                                                                  search_configuration=current_search_configuration,
                                                                  error=None, 
                                                                  is_initial_load=False)
            else:
                if self.delegate is not None:
                    self.delegate.ds_completed_search_with_result(ds=self,
                                                                  search_configuration=current_search_configuration,
                                                                  error=error,
                                                                  is_initial_load=False)
                    
            self._is_loading = False
        
        self._is_loading = True
        self._api_client.search(current_search_configuration, 
                                PaginationConfiguration(self._next_page, self._page_size), 
                                completed_with_search_result)
        print(f'loading next page: {self._next_page}')

    @property
    def current_previewed_trading_card_is_flippable(self) -> bool:
        if self._selected_index is not None and self._selected_index < len(self._trading_card_providers):
            return self._trading_card_providers[self._selected_index].is_flippable
        return False

    def select_card_resource_for_card_selection(self, index: int):
        if index < len(self._trading_card_providers):
            self._selected_index = index
            self._retrieve_card_resource_for_card_selection(index)

    def flip_current_previewed_card(self):
        if self._selected_index is not None and self.current_previewed_trading_card_is_flippable:
            self._trading_card_providers[self._selected_index].flip()
            self._retrieve_card_resource_for_card_selection(self._selected_index)
    
    def redownload_currently_selected_card_resource(self):
        if self._selected_index is not None:
            self._retrieve_card_resource_for_card_selection(self._selected_index, True)

    def _retrieve_card_resource_for_card_selection(self, index: int, retry: bool = False):
        trading_card_resource_provider = self._trading_card_providers[index]
        selected_resource = trading_card_resource_provider.local_resource
        self._selected_resource = selected_resource
        self._observation_tower.notify(LocalCardResourceSelectedEvent(selected_resource))
        self._image_resource_processor_provider.image_resource_processor.async_store_local_resource(selected_resource, retry)
        if self.delegate is not None:
            self.delegate.ds_did_retrieve_card_resource_for_card_selection(self)
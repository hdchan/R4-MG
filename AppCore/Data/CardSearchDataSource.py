import copy
from typing import List, Optional
from functools import reduce
from AppCore.Data.APIClientProtocol import *
from AppCore.Data.LocalResourceDataSourceProtocol import *
from AppCore.Image.ImageResourceProcessorProtocol import *
from AppCore.Models import LocalCardResource, SearchConfiguration, TradingCard
from AppCore.Observation import *
from AppCore.Observation.Events import SearchEvent, LocalResourceSelectedEvent
from AppCore.Resource import CardResourceProvider
from AppCore.CoreDependencyProviding import CoreDependencyProviding


class CardSearchDataSourceDelegate:
    def ds_completed_search_with_result(self, 
                                        ds: ...,
                                        error: Optional[Exception], 
                                        is_initial_load: bool, 
                                        has_more_pages: bool) -> None:
        pass

    def ds_did_retrieve_card_resource_for_card_selection(self, ds: ..., local_resource: LocalCardResource, is_flippable: bool) -> None:
        pass

INITIAL_PAGE = 0
INITIAL_PAGE_COUNT = 0

class CardSearchDataSource(LocalResourceDataSourceProtocol):
    def __init__(self, 
                 core_dependency_providing: CoreDependencyProviding, 
                 api_client_provider: APIClientProviding, 
                 page_size: int):
        self._observation_tower = core_dependency_providing.observation_tower
        self._api_client_provider = api_client_provider
        self._configuration_manager = core_dependency_providing.configuration_manager
        self._card_image_source_provider = core_dependency_providing.image_source_provider
        self._image_resource_processor_provider = core_dependency_providing.image_resource_processor_provider

        self.delegate: Optional[CardSearchDataSourceDelegate] = None

        self._current_page = INITIAL_PAGE
        self._page_size = page_size
        self._current_search_configuration: Optional[SearchConfiguration] = None
        # stateful variables
        self._selected_index: Optional[int] = None
        self._selected_resource: Optional[LocalCardResource] = None
        self._paginated_trading_card_providers: List[List[CardResourceProvider]] = []
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
    def _api_client(self) -> APIClientProtocol:
        return self._api_client_provider.client
    
    @property
    def _image_resource_processor(self) -> ImageResourceProcessorProtocol:
        return self._image_resource_processor_provider.image_resource_processor
    
    @property
    def _trading_card_providers(self) -> List[CardResourceProvider]:
        if len(self._paginated_trading_card_providers) == 0:
            return []
        if len(self._paginated_trading_card_providers) == 1:
            return self._paginated_trading_card_providers[0]
        return reduce(lambda x, y: x + y, self._paginated_trading_card_providers)
    
    @property
    def _has_more_pages(self) -> bool:
        for (idx, i) in enumerate(self._paginated_trading_card_providers):
            if len(i) == 0 and idx is not 0:
                return True
        return False
    
    @property
    def trading_cards(self) -> List[TradingCard]:
        return list(map(lambda x: x.trading_card, self._trading_card_providers))

    @property
    def selected_local_resource(self) -> Optional[LocalCardResource]:
        if self._selected_resource is not None:
            return self._selected_resource
        return None
    
    @property
    def current_card_search_resource(self) -> Optional[LocalCardResource]:
        if self._selected_resource is not None:
            return copy.deepcopy(self._selected_resource)
        return None

    def search(self, search_configuration: SearchConfiguration):
        initial_event = SearchEvent(SearchEvent.EventType.STARTED,
                                    copy.deepcopy(search_configuration))
        self._observation_tower.notify(initial_event) # TODO: need way to identify which data source is making call

        def completed_with_search_result(result: APIClientSearchResult):
            response, error = result
            if error is None and response is not None:
                assert(self._current_page == INITIAL_PAGE)
                assert(len(self._paginated_trading_card_providers) == 0)
                
                if response.page_count == 0:
                    if self.delegate is not None:
                        self.delegate.ds_completed_search_with_result(self,
                                                                      None,
                                                                      True,
                                                                      False)
                    return
                
                for _ in range(response.page_count):
                    self._paginated_trading_card_providers.append([])
                
                def create_trading_card_resource(trading_card: TradingCard):
                    return CardResourceProvider(trading_card, 
                                                self._configuration_manager,
                                                self._card_image_source_provider)
                card_providers = list(map(create_trading_card_resource, response.trading_card_list))
                
                
                self._paginated_trading_card_providers[response.page - 1] = card_providers
                self._current_page = response.page
                self._current_search_configuration = search_configuration
                
                if self.delegate is not None:
                    self.delegate.ds_completed_search_with_result(self,
                                                                  None, 
                                                                  True, 
                                                                  self._has_more_pages)
            else:
                if self.delegate is not None:
                    self.delegate.ds_completed_search_with_result(self,
                                                                  error, 
                                                                  True, 
                                                                  self._has_more_pages)
            finished_event = SearchEvent(SearchEvent.EventType.FINISHED,
                                         copy.deepcopy(search_configuration))
            finished_event.predecessor = initial_event
            self._observation_tower.notify(finished_event)
            self._is_loading = False
            
        self._is_loading = True
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
        if self._current_search_configuration is None:
            print('no configuration')
            return
        if self._next_page > len(self._paginated_trading_card_providers):
            print('no more pages to load')
            return
        
        def completed_with_search_result(result: APIClientSearchResult):
            response, error = result
            if error is None and response is not None:
                
                def create_trading_card_resource(trading_card: TradingCard):
                    return CardResourceProvider(trading_card, 
                                                self._configuration_manager,
                                                self._card_image_source_provider)
                card_providers = list(map(create_trading_card_resource, response.trading_card_list))
                
                self._paginated_trading_card_providers[response.page - 1] = card_providers
                self._current_page = response.page
                
                if self.delegate is not None:
                    self.delegate.ds_completed_search_with_result(self,
                                                                  None, 
                                                                  False, 
                                                                  self._has_more_pages)
            else:
                if self.delegate is not None:
                    self.delegate.ds_completed_search_with_result(self,
                                                                  error,
                                                                  False,
                                                                  self._has_more_pages)
                    
            self._is_loading = False
        
        self._is_loading = True
        self._api_client.search(self._current_search_configuration, 
                                PaginationConfiguration(self._next_page, self._page_size), 
                                completed_with_search_result)
        print(f'loading next page: {self._next_page}')

    def current_previewed_trading_card_is_flippable(self) -> bool:
        if self._selected_index is not None:
            return self._trading_card_providers[self._selected_index].is_flippable
        return False

    def select_card_resource_for_card_selection(self, index: int):
        if index < len(self._trading_card_providers):
            self._selected_index = index
            self._retrieve_card_resource_for_card_selection(index)

    def flip_current_previewed_card(self):
        if self._selected_index is not None and self.current_previewed_trading_card_is_flippable():
            self._trading_card_providers[self._selected_index].flip()
            self._retrieve_card_resource_for_card_selection(self._selected_index)
    
    def redownload_currently_selected_card_resource(self):
        if self._selected_index is not None:
            self._retrieve_card_resource_for_card_selection(self._selected_index, True)

    def _retrieve_card_resource_for_card_selection(self, index: int, retry: bool = False):
        trading_card_resource_provider = self._trading_card_providers[index]
        selected_resource = trading_card_resource_provider.local_resource
        self._selected_resource = selected_resource
        self._observation_tower.notify(LocalResourceSelectedEvent(selected_resource))
        self._image_resource_processor_provider.image_resource_processor.async_store_local_resource(selected_resource, retry)
        if self.delegate is not None:
            self.delegate.ds_did_retrieve_card_resource_for_card_selection(self, copy.deepcopy(selected_resource), trading_card_resource_provider.is_flippable)
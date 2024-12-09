import copy
from typing import List, Optional, Tuple

from AppCore.Data.APIClientProtocol import *
from AppCore.Data.LocalResourceDataSourceProtocol import *
from AppCore.Image.ImageResourceProcessorProtocol import *
from AppCore.Models import LocalCardResource, SearchConfiguration, TradingCard
from AppCore.Observation import *
from AppCore.Observation.Events import SearchEvent, LocalResourceSelectedEvent
from AppCore.Resource import CardResourceProvider
from AppCore.CoreDependencyProviding import CoreDependencyProviding


class CardSearchDataSourceDelegate:
    def ds_completed_search_with_result(self, ds: ..., result_list: List[TradingCard], error: Optional[Exception]) -> None:
        pass

    def ds_did_retrieve_card_resource_for_card_selection(self, ds: ..., local_resource: LocalCardResource, is_flippable: bool) -> None:
        pass

class CardSearchDataSource(LocalResourceDataSourceProtocol, LocalResourceDataSourceProviding):
    def __init__(self, 
                 core_dependency_providing: CoreDependencyProviding, 
                 api_client_provider: APIClientProviding):
        self._observation_tower = core_dependency_providing.observation_tower
        self._api_client_provider = api_client_provider
        self._configuration_provider = core_dependency_providing.configuration_provider
        self._card_image_source_provider = core_dependency_providing.image_source_provider
        self._image_resource_processor_provider = core_dependency_providing.image_resource_processor_provider

        self.delegate: Optional[CardSearchDataSourceDelegate]

        # stateful variables
        self._search_configuration = SearchConfiguration()
        self._selected_index: Optional[int] = None
        self._selected_resource: Optional[LocalCardResource] = None
        self._trading_card_providers: List[CardResourceProvider] = []
        
    @property
    def _api_client(self) -> APIClientProtocol:
        return self._api_client_provider.client
    
    @property
    def _image_resource_processor(self) -> ImageResourceProcessorProtocol:
        return self._image_resource_processor_provider.image_resource_processor

    @property
    def data_source(self) -> LocalResourceDataSourceProtocol:
        return self

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
        self._observation_tower.notify(SearchEvent(SearchEvent.EventType.STARTED,
                                                  copy.deepcopy(search_configuration)))

        def completed_with_search_result(result: Tuple[Optional[List[TradingCard]], Optional[Exception]]):
            result_list, error = result
            
            if error is None and result_list is not None:
                def create_trading_card_resource(trading_card: TradingCard):
                    return CardResourceProvider(trading_card, 
                                                self._configuration_provider,
                                                self._card_image_source_provider)
                self._trading_card_providers = list(map(create_trading_card_resource, result_list))
                if self.delegate is not None:
                    self.delegate.ds_completed_search_with_result(self, result_list, None)
            else:
                if self.delegate is not None:
                    self.delegate.ds_completed_search_with_result(self, [], error)
                    
            self._observation_tower.notify(SearchEvent(SearchEvent.EventType.FINISHED,
                                                      copy.deepcopy(search_configuration)))

        self._api_client.search(search_configuration, completed_with_search_result)

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
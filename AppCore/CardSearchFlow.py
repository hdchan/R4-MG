from typing import List, Optional

from .Data import (APIClientProvider, CardDataSource, CardDataSourceDelegate,
                   TradingCard)
from .Image import (ImageFetcherProvider, ImageResourceCacher,
                    ImageResourceCacherDelegate)
from .Models import TradingCard, SearchConfiguration
from .Observation import ObservationTower
from .Observation.Events import *


class CardSearchFlowDelegate:
    def sf_did_complete_search(self, sf: ..., result_list: List[str], error: Optional[Exception]) -> None:
        pass
    
    def sf_did_retrieve_card_resource_for_card_selection(self, sf: ..., local_resource: LocalCardResource, is_flippable: bool) -> None:
        pass

    def sf_did_finish_storing_local_resource(self, sf: ..., local_resource: LocalCardResource) -> None:
        pass
    
    def sf_did_update_search_configuration(self, sf: ..., search_configuration: SearchConfiguration) -> None:
        pass
    
class CardSearchFlow(CardDataSourceDelegate, ImageResourceCacherDelegate):
    def __init__(self, 
                 observation_tower: ObservationTower, 
                 api_client_provider: APIClientProvider,
                 image_fetcher_provider: ImageFetcherProvider, 
                 configuration: Configuration):
        self._data_source = CardDataSource(api_client_provider)
        self._data_source.delegate = self
        self._resource_cacher = ImageResourceCacher(image_fetcher_provider, 
                                                    configuration)
        self._resource_cacher.delegate = self
        
        self._observation_tower = observation_tower
        self.current_card_search_resource: Optional[LocalCardResource] = None
        self.delegate: Optional[CardSearchFlowDelegate]

    # MARK: - Datasource
    @property
    def search_configuration(self) -> SearchConfiguration:
        return self._data_source.search_configuration

    def search(self, card_name: str):
        self._data_source.search(card_name)
    
    def user_update_search_configuration(self, search_config: SearchConfiguration):
        self._data_source.update_search_configuration(search_config)
        
    def system_update_search_configuration(self, search_config: SearchConfiguration):
        self._data_source.update_search_configuration(search_config)
        if self.delegate is not None:
            self.delegate.sf_did_update_search_configuration(self, search_config)

    def select_card_resource_for_card_selection(self, index: int):
        self._data_source.select_card_resource_for_card_selection(index)

    def flip_current_previewed_card(self):
        self._data_source.flip_current_previewed_card()

    def current_previewed_trading_card_is_flippable(self) -> bool:
        return self._data_source.current_previewed_trading_card_is_flippable()

    # MARK: - DS Delegate methods
    def ds_completed_search_with_result(self, ds: CardDataSource, result_list: List[TradingCard], error: Optional[Exception]):
        self._resource_cacher.attach_local_resources(result_list)
        if self.delegate is not None:
            display_name_list = list(map(lambda x: x.friendly_display_name, result_list))
            self.delegate.sf_did_complete_search(self, display_name_list, error)

    def ds_did_retrieve_card_resource_for_card_selection(self, ds: CardDataSource, trading_card: TradingCard):
        self._resource_cacher.async_store_local_resource(trading_card)
        self.current_card_search_resource = trading_card.local_resource
        if self.delegate is not None:
            self.delegate.sf_did_retrieve_card_resource_for_card_selection(self, trading_card.local_resource, trading_card.is_flippable)
        

    # MARK: - Resource Cacher Delegate
    def rc_did_finish_storing_local_resource(self, rc: ImageResourceCacher, local_resource: LocalCardResource):
        self._observation_tower.notify(LocalResourceReadyEvent(local_resource))
        if self.delegate is not None:
            self.delegate.sf_did_finish_storing_local_resource(self, local_resource)
from typing import List, Tuple, Optional

from AppCore.Data import APIClientProtocol, APIClientProvider
from AppCore.Models import TradingCard, SearchConfiguration
from AppCore.Observation import ObservationTower
from AppCore.Observation.Events import SearchEvent
class CardDataSourceDelegate:
    def ds_completed_search_with_result(self, ds: ..., result_list: List[TradingCard], error: Optional[Exception]) -> None:
        pass
    
    def ds_did_retrieve_card_resource_for_card_selection(self, ds: ..., trading_card: TradingCard) -> None:
        pass
    

class CardDataSource:
    def __init__(self,
                 observation_tower: ObservationTower,
                 api_client_provider: APIClientProvider):
        self.observation_tower = observation_tower
        self.api_client_provider: APIClientProvider = api_client_provider
        self.delegate: Optional[CardDataSourceDelegate]
        self.current_previewed_trading_card: Optional[TradingCard] = None
        self._current_trading_cards_list: List[TradingCard] = []
        self._search_configuration = SearchConfiguration()
        
    @property
    def api_client(self) -> APIClientProtocol:
        return self.api_client_provider.provideClient()
    
    @property
    def search_configuration(self) -> SearchConfiguration:
        return self._search_configuration

    def search(self, card_name: str, is_system_initiated: bool = False):
        self.observation_tower.notify(SearchEvent(SearchEvent.EventType.STARTED, is_system_initiated))

        def completed_with_search_result(result: Tuple[Optional[List[TradingCard]], Optional[Exception]]):
            self._current_trading_cards_list = []
            result_list, error = result
            
            if error is None and result_list is not None:
                self._current_trading_cards_list = result_list
                if self.delegate is not None:
                    self.delegate.ds_completed_search_with_result(self, result_list, None)
            else:
                if self.delegate is not None:
                    self._current_trading_cards_list = []
                    self.delegate.ds_completed_search_with_result(self, [], error)
                    
            self.observation_tower.notify(SearchEvent(SearchEvent.EventType.FINISHED, is_system_initiated))

        self.api_client.search(card_name, self.search_configuration, completed_with_search_result)
        
    def update_search_configuration(self, search_config: SearchConfiguration):
        self._search_configuration = search_config
    
    def select_card_resource_for_card_selection(self, index: int):
        if index < len(self._current_trading_cards_list):
            trading_card = self._current_trading_cards_list[index]
            self.current_previewed_trading_card = trading_card
            if self.delegate is not None:
                self.delegate.ds_did_retrieve_card_resource_for_card_selection(self, trading_card)

    def current_previewed_trading_card_is_flippable(self) -> bool:
        if self.current_previewed_trading_card is not None:
            return self.current_previewed_trading_card.is_flippable
        return False
    
    def flip_current_previewed_card(self):
        if self.current_previewed_trading_card is not None and self.current_previewed_trading_card_is_flippable():
            self.current_previewed_trading_card.flip()
            trading_card = self.current_previewed_trading_card
            if self.delegate is not None:
                self.delegate.ds_did_retrieve_card_resource_for_card_selection(self, trading_card)
        
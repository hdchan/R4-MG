from typing import List, Tuple

from AppCore.Data import APIClientProtocol, APIClientProvider
from AppCore.Models.TradingCard import *

class CardDataSourceDelegate:
    def ds_completed_search_with_result(self, ds: ..., result_list: List[TradingCard], error: Optional[Exception]) -> None:
        pass
    
    def ds_did_retrieve_card_resource_for_card_selection(self, ds: ..., trading_card: TradingCard) -> None:
        pass
    

class CardDataSource:
    def __init__(self, 
                 api_client_provider: APIClientProvider):
        self.api_client_provider: APIClientProvider = api_client_provider
        self.delegate: Optional[CardDataSourceDelegate]
        self.current_previewed_trading_card: Optional[TradingCard] = None
        self._current_trading_cards_list: List[TradingCard] = []
    
    @property
    def api_client(self) -> APIClientProtocol:
        return self.api_client_provider.provideClient()

    def search(self, query: str):
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

        self.api_client.search(query, completed_with_search_result)
        
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
        
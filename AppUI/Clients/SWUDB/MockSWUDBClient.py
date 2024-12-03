  
import json
from typing import List, Dict, Any, Optional

from AppCore.Data.APIClientProtocol import (APIClientProtocol,
                                       APIClientSearchCallback)
from AppCore.Models import TradingCard, SearchConfiguration, CardType
from AppCore.Network import MockNetworker
from AppCore.Clients.SWUDB.SWUTradingCard import SWUTradingCard
from ...Assets import AssetProvider
CardListData = List[Dict[str, Any]]
class MockSWUDBClient(APIClientProtocol):
    def __init__(self, mock_networker: MockNetworker, asset_provider: AssetProvider):
        self.mock_networker = mock_networker
        self.asset_provider = asset_provider
        self.__response_card_list: Optional[List[TradingCard]] = None
    
    @property
    def site_source_url(self) -> str:
        return "Local (SOR, SHD, TWI)"

    def search(self, search_configuration: SearchConfiguration, callback: APIClientSearchCallback):
        def completed_search():
            self._perform_search(search_configuration, callback)
        print(f'Mock search. card_name: {search_configuration.card_name}, search_configuration: {search_configuration}')
        self.mock_networker.load_mock(completed_search)
    
    def _perform_search(self, search_configuration: SearchConfiguration, callback: APIClientSearchCallback):
        def filter_the_result(card: TradingCard):
            return (search_configuration.card_name.lower() in card.name.lower() and 
                    (search_configuration.card_type.value.lower() == card.type.lower() or search_configuration.card_type == CardType.UNSPECIFIED))
        def sort_the_result(card: TradingCard):
            return card.name
        filtered_list = list(filter(filter_the_result, self._response_card_list))
        filtered_list.sort(key=sort_the_result)
        callback((filtered_list, None))
        
    @property
    def _response_card_list(self) -> List[TradingCard]:
        if self.__response_card_list is None:
            # TODO: needs to be referenced in package, otherwise crashes on distribution
            with open(self.asset_provider.data.sor_set_path, 'r') as file, open(self.asset_provider.data.shd_set_path) as file2, open(self.asset_provider.data.twi_set_path) as file3:
                sor_response = json.load(file)['data']
                shd_response = json.load(file2)['data']
                twi_response = json.load(file3)['data']
                response_data = sor_response + shd_response + twi_response
                result_list: List[TradingCard] = []
                for i in response_data:
                    swu_card = SWUTradingCard.from_swudb_response(i)
                    result_list.append(swu_card)
                self.__response_card_list = result_list
        return self.__response_card_list or []
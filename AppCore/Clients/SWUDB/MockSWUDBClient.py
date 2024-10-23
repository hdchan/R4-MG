  
import json
from typing import List

from ...Data.APIClientProtocol import (APIClientProtocol,
                                       APIClientSearchCallback)
from ...Models import TradingCard, SearchConfiguration
from ...Network import MockNetworker
from .SWUTradingCard import SWUTradingCard


class MockSWUDBClient(APIClientProtocol):
    def __init__(self, mock_networker: MockNetworker):
        self.mock_networker = mock_networker
        
    def search(self, card_name: str, search_configuration: SearchConfiguration, callback: APIClientSearchCallback):
        def completed_search():
            # TODO: needs to be referenced in package, otherwise crashes on distribution
            with open('./AppCore/Clients/SWUDB/sor.json', 'r') as file:
                json_response = json.load(file)
                result_list: List[TradingCard] = []
                for i in json_response['data']:
                    swu_card = SWUTradingCard.from_swudb_response(i)
                    result_list.append(swu_card)
                callback((result_list, None))
        print(f'Mock search. card_name: {card_name}, search_configuration: {search_configuration}')
        self.mock_networker.load_mock(completed_search)
        
        
        
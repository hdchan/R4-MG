  
import json
from typing import Any, Dict, List, Optional

from AppCore.Data.APIClientProtocol import (APIClientProtocol,
                                            APIClientSearchCallback, APIClientSearchResponse)
from AppCore.Models import SearchConfiguration, TradingCard
from AppCore.Network import LocalNetworker

from ...Assets import AssetProvider
from AppCore.Models import CardType, PaginationConfiguration
from ..SWUCardSearchConfiguration import SWUCardSearchConfiguration
from .SWUTradingCard import SWUTradingCard

CardListData = List[Dict[str, Any]]
class SWUDBAPILocalClient(APIClientProtocol):
    def __init__(self, mock_networker: LocalNetworker, asset_provider: AssetProvider):
        self.mock_networker = mock_networker
        self.asset_provider = asset_provider
        self.__response_card_list: Optional[List[TradingCard]] = None
    
    @property
    def source_display_name(self) -> str:
        return "Local Search + www.swu-db.com Images (Set 1-4)"
    
    @property
    def site_source_url(self) -> Optional[str]:
        return None

    def search(self, search_configuration: SearchConfiguration,
               pagination_configuration: Optional[PaginationConfiguration],
               callback: APIClientSearchCallback):
        def completed_search():
            self._perform_search(search_configuration, callback)
        print(f'Mock search. card_name: {search_configuration.card_name}, search_configuration: {search_configuration}')
        self.mock_networker.load_mock(completed_search)
    
    def _perform_search(self, search_configuration: SearchConfiguration, callback: APIClientSearchCallback):
        swu_search_config = SWUCardSearchConfiguration.from_search_configuration(search_configuration)
        def filter_the_result(card: TradingCard):
            return (swu_search_config.card_name.lower() in card.name.lower() and 
                    (swu_search_config.card_type.value.lower() == card.type.lower() or swu_search_config.card_type == CardType.UNSPECIFIED))
        def sort_the_result(card: TradingCard):
            return card.name
        filtered_list = list(filter(filter_the_result, self._response_card_list))
        filtered_list.sort(key=sort_the_result)
        result = APIClientSearchResponse(filtered_list)
        callback((result, None))
        
    @property
    def _response_card_list(self) -> List[TradingCard]:
        if self.__response_card_list is None:
            with open(self.asset_provider.data.sor_set_path, 'r') as file, open(self.asset_provider.data.shd_set_path) as file2, open(self.asset_provider.data.twi_set_path) as file3, open(self.asset_provider.data.jtl_set_path) as file4:
                sor_response = json.load(file)['data']
                shd_response = json.load(file2)['data']
                twi_response = json.load(file3)['data']
                jtl_response = json.load(file4)['data']
                response_data = sor_response + shd_response + twi_response + jtl_response
                result_list: List[TradingCard] = []
                for i in response_data:
                    swu_card = SWUTradingCard.from_swudb_response(i)
                    result_list.append(swu_card)
                self.__response_card_list = result_list
        return self.__response_card_list or []
  
import json
from typing import Any, Dict, List, Optional

from AppCore.Data.APIClientProtocol import (APIClientProtocol,
                                            APIClientSearchCallback,
                                            APIClientSearchResponse,
                                            APIClientSearchResult)
from AppCore.Models import (CardType, PaginationConfiguration,
                            SearchConfiguration, TradingCard)
from AppCore.Network import NetworkerLocal
from AppUI.Assets import AssetProvider

from ..SWUCardSearchConfiguration import SWUCardSearchConfiguration
from .SWUTradingCard import SWUTradingCard

CardListData = List[Dict[str, Any]]
class SWUDBAPILocalClient(APIClientProtocol):
    def __init__(self, local_networker: NetworkerLocal, asset_provider: AssetProvider):
        self.local_networker = local_networker
        self.asset_provider = asset_provider
        self.__response_card_list: Optional[List[TradingCard]] = None
    
    @property
    def source_display_name(self) -> str:
        return "Local Search + www.swu-db.com Images (Set 1-4)"
    
    @property
    def site_source_url(self) -> Optional[str]:
        return None

    def search(self, 
               search_configuration: SearchConfiguration,
               pagination_configuration: Optional[PaginationConfiguration],
               callback: APIClientSearchCallback):
        def completed_search(result: APIClientSearchResult):
            callback(result)
        self.local_networker.load(self._perform_search, completed_search, search_configuration=search_configuration)
    
    def _perform_search(self, args: Any) -> APIClientSearchResult:
        search_configuration: SearchConfiguration = args.get('search_configuration')
        print(f'Mock search. card_name: {search_configuration.card_name}, search_configuration: {search_configuration}')
        swu_search_config = SWUCardSearchConfiguration.from_search_configuration(search_configuration)
        def filter_the_result(card: TradingCard):
            return (swu_search_config.card_name.lower() in card.name.lower() and 
                    (swu_search_config.card_type.value.lower() == card.type.lower() or swu_search_config.card_type == CardType.UNSPECIFIED))
        def sort_the_result(card: TradingCard):
            return card.name
        filtered_list = list(filter(filter_the_result, self._response_card_list))
        filtered_list.sort(key=sort_the_result)
        result = APIClientSearchResponse(filtered_list)
        return (result, None)
        
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
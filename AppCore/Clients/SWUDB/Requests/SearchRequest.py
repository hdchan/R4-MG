from ....Models import TradingCard, SearchConfiguration, CardType
from ....Network import NetworkRequestProtocol
from ..SWUTradingCard import SWUTradingCard
import urllib.parse
from typing import Any, Dict, List, Optional
from urllib.request import Request

# https://api.swu-db.com/cards/search?q=type:leader%20name:luke
class SearchRequest(NetworkRequestProtocol[List[TradingCard]]):
        SWUDB_API_ENDPOINT = 'https://api.swu-db.com/cards/search'
        
        def __init__(self, card_name: str, search_configuration: SearchConfiguration):
            self.card_name = card_name
            self.search_configuration = search_configuration
        
        def request(self) -> Optional[Request]:
            card_name = self.card_name
            params: List[str] = []
            if card_name.replace(" ", '') != "":
                params.append(f'name:{card_name}')
            if self.search_configuration.card_type is not CardType.UNSPECIFIED:
                params.append(f'type:{self.search_configuration.card_type.value}')
            
            if len(params) == 0:
                return None
            
            q = urllib.parse.quote_plus(' '.join(params))
            
            url = f'{self.SWUDB_API_ENDPOINT}?q={q}&format=json'
            print(url)
            return Request(url)
        
        def response(self, json: Dict[str, Any]) -> List[TradingCard]:
            result_list: List[TradingCard] = []
            for i in json['data']:
                swu_card = SWUTradingCard.from_swudb_response(i)
                result_list.append(swu_card)
            return result_list
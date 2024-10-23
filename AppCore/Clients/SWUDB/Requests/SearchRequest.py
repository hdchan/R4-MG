import urllib.parse
from typing import Any, Dict, List, Optional
from urllib.request import Request

from ....Models import CardAspect, CardType, SearchConfiguration, TradingCard
from ....Network import NetworkRequestProtocol
from ..SWUTradingCard import SWUTradingCard


# https://api.swu-db.com/cards/search?q=type:leader%20name:luke
class SearchRequest(NetworkRequestProtocol[List[TradingCard]]):
        SWUDB_API_ENDPOINT = 'https://api.swu-db.com/cards/search'
        
        def __init__(self, search_configuration: SearchConfiguration):
            self.search_configuration = search_configuration
        
        def __eq__(self, other):  # type: ignore
            if not isinstance(other, SearchRequest):
                # don't attempt to compare against unrelated types
                return NotImplemented

            return (self.search_configuration == other.search_configuration)
        
        def request(self) -> Optional[Request]:
            params: List[str] = []
            if self.search_configuration.card_name.replace(" ", '') != "":
                params.append(f'name:{self.search_configuration.card_name}')
            if self.search_configuration.card_type is not CardType.UNSPECIFIED:
                params.append(f'type:{self.search_configuration.card_type.value}')
                
            card_aspect_query_str = self.card_aspect_query_string(self.search_configuration.card_aspects)
            if card_aspect_query_str is not None:
                params.append(f'a:{card_aspect_query_str}')
            
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
        
        def card_aspect_query_string(self, card_aspects: List[CardAspect]) -> Optional[str]:
            if len(card_aspects) > 0:
                result = ""
                for a in card_aspects:
                    if a == CardAspect.VIGILANCE:
                        result += "B"
                    elif a == CardAspect.COMMAND:
                        result += "G"
                    elif a == CardAspect.AGGRESSION:
                        result += "R"
                    elif a == CardAspect.CUNNING:
                        result += "Y"
                    elif a == CardAspect.HEROISM:
                        result += "W"
                    elif a == CardAspect.VILLAINY:
                        result += "K"
                return result
            return None
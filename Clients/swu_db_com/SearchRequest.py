import urllib.parse
from typing import Any, Dict, List, Optional
from urllib.request import Request

from AppCore.Models import TradingCard
from AppCore.DataFetcher import DataFetcherRemoteRequestProtocol
from AppCore.DataSource import DataSourceCardSearchClientSearchResponse

from Clients.Models.CardType import CardType
from ..Models.SWUCardSearchConfiguration import SWUCardSearchConfiguration
from .SWUDBTradingCard import SWUDBTradingCard

# https://api.swu-db.com/cards/search?q=type:leader%20name:luke
class SearchRequest(DataFetcherRemoteRequestProtocol[DataSourceCardSearchClientSearchResponse]):
        SWUDB_API_ENDPOINT = 'https://api.swu-db.com/cards/search'
        
        def __init__(self, 
                     search_configuration: SWUCardSearchConfiguration):
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
            
            if len(params) == 0:
                return None
            
            q = urllib.parse.quote_plus(' '.join(params))
            
            url = f'{self.SWUDB_API_ENDPOINT}?q={q}&format=json'
            print(url)
            return Request(url)
        
        def response(self, json: Dict[str, Any]) -> DataSourceCardSearchClientSearchResponse:
            result_list: List[TradingCard] = []
            for i in json['data']:
                swu_card = SWUDBTradingCard.from_swudb_response(i)
                result_list.append(swu_card)
            return DataSourceCardSearchClientSearchResponse(result_list)
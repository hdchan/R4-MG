from ....Models.TradingCard import TradingCard
from ....Network import NetworkRequestProtocol
from ..SWUTradingCard import SWUTradingCard
import urllib.parse
from typing import Any, Dict, List
from urllib.request import Request


class SearchRequest(NetworkRequestProtocol[List[TradingCard]]):
        SWUDB_API_ENDPOINT = 'https://api.swu-db.com/cards/search'
        
        def __init__(self, query: str):
            self.query = query
        
        def request(self) -> Request:
            query = urllib.parse.quote_plus(self.query)
            url = f'{self.SWUDB_API_ENDPOINT}?q=name:{query}&format=json'
            return Request(url)
        def response(self, json: Dict[str, Any]) -> List[TradingCard]:
            result_list: List[TradingCard] = []
            for i in json['data']:
                swu_card = SWUTradingCard.from_swudb_response(i)
                result_list.append(swu_card)
            return result_list
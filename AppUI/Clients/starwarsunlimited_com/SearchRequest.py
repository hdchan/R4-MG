import json
from typing import Any, Dict, List, Optional
from urllib.request import Request
import urllib.parse
from AppCore.Models import TradingCard
from AppCore.Models.CardType import CardType
from AppCore.Network import NetworkRequestProtocol

from ...Assets import AssetProvider
from ..SWUCardSearchConfiguration import SWUCardSearchConfiguration
from .TradingCard import StarWarsUnlimitedTradingCard


class SearchRequest(NetworkRequestProtocol[List[TradingCard]]):
    API_ENDPOINT = "https://admin.starwarsunlimited.com/api/card-list"
    
    def __init__(self, search_configuration: SWUCardSearchConfiguration, asset_provider: AssetProvider):
            self.search_configuration = search_configuration
            self._asset_provider = asset_provider
    
    def request(self) -> Optional[Request]:
        params: List[str] = [
            
        ]
        
        # requires text to search
        if self.search_configuration.card_name.replace(" ", '') != "":
                params.append(f'filters[$and][2][$or][0][title][$containsi]={self.search_configuration.card_name}')
        
        # will still search without type filter
        if self.search_configuration.card_type is not CardType.UNSPECIFIED:
            filter_value  = self._map_card_type(self.search_configuration.card_type)
            if filter_value is not None:
                params.append(f'filters[$and][1][$or][0][type][id][$in][0]={filter_value}')
        
        if len(params) == 0:
            return None
        
        params += [
            'locale=en',
            # 'orderBy[title][id]=asc',
            'sort[0]=title:asc,expansion.sortValue:asc,cardNumber:asc',
            'pagination[page]=1&pagination[pageSize]=40' # TODO: may need to engineer pagination
        ]
        
        q = '&'.join(params)
        
        url = f'{self.API_ENDPOINT}?{q}'
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:136.0) Gecko/20100101 Firefox/136.0'}
        
        request = Request(url, headers=headers)
        return request
        # return Request('https://admin.starwarsunlimited.com/api/card-list?locale=en&orderBy[title][id]=asc&filters[$and][0][variantOf][id][$null]=true&filters[$and][1][$or][0][type][id][$in][0]=4&filters[$and][1][$or][1][type2][id][$in][0]=4&filters[$and][2][$or][0][title][$containsi]=luke&pagination[page]=1&pagination[pageSize]=100')
    
    def response(self, json: Dict[str, Any]) -> List[TradingCard]:
        data = json['data']
        result: List[TradingCard] = []
        for card in data:
            trading_card = StarWarsUnlimitedTradingCard.from_swudb_response(card)
            result.append(trading_card)
        return result
    
    
    def _map_card_type(self, card_type: CardType) -> Optional[str]:
        card_type_value = card_type.value.lower()
        with open(self._asset_provider.data.starwarsunlimited_com_filter_path, 'r') as file:
            card_types = json.load(file)['pageProps']['filters']['cardTypes']
            print(card_types)
            for t in card_types:
                if t['value'].lower() == card_type_value:
                    return f'{t.get("id")}'
            
        return None
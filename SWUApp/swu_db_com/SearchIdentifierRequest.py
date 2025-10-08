from typing import Any, Dict, Optional
from urllib.request import Request

from AppCore.DataFetcher import DataFetcherRemoteRequestProtocol
from AppCore.DataSource import DataSourceCardSearchClientSearchResponse

from ..Models.SWUCardSearchConfiguration import SWUCardSearchConfiguration
from .SWUDBTradingCard import SWUDBTradingCard

# https://api.swu-db.com/cards/search?q=type:leader%20name:luke
class SearchIdentifierRequest(DataFetcherRemoteRequestProtocol[DataSourceCardSearchClientSearchResponse]):
        SWUDB_API_ENDPOINT = 'https://api.swu-db.com/cards'
        
        def __init__(self, 
                     search_configuration: SWUCardSearchConfiguration):
            self.search_configuration = search_configuration
        
        def __eq__(self, other):  # type: ignore
            if not isinstance(other, SearchIdentifierRequest):
                # don't attempt to compare against unrelated types
                return NotImplemented

            return (self.search_configuration == other.search_configuration)
        
        def request(self) -> Optional[Request]:
            
            if self.search_configuration.card_set is None or self.search_configuration.card_number is None:
                 raise Exception
            
            url = f'{self.SWUDB_API_ENDPOINT}/{self.search_configuration.card_set}/{self.search_configuration.card_number}'
            print(url)
            return Request(url)
        
        def response(self, json: Dict[str, Any]) -> DataSourceCardSearchClientSearchResponse:
            swu_card = SWUDBTradingCard.from_swudb_response(json)
            return DataSourceCardSearchClientSearchResponse([swu_card])
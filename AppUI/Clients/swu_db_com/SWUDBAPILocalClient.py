  
import json
from typing import Any, Dict, List, Optional

from AppCore.DataFetcher import DataFetcherLocal
from AppCore.DataSource.DataSourceCardSearchClientProtocol import (
    DataSourceCardSearchClientProtocol,
    DataSourceCardSearchClientSearchCallback,
    DataSourceCardSearchClientSearchResponse,
    DataSourceCardSearchClientSearchResult)
from AppCore.Models import (PaginationConfiguration, SearchConfiguration,
                            TradingCard)
from ..Assets import AssetProvider

from ..CardType import CardType
from ..SWUCardSearchConfiguration import SWUCardSearchConfiguration
from .SWUDBTradingCard import SWUDBTradingCard

CardListData = List[Dict[str, Any]]

# TODO: Deprecate
class SWUDBAPILocalClient(DataSourceCardSearchClientProtocol):
    def __init__(self, 
                 local_fetcher: DataFetcherLocal, 
                 asset_provider: AssetProvider):
        self._local_fetcher = local_fetcher
        self._asset_provider = asset_provider
        self.__response_card_list: Optional[List[TradingCard]] = None
    
    @property
    def source_display_name(self) -> str:
        return "Local Search + www.swu-db.com Images (Set 1-5)"
    
    @property
    def site_source_url(self) -> Optional[str]:
        return None

    def search(self, 
               search_configuration: SearchConfiguration,
               pagination_configuration: Optional[PaginationConfiguration],
               callback: DataSourceCardSearchClientSearchCallback):
        print(f'Local search www.swu-db.com. card_name: {search_configuration.card_name}, search_configuration: {search_configuration}')
        def completed_search(result: DataSourceCardSearchClientSearchResult):
            callback(result)
        self._local_fetcher.load(self._perform_search, completed_search, search_configuration=search_configuration)
    
    def _perform_search(self, args: Any) -> DataSourceCardSearchClientSearchResult:
        # TODO: implement more performant search
        search_configuration: SearchConfiguration = args.get('search_configuration')
        swu_search_config = SWUCardSearchConfiguration.from_search_configuration(search_configuration)
        def filter_the_result(card: TradingCard):
            return (swu_search_config.card_name.lower() in card.name.lower() and 
                    (swu_search_config.card_type.value.lower() == card.type.lower() or swu_search_config.card_type == CardType.UNSPECIFIED))
        def sort_the_result(card: TradingCard):
            return card.name
        filtered_list = list(filter(filter_the_result, self._response_card_list))
        filtered_list.sort(key=sort_the_result)
        result = DataSourceCardSearchClientSearchResponse(filtered_list)
        return (result, None)
        
    @property
    def _response_card_list(self) -> List[TradingCard]:
        if self.__response_card_list is None:
            # retrieve from asset provider
            decks = [
                self._asset_provider.data.sor_set_path,
                self._asset_provider.data.shd_set_path,
                self._asset_provider.data.twi_set_path,
                self._asset_provider.data.jtl_set_path,
                self._asset_provider.data.lof_set_path
            ]
            result_list: List[TradingCard] = []
            for deck in decks:
                with open(deck, 'r') as file:
                    cards = json.load(file)['data']
                    for card in cards:
                        swu_card = SWUDBTradingCard.from_swudb_response(card)
                        result_list.append(swu_card)
            self.__response_card_list = result_list
                
        return self.__response_card_list or []
import json
from io import TextIOWrapper
from typing import List, Optional

from AppCore.DataFetcher import DataFetcherLocal
from AppCore.DataSource import DataSourceLocallyManagedSets
from AppCore.DataSource.DataSourceCardSearchClientProtocol import (
    DataSourceCardSearchClientProtocol,
    DataSourceCardSearchClientSearchResponse,
    DataSourceCardSearchClientSearchResult,
)
from AppCore.DataSource.DataSourceLocallyManagedSets import (
    DataSourceLocallyManagedSetsClientProtocol,
)
from AppCore.Models import PaginationConfiguration, SearchConfiguration, TradingCard

from ..Models.CardType import CardType
from ..Models.SWUCardSearchConfiguration import SWUCardSearchConfiguration
from .SWUDBTradingCard import SWUDBTradingCard


class SWUDBLocalCardRetrieverClient(DataSourceCardSearchClientProtocol):
    def __init__(self,
                 local_fetcher: DataFetcherLocal, 
                 data_source_local_managed_sets: DataSourceLocallyManagedSets):
        self._local_fetcher = local_fetcher
        self._data_source_local_managed_sets = data_source_local_managed_sets
        
    @property
    def source_display_name(self) -> str:
        return "Locally managed sets"

    @property
    def can_auto_search(self) -> bool:
        return True
    
    # MARK: - DataSourceCardSearchClientProtocol
    def search_with_result(self, 
               search_configuration: SearchConfiguration,
               pagination_configuration: Optional[PaginationConfiguration]) -> DataSourceCardSearchClientSearchResult:
        print(f'Local search www.swu-db.com. card_name: {search_configuration.card_name}, search_configuration: {search_configuration}')
        swu_search_config = SWUCardSearchConfiguration.from_search_configuration(search_configuration)
        swu_search_filtered_string = "".join(filter(str.isalnum, swu_search_config.card_name.lower()))

        # TODO: need to filter by subtitle as well? for melee.gg
        def filter_the_result(card: TradingCard):
            if swu_search_config.card_set is not None and swu_search_config.card_number is not None:
                return (card.number == swu_search_config.card_number and card.set == swu_search_config.card_set)
            else:
                if swu_search_config.card_name.strip() == "":
                    return False # don't return all cards if no search string
                card_filtered_string = "".join(filter(str.isalnum, card.name.lower()))
                return (swu_search_filtered_string in card_filtered_string and 
                        (swu_search_config.card_type.value.lower() == card.type.lower() or swu_search_config.card_type == CardType.UNSPECIFIED))

        def sort_the_result(card: TradingCard):
            return card.name
        try:
            filtered_list = list(filter(filter_the_result, self._response_card_list))
            filtered_list.sort(key=sort_the_result)
            result = DataSourceCardSearchClientSearchResponse(filtered_list)
            return (result, None)
        except Exception as error:
            return (DataSourceCardSearchClientSearchResponse([]), error)
    
    @property
    def _response_card_list(self) -> List[TradingCard]:
        return self._data_source_local_managed_sets.retrieve_card_list()

DOMAIN_IDENTIFIER = 'api.swu-db.com'

class SWUDBLocalSetRetrieverClient(DataSourceLocallyManagedSetsClientProtocol): 
    @property
    def _site_source_url(self) -> str:
        return "https://api.swu-db.com/"
    
    @property
    def domain_identifier(self) -> str:
        return DOMAIN_IDENTIFIER
    
    # MARK: - DataSourceLocalManagedSetClientProtocol
    def remote_url(self, deck_identifier: str) -> str:
        return  f'{self._site_source_url}cards/{deck_identifier.lower()}'
    
    @property
    def file_extension(self) -> str:
        return 'json'
    
    def parse_asset(self, file: TextIOWrapper) -> List[TradingCard]:
        result_list: List[TradingCard] = []
        loaded_json = json.load(file)
        if 'data' not in loaded_json:
            # not a valid structure
            raise Exception
        cards = loaded_json['data']
        for card in cards:
            swu_card = SWUDBTradingCard.from_swudb_response(card)
            result_list.append(swu_card)
        return result_list
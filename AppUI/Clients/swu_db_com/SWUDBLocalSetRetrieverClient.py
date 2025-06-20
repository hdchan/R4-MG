import json
from io import TextIOWrapper
from typing import Any, List, Optional

from AppCore.DataFetcher import DataFetcherLocal
from AppCore.DataSource import DataSourceLocallyManagedSets
from AppCore.DataSource.DataSourceCardSearchClientProtocol import (
    DataSourceCardSearchClientProtocol,
    DataSourceCardSearchClientSearchCallback,
    DataSourceCardSearchClientSearchResponse,
    DataSourceCardSearchClientSearchResult)
from AppCore.DataSource.DataSourceLocallyManagedSets import \
    DataSourceLocallyManagedSetsClientProtocol
from AppCore.Models import (CardType, PaginationConfiguration,
                            SearchConfiguration, TradingCard)
from AppCore.Observation import ObservationTower
from AppCore.Service.ModelEncoder import ModelEncoder

from ..SWUCardSearchConfiguration import SWUCardSearchConfiguration
from .SWUTradingCard import SWUTradingCard


class SWUDBLocalCardRetrieverClient(DataSourceCardSearchClientProtocol):
    def __init__(self, 
                 observation_tower: ObservationTower,
                 local_fetcher: DataFetcherLocal, 
                 local_managed_sets: DataSourceLocallyManagedSets):
        self._observation_tower = observation_tower
        self._local_fetcher = local_fetcher
        self._local_managed_sets = local_managed_sets
        
    @property
    def source_display_name(self) -> str:
        return "Locally managed sets"
    
    # MARK: - DataSourceCardSearchClientProtocol
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
        try:
            filtered_list = list(filter(filter_the_result, self._response_card_list))
            filtered_list.sort(key=sort_the_result)
            result = DataSourceCardSearchClientSearchResponse(filtered_list)
            return (result, None)
        except Exception as error:
            return (DataSourceCardSearchClientSearchResponse([]), error)
        
    
    @property
    def _response_card_list(self) -> List[TradingCard]:
        return self._local_managed_sets.retrieve_card_list()

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
            swu_card = SWUTradingCard.from_swudb_response(card)
            result_list.append(swu_card)
        return result_list
    
    def save_asset(self, file: TextIOWrapper, data: Any):
        json_data = json.load(data)
        json.dump(json_data, file, cls=ModelEncoder)
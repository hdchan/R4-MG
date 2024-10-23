import copy
from typing import List, Optional, Tuple

from AppCore.Data import APIClientProtocol, APIClientProvider
from AppCore.Models import SearchConfiguration, TradingCard
from AppCore.Observation import ObservationTower
from AppCore.Observation.Events import SearchEvent


class CardDataSourceDelegate:
    def ds_completed_search_with_result(self, ds: ..., result_list: List[TradingCard], error: Optional[Exception]) -> None:
        pass

class CardDataSource:
    def __init__(self,
                 observation_tower: ObservationTower,
                 api_client_provider: APIClientProvider):
        self.observation_tower = observation_tower
        self.api_client_provider: APIClientProvider = api_client_provider
        self.delegate: Optional[CardDataSourceDelegate]
        self._search_configuration = SearchConfiguration()
        
    @property
    def api_client(self) -> APIClientProtocol:
        return self.api_client_provider.provideClient()
    

    def search(self, search_configuration: SearchConfiguration):
        self.observation_tower.notify(SearchEvent(SearchEvent.EventType.STARTED,
                                                  copy.deepcopy(search_configuration)))

        def completed_with_search_result(result: Tuple[Optional[List[TradingCard]], Optional[Exception]]):
            result_list, error = result
            
            if error is None and result_list is not None:
                if self.delegate is not None:
                    self.delegate.ds_completed_search_with_result(self, result_list, None)
            else:
                if self.delegate is not None:
                    self.delegate.ds_completed_search_with_result(self, [], error)
                    
            self.observation_tower.notify(SearchEvent(SearchEvent.EventType.FINISHED,
                                                      copy.deepcopy(search_configuration)))

        self.api_client.search(search_configuration, completed_with_search_result)
    
    
        
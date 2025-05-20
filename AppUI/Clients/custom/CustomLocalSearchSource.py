import os
from typing import Any, Dict, List, Optional

from AppCore.Data.APIClientProtocol import (APIClientProtocol,
                                            APIClientSearchCallback,
                                            APIClientSearchResponse)
from AppCore.Models import (CardType, PaginationConfiguration,
                            SearchConfiguration, TradingCard)
from AppCore.Network import LocalNetworker

from ..SWUCardSearchConfiguration import SWUCardSearchConfiguration


class CustomTradingCard(TradingCard):
    @classmethod
    def from_swudb_response(cls, name):
        obj = cls.__new__(cls)
        metadata: Dict[str, Any] = {}
        super(CustomTradingCard, obj).__init__(
            name=name,
            set="no set",
            type='no type',
            number='no number',
            json={},
            metadata=metadata
        )
        return obj
    
    @property
    def friendly_display_name_detailed(self) -> str:
        return self.name
    
    @property
    def front_art_url(self) -> str:
        return self.name

class CustomLocalSearchSource(APIClientProtocol):
    def __init__(self, local_networker: LocalNetworker, directory_path, preview_dir_path):
        self._local_networker = local_networker
        self._directory_path = directory_path
        self._preview_dir_path = preview_dir_path
        
    @property
    def source_display_name(self) -> str:
        return "Custom images"

    @property
    def site_source_url(self) -> Optional[str]:
        return None
        
    def search(self, 
               search_configuration: SearchConfiguration,
               pagination_configuration: PaginationConfiguration,
               callback: APIClientSearchCallback) -> None:
        def completed_search():
            self._perform_search(search_configuration, callback)
        print(f'Custom search. card_name: {search_configuration.card_name}, search_configuration: {search_configuration}')
        self._local_networker.load_mock(completed_search)
        
    def _perform_search(self, search_configuration: SearchConfiguration, callback: APIClientSearchCallback):
        swu_search_config = SWUCardSearchConfiguration.from_search_configuration(search_configuration)
        def filter_the_result(card: TradingCard):
            if swu_search_config.card_name.replace(" ", "") == '':
                return True
            return (swu_search_config.card_name.lower() in card.name.lower() and 
                    (swu_search_config.card_type.value.lower() == card.type.lower() or swu_search_config.card_type == CardType.UNSPECIFIED))
        def sort_the_result(card: TradingCard):
            return card.name
        filtered_list = list(filter(filter_the_result, self._response_card_list))
        filtered_list.sort(key=sort_the_result)
        result = APIClientSearchResponse(filtered_list)
        callback((result, None))
        
    @property
    def _response_card_list(self) -> List[TradingCard]:
        result = []
        for i in self.list_files_in_directory():
            # TODO: guard against non PNG files
            name = os.path.splitext(i)[0]
            card = CustomTradingCard.from_swudb_response(name)
            card.local_image_path = self._directory_path
            card.local_image_preview_path = self._preview_dir_path
            result.append(card)
        
        return result
    
    def list_files_in_directory(self):
        try:
            files = [f for f in os.listdir(self._directory_path) if os.path.isfile(os.path.join(self._directory_path, f))]
            return files
        except FileNotFoundError:
            return []
        
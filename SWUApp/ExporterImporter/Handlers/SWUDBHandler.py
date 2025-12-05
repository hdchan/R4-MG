
import json
from collections import deque
from typing import Any, Dict, List, Optional

from AppCore.DataSource.DataSourceCardSearch import (
    DataSourceCardSearch,
    DataSourceCardSearchDelegate,
)
from AppCore.Models import SearchConfiguration

from ...Models import (
    ParsedDeckList,
    SWUCardSearchConfiguration,
    SWUTradingCardBackedLocalCardResource,
    SWUTradingCardModelMapper,
)
from ...SWUAppDependenciesProviding import SWUAppDependenciesProviding
from ..ExportImportFormattable import ExportFormattable, Importable


class SWUDBHandler(ExportFormattable, Importable, DataSourceCardSearchDelegate):
    def __init__(self, 
                 swu_app_dependencies_provider: SWUAppDependenciesProviding):
        self._swu_app_dependencies_provider = swu_app_dependencies_provider
        self._search_data_source = swu_app_dependencies_provider.new_data_source_card_search(self)
        self._data_source_draft_list = swu_app_dependencies_provider.data_source_draft_list
        self._router = swu_app_dependencies_provider.router

        self._search_queue: deque[SWUCardSearchConfiguration] = deque([])
        self._result: List[SWUTradingCardBackedLocalCardResource] = []
        self._not_found: List[SearchConfiguration] = []

    @property
    def file_format(self) -> str:
        return "swudb.com (*.json)"
    
    @property
    def format_name(self) -> str:
        return "swudb.com"
    

    # MARK: Importer
    def import_text(self, text: str) -> None:
        try:
            def _obj_to_config(card: Dict[str, Any], is_sideboard: bool = False) -> SWUCardSearchConfiguration:
                leader_contents = card.get('id').split('_')
                quantity = card.get('count')
                config = SWUCardSearchConfiguration()
                config.card_set = leader_contents[0]
                config.card_number = leader_contents[1]
                config.metadata['is_sideboard'] = is_sideboard
                config.metadata['quantity'] = quantity
                return config

            dic: Dict[str, Any] = json.loads(text)
            
            self._search_queue.appendleft(_obj_to_config(dic.get('leader')))
            self._search_queue.appendleft(_obj_to_config(dic.get('base')))
            if 'deck' in dic:
                for d in dic.get('deck'):
                    self._search_queue.appendleft(_obj_to_config(d))
            if 'sideboard' in dic:
                for d in dic.get('sideboard'):
                    self._search_queue.appendleft(_obj_to_config(d, True))
        except Exception as error:
            exception = Exception(f"Incorrect swudb.com format {error}")
            self._router.show_error(exception)

        self._continue_processing_search_queue()

    def _continue_processing_search_queue(self):
        if len(self._search_queue) == 0:
            # finish processing
            if len(self._not_found) > 0:
                not_found_card_string = ", ".join(map(lambda x: x.card_name, self._not_found))
                self._router.show_error(Exception(f'Could not find: {not_found_card_string}'))
            else:
                self._data_source_draft_list.create_new_pack_from_list("Imported SWUDB.com deck", self._result)
            return
        config = self._search_queue.pop()
        self._search_data_source.search(config)

    def ds_completed_search_with_result(self, 
                                        ds: DataSourceCardSearch,
                                        search_configuration: SearchConfiguration,
                                        error: Optional[Exception], 
                                        is_initial_load: bool) -> None:
        local_resources = list(filter(None, list(map(lambda x: SWUTradingCardModelMapper.from_card_resource(x), ds.local_card_resources))))
        swu_search_configuration = SWUCardSearchConfiguration.from_search_configuration(search_configuration)
        if len(local_resources) > 0:
            current_resource = local_resources[0]
            current_number = int(current_resource.guaranteed_trading_card.number)
            if len(local_resources) > 1:
                # multiple cards found
                for l in local_resources:
                    if l.guaranteed_trading_card.name == swu_search_configuration.card_name and l.guaranteed_trading_card.subtitle == swu_search_configuration.subtitle and int(current_number) > int(l.guaranteed_trading_card.number):
                        current_number = l.guaranteed_trading_card.number # set lowest card number
                        current_resource = l
            current_resource.set_is_sideboard(swu_search_configuration.metadata['is_sideboard'])
            quantity = swu_search_configuration.metadata.get('quantity', 1)
            for _ in range(quantity):
                self._result.append(current_resource)
        else:
            self._not_found.append(search_configuration)
        self._continue_processing_search_queue()

    # MARK: - Exporter
    def export(self, 
               file_path: str,
               parsed_deck_list: ParsedDeckList) -> None:
        selected_leader, selected_base = parsed_deck_list.first_leader_and_first_base
        main_deck = parsed_deck_list.main_deck
        sideboard = parsed_deck_list.sideboard
        def aggregate(card_list: List[SWUTradingCardBackedLocalCardResource]) -> List[Dict[str, Any]]:
            deck_counter: Dict[str, int] = {}
            for m in card_list:
                hash = f'{m.guaranteed_trading_card.set}_{m.guaranteed_trading_card.number}'
                if hash not in deck_counter:
                    deck_counter[hash] = 0
                    
                deck_counter[hash] += 1
            
            deck_result: List[Dict[str, Any]] = []
            for m in deck_counter.keys():
                deck_result.append({
                    "id": m,
                    "count": deck_counter[m]
                })
            return deck_result
            
        result: Dict[str, Any] = {
            "leader": {
                "id": f'{selected_leader.guaranteed_trading_card.set}_{selected_leader.guaranteed_trading_card.number}',
                "count": 1
            },
            "base": {
                "id": f'{selected_base.guaranteed_trading_card.set}_{selected_base.guaranteed_trading_card.number}',
                "count": 1
            },
            "deck": aggregate(main_deck),
            "sideboard": aggregate(sideboard)
        }
        
        with open(f'{file_path}', 'w') as f:
            f.write(json.dumps(result, indent=4))

from collections import deque
from typing import Dict, List, Optional

from AppCore.DataSource.DataSourceCardSearch import (
    DataSourceCardSearch, DataSourceCardSearchDelegate)
from AppCore.Models import SearchConfiguration

from ...Models import (CardType, ParsedDeckList, SWUCardSearchConfiguration,
                       SWUTradingCardBackedLocalCardResource,
                       SWUTradingCardModelMapper)
from ...Models.SWUTradingCardBackedLocalCardResource import \
    SWUTradingCardBackedLocalCardResource
from ...SWUAppDependenciesProviding import SWUAppDependenciesProviding
from ..ExportImportFormattable import ExportFormattable, Importable


class MGGHandler(ExportFormattable, Importable, DataSourceCardSearchDelegate):
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
        return "Melee.gg (*.txt)"
    
    @property
    def format_name(self) -> str:
        return "Melee.gg"
    
    # Importer
    def import_text(self, text: str):
        all_lines = text.split("\n")
        # TODO: maybe use regex
        current_card_type = CardType.UNSPECIFIED
        current_section = ''
        try:
            for l in all_lines:
                if not any(char.isalnum() for char in l):
                    current_section = ""
                    continue
                if l.lower() == "leader".lower():
                    current_section = l.lower()
                    current_card_type = CardType.LEADER
                    continue
                elif l.lower() == 'base'.lower():
                    current_section = l.lower()
                    current_card_type = CardType.BASE
                    continue
                    
                if l.lower().replace(" ", '') == "maindeck".lower() \
                    or l.lower() == "sideboard":
                    current_section = l.lower()
                    current_card_type = CardType.UNSPECIFIED
                    continue
                
                # TODO: rework
                split = l.split(' ', 1)
                quantity = split[0]
                card = split[1]
                split_2 = card.split(' | ')
                card_name = split_2[0]
                subtitle: Optional[str] = None
                if len(split_2) > 1:
                    subtitle = split_2[1]

            
                config = SWUCardSearchConfiguration()
                config.card_name = card_name
                config.subtitle = subtitle
                config.card_type = current_card_type
                config.metadata['quantity'] = int(quantity)
                config.metadata['is_sideboard'] = current_section == 'sideboard'
                self._search_queue.appendleft(config)
        except Exception as error:
            exception = Exception(f"Incorrect melee.gg format: {error}")
            self._router.show_error(exception)

        self._continue_processing_search_queue()

    def _continue_processing_search_queue(self):
        if len(self._search_queue) == 0:
            # finish processing
            if len(self._not_found) > 0:
                not_found_card_string = ", ".join(map(lambda x: x.card_name, self._not_found))
                self._router.show_error(Exception(f'Could not find: {not_found_card_string}'))
            else:
                self._data_source_draft_list.create_new_pack_from_list("Imported MGG deck", self._result)
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

    # Exporter
    def export(self, 
               file_path: str,
               parsed_deck_list: ParsedDeckList) -> None:
            selected_leader, selected_base = parsed_deck_list.first_leader_and_first_base
            main_deck = parsed_deck_list.main_deck
            sideboard = parsed_deck_list.sideboard
            def aggregate(card_list: List[SWUTradingCardBackedLocalCardResource]) -> List[str]:
                deck_counter: Dict[str, int] = {}
                for m in card_list:
                    hash_array: List[str] = [m.guaranteed_trading_card.name]
                    if m.guaranteed_trading_card.subtitle is not None:
                        hash_array.append(m.guaranteed_trading_card.subtitle)
                    hash = " | ".join(hash_array)
                    
                    if hash not in deck_counter:
                        deck_counter[hash] = 0
                    deck_counter[hash] += 1
                
                deck_result: List[str] = []
                for m in deck_counter.keys():
                    deck_result.append(f'{deck_counter[m]} {m}\n')
                return deck_result
                
            result: List[str] = [
                "Leader\n",
                f"1 {selected_leader.guaranteed_trading_card.name} | {selected_leader.guaranteed_trading_card.subtitle}\n",
                "\n",
                "Base\n",
                f"1 {selected_base.guaranteed_trading_card.name}\n", # no subtitle
                "\n",
                "MainDeck\n"] + aggregate(main_deck) + [
                "\n",
                "Sideboard\n"] + aggregate(sideboard) + [
            ]
            
            with open(f'{file_path}', 'w') as f:
                for r in result:
                    f.write(r)
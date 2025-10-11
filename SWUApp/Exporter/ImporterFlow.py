from typing import Any, Dict, List, Optional

from AppCore.DataSource.DataSourceCardSearch import (
    DataSourceCardSearch, DataSourceCardSearchDelegate)
from AppCore.DataSource.DataSourceCardSearchClientProtocol import (
    DataSourceCardSearchClientProtocol, DataSourceCardSearchClientProviding,
    DataSourceCardSearchClientSearchCallback)
from AppCore.Models import PaginationConfiguration, SearchConfiguration

from ..Models.CardType import CardType
from ..Models.SWUCardSearchConfiguration import SWUCardSearchConfiguration
from ..SWUAppDependenciesProviding import SWUAppDependenciesProviding
from .ImporterDialog import ImporterDialog
from ..swu_db_com.SWUDBAPIRemoteClient import SWUDBAPIRemoteClient
from AppCore.DataFetcher import DataFetcherRemote


class ImporterSearchClient(DataSourceCardSearchClientProviding, DataSourceCardSearchClientProtocol):

    def __init__(self):
        self._remote_client = SWUDBAPIRemoteClient()

    @property
    def source_display_name(self) -> str:
        return "swu-db.com"
        
    def search(self, 
               search_configuration: SearchConfiguration,
               pagination_configuration: PaginationConfiguration,
               callback: DataSourceCardSearchClientSearchCallback) -> None:
        # TODO: switch depending on the config
        self._remote_client.search(search_configuration, pagination_configuration, callback)
    
    @property
    def search_client(self) -> DataSourceCardSearchClientProtocol:
        return self
        

class ImporterFlow(DataSourceCardSearchDelegate):
    def __init__(self, app_dependencies_provider: SWUAppDependenciesProviding):
        self._search_data_source = app_dependencies_provider.new_data_source_card_search(self, ImporterSearchClient())

    def start(self):
        dialog = ImporterDialog()
        result = dialog.exec()
        if result:
            self._process_melee_gg(dialog.data_string)

    def _process_melee_gg(self, text: str):
        line_items: List[Dict[str, Optional[Any]]] = []
        all_lines = text.split("\n")
        # TODO: maybe use regex
        current_card_type = CardType.UNSPECIFIED
        for l in all_lines:
            if not any(char.isalnum() for char in l):
                continue
            
            
            if l.lower() == "leader":
                current_card_type = CardType.LEADER
                continue
            elif l.lower() == 'base':
                current_card_type = CardType.BASE
                continue
                 
            if l.lower() == "maindeck" \
                or l.lower() == "sideboard":
                current_card_type = CardType.UNSPECIFIED
                continue

            split = l.split(' ', 1)
            quantity = split[0]
            card = split[1]
            split_2 = card.split(' | ')
            card_name = split_2[0]
            subtitle: Optional[str] = None
            if len(split_2) > 1:
                subtitle = split_2[1]

            dic = {
                'quantity': int(quantity),
                'card_name': card_name,
                'subtitle': subtitle,
                'card_type': current_card_type
            }

            line_items.append(dic)
        print(line_items)
        config = SWUCardSearchConfiguration()
        config.card_name = line_items[0]['card_name']
        config.card_type = line_items[0]['card_type']

        self._search_data_source.search(config)

    def ds_started_search_with_result(self,
                                      ds: DataSourceCardSearch,
                                      search_configuration: SearchConfiguration):
        pass
    
    def ds_completed_search_with_result(self, 
                                        ds: DataSourceCardSearch,
                                        search_configuration: SearchConfiguration,
                                        error: Optional[Exception], 
                                        is_initial_load: bool) -> None:
        raise Exception

    def ds_did_retrieve_card_resource_for_card_selection(self, 
                                                         ds: DataSourceCardSearch) -> None:
        raise Exception

    def ds_loading_state_changed(self, 
                                 ds: DataSourceCardSearch) -> None:
        pass
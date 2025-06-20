import json
from copy import deepcopy
from datetime import datetime
from pathlib import Path
from typing import Any, List, Tuple, Dict, Optional

from AppCore.Config import ConfigurationManager
from AppCore.Models import SearchConfiguration

from AppCore.Observation import *
from AppCore.Service.ModelEncoder import ModelEncoder
from AppCore.Service import StringFormatter

class DataSourceRecentSearch():
    class Keys:
        DATETIME = 'datetime'
        SEARCH_CONFIG = 'search_config'
        
    def __init__(self,
                 identifier: Optional[str],
                 configuration_manager: ConfigurationManager, 
                 string_formatter: StringFormatter):
        loaded = None
        self._identifier = identifier
        self._string_formatter = string_formatter
        self._search_history: List[Tuple[SearchConfiguration, datetime]] = []
        
        if self._identifier is not None:
            Path(configuration_manager.configuration.cache_history_dir_path).mkdir(parents=True, exist_ok=True)
            self._search_history_path = f'{configuration_manager.configuration.cache_history_dir_path}{identifier}.json'
            my_file = Path(self._search_history_path)
            if my_file.is_file():
                with open(self._search_history_path, "r") as f:
                    loaded = json.load(f)
                    for l in loaded:
                        self._search_history.append((SearchConfiguration.from_json(l[self.Keys.SEARCH_CONFIG]), datetime.fromtimestamp(l[self.Keys.DATETIME])))

    @property
    def _search_list_history(self) -> List[Tuple[SearchConfiguration, datetime]]:
        return deepcopy(self._search_history)

    def get_search_configuration_from_history(self, index: int) -> Optional[Tuple[SearchConfiguration, datetime]]:
        if index < len(self._search_list_history):
            return self._search_list_history[index]
        return None

    @property
    def search_list_history_display(self) -> List[str]:
        def map_history(result: Tuple[SearchConfiguration, datetime]) -> str:
            search_config, timestamp = result
            def map_metadata(key: str) -> str:
                string = f'{key}: {search_config.metadata[key]}'
                string = string.replace("_", " ").title()
                return string
            metadata = ', '.join(map(map_metadata, search_config.metadata.keys()))
            return f'{self._string_formatter.format_date(timestamp)} - Name: "{search_config.card_name}", {metadata}'
        return list(map(map_history, self._search_list_history))

    def save_search(self, search_configuration: SearchConfiguration):
        self._search_history.insert(0, (search_configuration, datetime.now()))
        self._save_data()
            
    def _save_data(self):
        if self._identifier is not None:
            data: List[Dict[str, Any]] = []
            for e in self._search_history[:100]: # TODO: configuration
                data.append({
                    self.Keys.SEARCH_CONFIG: e[0],
                    self.Keys.DATETIME: e[1].timestamp()
                })
            with open(self._search_history_path, "w") as f:
                json.dump(data, f, cls=ModelEncoder)
            

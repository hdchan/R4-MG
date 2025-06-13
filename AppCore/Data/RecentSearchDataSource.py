import json
from copy import deepcopy
from datetime import datetime
from pathlib import Path
from typing import Any, List, Tuple

from AppCore.CoreDependencyProviding import CoreDependencyProviding
from AppCore.Models import SearchConfiguration

from AppCore.Observation import *
from AppCore.Observation.Events import SearchEvent
from AppCore.Service.ModelEncoder import ModelEncoder


class RecentSearchDataSource(TransmissionReceiverProtocol):
    class Keys:
        DATETIME = 'datetime'
        SEARCH_CONFIG = 'search_config'
        
    def __init__(self,
                 core_dependency_provider: CoreDependencyProviding):
        self._observation_tower = core_dependency_provider.observation_tower
        self._configuration_provider = core_dependency_provider.configuration_manager
        loaded = None
        self._search_history: List[Tuple[SearchConfiguration, datetime]] = []
        my_file = Path(self._configuration_provider.configuration.search_history_path)
        if my_file.is_file():
            with open(self._configuration_provider.configuration.search_history_path, "r") as f:
                loaded = json.load(f)
                for l in loaded:
                    self._search_history.append((SearchConfiguration.from_json(l[self.Keys.SEARCH_CONFIG]), datetime.fromtimestamp(l[self.Keys.DATETIME])))
        

        self._observation_tower.subscribe(self, SearchEvent)

    @property
    def search_list_history(self) -> List[Tuple[SearchConfiguration, datetime]]:
        return deepcopy(self._search_history)

    def handle_observation_tower_event(self, event: TransmissionProtocol) -> None:
        if type(event) == SearchEvent and event.event_type == SearchEvent.EventType.FINISHED:
            self._search_history.insert(0, (event.search_configuration, event.date_time))
            self._save_data()
            
    def _save_data(self):
        # save async
        data: List[Dict[str, Any]] = []
        for e in self._search_history[:100]: # TODO: configuration
            data.append({
                self.Keys.SEARCH_CONFIG: e[0],
                self.Keys.DATETIME: e[1].timestamp()
            })
        with open(self._configuration_provider.configuration.search_history_path, "w") as f:
            json.dump(data, f, cls=ModelEncoder)
            

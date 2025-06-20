import json
from copy import deepcopy
from datetime import datetime
from pathlib import Path
from typing import Any, List, Tuple, Optional, Dict

from AppCore.CoreDependenciesProviding import CoreDependenciesProviding

from AppCore.Observation import *
from AppCore.Observation.Events import (LocalCardResourceSelectedEvent,
                                  PublishStagedCardResourcesEvent)
from AppCore.Service.ModelEncoder import ModelEncoder
from AppCore.Models import LocalCardResource

class DataSourceRecentPublishedDelegate:
    def rp_did_retrieve_card_resource_for_card_selection(self, ds: ..., local_resource: LocalCardResource) -> None:
        pass
    
class DataSourceRecentPublished(TransmissionReceiverProtocol):
    class Keys:
        DATETIME = 'datetime'
        PUBLISHED_RESOURCE = 'published_resource'

    def __init__(self, 
                 core_dependency_provider: CoreDependenciesProviding):
        self._observation_tower = core_dependency_provider.observation_tower
        self._image_resource_processor_provider = core_dependency_provider.image_resource_processor_provider
        self._configuration_provider = core_dependency_provider.configuration_manager

        self._published_history: List[Tuple[LocalCardResource, datetime]] = []
        
        Path(self._configuration_provider.configuration.cache_history_dir_path).mkdir(parents=True, exist_ok=True)
        self._publish_history_path = f'{self._configuration_provider.configuration.cache_history_dir_path}publish_history.json'
        my_file = Path(self._publish_history_path)
        if my_file.is_file():
            with open(self._publish_history_path, "r") as f:
                loaded = json.load(f)
                for l in loaded:
                    self._published_history.append((LocalCardResource.from_json(l[self.Keys.PUBLISHED_RESOURCE]), datetime.fromtimestamp(l[self.Keys.DATETIME])))
        

        self._selected_index: Optional[int] = None
        self._selected_resource: Optional[LocalCardResource] = None
        self.delegate: Optional[DataSourceRecentPublishedDelegate] = None
        self._observation_tower.subscribe(self, PublishStagedCardResourcesEvent)
    
    @property
    def selected_local_resource(self) -> Optional[LocalCardResource]:
        if self._selected_resource is not None:
            return self._selected_resource
        return None
    
    @property
    def published_resources_history(self) -> List[Tuple[LocalCardResource, datetime]]:
        return self._published_history
    
    def select_card_resource_for_card_selection(self, index: int):
        if index < len(self._published_history):
            self._selected_index = index
            self._retrieve_card_resource_for_card_selection(index)
    
    def _retrieve_card_resource_for_card_selection(self, index: int, retry: bool = False):
        selected_resource = self._published_history[index][0]
        self._selected_resource = selected_resource
        self._observation_tower.notify(LocalCardResourceSelectedEvent(selected_resource))
        self._image_resource_processor_provider.image_resource_processor.async_store_local_resource(selected_resource, retry)
        if self.delegate is not None:
            self.delegate.rp_did_retrieve_card_resource_for_card_selection(self, deepcopy(selected_resource))
    
    def handle_observation_tower_event(self, event: TransmissionProtocol) -> None:
        if type(event) == PublishStagedCardResourcesEvent and event.event_type == PublishStagedCardResourcesEvent.EventType.FINISHED:
            for e in event.deployment_resources:
                if e.staged_resource is not None:
                    self._published_history.insert(0, (e.staged_resource, event.date_time))
                    # sorted
            self._save_data()

    def _save_data(self):
        # save async
        data: List[Dict[str, Any]] = []
        for e in self._published_history[:100]: # TODO: configuration
            data.append({
                self.Keys.PUBLISHED_RESOURCE: e[0],
                self.Keys.DATETIME: e[1].timestamp()
            })
        with open(self._publish_history_path, "w") as f:
            json.dump(data, f, cls=ModelEncoder)
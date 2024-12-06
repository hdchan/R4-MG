from copy import deepcopy
from datetime import datetime
from typing import List, Tuple

from AppCore.CoreDependencyProviding import CoreDependencyProviding

from ..Observation import *
from ..Observation.Events import (LocalResourceSelectedEvent,
                                  PublishStagedResourcesEvent)
from .LocalResourceDataSourceProtocol import *


class RecentPublishedDataSourceDelegate:
    def rp_did_retrieve_card_resource_for_card_selection(self, ds: ..., local_resource: LocalCardResource) -> None:
        pass
    
class RecentPublishedDataSource(LocalResourceDataSourceProtocol, TransmissionReceiverProtocol):
    def __init__(self, 
                 core_dependency_providing: CoreDependencyProviding):
        self._observation_tower = core_dependency_providing.observation_tower
        self._image_resource_processor_provider = core_dependency_providing.image_resource_processor_provider
        self._published_resources_history: List[Tuple[LocalCardResource, datetime]] = []
        
        self._selected_index: Optional[int] = None
        self._selected_resource: Optional[LocalCardResource] = None
        self.delegate: Optional[RecentPublishedDataSourceDelegate] = None
        self._observation_tower.subscribe(self, PublishStagedResourcesEvent)
    
    @property
    def selected_local_resource(self) -> Optional[LocalCardResource]:
        if self._selected_resource is not None:
            return self._selected_resource
        return None
    
    @property
    def published_resources_history(self) -> List[Tuple[LocalCardResource, datetime]]:
        return self._published_resources_history
    
    def select_card_resource_for_card_selection(self, index: int):
        if index < len(self._published_resources_history):
            self._selected_index = index
            self._retrieve_card_resource_for_card_selection(index)
    
    def _retrieve_card_resource_for_card_selection(self, index: int, retry: bool = False):
        selected_resource = self._published_resources_history[index][0]
        self._selected_resource = selected_resource
        self._observation_tower.notify(LocalResourceSelectedEvent(selected_resource))
        self._image_resource_processor_provider.image_resource_processor.async_store_local_resource(selected_resource, retry)
        if self.delegate is not None:
            self.delegate.rp_did_retrieve_card_resource_for_card_selection(self, deepcopy(selected_resource))
    
    def handle_observation_tower_event(self, event: TransmissionProtocol) -> None:
        if type(event) == PublishStagedResourcesEvent and event.event_type == PublishStagedResourcesEvent.EventType.FINISHED:
            for e in event.deployment_resources:
                if e.staged_resource is not None:
                    self._published_resources_history.insert(0, (e.staged_resource, event.date_time))
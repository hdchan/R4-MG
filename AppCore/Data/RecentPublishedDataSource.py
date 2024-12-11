from typing import List, Tuple
from datetime import datetime
from ..Observation import *
from ..Observation.Events import PublishStagedResourcesEvent
from .LocalResourceDataSourceProtocol import *

class RecentPublishedDataSource(LocalResourceDataSourceProtocol, TransmissionReceiverProtocol):
    def __init__(self, observation_tower: ObservationTower):
        self._observation_tower = observation_tower
        self._published_resources_history: List[Tuple[LocalCardResource, datetime]] = []
        
        self._observation_tower.subscribe(self, PublishStagedResourcesEvent)
    
    @property
    def published_resources_history(self) -> List[Tuple[LocalCardResource, datetime]]:
        return self._published_resources_history
    
    def handle_observation_tower_event(self, event: TransmissionProtocol) -> None:
        if type(event) == PublishStagedResourcesEvent and event.event_type == PublishStagedResourcesEvent.EventType.FINISHED:
            for e in event.published_resources:
                self._published_resources_history.append((e.local_card_resource, event.date_time))
            
            # print(self._events)
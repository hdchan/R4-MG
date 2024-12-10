from typing import List

from ..Models import StagedCardResource
from ..Observation import *
from ..Observation.Events import PublishStagedResourcesEvent
from .LocalResourceDataSourceProtocol import *

class RecentPublishedDataSource(LocalResourceDataSourceProtocol, TransmissionReceiverProtocol):
    def __init__(self, observation_tower: ObservationTower):
        self._observation_tower = observation_tower
        self._events: List[StagedCardResource] = []
        
        self._observation_tower.subscribe(self, PublishStagedResourcesEvent)
    
    @property
    def published_resources_history(self) -> List[LocalCardResource]:
        return list(map(lambda x: x.local_card_resource, self._events))
    
    def handle_observation_tower_event(self, event: TransmissionProtocol) -> None:
        if type(event) == PublishStagedResourcesEvent and event.event_type == PublishStagedResourcesEvent.EventType.FINISHED:
            self._events += event.published_resources
            
            # print(self._events)
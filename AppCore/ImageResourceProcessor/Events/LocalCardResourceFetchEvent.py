from enum import Enum
from typing import Optional

from AppCore.Models.LocalCardResource import LocalCardResource

from AppCore.Observation import TransmissionProtocol


class LocalCardResourceFetchEvent(TransmissionProtocol):
    class EventType(int, Enum):
        STARTED = 1
        FINISHED = 2
        FAILED = 3
        
    def __init__(self, 
                 event_type: EventType,
                 local_resource: LocalCardResource):
        super().__init__()
        self.event_type = event_type
        self.local_resource = local_resource

    @property
    def transmission_identifier(self) -> Optional[str]:
        return self.local_resource.asset_path
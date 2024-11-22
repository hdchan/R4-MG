from ...Models.LocalCardResource import LocalCardResource
from ..TransmissionProtocol import TransmissionProtocol

from enum import Enum
class LocalResourceEvent(TransmissionProtocol):
    class EventType(Enum):
        STARTED = 1
        FINISHED = 2
        FAILED = 3
        
    def __init__(self, 
                 event_type: EventType,
                 local_resource: LocalCardResource):
        self.event_type = event_type
        self.local_resource = local_resource
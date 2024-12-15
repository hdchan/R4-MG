from enum import Enum

from ...Models.LocalCardResource import LocalCardResource
from ..TransmissionProtocol import TransmissionProtocol


class LocalResourceFetchEvent(TransmissionProtocol):
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
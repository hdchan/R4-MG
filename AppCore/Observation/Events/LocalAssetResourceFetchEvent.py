from enum import Enum

from AppCore.Models.LocalCardResource import LocalAssetResource

from ..TransmissionProtocol import TransmissionProtocol


class LocalAssetResourceFetchEvent(TransmissionProtocol):
    class EventType(int, Enum):
        STARTED = 1
        FINISHED = 2
        FAILED = 3
        
    def __init__(self, 
                 event_type: EventType,
                 local_resource: LocalAssetResource):
        super().__init__()
        self.event_type = event_type
        self.local_resource = local_resource
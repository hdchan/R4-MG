from ..TransmissionProtocol import TransmissionProtocol
from enum import Enum

class PublishStagedResourcesEvent(TransmissionProtocol):
    class EventType(Enum):
        STARTED = 0
        FINISHED = 1
        FAILED = 2

    def __init__(self, event_type: EventType):
        self.event_type = event_type
from enum import Enum
from ..TransmissionProtocol import TransmissionProtocol
class SearchEvent(TransmissionProtocol):
    class EventType(Enum):
        STARTED = 1
        FINISHED = 2

    def __init__(self, event_type: EventType, 
                 is_system_initiated: bool):
        self.event_type = event_type
        self.is_system_initiated = is_system_initiated
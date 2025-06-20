from ..TransmissionProtocol import TransmissionProtocol
from enum import Enum

class ProductionCardResourcesLoadEvent(TransmissionProtocol):
    class EventType(int, Enum):
        STARTED = 1
        FINISHED = 2
        
    def __init__(self, event_type: EventType):
        self.event_type = event_type
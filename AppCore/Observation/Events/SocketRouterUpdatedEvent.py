from ..TransmissionProtocol import TransmissionProtocol
from enum import Enum

class SocketRouterUpdatedEvent(TransmissionProtocol):
    class EventType(Enum):
        DISCONNECTED = 0
        ESTABLISHING_CONNECTION = 1
        CONNECTED = 2

    def __init__(self, event_type: EventType):
        self.event_type = event_type
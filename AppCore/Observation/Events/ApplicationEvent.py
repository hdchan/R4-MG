from enum import Enum

from ..TransmissionProtocol import TransmissionProtocol


class ApplicationEvent(TransmissionProtocol):
    class EventType(Enum):
        APP_WILL_TERMINATE = 0

    def __init__(self, event_type: EventType):
        self.event_type = event_type
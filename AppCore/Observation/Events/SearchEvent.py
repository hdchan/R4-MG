from enum import Enum

from ...Models import SearchConfiguration
from ..TransmissionProtocol import TransmissionProtocol


class SearchEvent(TransmissionProtocol):
    class EventType(Enum):
        STARTED = 1
        FINISHED = 2

    def __init__(self, 
                 event_type: EventType,
                 search_configuration: SearchConfiguration):
        self.event_type = event_type
        self.search_configuration = search_configuration
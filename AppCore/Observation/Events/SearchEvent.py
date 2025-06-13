from enum import Enum

from AppCore.Models import SearchConfiguration

from ..TransmissionProtocol import TransmissionProtocol


class SearchEvent(TransmissionProtocol):
    class EventType(int, Enum):
        STARTED = 1
        FINISHED = 2

    def __init__(self, 
                 event_type: EventType,
                 search_configuration: SearchConfiguration):
        super().__init__()
        self.event_type = event_type
        self.search_configuration = search_configuration
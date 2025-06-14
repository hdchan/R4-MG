from enum import Enum

from AppCore.Models import SearchConfiguration

from ..TransmissionProtocol import TransmissionProtocol


class SearchEvent(TransmissionProtocol):
    class EventType(int, Enum):
        STARTED = 1
        FINISHED = 2
        
    class SourceType(int, Enum):
        LOCAL = 1
        REMOTE = 2

    def __init__(self, 
                 event_type: EventType,
                 source_type: SourceType,
                 search_configuration: SearchConfiguration):
        super().__init__()
        self.event_type = event_type
        self.source_type = source_type
        self.search_configuration = search_configuration
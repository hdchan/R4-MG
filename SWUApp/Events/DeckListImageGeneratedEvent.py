from enum import Enum

from AppCore.Observation import TransmissionProtocol

from ..Models import ParsedDeckList


class DeckListImageGeneratedEvent(TransmissionProtocol):

    class EventType(int, Enum):
        STARTED = 0
        FINISHED = 1

    def __init__(self, event_type: EventType, 
                 deck_list: ParsedDeckList):
        super().__init__()
        self.event_type = event_type
        self.deck_list = deck_list
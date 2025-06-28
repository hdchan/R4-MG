from enum import Enum

from ..TransmissionProtocol import TransmissionProtocol


class DraftListUpdatedEvent(TransmissionProtocol):
        
    def __init__(self):
        super().__init__()
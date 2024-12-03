from ..TransmissionProtocol import TransmissionProtocol

class PublishStatusUpdatedEvent(TransmissionProtocol):
    def __init__(self, can_publish: bool):
        self.can_publish = can_publish
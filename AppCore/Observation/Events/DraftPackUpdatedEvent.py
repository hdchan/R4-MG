from ..TransmissionProtocol import TransmissionProtocol

# TODO: futher break down events?
class DraftPackUpdatedEvent(TransmissionProtocol):
    
    def __init__(self):
        super().__init__()
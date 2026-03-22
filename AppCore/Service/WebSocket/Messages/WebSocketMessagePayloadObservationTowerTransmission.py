from ..WebSocketMessageProtocol import WebSocketMessagePayloadType
from AppCore.Observation import TransmissionProtocol


class WebSocketMessagePayloadObservationTowerTransmission(WebSocketMessagePayloadType):
    def __init__(self, event: TransmissionProtocol):
        self.event = event
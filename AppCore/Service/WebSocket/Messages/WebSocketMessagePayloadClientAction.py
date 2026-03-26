
from ..WebSocketMessageProtocol import WebSocketMessagePayloadType

class WebSocketMessagePayloadClientAction(WebSocketMessagePayloadType):
    def __init__(self, partial_action):
        self.partial_action = partial_action
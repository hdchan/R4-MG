class WebSocketMessagePayloadType:
    pass

class WebSocketMessageProtocol:
    def __init__(self, payload: WebSocketMessagePayloadType):
        self.payload = payload
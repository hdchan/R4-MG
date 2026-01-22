from ..WebSocketMessageProtocol import WebSocketMessageProtocol

class ClientConnectedMessage(WebSocketMessageProtocol):
    def __init__(self, identifier: str, object: object):
        super().__init__(identifier)
        self.object = object
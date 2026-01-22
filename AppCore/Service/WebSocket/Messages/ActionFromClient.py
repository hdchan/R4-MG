from ..WebSocketMessageProtocol import WebSocketMessageProtocol

class ActionFromClient(WebSocketMessageProtocol):
    def __init__(self, identifier: str, function_name: str, **kwargs):
        super().__init__(identifier)
        self.function_name = function_name
        self.kwargs = kwargs
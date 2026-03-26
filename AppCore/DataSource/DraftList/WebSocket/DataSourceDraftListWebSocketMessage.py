from AppCore.Service.WebSocket.WebSocketMessageProtocol import (
    WebSocketMessagePayloadType,
    WebSocketMessageProtocol,
)

from ..DataSourceDraftListProtocol import (
    DataSourceDraftListProtocol,
)


class DataSourceDraftListWebSocketMessage(WebSocketMessageProtocol):
    def __init__(self, data_source: DataSourceDraftListProtocol, payload: WebSocketMessagePayloadType):
        self.data_source = data_source
        self.payload = payload

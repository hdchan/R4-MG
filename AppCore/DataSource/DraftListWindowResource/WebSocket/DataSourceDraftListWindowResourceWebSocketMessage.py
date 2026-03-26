from AppCore.Service.WebSocket.WebSocketMessageProtocol import (
    WebSocketMessagePayloadType,
    WebSocketMessageProtocol,
)

from ..DataSourceDraftListWindowResourceDeployerProtocol import DataSourceDraftListWindowResourceDeployerProtocol

class DataSourceDraftListWindowResourceWebSocketMessage(WebSocketMessageProtocol):
    def __init__(self, data_source: DataSourceDraftListWindowResourceDeployerProtocol, payload: WebSocketMessagePayloadType):
        self.data_source = data_source
        self.payload = payload

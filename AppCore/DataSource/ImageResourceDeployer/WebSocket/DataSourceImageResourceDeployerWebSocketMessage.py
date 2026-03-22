from AppCore.Service.WebSocket.WebSocketMessageProtocol import (
    WebSocketMessagePayloadType,
    WebSocketMessageProtocol,
)

from ..DataSourceImageResourceDeployerProtocol import (
    DataSourceImageResourceDeployerProtocol,
)


class DataSourceImageResourceDeployerWebSocketMessage(WebSocketMessageProtocol):
    def __init__(self, data_source: DataSourceImageResourceDeployerProtocol, payload: WebSocketMessagePayloadType):
        self.data_source = data_source
        self.payload = payload

from AppCore.Service.WebSocket.WebSocketServiceProtocol import (
    WebSocketMessageReceiverProtocol,
    WebSocketServiceProtocol,
    WebSocketHostObjectProtocol
)

from ..ImageResourceProcessorProtocol import ImageResourceProcessorProtocol


class DataSourceImageResourceDeployerWebSocketHost(ImageResourceProcessorProtocol,
                                                   WebSocketHostObjectProtocol,
                                                   WebSocketMessageReceiverProtocol):
    def __init__(self, websocket_service: WebSocketServiceProtocol):
        pass

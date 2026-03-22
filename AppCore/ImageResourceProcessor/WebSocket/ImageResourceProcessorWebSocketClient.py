from AppCore.Service.WebSocket.WebSocketServiceProtocol import (
    WebSocketMessageReceiverProtocol,
    WebSocketServiceProtocol,
)

from ..ImageResourceProcessorProtocol import ImageResourceProcessorProtocol


class DataSourceImageResourceDeployerWebSocketClient(ImageResourceProcessorProtocol,
                                                     WebSocketMessageReceiverProtocol):
    def __init__(self, websocket_service: WebSocketServiceProtocol):
        pass

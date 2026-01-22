from PySide6.QtCore import QUrl
from typing import Optional
from AppCore.Observation import ObservationTower
from .WebSocketServiceProtocol import WebSocketClientDelegate
from PySide6.QtWebSockets import QWebSocket

class WebSocketClient(QWebSocket):
    def __init__(self):
        super().__init__()
        self.delegate: Optional[WebSocketClientDelegate] = None
        
        self.connected.connect(self.on_connect)
        self.textMessageReceived.connect(self.on_message)

    def connect_to_server(self, ip: str, port: Optional[int]):
        if port is None:
            port = 80
        self.open(QUrl(f'ws://{ip}:{port}'))

    def on_connect(self):
        if self.delegate is not None:
            self.delegate.client_connected()

    def on_disconnected(self):
        print("Disconnected from server.")
        if self.delegate is not None:
            self.delegate.client_disconnected()

    def disconnect(self):
        self.close()

    def on_error(self, error_code):
        print(f"Error: {self.client.errorString()}")
        print(f"Error Code: {error_code}")
        
    def on_message(self, message):
        if self.delegate is not None:
            self.delegate.client_received_message(message)

    def send_message(self, message: str):
        self.sendTextMessage(message)
from PySide6.QtCore import QUrl
from typing import Optional
from PySide6.QtWebSockets import QWebSocket

class WebSocketClientDelegate:
    def client_connected(self) -> None:
        return

    def client_disconnected(self) -> None:
        return

    def client_received_message(self, message: str) -> None:
        return

class WebSocketClient(QWebSocket):
    def __init__(self):
        super().__init__()
        self.delegate: Optional[WebSocketClientDelegate] = None
        self._latest_ip: Optional[str] = None

        self.connected.connect(self.on_connect)
        self.errorOccurred.connect(self.handle_error)
        self.disconnected.connect(self.on_disconnected)
        self.textMessageReceived.connect(self.on_message)

    @property
    def latest_ip(self) -> Optional[str]:
        return self._latest_ip

    def connect_to_server(self, ip: str, port: Optional[int]):
        if port is None:
            port = 80
        self.open(QUrl(f'ws://{ip}:{port}'))
        self._latest_ip = ip

    def on_connect(self):
        if self.delegate is not None:
            self.delegate.client_connected()

    def on_disconnected(self):
        print("Disconnected from server.")
        if self.delegate is not None:
            self.delegate.client_disconnected()

    def stop_client(self):
        self.close()

    def handle_error(self, error_code):
        error_string = self.errorString()
        print(f"Connection Error: {error_string} (Code: {error_code})")
        # Optional: Logic to retry connection or cleanup
        self.close()
        
    def on_message(self, message):
        if self.delegate is not None:
            self.delegate.client_received_message(message)

    def send_message(self, message: str):
        self.sendTextMessage(message)
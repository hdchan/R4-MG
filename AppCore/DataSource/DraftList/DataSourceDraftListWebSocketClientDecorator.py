# accepts json encoded file from server and uses that as the datasource for client
# actions will send messages to server

from .DataSourceDraftListProtocol import DataSourceDraftListProtocol
from PySide6.QtWebSockets import QWebSocket
from PySide6.QtCore import QUrl, Slot
from typing import Optional
class DataSourceDraftListWebSocketClientDecoratorDelegate:
    pass
class DataSourceDraftListWebSocketClientDecorator(QWebSocket, DataSourceDraftListProtocol):
    def __init__(self, draft_list_data_source: DataSourceDraftListProtocol):
        super().__init__()
        self._draft_list_data_source = draft_list_data_source
        self.delegate: Optional[DataSourceDraftListWebSocketClientDecorator] = None
        self.connected.connect(self.on_connect)
        self.textMessageReceived.connect(self.on_message)

    def connect(self, ip: str, port: int = 80):
        self.open(QUrl(f'ws://{ip}:{port}'))

    def disconnect(self):
        self.close()

    def send_safe_message(self, text):
        if self.client.isValid():
            self.client.sendTextMessage(text)
            print(f"Sent: {text}")
        else:
            print("Error: Not connected to a server.")

    @Slot()
    def on_connect(self):
        print("Connected! Sending a 'Hello'...")
        self.sendTextMessage("Hello from the other computer!")

    @Slot(str)
    def on_message(self, message):
        print(f"Reply from Server: {message}")
from typing import List, Optional

import jsonpickle  # type: ignore
from PySide6.QtCore import QByteArray, QObject
from PySide6.QtNetwork import QHostAddress
from PySide6.QtWebSockets import QWebSocket, QWebSocketServer

from .WebSocketServiceProtocol import (
    WebSocketClientObjectProtocol,
    WebSocketMessageProtocol,
)


class WebSocketClientObject(WebSocketClientObjectProtocol):
    def __init__(self, websocket: QWebSocket):
        self._websocket = websocket

    def wbc_send_message(self, message: WebSocketMessageProtocol):
        message_str = jsonpickle.encode(message, make_refs=False)
        self._websocket.sendTextMessage(message_str)


class WebSocketHostDelegate:
    def host_started(self, is_started: bool) -> None:
        return

    def host_stopped(self) -> None:
        return

    def host_received_message(self, message: str) -> None:
        return

    def host_received_binary_message(self, message: QByteArray) -> None:
        return

    def host_received_client_connection(self, client_object: WebSocketClientObjectProtocol) -> None:
        return


class WebSocketHost(QObject):
    def __init__(self):
        super().__init__()
        self.server = QWebSocketServer(
            "MyServer", QWebSocketServer.SslMode.NonSecureMode, self)
        self.server.newConnection.connect(self.on_new_connection)
        self.delegate: Optional[WebSocketHostDelegate] = None

        self.clients: List[QWebSocket] = []

    @property
    def has_clients(self) -> bool:
        return len(self.clients) > 0

    def start_server(self, port: int = 80):
        is_started = self.server.listen(QHostAddress.SpecialAddress.Any, port)
        print("Server listening for new clients.")
        if self.delegate is not None:
            self.delegate.host_started(is_started)

    def stop_server(self):
        if self.server.isListening():
            self.server.close()
            print("Server is no longer listening for new clients.")

        # 2. Kick out all CURRENTLY connected clients
        # We create a copy of the list [:] because closing triggers a
        # signal that might modify the list while we loop.
        for client in self.clients[:]:
            client.close()

        # 3. Clear your local list of clients
        self.clients.clear()
        print("All clients disconnected and server stopped.")
        if self.delegate is not None:
            self.delegate.host_stopped()

    def on_new_connection(self):
        # Get the socket for the new client
        client_socket = self.server.nextPendingConnection()
        client_socket.textMessageReceived.connect(self.process_message)
        client_socket.binaryMessageReceived.connect(self.process_binary_message)
        client_socket.disconnected.connect(self.on_disconnected)

        self.clients.append(client_socket)
        if self.delegate is not None:
            self.delegate.host_received_client_connection(
                WebSocketClientObject(client_socket))

    def process_binary_message(self, message: QByteArray):
        if self.delegate is not None:
            self.delegate.host_received_binary_message(message)

    def process_message(self, message: str):
        if self.delegate is not None:
            self.delegate.host_received_message(message)

    def on_disconnected(self):
        client = self.sender()
        self.clients.remove(client)
        # if self.delegate is not None:
        #     self.delegate.host_received_client_disconnected(message)

    def send_message(self, message: str):
        for client in self.clients:
            client.sendTextMessage(message)

    def send_binary_message(self, message: QByteArray):
        for client in self.clients:
            client.sendBinaryMessage(message)

# uses the normal data source
# receives messages from clients, which will call functions as normal and respond with full updated list
# actions will also send full updated list

from typing import Optional

from PySide6.QtCore import QObject, Slot
from PySide6.QtNetwork import QHostAddress
from PySide6.QtWebSockets import QWebSocketServer

from AppCore.Service import DataSerializer

from .DataSourceDraftListProtocol import DataSourceDraftListProtocol
from .DataSourceDraftListWebSocketHostDecoratorDelegate import \
    DataSourceDraftListWebSocketHostDecoratorDelegate


class DataSourceDraftListWebSocketHostDecorator(QObject, DataSourceDraftListProtocol):
    def __init__(self, 
                 draft_list_data_source: DataSourceDraftListProtocol, 
                 data_serializer: DataSerializer):
        super().__init__()
        self._draft_list_data_source = draft_list_data_source
        self._data_serializer = data_serializer
        self.server = QWebSocketServer("MyServer", QWebSocketServer.NonSecureMode, self)
        self.server.newConnection.connect(self.on_new_connection)
        self.delegate: Optional[DataSourceDraftListWebSocketHostDecoratorDelegate] = None
        self.clients = []

    def start_server(self, port: int = 80):
        is_started = self.server.listen(QHostAddress.Any, port)
        if self.delegate is not None:
            self.delegate.server_started(is_started)

    def stop_server(self):
        if self.server.isListening():
            self.server.close()
            print("Server is no longer listening for new clients.")

        # 2. Kick out all CURRENTLY connected clients
        # We create a copy of the list [:] because closing triggers a 
        # signal that might modify the list while we loop.
        for client in self.clients[:]:
            client.sendTextMessage("Server shutting down...")
            client.close()
        
        # 3. Clear your local list of clients
        self.clients.clear()
        print("All clients disconnected and server stopped.")
        if self.delegate is not None:
            self.delegate.server_stopped()

    @Slot()
    def on_new_connection(self):
        # Get the socket for the new client
        client_socket = self.server.nextPendingConnection()
        client_socket.textMessageReceived.connect(self.process_message)
        client_socket.disconnected.connect(self.on_disconnected)
        
        self.clients.append(client_socket)
        print("A client just connected!")
        json_string = self._data_serializer.to_string(self._draft_list_data_source.draft_packs)
        client_socket.sendTextMessage(json_string)

    @Slot(str)
    def process_message(self, message):
        print(f"Client says: {message}")
        # Echo back to the client
        # sender = self.sender()
        # sender.sendTextMessage(f"Server received: {message}")

    @Slot()
    def on_disconnected(self):
        client = self.sender()
        self.clients.remove(client)
        print("Client disconnected.")
# uses the normal data source
# receives messages from clients, which will call functions as normal and respond with full updated list
# actions will also send full updated list

from typing import Any, List, Optional

import jsonpickle
from PySide6.QtCore import QObject, Slot
from PySide6.QtNetwork import QHostAddress
from PySide6.QtWebSockets import QWebSocketServer

from AppCore.Models import DraftPack, LocalCardResource, WebSocketPayload
from AppCore.Observation import (ObservationTower, TransmissionProtocol,
                                 TransmissionReceiverProtocol)
from AppCore.Observation.Events import (DraftListUpdatedEvent,
                                        DraftPackUpdatedEvent)
from AppCore.Service import DataSerializer

from .DataSourceDraftListProtocol import DataSourceDraftListProtocol
from .DataSourceDraftListWebSocketHostDecoratorDelegate import \
    DataSourceDraftListWebSocketHostDecoratorDelegate


class DataSourceDraftListWebSocketHostDecorator(QObject, DataSourceDraftListProtocol, TransmissionReceiverProtocol):
    def __init__(self,
                 draft_list_data_source: DataSourceDraftListProtocol,
                 data_serializer: DataSerializer,
                 observation_tower: ObservationTower):
        super().__init__()
        self._draft_list_data_source = draft_list_data_source
        self._data_serializer = data_serializer
        self.server = QWebSocketServer(
            "MyServer", QWebSocketServer.NonSecureMode, self)
        self.server.newConnection.connect(self.on_new_connection)
        self.delegate: Optional[DataSourceDraftListWebSocketHostDecoratorDelegate] = None
        self.clients = []

        observation_tower.subscribe_multi(
            self, [DraftPackUpdatedEvent, DraftListUpdatedEvent])

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

    def send_clients_message(self, message: str):
        for client in self.clients:
            client.sendTextMessage(message)

    def sync_clients(self):
        self.send_clients_message(WebSocketPayload('sync_clients', {
                                  'draft_packs': self._draft_list_data_source.draft_packs}).encoded_self)

    @Slot()
    def on_new_connection(self):
        # Get the socket for the new client
        client_socket = self.server.nextPendingConnection()
        client_socket.textMessageReceived.connect(self.process_message)
        client_socket.disconnected.connect(self.on_disconnected)

        self.clients.append(client_socket)
        print("A client just connected!")
        event = DraftPackUpdatedEvent()  # force initial sync with host
        client_socket.sendTextMessage(WebSocketPayload('on_new_connection', {
                                      'event': event, 'draft_packs': self._draft_list_data_source.draft_packs}).encoded_self)

    @Slot(str)
    def process_message(self, message):
        payload = WebSocketPayload.decode(message)
        method = getattr(self, payload.action)
        method(**payload.metadata)
        print(payload)

    @Slot()
    def on_disconnected(self):
        client = self.sender()
        self.clients.remove(client)
        print("Client disconnected.")

    @property
    def draft_packs(self) -> List[DraftPack]:
        return self._draft_list_data_source.draft_packs

    # MARK: - modify packs
    def clear_entire_draft_list(self):
        self._draft_list_data_source.clear_entire_draft_list()

    def keep_packs_clear_lists(self):
        self._draft_list_data_source.keep_packs_clear_lists()

    def create_new_pack(self) -> int:
        self._draft_list_data_source.create_new_pack()

    def create_new_pack_from_list(self, name: str, list: List[LocalCardResource]):
        self._draft_list_data_source.create_new_pack_from_list(name, list)

    def update_pack_name(self, pack_index: int, name: str):
        self._draft_list_data_source.update_pack_name(pack_index, name)

    def remove_pack(self, pack_index: int):
        self._draft_list_data_source.remove_pack(pack_index)

    def move_pack_left(self, pack_index: int):
        self._draft_list_data_source.move_pack_left(pack_index)

    def move_pack_right(self, pack_index: int):
        self._draft_list_data_source.move_pack_right(pack_index)

    # MARK: - modify resource order
    def add_resource_to_pack(self, pack_index: int, local_resource: LocalCardResource):
        self._draft_list_data_source.add_resource_to_pack(
            pack_index, local_resource)

    def remove_resource(self, pack_index: int, resource_index: int):
        self._draft_list_data_source.remove_resource(
            pack_index, resource_index)

    def move_up(self, pack_index: int, resource_index: int):
        self._draft_list_data_source.move_up(pack_index, resource_index)

    def move_down(self, pack_index: int, resource_index: int):
        self._draft_list_data_source.move_down(pack_index, resource_index)

    def insert_above(self, pack_index: int, resource_index: int, local_resource: LocalCardResource):
        self._draft_list_data_source.insert_above(
            pack_index, resource_index, local_resource)

    def insert_below(self, pack_index: int, resource_index: int, local_resource: LocalCardResource):
        self._draft_list_data_source.insert_below(
            pack_index, resource_index, local_resource)

    def mark_resource_as_sideboard(self, pack_index: int, resource_index: int, key: str, value: Any):
        self._draft_list_data_source.mark_resource_as_sideboard(
            pack_index, resource_index, key, value)

    # Mark: - TransmissionReceiverProtocol

    def handle_observation_tower_event(self, event: TransmissionProtocol) -> None:
        self.send_clients_message(WebSocketPayload('handle_observation_tower_event', {
                                  'event': event, 'draft_packs': self._draft_list_data_source.draft_packs}).encoded_self)

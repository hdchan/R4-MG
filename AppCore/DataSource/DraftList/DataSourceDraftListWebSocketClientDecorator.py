# accepts json encoded file from server and uses that as the datasource for client
# actions will send messages to server

import json
import copy
from typing import List, Optional

from PySide6.QtCore import QUrl, Slot
from PySide6.QtWebSockets import QWebSocket

from AppCore.Models import DraftPack

from .DataSourceDraftListProtocol import DataSourceDraftListProtocol
from .DataSourceDraftListWebSocketClientDecoratorDelegate import \
    DataSourceDraftListWebSocketClientDecoratorDelegate


class DataSourceDraftListWebSocketClientDecorator(QWebSocket, DataSourceDraftListProtocol):
    def __init__(self):
        super().__init__()
        self.delegate: Optional[DataSourceDraftListWebSocketClientDecoratorDelegate] = None
        
        self.connected.connect(self.on_connect)
        self.textMessageReceived.connect(self.on_message)

        self._packs: List[DraftPack] = []

    def connect_to_server(self, ip: str, port: Optional[int]):
        if port is None:
            port = 80
        self.open(QUrl(f'ws://{ip}:{port}'))

    def disconnect(self):
        self.close()

    @Slot()
    def on_connect(self):
        if self.delegate is not None:
            self.delegate.client_connected()

    @Slot()
    def on_disconnected(self):
        print("Disconnected from server.")
        if self.delegate is not None:
            self.delegate.client_disconnected()

    # @Slot()
    def on_error(self, error_code):
        print(f"Error: {self.client.errorString()}")
        print(f"Error Code: {error_code}")
        

    @Slot(str)
    def on_message(self, message):
        loaded = json.loads(message)
        if loaded is not None:
            for pack_json in loaded:
                self._packs.append(DraftPack.from_json(pack_json))

        if self.delegate is not None:
            self.delegate.client_sync_with_server()


    @property
    def draft_packs(self) -> List[DraftPack]:
        return copy.deepcopy(self._packs)
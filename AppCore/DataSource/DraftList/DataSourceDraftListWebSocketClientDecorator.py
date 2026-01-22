# accepts json encoded file from server and uses that as the datasource for client
# actions will send messages to server

import json
import copy
from typing import List, Optional, Any

from PySide6.QtCore import QUrl, Slot
from PySide6.QtWebSockets import QWebSocket

from AppCore.Models import DraftPack, WebSocketPayload, LocalCardResource
from AppCore.Observation import TransmissionProtocol, ObservationTower

from .DataSourceDraftListProtocol import DataSourceDraftListProtocol
from .DataSourceDraftListWebSocketClientDecoratorDelegate import \
    DataSourceDraftListWebSocketClientDecoratorDelegate


class DataSourceDraftListWebSocketClientDecorator(QWebSocket, DataSourceDraftListProtocol):
    def __init__(self, observation_tower: ObservationTower):
        super().__init__()
        self._observation_tower = observation_tower
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

    def on_error(self, error_code):
        print(f"Error: {self.client.errorString()}")
        print(f"Error Code: {error_code}")
        

    @Slot(str)
    def on_message(self, message):
        payload = WebSocketPayload.decode(message)
        
        if 'draft_packs' in payload.metadata:
            self._packs = payload.metadata['draft_packs']

        if 'event' in payload.metadata:
            self._observation_tower.notify(payload.metadata['event'])

    @property
    def draft_packs(self) -> List[DraftPack]:
        return copy.deepcopy(self._packs)

    # MARK: - modify packs
    def clear_entire_draft_list(self):
        self.sendTextMessage(WebSocketPayload('clear_entire_draft_list').encoded_self)
        
    def keep_packs_clear_lists(self):
        self.sendTextMessage(WebSocketPayload('keep_packs_clear_lists').encoded_self)
        
    def create_new_pack(self) -> int:
        self.sendTextMessage(WebSocketPayload('create_new_pack').encoded_self)

    def create_new_pack_from_list(self, name: str, list: List[LocalCardResource]):
        self.sendTextMessage(WebSocketPayload('create_new_pack_from_list', {'name': name, 'list': list}).encoded_self)
        
    def update_pack_name(self, pack_index: int, name: str):
        self.sendTextMessage(WebSocketPayload('update_pack_name', { 'pack_index': pack_index, 'name': name }).encoded_self)
            
    def remove_pack(self, pack_index: int):
        self.sendTextMessage(WebSocketPayload('remove_pack', { 'pack_index': pack_index }).encoded_self)
            
    def move_pack_left(self, pack_index: int):
        self.sendTextMessage(WebSocketPayload('move_pack_left', { 'pack_index': pack_index }).encoded_self)
    
    def move_pack_right(self, pack_index: int):
        self.sendTextMessage(WebSocketPayload('move_pack_right', { 'pack_index': pack_index }).encoded_self)

    # MARK: - modify resource order
    def add_resource_to_pack(self, pack_index: int, local_resource: LocalCardResource):
        # raise Exception
        self.sendTextMessage(WebSocketPayload('add_resource_to_pack', {'pack_index': pack_index, 'local_resource': local_resource}).encoded_self)
            
    def remove_resource(self, pack_index: int, resource_index: int):
        self.sendTextMessage(WebSocketPayload('remove_resource', { 'pack_index': pack_index, 'resource_index': resource_index }).encoded_self)

    def move_up(self, pack_index: int, resource_index: int):
        self.sendTextMessage(WebSocketPayload('move_up', { 'pack_index': pack_index, 'resource_index': resource_index }).encoded_self)
        
    def move_down(self, pack_index: int, resource_index: int):
        self.sendTextMessage(WebSocketPayload('move_down', { 'pack_index': pack_index, 'resource_index': resource_index }).encoded_self)
        
    def insert_above(self, pack_index: int, resource_index: int, local_resource: LocalCardResource):
        self.sendTextMessage(WebSocketPayload('insert_above', { 'pack_index': pack_index, 'resource_index': resource_index, 'local_resource': local_resource }).encoded_self)
        
    def insert_below(self, pack_index: int, resource_index: int, local_resource: LocalCardResource):
        self.sendTextMessage(WebSocketPayload('insert_below', { 'pack_index': pack_index, 'resource_index': resource_index, 'local_resource': local_resource }).encoded_self)
    
    def mark_resource_as_sideboard(self, pack_index: int, resource_index: int, key: str, value: Any):
        self.sendTextMessage(WebSocketPayload('mark_resource_as_sideboard', { 'pack_index': pack_index, 'resource_index': resource_index, 'key': key, 'value': value }).encoded_self)
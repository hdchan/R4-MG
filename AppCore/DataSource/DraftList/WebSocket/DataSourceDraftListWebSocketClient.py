from typing import List, Any, Optional
from functools import partial
from AppCore.Models import DraftPack, LocalCardResource
from AppCore.Observation import ObservationTower

from ..DataSourceDraftListProtocol import DataSourceDraftListProtocol
from .DataSourceDraftListWebSocketMessagePartials import DataSourceDraftListWebSocketMessagePartials
from AppCore.Service.WebSocket.WebSocketServiceProtocol import (
    WebSocketMessageReceiverProtocol,
    WebSocketServiceProtocol,
    WebSocketMessageProtocol
)
from .DataSourceDraftListWebSocketMessage import DataSourceDraftListWebSocketMessage
from AppCore.Service.WebSocket.Messages import WebSocketMessagePayloadClientAction

class DataSourceDraftListWebSocketClient(DataSourceDraftListProtocol, WebSocketMessageReceiverProtocol):
    def __init__(self,
                 websocket_service: WebSocketServiceProtocol,
                 observation_tower: ObservationTower):
        super().__init__()
        self._websocket_service = websocket_service
        self._observation_tower = observation_tower
        self._latest_ds: Optional[DataSourceDraftListProtocol] = None

        self._websocket_service.register_for_messages(
            self, DataSourceDraftListWebSocketMessage)

    @property
    def observation_tower(self) -> ObservationTower:
        return self._observation_tower

    @property
    def draft_packs(self) -> List[DraftPack]:
        if self._latest_ds is None:
            return []
        return self._latest_ds.draft_packs

    # MARK: - modify packs
    def clear_entire_draft_list(self):
        partial_action = partial(
            DataSourceDraftListWebSocketMessagePartials.clear_entire_draft_list)
        self._send_host_action(partial_action)

    def keep_packs_clear_lists(self):
        partial_action = partial(
            DataSourceDraftListWebSocketMessagePartials.keep_packs_clear_lists)
        self._send_host_action(partial_action)

    def create_new_pack(self):
        partial_action = partial(
            DataSourceDraftListWebSocketMessagePartials.create_new_pack)
        self._send_host_action(partial_action)

    def create_new_pack_from_list(self, name: str, list: List[LocalCardResource]):
        partial_action = partial(
            DataSourceDraftListWebSocketMessagePartials.create_new_pack_from_list, name, list)
        self._send_host_action(partial_action)

    def update_pack_name(self, pack_index: int, name: str):
        partial_action = partial(
            DataSourceDraftListWebSocketMessagePartials.update_pack_name, pack_index, name)
        self._send_host_action(partial_action)

    def remove_pack(self, pack_index: int):
        partial_action = partial(
            DataSourceDraftListWebSocketMessagePartials.remove_pack, pack_index)
        self._send_host_action(partial_action)

    def swap_pack_positions(self, pi1: int, pi2: int):
        partial_action = partial(
            DataSourceDraftListWebSocketMessagePartials.swap_pack_positions, pi1, pi2)
        self._send_host_action(partial_action)

    # MARK: - modify resource order
    def add_resource_to_pack(self, pack_index: int, local_resource: LocalCardResource):
        partial_action = partial(
            DataSourceDraftListWebSocketMessagePartials.add_resource_to_pack, pack_index, local_resource)
        self._send_host_action(partial_action)

    def remove_resource(self, pack_index: int, resource_index: int):
        partial_action = partial(
            DataSourceDraftListWebSocketMessagePartials.remove_resource, pack_index)
        self._send_host_action(partial_action)

    def swap_resources(self, pack_index: int, ri1: int, ri2: int):
        partial_action = partial(
            DataSourceDraftListWebSocketMessagePartials.swap_resources, pack_index, ri1, ri2)
        self._send_host_action(partial_action)

    def insert_resource(self, pack_index: int, resource_index: int, local_resource: LocalCardResource):
        partial_action = partial(
            DataSourceDraftListWebSocketMessagePartials.insert_resource, pack_index, resource_index, local_resource)
        self._send_host_action(partial_action)

    def mark_resource_as_sideboard(self, pack_index: int, resource_index: int, key: str, value: Any):
        partial_action = partial(
            DataSourceDraftListWebSocketMessagePartials.mark_resource_as_sideboard, pack_index, resource_index, key, value)
        self._send_host_action(partial_action)

    def _send_host_action(self, partial_action):
        payload = WebSocketMessagePayloadClientAction(
            partial_action=partial_action)
        message = DataSourceDraftListWebSocketMessage(
            self, payload)
        self._websocket_service.send_websocket_message(message)

    # MARK: - WebSocketMessageReceiverProtocol
    def wsmr_will_handle_websocket_message(self, message: WebSocketMessageProtocol) -> None:
        self._latest_ds = message.data_source

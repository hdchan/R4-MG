
from typing import Any, List, Optional

from PySide6.QtCore import QObject

from AppCore.Models import DraftPack, LocalCardResource
from AppCore.Observation import (ObservationTower, TransmissionProtocol,
                                 TransmissionReceiverProtocol)
from AppCore.Service.WebSocket.Messages import \
    WebSocketMessagePayloadObservationTowerTransmission
from AppCore.Service.WebSocket.WebSocketModelLocalizer import \
    WebSocketModelLocalizer
from AppCore.Service.WebSocket.WebSocketServiceProtocol import (
    WebSocketClientObjectProtocol, WebSocketHostObjectProtocol,
    WebSocketMessageReceiverProtocol, WebSocketServiceProtocol)

from ..DataSourceDraftListProtocol import DataSourceDraftListProtocol
from ..Events import DraftListUpdatedEvent, DraftPackUpdatedEvent
from .DataSourceDraftListWebSocketMessage import \
    DataSourceDraftListWebSocketMessage


class DataSourceDraftListWebSocketHost(QObject,
                                       DataSourceDraftListProtocol,
                                       WebSocketMessageReceiverProtocol,
                                       TransmissionReceiverProtocol,
                                       WebSocketHostObjectProtocol):
    def __init__(self,
                 observation_tower: ObservationTower,
                 websocket_service: WebSocketServiceProtocol,
                 websocket_model_localizer: WebSocketModelLocalizer,
                 draft_list_data_source: DataSourceDraftListProtocol):
        super().__init__()
        self._draft_list_data_source = draft_list_data_source
        self._websocket_service = websocket_service
        self._websocket_model_localizer = websocket_model_localizer

        self._websocket_service.register_as_host(self)
        self._websocket_service.register_for_messages(
            self, DataSourceDraftListWebSocketMessage)
        observation_tower.subscribe_multi(
            self, [DraftPackUpdatedEvent, DraftListUpdatedEvent])

    @property
    def draft_packs(self) -> List[DraftPack]:
        return self._draft_list_data_source.draft_packs

    # MARK: - modify packs
    def clear_entire_draft_list(self):
        self._draft_list_data_source.clear_entire_draft_list()

    def keep_packs_clear_lists(self):
        self._draft_list_data_source.keep_packs_clear_lists()

    def create_new_pack(self):
        self._draft_list_data_source.create_new_pack()

    def create_new_pack_from_list(self, name: str, list: List[LocalCardResource]):
        localized_resource_list = self._websocket_model_localizer.localize_local_card_resource_list(
            list)
        self._draft_list_data_source.create_new_pack_from_list(
            name, localized_resource_list)

    def update_pack_name(self, pack_index: int, name: str):
        self._draft_list_data_source.update_pack_name(pack_index, name)

    def remove_pack(self, pack_index: int):
        self._draft_list_data_source.remove_pack(pack_index)

    def swap_pack_positions(self, pi1: int, pi2: int):
        self._draft_list_data_source.swap_pack_positions(pi1, pi2)

    # MARK: - modify resource order
    def add_resource_to_pack(self, pack_index: int, local_resource: LocalCardResource):
        localized_resource = self._websocket_model_localizer.localize_local_card_resource(
            local_resource)
        self._draft_list_data_source.add_resource_to_pack(
            pack_index, localized_resource)

    def remove_resource(self, pack_index: int, resource_index: int):
        self._draft_list_data_source.remove_resource(
            pack_index, resource_index)

    def swap_resources(self, pack_index: int, ri1: int, ri2: int):
        self._draft_list_data_source.swap_resources(
            pack_index, ri1, ri2)

    def insert_resource(self, pack_index: int, resource_index: int, local_resource: LocalCardResource):
        localized_resource = self._websocket_model_localizer.localize_local_card_resource(
            local_resource)
        self._draft_list_data_source.insert_resource(
            pack_index, resource_index, localized_resource)

    def mark_resource_as_sideboard(self, pack_index: int, resource_index: int, key: str, value: Any):
        self._draft_list_data_source.mark_resource_as_sideboard(
            pack_index, resource_index, key, value)

    # MARK: - WebSocketHostObjectProtocol
    def wsh_handle_new_connection(self, client_object: WebSocketClientObjectProtocol) -> None:
        event = DraftPackUpdatedEvent()
        message = DataSourceDraftListWebSocketMessage(
            data_source=self._draft_list_data_source,
            payload=WebSocketMessagePayloadObservationTowerTransmission(event))
        client_object.wbc_send_message(message)

    # Mark: - TransmissionReceiverProtocol
    def handle_observation_tower_event(self, event: TransmissionProtocol) -> None:
        message = DataSourceDraftListWebSocketMessage(
            data_source=self._draft_list_data_source,
            payload=WebSocketMessagePayloadObservationTowerTransmission(event))
        self._websocket_service.send_websocket_message(message)

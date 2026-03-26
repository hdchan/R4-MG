

from PySide6.QtCore import QObject
from typing import List, Optional
from AppCore.Observation import (
    ObservationTower,
    TransmissionProtocol,
    TransmissionReceiverProtocol,
)
from AppCore.Service.WebSocket.Messages import (
    WebSocketMessagePayloadObservationTowerTransmission,
)
from AppCore.Service.WebSocket.WebSocketServiceProtocol import (
    WebSocketClientObjectProtocol,
    WebSocketHostObjectProtocol,
    WebSocketMessageReceiverProtocol,
    WebSocketServiceProtocol,
)
from AppCore.Models import LocalResourceDraftListWindow
from ..DataSourceDraftListWindowResourceDeployerProtocol import (
    DataSourceDraftListWindowResourceDeployerProtocol,
)
from ..Events import DraftListWindowResourceLoadEvent, DraftListWindowResourceUpdatedEvent
from .DataSourceDraftListWindowResourceWebSocketMessage import (
    DataSourceDraftListWindowResourceWebSocketMessage,
)


class DataSourceDraftListWindowResourceWebSocketHost(QObject,
                                                     DataSourceDraftListWindowResourceDeployerProtocol,
                                                     WebSocketMessageReceiverProtocol,
                                                     TransmissionReceiverProtocol,
                                                     WebSocketHostObjectProtocol):
    def __init__(self,
                 observation_tower: ObservationTower,
                 websocket_service: WebSocketServiceProtocol,
                 draft_list_window_resource_data_source: DataSourceDraftListWindowResourceDeployerProtocol):
        super().__init__()
        self._draft_list_window_resource_data_source = draft_list_window_resource_data_source
        self._websocket_service = websocket_service

        self._websocket_service.register_as_host(self)
        self._websocket_service.register_for_messages(
            self, DataSourceDraftListWindowResourceWebSocketMessage)
        observation_tower.subscribe_multi(
            self, [DraftListWindowResourceLoadEvent, DraftListWindowResourceUpdatedEvent])

    # MARK: - DataSourceDraftListWindowResourceDeployerProtocol
    @property
    def draft_list_windows(self) -> List[LocalResourceDraftListWindow]:
        return self._draft_list_window_resource_data_source.draft_list_windows

    def load_resources(self):
        self._draft_list_window_resource_data_source.load_resources()

    def create_new_window(self, window_name: str):
        self._draft_list_window_resource_data_source.create_new_window(window_name)

    def delete_window_resource(self, resource: LocalResourceDraftListWindow):
        self._draft_list_window_resource_data_source.delete_window_resource(resource)

    def unbind_draft_pack_name(self, resource: LocalResourceDraftListWindow):
        self._draft_list_window_resource_data_source.unbind_draft_pack_name(resource)

    def update_window_dimension(self, resource: LocalResourceDraftListWindow, width: Optional[int], height: Optional[int]):
        self._draft_list_window_resource_data_source.update_window_dimension(resource, width, height)

    def update_window_draft_pack(self, resource: LocalResourceDraftListWindow, draft_pack_identifier: Optional[str]):
        self._draft_list_window_resource_data_source.update_window_draft_pack(resource, draft_pack_identifier)

    # MARK: - WebSocketHostObjectProtocol
    def wsh_handle_new_connection(self, client_object: WebSocketClientObjectProtocol) -> None:
        event = DraftListWindowResourceLoadEvent()
        message = DataSourceDraftListWindowResourceWebSocketMessage(
            data_source=self._draft_list_window_resource_data_source,
            payload=WebSocketMessagePayloadObservationTowerTransmission(event))
        client_object.wbc_send_message(message)

    # Mark: - TransmissionReceiverProtocol
    def handle_observation_tower_event(self, event: TransmissionProtocol) -> None:
        message = DataSourceDraftListWindowResourceWebSocketMessage(
            data_source=self._draft_list_window_resource_data_source,
            payload=WebSocketMessagePayloadObservationTowerTransmission(event))
        self._websocket_service.send_websocket_message(message)

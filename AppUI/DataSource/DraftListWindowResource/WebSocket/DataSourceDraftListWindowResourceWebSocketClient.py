from typing import List, Optional

from AppCore.Models import LocalResourceDraftListWindow
from AppCore.Observation import ObservationTower
from AppCore.Service.WebSocket.WebSocketServiceProtocol import (
    WebSocketMessageProtocol,
    WebSocketMessageReceiverProtocol,
    WebSocketServiceProtocol,
)

from ..DataSourceDraftListWindowResourceDeployerProtocol import (
    DataSourceDraftListWindowResourceDeployerProtocol,
)
from .DataSourceDraftListWindowResourceWebSocketMessage import (
    DataSourceDraftListWindowResourceWebSocketMessage,
)


class DataSourceDraftListWindowResourceWebSocketClient(DataSourceDraftListWindowResourceDeployerProtocol, WebSocketMessageReceiverProtocol):
    def __init__(self,
                 websocket_service: WebSocketServiceProtocol,
                 observation_tower: ObservationTower):
        super().__init__()
        self._websocket_service = websocket_service
        self._observation_tower = observation_tower
        self._latest_ds: Optional[DataSourceDraftListWindowResourceDeployerProtocol] = None

        self._websocket_service.register_for_messages(
            self, DataSourceDraftListWindowResourceWebSocketMessage)

    # MARK: - DataSourceDraftListWindowResourceDeployerProtocol
    @property
    def draft_list_windows(self) -> List[LocalResourceDraftListWindow]:
        return self._latest_ds.draft_list_windows

    def load_resources(self):
        raise Exception("Not allowed")

    def create_new_window(self, window_name: str):
        raise Exception("Not allowed")

    def delete_window_resource(self, resource: LocalResourceDraftListWindow):
        raise Exception("Not allowed")

    def unbind_draft_pack_name(self, resource: LocalResourceDraftListWindow):
        raise Exception("Not allowed")

    def update_window_dimension(self, resource: LocalResourceDraftListWindow, width: Optional[int], height: Optional[int]):
        raise Exception("Not allowed")

    def update_window_draft_pack(self, resource: LocalResourceDraftListWindow, draft_pack_identifier: Optional[str]):
        raise Exception("Not allowed")

    @property
    def observation_tower(self) -> ObservationTower:
        return self._observation_tower

    # MARK: - WebSocketMessageReceiverProtocol

    def wsmr_will_handle_websocket_message(self, message: WebSocketMessageProtocol) -> None:
        self._latest_ds = message.data_source

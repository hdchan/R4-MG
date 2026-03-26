from typing import Optional

from AppCore.Config import ConfigurationManager
from AppCore.DataSource.DraftList.DataSourceDraftListProtocol import (
    DataSourceDraftListProviding,
)
from AppCore.DataSource.DraftList.Events import DraftPackUpdatedEvent
from AppCore.Observation import (
    ObservationTower,
    TransmissionProtocol,
    TransmissionReceiverProtocol,
)
from AppCore.Service import DataSerializer
from AppCore.Service.WebSocket.Events import WebSocketStatusUpdatedEvent
from AppCore.Service.WebSocket.WebSocketServiceProtocol import (
    WebSocketMessageReceiverProtocol,
    WebSocketServiceProtocol,
    WebSocketServiceStatus,
)

from .DataSourceDraftListWindowResourceDeployer import (
    DataSourceDraftListWindowResourceDeployer,
)
from .DataSourceDraftListWindowResourceDeployerProtocol import (
    DataSourceDraftListWindowResourceDeployerProtocol,
    DataSourceDraftListWindowResourceDeployerProviding,
)
from .WebSocket.DataSourceDraftListWindowResourceWebSocketClient import (
    DataSourceDraftListWindowResourceWebSocketClient,
)
from .WebSocket.DataSourceDraftListWindowResourceWebSocketHost import (
    DataSourceDraftListWindowResourceWebSocketHost,
)


class DataSourceDraftListWindowResourceDeployerProvider(DataSourceDraftListWindowResourceDeployerProviding, TransmissionReceiverProtocol):
    def __init__(self,
                 configuration_manager: ConfigurationManager,
                 observation_tower: ObservationTower,
                 data_source_draft_list_provider: DataSourceDraftListProviding,
                 data_serializer: DataSerializer,
                 websocket_service: WebSocketServiceProtocol):
        self._observation_tower = observation_tower
        self._websocket_service = websocket_service
        self._window_resource_data_source = DataSourceDraftListWindowResourceDeployer(configuration_manager,
                                                                                      observation_tower,
                                                                                      data_source_draft_list_provider,
                                                                                      data_serializer)

        self._current_websocket_ds: Optional[DataSourceDraftListWindowResourceDeployerProtocol |
                                             WebSocketMessageReceiverProtocol] = None

        observation_tower.subscribe(self, WebSocketStatusUpdatedEvent)

    @property
    def draft_list_window_resource_data_source(self) -> DataSourceDraftListWindowResourceDeployerProtocol:
        # if self._websocket_service.state != WebSocketServiceStatus.NONE:
        #     if self._current_websocket_ds is not None:
        #         return self._current_websocket_ds  # type: ignore

        # We probably don't need websockets as this is more of something that the host only needs to control
        return self._window_resource_data_source

    def handle_observation_tower_event(self, event: TransmissionProtocol) -> None:
        pass
        # if type(event) is WebSocketStatusUpdatedEvent:
        #     if self._websocket_service.state == WebSocketServiceStatus.IS_CLIENT:
        #         self._current_websocket_ds = DataSourceDraftListWindowResourceWebSocketClient(self._websocket_service,
        #                                                                                       self._observation_tower)
        #     elif self._websocket_service.state == WebSocketServiceStatus.IS_HOST:
        #         self._current_websocket_ds = DataSourceDraftListWindowResourceWebSocketHost(self._observation_tower,
        #                                                                                     self._websocket_service,
        #                                                                                     self._window_resource_data_source)
        #     else:
        #         self._current_websocket_ds = None
        #     self._observation_tower.notify(DraftPackUpdatedEvent())

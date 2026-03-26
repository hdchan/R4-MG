from typing import Optional

from AppCore.Config import ConfigurationManager
from AppCore.Observation import ObservationTower, TransmissionProtocol, TransmissionReceiverProtocol
from AppCore.Service import DataSerializer
from AppCore.Service.WebSocket.Events import WebSocketStatusUpdatedEvent
from AppCore.Service.WebSocket.WebSocketServiceProtocol import \
    WebSocketMessageReceiverProtocol, WebSocketServiceStatus, WebSocketServiceProtocol

from .DataSourceDraftList import DataSourceDraftList
from .DataSourceDraftListProtocol import (DataSourceDraftListProtocol,
                                          DataSourceDraftListProviding)
from .WebSocket.DataSourceDraftListWebSocketClient import DataSourceDraftListWebSocketClient
from .WebSocket.DataSourceDraftListWebSocketHost import DataSourceDraftListWebSocketHost
from .Events import DraftPackUpdatedEvent
from AppCore.DataSource.ImageResourceDeployer.DataSourceImageResourceDeployerProtocol import DataSourceImageResourceDeployerProviding

class DataSourceDraftListProvider(DataSourceDraftListProviding, TransmissionReceiverProtocol):
    def __init__(self,
                 configuration_manager: ConfigurationManager,
                 observation_tower: ObservationTower,
                 data_serializer: DataSerializer,
                 websocket_service: WebSocketServiceProtocol, 
                 data_source_image_resource_deployer_provider: DataSourceImageResourceDeployerProviding):
        self._observation_tower = observation_tower
        self._data_serializer = data_serializer
        self._websocket_service = websocket_service
        self._draft_list_data_source = DataSourceDraftList(configuration_manager,
                                                           observation_tower,
                                                           data_serializer, 
                                                           data_source_image_resource_deployer_provider)

        self._current_websocket_ds: Optional[DataSourceDraftListProtocol |
                                             WebSocketMessageReceiverProtocol] = None

        observation_tower.subscribe(self, WebSocketStatusUpdatedEvent)

    @property
    def draft_list_data_source(self) -> DataSourceDraftListProtocol:
        if self._websocket_service.state != WebSocketServiceStatus.NONE:
            if self._current_websocket_ds is not None:
                return self._current_websocket_ds  # type: ignore
        return self._draft_list_data_source

    def handle_observation_tower_event(self, event: TransmissionProtocol) -> None:
        if type(event) is WebSocketStatusUpdatedEvent:
            if self._websocket_service.state == WebSocketServiceStatus.IS_CLIENT:
                self._current_websocket_ds = DataSourceDraftListWebSocketClient(self._websocket_service,
                                                                                self._observation_tower)
            elif self._websocket_service.state == WebSocketServiceStatus.IS_HOST:
                self._current_websocket_ds = DataSourceDraftListWebSocketHost(self._observation_tower,
                                                                              self._websocket_service,
                                                                              self._draft_list_data_source)
            else:
                self._current_websocket_ds = None
            self._observation_tower.notify(DraftPackUpdatedEvent())


from typing import Optional

from AppCore.Config import ConfigurationManager
from AppCore.ImageResource import ImageResourceProcessorProviding
from AppCore.Observation import ObservationTower
from AppCore.Service.WebSocket.WebSocketServiceProtocol import (
    WebSocketServiceProtocol, WebSocketServiceStatus, WebSocketMessageReceiverProtocol)

from .DataSourceImageResourceDeployer import DataSourceImageResourceDeployer
from .DataSourceImageResourceDeployerProtocol import (
    DataSourceImageResourceDeployerProtocol,
    DataSourceImageResourceDeployerProviding)
from .DataSourceImageResourceDeployerWebSocketClient import \
    DataSourceImageResourceDeployerWebSocketClient
from .DataSourceImageResourceDeployerWebSocketHost import \
    DataSourceImageResourceDeployerWebSocketHost
from AppCore.Observation.Events import WebSocketStatusUpdatedEvent
from AppCore.Observation import TransmissionProtocol, TransmissionReceiverProtocol


class DataSourceImageResourceDeployerProvider(DataSourceImageResourceDeployerProviding, TransmissionReceiverProtocol):
    def __init__(self,
                 configuration_manager: ConfigurationManager,
                 observation_tower: ObservationTower,
                 image_resource_processor_provider: ImageResourceProcessorProviding,
                 websocket_service: WebSocketServiceProtocol):
        self._image_resource_processor_provider = image_resource_processor_provider
        self._websocket_service = websocket_service
        self._observation_tower = observation_tower
        self._data_source_image_resource_deployer = DataSourceImageResourceDeployer(configuration_manager,
                                                                                    observation_tower,
                                                                                    image_resource_processor_provider)
        self._current_websocket_ds: Optional[DataSourceImageResourceDeployerProtocol |
                                             WebSocketMessageReceiverProtocol] = None

        observation_tower.subscribe(self, WebSocketStatusUpdatedEvent)

    @property
    def data_source_image_resource_deployer(self) -> DataSourceImageResourceDeployerProtocol:
        if self._websocket_service.state == WebSocketServiceStatus.IS_CLIENT or self._websocket_service.state == WebSocketServiceStatus.IS_HOST:
            if self._current_websocket_ds is not None:
                return self._current_websocket_ds
        return self._data_source_image_resource_deployer

    def handle_observation_tower_event(self, event: TransmissionProtocol) -> None:
        if type(event) is WebSocketStatusUpdatedEvent:
            if self._websocket_service.state == WebSocketServiceStatus.IS_CLIENT:
                self._current_websocket_ds = DataSourceImageResourceDeployerWebSocketClient(
                    self._websocket_service, self._observation_tower, self._image_resource_processor_provider)
            elif self._websocket_service.state == WebSocketServiceStatus.IS_HOST:
                self._current_websocket_ds = DataSourceImageResourceDeployerWebSocketHost(self._websocket_service,
                                                                                          self._data_source_image_resource_deployer)

            self._websocket_service.register_for_messages(
                'stuff', self._current_websocket_ds)

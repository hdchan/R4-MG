
from typing import Optional

from AppCore.Config import ConfigurationManager
from AppCore.ImageResourceProcessor import ImageResourceProcessorProviding
from AppCore.Observation import (ObservationTower, TransmissionProtocol,
                                 TransmissionReceiverProtocol)
from AppCore.Service.WebSocket.Events import WebSocketStatusUpdatedEvent
from AppCore.Service.WebSocket.WebSocketServiceProtocol import (
    WebSocketMessageReceiverProtocol, WebSocketServiceProtocol,
    WebSocketServiceStatus)

from .DataSourceImageResourceDeployer import DataSourceImageResourceDeployer
from .DataSourceImageResourceDeployerProtocol import (
    DataSourceImageResourceDeployerProtocol,
    DataSourceImageResourceDeployerProviding)
from .DataSourceRecentPublished import DataSourceRecentPublished
from .WebSocket.DataSourceImageResourceDeployerWebSocketClient import \
    DataSourceImageResourceDeployerWebSocketClient
from .WebSocket.DataSourceImageResourceDeployerWebSocketHost import \
    DataSourceImageResourceDeployerWebSocketHost


class DataSourceImageResourceDeployerProvider(DataSourceImageResourceDeployerProviding, TransmissionReceiverProtocol):
    def __init__(self,
                 configuration_manager: ConfigurationManager,
                 observation_tower: ObservationTower,
                 image_resource_processor_provider: ImageResourceProcessorProviding,
                 websocket_service: WebSocketServiceProtocol,
                 data_source_recent_published: DataSourceRecentPublished):
        self._image_resource_processor_provider = image_resource_processor_provider
        self._websocket_service = websocket_service
        self._observation_tower = observation_tower
        self._data_source_image_resource_deployer = DataSourceImageResourceDeployer(configuration_manager,
                                                                                    observation_tower,
                                                                                    image_resource_processor_provider,
                                                                                    websocket_service,
                                                                                    data_source_recent_published)
        self._current_websocket_ds: Optional[DataSourceImageResourceDeployerProtocol |
                                             WebSocketMessageReceiverProtocol] = None

        observation_tower.subscribe(self, WebSocketStatusUpdatedEvent)

    @property
    def data_source_image_resource_deployer(self) -> DataSourceImageResourceDeployerProtocol:
        if self._websocket_service.state != WebSocketServiceStatus.NONE:
            if self._current_websocket_ds is not None:
                return self._current_websocket_ds  # type: ignore
        return self._data_source_image_resource_deployer

    def handle_observation_tower_event(self, event: TransmissionProtocol) -> None:
        if type(event) is WebSocketStatusUpdatedEvent:
            if self._websocket_service.state == WebSocketServiceStatus.IS_CLIENT:
                self._current_websocket_ds = DataSourceImageResourceDeployerWebSocketClient(
                    self._websocket_service, self._observation_tower, self._image_resource_processor_provider)
            elif self._websocket_service.state == WebSocketServiceStatus.IS_HOST:
                self._current_websocket_ds = DataSourceImageResourceDeployerWebSocketHost(self._observation_tower,
                                                                                          self._websocket_service,
                                                                                          self._image_resource_processor_provider,
                                                                                          self._data_source_image_resource_deployer)
            else:
                self._current_websocket_ds = None
            self._data_source_image_resource_deployer.load_production_resources()

from functools import partial
from typing import List, Optional

from AppCore.DataSource.ImageResourceDeployer.Events import (
    DataSourceImageResourceDeployerStateUpdatedEvent,
    ProductionCardResourcesLoadEvent,
)
from AppCore.ImageResourceProcessor.ImageResourceProcessorProtocol import (
    ImageResourceProcessorProviding,
)
from AppCore.Models import DeploymentCardResource, LocalCardResource
from AppCore.Observation import ObservationTower
from AppCore.Service.WebSocket.Messages import WebSocketMessagePayloadOnLoadWithHost, WebSocketMessagePayloadObservationTowerTransmission
from AppCore.Service.WebSocket.WebSocketMessageProtocol import WebSocketMessageProtocol
from AppCore.Service.WebSocket.WebSocketServiceProtocol import (
    WebSocketMessageReceiverProtocol,
    WebSocketServiceProtocol,
)

from ..DataSourceImageResourceDeployerProtocol import (
    DataSourceImageResourceDeployerProtocol,
)
from .DataSourceImageResourceDeployerWebSocketMessage import (
    DataSourceImageResourceDeployerWebSocketMessage,
)
from .DataSourceImageResourceDeployerWebSocketMessagePayloadAction import (
    DataSourceImageResourceDeployerWebSocketMessagePayloadAction,
    stage_resource_action,
    unstage_resource_action,
    publish_staged_resources_action
)


class DataSourceImageResourceDeployerWebSocketClient(DataSourceImageResourceDeployerProtocol, WebSocketMessageReceiverProtocol):
    def __init__(self,
                 websocket_service: WebSocketServiceProtocol,
                 observation_tower: ObservationTower,
                 image_resource_processor_provider: ImageResourceProcessorProviding):
        self._websocket_service = websocket_service
        self._observation_tower = observation_tower
        self._image_resource_processor_provider = image_resource_processor_provider
        self._latest_ds: Optional[DataSourceImageResourceDeployerProtocol] = None

        # self._websocket_service.register_as_client(self)
        self._websocket_service.register_for_messages(
            self, DataSourceImageResourceDeployerWebSocketMessage)

    # MARK: - DataSourceImageResourceDeployerProtocol

    @property
    def deployment_resources(self) -> List[DeploymentCardResource]:
        if self._latest_ds is None:
            return []
        resources = self._latest_ds.deployment_resources
        for r in resources:
            staged_resource = r.staged_resource
            if staged_resource is not None:
                # async download staged images if needed
                # TODO: can we refactor image resource to websocket
                self._image_resource_processor_provider.image_resource_processor.async_store_local_resource(
                    staged_resource)
        return resources

    @property
    def can_publish_staged_resources(self) -> bool:
        if self._latest_ds is None:
            return False
        return self._latest_ds.can_publish_staged_resources

    def latest_deployment_resource(self, deployment_resource: DeploymentCardResource) -> Optional[DeploymentCardResource]:
        if self._latest_ds is None:
            return None
        return self._latest_ds.latest_deployment_resource(deployment_resource)

    def stage_resource(self, deployment_resource: DeploymentCardResource, selected_resource: LocalCardResource):
        partial_action = partial(stage_resource_action, deployment_resource, selected_resource)
        self._send_host_action(partial_action)

    def unstage_resource(self, deployment_resource: DeploymentCardResource):
        partial_action = partial(unstage_resource_action, deployment_resource)
        self._send_host_action(partial_action)

    def publish_staged_resources(self):
        partial_action = partial(publish_staged_resources_action)
        self._send_host_action(partial_action)

    def _send_host_action(self, partial_action):
        payload = DataSourceImageResourceDeployerWebSocketMessagePayloadAction(
            partial_action=partial_action)
        message = DataSourceImageResourceDeployerWebSocketMessage(
            self, payload)
        self._websocket_service.send_websocket_message(message)

    # MARK: - WebSocketMessageReceiverProtocol
    def wsmr_handle_websocket_message(self, message: WebSocketMessageProtocol) -> None:
        if type(message) is DataSourceImageResourceDeployerWebSocketMessage:
            self._latest_ds = message.data_source
            payload = message.payload
            # if type(payload) is WebSocketMessagePayloadOnLoadWithHost:
            #     self._observation_tower.notify(ProductionCardResourcesLoadEvent(
            #         event_type=ProductionCardResourcesLoadEvent.EventType.FINISHED))
            if type(payload) is WebSocketMessagePayloadObservationTowerTransmission:
                self._observation_tower.notify(payload.event)
            # else:
            #     self._observation_tower.notify(
            #         DataSourceImageResourceDeployerStateUpdatedEvent())

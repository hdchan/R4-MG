from functools import partial
from typing import List, Optional

from AppCore.ImageResourceProcessor.ImageResourceProcessorProtocol import (
    ImageResourceProcessorProviding,
)
from AppCore.Models import DeploymentCardResource, LocalCardResource
from AppCore.Observation import ObservationTower
from AppCore.Service.WebSocket.Messages import WebSocketMessagePayloadClientAction, WebSocketMessagePayloadObservationTowerTransmission
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
from .DataSourceImageResourceDeployerWebSocketMessagePartials import DataSourceImageResourceDeployerWebSocketMessagePartials


class DataSourceImageResourceDeployerWebSocketClient(DataSourceImageResourceDeployerProtocol,
                                                     WebSocketMessageReceiverProtocol):
    def __init__(self,
                 websocket_service: WebSocketServiceProtocol,
                 observation_tower: ObservationTower,
                 image_resource_processor_provider: ImageResourceProcessorProviding):
        self._websocket_service = websocket_service
        self._observation_tower = observation_tower
        self._image_resource_processor_provider = image_resource_processor_provider
        self._latest_ds: Optional[DataSourceImageResourceDeployerProtocol] = None

        self._websocket_service.register_for_messages(
            self, DataSourceImageResourceDeployerWebSocketMessage)

    @property
    def observation_tower(self) -> ObservationTower:
        return self._observation_tower

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

    def deployment_resource_for_file_name(self, file_name: str) -> Optional[DeploymentCardResource]:
        if self._latest_ds is None:
            return None
        return self._latest_ds.deployment_resource_for_file_name(file_name)

    def load_production_resources(self):
        raise Exception("Not allowed")

    def latest_deployment_resource(self, deployment_resource: DeploymentCardResource) -> Optional[DeploymentCardResource]:
        if self._latest_ds is None:
            return None
        return self._latest_ds.latest_deployment_resource(deployment_resource)

    def stage_resource(self, deployment_resource: DeploymentCardResource, selected_resource: LocalCardResource):
        partial_action = partial(
            DataSourceImageResourceDeployerWebSocketMessagePartials.stage_resource, deployment_resource, selected_resource)
        self._send_host_action(partial_action)

    def unstage_resource(self, deployment_resource: DeploymentCardResource):
        partial_action = partial(
            DataSourceImageResourceDeployerWebSocketMessagePartials.unstage_resource, deployment_resource)
        self._send_host_action(partial_action)

    def publish_staged_resources(self):
        partial_action = partial(
            DataSourceImageResourceDeployerWebSocketMessagePartials.publish_staged_resources)
        self._send_host_action(partial_action)

    def generate_new_file(self, file_name: str, placeholder_image_path: Optional[str]):
        raise Exception("Not allowed")

    @property
    def is_publishing(self) -> bool:
        if self._latest_ds is None:
            return False
        return self._latest_ds.is_publishing

    def attach_preview_binary_to_prod_resources(self) -> None:
        raise Exception("Not allowed")

    def _send_host_action(self, partial_action):
        payload = WebSocketMessagePayloadClientAction(
            partial_action=partial_action)
        message = DataSourceImageResourceDeployerWebSocketMessage(
            self, payload)
        self._websocket_service.send_websocket_message(message)

    # MARK: - WebSocketMessageReceiverProtocol
    def wsmr_will_handle_websocket_message(self, message: WebSocketMessageProtocol) -> None:
        self._latest_ds = message.data_source

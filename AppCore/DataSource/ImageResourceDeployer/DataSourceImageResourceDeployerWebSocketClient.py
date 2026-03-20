from .DataSourceImageResourceDeployerProtocol import DataSourceImageResourceDeployerProtocol

from AppCore.Service.WebSocket.WebSocketServiceProtocol import WebSocketMessageReceiverProtocol, WebSocketServiceProtocol, WebSocketMessageProtocol

from typing import List, Optional

from AppCore.Models import DeploymentCardResource
from AppCore.Observation import ObservationTower
from AppCore.Observation.Events import ProductionCardResourcesLoadEvent
from AppCore.DataSource.ImageResourceDeployer.DataSourceImageResourceDeployer import DataSourceImageResourceDeployer
from AppCore.Service.WebSocket.Messages.ClientConnectedMessage import ClientConnectedMessage
from AppCore.Service.WebSocket.Messages.ActionFromClient import ActionFromClient
from AppCore.Models import LocalCardResource
from AppCore.ImageResource.ImageResourceProcessorProtocol import ImageResourceProcessorProviding


class DataSourceImageResourceDeployerWebSocketClient(DataSourceImageResourceDeployerProtocol, WebSocketMessageReceiverProtocol):
    def __init__(self,
                 websocket_service: WebSocketServiceProtocol,
                 observation_tower: ObservationTower,
                 image_resource_processor_provider: ImageResourceProcessorProviding):
        self._websocket_service = websocket_service
        self._observation_tower = observation_tower
        self._image_resource_processor_provider = image_resource_processor_provider
        self._latest_ds: Optional[DataSourceImageResourceDeployer] = None

    def handle_websocket_message(self, message: WebSocketMessageProtocol) -> None:
        if type(message) is ClientConnectedMessage:
            self._latest_ds = message.object
            finish_load_event = ProductionCardResourcesLoadEvent(
                ProductionCardResourcesLoadEvent.EventType.FINISHED)
            self._observation_tower.notify(finish_load_event)

    @property
    def deployment_resources(self) -> List[DeploymentCardResource]:
        if self._latest_ds is None:
            return []
        resources = self._latest_ds.deployment_resources
        for r in resources:
            staged_resource = r.staged_resource
            if staged_resource is not None:
                # async download staged images if needed
                self._image_resource_processor_provider.image_resource_processor.async_store_local_resource(
                    staged_resource)
        return resources

    @property
    def can_publish_staged_resources(self) -> bool:
        if self._latest_ds is None:
            return False
        return self._latest_ds.can_publish_staged_resources
        # return True

    def latest_deployment_resource(self, deployment_resource: DeploymentCardResource) -> Optional[DeploymentCardResource]:
        if self._latest_ds is None:
            return None
        return self._latest_ds.latest_deployment_resource(deployment_resource)

    def stage_resource(self, deployment_resource: DeploymentCardResource, selected_resource: LocalCardResource, is_async_store: bool = True):
        kwargs = {
            'deployment_resource': deployment_resource,
            'selected_resource': selected_resource,
            'is_async_store': is_async_store
        }
        message = ActionFromClient("stuff", "stage_resource", **kwargs)
        self._websocket_service.send_message(message)

    def unstage_resource(self, deployment_resource: DeploymentCardResource):
        kwargs = {
            'deployment_resource': deployment_resource
        }
        message = ActionFromClient("stuff", "unstage_resource", **kwargs)
        self._websocket_service.send_message(message)

    def publish_staged_resources(self):
        message = ActionFromClient("stuff", "publish_staged_resources")
        self._websocket_service.send_message(message)

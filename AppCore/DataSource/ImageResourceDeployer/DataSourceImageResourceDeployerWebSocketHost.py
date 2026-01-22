from typing import List, Optional

from AppCore.Models import DeploymentCardResource
from AppCore.Service.WebSocket.Messages.ActionFromClient import \
    ActionFromClient
from AppCore.Service.WebSocket.Messages.ClientConnectedMessage import \
    ClientConnectedMessage
from AppCore.Service.WebSocket.WebSocketServiceProtocol import (
    WebSocketHostObjectProtocol, WebSocketMessageProtocol,
    WebSocketMessageReceiverProtocol, WebSocketServiceProtocol)

from .DataSourceImageResourceDeployer import DataSourceImageResourceDeployer
from .DataSourceImageResourceDeployerProtocol import \
    DataSourceImageResourceDeployerProtocol
from AppCore.Models import LocalCardResource

class DataSourceImageResourceDeployerWebSocketHost(DataSourceImageResourceDeployerProtocol, WebSocketHostObjectProtocol, WebSocketMessageReceiverProtocol):
    def __init__(self, websocket_service: WebSocketServiceProtocol, data_source_image_resource_deployer: DataSourceImageResourceDeployer):
        self._websocket_service = websocket_service
        self._data_source_image_resource_deployer = data_source_image_resource_deployer

        self._websocket_service.register_as_host(self)

    def handle_new_connection(self) -> WebSocketMessageProtocol:
        return ClientConnectedMessage('stuff', self._data_source_image_resource_deployer)

    def handle_websocket_message(self, message: WebSocketMessageProtocol) -> None:
        if type(message) is ActionFromClient:
            method = getattr(
                self, message.function_name)
            method(**message.kwargs)

    # def __getattr__(self, name):
    #     return getattr(self._data_source_image_resource_deployer, name)

    def _refresh_clients(self):
        self._data_source_image_resource_deployer
        self._websocket_service.send_message(ClientConnectedMessage(
                'stuff', self._data_source_image_resource_deployer))

    @property
    def deployment_resources(self) -> List[DeploymentCardResource]:
        resources = self._data_source_image_resource_deployer.deployment_resources
        return resources

    @property
    def can_publish_staged_resources(self) -> bool:
        return self._data_source_image_resource_deployer.can_publish_staged_resources

    def latest_deployment_resource(self, deployment_resource: DeploymentCardResource) -> Optional[DeploymentCardResource]:
        return self._data_source_image_resource_deployer.latest_deployment_resource(deployment_resource)

    def stage_resource(self, deployment_resource: DeploymentCardResource, selected_resource: LocalCardResource, is_async_store: bool = True):
        self._data_source_image_resource_deployer.stage_resource(deployment_resource, selected_resource, is_async_store)
        self._refresh_clients()
    
    def unstage_resource(self, deployment_resource: DeploymentCardResource):
        self._data_source_image_resource_deployer.unstage_resource(deployment_resource)
        self._refresh_clients()

    def publish_staged_resources(self):
        self._data_source_image_resource_deployer.publish_staged_resources()
        self._refresh_clients()

from AppCore.Service.WebSocket.WebSocketMessageProtocol import WebSocketMessagePayloadType
from ..DataSourceImageResourceDeployerProtocol import (
    DataSourceImageResourceDeployerProtocol,
)
from AppCore.Models import DeploymentCardResource, LocalCardResource

def stage_resource_action(deployment_resource: DeploymentCardResource, selected_resource: LocalCardResource, data_source: DataSourceImageResourceDeployerProtocol):
    data_source.stage_resource(deployment_resource=deployment_resource, selected_resource=selected_resource)

def unstage_resource_action(deployment_resource: DeploymentCardResource, data_source: DataSourceImageResourceDeployerProtocol):
    data_source.unstage_resource(deployment_resource=deployment_resource)

def publish_staged_resources_action(data_source: DataSourceImageResourceDeployerProtocol):
    data_source.publish_staged_resources()

class DataSourceImageResourceDeployerWebSocketMessagePayloadAction(WebSocketMessagePayloadType):
    def __init__(self, partial_action):
        self.partial_action = partial_action
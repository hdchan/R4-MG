
from ..DataSourceImageResourceDeployerProtocol import (
    DataSourceImageResourceDeployerProtocol,
)
from AppCore.Models import DeploymentCardResource, LocalCardResource


class DataSourceImageResourceDeployerWebSocketMessagePartials:
    @staticmethod
    def stage_resource(deployment_resource: DeploymentCardResource,
                       selected_resource: LocalCardResource,
                       data_source: DataSourceImageResourceDeployerProtocol):
        data_source.stage_resource(
            deployment_resource=deployment_resource, selected_resource=selected_resource)

    @staticmethod
    def unstage_resource(deployment_resource: DeploymentCardResource,
                         data_source: DataSourceImageResourceDeployerProtocol):
        data_source.unstage_resource(deployment_resource=deployment_resource)

    @staticmethod
    def publish_staged_resources(data_source: DataSourceImageResourceDeployerProtocol):
        data_source.publish_staged_resources()


from typing import List, Optional

from AppCore.Models import DeploymentCardResource, LocalCardResource
from abc import ABC, abstractmethod

class DataSourceImageResourceDeployerProtocol(ABC):
    @property
    @abstractmethod
    def deployment_resources(self) -> List[DeploymentCardResource]:
        raise NotImplementedError

    @property
    @abstractmethod
    def can_publish_staged_resources(self) -> bool:
        raise NotImplementedError


    def deployment_resource_for_file_name(self, file_name: str) -> Optional[DeploymentCardResource]:
        raise NotImplementedError

    def load_production_resources(self):
        raise NotImplementedError

    @abstractmethod
    def latest_deployment_resource(self, deployment_resource: DeploymentCardResource) -> Optional[DeploymentCardResource]:
        raise NotImplementedError

    @abstractmethod
    def stage_resource(self, deployment_resource: DeploymentCardResource, selected_resource: LocalCardResource):
        raise NotImplementedError

    @abstractmethod
    def unstage_resource(self, deployment_resource: DeploymentCardResource):
        raise NotImplementedError

    def unstage_all_resources(self):
        raise NotImplementedError

    @abstractmethod
    def publish_staged_resources(self):
        raise NotImplementedError

    def generate_new_file(self, file_name: str, placeholder_image_path: Optional[str]):
        raise NotImplementedError

    @property
    def is_publishing(self) -> bool:
        raise NotImplementedError

    def attach_preview_binary_to_prod_resources(self) -> None:
        raise NotImplementedError


class DataSourceImageResourceDeployerProviding:
    @property
    def data_source_image_resource_deployer(self) -> DataSourceImageResourceDeployerProtocol | None:
        raise NotImplementedError

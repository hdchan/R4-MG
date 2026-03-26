from typing import List, Optional

from AppCore.ImageResourceProcessor import (
    ImageResourceProcessorProtocol,
    ImageResourceProcessorProviding,
)
from AppCore.Models import DeploymentCardResource, LocalCardResource
from AppCore.Observation import (
    ObservationTower,
    TransmissionProtocol,
    TransmissionReceiverProtocol,
)
from AppCore.Service.WebSocket.Messages import (
    WebSocketMessagePayloadObservationTowerTransmission
)
from AppCore.Service.WebSocket.WebSocketServiceProtocol import (
    WebSocketClientObjectProtocol,
    WebSocketHostObjectProtocol,
    WebSocketMessageReceiverProtocol,
    WebSocketServiceProtocol,
)

from ..DataSourceImageResourceDeployerProtocol import (
    DataSourceImageResourceDeployerProtocol,
)
from ..Events import (
    DataSourceImageResourceDeployerStateUpdatedEvent,
    ProductionCardResourcesLoadEvent
)
from .DataSourceImageResourceDeployerWebSocketMessage import (
    DataSourceImageResourceDeployerWebSocketMessage,
)


class DataSourceImageResourceDeployerWebSocketHost(DataSourceImageResourceDeployerProtocol,
                                                   WebSocketHostObjectProtocol,
                                                   WebSocketMessageReceiverProtocol,
                                                   TransmissionReceiverProtocol):

    def __init__(self,
                 observation_tower: ObservationTower,
                 websocket_service: WebSocketServiceProtocol,
                 image_resource_processor_provider: ImageResourceProcessorProviding,
                 data_source_image_resource_deployer: DataSourceImageResourceDeployerProtocol):
        self._websocket_service = websocket_service
        self._data_source_image_resource_deployer = data_source_image_resource_deployer
        self._image_resource_processor_provider = image_resource_processor_provider

        self._websocket_service.register_as_host(self)
        self._websocket_service.register_for_messages(
            self, DataSourceImageResourceDeployerWebSocketMessage)
        observation_tower.subscribe_multi(
            self, [DataSourceImageResourceDeployerStateUpdatedEvent, ProductionCardResourcesLoadEvent])

    @property
    def _image_resource_processor(self) -> ImageResourceProcessorProtocol:
        return self._image_resource_processor_provider.image_resource_processor

    # MARK: - DataSourceImageResourceDeployerProtocol
    @property
    def deployment_resources(self) -> List[DeploymentCardResource]:
        resources = self._data_source_image_resource_deployer.deployment_resources
        return resources

    @property
    def can_publish_staged_resources(self) -> bool:
        return self._data_source_image_resource_deployer.can_publish_staged_resources

    def deployment_resource_for_file_name(self, file_name: str) -> Optional[DeploymentCardResource]:
        return self._data_source_image_resource_deployer.deployment_resource_for_file_name(file_name)

    def load_production_resources(self):
        self._data_source_image_resource_deployer.load_production_resources()

    def latest_deployment_resource(self, deployment_resource: DeploymentCardResource) -> Optional[DeploymentCardResource]:
        return self._data_source_image_resource_deployer.latest_deployment_resource(deployment_resource)

    def stage_resource(self, deployment_resource: DeploymentCardResource, selected_resource: LocalCardResource):
        self._data_source_image_resource_deployer.stage_resource(
            deployment_resource, selected_resource)

    def unstage_resource(self, deployment_resource: DeploymentCardResource):
        self._data_source_image_resource_deployer.unstage_resource(
            deployment_resource)

    def publish_staged_resources(self):
        self._data_source_image_resource_deployer.publish_staged_resources()

    def generate_new_file(self, file_name: str, placeholder_image_path: Optional[str]):
        self._data_source_image_resource_deployer.generate_new_file(file_name, placeholder_image_path)

    @property
    def is_publishing(self) -> bool:
        return self._data_source_image_resource_deployer.is_publishing

    def attach_preview_binary_to_prod_resources(self) -> None:
        raise Exception("Not allowed")

    # MARK: - WebSocketHostObjectProtocol
    def wsh_handle_new_connection(self, client_object: WebSocketClientObjectProtocol) -> None:
        self._data_source_image_resource_deployer.attach_preview_binary_to_prod_resources()
        # Send our individual client a message to load and update
        new_connection_events = [
            ProductionCardResourcesLoadEvent(
            ProductionCardResourcesLoadEvent.EventType.FINISHED),
            DataSourceImageResourceDeployerStateUpdatedEvent()
        ]
        for e in new_connection_events:
            message = DataSourceImageResourceDeployerWebSocketMessage(
                data_source=self._data_source_image_resource_deployer,
                payload=WebSocketMessagePayloadObservationTowerTransmission(e))
            client_object.wbc_send_message(message)

    def handle_observation_tower_event(self, event: TransmissionProtocol) -> None:
        # pass all datasource events to client
        # cannot call ds function because we're inside one right now from observation event, when can we attach preview?
        self._data_source_image_resource_deployer.attach_preview_binary_to_prod_resources()
        message = DataSourceImageResourceDeployerWebSocketMessage(
            data_source=self._data_source_image_resource_deployer,
            payload=WebSocketMessagePayloadObservationTowerTransmission(event))
        self._websocket_service.send_websocket_message(message)

from AppCore.DataSource.ImageResourceDeployer import DataSourceImageResourceDeployerProviding, DataSourceImageResourceDeployerProtocol
from AppCore.Observation import ObservationTower, TransmissionProtocol, TransmissionReceiverProtocol
from AppCore.Observation.Events import DraftListUpdatedEvent
from AppCore.Config import ConfigurationManager, Configuration
from AppCore.Models import LocalCardResource

class DataSourceEventCoordinator(TransmissionReceiverProtocol):
    def __init__(self, 
                 observation_tower: ObservationTower,
                 configuration_manager: ConfigurationManager,
                 data_source_image_resource_deployer_provider: DataSourceImageResourceDeployerProviding):
        self._observation_tower = observation_tower
        self._configuration_manager = configuration_manager
        self._data_source_image_resource_deployer_provider = data_source_image_resource_deployer_provider

        self._observation_tower.subscribe_multi(self, [DraftListUpdatedEvent])

    @property
    def _data_source_image_resource_deployer(self) -> DataSourceImageResourceDeployerProtocol:
        return self._data_source_image_resource_deployer_provider.data_source_image_resource_deployer

    @property
    def _configuration(self) -> Configuration:
        return self._configuration_manager.configuration

    def handle_observation_tower_event(self, event: TransmissionProtocol) -> None:
        if type(event) is DraftListUpdatedEvent:
            event_type = event.event_type
            if type(event_type) is DraftListUpdatedEvent.AddedResource:
                self._stage_publish_draft_item_if_needed(event_type.local_resource)
    
    def _stage_publish_draft_item_if_needed(self, selected_resource: LocalCardResource):
        destination_file_name = self._configuration.draft_list_add_card_deployment_destination
        if destination_file_name is None:
            return
        
        matching_deployment_resource = self._data_source_image_resource_deployer.deployment_resource_for_file_name(destination_file_name)
        
        if matching_deployment_resource is None:
            self._reset_deployment_destination_selection()
            return
        add_card_mode = self._configuration.draft_list_add_card_mode
        
        if add_card_mode == Configuration.Settings.DraftListAddCardMode.STAGE or add_card_mode == Configuration.Settings.DraftListAddCardMode.STAGE_AND_PUBLISH:
            self._data_source_image_resource_deployer.stage_resource(matching_deployment_resource, selected_resource, is_async_store=False)
        if add_card_mode == Configuration.Settings.DraftListAddCardMode.STAGE_AND_PUBLISH:
            self._data_source_image_resource_deployer.publish_staged_resources()
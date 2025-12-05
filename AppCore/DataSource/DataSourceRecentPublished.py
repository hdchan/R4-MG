
from AppCore.Config import ConfigurationManager
from AppCore.ImageResource.ImageResourceProcessorProvider import \
    ImageResourceProcessorProviding
from AppCore.Observation import (ObservationTower, TransmissionProtocol,
                                 TransmissionReceiverProtocol)
from AppCore.Observation.Events import PublishStagedCardResourcesEvent
from AppCore.Service import DataSerializer

from .DataSourceCachedHistory import DataSourceCachedHistory


class DataSourceRecentPublished(DataSourceCachedHistory, TransmissionReceiverProtocol):
    def __init__(self, 
                 observation_tower: ObservationTower, 
                 image_resource_processor_provider: ImageResourceProcessorProviding, 
                 configuration_manager: ConfigurationManager, 
                 data_serializer: DataSerializer):
        
        configuration = DataSourceCachedHistory.DataSourceCachedHistoryConfiguration(cache_history_identifier="publish_history")
        super().__init__(observation_tower, 
                         image_resource_processor_provider, 
                         configuration_manager, 
                         data_serializer, 
                         configuration)
        self._observation_tower.subscribe(self, PublishStagedCardResourcesEvent)
    
    def handle_observation_tower_event(self, event: TransmissionProtocol) -> None:
        if type(event) is PublishStagedCardResourcesEvent and event.event_type == PublishStagedCardResourcesEvent.EventType.FINISHED:
            for e in event.deployment_resources:
                if e.staged_resource is not None:
                    self.add_resource(e.staged_resource, event.date_time)
                    # sorted
            self.save_data()
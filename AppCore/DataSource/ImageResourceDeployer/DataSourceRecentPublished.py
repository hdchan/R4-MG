
from datetime import datetime
from typing import List

from AppCore.Config import ConfigurationManager
from AppCore.DataSource.DataSourceCachedHistory import DataSourceCachedHistory
from AppCore.ImageResourceProcessor.ImageResourceProcessorProvider import (
    ImageResourceProcessorProviding,
)
from AppCore.Models.DeploymentCardResource import DeploymentCardResource
from AppCore.Observation import ObservationTower
from AppCore.Service import DataSerializer


class DataSourceRecentPublished(DataSourceCachedHistory):
    def __init__(self,
                 observation_tower: ObservationTower,
                 image_resource_processor_provider: ImageResourceProcessorProviding,
                 configuration_manager: ConfigurationManager,
                 data_serializer: DataSerializer):

        configuration = DataSourceCachedHistory.DataSourceCachedHistoryConfiguration(
            cache_history_identifier="publish_history")
        super().__init__(observation_tower,
                         image_resource_processor_provider,
                         configuration_manager,
                         data_serializer,
                         configuration)

    def save_published_resources(self, deployment_resources: List[DeploymentCardResource]):
        for e in deployment_resources:
            if e.staged_resource is not None:
                self.add_resource(e.staged_resource, datetime.now())
                # sorted
        self.save_data()

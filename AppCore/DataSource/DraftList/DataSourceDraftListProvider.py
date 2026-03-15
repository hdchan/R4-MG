from AppCore.Config import ConfigurationManager
from AppCore.Observation import ObservationTower
from AppCore.Service import DataSerializer

from .DataSourceDraftList import DataSourceDraftList
from .DataSourceDraftListProtocol import (
    DataSourceDraftListProtocol,
    DataSourceDraftListProviding,
)


class DataSourceDraftListProvider(DataSourceDraftListProviding):
    def __init__(self, 
                 configuration_manager: ConfigurationManager,
                 observation_tower: ObservationTower, 
                 data_serializer: DataSerializer):
        self._draft_list_data_source = DataSourceDraftList(configuration_manager,
                                                           observation_tower, 
                                                           data_serializer)

    @property
    def draft_list_data_source(self) -> DataSourceDraftListProtocol:
        return self._draft_list_data_source
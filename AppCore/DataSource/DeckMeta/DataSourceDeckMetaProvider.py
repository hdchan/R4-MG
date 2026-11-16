from AppCore.Config import ConfigurationManager
from AppCore.DataSource.DeckMeta import (
    DataSourceDeckMeta,
    DataSourceDeckMetaClientProtocol,
    DataSourceDeckMetaProtocol,
    DataSourceDeckMetaProviding,
)
from AppCore.Observation import ObservationTower


class DataSourceDeckMetaProvider(DataSourceDeckMetaProviding):
    def __init__(self,
                 configuration_manager: ConfigurationManager,
                 observation_tower: ObservationTower,
                 data_source_deck_meta_client: DataSourceDeckMetaClientProtocol):
        self._data_source_deck_meta_client = data_source_deck_meta_client
        self._data_source_deck_meta = DataSourceDeckMeta(data_source_deck_meta_client)

    @property
    def data_source_deck_meta(self) -> DataSourceDeckMetaProtocol:
        return self._data_source_deck_meta

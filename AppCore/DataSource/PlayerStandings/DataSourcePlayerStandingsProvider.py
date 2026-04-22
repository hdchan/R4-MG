from AppCore.Config import ConfigurationManager
from AppCore.Observation import ObservationTower

from .DataSourcePlayerStandings import DataSourcePlayerStandings
from .DataSourcePlayerStandingsProtocol import (
    DataSourcePlayerStandingsProtocol, DataSourcePlayerStandingsProviding)
from AppCore.DataSource.PlayerStandings.DataSourcePlayerStandingsProtocol import DataSourcePlayerStandingsClientProtocol

class DataSourcePlayerStandingsProvider(DataSourcePlayerStandingsProviding):
    def __init__(self,
                 configuration_manager: ConfigurationManager,
                 observation_tower: ObservationTower, 
                 data_source_client: DataSourcePlayerStandingsClientProtocol):
        self._player_standings_data_source = DataSourcePlayerStandings(configuration_manager,
                                                                       observation_tower, 
                                                                       data_source_client)

    @property
    def data_source_player_standing(self) -> DataSourcePlayerStandingsProtocol:
        return self._player_standings_data_source

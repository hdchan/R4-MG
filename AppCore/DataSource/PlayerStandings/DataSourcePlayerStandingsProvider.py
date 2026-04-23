from AppCore.Config import ConfigurationManager
from AppCore.Observation import ObservationTower

from .DataSourcePlayerStandings import DataSourcePlayerStandings
from .DataSourcePlayerStandingsProtocol import (
    DataSourcePlayerStandingsProtocol, DataSourcePlayerStandingsProviding)


class DataSourcePlayerStandingsProvider(DataSourcePlayerStandingsProviding):
    def __init__(self,
                 configuration_manager: ConfigurationManager,
                 observation_tower: ObservationTower):
        self._player_standings_data_source = DataSourcePlayerStandings(configuration_manager,
                                                                       observation_tower)

    @property
    def data_source_player_standing(self) -> DataSourcePlayerStandingsProtocol:
        return self._player_standings_data_source

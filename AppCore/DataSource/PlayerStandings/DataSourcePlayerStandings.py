
from typing import List, Optional

from PySide6.QtCore import QTimer

from AppCore.Config import ConfigurationManager
from AppCore.Models import PlayerStanding
from AppCore.Observation import ObservationTower

from .DataSourcePlayerStandingsProtocol import (
    DataSourcePlayerStandingsClientProtocol, DataSourcePlayerStandingsProtocol)
from .Events import PlayerStandingsDidUpdate


class DataSourcePlayerStandings(DataSourcePlayerStandingsProtocol):

    def __init__(self,
                 configuration_manager: ConfigurationManager,
                 observation_tower: ObservationTower, 
                 data_source_client: DataSourcePlayerStandingsClientProtocol):
        self._configuration_manager = configuration_manager
        self._observation_tower = observation_tower
        self._data_source_client = data_source_client
        self._standings: List[PlayerStanding] = []

        self._retrieve_standings()

        self.timer = QTimer()
        self.timer.timeout.connect(self._retrieve_standings)
        self.timer.start(5000)

    @property
    def standings(self) -> List[PlayerStanding]:
        return self._standings[:8]

    # TODO: refactor
    @property
    def _player_standings_folder_dir_path(self) -> Optional[str]:
        return self._configuration_manager.configuration.configuration_for_key('player_standings_folder_dir_path')

    def _retrieve_standings(self):
        self._standings = self._data_source_client.retrieve_standings(self._player_standings_folder_dir_path)
        self._observation_tower.notify(PlayerStandingsDidUpdate())

import csv
from pathlib import Path
from typing import List

from AppCore.Config import Configuration, ConfigurationManager
from AppCore.Models import PlayerStanding
from AppCore.Observation import ObservationTower

from .DataSourcePlayerStandingsProtocol import \
    DataSourcePlayerStandingsProtocol
from .Events import PlayerStandingsDidUpdate


class DataSourcePlayerStandings(DataSourcePlayerStandingsProtocol):

    def __init__(self,
                 configuration_manager: ConfigurationManager,
                 observation_tower: ObservationTower):
        self._configuration_manager = configuration_manager
        self._observation_tower = observation_tower
        self._standings: List[PlayerStanding] = []

    @property
    def standings(self) -> List[PlayerStanding]:
        return self._standings

    @property
    def _configuration(self) -> Configuration:
        return self._configuration_manager.configuration

    @property
    def _asset_dir_path(self) -> str:
        return self._configuration.assets_dir_path

    def retrieve_standings(self):
        file_path = Path(
            f'{self._asset_dir_path}standings-export-20260422_022249.csv')
        if file_path.is_file():
            with open(file_path, newline='', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                temp_array: List[PlayerStanding] = []
                for i, row in enumerate(reader):
                    print(row)  # Each row is a list o
                    temp_array.append(PlayerStanding(
                        i + 1, row['TeamPlayers1FirstName']))
                self._standings = temp_array

                self._observation_tower.notify(PlayerStandingsDidUpdate())

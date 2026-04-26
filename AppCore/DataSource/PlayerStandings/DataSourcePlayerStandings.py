import csv
from pathlib import Path
from typing import List

from AppCore.Config import Configuration, ConfigurationManager
from AppCore.Models import PlayerStanding
from AppCore.Observation import ObservationTower

from .DataSourcePlayerStandingsProtocol import \
    DataSourcePlayerStandingsProtocol
from .Events import PlayerStandingsDidUpdate
from PySide6.QtCore import QTimer


class DataSourcePlayerStandings(DataSourcePlayerStandingsProtocol):

    def __init__(self,
                 configuration_manager: ConfigurationManager,
                 observation_tower: ObservationTower):
        self._configuration_manager = configuration_manager
        self._observation_tower = observation_tower
        self._standings: List[PlayerStanding] = []

        self._retrieve_standings()

        self.timer = QTimer()
        self.timer.timeout.connect(self._retrieve_standings)
        self.timer.start(5000)

    @property
    def standings(self) -> List[PlayerStanding]:
        return self._standings

    @property
    def _configuration(self) -> Configuration:
        return self._configuration_manager.configuration

    @property
    def _asset_dir_path(self) -> str:
        return self._configuration.assets_dir_path

    def _retrieve_standings(self):
        file_path = Path(
            f'{self._asset_dir_path}standings-export-20260422_022249.csv')
        if file_path.is_file():
            with open(file_path, newline='', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                temp_array: List[PlayerStanding] = []
                for i, row in enumerate(reader):
                    # print(row)  # Each row is a list o
                    temp_array.append(PlayerStanding(
                        rank=i + 1,
                        first_name=row.get('TeamPlayers1FirstName', ''), 
                        last_name=row.get('TeamPlayers1LastName', ''),
                        deck_name=row.get('Decklists1DecklistName', ''),
                        game_wins=int(row.get('GameWins', '0')),
                        game_loses=int(row.get('GameLoses', '0')),
                        match_wins=int(row.get('MatchWins', '0')),
                        match_loses=int(row.get('MatchLoses', '0')),
                        ogw=float(row.get('OpponentGameWinPercentage', '0')),
                        omw=float(row.get('OpponentMatchWinPercentage', '0')),
                        pgw=float(row.get('TeamGameWinPercentage', '0'))
                        ))
                self._standings = temp_array

                self._observation_tower.notify(PlayerStandingsDidUpdate())

import csv
from pathlib import Path
from typing import List, Optional
import os

from AppCore.DataSource.PlayerStandings.DataSourcePlayerStandingsProtocol import \
    DataSourcePlayerStandingsClientProtocol
from AppCore.Models import PlayerStanding


class DataSourcePlayerStandingsClient(DataSourcePlayerStandingsClientProtocol):
    def __init__(self, swu_app_dependencies_provider):
        self._swu_app_dependencies_provider = swu_app_dependencies_provider

    def retrieve_standings(self, folder_dir_path: Optional[str]) -> List[PlayerStanding]:
        if folder_dir_path is None:
            return []

        # TODO: needs to be able to pick alt file names
        # TODO: needs dynamic top N
        file_list = list(filter(lambda x: x.startswith('standings-export') and x.endswith('.csv'), os.listdir(folder_dir_path)))
        if len(file_list) == 0:
            return []

        sorted_list = sorted(file_list, reverse=True)

        file_path = Path(
            f'{folder_dir_path}/{sorted_list[0]}')
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
                return temp_array
        return []

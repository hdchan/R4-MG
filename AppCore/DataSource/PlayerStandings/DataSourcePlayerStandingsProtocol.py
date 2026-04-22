from typing import List, Optional

from AppCore.Models import PlayerStanding


class DataSourcePlayerStandingsProtocol:
    
    @property
    def standings(self) -> List[PlayerStanding]:
        raise Exception

class DataSourcePlayerStandingsProviding:
    @property
    def data_source_player_standing(self) -> DataSourcePlayerStandingsProtocol:
        raise Exception

class DataSourcePlayerStandingsClientProtocol:
    def retrieve_standings(self, folder_dir_path: Optional[str]) -> List[PlayerStanding]:
        return []
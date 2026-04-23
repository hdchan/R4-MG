from typing import List

from AppCore.Models import PlayerStanding


class DataSourcePlayerStandingsProtocol:
    
    @property
    def standings(self) -> List[PlayerStanding]:
        raise Exception
    
    def retrieve_standings(self) -> None:
        raise Exception

class DataSourcePlayerStandingsProviding:
    @property
    def data_source_player_standing(self) -> DataSourcePlayerStandingsProtocol:
        raise Exception

from typing import List

from AppCore.Models import PlayerStanding


class DataSourcePlayerStandingsProtocol:
    
    @property
    def standings(self) -> List[PlayerStanding]:
        raise Exception

class DataSourcePlayerStandingsProviding:
    @property
    def data_source_player_standing(self) -> DataSourcePlayerStandingsProtocol:
        raise Exception

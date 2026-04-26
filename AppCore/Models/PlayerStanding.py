class PlayerStanding:
    def __init__(self,
                 rank: str,
                 first_name: str, 
                 last_name: str, 
                 deck_name: str, 
                 game_wins: int,
                 game_loses: int, 
                 match_wins: int,
                 match_loses: int, 
                 ogw: float, 
                 omw: float, 
                 pgw: float):
        self.rank = rank
        self.first_name = first_name
        self.last_name = last_name
        self.deck_name = deck_name
        self.game_wins = game_wins
        self.game_loses = game_loses
        self.match_wins = match_wins
        self.match_loses = match_loses
        self.ogw = ogw
        self.omw = omw
        self.pgw = pgw

    def _format_name(self, name):                
        if not name:                
            return ""                
        # Returns first letter + dot if longer than 1
        return name[0] + "." if len(name) > 1 else name

    @property
    def display_details(self) -> str:
        return f'{self.first_name} {self._format_name(self.last_name)} - {self.deck_name}'

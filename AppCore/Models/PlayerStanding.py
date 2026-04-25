class PlayerStanding:
    def __init__(self,
                 rank: str,
                 first_name: str, 
                 last_name: str, 
                 deck_name: str):
        self.rank = rank
        self.first_name = first_name
        self.last_name = last_name
        self.deck_name = deck_name

    @property
    def display_details(self) -> str:
        return f'{self.first_name} {self.last_name} - {self.deck_name}'

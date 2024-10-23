from typing import Optional

class TradingCard:
    def __init__(self,
                 name: str, 
                 set: str, 
                 type: str, 
                 front_art: str, 
                 number: str,
                 double_sided: bool,
                 back_art: Optional[str] = None):
        super().__init__()
        self.name: str = name
        self.set: str = set
        self.type: str = type
        self.number: str = number
        self.double_sided: bool = double_sided
        
        self.front_art: str = front_art
        self.back_art: Optional[str] = back_art
        
    @property
    def is_flippable(self) -> bool:
        return self.double_sided
    
    @property
    def friendly_display_name(self) -> str:
        return f'[{self.set+self.number}] {self.name} - {self.type}'

from typing import Any, Dict, Optional


# Should only be subclassed
class TradingCard:
    def __init__(self,
                 name: str, 
                 set: str, 
                 type: str,
                 number: str,
                 json: Dict[str, Any],
                 metadata: Dict[str, Any] = {}):
        super().__init__()
        self.name: str = name
        self.set: str = set
        self.type: str = type
        self.number: str = number
        self.json = json
        self.metadata = metadata
    
    @property
    def friendly_display_name_short(self) -> str:
        return f'{self.set+self.number}'

    @property
    def friendly_display_name(self) -> str:
        return f'[{self.set+self.number}] {self.name} - {self.type}'
    
    @property
    def friendly_display_name_detailed(self) -> str:
        return f'[{self.set+self.number}] {self.name} - {self.type}'
    
    @property
    def front_art_url(self) -> str:
        return NotImplemented
    
    @property
    def back_art_url(self) -> Optional[str]:
        return NotImplemented
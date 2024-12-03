from typing import Any, Dict


class TradingCard:
    def __init__(self,
                 name: str, 
                 set: str, 
                 type: str,
                 number: str,
                 double_sided: bool,
                 json: Dict[str, Any], 
                 metadata: Dict[str, Any] = {}):
        super().__init__()
        self.name: str = name
        self.set: str = set
        self.type: str = type
        self.number: str = number
        self.double_sided: bool = double_sided
        self.json = json
        self.metadata = metadata
        
    @property
    def is_flippable(self) -> bool:
        return self.double_sided
    
    @property
    def friendly_display_name_short(self) -> str:
        return f'{self.set+self.number}'

    @property
    def friendly_display_name(self) -> str:
        return f'[{self.set+self.number}] {self.name} - {self.type}'
    
    @property
    def friendly_display_name_detailed(self) -> str:
        return f'[{self.set+self.number}] {self.name} - {self.type}'

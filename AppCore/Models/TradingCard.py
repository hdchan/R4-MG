from typing import Dict, Any

class TradingCard:
    def __init__(self,
                 name: str, 
                 set: str, 
                 type: str,
                 number: str,
                 double_sided: bool,
                 json: Dict[str, Any]):
        super().__init__()
        self.name: str = name
        self.set: str = set
        self.type: str = type
        self.number: str = number
        self.double_sided: bool = double_sided
        self.json = json
        
    @property
    def is_flippable(self) -> bool:
        return self.double_sided
    
    @property
    def friendly_display_name(self) -> str:
        return f'[{self.set+self.number}] {self.name} - {self.type}'

from typing import Any, Dict

from AppCore.Models import TradingCard


class CustomTradingCard(TradingCard):
    @classmethod
    def from_name(cls, name: str, file_name: str, path: str):
        obj = cls.__new__(cls)
        metadata: Dict[str, Any] = {}
        metadata['path'] = path
        metadata['file_name'] = file_name
        super(CustomTradingCard, obj).__init__(
            name=name,
            set="no set",
            type='no type',
            number='no number',
            json={},
            metadata=metadata
        )
        return obj
    
    @property
    def friendly_display_name_detailed(self) -> str:
        return self.name
    
    @property
    def front_art_url(self) -> str:
        return f"{self.metadata['path']}{self.metadata['file_name']}"
    
    @property
    def friendly_display_name_short(self) -> str:
        return self.name

    @property
    def friendly_display_name(self) -> str:
        return self.name
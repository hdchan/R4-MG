from typing import Any, Dict

from AppCore.Models.TradingCard import TradingCard
from .CardAspect import CardAspect

class SWUTradingCard(TradingCard):
    @classmethod
    def from_swudb_response(cls, json: Dict[str, Any]):
        obj = cls.__new__(cls)
        metadata: Dict[str, Any] = {}
        if 'Aspects' in json:
            emojis = list(map(lambda x: CardAspect(x).emoji, json['Aspects']))
            metadata['aspect_description_emoji'] = emojis
        super(SWUTradingCard, obj).__init__(
            name=json['Name'],
            set=json['Set'],
            type=json['Type'],
            number=json['Number'],
            double_sided=json['DoubleSided'],
            json=json,
            metadata=metadata
        )
        return obj
    
    @property
    def friendly_display_name_detailed(self) -> str:
        display_name = super().friendly_display_name

        if 'VariantType' in self.json:
            if self.json['VariantType'] == "Hyperspace":
                display_name += ' 💙'
            elif self.json['VariantType'] == "Showcase":
                display_name += ' 💜'

        if 'aspect_description_emoji' in self.metadata:
            emojis = ''.join(self.metadata['aspect_description_emoji'])
            display_name += f' {emojis}'
        
        return display_name
from typing import Any, Dict

from AppCore.Models.TradingCard import TradingCard
from AppCore.Models.CardAspect import CardAspect
from typing import Optional

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
            json=json,
            metadata=metadata
        )
        return obj
    
    @property
    def friendly_display_name_detailed(self) -> str:
        display_name = super().friendly_display_name
        
        if 'VariantType' in self.json:
            variant_type = self.json['VariantType']
            temp_display_name = ''
            if "Hyperspace" in variant_type:
                temp_display_name = '💙'
            elif "Showcase" in variant_type:
                temp_display_name = '💜'
            elif "Prestige" in variant_type:
                temp_display_name = '🖤'
            if "Foil" in variant_type:
                temp_display_name += '⭐'
            display_name += f' {temp_display_name}'

        if 'aspect_description_emoji' in self.metadata:
            emojis = ''.join(self.metadata['aspect_description_emoji'])
            display_name += f' {emojis}'
        
        return display_name
    
    @property
    def front_art_url(self) -> str:
        return self.json['FrontArt']
    
    @property
    def back_art_url(self) -> Optional[str]:
        return self.json.get('BackArt', None)
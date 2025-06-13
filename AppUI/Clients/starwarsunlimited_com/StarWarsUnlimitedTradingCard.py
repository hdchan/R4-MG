from typing import Any, Dict, List, Optional

from AppCore.Models.CardAspect import CardAspect
from AppCore.Models.TradingCard import TradingCard


class StarWarsUnlimitedTradingCard(TradingCard):
    @classmethod
    def from_swudb_response(cls, json: Dict[str, Any]):
        obj = cls.__new__(cls)
        metadata: Dict[str, Any] = {}
        attributes = json['attributes']
        super(StarWarsUnlimitedTradingCard, obj).__init__(
            name=attributes['title'],
            set=attributes['expansion']['data']['attributes']['code'],
            type=attributes['type']['data']['attributes']['value'],
            number=f'{attributes["cardNumber"]:03}',
            json=json,
            metadata=metadata
        )
        return obj
    
    @property
    def friendly_display_name_detailed(self) -> str:
        display_name = self.friendly_display_name
        
        if self.json['attributes']['showcase']:
            display_name += ' 💜'
        elif self.json['attributes']['hyperspace']:
            display_name += ' 💙'
        
        emojisList: List[str] = []
        for a in self.json['attributes']['aspects']['data']:
            emoji = CardAspect(a['attributes']['name']).emoji
            emojisList.append(emoji)
        
        emojis = ''.join(emojisList)
        display_name += f' {emojis}'
        
        return display_name
    
    @property
    def front_art_url(self) -> str:
        return self.json['attributes']['artFront']['data']['attributes']['formats']['card']['url']
    
    @property
    def back_art_url(self) -> Optional[str]:
        back_art = self.json['attributes']['artBack']['data']
        if back_art is None:
            return None
        return back_art['attributes']['formats']['card']['url']
from typing import Any, Dict, List, Optional

from AppCore.Models.TradingCard import TradingCard
import copy
from .CardAspect import CardAspect
from .CardType import CardType
from .CardVariant import CardVariant

class SWUTradingCard(TradingCard):
    def __init__(self,
                 name: str, 
                 set: str, 
                 type: str,
                 number: str,
                 cost: Optional[str],
                 power: Optional[str],
                 hp: Optional[str],
                 json: Dict[str, Any],
                 metadata: Dict[str, Any],
                 aspects: List[str], 
                 subtitle: Optional[str], 
                 front_art_url: str, 
                 back_art_url: Optional[str], 
                 variants: List[str]):
        
        merged_metadata: Dict[str, Any] = copy.deepcopy(metadata)
        merged_metadata['aspects'] = list(map(lambda x: x.lower(), aspects))
        merged_metadata['subtitle'] = subtitle
        merged_metadata['front_art_url'] = front_art_url
        merged_metadata['back_art_url'] = back_art_url
        merged_metadata['variants'] = list(map(lambda x: x.lower(), variants))
        super().__init__(name=name,
                         set=set,
                         type=type,
                         number=number,
                         cost=cost,
                         power=power,
                         hp=hp,
                         json=json, 
                         metadata=merged_metadata)
    
    # def __hash__(self):
    #     return hash((self.name, self.subtitle, self.aspects, self.cost, self.power, self.hp))
    
    # def __eq__(self, other):  # type: ignore
    #     if not isinstance(other, SWUTradingCard):
    #         # don't attempt to compare against unrelated types
    #         return NotImplemented

    #     return self.name == other.name and \
    #         self.subtitle == other.subtitle and \
    #             self.aspects == other.aspects and \
    #                 self.cost == other.cost and \
    #                     self.power == other.power and \
    #                         self.hp == other.hp
    
    @property
    def subtitle(self) -> Optional[str]:
        if 'subtitle' in self.metadata:
            return self.metadata['subtitle']
        return None
        
    @property
    def aspects(self) -> List[CardAspect]:
        aspects = self.metadata['aspects']
        return sorted(list(map(lambda x: CardAspect(x.lower()), aspects)))
    
    @property
    def variants(self) -> List[CardVariant]:
        aspects = self.metadata['variants']
        return sorted(list(map(lambda x: CardVariant(x.lower()), aspects)))
    
    @property
    def card_type(self) -> CardType:
        try:
            return CardType(self.type.lower())
        except:
            return CardType.UNSPECIFIED
        
    @property
    def front_art_url(self) -> str:
        return self.metadata['front_art_url']
    
    @property
    def back_art_url(self) -> Optional[str]:
        return self.metadata['back_art_url']
    
    @property
    def friendly_display_name_detailed(self) -> str:
        variants_string = ''.join(list(map(lambda x: x.emoji, self.variants)))
        aspects_string = ''.join(list(map(lambda x: x.emoji, self.aspects)))
        return f'{self.friendly_display_name} {variants_string} {aspects_string}'
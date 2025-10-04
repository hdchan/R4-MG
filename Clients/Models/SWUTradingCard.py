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
    
    @property
    def subtitle(self) -> Optional[str]:
        if 'subtitle' in self.metadata:
            return self.metadata['subtitle']
        return None
        
    @property
    def aspects(self) -> List[CardAspect]:
        aspects = self.metadata['aspects']
        result: List[CardAspect] = []
        for a in aspects:
            try:
                result.append(CardAspect(a.lower()))
            except:
                continue
        return sorted(result)
    
    @property
    def variants(self) -> List[CardVariant]:
        variants = self.metadata['variants']
        result: List[CardVariant] = []
        for v in variants:
            try:
                result.append(CardVariant(v.lower()))
            except:
                continue
        return sorted(result)
    
    @property
    def variants_string(self) -> str:
        return ''.join(list(map(lambda x: x.emoji, self.variants)))

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
        aspects_string = ''.join(list(map(lambda x: x.emoji, self.aspects)))
        return f'{self.friendly_display_name} {self.variants_string} {aspects_string}'
    
    @property
    def card_cost(self) -> int:
        # assumes that there are no cards with non-numeric costs
        # this is mainly for main deck cards
        try:
            if self.cost is None:
                return 0
            return int(self.cost)
        except:
            return 0
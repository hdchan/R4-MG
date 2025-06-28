from typing import Any, Dict
from AppCore.Models import TradingCard
from ..SWUTradingCard import SWUTradingCard
from typing import Optional, List
class SWUDBTradingCard(SWUTradingCard):
    @classmethod
    def from_trading_card(cls, trading_card: TradingCard) -> 'SWUDBTradingCard':
        return SWUDBTradingCard.from_swudb_response(trading_card.json)
    
    @classmethod
    def from_swudb_response(cls, json: Dict[str, Any]):
        metadata: Dict[str, Any] = {}
        variant_string: Optional[str] = json.get('VariantType')
        variant_string_array: List[str] = []
        if variant_string is not None:
            variant_string_array = variant_string.split()
            
        return cls(
            name=json['Name'],
            set=json['Set'],
            type=json['Type'],
            number=json['Number'],
            cost=json.get("Cost"),
            power=json.get("Power"),
            hp=json.get("HP"),
            json=json,
            metadata=metadata,
            aspects=list(map(lambda x: str(x), json.get('Aspects', []))),
            subtitle=json.get('Subtitle'),
            front_art_url=json['FrontArt'],
            back_art_url=json.get('BackArt', None),
            variants=variant_string_array
        )
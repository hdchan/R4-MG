from .DraftPack import DraftPack
from typing import List, Dict, Any
from .LocalCardResource import LocalCardResource

class DraftDeck:
    def __init__(self, packs: List[DraftPack], sideboard: List[LocalCardResource]):
        self._packs: List[DraftPack] = packs
        self._sideboard: List[LocalCardResource] = sideboard

    class Keys:
        PACKS = 'packs'
        SIDEBOARD = 'sideboard'

    @classmethod
    def default(cls):
        return cls([], [])

    def to_data(self) -> Dict[str, Any]:
        return {
            self.Keys.PACKS: self._packs
        }
    
    # @classmethod
    # def from_json(cls, json: Dict[str, Any]):
    #     obj = cls.__new__(cls)
    #     obj.name = json[TradingCard.Keys.NAME]
    #     obj.set = json[TradingCard.Keys.SET]
    #     obj.type = json[TradingCard.Keys.TYPE]
    #     obj.number = json[TradingCard.Keys.NUMBER]
    #     obj.cost = json.get(TradingCard.Keys.COST, None)
    #     obj.power = json.get(TradingCard.Keys.POWER, None)
    #     obj.hp = json.get(TradingCard.Keys.HP, None)
    #     obj.metadata = json[TradingCard.Keys.METADATA]
    #     obj.json = json.get(TradingCard.Keys.JSON, {})
    #     return obj
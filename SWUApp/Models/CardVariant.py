from enum import Enum
from typing import Dict

class CardVariant(str, Enum):
    HYPERSPACE = 'hyperspace'
    SHOWCASE = 'showcase'
    PRESTIGE = 'prestige'
    SERIALIZED ='serialized'
    FOIL = 'foil'
    NORMAL = 'normal'
    
    @staticmethod
    def _emoji_mapping() -> Dict['CardVariant', str]:
        return {
            CardVariant.HYPERSPACE: "💙",
            CardVariant.SHOWCASE: "💜",
            CardVariant.PRESTIGE: "🖤",
            CardVariant.SERIALIZED: "🔢",
            CardVariant.FOIL: "⭐",
            CardVariant.NORMAL: ""
        }
    
    @property
    def emoji(self) -> str:
        return self._emoji_mapping()[self]
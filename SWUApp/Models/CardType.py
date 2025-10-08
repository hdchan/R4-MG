from enum import Enum
from typing import Dict

class CardType(str, Enum):
    UNSPECIFIED = 'unspecified'
    BASE = 'base'
    EVENT = 'event'
    LEADER = 'leader'
    UNIT = 'unit'
    UPGRADE = 'upgrade'

    @staticmethod
    def _emoji_mapping() -> Dict['CardType', str]:
        return {
            CardType.UNSPECIFIED: "",
            CardType.BASE: "🏰",
            CardType.EVENT: "🗓️",
            CardType.LEADER: "👑",
            CardType.UNIT: "♟️",
            CardType.UPGRADE: "🔧"
        }
    
    @property
    def emoji(self) -> str:
        return self._emoji_mapping()[self]
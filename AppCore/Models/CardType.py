from enum import Enum
from typing import Dict

class CardType(str, Enum):
    UNSPECIFIED = 'Unspecified'
    BASE = 'Base'
    EVENT = 'Event'
    LEADER = 'Leader'
    UNIT = 'Unit'
    UPGRADE = 'Upgrade'
    
    # @staticmethod
    # def _letter_mapping() -> Dict['CardType', str]:
    #     return {
    #         CardType.UNSPECIFIED: "",
    #         CardType.BASE: "B",
    #         CardType.EVENT: "E",
    #         CardType.LEADER: "L",
    #         CardType.UNIT: "Un",
    #         CardType.UPGRADE: "Up"
    #     }
    
    # @property
    # def abbreviation(self) -> str:
    #     return self._letter_mapping()[self]
    
    # def to_data(self) -> str:
    #     return self.value
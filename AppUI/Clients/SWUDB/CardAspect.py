from enum import Enum
from typing import Dict

class CardAspect(str, Enum):
    VIGILANCE = 'Vigilance'
    COMMAND = 'Command'
    AGGRESSION = 'Aggression'
    CUNNING = 'Cunning'
    HEROISM = 'Heroism'
    VILLAINY = 'Villainy'
    
    @staticmethod
    def _emoji_mapping() -> Dict['CardAspect', str]:
        return {
            CardAspect.VIGILANCE: "🔵",
            CardAspect.COMMAND: "🟢",
            CardAspect.AGGRESSION: "🔴",
            CardAspect.CUNNING: "🟡",
            CardAspect.HEROISM: "⚪",
            CardAspect.VILLAINY: "⚫"
        }
    
    @staticmethod
    def _letter_mapping() -> Dict['CardAspect', str]:
        return {
            CardAspect.VIGILANCE: "Vg",
            CardAspect.COMMAND: "Co",
            CardAspect.AGGRESSION: "A",
            CardAspect.CUNNING: "Cu",
            CardAspect.HEROISM: "H",
            CardAspect.VILLAINY: "Vl"
        }
    
    @property
    def emoji(self) -> str:
        return self._emoji_mapping()[self]

    @property
    def abbreviation(self) -> str:
        return self._letter_mapping()[self]
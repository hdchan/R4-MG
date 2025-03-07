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
    
    @property
    def emoji(self) -> str:
        return self._emoji_mapping()[self]
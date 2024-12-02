from enum import Enum
class CardAspect(Enum):
    VIGILANCE = 'Vigilance'
    COMMAND = 'Command'
    AGGRESSION = 'Aggression'
    CUNNING = 'Cunning'
    HEROISM = 'Heroism'
    VILLAINY = 'Villainy'
    
    @property
    def emoji(self) -> str:
        if self == CardAspect.VIGILANCE:
            return '🔵'
        elif self == CardAspect.COMMAND:
            return '🟢'
        elif self == CardAspect.AGGRESSION:
            return '🔴'
        elif self == CardAspect.CUNNING:
            return '🟡'
        elif self == CardAspect.HEROISM:
            return '⚪'
        elif self == CardAspect.VILLAINY:
            return '⚫'
        raise Exception('all cases not accounted for')
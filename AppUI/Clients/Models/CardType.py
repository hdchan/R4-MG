from enum import Enum

class CardType(str, Enum):
    UNSPECIFIED = 'unspecified'
    BASE = 'base'
    EVENT = 'event'
    LEADER = 'leader'
    UNIT = 'unit'
    UPGRADE = 'upgrade'
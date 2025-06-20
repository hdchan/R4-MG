from enum import Enum

# TOOD: needs to be generalized

class CardType(str, Enum):
    UNSPECIFIED = 'Unspecified'
    BASE = 'Base'
    EVENT = 'Event'
    LEADER = 'Leader'
    UNIT = 'Unit'
    UPGRADE = 'Upgrade'
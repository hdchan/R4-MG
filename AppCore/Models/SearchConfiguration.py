from typing import List

from .CardAspect import CardAspect
from .CardType import CardType


class SearchConfiguration:
    def __init__(self):
        self.card_name: str = ""
        self.card_type: CardType = CardType.UNSPECIFIED
        self.card_aspects: List[CardAspect] = []
        
    def __eq__(self, other):  # type: ignore
        if not isinstance(other, SearchConfiguration):
            # don't attempt to compare against unrelated types
            return NotImplemented

        return (self.card_type == other.card_type and 
                self.card_name == other.card_name and 
                self.card_aspects == other.card_aspects)
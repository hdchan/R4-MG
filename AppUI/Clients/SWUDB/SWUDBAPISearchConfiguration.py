from typing import List

from AppCore.Models import SearchConfiguration

from .CardAspect import CardAspect
from .CardType import CardType


class SWUDBAPISearchConfiguration(SearchConfiguration):
    def __init__(self):
        super().__init__()
        self.card_type = CardType.UNSPECIFIED
        self.card_aspects = []
    
    @classmethod
    def from_search_configuration(cls, search_configuration: SearchConfiguration):
        obj = cls.__new__(cls)
        super(SWUDBAPISearchConfiguration, obj).__init__()
        obj.card_name = search_configuration.card_name
        obj.metadata = search_configuration.metadata
        return obj
    
    @property
    def card_type(self) -> CardType:
        return self.metadata['card_type']
    
    @card_type.setter
    def card_type(self, value: CardType):
        self.metadata['card_type'] = value
        
    @property
    def card_aspects(self) -> List[CardAspect]:
        return self.metadata['card_aspects']
    
    @card_aspects.setter
    def card_aspects(self, value: List[CardAspect]):
        self.metadata['card_aspects'] = value
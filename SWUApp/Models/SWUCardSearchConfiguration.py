
from AppCore.Models import SearchConfiguration
from ..Models.CardType import CardType
from typing import Optional

class SWUCardSearchConfiguration(SearchConfiguration):
    def __init__(self):
        super().__init__()
        self.card_type = CardType.UNSPECIFIED
    
    @classmethod
    def from_search_configuration(cls, search_configuration: SearchConfiguration):
        obj = cls.__new__(cls)
        super(SWUCardSearchConfiguration, obj).__init__()
        obj.card_name = search_configuration.card_name
        obj.metadata = search_configuration.metadata
        return obj

    class SWUSearchConfigKeys:
        CARD_TYPE = 'card_type'
        SUBTITLE = 'subtitle'
        CARD_SET = 'card_set'
        CARD_NUMBER = 'card_number'

    @property
    def card_type(self) -> CardType:
        if self.SWUSearchConfigKeys.CARD_TYPE in self.metadata:
            return CardType(self.metadata[self.SWUSearchConfigKeys.CARD_TYPE])
        else:
            return CardType.UNSPECIFIED
    
    @card_type.setter
    def card_type(self, value: CardType):
        self.metadata[self.SWUSearchConfigKeys.CARD_TYPE] = value.value

    @property
    def subtitle(self) -> Optional[str]:
        if self.SWUSearchConfigKeys.SUBTITLE in self.metadata:
            return self.metadata[self.SWUSearchConfigKeys.SUBTITLE]
        return None
    
    @subtitle.setter
    def subtitle(self, value: Optional[str]):
        self.metadata[self.SWUSearchConfigKeys.SUBTITLE] = value

    @property
    def card_set(self) -> Optional[str]:
        if self.SWUSearchConfigKeys.CARD_SET in self.metadata:
            return self.metadata[self.SWUSearchConfigKeys.CARD_SET]
        return None
    
    @card_set.setter
    def card_set(self, value: Optional[str]):
        self.metadata[self.SWUSearchConfigKeys.CARD_SET] = value

    @property
    def card_number(self) -> Optional[str]:
        if self.SWUSearchConfigKeys.CARD_NUMBER in self.metadata:
            return self.metadata[self.SWUSearchConfigKeys.CARD_NUMBER]
        return None
    
    @card_number.setter
    def card_number(self, value: Optional[str]):
        self.metadata[self.SWUSearchConfigKeys.CARD_NUMBER] = value
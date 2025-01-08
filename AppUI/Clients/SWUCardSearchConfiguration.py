
from AppCore.Models import SearchConfiguration
from AppCore.Models.CardType import CardType


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

    @property
    def card_type(self) -> CardType:
        return CardType(self.metadata['card_type'])
    
    @card_type.setter
    def card_type(self, value: CardType):
        self.metadata['card_type'] = value.value
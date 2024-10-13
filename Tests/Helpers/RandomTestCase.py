import random
import string
import unittest
from typing import Optional, TypeVar

from AppCore.Models.TradingCard import TradingCard

T = TypeVar("T")

class RandomTestCase(unittest.TestCase):
    
    def randomAlphaNumericString(self, length: int=random.randrange(1, 100)) -> str:
        return ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(length))
    
    def randomOptional(self, value: T) -> Optional[T]:
        if bool(random.getrandbits(1)):
            return value
        return None
    
    def randomTradingCard(self, 
                          name:Optional[str]=None, 
                          set:Optional[str]=None, type:Optional[str]=None, 
                          front_art:Optional[str]=None, 
                          number:Optional[str]=None, 
                          back_art:Optional[str]=None) -> TradingCard:
        name = name if name is not None else self.randomAlphaNumericString()
        set = set if set is not None else self.randomAlphaNumericString()
        type = type if type is not None else self.randomAlphaNumericString()
        front_art = front_art if front_art is not None else self.randomAlphaNumericString()
        number = number if number is not None else self.randomAlphaNumericString()
        return TradingCard(
            name=name,
            set=set,
            type=type,
            front_art=front_art,
            number=number,
            back_art=back_art
        )
from AppCore.Resource.CardImageSourceProtocol import *
from AppCore.Models import TradingCard
from typing import Optional

class SWUDBImageSource(CardImageSourceProtocol):
    
    @property
    def site_source_url(self) -> str:
        return 'https://www.swudb.com/'
    
    @property
    def site_source_identifier(self) -> str:
        return 'www.swudb.com'
    
    def front_art_url(self, trading_card: TradingCard) -> str:
        return f'https://swudb.com/cards/{trading_card.set}/{trading_card.number}.png'
        
    def back_art_url(self, trading_card: TradingCard) -> Optional[str]:
        return f'https://swudb.com/cards/{trading_card.set}/{trading_card.number}-portrait.png'
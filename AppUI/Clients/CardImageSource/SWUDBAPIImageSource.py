from AppCore.Resource.CardImageSourceProtocol import *
from AppCore.Models import TradingCard
from typing import Optional

class SWUDBAPIImageSource(CardImageSourceProtocol):
    
    def site_source_url(self) -> str:
        return 'https://www.swu-db.com/'
    
    def site_source_identifier(self) -> str:
        return 'www.swu-db.com'
    
    def front_art_url(self, trading_card: TradingCard) -> str:
        return trading_card.json['FrontArt']
        
    def back_art_url(self, trading_card: TradingCard) -> Optional[str]:
        return trading_card.json.get('BackArt', None)
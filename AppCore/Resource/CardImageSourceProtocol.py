from ..Models.TradingCard import TradingCard
from typing import Optional

class CardImageSourceProtocol:
    
    def site_source_url(self) -> str:
        return NotImplemented
    
    def site_source_identifier(self) -> str:
        return NotImplemented
    
    def front_art_url(self, trading_card: TradingCard) -> str:
        return NotImplemented
        
    def back_art_url(self, trading_card: TradingCard) -> Optional[str]:
        return NotImplemented
    
class CardImageSourceProviderProtocol:
    def provideSource(self) -> CardImageSourceProtocol:
        return NotImplemented
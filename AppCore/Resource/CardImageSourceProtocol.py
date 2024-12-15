from typing import Optional

from ..Models.TradingCard import TradingCard


class CardImageSourceProtocol:
    
    @property
    def site_source_url(self) -> str:
        return NotImplemented
    
    @property
    def site_source_identifier(self) -> str:
        return NotImplemented
    
    def front_art_url(self, trading_card: TradingCard) -> str:
        return NotImplemented
        
    def back_art_url(self, trading_card: TradingCard) -> Optional[str]:
        return NotImplemented
    
class CardImageSourceProviding:
    @property
    def card_image_source(self) -> CardImageSourceProtocol:
        return NotImplemented
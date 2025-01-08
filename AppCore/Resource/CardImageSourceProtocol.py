from typing import Optional

from ..Models.TradingCard import TradingCard
from ..Config import ConfigurationManager

class CardImageSourceProtocol:
    @property
    def source_label_display(self) -> str:
        return NotImplemented
    
    def front_art_url(self, trading_card: TradingCard) -> Optional[str]:
        return NotImplemented
        
    def back_art_url(self, trading_card: TradingCard) -> Optional[str]:
        return NotImplemented
    
    @property
    def image_path(self) -> str:
        return NotImplemented
    
    @property
    def image_preview_dir(self) -> str:
        return NotImplemented
    
class RemoteCachedCardImageSourceProtocol(CardImageSourceProtocol):
    
    @property
    def configuration_manager(self) -> ConfigurationManager:
        return NotImplemented
    
    @property
    def site_source_identifier(self) -> str:
        return NotImplemented
    
    @property
    def image_path(self) -> str:
        return f'{self.configuration_manager.configuration.cache_dir_path}{self.site_source_identifier}/'
    
    @property
    def image_preview_dir(self) -> str:
        return f'{self.configuration_manager.configuration.cache_preview_dir_path}{self.site_source_identifier}/'

class LocalCardImageSourceProtocol(CardImageSourceProtocol):
    def front_art_url(self, trading_card: TradingCard) -> Optional[str]:
        return None
        
    def back_art_url(self, trading_card: TradingCard) -> Optional[str]:
        return None
    
class CardImageSourceProviding:
    @property
    def card_image_source(self) -> CardImageSourceProtocol:
        return NotImplemented
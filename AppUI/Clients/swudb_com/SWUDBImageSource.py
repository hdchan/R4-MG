from AppCore.Resource.CardImageSourceProtocol import RemoteCachedCardImageSourceProtocol
from AppCore.Models import TradingCard
from typing import Optional
from AppCore.Config import ConfigurationManager
class SWUDBImageSource(RemoteCachedCardImageSourceProtocol):
    def __init__(self, configuration_manager: ConfigurationManager):
        self._configuration_manager = configuration_manager
        
    @property
    def configuration_manager(self) -> ConfigurationManager:
        return self._configuration_manager
    
    @property
    def _site_source_url(self) -> str:
        return 'https://www.swudb.com/'
    
    @property
    def site_source_identifier(self) -> str:
        return 'www.swudb.com'
    
    @property
    def source_label_display(self) -> str:
        return f'<a href="{self._site_source_url}">{self.site_source_identifier}</a>'
    
    def front_art_url(self, trading_card: TradingCard) -> Optional[str]:
        return f'https://swudb.com/images/cards/{trading_card.set}/{trading_card.number}.png'
        
    def back_art_url(self, trading_card: TradingCard) -> Optional[str]:
        return f'https://swudb.com/images/cards/{trading_card.set}/{trading_card.number}-portrait.png'
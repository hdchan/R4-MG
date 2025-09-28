

from AppCore.Models import  LocalCardResource

from .SWUTradingCard import SWUTradingCard

class SWUTradingCardBackedLocalCardResource(LocalCardResource):
    def __init__(self, 
                 image_dir: str,
                 image_preview_dir: str,
                 file_name: str,
                 display_name: str,
                 display_name_short: str,
                 display_name_detailed: str,
                 remote_image_url: str,
                 trading_card: SWUTradingCard):
        super().__init__(image_dir=image_dir, 
                         image_preview_dir=image_preview_dir, 
                         file_name=file_name, 
                         display_name=display_name, 
                         display_name_short=display_name_short, 
                         display_name_detailed=display_name_detailed, 
                         remote_image_url=remote_image_url, 
                         trading_card=trading_card)
        self._guaranteed_trading_card = trading_card
        
    @property
    def guaranteed_trading_card(self) -> SWUTradingCard:
        return self._guaranteed_trading_card
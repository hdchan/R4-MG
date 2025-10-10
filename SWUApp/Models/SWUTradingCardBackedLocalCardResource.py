

from AppCore.Models import  LocalCardResource

from .SWUTradingCard import SWUTradingCard
from typing import Dict, Any

class SWUTradingCardBackedLocalCardResource(LocalCardResource):
    def __init__(self, 
                 image_dir: str,
                 image_preview_dir: str,
                 file_name: str,
                 display_name: str,
                 display_name_short: str,
                 display_name_detailed: str,
                 remote_image_url: str,
                 trading_card: SWUTradingCard, 
                 metadata: Dict[str, Any]):
        super().__init__(image_dir=image_dir, 
                         image_preview_dir=image_preview_dir, 
                         file_name=file_name, 
                         display_name=display_name, 
                         display_name_short=display_name_short, 
                         display_name_detailed=display_name_detailed, 
                         remote_image_url=remote_image_url, 
                         trading_card=trading_card, 
                         metadata=metadata)
        self._guaranteed_trading_card = trading_card
        
    @property
    def guaranteed_trading_card(self) -> SWUTradingCard:
        return self._guaranteed_trading_card
    
    @property
    def is_sideboard(self) -> bool:
        if 'is_sideboard' in self.metadata:
            return self.metadata['is_sideboard']
        return False
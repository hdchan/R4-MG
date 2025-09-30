from typing import Optional

from AppCore.Models import TradingCard, LocalCardResource

from .starwarsunlimited_com.StarWarsUnlimitedTradingCard import \
    StarWarsUnlimitedTradingCard
from .swu_db_com.SWUDBTradingCard import SWUDBTradingCard
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
        
class SWUTradingCardModelMapper:
    @staticmethod
    def from_card_resource(local_resource: LocalCardResource) -> Optional[SWUTradingCardBackedLocalCardResource]:
        # TODO: maybe we do want to return the resource if remote url is not present? and put a placeholder?
        if local_resource.trading_card is None or local_resource.remote_image_url is None:
            return None
        swu_trading_card = SWUTradingCardModelMapper.from_trading_card(local_resource.trading_card)
        if swu_trading_card is None:
            return
        
        return SWUTradingCardBackedLocalCardResource(
            image_dir=local_resource.image_dir, 
            image_preview_dir=local_resource.image_preview_dir, 
            file_name=local_resource.file_name, 
            display_name=local_resource.display_name, 
            display_name_short=local_resource.display_name_short, 
            display_name_detailed=local_resource.display_name_detailed, 
            remote_image_url=local_resource.remote_image_url, 
            trading_card=swu_trading_card
            )
    @staticmethod
    def from_trading_card(trading_card: TradingCard) -> Optional[SWUTradingCard]:
        try:
            return SWUDBTradingCard.from_trading_card(trading_card)
        except:
            pass
        
        try:
            return StarWarsUnlimitedTradingCard.from_trading_card(trading_card)
        except:
            pass
        
        return None

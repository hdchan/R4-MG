import copy
from typing import Any, Dict, Optional

from AppCore.Models import LocalCardResource, TradingCard

from ..starwarsunlimited_com.StarWarsUnlimitedTradingCard import \
    StarWarsUnlimitedTradingCard
from ..swu_db_com.SWUDBTradingCard import SWUDBTradingCard
from .SWUTradingCard import SWUTradingCard
from .SWUTradingCardBackedLocalCardResource import \
    SWUTradingCardBackedLocalCardResource


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
            trading_card=swu_trading_card,
            metadata=copy.deepcopy(local_resource.metadata) # not sure why this value gets shared
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
    
    @staticmethod
    def from_json_response(json: Dict[str, Any]) -> Optional[SWUTradingCard]:
        try:
            return SWUTradingCardModelMapper.from_trading_card(SWUDBTradingCard.from_swudb_response(json))
        except:
            pass

        try:
            return SWUTradingCardModelMapper.from_trading_card(StarWarsUnlimitedTradingCard.from_swudb_response(json))
        except:
            pass

        return None

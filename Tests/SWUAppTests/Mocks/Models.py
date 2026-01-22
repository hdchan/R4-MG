import string
import random
from typing import Optional
from SWUApp.Models import SWUTradingCard, SWUTradingCardBackedLocalCardResource

class RandomModels:
    
    @staticmethod
    def random_string(size=6, chars=string.ascii_uppercase + string.digits):
        return ''.join(random.choice(chars) for _ in range(size))

    @staticmethod
    def swu_trading_card(type: Optional[str] = None, cost: Optional[str] = None) -> SWUTradingCard:
        return SWUTradingCard(
            name=RandomModels.random_string(),
            set=RandomModels.random_string(),
            type=type if type is not None else RandomModels.random_string(),
            number=RandomModels.random_string(),
            cost=cost,
            power=None,
            hp=None,
            json={},
            metadata={},
            aspects={},
            subtitle=None,
            front_art_url="",
            back_art_url=None,
            variants=[]
        )

    @staticmethod
    def swu_trading_card_backed_local_card_resource(trading_card: Optional[SWUTradingCard] = None) -> SWUTradingCardBackedLocalCardResource:
        return SWUTradingCardBackedLocalCardResource(
            image_dir=RandomModels.random_string(),
            image_preview_dir=RandomModels.random_string(),
            file_name=RandomModels.random_string(),
            display_name=RandomModels.random_string(),
            display_name_short=RandomModels.random_string(),
            display_name_detailed=RandomModels.random_string(),
            remote_image_url=RandomModels.random_string(),
            trading_card=trading_card if trading_card is not None else RandomModels.swu_trading_card(),
            metadata={}
        )
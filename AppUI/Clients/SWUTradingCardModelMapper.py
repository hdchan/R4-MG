from typing import Optional

from AppCore.Models import TradingCard

from .starwarsunlimited_com.StarWarsUnlimitedTradingCard import \
    StarWarsUnlimitedTradingCard
from .swu_db_com.SWUDBTradingCard import SWUDBTradingCard
from .SWUTradingCard import SWUTradingCard


class SWUTradingCardModelMapper:
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
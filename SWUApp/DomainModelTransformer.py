from typing import Any, Dict, Optional

from AppCore.Models import TradingCard, ModelTransformer
from .Models import SWUTradingCardModelMapper

class DomainModelTransformer(ModelTransformer):
    
    def transform_json_to_trading_card(self, json: Dict[str, Any]) -> Optional[TradingCard]:
        return SWUTradingCardModelMapper.from_json_response(json)
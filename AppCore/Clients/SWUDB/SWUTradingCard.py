from typing import Any, Dict

from ...Models.TradingCard import TradingCard


class SWUTradingCard(TradingCard):
    @classmethod
    def from_swudb_response(cls, json: Dict[str, Any]):
        obj = cls.__new__(cls)
        super(SWUTradingCard, obj).__init__(
            name=json['Name'],
            set=json['Set'],
            type=json['Type'],
            number=json['Number'],
            double_sided=json['DoubleSided'],
            json=json
        )
        return obj
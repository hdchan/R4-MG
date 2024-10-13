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
            front_art=json['FrontArt'],
            number=json['Number'],
            back_art=json.get('BackArt', None)
        )
        return obj
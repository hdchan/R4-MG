from typing import Any, Dict, List
from AppCore.Models import TradingCard
from ..SWUTradingCard import SWUTradingCard
class StarWarsUnlimitedTradingCard(SWUTradingCard):
    @classmethod
    def from_trading_card(cls, trading_card: TradingCard) -> 'StarWarsUnlimitedTradingCard':
        return StarWarsUnlimitedTradingCard.from_swudb_response(trading_card.json)

    @classmethod
    def from_swudb_response(cls, json: Dict[str, Any]):
        back_art = json['attributes']['artBack']['data']
        back_art_url = None
        if back_art is not None:
            back_art_url = back_art['attributes']['formats']['card']['url']
        attributes = json['attributes']
        metadata: Dict[str, Any] = {}
        variants: List[str] = []
        if attributes['showcase']:
            variants.append('showcase')
        if attributes['hyperspace']:
            variants.append('hyperspace')
        return cls(
            name=attributes['title'],
            set=attributes['expansion']['data']['attributes']['code'],
            type=attributes['type']['data']['attributes']['value'],
            number=f'{attributes["cardNumber"]:03}',
            cost=str(attributes.get("cost")),
            power=str(attributes.get("power")),
            hp=str(attributes.get("hp")),
            json=json,
            metadata=metadata,
            aspects=list(map(lambda x: str(x['attributes']['name']), json['attributes']['aspects']['data'])),
            subtitle=attributes['subtitle'],
            front_art_url=attributes['artFront']['data']['attributes']['formats']['card']['url'],
            back_art_url=back_art_url,
            variants=variants
        )
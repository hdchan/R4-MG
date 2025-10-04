import copy
from typing import Callable, List, Optional, Set, Dict, Any

from AppCore.Models import DraftPack

from .CardType import CardType
from .SWUTradingCard import SWUTradingCard
from .SWUTradingCardBackedLocalCardResource import \
    SWUTradingCardBackedLocalCardResource
from .SWUTradingCardModelMapper import SWUTradingCardModelMapper


class ParsedDeckList:
    @classmethod
    def from_draft_packs(cls, draft_packs: List[DraftPack]):
        flat_list = [item for pack in draft_packs for item in pack.draft_list]
        
        swu_backed_resources: List[SWUTradingCardBackedLocalCardResource] = []
        for r in flat_list:
            swu_backed_resource = SWUTradingCardModelMapper.from_card_resource(r)
            if swu_backed_resource is None:
                # no_trading_card_resources.append(r)
                continue
            swu_backed_resources.append(swu_backed_resource)
        return cls(swu_backed_resources)
    
    def __init__(self, swu_backed_resources: List[SWUTradingCardBackedLocalCardResource]):
        self._swu_backed_resources = swu_backed_resources
        
    def __hash__(self):
        result = ",".join(list(map(lambda x: x.asset_path, self._swu_backed_resources)))
        return hash(result)
    
    @property
    def has_cards(self) -> bool:
        return len(self._swu_backed_resources) > 0
    
    @property
    def all_cards(self) -> List[SWUTradingCardBackedLocalCardResource]:
        return self._deep_copy_swu_backed_resources
    
    @property
    def first_leader_and_first_base(self) -> List[SWUTradingCardBackedLocalCardResource]:
        result: List[SWUTradingCardBackedLocalCardResource] = []
        leaders = self.leaders
        bases = self.bases
        if len(leaders) > 0:
            result.append(leaders[0])
        if len(bases) > 0:
            result.append(bases[0])
        return result
    
    @property
    def cost_curve_values(self) -> List[int]:
        value_set: Set[int] = set()
        for c in self.all_cards:
            value_set.add(c.guaranteed_trading_card.card_cost)
        return sorted(list(value_set))
    
    @property
    def _deep_copy_swu_backed_resources(self) -> List[SWUTradingCardBackedLocalCardResource]:
        return copy.deepcopy(self._swu_backed_resources)
    
    def _filtered_cards(self, criteria: Callable[[SWUTradingCard], bool]) -> List[SWUTradingCardBackedLocalCardResource]:
        return list(filter(lambda x: criteria(x.guaranteed_trading_card), self._deep_copy_swu_backed_resources))
    
    def _filter_card_with_cost(self, cost: int, input_list: List[SWUTradingCardBackedLocalCardResource]) -> List[SWUTradingCardBackedLocalCardResource]:
        return list(filter(lambda x: x.guaranteed_trading_card.card_cost == cost, input_list))
    
    @property
    def leaders(self) -> List[SWUTradingCardBackedLocalCardResource]:
        return self._filtered_cards(lambda x: x.card_type == CardType.LEADER)
        
    @property
    def bases(self) -> List[SWUTradingCardBackedLocalCardResource]:
        return self._filtered_cards(lambda x: x.card_type == CardType.BASE)
    
    @property
    def main_deck(self) -> List[SWUTradingCardBackedLocalCardResource]:
        return list(filter(lambda x: x.guaranteed_trading_card.card_type != CardType.LEADER and x.guaranteed_trading_card.card_type != CardType.BASE and not x.is_sideboard, self._deep_copy_swu_backed_resources))
    
    @property
    def sideboard(self) -> List[SWUTradingCardBackedLocalCardResource]:
        return list(filter(lambda x: x.guaranteed_trading_card.card_type != CardType.LEADER and x.guaranteed_trading_card.card_type != CardType.BASE and x.is_sideboard, self._deep_copy_swu_backed_resources))
        
    def main_deck_with_cost(self, cost: int) -> List[SWUTradingCardBackedLocalCardResource]:
        return self._filter_card_with_cost(cost, self.main_deck)
    
    def all_units_with_cost(self, cost: int) -> List[SWUTradingCardBackedLocalCardResource]:
        result = list(filter(lambda x: x.guaranteed_trading_card.card_type == CardType.UNIT and not x.is_sideboard, self._deep_copy_swu_backed_resources))
        return self._filter_card_with_cost(cost, result)

    def all_upgrades_and_events_with_cost(self, cost: int) -> List[SWUTradingCardBackedLocalCardResource]:
        result = list(filter(lambda x: (x.guaranteed_trading_card.card_type == CardType.UPGRADE or x.guaranteed_trading_card.card_type == CardType.EVENT) and not x.is_sideboard, self._deep_copy_swu_backed_resources))
        return self._filter_card_with_cost(cost, result)
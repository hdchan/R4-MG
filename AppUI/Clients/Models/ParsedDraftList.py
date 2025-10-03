import copy
from typing import Callable, List, Optional, Set, Dict, Any

from AppCore.Models import DraftPack

from .CardType import CardType
from .SWUTradingCard import SWUTradingCard
from .SWUTradingCardBackedLocalCardResource import \
    SWUTradingCardBackedLocalCardResource
from .SWUTradingCardModelMapper import SWUTradingCardModelMapper


class ParsedDraftList:
    def __init__(self, draft_packs: List[DraftPack]):
        self._draft_packs = draft_packs
        self._flat_list = [item for pack in draft_packs for item in pack.draft_list]
        self._swu_backed_resources: List[SWUTradingCardBackedLocalCardResource] = []
        
        self._stored_values: Dict[str, Any] = {}
        
        for r in self._flat_list:
            swu_backed_resource = SWUTradingCardModelMapper.from_card_resource(r)
            if swu_backed_resource is None:
                # no_trading_card_resources.append(r)
                continue
            self._swu_backed_resources.append(swu_backed_resource)
            
        
    
    def __hash__(self):
        result = ",".join(list(map(lambda x: x.asset_path, self._flat_list)))
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
        for c in self.main_deck:
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
        if 'leaders' not in self._stored_values:
            self._stored_values['leaders'] = self._filtered_cards(lambda x: x.card_type == CardType.LEADER)
        return self._stored_values['leaders']
    
    @property
    def first_leader(self) -> Optional[SWUTradingCardBackedLocalCardResource]:
        if len(self.leaders) > 0:
            return self.leaders[0]
        return None
        
    @property
    def bases(self) -> List[SWUTradingCardBackedLocalCardResource]:
        if 'bases' not in self._stored_values:
            self._stored_values['bases'] = self._filtered_cards(lambda x: x.card_type == CardType.BASE)
        return self._stored_values['bases']
    
    @property
    def first_base(self) -> Optional[SWUTradingCardBackedLocalCardResource]:
        if len(self.bases) > 0:
            return self.bases[0]
        return None
    
    @property
    def main_deck(self) -> List[SWUTradingCardBackedLocalCardResource]:
        if 'main_deck' not in self._stored_values:
            return self._filtered_cards(lambda x: x.card_type != CardType.LEADER and x.card_type != CardType.BASE)
        return self._stored_values['main_deck']
        
    
    def main_deck_with_cost(self, cost: int) -> List[SWUTradingCardBackedLocalCardResource]:
        return self._filter_card_with_cost(cost, self.main_deck)
    
    
    
    # MARK: - units
    @property
    def all_units(self) -> List[SWUTradingCardBackedLocalCardResource]:
        return self._filtered_cards(lambda x: x.card_type == CardType.UNIT)
    
    def all_units_with_cost(self, cost: int) -> List[SWUTradingCardBackedLocalCardResource]:
        return self._filter_card_with_cost(cost, self.all_units)


    def all_upgrades_and_events_with_cost(self, cost: int) -> List[SWUTradingCardBackedLocalCardResource]:
        result = self._filtered_cards(lambda x: x.card_type == CardType.UPGRADE or x.card_type == CardType.EVENT)
        return self._filter_card_with_cost(cost, result)


    # MARK: - upgrades
    @property
    def all_upgrades(self) -> List[SWUTradingCardBackedLocalCardResource]:
        return self._filtered_cards(lambda x: x.card_type == CardType.UPGRADE)
    
    def all_upgrades_with_cost(self, cost: int) -> List[SWUTradingCardBackedLocalCardResource]:
        return self._filter_card_with_cost(cost, self.all_upgrades)

    
    # MARK: - events
    @property
    def all_events(self) -> List[SWUTradingCardBackedLocalCardResource]:
        return self._filtered_cards(lambda x: x.card_type == CardType.EVENT)
    
    def all_events_with_cost(self, cost: int) -> List[SWUTradingCardBackedLocalCardResource]:
        return self._filter_card_with_cost(cost, self.all_events)

import copy
from typing import Callable, List, Set

from AppCore.Models import DraftPack, LocalCardResource

from .CardType import CardType
from .SWUTradingCardBackedLocalCardResource import \
    SWUTradingCardBackedLocalCardResource
from .SWUTradingCardModelMapper import SWUTradingCardModelMapper


class FilterCriteria:
    def __init__(self, criteria: Callable[[SWUTradingCardBackedLocalCardResource], bool]):
        self.criteria = criteria

    @classmethod
    def card_type(cls, card_type: CardType, is_card_type: bool):
        return cls(lambda x: (x.guaranteed_trading_card.card_type == card_type) == is_card_type)

    @classmethod
    def leader(cls, is_leader: bool = True):
        return FilterCriteria.card_type(CardType.LEADER, is_leader)
    
    @classmethod
    def base(cls, is_base: bool = True):
        return FilterCriteria.card_type(CardType.BASE, is_base)
    
    @classmethod
    def sideboard(cls, is_sideboard: bool = True):
        return cls(lambda x: x.is_sideboard == is_sideboard)
    
    @classmethod
    def all_units(cls, is_unit: bool = True):
        return FilterCriteria.card_type(CardType.UNIT, is_unit)
    
    @classmethod
    def all_upgrades_and_events(cls):
        return cls(lambda x: x.guaranteed_trading_card.card_type == CardType.UPGRADE or x.guaranteed_trading_card.card_type == CardType.EVENT)
    
    @classmethod
    def cost(cls, cost: int):
        return cls(lambda x: x.guaranteed_trading_card.card_cost == cost)

class FilterCriteriaBuilder:
    def __init__(self):
        self._criterias: List[FilterCriteria] = []

    def add(self, criteria: FilterCriteria) -> 'FilterCriteriaBuilder':
        self._criterias.append(criteria)
        return self

    def _meets_criteria(self, resource: SWUTradingCardBackedLocalCardResource) -> bool:
        for c in self._criterias:
            if not c.criteria(resource):
                return False
        return True
    
    def filter(self, cards: List[SWUTradingCardBackedLocalCardResource]) -> List[SWUTradingCardBackedLocalCardResource]:
        return list(filter(lambda x: self._meets_criteria(x), cards))

class ParsedDeckList:
    @classmethod
    def from_draft_packs(cls, draft_packs: List[DraftPack]):
        flat_list = [item for pack in draft_packs for item in pack.draft_list]
        return ParsedDeckList.from_local_card_resources(flat_list)

    @classmethod
    def from_local_card_resources(cls, local_card_resources: List[LocalCardResource]):
        swu_backed_resources: List[SWUTradingCardBackedLocalCardResource] = []
        for r in local_card_resources:
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
        return copy.deepcopy(self._swu_backed_resources)
    
    def card_count_main_deck(self, resource: SWUTradingCardBackedLocalCardResource) -> int:
        filtered: List[SWUTradingCardBackedLocalCardResource] = list(filter(lambda x: x == resource, self.main_deck))
        return len(filtered)
    
    def card_count_sideboard(self, resource: SWUTradingCardBackedLocalCardResource) -> int:
        filtered: List[SWUTradingCardBackedLocalCardResource] = list(filter(lambda x: x == resource, self.sideboard))
        return len(filtered)
    
    @property
    def first_leader_and_first_base(self) -> List[SWUTradingCardBackedLocalCardResource]:
        result: List[SWUTradingCardBackedLocalCardResource] = []
        leaders = FilterCriteriaBuilder() \
            .add(FilterCriteria.leader()) \
            .filter(self._swu_backed_resources)
        bases = FilterCriteriaBuilder() \
            .add(FilterCriteria.base()) \
            .filter(self._swu_backed_resources)
        if len(leaders) > 0:
            result.append(leaders[0])
        if len(bases) > 0:
            result.append(bases[0])
        return result
    
    @property
    def main_deck_cost_curve_values(self) -> List[int]:
        value_set: Set[int] = set()
        for c in self.main_deck:
            value_set.add(c.guaranteed_trading_card.card_cost)
        return sorted(list(value_set))
    
    @property
    def sideboard_cost_curve_values(self) -> List[int]:
        value_set: Set[int] = set()
        for c in self.sideboard:
            value_set.add(c.guaranteed_trading_card.card_cost)
        return sorted(list(value_set))
    
    @property
    def main_deck(self) -> List[SWUTradingCardBackedLocalCardResource]:
        return FilterCriteriaBuilder() \
            .add(FilterCriteria.leader(False)) \
            .add(FilterCriteria.base(False)) \
            .add(FilterCriteria.sideboard(False)) \
            .filter(self._swu_backed_resources)
    
    @property
    def sideboard(self) -> List[SWUTradingCardBackedLocalCardResource]:
        return FilterCriteriaBuilder() \
            .add(FilterCriteria.sideboard()) \
            .filter(self._swu_backed_resources)
        
    def main_deck_with_cost(self, cost: int, is_alphabetical: bool = False) -> List[SWUTradingCardBackedLocalCardResource]:
        result = FilterCriteriaBuilder() \
            .add(FilterCriteria.cost(cost)) \
            .filter(self.main_deck)
        if is_alphabetical:
            result = sorted(result, key=lambda x: x.guaranteed_trading_card.name)
        return result
    
    def sideboard_with_cost(self, cost: int, is_alphabetical: bool = False) -> List[SWUTradingCardBackedLocalCardResource]:
        result = FilterCriteriaBuilder() \
            .add(FilterCriteria.sideboard()) \
            .add(FilterCriteria.cost(cost)) \
            .filter(self._swu_backed_resources)
        if is_alphabetical:
            result = sorted(result, key=lambda x: x.guaranteed_trading_card.name)
        return result
    
    def all_cards_excluding_leader_base(self) -> List[SWUTradingCardBackedLocalCardResource]:
        result = list(filter(lambda x: x.guaranteed_trading_card.card_type != CardType.LEADER and x.guaranteed_trading_card.card_type != CardType.BASE, self._swu_backed_resources))
        return result

    def all_main_deck_units_with_cost(self, cost: int, is_alphabetical: bool = False) -> List[SWUTradingCardBackedLocalCardResource]:
        result = FilterCriteriaBuilder() \
            .add(FilterCriteria.all_units()) \
            .add(FilterCriteria.cost(cost)) \
            .filter(self.main_deck)
        if is_alphabetical:
            result = sorted(result, key=lambda x: x.guaranteed_trading_card.name)
        return result

    def all_main_deck_upgrades_and_events_with_cost(self, cost: int, is_alphabetical: bool = False) -> List[SWUTradingCardBackedLocalCardResource]:
        result = FilterCriteriaBuilder() \
            .add(FilterCriteria.leader(False)) \
            .add(FilterCriteria.base(False)) \
            .add(FilterCriteria.all_units(False)) \
            .add(FilterCriteria.cost(cost)) \
            .filter(self.main_deck)
        if is_alphabetical:
            result = sorted(result, key=lambda x: x.guaranteed_trading_card.name)
        return result
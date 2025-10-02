import copy
from typing import List

from AppCore.Models import DraftPack, LocalCardResource

from ..Models.CardType import CardType
from ..Models.SWUTradingCardModelMapper import (
    SWUTradingCardBackedLocalCardResource, SWUTradingCardModelMapper)


class ParsedDraftList:
    def __init__(self, draft_packs: List[DraftPack]):
        self._draft_packs = draft_packs
        
        flat_list = [item for pack in draft_packs for item in pack.draft_list]
        
        non_empty_trading_cards: List[SWUTradingCardBackedLocalCardResource] = []
        no_trading_card_resources: List[LocalCardResource] = [] # send warning?
        
        self._leaders: List[SWUTradingCardBackedLocalCardResource] = []
        self._bases: List[SWUTradingCardBackedLocalCardResource] = []
        self._main_deck: List[SWUTradingCardBackedLocalCardResource] = []
        
        for r in flat_list:
            swu_backed_resource = SWUTradingCardModelMapper.from_card_resource(r)
            if swu_backed_resource is None:
                no_trading_card_resources.append(r)
                continue
            
            non_empty_trading_cards.append(swu_backed_resource)
            
            if swu_backed_resource.guaranteed_trading_card.card_type == CardType.LEADER:
                self._leaders.append(swu_backed_resource)
            elif swu_backed_resource.guaranteed_trading_card.card_type == CardType.BASE:
                self._bases.append(swu_backed_resource)
            else:
                self._main_deck.append(swu_backed_resource)
                
    @property
    def leaders(self) -> List[SWUTradingCardBackedLocalCardResource]:
        return copy.deepcopy(self._leaders)
    
    @property
    def bases(self) -> List[SWUTradingCardBackedLocalCardResource]:
        return copy.deepcopy(self._bases)
    
    @property
    def main_deck(self) -> List[SWUTradingCardBackedLocalCardResource]:
        return copy.deepcopy(self._main_deck)
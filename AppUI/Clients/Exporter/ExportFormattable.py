import csv
import json
from typing import Any, Dict, List

from AppCore.Models import DraftPack

from ..CardAspect import CardAspect
from ..SWUTradingCardModelMapper import (SWUTradingCardBackedLocalCardResource,
                                         SWUTradingCardModelMapper)


class ExportFormattable:
    @property
    def file_format(self) -> str:
        raise Exception
    
    @property
    def format_name(self) -> str:
        raise Exception
    
    def export(self,
               file_path: str,
               raw_draft_packs: List[DraftPack], 
               selected_leader: SWUTradingCardBackedLocalCardResource, 
               selected_base: SWUTradingCardBackedLocalCardResource, 
               main_deck: List[SWUTradingCardBackedLocalCardResource], 
               side_board: List[SWUTradingCardBackedLocalCardResource]) -> None:
        raise Exception
    
class MGGExporter(ExportFormattable):
    @property
    def file_format(self) -> str:
        return "Melee.gg (*.txt)"
    
    @property
    def format_name(self) -> str:
        return "Melee.gg"
    
    def export(self, 
               file_path: str,
               raw_draft_packs: List[DraftPack], 
               selected_leader: SWUTradingCardBackedLocalCardResource, 
               selected_base: SWUTradingCardBackedLocalCardResource, 
               main_deck: List[SWUTradingCardBackedLocalCardResource], 
               side_board: List[SWUTradingCardBackedLocalCardResource]) -> None:
            def aggregate(card_list: List[SWUTradingCardBackedLocalCardResource]) -> List[str]:
                deck_counter: Dict[str, int] = {}
                for m in card_list:
                    hash_array: List[str] = [m.guaranteed_trading_card.name]
                    if m.guaranteed_trading_card.subtitle is not None:
                        hash_array.append(m.guaranteed_trading_card.subtitle)
                    hash = " | ".join(hash_array)
                    
                    if hash not in deck_counter:
                        deck_counter[hash] = 0
                    deck_counter[hash] += 1
                
                deck_result: List[str] = []
                for m in deck_counter.keys():
                    deck_result.append(f'{deck_counter[m]} {m}\n')
                return deck_result
                
            result: List[str] = [
                "Leader\n",
                f"1 {selected_leader.guaranteed_trading_card.name} | {selected_leader.guaranteed_trading_card.subtitle}\n",
                "\n",
                "Base\n",
                f"1 {selected_base.guaranteed_trading_card.name}\n", # no subtitle
                "\n",
                "MainDeck\n"] + aggregate(main_deck) + [
                "\n",
                "Sideboard\n"] + aggregate(side_board) + [
            ]
            
            with open(f'{file_path}', 'w') as f:
                for r in result:
                    f.write(r)
    
class SWUDBDotCOMExporter(ExportFormattable):
    @property
    def file_format(self) -> str:
        return "swudb.com (*.json)"
    
    @property
    def format_name(self) -> str:
        return "swudb.com"
    
    def export(self, 
               file_path: str,
               raw_draft_packs: List[DraftPack], 
               selected_leader: SWUTradingCardBackedLocalCardResource, 
               selected_base: SWUTradingCardBackedLocalCardResource, 
               main_deck: List[SWUTradingCardBackedLocalCardResource], 
               side_board: List[SWUTradingCardBackedLocalCardResource]) -> None:
        def aggregate(card_list: List[SWUTradingCardBackedLocalCardResource]) -> List[Dict[str, Any]]:
            deck_counter: Dict[str, int] = {}
            for m in card_list:
                hash = f'{m.guaranteed_trading_card.set}_{m.guaranteed_trading_card.number}'
                if hash not in deck_counter:
                    deck_counter[hash] = 0
                    
                deck_counter[hash] += 1
            
            deck_result: List[Dict[str, Any]] = []
            for m in deck_counter.keys():
                deck_result.append({
                    "id": m,
                    "count": deck_counter[m]
                })
            return deck_result
            
        result: Dict[str, Any] = {
            "leader": {
                "id": f'{selected_leader.guaranteed_trading_card.set}_{selected_leader.guaranteed_trading_card.number}',
                "count": 1
            },
            "base": {
                "id": f'{selected_base.guaranteed_trading_card.set}_{selected_base.guaranteed_trading_card.number}',
                "count": 1
            },
            "deck": aggregate(main_deck),
            "sideboard": aggregate(side_board)
        }
        
        with open(f'{file_path}', 'w') as f:
            f.write(json.dumps(result, indent=4))
        
class CSVExporter(ExportFormattable):
    @property
    def file_format(self) -> str:
        return "CSV (*.csv)"
    
    @property
    def format_name(self) -> str:
        return "csv"
    
    def export(self, 
               file_path: str,
               raw_draft_packs: List[DraftPack], 
               selected_leader: SWUTradingCardBackedLocalCardResource, 
               selected_base: SWUTradingCardBackedLocalCardResource, 
               main_deck: List[SWUTradingCardBackedLocalCardResource], 
               side_board: List[SWUTradingCardBackedLocalCardResource]) -> None:
        # flat_list = [item for pack in draft_packs for item in pack.draft_list]
        aspects = [member.value for member in CardAspect]
        data: List[List[str]] = [
            [
                "original_order",
                "draft_pack",
                "set",
                "identifier",
                "name", 
                "subtitle",
                "type",
                "cost",
                "power",
                "hp"
                ] + aspects
            ]
        counter = 0
        for p in raw_draft_packs:
            for r in p.draft_list:
                t = r.trading_card
                if t is not None:
                    swu_t = SWUTradingCardModelMapper.from_trading_card(t)
                    if swu_t is None:
                        continue
                    card_aspects = swu_t.aspects
                    counter += 1
                    more_data: List[str] = [
                        counter,
                        p.pack_name,
                        swu_t.set,
                        swu_t.set+swu_t.number,
                        swu_t.name, 
                        swu_t.subtitle,
                        swu_t.card_type,
                        swu_t.cost,
                        swu_t.power,
                        swu_t.hp,
                        ] + [member.value in card_aspects for member in CardAspect]
                    data.append(more_data)
        
        with open(f'{file_path}', 'w', newline='') as csv_file:
            csv_writer = csv.writer(csv_file)
            csv_writer.writerows(data)
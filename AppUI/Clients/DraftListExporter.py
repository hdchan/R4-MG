
import csv
import json
from typing import Dict, List

from PyQt5.QtWidgets import (QDialog, QFileDialog)

from AppCore.DataFetcher import *
from AppCore.Models import DraftPack, LocalCardResource

from .CardAspect import CardAspect
from .DraftListExporterDialog import DraftListExporterDialog
from .CardType import CardType
from .SWUTradingCardModelMapper import SWUTradingCardModelMapper, SWUTradingCardBackedLocalCardResource

class DraftListExporter:
    def export_draft_list(self, draft_packs: List[DraftPack], to_path: str, swu_db: bool):
        # takes only first leader and base
        flat_list = [item for pack in draft_packs for item in pack.draft_list]
        
        non_empty_trading_cards: List[SWUTradingCardBackedLocalCardResource] = []
        no_trading_card_resources: List[LocalCardResource] = []
        
        leaders: List[SWUTradingCardBackedLocalCardResource] = []
        bases: List[SWUTradingCardBackedLocalCardResource] = []
        main_deck: List[SWUTradingCardBackedLocalCardResource] = []
        
        for r in flat_list:
            swu_backed_resource = SWUTradingCardModelMapper.from_card_resource(r)
            if swu_backed_resource is None:
                no_trading_card_resources.append(r)
                continue
            
            non_empty_trading_cards.append(swu_backed_resource)
            
            if swu_backed_resource.guaranteed_trading_card.card_type == CardType.LEADER:
                leaders.append(swu_backed_resource)
            elif swu_backed_resource.guaranteed_trading_card.card_type == CardType.BASE:
                bases.append(swu_backed_resource)
            else:
                main_deck.append(swu_backed_resource)
        
        if len(leaders) == 0:
            raise Exception("No leader card")
        if len(bases) == 0:
            raise Exception("No base card")
        
        export_formats = ["swudb.com", "Melee.gg"]
        file_formats = ["swudb.com (*.json)", "Melee.gg (*.txt)"]
        card_selector = DraftListExporterDialog(leaders, 
                                                bases, 
                                                main_deck, 
                                                export_formats)
        result = card_selector.exec()
        if result == QDialog.DialogCode.Rejected:
            return 
        selected_leader = card_selector.selected_leader
        selected_base = card_selector.selected_base
        main_deck = card_selector.main_deck
        side_board = card_selector.side_board
        selected_format_index = card_selector.export_format_index
        
        file_name, ok = QFileDialog.getSaveFileName(None, "Save File", "", f"{file_formats[selected_format_index]};;All Files (*)")
        
        if not ok:
            return
        
        def export_to_mgg():
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
            
            with open(f'{file_name}', 'w') as f:
                for r in result:
                    f.write(r)
        
        def export_to_swudb():
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
            
            with open(f'{file_name}', 'w') as f:
                f.write(json.dumps(result, indent=4))
        
        if export_formats[selected_format_index] == "swudb.com":
            export_to_swudb()
        elif export_formats[selected_format_index] ==  "Melee.gg":
            export_to_mgg()
            
    def export_draft_list_csv(self, draft_packs: List[DraftPack], to_path: str):
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
        for p in draft_packs:
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
        
        with open(f'{to_path}your_file_csv.csv', 'w', newline='') as csv_file:
            csv_writer = csv.writer(csv_file)
            csv_writer.writerows(data)
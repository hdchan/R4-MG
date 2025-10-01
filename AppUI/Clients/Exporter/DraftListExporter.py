
from typing import List

from PyQt5.QtWidgets import QDialog, QFileDialog

from AppCore.DataFetcher import *
from AppCore.Models import DraftPack, LocalCardResource

from ..CardType import CardType
from ..DraftListExporterDialog import DraftListExporterDialog
from ..SWUTradingCardModelMapper import (SWUTradingCardBackedLocalCardResource,
                                         SWUTradingCardModelMapper)
from .ExportFormattable import (CSVExporter, ExportFormattable, MGGExporter,
                                SWUDBDotCOMExporter, VisualizedCardsExporter)


class DraftListExporter:
    def export_draft_list(self, draft_packs: List[DraftPack], to_path: str, swu_db: bool):
        # takes only first leader and base
        flat_list = [item for pack in draft_packs for item in pack.draft_list]
        
        non_empty_trading_cards: List[SWUTradingCardBackedLocalCardResource] = []
        no_trading_card_resources: List[LocalCardResource] = [] # send warning?
        
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
        
        exporters: List[ExportFormattable] = [
            SWUDBDotCOMExporter(), 
            MGGExporter(), 
            CSVExporter(),
            VisualizedCardsExporter()
            ]
        
        card_selector = DraftListExporterDialog(leaders, 
                                                bases, 
                                                main_deck,
                                                exporters)
        result = card_selector.exec()
        if result == QDialog.DialogCode.Rejected:
            return 
        selected_leader = card_selector.selected_leader
        selected_base = card_selector.selected_base
        main_deck = card_selector.main_deck
        side_board = card_selector.side_board
        selected_exporter = card_selector.selected_exporter
        
        file_path, ok = QFileDialog.getSaveFileName(None, "Save File", "", f"{selected_exporter.file_format};;All Files (*)")
        
        if not ok:
            return
        
        selected_exporter.export(file_path=file_path, 
                                 raw_draft_packs=draft_packs, 
                                 selected_leader=selected_leader, 
                                 selected_base=selected_base, 
                                 main_deck=main_deck, 
                                 side_board=side_board)

from typing import List

from PyQt5.QtWidgets import QDialog, QFileDialog

from AppCore.DataFetcher import *
from AppCore.Models import DraftPack

from ..Models.ParsedDeckList import ParsedDeckList
from ..UIComponents.DraftListExporterDialog import DraftListExporterDialog
from .ExportFormattable import (CSVExporter, ExportFormattable, MGGExporter,
                                SWUDBDotCOMExporter)


class DraftListExporter:
    def export_draft_list(self, draft_packs: List[DraftPack], to_path: str, swu_db: bool):
        parsed_deck_list = ParsedDeckList.from_draft_packs(draft_packs)
        
        leaders = parsed_deck_list.leaders
        bases = parsed_deck_list.bases
        main_deck = parsed_deck_list.main_deck
        
        if len(leaders) == 0:
            raise Exception("No leader card")
        if len(bases) == 0:
            raise Exception("No base card")
        
        exporters: List[ExportFormattable] = [
            SWUDBDotCOMExporter(), 
            MGGExporter(), 
            CSVExporter(),
            # VisualizedCardsExporter()
            ]
        
        card_selector = DraftListExporterDialog(leaders, 
                                                bases, 
                                                main_deck,
                                                exporters)
        result = card_selector.exec()
        if result == QDialog.DialogCode.Rejected:
            return 
        selected_leader, selected_base = parsed_deck_list.first_leader_and_first_base
        main_deck = parsed_deck_list.main_deck
        sideboard = parsed_deck_list.sideboard
        selected_exporter = card_selector.selected_exporter
        
        file_path, ok = QFileDialog.getSaveFileName(None, 
                                                    "Save File", 
                                                    "", 
                                                    f"{selected_exporter.file_format};;All Files (*)")
        
        if not ok:
            return
        
        selected_exporter.export(file_path=file_path, 
                                 raw_draft_packs=draft_packs, 
                                 selected_leader=selected_leader, 
                                 selected_base=selected_base, 
                                 main_deck=main_deck, 
                                 sideboard=sideboard)
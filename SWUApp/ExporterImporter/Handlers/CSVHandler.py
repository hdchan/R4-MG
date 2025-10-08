import csv
from typing import List

from AppCore.Models import DraftPack

from ...Models import (SWUTradingCardBackedLocalCardResource,
                       SWUTradingCardModelMapper)
from ...Models.CardAspect import CardAspect
from ...SWUAppDependenciesProviding import SWUAppDependenciesProviding
from ..ExportImportFormattable import ExportFormattable, Importable


class CSVHandler(ExportFormattable, Importable):
    def __init__(self, 
                 swu_app_dependencies_provider: SWUAppDependenciesProviding):
        self._swu_app_dependencies_provider = swu_app_dependencies_provider

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
               sideboard: List[SWUTradingCardBackedLocalCardResource]) -> None:
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

from typing import List

from PyQt5.QtWidgets import QDialog

from R4UI import (BoldLabel, ComboBox,
                    HorizontalBoxLayout, R4UIHorizontallyExpandingSpacer,
                    PushButton, VerticalBoxLayout)

from ..Exporter.ExportFormattable import ExportFormattable
from ..Models import SWUTradingCardBackedLocalCardResource

# T = TypeVar("T")

# class CellObject(Generic[T]):
#     def __init__(self, o: T):
#         self._o: T = o
#         self._is_checked = False
        
#         def _checked(checked: bool):
#             self._is_checked = checked
        
#         self._check_box = R4UICheckBox(_checked)
    
#     @property
#     def check_box(self) -> R4UICheckBox:
#         return self._check_box
    
#     @property
#     def is_checked(self) -> bool:
#         return self._is_checked
    
#     @property
#     def object(self) -> T:
#         return self._o

class DraftListExporterDialog(QDialog):
        def __init__(self, 
                     leaders: List[SWUTradingCardBackedLocalCardResource],
                     bases: List[SWUTradingCardBackedLocalCardResource], 
                     all_other_cards: List[SWUTradingCardBackedLocalCardResource],
                     exporters: List[ExportFormattable]):
            super().__init__()
            self._selected_leader: SWUTradingCardBackedLocalCardResource = leaders[0]
            self._selected_base: SWUTradingCardBackedLocalCardResource = bases[0]
            self._exporters = exporters
            
            self._accept_button = PushButton("Export", self.accept)
           
            
            self._export_format = ComboBox(list(map(lambda x: x.format_name, self._exporters)))
            
            VerticalBoxLayout([
                HorizontalBoxLayout([
                    BoldLabel("Format"),
                    self._export_format
                ]).add_spacer(R4UIHorizontallyExpandingSpacer()),
                HorizontalBoxLayout([
                    PushButton("Cancel", self.reject),
                    self._accept_button
                ])
            ]).set_layout_to_widget(self)
        
        @property
        def _export_format_index(self) -> int:
            return self._export_format.currentIndex()
        
        @property
        def selected_leader(self) -> SWUTradingCardBackedLocalCardResource:
            return self._selected_leader
        
        @property
        def selected_base(self) -> SWUTradingCardBackedLocalCardResource:
            return self._selected_base
        
        @property
        def selected_exporter(self) -> ExportFormattable:
            return self._exporters[self._export_format_index]
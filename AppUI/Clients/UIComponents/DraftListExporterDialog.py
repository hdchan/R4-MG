from typing import Callable, Generic, List, TypeVar

from PyQt5.QtWidgets import QDialog, QSizePolicy

from R4UI import (BoldLabel, ButtonGroup, CheckBox, ComboBox,
                    HorizontalBoxLayout, R4UIHorizontallyExpandingSpacer, Label,
                    PushButton, ScrollArea, VerticalBoxLayout,
                    VerticalGroupBox, R4UIVerticallyExpandingSpacer)

from ..Exporter.ExportFormattable import ExportFormattable
from ..Models import SWUTradingCardBackedLocalCardResource

T = TypeVar("T")

class CellObject(Generic[T]):
    def __init__(self, o: T):
        self._o: T = o
        self._is_checked = False
        
        def _checked(checked: bool):
            self._is_checked = checked
        
        self._check_box = CheckBox(_checked)
    
    @property
    def check_box(self) -> CheckBox:
        return self._check_box
    
    @property
    def is_checked(self) -> bool:
        return self._is_checked
    
    @property
    def object(self) -> T:
        return self._o

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
            
            def _selected_leader(value: SWUTradingCardBackedLocalCardResource) -> None:
                self._selected_leader = value
                self._sync_ui()
                
            def _selected_base(value: SWUTradingCardBackedLocalCardResource) -> None:
                self._selected_base = value
                self._sync_ui()
            
            self._main_card_objects = list(map(lambda x: CellObject[SWUTradingCardBackedLocalCardResource](x), all_other_cards))
            
            self._accept_button = PushButton("Export", self.accept)
            self._all_other_cards_list = VerticalBoxLayout()
            self._all_other_cards_list.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)
            for a in self._main_card_objects:
                cell = HorizontalBoxLayout([
                    a.check_box,
                    Label(a.object.guaranteed_trading_card.name),
                    
                ]).add_spacer(R4UIHorizontallyExpandingSpacer())
                self._all_other_cards_list.add_widget(cell)
                
            self._all_other_cards_list.add_spacer(R4UIVerticallyExpandingSpacer())
            
            self._export_format = ComboBox(list(map(lambda x: x.format_name, self._exporters)))
            
            VerticalBoxLayout([
                HorizontalBoxLayout([
                    
                    VerticalBoxLayout([
                        Label(leaders[0].guaranteed_trading_card.name),
                        Label(bases[0].guaranteed_trading_card.name),
                        # VerticalGroupBox([
                        #     BoldLabel("Select Leader"),
                        #     self._button_group(leaders, _selected_leader),
                        #     ]).set_alignment_top().add_spacer(R4UIVerticallyExpandingSpacer()),
                        # VerticalGroupBox([
                        #     BoldLabel("Select Base"),
                        #     self._button_group(bases, _selected_base),
                        #     ]).set_alignment_top().add_spacer(R4UIVerticallyExpandingSpacer()),
                        ]),
                    VerticalBoxLayout([
                        BoldLabel("Selected side-board cards"),
                        Label("Unselected cards will be a part of the main deck"),
                        ScrollArea(self._all_other_cards_list)
                    ])
                    ]),
                HorizontalBoxLayout([
                    BoldLabel("Format"),
                    self._export_format
                ]).add_spacer(R4UIHorizontallyExpandingSpacer()),
                HorizontalBoxLayout([
                    PushButton("Cancel", self.reject),
                    self._accept_button
                ])
            ]).set_layout_to_widget(self)
            
            self._sync_ui()
        
        def _button_group(self, cards: List[SWUTradingCardBackedLocalCardResource], selected_fn: Callable[[SWUTradingCardBackedLocalCardResource], None]) -> ButtonGroup:
            button_group_values: List[tuple[str, SWUTradingCardBackedLocalCardResource]] = []
            button_group_values = list(map(lambda x: (x.guaranteed_trading_card.name, x), cards))
            
            button_group = ButtonGroup(button_group_values, selected_fn)
            button_group.set_checked(0)
            return button_group
        
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
        
        @property
        def main_deck(self) -> List[SWUTradingCardBackedLocalCardResource]:
            filtered = list(filter(lambda x: x.is_checked == False, self._main_card_objects))
            return list(map(lambda x: x.object, filtered))
        
        @property
        def side_board(self) -> List[SWUTradingCardBackedLocalCardResource]:
            filtered = list(filter(lambda x: x.is_checked == True, self._main_card_objects))
            return list(map(lambda x: x.object, filtered))
        
        def _sync_ui(self):
            pass
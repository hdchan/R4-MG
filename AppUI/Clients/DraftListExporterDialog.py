from typing import List, Callable

from PyQt5.QtWidgets import QDialog, QSizePolicy

from PyQtUI import (HorizontalBoxLayout, PushButton,
                    VerticalBoxLayout, VerticalGroupBox, ButtonGroup, BoldLabel, ScrollArea, VerticallyExpandingSpacer, Label, CheckBox, HorizontallyExpandingSpacer, ComboBox)

from .SWUTradingCard import SWUTradingCard

class CellObject:
    def __init__(self, trading_card: SWUTradingCard):
        self._trading_card = trading_card
        self._is_sideboard = False
        
        def _checked(checked: bool):
            self._is_sideboard = checked
        
        self._check_box = CheckBox(_checked)
    
    @property
    def check_box(self) -> CheckBox:
        return self._check_box
    
    @property
    def is_sideboard(self) -> bool:
        return self._is_sideboard
    
    @property
    def trading_card(self) -> SWUTradingCard:
        return self._trading_card

class DraftListExporterDialog(QDialog):
        def __init__(self, 
                     leaders: List[SWUTradingCard],
                     bases: List[SWUTradingCard], 
                     all_other_cards: List[SWUTradingCard], 
                     export_formats: List[str]):
            super().__init__()
            self._selected_leader: SWUTradingCard = leaders[0]
            self._selected_base: SWUTradingCard = bases[0]
            
            def _selected_leader(value: SWUTradingCard) -> None:
                self._selected_leader = value
                self._sync_ui()
                
            def _selected_base(value: SWUTradingCard) -> None:
                self._selected_base = value
                self._sync_ui()
            
            self._main_card_objects = list(map(lambda x: CellObject(x), all_other_cards))
            
            self._accept_button = PushButton("Export", self.accept)
            self._all_other_cards_list = VerticalBoxLayout()
            self._all_other_cards_list.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)
            for a in self._main_card_objects:
                cell = HorizontalBoxLayout([
                    a.check_box,
                    Label(a.trading_card.name),
                    
                ]).add_spacer(HorizontallyExpandingSpacer())
                self._all_other_cards_list.add_widget(cell)
            self._all_other_cards_list.add_spacer(VerticallyExpandingSpacer())
            
            self._export_format = ComboBox(export_formats)
            
            VerticalBoxLayout([
                HorizontalBoxLayout([
                    VerticalBoxLayout([
                        VerticalGroupBox([
                            BoldLabel("Select Leader"),
                            self._button_group(leaders, _selected_leader),
                            ]).set_alignment_top().add_spacer(VerticallyExpandingSpacer()),
                        VerticalGroupBox([
                            BoldLabel("Select Base"),
                            self._button_group(bases, _selected_base),
                            ]).set_alignment_top().add_spacer(VerticallyExpandingSpacer()),
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
                ]).add_spacer(HorizontallyExpandingSpacer()),
                HorizontalBoxLayout([
                    PushButton("Cancel", self.reject),
                    self._accept_button
                ])
            ]).set_to_layout(self)
            
            self._sync_ui()
        
        def _button_group(self, cards: List[SWUTradingCard], selected_fn: Callable[[SWUTradingCard], None]) -> ButtonGroup:
            button_group_values: List[tuple[str, SWUTradingCard]] = []
            button_group_values = list(map(lambda x: (x.name, x), cards))
            
            
            button_group = ButtonGroup(button_group_values, selected_fn)
            button_group.set_checked(0)
            return button_group
        
        @property
        def export_format_index(self) -> int:
            return self._export_format.currentIndex()
        
        @property
        def selected_leader(self) -> SWUTradingCard:
            return self._selected_leader
        
        @property
        def selected_base(self) -> SWUTradingCard:
            return self._selected_base
        
        @property
        def main_deck(self) -> List[SWUTradingCard]:
            filtered = list(filter(lambda x: x.is_sideboard == False, self._main_card_objects))
            return list(map(lambda x: x.trading_card, filtered))
        
        @property
        def side_board(self) -> List[SWUTradingCard]:
            filtered = list(filter(lambda x: x.is_sideboard == True, self._main_card_objects))
            return list(map(lambda x: x.trading_card, filtered))
        
        @property
        def selected_cards(self) -> tuple[SWUTradingCard, SWUTradingCard]:
            return self._selected_leader, self._selected_base
        
        def _sync_ui(self):
            # self._accept_button.setEnabled(self._selected_value is not None)
            pass
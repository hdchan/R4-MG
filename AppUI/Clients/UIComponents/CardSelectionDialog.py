from typing import List, Optional

from PyQt5.QtWidgets import QDialog, QWidget

from R4UI import (HorizontalBoxLayout, LabeledRadioButton, PushButton,
                    VerticalBoxLayout, VerticalGroupBox, ButtonGroup)

from ..Models.SWUTradingCard import SWUTradingCard


class CardSelectionDialog(QDialog):
        def __init__(self, 
                     trading_cards: List[SWUTradingCard]):
            super().__init__()
            # self.setWindowTitle("Custom Message Box")
            
            def _selected_value(value: SWUTradingCard) -> None:
                self._selected_value = value
                self._sync_ui()
                
            self._selected_value: Optional[SWUTradingCard] = None
            button_group_values: List[tuple[str, SWUTradingCard]] = []
            button_group_values = list(map(lambda x: (x.name, x), trading_cards))
            
            self._accept_button = PushButton("Accept", self.accept)
            
            VerticalBoxLayout([
                ButtonGroup(button_group_values, _selected_value),
                HorizontalBoxLayout([
                    PushButton("Cancel", self.reject),
                    self._accept_button
                ])
            ]).set_layout_to_widget(self)
            
            self._sync_ui()
        
        @property
        def selected_card(self) -> Optional[SWUTradingCard]:
            return self._selected_value
        
        def _sync_ui(self):
            self._accept_button.setEnabled(self._selected_value is not None)
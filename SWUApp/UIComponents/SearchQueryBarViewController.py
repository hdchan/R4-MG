from typing import Optional

from AppCore.Models import SearchConfiguration
from AppUI.ExternalAppDependenciesProviding import SearchQueryBarViewProviding
from R4UI import RComboBox, HorizontalBoxLayout, Label, LineEditText

from ..Models.CardType import CardType
from ..Models.SWUCardSearchConfiguration import SWUCardSearchConfiguration


class SearchQueryBarViewController(SearchQueryBarViewProviding):
    def __init__(self):
        super().__init__()
        
        self._query_text: Optional[str] = None

        self._query_search_bar = LineEditText(triggered_fn=self._set_text,
                         placeholder_text="Lookup by card name (Ctrl+L)")
        self._card_type_selection = RComboBox(list(CardType))
        HorizontalBoxLayout([
            self._query_search_bar,
            HorizontalBoxLayout([
                Label("Type"),
                self._card_type_selection
            ])
        ]).set_uniform_content_margins(0).set_layout_to_widget(self)

    def _set_text(self, text: str):
        self._query_text = text

    def set_enabled(self, is_on: bool) -> None:
        self._query_search_bar.setEnabled(is_on)
        self._card_type_selection.setEnabled(is_on)

    @property
    def search_configuration(self) -> SearchConfiguration:
        config = SWUCardSearchConfiguration()
        if self._query_text is not None:
            config.card_name = self._query_text.strip()
        try:
            index = self._card_type_selection.currentIndex()
            card_type = list(CardType)[index]
            config.card_type = card_type
        except:
            pass
        return config
    
    @property
    def secondary_search_configuration(self) -> Optional[SearchConfiguration]:
        config = SWUCardSearchConfiguration()
        if self._query_text is not None:
            config.card_name = self._query_text.strip()
        try:
            index = self._card_type_selection.currentIndex()
            card_type = list(CardType)[index]
            config.card_type = card_type
        except:
            pass
        config.card_type = CardType.LEADER
        return config
        

    @property
    def tertiary_search_configuration(self) -> Optional[SearchConfiguration]:
        config = SWUCardSearchConfiguration()
        if self._query_text is not None:
            config.card_name = self._query_text.strip()
        try:
            index = self._card_type_selection.currentIndex()
            card_type = list(CardType)[index]
            config.card_type = card_type
        except:
            pass
        config.card_type = CardType.BASE
        return config
    
    def set_search_focus(self) -> None:
        self._query_search_bar.setFocus()
        self._query_search_bar.selectAll()
    
    def reset_search(self) -> None:
        self._query_search_bar.clear()
        self.set_card_type_filter(None)

    def did_receive_configuration(self, search_configuration: SearchConfiguration) -> None:
        self.set_search_bar_text(search_configuration.card_name)
        swu_search_config = SWUCardSearchConfiguration.from_search_configuration(search_configuration)
        self.set_card_type_filter(swu_search_config.card_type)

    def set_card_type_filter(self, card_type: Optional[str]):
        if card_type is not None:
            found_index = self._card_type_selection.findText(card_type)
        else:
            found_index = self._card_type_selection.findText(list(CardType)[0])
           
        if found_index >= 0:
                self._card_type_selection.setCurrentIndex(found_index)
        else:
            raise Exception("index not found")

    def set_search_bar_text(self, text: str):
        self._query_search_bar.setText(text)
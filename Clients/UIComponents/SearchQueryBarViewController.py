from AppCore.Models import SearchConfiguration
from AppUI.ExternalAppDependenciesProviding import SearchQueryBarViewProviding
from R4UI import ComboBox, HorizontalBoxLayout, Label, LineEditText, R4UIWidget
from typing import Optional

class SearchQueryBarViewController(SearchQueryBarViewProviding):
    def __init__(self):
        super().__init__()

        self._query_text: Optional[str] = None

        HorizontalBoxLayout([
            LineEditText(triggered_fn=self._set_text,
                         placeholder_text="Lookup by card name (Ctrl+L)"),
            HorizontalBoxLayout([
                Label("Type"),
                ComboBox([
                    "Option 1"
                ])
            ])
        ]).set_uniform_content_margins(0).set_layout_to_widget(self)

        # query_layout = QHBoxLayout()
        # query_layout.setContentsMargins(0, 0, 0, 0)
        # query_widget = QWidget()
        # query_widget.setLayout(query_layout)
        # layout.addWidget(query_widget)

        # card_name_search_bar = QLineEdit(self)
        # card_name_search_bar.setPlaceholderText()
        # self.card_name_search_bar = card_name_search_bar
        # query_layout.addWidget(card_name_search_bar)
        
        # card_type_layout = QHBoxLayout()
        # card_type_layout.setContentsMargins(0, 0, 0, 0)
        # card_type_widget = QWidget()
        # card_type_widget.setLayout(card_type_layout)
        # query_layout.addWidget(card_type_widget)
        
        # card_type_selection_label = QLabel("Type")
        # card_type_layout.addWidget(card_type_selection_label)
        # self._card_type_selection_label = card_type_selection_label
        
        # card_type_selection = QComboBox()
        # for i in self._delegate.stc_card_type_list:
        #     card_type_selection.addItem(i)
        # self.card_type_selection = card_type_selection
        # card_type_layout.addWidget(card_type_selection)

    def _set_text(self, text: str):
        self._query_text = text

    @property
    def search_configuration(self) -> SearchConfiguration:
        config = SearchConfiguration()
        if self._query_text is not None:
            config.card_name = self._query_text.strip()
        return config
from typing import List, Optional

from PyQt5.QtWidgets import (QComboBox, QHBoxLayout, QLabel, QLineEdit,
                             QListWidget, QPushButton, QVBoxLayout, QWidget)

from AppCore.Models import CardType
from AppCore.Observation import ObservationTower, TransmissionReceiver
from AppCore.Observation.Events import SearchEvent, TransmissionProtocol

from .LoadingSpinner import LoadingSpinner


class SearchTableView(QWidget, TransmissionReceiver):
    def __init__(self, 
                 observation_tower: ObservationTower, 
                 card_type_list: List[CardType]):
        super().__init__()
        card_name_search_bar = QLineEdit(self)
        card_name_search_bar.setPlaceholderText("Search card by name (Ctrl+L)")
        card_name_search_bar.returnPressed.connect(self.search)
        self.card_name_search_bar = card_name_search_bar

        search_button = QPushButton()
        search_button.setText("Search (Enter)")
        search_button.clicked.connect(self.search)
        self.search_button = search_button
        
        
        card_type_selection_label = QLabel("Card type")
        
        card_type_selection = QComboBox()
        for i in card_type_list:
            card_type_selection.addItem(i.value)
        card_type_selection.currentIndexChanged.connect(self._card_type_selection_changed)
        self.card_type_selection = card_type_selection
        self._card_type_list = card_type_list
        
        card_type_selection_layout = QHBoxLayout(self)
        container_widget = QWidget(self)
        

        result_list = QListWidget(self)
        result_list.itemSelectionChanged.connect(self.get_selection)
        self.result_list = result_list

        layout = QVBoxLayout(self)
        layout.addWidget(card_name_search_bar)
        card_type_selection_layout.addWidget(card_type_selection_label)
        card_type_selection_layout.addWidget(card_type_selection, 1)
        container_widget.setLayout(card_type_selection_layout)
        
        layout.addWidget(container_widget)
        
        layout.addWidget(search_button)
        layout.addWidget(result_list)
        self.setLayout(layout)
        
        self._loading_spinner = LoadingSpinner(self)

        self.delegate = None
        
        self.set_card_type_filter(None)
        
        observation_tower.subscribe(self, SearchEvent)

    def get_selection(self):
        selected_indexs = self.result_list.selectedIndexes()
        if len(selected_indexs) > 0:
            self.delegate.tv_did_select(self, selected_indexs[0].row())

    def set_search_focus(self):
        self.card_name_search_bar.setFocus()

    def set_item_active(self, index: int):
        self.result_list.setCurrentRow(index)

    def set_card_type_filter(self, card_type: Optional[CardType]):
        if card_type is not None:
            found_index = self.card_type_selection.findText(card_type.value)
        else:
            found_index = self.card_type_selection.findText(CardType.UNSPECIFIED.value)
           
        if found_index >= 0:
                self.card_type_selection.setCurrentIndex(found_index)
        else:
            raise Exception("index not found")

    def search(self):
        # prevent query errors
        stripped_text = self.card_name_search_bar.text().strip()
        self.card_name_search_bar.setText(stripped_text)
        self.delegate.tv_did_tap_search(self, stripped_text)
        

    def update_list(self, list: List[str]):
        self.result_list.clear()
        for i in list:
            self.result_list.addItem(i)
        # important that this is the last thing that happens
        self._set_search_components_enabled(True)
        

    def _set_search_components_enabled(self, is_on: bool):
        self.card_name_search_bar.setEnabled(is_on)
        self.search_button.setEnabled(is_on)
        self.card_type_selection.setEnabled(is_on)
        if is_on:
            self._loading_spinner.stop()
        else:
            self._loading_spinner.start()
        
    def _card_type_selection_changed(self):
        selection = self._card_type_list[self.card_type_selection.currentIndex()]
        self.delegate.tv_did_update_search_configuration(self, selection)
        
    def handle_observation_tower_event(self, event: TransmissionProtocol):
        if type(event) == SearchEvent:
            if event.event_type == SearchEvent.EventType.STARTED:
                self._set_search_components_enabled(False)
                if event.is_system_initiated:
                    self.card_name_search_bar.clear()
            elif event.event_type == SearchEvent.EventType.FINISHED:
                self._set_search_components_enabled(True)
                if self.result_list.count() > 0:
                    self.set_item_active(0)
                
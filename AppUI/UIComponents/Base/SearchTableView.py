from typing import List, Optional
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QComboBox, QHBoxLayout, QLabel, QLineEdit,
                             QListWidget, QPushButton, QVBoxLayout, QWidget, QCheckBox)

from AppCore.Models import CardType, TradingCard, SearchConfiguration, CardAspect
from AppCore.Observation import ObservationTower, TransmissionReceiver
from AppCore.Observation.Events import SearchEvent, TransmissionProtocol
from ...Observation.Events import KeyboardEvent
from .LoadingSpinner import LoadingSpinner

class SearchTableView(QWidget, TransmissionReceiver):
    def __init__(self, 
                 observation_tower: ObservationTower, 
                 card_type_list: List[CardType]):
        super().__init__()
        card_name_search_bar = QLineEdit(self)
        card_name_search_bar.setPlaceholderText("Search card by name (Ctrl+L)")
        # card_name_search_bar.returnPressed.connect(self.search)
        self.card_name_search_bar = card_name_search_bar

        search_button = QPushButton()
        search_button.clicked.connect(self.search)
        self.search_button = search_button
        self.set_default_search_button_text()
        
        card_type_selection_label = QLabel("Card type")
        
        card_type_selection = QComboBox()
        for i in card_type_list:
            card_type_selection.addItem(i.value)
        self.card_type_selection = card_type_selection
        self._card_type_list = card_type_list
        
        card_type_selection_layout = QHBoxLayout()
        container_widget = QWidget()
        

        result_list = QListWidget()
        result_list.itemSelectionChanged.connect(self.get_selection)
        self.result_list = result_list

        layout = QVBoxLayout()
        layout.addWidget(card_name_search_bar)
        card_type_selection_layout.addWidget(card_type_selection_label)
        card_type_selection_layout.addWidget(card_type_selection, 1)
        container_widget.setLayout(card_type_selection_layout)
        
        layout.addWidget(container_widget)
        
        aspect_map = {
            "B": CardAspect.VIGILANCE,
            "G": CardAspect.COMMAND,
            "R": CardAspect.AGGRESSION,
            "Y": CardAspect.CUNNING,
            "W": CardAspect.HEROISM,
            "K": CardAspect.VILLAINY
        }
        checkbox_layout = QHBoxLayout()
        checkbox_widget = QWidget()
        checkbox_widget.setLayout(checkbox_layout)
        self.check_boxes = []
        self.check_boxes_map = {}
        for a in aspect_map.keys():
            box = QCheckBox(a)
            self.check_boxes.append(box)
            self.check_boxes_map[box] = aspect_map[a]
            # checkbox_layout.addWidget(box)
        layout.addWidget(checkbox_widget)
        
        
        layout.addWidget(search_button)
        layout.addWidget(result_list)
        self.setLayout(layout)
        
        self._loading_spinner = LoadingSpinner(self)

        self.delegate = None
        
        self._set_card_type_filter(None)
        
        observation_tower.subscribe_multi(self, [SearchEvent, 
                                                 KeyboardEvent])
    def set_default_search_button_text(self):
        self.search_button.setText("Search (Enter)")

    def get_selection(self):
        selected_indexs = self.result_list.selectedIndexes()
        if len(selected_indexs) > 0:
            self.delegate.tv_did_select(self, selected_indexs[0].row())

    def set_search_focus(self):
        self.card_name_search_bar.setFocus()
        self.card_name_search_bar.selectAll()

    def set_item_active(self, index: int):
        self.result_list.setCurrentRow(index)

    def _set_card_type_filter(self, card_type: Optional[CardType]):
        if card_type is not None:
            found_index = self.card_type_selection.findText(card_type.value)
        else:
            found_index = self.card_type_selection.findText(CardType.UNSPECIFIED.value)
           
        if found_index >= 0:
                self.card_type_selection.setCurrentIndex(found_index)
        else:
            raise Exception("index not found")

    def search(self):
        self._search()

    def search_leader(self):
        def modifier(config):
            config.card_type = CardType.LEADER
            return config
        self._search(modifier)
        
    def search_base(self):
        def modifier(config):
            config.card_type = CardType.BASE
            return config
        self._search(modifier)

    def _search(self, config_modifier = None):
        # prevent query errors
        stripped_text = self.card_name_search_bar.text().strip()
        self.card_name_search_bar.setText(stripped_text)
        
        search_configuration = SearchConfiguration()
        search_configuration.card_name = stripped_text
        search_configuration.card_type = self._card_type_list[self.card_type_selection.currentIndex()]
        for i in self.check_boxes_map.keys():
            if i.isChecked():
                search_configuration.card_aspects.append(self.check_boxes_map[i])
                
        if config_modifier is not None:
            search_configuration = config_modifier(search_configuration)
        
        self.delegate.tv_did_tap_search(self, search_configuration)

        

    def update_list(self, list: List[TradingCard]):
        # https://stackoverflow.com/questions/25187444/pyqt-qlistwidget-custom-items
        self.result_list.clear()
        for i in list:
            self.result_list.addItem(i.friendly_display_name)
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
        
    def _set_card_aspect_filter(self, aspects: List[CardAspect]):
        # for i in self.asp
        pass
        
    def handle_observation_tower_event(self, event: TransmissionProtocol):
        if type(event) == SearchEvent:
            if event.event_type == SearchEvent.EventType.STARTED:
                self._set_search_components_enabled(False)
                self.card_name_search_bar.setText(event.search_configuration.card_name)
                self._set_card_type_filter(event.search_configuration.card_type)

            elif event.event_type == SearchEvent.EventType.FINISHED:
                self._set_search_components_enabled(True)
                if self.result_list.count() > 0:
                    self.set_item_active(0)
        elif type(event) == KeyboardEvent:
            # TODO: buggy
            pass
            # if event.action == KeyboardEvent.Action.PRESSED:
            #     if event.event.key() == Qt.Key.Key_Shift:
            #         self.search_button.setText('Search Base (Shift + Enter)')
                
            #     elif event.event.key() == Qt.Key.Key_Control:
            #         self.search_button.setText('Search Leader (Ctrl + Enter)')
            # else:
            #     if event.event.key() == Qt.Key.Key_Shift or event.event.key() == Qt.Key.Key_Control:
            #         self.set_default_search_button_text()
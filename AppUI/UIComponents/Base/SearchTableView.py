from typing import Dict, List, Optional

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QCheckBox, QComboBox, QHBoxLayout, QLabel,
                             QLineEdit, QListWidget, QPushButton, QVBoxLayout,
                             QWidget)

from AppCore.Models import (CardAspect, CardType, SearchConfiguration,
                            TradingCard)
from AppCore.Observation import ObservationTower, TransmissionReceiver
from AppCore.Observation.Events import SearchEvent, TransmissionProtocol, ConfigurationUpdatedEvent

from ...Observation.Events import KeyboardEvent
from .LoadingSpinner import LoadingSpinner
from AppCore.Config import ConfigurationProvider, Configuration


class SearchTableViewDelegate:
    def tv_did_select(self, sv: ..., index: int) -> None:
        pass

    def tv_did_tap_search(self, sv: ..., search_configuration: SearchConfiguration) -> None:
        pass

class SearchTableView(QWidget, TransmissionReceiver):
    def __init__(self, 
                 observation_tower: ObservationTower, 
                 card_type_list: List[CardType], 
                 configuration_provider: ConfigurationProvider):
        super().__init__()
        
        self._shift_pressed = False
        self._ctrl_pressed = False
        self._configuration_provider = configuration_provider
        self._result_list: Optional[List[TradingCard]] = None
        # self._selected_index = 0

        layout = QVBoxLayout()
        self.setLayout(layout)
        
        
        query_layout = QHBoxLayout()
        query_layout.setContentsMargins(0, 0, 0, 0)
        query_widget = QWidget()
        # query_widget.setStyleSheet('background-color: red;')
        query_widget.setLayout(query_layout)
        layout.addWidget(query_widget)
        
        card_name_search_bar = QLineEdit(self)
        card_name_search_bar.setPlaceholderText("Lookup by card name (Ctrl+L)")
        self.card_name_search_bar = card_name_search_bar
        query_layout.addWidget(card_name_search_bar, 1)
        
        card_type_layout = QHBoxLayout()
        card_type_layout.setContentsMargins(0, 0, 0, 0)
        card_type_widget = QWidget()
        card_type_widget.setLayout(card_type_layout)
        query_layout.addWidget(card_type_widget)
        
        card_type_selection_label = QLabel("Type")
        card_type_layout.addWidget(card_type_selection_label)
        
        card_type_selection = QComboBox()
        for i in card_type_list:
            card_type_selection.addItem(i.value)
        self.card_type_selection = card_type_selection
        self._card_type_list = card_type_list
        card_type_layout.addWidget(card_type_selection)
        
        
        result_list = QListWidget()
        result_list.itemSelectionChanged.connect(self.get_selection)
        self.result_list = result_list
        layout.addWidget(result_list, 1)
        
        
        # card_type_selection_layout.addWidget(card_type_selection_label)
        # card_type_selection_layout.addWidget(card_type_selection, 1)
        # container_widget.setLayout(card_type_selection_layout)
        
        
        
        # aspect_map = {
        #     "B": CardAspect.VIGILANCE,
        #     "G": CardAspect.COMMAND,
        #     "R": CardAspect.AGGRESSION,
        #     "Y": CardAspect.CUNNING,
        #     "W": CardAspect.HEROISM,
        #     "K": CardAspect.VILLAINY
        # }
        # checkbox_layout = QHBoxLayout()
        # checkbox_widget = QWidget()
        # checkbox_widget.setLayout(checkbox_layout)
        # self.check_boxes: List[QCheckBox] = []
        # self.check_boxes_map: Dict[QCheckBox, CardAspect] = {}
        # for a in aspect_map.keys():
        #     box = QCheckBox(a)
        #     self.check_boxes.append(box)
        #     self.check_boxes_map[box] = aspect_map[a]
        #     # checkbox_layout.addWidget(box)
        # layout.addWidget(checkbox_widget)
        
        
        
        
        search_button = QPushButton()
        search_button.clicked.connect(self.search)
        self.search_button = search_button
        self._sync_search_button_text()
        layout.addWidget(search_button)
        
        
        self._loading_spinner = LoadingSpinner(self)

        self.delegate: Optional[SearchTableViewDelegate] = None
        
        self._set_card_type_filter(None)
        
        observation_tower.subscribe_multi(self, [SearchEvent, 
                                                 KeyboardEvent, 
                                                 ConfigurationUpdatedEvent]) 
        
        self._is_config_updating = False

    def get_selection(self):
        if self._is_config_updating:
            # don't trigger update when changing configuration
            return
        selected_indexs = self.result_list.selectedIndexes()
        if len(selected_indexs) > 0 and self.delegate is not None:
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
        def modifier(config: SearchConfiguration) -> SearchConfiguration:
            config.card_type = CardType.LEADER
            return config
        self._search(modifier)
        
    def search_base(self):
        def modifier(config: SearchConfiguration) -> SearchConfiguration:
            config.card_type = CardType.BASE
            return config
        self._search(modifier)

    def _search(self, config_modifier: ... = None):
        # prevent query errors
        stripped_text = self.card_name_search_bar.text().strip()
        self.card_name_search_bar.setText(stripped_text)
        
        search_configuration = SearchConfiguration()
        search_configuration.card_name = stripped_text
        search_configuration.card_type = self._card_type_list[self.card_type_selection.currentIndex()]
        # for i in self.check_boxes_map.keys():
        #     if i.isChecked():
        #         search_configuration.card_aspects.append(self.check_boxes_map[i])
                
        if config_modifier is not None:
            search_configuration = config_modifier(search_configuration)
        
        if self.delegate is not None:
            self.delegate.tv_did_tap_search(self, search_configuration)


    def update_list(self, list: List[TradingCard]):
        # https://stackoverflow.com/questions/25187444/pyqt-qlistwidget-custom-items
        self._result_list = list
        self._load_list()
        
    def _load_list(self):
        selected_indexs = self.result_list.selectedIndexes()
        selected_index = 0
        if len(selected_indexs) > 0:
            selected_index = selected_indexs[0].row()

        if self._result_list is not None:
            self.result_list.clear()
            for i in self._result_list:
                display_name = i.friendly_display_name
                if self._configuration_provider.configuration.card_title_detail == Configuration.Settings.CardTitleDetail.SHORT:
                    display_name = i.friendly_display_name_short
                elif self._configuration_provider.configuration.card_title_detail == Configuration.Settings.CardTitleDetail.DETAILED:
                    display_name = i.friendly_display_name_detailed
                self.result_list.addItem(display_name)
            # important that this is the last thing that happens
            self.set_item_active(selected_index)
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
    
    def _sync_search_button_text(self):
        if self._ctrl_pressed and self._shift_pressed:
            self.search_button.setText("Only Ctrl OR Shift can be held to search")
        elif self._ctrl_pressed:
            self.search_button.setText('Search Leader (Ctrl + Enter)')
        elif self._shift_pressed:
            self.search_button.setText('Search Base (Shift + Enter)')
        else:
            self.search_button.setText("Search (Enter)")
        
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
            if event.action == KeyboardEvent.Action.PRESSED:
                if event.event.key() == Qt.Key.Key_Shift:
                    self._shift_pressed = True
                
                if event.event.key() == Qt.Key.Key_Control:
                    self._ctrl_pressed = True
            else:
                if event.event.key() == Qt.Key.Key_Shift:
                    self._shift_pressed = False
                    
                if event.event.key() == Qt.Key.Key_Control:
                    self._ctrl_pressed = False
            self._sync_search_button_text()

        elif type(event) == ConfigurationUpdatedEvent:
            self._is_config_updating = True
            self._load_list()
            self._is_config_updating = False
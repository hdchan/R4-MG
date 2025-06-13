from typing import List, Optional
from urllib.error import HTTPError

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QComboBox, QHBoxLayout, QLabel, QLineEdit,
                             QListWidget, QPushButton, QVBoxLayout, QWidget)

from AppCore.Config import Configuration
from AppCore.Data.CardSearchDataSource import *
from AppCore.Models import (CardType, LocalCardResource, SearchConfiguration,
                            TradingCard)
from AppCore.Observation import *
from AppCore.Observation.Events import (ConfigurationUpdatedEvent,
                                        LocalResourceFetchEvent, SearchEvent)
from AppUI.AppDependencyProviding import AppDependencyProviding
from AppUI.Clients import SWUCardSearchConfiguration

from ...Observation.Events import KeyboardEvent
from ..Base.ImagePreviewViewController import ImagePreviewViewController
from .LoadingSpinner import LoadingSpinner


class SearchTableViewController(QWidget, TransmissionReceiverProtocol, CardSearchDataSourceDelegate):
    def __init__(self, 
                 app_dependency_provider: AppDependencyProviding,
                 image_preview_view: ImagePreviewViewController):
        super().__init__()
        self._image_preview_view = image_preview_view
        self._card_search_data_source = CardSearchDataSource(app_dependency_provider, 
                                                             app_dependency_provider.api_client_provider, 
                                                             page_size=40) 
        self._card_search_data_source.delegate = self
        self._observation_tower = app_dependency_provider.observation_tower
        
        self._shift_pressed = False
        self._ctrl_pressed = False
        self._configuration_manager = app_dependency_provider.configuration_manager
        self._result_list: Optional[List[TradingCard]] = None

        layout = QVBoxLayout()
        self.setLayout(layout)
        
        buttons_layout = QHBoxLayout()
        buttons_layout.setContentsMargins(0, 0, 0, 0)
        buttons_widget = QWidget()
        buttons_widget.setLayout(buttons_layout)
        layout.addWidget(buttons_widget)

        flip_button = QPushButton()
        flip_button.setText("Flip (Ctrl+F)")
        flip_button.setEnabled(False)
        flip_button.clicked.connect(self._tapped_flip_button)
        self.flip_button = flip_button
        buttons_layout.addWidget(flip_button)
        
        query_layout = QHBoxLayout()
        query_layout.setContentsMargins(0, 0, 0, 0)
        query_widget = QWidget()
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
        self._card_type_list = list(CardType)
        for i in self._card_type_list:
            card_type_selection.addItem(i.value)
        self.card_type_selection = card_type_selection
        card_type_layout.addWidget(card_type_selection)
        
        
        result_list = QListWidget()
        result_list.itemSelectionChanged.connect(self.get_selection)
        result_list.itemClicked.connect(self.get_selection)
        self.result_list = result_list
        layout.addWidget(result_list, 1)
        vertical_scroll_bar = result_list.verticalScrollBar()
        if vertical_scroll_bar is not None:
            vertical_scroll_bar.valueChanged.connect(self._result_list_scrolled)
        
        
        search_button = QPushButton()
        search_button.clicked.connect(self.search)
        self.search_button = search_button
        self._sync_search_button_text()
        layout.addWidget(search_button)
        
        
        search_source_label = QLabel()
        search_source_label.setOpenExternalLinks(True)
        layout.addWidget(search_source_label)
        self.search_source_label = search_source_label

        self._load_source_labels()
        
        
        self._loading_spinner = LoadingSpinner(self)
        
        self._set_card_type_filter(None)
        
        app_dependency_provider.observation_tower.subscribe_multi(self, [SearchEvent,
                                                                         KeyboardEvent,
                                                                         ConfigurationUpdatedEvent, 
                                                                         LocalResourceFetchEvent]) 
        
        app_dependency_provider.shortcut_action_coordinator.bind_flip(self._tapped_flip_button, self)
        app_dependency_provider.shortcut_action_coordinator.bind_focus_search(self._set_search_focus, self)
        app_dependency_provider.shortcut_action_coordinator.bind_reset_search(self._reset_search, self)
        app_dependency_provider.shortcut_action_coordinator.bind_search(self.search, self)
        app_dependency_provider.shortcut_action_coordinator.bind_search_leader(self._search_leader, self)
        app_dependency_provider.shortcut_action_coordinator.bind_search_base(self._search_base, self)

        self._sync_ui()
    
    @property
    def card_search_data_source(self) -> CardSearchDataSource:
        return self._card_search_data_source
    
    @property
    def _configuration(self) -> Configuration:
        return self._configuration_manager.configuration
    
    def ds_completed_search_with_result(self, 
                                        ds: CardSearchDataSource,
                                        error: Optional[Exception], 
                                        is_initial_load: bool, 
                                        has_more_pages: bool):
        status = "🟢 OK"
        if error is not None:
            if isinstance(error, HTTPError):
                status = f"🔴 {error.code}"
            else:
                status = str(error)
        self.update_list(self._card_search_data_source.trading_cards, is_initial_load, has_more_pages)
        self._load_source_labels(status_string=status)

    def ds_did_retrieve_card_resource_for_card_selection(self, 
                                                         ds: CardSearchDataSource, 
                                                         local_resource: LocalCardResource, 
                                                         is_flippable: bool):
        self._image_preview_view.set_image(local_resource)
        self._sync_buttons(is_flippable)

    def set_active(self):
        self.get_selection()

    def get_selection(self):
        selected_indexs = self.result_list.selectedIndexes()
        if len(selected_indexs) > 0:
            self._card_search_data_source.select_card_resource_for_card_selection(selected_indexs[0].row())

    def _set_search_focus(self):
        self.card_name_search_bar.setFocus()
        self.card_name_search_bar.selectAll()

    def _reset_search(self):
        self.card_name_search_bar.clear()
        self.card_name_search_bar.setFocus()
        self._set_card_type_filter(None)

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

    def _search_leader(self):
        def modifier(config: SWUCardSearchConfiguration) -> SearchConfiguration:
            config.card_type = CardType.LEADER
            return config
        self._search(modifier)
        
    def _search_base(self):
        def modifier(config: SWUCardSearchConfiguration) -> SearchConfiguration:
            config.card_type = CardType.BASE
            return config
        self._search(modifier)

    def _search(self, config_modifier: ... = None):
        # prevent query errors
        stripped_text = self.card_name_search_bar.text().strip()
        self.card_name_search_bar.setText(stripped_text)
        
        search_configuration = SWUCardSearchConfiguration()
        search_configuration.card_name = stripped_text
        search_configuration.card_type = self._card_type_list[self.card_type_selection.currentIndex()]
                
        if config_modifier is not None:
            search_configuration = config_modifier(search_configuration)
        
        self._card_search_data_source.search(search_configuration)

    def _tapped_flip_button(self):
        self._card_search_data_source.flip_current_previewed_card()
        
    def _sync_buttons(self, is_flippable: bool):
        self.flip_button.setEnabled(is_flippable)

    def update_list(self, 
                    list: List[TradingCard], 
                    is_initial_load: bool, 
                    has_more_pages: bool):
        # https://stackoverflow.com/questions/25187444/pyqt-qlistwidget-custom-items
        self._result_list = list
        self._load_list(is_initial_load, has_more_pages)
        
    def _load_list(self, is_initial_load: bool, has_more_pages: bool):
        vertical_scroll_bar = self.result_list.verticalScrollBar()
        current_position = 0
        if vertical_scroll_bar is not None:
            current_position = vertical_scroll_bar.sliderPosition()
        
        selected_indexs = self.result_list.selectedIndexes()
        selected_index = 0
        if len(selected_indexs) > 0:
            selected_index = selected_indexs[0].row()

        if self._result_list is not None:
            self.result_list.clear()
            for i in self._result_list:
                display_name = i.friendly_display_name
                if self._configuration.card_title_detail == Configuration.Settings.CardTitleDetail.SHORT:
                    display_name = i.friendly_display_name_short
                elif self._configuration.card_title_detail == Configuration.Settings.CardTitleDetail.DETAILED:
                    display_name = i.friendly_display_name_detailed
                self.result_list.addItem(display_name)
                # self.result_list.item(len(self.result_list) - 1).setToolTip("<img src='https://cdn.swu-db.com/images/cards/TWI/269.png' />") 
            
            if has_more_pages:
                self.result_list.addItem('Loading more...')
            else:
                self.result_list.addItem('No more results')
            # important that this is the last thing that happens
            self.set_item_active(selected_index)
            self._set_search_components_enabled(True)
            
            
        if not is_initial_load and vertical_scroll_bar is not None:
            vertical_scroll_bar.setSliderPosition(current_position)

    def _set_search_components_enabled(self, is_on: bool):
        self.card_name_search_bar.setEnabled(is_on)
        self.search_button.setEnabled(is_on)
        self.card_type_selection.setEnabled(is_on)
        if is_on:
            self._loading_spinner.stop()
        else:
            self._loading_spinner.start()
            
    def _sync_ui(self):
        pass

    def _load_source_labels(self, status_string: str = ""):
        search_source_url = self._card_search_data_source.site_source_url
        if search_source_url is not None:
            self.search_source_label.setText(f'Search source: <a href="{search_source_url}">{self._card_search_data_source.source_display_name}</a> {status_string}')
        else:
            self.search_source_label.setText(f'Search source: {self._card_search_data_source.source_display_name} {status_string}')
    
    def _sync_search_button_text(self):
        if self._ctrl_pressed and self._shift_pressed:
            self.search_button.setText("Only Ctrl OR Shift can be held to search")
        elif self._ctrl_pressed:
            self.search_button.setText('Search Leader (Ctrl + Enter)')
        elif self._shift_pressed:
            self.search_button.setText('Search Base (Shift + Enter)')
        else:
            self.search_button.setText("Search (Enter)")
    
    def _result_list_scrolled(self, value: int):
        # print(value)
        vertical_scroll_bar = self.result_list.verticalScrollBar()
        if vertical_scroll_bar is not None:
            if value >= vertical_scroll_bar.maximum() * .8:
                self._card_search_data_source.load_next_page()
        
    def handle_observation_tower_event(self, event: TransmissionProtocol):
        if type(event) == SearchEvent:
            if event.event_type == SearchEvent.EventType.STARTED:
                self._set_search_components_enabled(False)
                self.card_name_search_bar.setText(event.search_configuration.card_name)
                # TODO: may need more specific check
                swu_search_config = SWUCardSearchConfiguration.from_search_configuration(event.search_configuration)
                self._set_card_type_filter(swu_search_config.card_type)

            elif event.event_type == SearchEvent.EventType.FINISHED:
                self._set_search_components_enabled(True)
                if self.result_list.count() > 0:
                    self.set_item_active(0)

            if event.seconds_since_predecessor is not None:
                print(f"Search took :{event.seconds_since_predecessor}s")
                    
        if type(event) == KeyboardEvent:
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

        if type(event) == ConfigurationUpdatedEvent:
            self._load_source_labels()
            self._sync_ui()
            
        if type(event) == LocalResourceFetchEvent:
            pass
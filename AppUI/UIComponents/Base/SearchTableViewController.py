from typing import List, Optional

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QComboBox, QHBoxLayout, QLabel, QLineEdit,
                             QListWidget, QPushButton, QVBoxLayout, QWidget)

from AppCore.Config import Configuration
from AppCore.Data.CardSearchDataSource import *
from AppCore.Models import LocalCardResource, SearchConfiguration, TradingCard
from AppCore.Observation import *
from AppCore.Observation.Events import (ConfigurationUpdatedEvent,
                                        LocalResourceFetchEvent, SearchEvent)
from AppUI.AppDependencyProviding import AppDependencyProviding

from ...Clients.SWUDB import CardType, SWUDBAPISearchConfiguration
from ...Observation.Events import KeyboardEvent
from ..Base.ImagePreviewViewController import ImagePreviewViewController
from .LoadingSpinner import LoadingSpinner


class SearchTableViewController(QWidget, TransmissionReceiverProtocol, CardSearchDataSourceDelegate):
    def __init__(self, 
                 app_dependency_provider: AppDependencyProviding, 
                 card_search_data_source: CardSearchDataSource, 
                 image_preview_view: ImagePreviewViewController):
        super().__init__()
        self._image_preview_view = image_preview_view
        self._card_search_data_source = card_search_data_source 
        card_search_data_source.delegate = self
        self._card_image_source_provider = app_dependency_provider.image_source_provider
        self._observation_tower = app_dependency_provider.observation_tower
        
        self._shift_pressed = False
        self._ctrl_pressed = False
        self._configuration_manager = app_dependency_provider.configuration_manager
        self._result_list: Optional[List[TradingCard]] = None

        layout = QVBoxLayout()
        # layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)
        
        
        buttons_layout = QHBoxLayout()
        buttons_layout.setContentsMargins(0, 0, 0, 0)
        buttons_widget = QWidget()
        buttons_widget.setLayout(buttons_layout)
        layout.addWidget(buttons_widget)

        flip_button = QPushButton()
        flip_button.setText("Flip (Ctrl+F)")
        flip_button.setEnabled(False)
        flip_button.clicked.connect(self.tapped_flip_button)
        self.flip_button = flip_button
        buttons_layout.addWidget(flip_button)
        
        retry_button = QPushButton()
        retry_button.setText("Redownload")
        retry_button.setEnabled(False)
        retry_button.clicked.connect(self.tapped_retry_button)
        self.retry_button = retry_button
        # buttons_layout.addWidget(retry_button)
        
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
        self.result_list = result_list
        layout.addWidget(result_list, 1)
        
        
        search_button = QPushButton()
        search_button.clicked.connect(self.search)
        self.search_button = search_button
        self._sync_search_button_text()
        layout.addWidget(search_button)
        
        
        search_source_label = QLabel()
        search_source_label.setOpenExternalLinks(True)
        layout.addWidget(search_source_label)
        self.search_source_label = search_source_label

        image_source_label = QLabel()
        image_source_label.setOpenExternalLinks(True)
        layout.addWidget(image_source_label)
        self.image_source_label = image_source_label

        self._load_source_labels()
        
        
        self._loading_spinner = LoadingSpinner(self)
        
        self._set_card_type_filter(None)
        
        app_dependency_provider.observation_tower.subscribe_multi(self, [SearchEvent,
                                                                         KeyboardEvent,
                                                                         ConfigurationUpdatedEvent, 
                                                                         LocalResourceFetchEvent]) 
        
        app_dependency_provider.shortcut_action_coordinator.bind_flip(self.tapped_flip_button, self)
        app_dependency_provider.shortcut_action_coordinator.bind_focus_search(self.set_search_focus, self)
        app_dependency_provider.shortcut_action_coordinator.bind_search(self.search, self)
        app_dependency_provider.shortcut_action_coordinator.bind_search_leader(self.search_leader, self)
        app_dependency_provider.shortcut_action_coordinator.bind_search_base(self.search_base, self)

        self._is_config_updating = False

    def set_active(self):
        local_resource = self._card_search_data_source.selected_local_resource
        if local_resource is not None:
            self._image_preview_view.set_image(local_resource)
            self._observation_tower.notify(LocalResourceSelectedEvent(local_resource)) # rework?

    def ds_completed_search_with_result(self, 
                                        ds: CardSearchDataSource, 
                                        result_list: List[TradingCard], 
                                        error: Optional[Exception]):
        self.update_list(result_list)

    def ds_did_retrieve_card_resource_for_card_selection(self, 
                                                         ds: CardSearchDataSource, 
                                                         local_resource: LocalCardResource, 
                                                         is_flippable: bool):
        self.set_active()
        self._sync_buttons(is_flippable)

    def get_selection(self):
        if self._is_config_updating:
            # don't trigger update when changing configuration
            return
        selected_indexs = self.result_list.selectedIndexes()
        if len(selected_indexs) > 0:
            self._card_search_data_source.select_card_resource_for_card_selection(selected_indexs[0].row())

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
        def modifier(config: SWUDBAPISearchConfiguration) -> SearchConfiguration:
            config.card_type = CardType.LEADER
            return config
        self._search(modifier)
        
    def search_base(self):
        def modifier(config: SWUDBAPISearchConfiguration) -> SearchConfiguration:
            config.card_type = CardType.BASE
            return config
        self._search(modifier)

    def _search(self, config_modifier: ... = None):
        # prevent query errors
        stripped_text = self.card_name_search_bar.text().strip()
        self.card_name_search_bar.setText(stripped_text)
        
        search_configuration = SWUDBAPISearchConfiguration()
        search_configuration.card_name = stripped_text
        search_configuration.card_type = self._card_type_list[self.card_type_selection.currentIndex()]
                
        if config_modifier is not None:
            search_configuration = config_modifier(search_configuration)
        
        self._card_search_data_source.search(search_configuration)

    def tapped_flip_button(self):
        self._card_search_data_source.flip_current_previewed_card()
        
    def tapped_retry_button(self):
        self._card_search_data_source.redownload_currently_selected_card_resource()
        
    def _sync_buttons(self, is_flippable: bool):
        self.flip_button.setEnabled(is_flippable)
        self._sync_retry_button()
    
    def _sync_retry_button(self):
        local_resource = self._card_search_data_source.selected_local_resource
        if local_resource is not None:
            self.retry_button.setEnabled(local_resource.remote_image_url is not None and not local_resource.is_loading)
        else:
            self.retry_button.setEnabled(False)

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
                if self._configuration_manager.configuration.card_title_detail == Configuration.Settings.CardTitleDetail.SHORT:
                    display_name = i.friendly_display_name_short
                elif self._configuration_manager.configuration.card_title_detail == Configuration.Settings.CardTitleDetail.DETAILED:
                    display_name = i.friendly_display_name_detailed
                self.result_list.addItem(display_name)
                # self.result_list.item(len(self.result_list) - 1).setToolTip("<img src='https://cdn.swu-db.com/images/cards/TWI/269.png' />") 
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

    def _load_source_labels(self):
        search_source_url = self._card_search_data_source.site_source_url
        if search_source_url is not None:
            self.search_source_label.setText(f'Search source: <a href="{search_source_url}">{self._card_search_data_source.source_display_name}</a>')
        else:
            self.search_source_label.setText(f'Search source: {self._card_search_data_source.source_display_name}')
            
        image_source_display_name = self._card_image_source_provider.card_image_source.site_source_identifier
        image_source_url = self._card_image_source_provider.card_image_source.site_source_url
        self.image_source_label.setText(f'Image source: <a href="{image_source_url}">{image_source_display_name}</a>')
    
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
                # TODO: may need more specific check
                swu_search_config = SWUDBAPISearchConfiguration.from_search_configuration(event.search_configuration)
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
            self._is_config_updating = True
            self._load_list()
            self._is_config_updating = False
            
            self._load_source_labels()
            
        if type(event) == LocalResourceFetchEvent:
            self._sync_retry_button()
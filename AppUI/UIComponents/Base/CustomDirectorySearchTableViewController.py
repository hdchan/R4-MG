from typing import Optional
from urllib.error import HTTPError

from PyQt5.QtWidgets import (QHBoxLayout, QLabel, QLineEdit, QListWidget,
                             QPushButton, QVBoxLayout, QWidget)

from AppCore.Config import Configuration
from AppCore.CustomDirectorySearch.CustomDirectorySearchDataSource import (
    CustomDirectorySearchDataSource, CustomDirectorySearchDataSourceDelegate)
from AppCore.Data.CardSearchDataSource import *
from AppCore.Models import LocalCardResource, SearchConfiguration
from AppCore.Observation import *
from AppCore.Observation.Events import (ConfigurationUpdatedEvent,
                                        LocalResourceFetchEvent, SearchEvent)
from AppUI.AppDependencyProviding import AppDependencyProviding

from ...Observation.Events import KeyboardEvent
from ..Base.ImagePreviewViewController import ImagePreviewViewController
from .LoadingSpinner import LoadingSpinner


# TODO: add pagination
class CustomDirectorySearchTableViewController(QWidget, TransmissionReceiverProtocol, CustomDirectorySearchDataSourceDelegate):
    def __init__(self, 
                 app_dependency_provider: AppDependencyProviding,
                 image_preview_view: ImagePreviewViewController):
        super().__init__()
        self._image_preview_view = image_preview_view
        self._card_image_source_provider = app_dependency_provider.image_source_provider
        self._observation_tower = app_dependency_provider.observation_tower
        self._card_search_data_source = CustomDirectorySearchDataSource(app_dependency_provider)
        self._card_search_data_source.delegate = self
        
        self._configuration_manager = app_dependency_provider.configuration_manager

        layout = QVBoxLayout()
        self.setLayout(layout)
        
        
        query_layout = QHBoxLayout()
        query_layout.setContentsMargins(0, 0, 0, 0)
        query_widget = QWidget()
        query_widget.setLayout(query_layout)
        layout.addWidget(query_widget)
        
        card_name_search_bar = QLineEdit(self)
        card_name_search_bar.setPlaceholderText("Lookup by card name (Ctrl+L)")
        self.card_name_search_bar = card_name_search_bar
        query_layout.addWidget(card_name_search_bar, 1)
        
        result_list = QListWidget()
        result_list.itemSelectionChanged.connect(self.get_selection)
        result_list.itemClicked.connect(self.get_selection)
        self.result_list = result_list
        layout.addWidget(result_list, 1)
        
        
        search_button = QPushButton()
        search_button.clicked.connect(self.search)
        self.search_button = search_button
        self._sync_search_button_text()
        layout.addWidget(search_button)
        
        
        search_source_label = QLabel()
        search_source_label.linkActivated.connect(self._handle_link_activated)
        layout.addWidget(search_source_label)
        self.search_source_label = search_source_label

        self._load_source_labels()
        
        
        self._loading_spinner = LoadingSpinner(self)
        
        
        app_dependency_provider.observation_tower.subscribe_multi(self, [SearchEvent,
                                                                         KeyboardEvent,
                                                                         ConfigurationUpdatedEvent, 
                                                                         LocalResourceFetchEvent]) 
        
        app_dependency_provider.shortcut_action_coordinator.bind_focus_search(self._set_search_focus, self)
        app_dependency_provider.shortcut_action_coordinator.bind_reset_search(self._reset_search, self)
        app_dependency_provider.shortcut_action_coordinator.bind_search(self.search, self)
        
        self._sync_ui()
    
    @property
    def _configuration(self) -> Configuration:
        return self._configuration_manager.configuration
    
    def ds_completed_search_with_result(self, 
                                        ds: CustomDirectorySearchDataSource,
                                        error: Optional[Exception]):
        status = "🟢 OK"
        if error is not None:
            if isinstance(error, HTTPError):
                status = f"🔴 {error.code}"
            else:
                status = str(error)
        self._load_list()
        self._load_source_labels(status_string=status)

    def ds_did_retrieve_card_resource_for_card_selection(self, 
                                                         ds: CustomDirectorySearchDataSource, 
                                                         local_resource: LocalCardResource):
        self._image_preview_view.set_image(local_resource)

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

    def set_item_active(self, index: int):
        self.result_list.setCurrentRow(index)

    def search(self):
        self._search()

    def _search(self, config_modifier: ... = None):
        # prevent query errors
        stripped_text = self.card_name_search_bar.text().strip()
        self.card_name_search_bar.setText(stripped_text)
        
        search_configuration = SearchConfiguration()
        search_configuration.card_name = stripped_text
                
        if config_modifier is not None:
            search_configuration = config_modifier(search_configuration)
        
        self._card_search_data_source.search(search_configuration)
        
    def _load_list(self):
        selected_indexs = self.result_list.selectedIndexes()
        selected_index = 0
        if len(selected_indexs) > 0:
            selected_index = selected_indexs[0].row()

        trading_cards = self._card_search_data_source.trading_cards
        self.result_list.clear()
        for i in trading_cards:
            display_name = i.friendly_display_name
            self.result_list.addItem(display_name)
        
        self.set_item_active(selected_index)
        self._set_search_components_enabled(True)
            

    def _set_search_components_enabled(self, is_on: bool):
        self.card_name_search_bar.setEnabled(is_on)
        self.search_button.setEnabled(is_on)
        if is_on:
            self._loading_spinner.stop()
        else:
            self._loading_spinner.start()
            
    def _sync_ui(self):
        pass

    def _load_source_labels(self, status_string: str = ""):
        self.search_source_label.setText(f'Search source: <a href="#open-directory">{self._card_search_data_source.source_display_name}</a> {status_string}')
    
    def _handle_link_activated(self, link: str):
        if link == "#open-directory":
            self._card_search_data_source.open_directory_path()
    
    def _sync_search_button_text(self):
        self.search_button.setText("Search (Enter)")
        
    def handle_observation_tower_event(self, event: TransmissionProtocol):
        # if type(event) == SearchEvent:
        #     if event.event_type == SearchEvent.EventType.STARTED:
        #         self._set_search_components_enabled(False)
        #         self.card_name_search_bar.setText(event.search_configuration.card_name)

        #     elif event.event_type == SearchEvent.EventType.FINISHED:
        #         self._set_search_components_enabled(True)
        #         if self.result_list.count() > 0:
        #             self.set_item_active(0)

        #     if event.seconds_since_predecessor is not None:
        #         print(f"Search took :{event.seconds_since_predecessor}s")
                    
        if type(event) == KeyboardEvent:
            self._sync_search_button_text()

        if type(event) == ConfigurationUpdatedEvent:
            self._load_source_labels()
            self._sync_ui()
from typing import Optional
from PyQt5.QtCore import QSize
from PyQt5.QtWidgets import (QHBoxLayout, QLabel, QLineEdit, QListWidget,
                             QPushButton, QVBoxLayout, QWidget, QSizePolicy)

from AppCore.Config import Configuration
from AppCore.DataSource.DataSourceCustomDirectorySearch import (
    CustomDirectorySearchDataSource, CustomDirectorySearchDataSourceDelegate)
from AppCore.DataSource.DataSourceCardSearch import *
from AppCore.Models import LocalCardResource, SearchConfiguration
from AppCore.Observation import *
from AppCore.Observation.Events import (ConfigurationUpdatedEvent,
                                        LocalCardResourceFetchEvent, CardSearchEvent)
from AppUI.AppDependenciesProviding import AppDependenciesProviding
from AppUI.Observation.Events import KeyboardEvent

from ..Base.ImagePreviewViewController import ImagePreviewViewController
from .LoadingSpinner import LoadingSpinner


class CustomDirectorySearchTableViewController(QWidget, TransmissionReceiverProtocol, CustomDirectorySearchDataSourceDelegate):
    def __init__(self, 
                 app_dependencies_provider: AppDependenciesProviding,
                 image_preview_view: ImagePreviewViewController):
        super().__init__()
        self._image_preview_view = image_preview_view
        self._observation_tower = app_dependencies_provider.observation_tower
        self._router = app_dependencies_provider.router
        self._card_search_data_source = app_dependencies_provider.new_instance_custom_directory_search_data_source(self)
        
        self._configuration_manager = app_dependencies_provider.configuration_manager

        layout = QVBoxLayout()
        self.setLayout(layout)
        
        
        query_layout = QHBoxLayout()
        query_layout.setContentsMargins(0, 0, 0, 0)
        query_widget = QWidget()
        query_widget.setLayout(query_layout)
        layout.addWidget(query_widget)
        
        card_name_search_bar = QLineEdit(self)
        card_name_search_bar.setPlaceholderText("Lookup by file name (Ctrl+L)")
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
        # TODO: need to account for long labels else where
        search_source_label.setMinimumSize(QSize(1, 1))
        search_source_label.setSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.Preferred)
        search_source_label.linkActivated.connect(self._handle_link_activated)
        layout.addWidget(search_source_label)
        self.search_source_label = search_source_label

        self._load_source_labels()
        
        
        self._loading_spinner = LoadingSpinner(self)
        
        
        app_dependencies_provider.observation_tower.subscribe_multi(self, [CardSearchEvent,
                                                                         KeyboardEvent,
                                                                         ConfigurationUpdatedEvent, 
                                                                         LocalCardResourceFetchEvent]) 
        
        app_dependencies_provider.shortcut_action_coordinator.bind_focus_search(self._set_search_focus, self)
        app_dependencies_provider.shortcut_action_coordinator.bind_reset_search(self._reset_search, self)
        app_dependencies_provider.shortcut_action_coordinator.bind_search(self.search, self)
        
        self._sync_ui()
    
    @property
    def _configuration(self) -> Configuration:
        return self._configuration_manager.configuration
    
    def ds_completed_search_with_result(self, 
                                        ds: CustomDirectorySearchDataSource,
                                        search_configuration: SearchConfiguration,
                                        error: Optional[Exception]):
        status = "🟢 OK"
        if error is not None:
            status = f"🔴 {error}"
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

        trading_cards = self._card_search_data_source.resource_display_names
        self.result_list.clear()
        for i in trading_cards:
            self.result_list.addItem(i)
        
        self.result_list.addItem('No more results')
        
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
            try:
                self._card_search_data_source.open_directory_path()
            except Exception as error:
                self._router.show_error(error)
    
    def _sync_search_button_text(self):
        self.search_button.setText("Search (Enter)")
        
    def handle_observation_tower_event(self, event: TransmissionProtocol):
        if type(event) == CardSearchEvent:
            if event.event_type == CardSearchEvent.EventType.STARTED:
                self._set_search_components_enabled(False)

            elif event.event_type == CardSearchEvent.EventType.FINISHED:
                self._set_search_components_enabled(True)

            if event.seconds_since_predecessor is not None and event.source_type is CardSearchEvent.SourceType.LOCAL:
                print(f"Custom search took :{event.seconds_since_predecessor}s")
                    
        if type(event) == KeyboardEvent:
            self._sync_search_button_text()

        if type(event) == ConfigurationUpdatedEvent:
            self._load_source_labels()
            self._sync_ui()
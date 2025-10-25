from typing import Optional
from urllib.error import HTTPError

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QSizePolicy

from AppCore.Config import Configuration
from AppCore.Models import (DataSourceSelectedLocalCardResourceProtocol,
                                LocalResourceDataSourceProviding)
from AppCore.DataSource.DataSourceCardSearch import *
from AppCore.Models import SearchConfiguration
from AppCore.Observation import *
from AppCore.Observation.Events import (CardSearchEvent,
                                        ConfigurationUpdatedEvent,
                                        LocalCardResourceFetchEvent)
from AppUI.AppDependenciesInternalProviding import \
    AppDependenciesInternalProviding
from AppUI.Observation.Events import KeyboardEvent
from R4UI import Label, RWidget, VerticalBoxLayout

from .SearchTableComboViewController import (
    SearchTableComboViewController, SearchTableComboViewControllerDelegate)


class SearchTableViewControllerDelegate:
    def stvc_did_retrieve_card(self) -> None:
        return

class SearchTableViewController(RWidget, 
                                TransmissionReceiverProtocol, 
                                DataSourceCardSearchDelegate, 
                                SearchTableComboViewControllerDelegate, 
                                LocalResourceDataSourceProviding, 
                                DataSourceSelectedLocalCardResourceProtocol):
    
    class SearchTableViewControllerConfiguration:
        def __init__(self,
                     search_history_identifier: Optional[str] = None,
                     search_history_page_size: Optional[int] = None, 
                     is_flip_button_hidden: bool = False):
            self.is_flip_button_hidden = is_flip_button_hidden
            self.search_history_identifier = search_history_identifier
            self.search_history_page_size = search_history_page_size
    
    def __init__(self,
                 app_dependencies_provider: AppDependenciesInternalProviding,
                 search_table_view_controller_config: SearchTableViewControllerConfiguration = SearchTableViewControllerConfiguration()):
        super().__init__()
        self._search_table_view_controller_config = search_table_view_controller_config
        ds_configuration = DataSourceCardSearch.DataSourceCardSearchConfiguration(search_table_view_controller_config.search_history_identifier, 
                                                                                  search_table_view_controller_config.search_history_page_size)
        self._card_search_data_source = app_dependencies_provider.new_instance_card_search_data_source(delegate=self,  
                                                                                                     search_client_provider=app_dependencies_provider.search_client_provider, 
                                                                                                     ds_configuration=ds_configuration)
        self._observation_tower = app_dependencies_provider.observation_tower
        self._router = app_dependencies_provider.router

        self.delegate: Optional[SearchTableViewControllerDelegate] = None
        
        self._shift_pressed = False
        self._ctrl_pressed = False
        self._configuration_manager = app_dependencies_provider.configuration_manager

        layout = VerticalBoxLayout().set_layout_to_widget(self)
        search_table_combo_view = SearchTableComboViewController(app_dependencies_provider, self)
        layout.add_widget(search_table_combo_view)
        self._search_table_combo_view = search_table_combo_view
    
        search_source_label = Label()
        # TODO: need to account for long labels else where
        search_source_label.setSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.Preferred)
        layout.add_widget(search_source_label)
        search_source_label.linkActivated.connect(self._handle_link_activated)
        self.search_source_label = search_source_label

        self._load_source_labels()
        
        # self._search_table_combo_view.set_card_type_filter(None)
        
        self._search_table_combo_view.sync_ui()
        
        app_dependencies_provider.observation_tower.subscribe_multi(self, [CardSearchEvent,
                                                                         KeyboardEvent,
                                                                         ConfigurationUpdatedEvent, 
                                                                         LocalCardResourceFetchEvent]) 
        
        app_dependencies_provider.shortcut_action_coordinator.bind_flip(self._flip_card, self)
        app_dependencies_provider.shortcut_action_coordinator.bind_focus_search(self._search_table_combo_view.set_search_focus, self)
        app_dependencies_provider.shortcut_action_coordinator.bind_reset_search(self._search_table_combo_view.reset_search, self)
        app_dependencies_provider.shortcut_action_coordinator.bind_search(self._search, self)
        app_dependencies_provider.shortcut_action_coordinator.bind_search_leader(self._search_secondary, self)
        app_dependencies_provider.shortcut_action_coordinator.bind_search_base(self._search_tertiary, self)
    
    @property
    def card_search_data_source(self) -> DataSourceCardSearch:
        return self._card_search_data_source
    
    @property
    def _configuration(self) -> Configuration:
        return self._configuration_manager.configuration

    def get_selection(self):
        self._search_table_combo_view.get_selection()

    def _search(self):
        self._card_search_data_source.search(self._search_table_combo_view.search_configuration)

    def _search_secondary(self):
        configuration = self._search_table_combo_view.secondary_search_configuration
        if configuration is None:
            return
        self._card_search_data_source.search(configuration)

    def _search_tertiary(self):
        configuration = self._search_table_combo_view.tertiary_search_configuration
        if configuration is None:
            return
        self._card_search_data_source.search(configuration)

    def _load_source_labels(self, status_string: str = ""):
        search_source_url = self._card_search_data_source.site_source_url
        if search_source_url is not None:
            self.search_source_label.setOpenExternalLinks(True)
            self.search_source_label.setText(f'Search source: <a href="{search_source_url}">{self._card_search_data_source.source_display_name}</a> {status_string}')
        elif self._configuration.search_source == Configuration.Settings.SearchSource.LOCALLY_MANAGED_DECKS:
            self.search_source_label.setOpenExternalLinks(False)
            self.search_source_label.setText(f'Search source: <a href="{self.LinkKey.LOCALLY_MANAGED_DECKS}">{self._card_search_data_source.source_display_name}</a> {status_string}')
        else:
            self.search_source_label.setText(f'Search source: {self._card_search_data_source.source_display_name} {status_string}')
    
    class LinkKey:
        LOCALLY_MANAGED_DECKS = '#locally-managed-decks'
    
    def _handle_link_activated(self, link: str):
            if link == self.LinkKey.LOCALLY_MANAGED_DECKS:
                self._router.open_manage_deck_list_page()
    
    def _flip_card(self):
        self._card_search_data_source.flip_current_previewed_card()

    # MARK: - DataSourceCardSearchDelegate
    def ds_started_search_with_result(self,
                                      ds: DataSourceCardSearch,
                                      search_configuration: SearchConfiguration):
        self._search_table_combo_view.set_search_components_enabled(False)
        self._search_table_combo_view.set_configuration(search_configuration)

    def ds_completed_search_with_result(self, 
                                        ds: DataSourceCardSearch,
                                        search_configuration: SearchConfiguration,
                                        error: Optional[Exception], 
                                        is_initial_load: bool):
        try:
            status = "🟢 OK"
            if error is not None:
                if isinstance(error, HTTPError):
                    status = f"🔴 {error.code}"
                else:
                    status = f"🔴 {error}"
            self._search_table_combo_view.load_list(is_initial_load)
            self._load_source_labels(status_string=status)

            self._search_table_combo_view.set_search_components_enabled(True)
            self._search_table_combo_view.set_item_active(0)
        except Exception as error:
            print(error)

    def ds_did_retrieve_card_resource_for_card_selection(self, 
                                                         ds: DataSourceCardSearch):
        if self._card_search_data_source.current_selected_card_search_resource is not None:
            if self.delegate is not None:
                self.delegate.stvc_did_retrieve_card()
        self._search_table_combo_view.sync_ui()
            
        
    # MARK: - SearchTableComboViewControllerDelegate
    @property
    def stc_history_list(self) -> List[str]:
        return self._card_search_data_source.search_list_history_display
    
    def stc_did_select_history(self, stc: SearchTableComboViewController, index: int):
        # set search parameters
        result = self._card_search_data_source.get_search_configuration_from_history(index)
        if result is not None:
            search_configuration, _ = result
            self._search_table_combo_view.set_configuration(search_configuration)
            stc.reset_search_history()

    @property
    def stc_search_button_text(self) -> str:
        if self._ctrl_pressed and self._shift_pressed:
            return "Only Ctrl OR Shift can be held to search"
        elif self._ctrl_pressed:
            return 'Search Leader (Ctrl + Enter)'
        elif self._shift_pressed:
            return 'Search Base (Shift + Enter)'
        else:
            return "Search (Enter)"
            
    @property
    def stc_is_flippable(self) -> bool:
        return self._card_search_data_source.current_previewed_trading_card_is_flippable
    
    @property
    def stc_flip_button_text(self) -> str:
        return "Flip (Ctrl+F)"

    def stc_tapped_flip_button(self, stc: SearchTableComboViewController):
        self._flip_card()
        
    @property
    def stc_has_more_pages(self) -> bool:
        return self._card_search_data_source.has_more_pages
    
    @property
    def stc_list_items(self) -> list[str]:
        return self._card_search_data_source.trading_card_display_names
    
    def stc_select_card_resource_for_card_selection(self, stc: SearchTableComboViewController, index: int) -> None:
        self._card_search_data_source.select_card_resource_for_card_selection(index)
    
    def stc_result_list_scrolled(self, stc: SearchTableComboViewController, value: int) -> None:
        self._card_search_data_source.load_next_page()
    
    def stc_did_click_search(self, stc: SearchTableComboViewController) -> None:
        self._search()
    
    @property
    def stc_is_flip_button_hidden(self) -> bool:
        return self._search_table_view_controller_config.is_flip_button_hidden

    @property
    def stc_is_history_dropdown_hidden(self) -> bool:
        return self._search_table_view_controller_config.search_history_identifier is None

    # MARK: - LocalResourceDataSourceProviding, DataSourceSelectedLocalCardResourceProtocol
    @property
    def data_source(self) -> DataSourceSelectedLocalCardResourceProtocol:
        return self
    
    @property
    def selected_local_resource(self) -> Optional[LocalCardResource]:
        return self._card_search_data_source.current_selected_card_search_resource

    # MARK: - Observation Tower
    def handle_observation_tower_event(self, event: TransmissionProtocol):
        if type(event) == CardSearchEvent:
            if event.source_type is not CardSearchEvent.SourceType.REMOTE:
                return # dont'process local searches
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
            self._search_table_combo_view.sync_ui()

        if type(event) == ConfigurationUpdatedEvent:
            self._load_source_labels()
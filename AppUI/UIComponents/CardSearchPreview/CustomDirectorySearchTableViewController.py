from typing import Optional, List

from PySide6.QtCore import QSize
from PySide6.QtWidgets import (QHBoxLayout, QLineEdit, QListWidget,
                               QPushButton, QSizePolicy, QVBoxLayout, QWidget)

from AppCore.Config import Configuration
from AppCore.DataSource.DataSourceCustomDirectorySearch import (
    CustomDirectorySearchDataSource, CustomDirectorySearchDataSourceDelegate)
from AppCore.Models import (DataSourceSelectedLocalCardResourceProtocol,
                            LocalCardResource, SearchConfiguration)
from AppCore.Observation import (TransmissionProtocol,
                                 TransmissionReceiverProtocol)
from AppCore.Observation.Events import (CardSearchEvent,
                                        ConfigurationUpdatedEvent,
                                        LocalCardResourceFetchEvent)
from AppUI.AppDependenciesInternalProviding import \
    AppDependenciesInternalProviding
from AppUI.Observation.Events import KeyboardEvent
from R4UI import Label, RWidget
from .SearchTableComboViewController import (
    SearchTableComboViewController, SearchTableComboViewControllerDelegate)
from R4UI import VerticalBoxLayout

class CustomDirectorySearchTableViewControllerDelegate:
    def cds_did_retrieve_card(self) -> None:
        return
    
class CustomDirectorySearchTableViewController(RWidget, 
                                               TransmissionReceiverProtocol, 
                                               CustomDirectorySearchDataSourceDelegate, 
                                               DataSourceSelectedLocalCardResourceProtocol, 
                                               SearchTableComboViewControllerDelegate):
    def __init__(self, 
                 app_dependencies_provider: AppDependenciesInternalProviding):
        super().__init__()
        self._observation_tower = app_dependencies_provider.observation_tower
        self._router = app_dependencies_provider.router
        self._card_search_data_source = app_dependencies_provider.new_instance_custom_directory_search_data_source(self)
        
        self._configuration_manager = app_dependencies_provider.configuration_manager
        self.delegate: Optional[CustomDirectorySearchTableViewControllerDelegate] = None

        layout = VerticalBoxLayout().set_layout_to_widget(self)
        
        search_table_combo_view = SearchTableComboViewController(self)
        layout.add_widget(search_table_combo_view)
        self._search_table_combo_view = search_table_combo_view
        
        
        search_source_label = Label()
        # TODO: need to account for long labels else where
        search_source_label.setMinimumSize(QSize(1, 1))
        search_source_label.setSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.Preferred)
        search_source_label.linkActivated.connect(self._handle_link_activated)
        layout.add_widget(search_source_label)
        self.search_source_label = search_source_label

        self._load_source_labels()

        self._search_table_combo_view.sync_ui()
        
        app_dependencies_provider.observation_tower.subscribe_multi(self, [CardSearchEvent,
                                                                         KeyboardEvent,
                                                                         ConfigurationUpdatedEvent, 
                                                                         LocalCardResourceFetchEvent]) 
        
        app_dependencies_provider.shortcut_action_coordinator.bind_focus_search(self._search_table_combo_view.set_search_focus, self)
        app_dependencies_provider.shortcut_action_coordinator.bind_reset_search(self._search_table_combo_view.reset_search, self)
        app_dependencies_provider.shortcut_action_coordinator.bind_search(self.search, self)
        
    
    @property
    def data_source(self) -> DataSourceSelectedLocalCardResourceProtocol:
        return self._card_search_data_source
    
    @property
    def _configuration(self) -> Configuration:
        return self._configuration_manager.configuration
    
    # MARK: - CustomDirectorySearchDataSourceDelegate

    def ds_completed_search_with_result(self, 
                                        ds: CustomDirectorySearchDataSource,
                                        search_configuration: SearchConfiguration,
                                        error: Optional[Exception]):
        try:
            status = "🟢 OK"
            if error is not None:
                status = f"🔴 {error}"
            self._search_table_combo_view.load_list()
            self._search_table_combo_view.set_item_active(0)
            self._load_source_labels(status_string=status)
        except Exception as error:
            print(error)

    def ds_did_retrieve_card_resource_for_card_selection(self, 
                                                         ds: CustomDirectorySearchDataSource, 
                                                         local_resource: LocalCardResource):
        if self.delegate is not None:
            self.delegate.cds_did_retrieve_card()

    # MARK: - SearchTableComboViewControllerDelegate
    def stc_select_card_resource_for_card_selection(self, stc: 'SearchTableComboViewController', index: int) -> None:
        self._card_search_data_source.select_card_resource_for_card_selection(index)
    
    def stc_did_click_search(self, stc: 'SearchTableComboViewController') -> None:
        self._search()
    
    @property
    def stc_list_items(self) -> List[str]:
        return self._card_search_data_source.resource_display_names

    @property
    def stc_search_button_text(self) -> str:
        return "Search (Enter)"

    def search(self):
        self._search()

    def _search(self, config_modifier: ... = None):
        self._card_search_data_source.search(self._search_table_combo_view.search_configuration)

    def _load_source_labels(self, status_string: str = ""):
        self.search_source_label.setText(f'Search source: <a href="#open-directory">{self._card_search_data_source.source_display_name}</a> {status_string}')
    
    def _handle_link_activated(self, link: str):
        if link == "#open-directory":
            try:
                self._card_search_data_source.open_directory_path()
            except Exception as error:
                self._router.show_error(error)
        
    def handle_observation_tower_event(self, event: TransmissionProtocol):
        if type(event) is CardSearchEvent:
            if event.event_type == CardSearchEvent.EventType.STARTED:
                self._search_table_combo_view.set_search_components_enabled(False)

            elif event.event_type == CardSearchEvent.EventType.FINISHED:
                self._search_table_combo_view.set_search_components_enabled(True)

            if event.seconds_since_predecessor is not None and event.source_type is CardSearchEvent.SourceType.LOCAL:
                print(f"Custom search took :{event.seconds_since_predecessor}s")
                    
        if type(event) is KeyboardEvent:
            self._search_table_combo_view.sync_ui()


        if type(event) is ConfigurationUpdatedEvent:
            self._load_source_labels()
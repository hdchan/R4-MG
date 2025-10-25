from typing import Optional

from PySide6.QtWidgets import QListWidget, QListWidgetItem

from AppCore.DataSource.DataSourceCachedHistory import DataSourceCachedHistory
from AppCore.Models import (DataSourceSelectedLocalCardResourceProtocol,
                            LocalCardResource,
                            LocalResourceDataSourceProviding)
from AppCore.Observation import *
from AppCore.Observation.Events import (
    LocalCardResourceSelectedFromDataSourceEvent,
    CacheHistoryUpdatedEvent)
from AppUI.AppDependenciesInternalProviding import \
    AppDependenciesInternalProviding
from R4UI import RWidget, VerticalBoxLayout


class CacheHistoryTableViewControllerDelegate:
    def ch_did_retrieve_card(self) -> None:
        return

class CacheHistoryTableViewController(RWidget, 
                                        TransmissionReceiverProtocol,
                                        DataSourceSelectedLocalCardResourceProtocol, 
                                        LocalResourceDataSourceProviding):
    def __init__(self, 
                 app_dependencies_provider: AppDependenciesInternalProviding, 
                 cache_history_data_source: DataSourceCachedHistory):
        super().__init__()
        self._observation_tower = app_dependencies_provider.observation_tower
        self._cache_history_data_source = cache_history_data_source
        self._string_formatter = app_dependencies_provider.string_formatter
        self.delegate: Optional[CacheHistoryTableViewControllerDelegate] = None
        
        self._container = VerticalBoxLayout().set_layout_to_widget(self)
        
        self._history_list = QListWidget()
        self._history_list.itemSelectionChanged.connect(self.get_selection)
        self._container.add_widget(self._history_list)
        
        self._observation_tower.subscribe_multi(self, [CacheHistoryUpdatedEvent, 
                                                       LocalCardResourceSelectedFromDataSourceEvent])
    
        self._update_history_list()

    def append_widget(self, widget: RWidget):
        self._container.add_widget(widget)

    @property
    def data_source(self) -> DataSourceSelectedLocalCardResourceProtocol:
        return self
    
    @property
    def selected_local_resource(self) -> Optional[LocalCardResource]:
        return self._cache_history_data_source.selected_local_resource
    
    def get_selection(self):
        selected_indexes = self._history_list.selectedIndexes()
        if len(selected_indexes) > 0:
            self._cache_history_data_source.select_card_resource_for_card_selection(selected_indexes[0].row())
    
    def _update_history_list(self):
        self._history_list.clear()
        for r in self._cache_history_data_source.cached_resources_history:
            item = QListWidgetItem(f'{self._string_formatter.format_date(r[1])} - {r[0].display_name}')
            item.setToolTip(f'{r[1].strftime("%m/%d/%Y, %I:%M %p")}')
            self._history_list.addItem(item)
    
    def handle_observation_tower_event(self, event: TransmissionProtocol):
        if type(event) == CacheHistoryUpdatedEvent:
            self._update_history_list()

        if type(event) == LocalCardResourceSelectedFromDataSourceEvent:
            if event.datasource == self._cache_history_data_source:
                if self.delegate is not None:
                    self.delegate.ch_did_retrieve_card()
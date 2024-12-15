from PyQt5.QtWidgets import QListWidget, QVBoxLayout, QWidget, QPushButton, QListWidgetItem

from AppCore.Data.RecentSearchDataSource import RecentSearchDataSource
from AppCore.Observation import *
from AppCore.Observation.Events import SearchEvent
from AppUI.AppDependencyProviding import AppDependencyProviding
from AppUI.Clients.SWUDB import SWUDBAPISearchConfiguration
from AppCore.Data.CardSearchDataSource import CardSearchDataSource

class SearchHistoryTableViewController(QWidget, TransmissionReceiverProtocol):
    def __init__(self, 
                 app_dependency_provider: AppDependencyProviding,
                 recent_search_data_source: RecentSearchDataSource, 
                 card_search_data_source: CardSearchDataSource):
        super().__init__()
        self._observation_tower = app_dependency_provider.observation_tower
        self._recent_search_data_source = recent_search_data_source
        self._card_search_data_source = card_search_data_source
        self._string_formatter = app_dependency_provider.string_formatter
        
        recent_search_layout = QVBoxLayout()
        self.setLayout(recent_search_layout)
        
        self._recent_search_list = QListWidget()
        self._recent_search_list.itemSelectionChanged.connect(self._selection_changed)
        recent_search_layout.addWidget(self._recent_search_list)
        
        self._search_button = QPushButton()
        self._search_button.setText('Search (Enter)')
        self._search_button.setEnabled(False)
        self._search_button.clicked.connect(self._perform_search)
        recent_search_layout.addWidget(self._search_button)
        
        self._observation_tower.subscribe(self, SearchEvent)
        
        app_dependency_provider.shortcut_action_coordinator.bind_search(self._perform_search, self)
    
        self._update_recent_search_list()

    def set_active(self):
        self._update_recent_search_list()

    def _update_recent_search_list(self):
        self._recent_search_list.clear()
        for r in self._recent_search_data_source.search_list_history:
            swu_search_config = SWUDBAPISearchConfiguration.from_search_configuration(r[0])
            item = QListWidgetItem(f'{self._string_formatter.format_date(r[1])} - Name: "{swu_search_config.card_name}", Type: {swu_search_config.card_type.value}')
            item.setToolTip(f'{r[1].strftime("%m/%d/%Y, %I:%M %p")}')
            self._recent_search_list.addItem(item)
            self._recent_search_list.setCurrentItem(self._recent_search_list.item(0))
        
    def _selection_changed(self):
        # self._search_button.setEnabled(index >= 0)
        selected_indexs = self._recent_search_list.selectedIndexes()
        if len(selected_indexs) > 0:
            index = selected_indexs[0].row()
            self._search_button.setEnabled(index >= 0)
    
    def _perform_search(self):
        index = self._recent_search_list.currentIndex()
        if index.row() >= 0:
            search_config = self._recent_search_data_source.search_list_history[index.row()][0]
            self._card_search_data_source.search(search_config)
    
    def handle_observation_tower_event(self, event: TransmissionProtocol):
        if type(event) == SearchEvent:
            self._update_recent_search_list()
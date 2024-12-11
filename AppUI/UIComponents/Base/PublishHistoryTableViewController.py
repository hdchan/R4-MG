from PyQt5.QtWidgets import QListWidget, QVBoxLayout, QWidget

from AppCore.Data.RecentPublishedDataSource import RecentPublishedDataSource
from AppCore.Observation import *
from AppCore.Observation.Events import PublishStagedResourcesEvent
from AppUI.AppDependencyProviding import AppDependencyProviding


class PublishHistoryTableViewController(QWidget, TransmissionReceiverProtocol):
    def __init__(self, 
                 app_dependency_provider: AppDependencyProviding, 
                 recent_published_data_source: RecentPublishedDataSource):
        super().__init__()
        
        self._observation_tower = app_dependency_provider.observation_tower
        self._recent_published_data_source = recent_published_data_source
        
        history_layout = QVBoxLayout()
        self.setLayout(history_layout)
        
        self._history_list = QListWidget()
        history_layout.addWidget(self._history_list)
        
        self._observation_tower.subscribe_multi(self, [PublishStagedResourcesEvent])
    
    def _update_history_list(self):
        self._history_list.clear()
        for r in reversed(self._recent_published_data_source.published_resources_history):
            self._history_list.addItem(f'{r[1].strftime("%m/%d/%Y, %H:%M:%S")} - {r[0].display_name}')
    
    def handle_observation_tower_event(self, event: TransmissionProtocol):
        if type(event) == PublishStagedResourcesEvent:
            self._update_history_list()
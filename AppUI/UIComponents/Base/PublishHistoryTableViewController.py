from PyQt5.QtWidgets import QListWidget, QVBoxLayout, QWidget

from AppCore.Data.RecentPublishedDataSource import *
from AppCore.Observation import *
from AppCore.Observation.Events import PublishStagedResourcesEvent
from AppUI.AppDependencyProviding import AppDependencyProviding

from ..Base.ImagePreviewViewController import ImagePreviewViewController


class PublishHistoryTableViewController(QWidget, TransmissionReceiverProtocol, RecentPublishedDataSourceDelegate):
    def __init__(self, 
                 app_dependency_provider: AppDependencyProviding, 
                 recent_published_data_source: RecentPublishedDataSource, 
                 image_preview_view: ImagePreviewViewController):
        super().__init__()
        self._image_preview_view = image_preview_view
        self._observation_tower = app_dependency_provider.observation_tower
        self._recent_published_data_source = recent_published_data_source
        recent_published_data_source.delegate = self
        
        history_layout = QVBoxLayout()
        self.setLayout(history_layout)
        
        self._history_list = QListWidget()
        self._history_list.itemSelectionChanged.connect(self.get_selection)
        history_layout.addWidget(self._history_list)
        
        self._observation_tower.subscribe_multi(self, [PublishStagedResourcesEvent])
    
    def set_active(self):
        local_resource = self._recent_published_data_source.selected_local_resource
        if local_resource is not None:
            self._image_preview_view.set_image(local_resource)
            self._observation_tower.notify(LocalResourceSelectedEvent(local_resource)) # rework?
    
    def rp_did_retrieve_card_resource_for_card_selection(self, ds: ..., local_resource: LocalCardResource) -> None:
        self.set_active()
    
    def get_selection(self):
        selected_indexs = self._history_list.selectedIndexes()
        if len(selected_indexs) > 0:
            self._recent_published_data_source.select_card_resource_for_card_selection(selected_indexs[0].row())
    
    def _update_history_list(self):
        self._history_list.clear()
        for r in self._recent_published_data_source.published_resources_history:
            self._history_list.addItem(f'{r[1].strftime("%m/%d/%Y, %I:%M %p")} - {r[0].display_name}')
    
    def handle_observation_tower_event(self, event: TransmissionProtocol):
        if type(event) == PublishStagedResourcesEvent:
            self._update_history_list()
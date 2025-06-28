from PyQt5.QtWidgets import QListWidget, QVBoxLayout, QWidget, QListWidgetItem

from AppCore.DataSource.DataSourceRecentPublished import *
from AppCore.Observation import *
from AppCore.Observation.Events import PublishStagedCardResourcesEvent
from AppUI.AppDependenciesProviding import AppDependenciesProviding

from ..Base.ImagePreviewViewController import ImagePreviewViewController

class PublishHistoryTableViewController(QWidget, TransmissionReceiverProtocol, DataSourceRecentPublishedDelegate):
    def __init__(self, 
                 app_dependencies_provider: AppDependenciesProviding, 
                 recent_published_data_source: DataSourceRecentPublished, 
                 image_preview_view: ImagePreviewViewController):
        super().__init__()
        self._image_preview_view = image_preview_view
        self._observation_tower = app_dependencies_provider.observation_tower
        self._recent_published_data_source = recent_published_data_source
        self._string_formatter = app_dependencies_provider.string_formatter
        recent_published_data_source.delegate = self
        
        history_layout = QVBoxLayout()
        self.setLayout(history_layout)
        
        self._history_list = QListWidget()
        self._history_list.itemSelectionChanged.connect(self.get_selection)
        history_layout.addWidget(self._history_list)
        
        self._observation_tower.subscribe_multi(self, [PublishStagedCardResourcesEvent])
    
        self._update_history_list()

    def set_active(self):
        local_resource = self._recent_published_data_source.selected_local_resource
        if local_resource is not None:
            self._image_preview_view.set_image(local_resource)

        # self._update_history_list()
    
    def rp_did_retrieve_card_resource_for_card_selection(self, ds: ..., local_resource: LocalCardResource) -> None:
        self.set_active()
    
    def get_selection(self):
        selected_indexs = self._history_list.selectedIndexes()
        if len(selected_indexs) > 0:
            self._recent_published_data_source.select_card_resource_for_card_selection(selected_indexs[0].row())
    
    def _update_history_list(self):
        self._history_list.clear()
        for r in self._recent_published_data_source.published_resources_history:
            item = QListWidgetItem(f'{self._string_formatter.format_date(r[1])} - {r[0].display_name}')
            item.setToolTip(f'{r[1].strftime("%m/%d/%Y, %I:%M %p")}')
            self._history_list.addItem(item)
    
    def handle_observation_tower_event(self, event: TransmissionProtocol):
        if type(event) == PublishStagedCardResourcesEvent:
            self._update_history_list()
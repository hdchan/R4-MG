from PyQt5.QtWidgets import QWidget

from AppCore.DataSource import DataSourceDraftList
from AppCore.Observation import *
from AppCore.Observation.Events import LocalAssetResourceFetchEvent
from PyQtUI import HorizontalBoxLayout, VerticalBoxLayout


class DraftListImagePreviewViewController(QWidget, TransmissionReceiverProtocol):
    def __init__(self, 
                 observation_tower: ObservationTower,
                 draft_list_data_source: DataSourceDraftList):
        self._observation_tower = observation_tower
        self._draft_list_data_source = draft_list_data_source
        
        self._observation_tower.subscribe_multi(self, [LocalAssetResourceFetchEvent])
        
        

        HorizontalBoxLayout([
            
            ]).set_layout_to_widget(self)
    
    def _sync_ui(self):
        pass
    
    def handle_observation_tower_event(self, event: TransmissionProtocol) -> None:
        if type(event) == LocalAssetResourceFetchEvent:
            if event.local_resource in self._draft_list_data_source.draft_pack_flat_list:
                self._sync_ui()
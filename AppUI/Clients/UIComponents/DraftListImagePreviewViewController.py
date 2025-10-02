from PIL.ImageQt import ImageQt
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QLabel, QWidget

from AppCore.DataSource import DataSourceDraftList
from AppCore.Observation import *
from AppCore.Observation.Events import LocalAssetResourceFetchEvent
from PyQtUI import HorizontalBoxLayout, VerticalBoxLayout

from ..Models.ParsedDraftList import ParsedDraftList
from ..Utility.DraftListImageGenerator import DraftListImageGenerator


class DraftListImagePreviewViewController(QWidget, TransmissionReceiverProtocol):
    def __init__(self, 
                 observation_tower: ObservationTower,
                 draft_list_data_source: DataSourceDraftList):
        super().__init__()
        self._observation_tower = observation_tower
        self._draft_list_data_source = draft_list_data_source
        
        self._setup_view()
        
        self._observation_tower.subscribe_multi(self, [LocalAssetResourceFetchEvent])
        
    def _setup_view(self):
        self._image_view = QLabel()
        
        HorizontalBoxLayout([
            self._image_view
            ]).set_layout_to_widget(self)
        
        self._sync_ui()
    
    def _sync_ui(self):
        parsed_draft_list = ParsedDraftList(self._draft_list_data_source.draft_packs)
        selected_leader = None
        selected_base = None
        if len(parsed_draft_list.leaders) > 0:
            selected_leader = parsed_draft_list.leaders[0]
        if len(parsed_draft_list.bases) > 0:
            selected_base = parsed_draft_list.bases[0]
        generated_image = DraftListImageGenerator.generate(selected_leader,
                                                           selected_base,
                                                           parsed_draft_list.main_deck,
                                                           [])
        pix = QPixmap()
        qt_image = ImageQt(generated_image)
        pix.fromImage(qt_image)
        self._image_view.setPixmap(pix)
    
    def handle_observation_tower_event(self, event: TransmissionProtocol) -> None:
        if type(event) == LocalAssetResourceFetchEvent:
            if event.local_resource in self._draft_list_data_source.draft_pack_flat_list:
                self._sync_ui()


from io import BytesIO
from typing import Optional, Set, Tuple

from PyQt5.QtCore import (QMutex, QObject, QRunnable, Qt, QThreadPool, QTimer,
                          pyqtSignal)
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QWidget
from PIL import Image
from AppCore.DataSource import DataSourceDraftList
from AppCore.Observation import *
from AppCore.Observation.Events import (DraftListUpdatedEvent,
                                        DraftPackUpdatedEvent,
                                        LocalAssetResourceFetchEvent)
from R4UI import HorizontalBoxLayout, VerticalBoxLayout

from ..Models.ParsedDraftList import ParsedDraftList
from ..Utility.DraftListImageGenerator import DraftListImageGenerator
from .PhotoViewer import PhotoViewerWindow


class DraftListImagePreviewViewController(QWidget, TransmissionReceiverProtocol):
    def __init__(self, 
                 observation_tower: ObservationTower,
                 draft_list_data_source: DataSourceDraftList):
        super().__init__()
        self._observation_tower = observation_tower
        self._draft_list_data_source = draft_list_data_source
        self.pool = QThreadPool()
        self.mutex = QMutex()
        self.working_resources: Set[ParsedDraftList] = set()
        self._main_deck_cols = 6
        
        self._save_async_timer = QTimer()
        self._save_async_timer.setSingleShot(True)
        self._save_async_timer.timeout.connect(self._generate_image)
        self.debounce_time = 1000
        
        self._setup_view()
        
        self._observation_tower.subscribe_multi(self, [LocalAssetResourceFetchEvent, DraftListUpdatedEvent, DraftPackUpdatedEvent])
    
    def _setup_view(self):
        self._image_view = PhotoViewerWindow(self._main_deck_cols, self._col_input_changed)
        
        HorizontalBoxLayout([
            self._image_view
            ]).set_layout_to_widget(self)
        
        self._sync_ui()
    
    def _col_input_changed(self, value: int):
        self._main_deck_cols = value
        self._sync_ui()
    
    def _lock_resource_and_notify(self, local_resource: ParsedDraftList) -> bool:
        if local_resource in self.working_resources:
            return False
        self.mutex.lock()
        self.working_resources.add(local_resource)
        self.mutex.unlock()
        return True
    
    def _unlock_resource_and_notify(self, result: Tuple[QPixmap, QImage, ParsedDraftList, Optional[Exception]]):
        pix_map, qimage, local_resource, _ = result
        if local_resource in self.working_resources:
            self.mutex.lock()
            self.working_resources.remove(local_resource)
            self.mutex.unlock()
            # self._image_view.viewer.setPhoto(pix_map)
            self._image_view.viewer.setPhoto(pix_map, None)
    
    def _sync_ui(self):
        self._save_async_timer.stop()
        self._save_async_timer.start(self.debounce_time)
    
    def _generate_image(self):
        print("Generating image")
        local_resource = ParsedDraftList(self._draft_list_data_source.draft_packs)
        if local_resource.has_cards == False:
            self._image_view.viewer.setPhoto(None)
            return
        if self._lock_resource_and_notify(local_resource):
            # should lock UI incase another job is added
            worker = Worker(local_resource, self._main_deck_cols)
            worker.signals.finished.connect(self._unlock_resource_and_notify)
            self.pool.start(worker)
        
    
    def handle_observation_tower_event(self, event: TransmissionProtocol) -> None:
        if type(event) == LocalAssetResourceFetchEvent:
            if event.local_resource in self._draft_list_data_source.draft_pack_flat_list:
                self._sync_ui()
        if type(event) == DraftListUpdatedEvent or type(event) == DraftPackUpdatedEvent:
            self._sync_ui()
            
            
class WorkerSignals(QObject):
    finished = pyqtSignal(object)

class Worker(QRunnable):
    def __init__(self, 
                 parsed_draft_list: ParsedDraftList, 
                 main_deck_cols: int):
        super(Worker, self).__init__()
        self.parsed_draft_list = parsed_draft_list
        self.main_deck_cols = main_deck_cols
        self.signals = WorkerSignals()

    def run(self):
        selected_leader = None
        selected_base = None
        if len(self.parsed_draft_list.leaders) > 0:
            selected_leader = self.parsed_draft_list.leaders[0]
        if len(self.parsed_draft_list.bases) > 0:
            selected_base = self.parsed_draft_list.bases[0]
        generated_image = DraftListImageGenerator.generate(selected_leader,
                                                           selected_base,
                                                           self.parsed_draft_list.main_deck,
                                                           [], 
                                                           self.main_deck_cols)
        
        byte_array = BytesIO()
        generated_image.save(byte_array, format="PNG")
        byte_array.seek(0)
        
        qimage = QImage.fromData(byte_array.getvalue())
        qpixmap = QPixmap.fromImage(qimage)
        # qpixmap = qpixmap.scaled(qpixmap.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        
        self.signals.finished.emit((qpixmap, qimage, self.parsed_draft_list, None))
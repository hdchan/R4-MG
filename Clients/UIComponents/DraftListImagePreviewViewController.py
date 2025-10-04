

from io import BytesIO
from typing import Optional, Set, Tuple

from PyQt5.QtCore import QMutex, QObject, QRunnable, QThreadPool, QTimer, pyqtSignal
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QFileDialog, QWidget

from AppCore.DataSource import DataSourceDraftList
from AppCore.Observation import ObservationTower, TransmissionReceiverProtocol, TransmissionProtocol
from AppCore.Observation.Events import (
    DraftListUpdatedEvent,
    DraftPackUpdatedEvent,
    LocalAssetResourceFetchEvent,
)
from AppUI.UIComponents.Base.LoadingSpinner import LoadingSpinner
from R4UI import (
    HorizontalBoxLayout,
    ObjectComboBox,
    R4UIHorizontallyExpandingSpacer,
    VerticalBoxLayout,
)

from ..Models.ParsedDeckList import ParsedDeckList
from ..Utility.DraftListImageGenerator import DraftListImageGenerator
from .PhotoViewer import PhotoViewer


class DraftListImagePreviewViewController(QWidget, TransmissionReceiverProtocol):
    def __init__(self, 
                 observation_tower: ObservationTower,
                 draft_list_data_source: DataSourceDraftList):
        super().__init__()
        self._observation_tower = observation_tower
        self._draft_list_data_source = draft_list_data_source
        self._image_generator: DraftListImageGenerator = DraftListImageGenerator()
        self.pool = QThreadPool()
        self.mutex = QMutex()
        self.working_resources: Set[ParsedDeckList] = set()
        self._main_deck_cols = 6
        
        self._save_async_timer = QTimer()
        self._save_async_timer.setSingleShot(True)
        self._save_async_timer.timeout.connect(self._generate_image)
        self.debounce_time = 1000
        
        self._setup_view()
        
        self._observation_tower.subscribe_multi(self, [LocalAssetResourceFetchEvent, 
                                                       DraftListUpdatedEvent, 
                                                       DraftPackUpdatedEvent])
    
    @property
    def _current_option(self) -> DraftListImageGenerator.Option:
        return self._option_dropdown.currentData()
    
    def _option_changed(self, val: int):
        self._sync_ui()

    def _setup_view(self):
        self.setMinimumSize(500, 400)
        self._image_view = PhotoViewer(self)
        self._loading_spinner = LoadingSpinner(self._image_view)
        self._image_view.delegate = self
        
        self._option_dropdown = ObjectComboBox([
                    
                    (DraftListImageGenerator.Option.COST_CURVE_LEADER_BASE_VERTICAL.value, DraftListImageGenerator.Option.COST_CURVE_LEADER_BASE_VERTICAL),

                    (DraftListImageGenerator.Option.COST_CURVE_LEADER_BASE_HORIZONTAL.value, DraftListImageGenerator.Option.COST_CURVE_LEADER_BASE_HORIZONTAL),
                ])
        self._option_dropdown.currentIndexChanged.connect(self._option_changed)
        
        VerticalBoxLayout([
            HorizontalBoxLayout([
                self._option_dropdown
                ]) \
                .set_uniform_content_margins(0) \
                .add_spacer(R4UIHorizontallyExpandingSpacer()),
            self._image_view,
            ]) \
        .set_layout_to_widget(self) \
        .set_uniform_content_margins(0)
        
        self._sync_ui()
    
    def _lock_resource_and_notify(self, local_resource: ParsedDeckList) -> bool:
        if local_resource in self.working_resources:
            return False
        self.mutex.lock()
        self.working_resources.add(local_resource)
        self.mutex.unlock()
        return True
    
    def _unlock_resource_and_notify(self, result: Tuple[QPixmap, QImage, ParsedDeckList, Optional[Exception]]):
        pix_map, _, local_resource, _ = result
        if local_resource in self.working_resources:
            self.mutex.lock()
            self.working_resources.remove(local_resource)
            self.mutex.unlock()
            self._image_view.setPhoto(pix_map, None)
            self._loading_spinner.stop()
    
    def _sync_ui(self):
        self._save_async_timer.stop()
        self._save_async_timer.start(self.debounce_time)
    
    def export_image(self) -> None:
        def finish(result: Tuple[QPixmap, QImage, ParsedDeckList, Optional[Exception]]):
            _, qimage, _, _ = result
            if local_resource in self.working_resources:
                self.mutex.lock()
                self.working_resources.remove(local_resource)
                self.mutex.unlock()
                
                file_path, ok = QFileDialog.getSaveFileName(None, 
                                                    "Save File", 
                                                    "", 
                                                    f"PNG (*.png);;All Files (*)")
                if ok:
                    qimage.save(file_path)
            
        
        print("Exporting image")
        local_resource = ParsedDeckList.from_draft_packs(self._draft_list_data_source.draft_packs)
        if self._lock_resource_and_notify(local_resource):
            # should lock UI in case another job is added
            worker = Worker(self._image_generator, 
                            local_resource, 
                            self._current_option)
            worker.signals.finished.connect(finish)
            self.pool.start(worker)
            
    def _generate_image(self):
        print("Generating image")
        self._loading_spinner.start()
        local_resource = ParsedDeckList.from_draft_packs(self._draft_list_data_source.draft_packs)
        if local_resource.has_cards == False:
            self._image_view.setPhoto(None)
            return
        if self._lock_resource_and_notify(local_resource):
            # should lock UI in case another job is added
            worker = Worker(self._image_generator, 
                            local_resource,
                            self._current_option)
            worker.signals.finished.connect(self._unlock_resource_and_notify)
            self.pool.start(worker)
        
    
    def handle_observation_tower_event(self, event: TransmissionProtocol) -> None:
        if type(event) is LocalAssetResourceFetchEvent:
            if event.local_resource in self._draft_list_data_source.draft_pack_flat_list:
                self._sync_ui()
        if type(event) is DraftListUpdatedEvent or type(event) is DraftPackUpdatedEvent:
            self._sync_ui()
            
            
class WorkerSignals(QObject):
    finished = pyqtSignal(object)

class Worker(QRunnable):
    def __init__(self, 
                 _image_generator: DraftListImageGenerator,
                 parsed_deck_list: ParsedDeckList, 
                 option: DraftListImageGenerator.Option):
        super(Worker, self).__init__()
        self._image_generator = _image_generator
        self.parsed_deck_list = parsed_deck_list
        self.option = option
        self.signals = WorkerSignals()

    def run(self):
        generated_image = self._image_generator.generate_image(self.option, self.parsed_deck_list)
        if generated_image is None:
            return
        byte_array = BytesIO()
        # TODO: fix crash here "tile cannot extend outside image"
        generated_image.save(byte_array, format="PNG")
        byte_array.seek(0)
        
        qimage = QImage.fromData(byte_array.getvalue())
        qpixmap = QPixmap.fromImage(qimage)
        # qpixmap = qpixmap.scaled(qpixmap.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        
        self.signals.finished.emit((qpixmap, qimage, self.parsed_deck_list, None))
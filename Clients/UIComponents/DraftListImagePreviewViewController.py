

from io import BytesIO
from typing import Optional, Set, Tuple, Hashable

from PyQt5.QtCore import QMutex, QObject, QRunnable, QThreadPool, QTimer, pyqtSignal
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QFileDialog

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
    VerticalBoxLayout,
    HorizontalLabeledInputRow,
    R4UICheckBox,
    R4UIWidget,
    R4UIVerticallyExpandingSpacer,
    LineEditInt,
    LineEditFloat,
    HorizontalSplitter
)
from ..Config.SWUAppConfiguration import SWUAppConfigurationManager
from ..Models.ParsedDeckList import ParsedDeckList, ParsedDeckListProviding
from ..Utility.DraftListImageGenerator import DraftListImageGenerator
from ..Events.DeckListImageGeneratedEvent import DeckListImageGeneratedEvent
from .PhotoViewer import PhotoViewer

class DraftListImagePreviewInspectorPanelViewControllerDelegate:
    def option_did_update(self):
        pass

class DraftListImagePreviewInspectorPanelViewController(R4UIWidget):
    def __init__(self, 
                 image_generator: DraftListImageGenerator, 
                 delegate: DraftListImagePreviewInspectorPanelViewControllerDelegate, 
                 configuration_manager: SWUAppConfigurationManager):
        super().__init__()
        self._image_generator = image_generator
        self._configuration_manager = configuration_manager
        self.delegate: Optional[DraftListImagePreviewInspectorPanelViewControllerDelegate] = delegate
        self._deck_list_image_generator_styles = configuration_manager.configuration.deck_list_image_generator_styles

        self._save_async_timer = QTimer()
        self._save_async_timer.setSingleShot(True)
        self._save_async_timer.timeout.connect(self._save_config_and_notify)
        self.debounce_time = 1000

        self._setup_view()
    

    def _start_save_timer(self):
        self._save_async_timer.stop()
        self._save_async_timer.start(self.debounce_time)

    def _save_config_and_notify(self):
        deck_list_styles = self._configuration_manager.configuration.deck_list_image_generator_styles
        
        deck_list_styles.is_leader_base_on_top = self._deck_list_image_generator_styles.is_leader_base_on_top
        deck_list_styles.sideboard_left_spacing_relative_to_main_deck = self._deck_list_image_generator_styles.sideboard_left_spacing_relative_to_main_deck
        deck_list_styles.main_deck_column_spacing = self._deck_list_image_generator_styles.main_deck_column_spacing
        deck_list_styles.main_deck_row_spacing = self._deck_list_image_generator_styles.main_deck_row_spacing
        deck_list_styles.leader_base_spacing_between = self._deck_list_image_generator_styles.leader_base_spacing_between
        deck_list_styles.leader_base_spacing_left_relative_to_main_deck = self._deck_list_image_generator_styles.leader_base_spacing_left_relative_to_main_deck
        deck_list_styles.stacked_card_reveal_percentage = self._deck_list_image_generator_styles.stacked_card_reveal_percentage
        deck_list_styles.is_sideboard_enabled = self._deck_list_image_generator_styles.is_sideboard_enabled
        deck_list_styles.is_sorted_alphabetically = self._deck_list_image_generator_styles.is_sorted_alphabetically

        self._configuration_manager.save_deck_list_image_generator_styles(deck_list_styles)
        self._notify_delegate()

    def _notify_delegate(self):
        if self.delegate is not None:
            self.delegate.option_did_update()


    def _is_leader_base_on_top_updated(self, val: bool):
        self._deck_list_image_generator_styles.is_leader_base_on_top = val
        self._start_save_timer()

    def _sideboard_left_spacing_relative_to_main_deck_updated(self, val: int):
        self._deck_list_image_generator_styles.sideboard_left_spacing_relative_to_main_deck = val
        self._start_save_timer()

    def _main_deck_column_spacing_updated(self, val: int):
        self._deck_list_image_generator_styles.main_deck_column_spacing = val
        self._start_save_timer()

    def _main_deck_row_spacing_updated(self, val: int):
        self._deck_list_image_generator_styles.main_deck_row_spacing = val
        self._start_save_timer()

    def _leader_base_spacing_between_updated(self, val: int):
        self._deck_list_image_generator_styles.leader_base_spacing_between = val
        self._start_save_timer()

    def _leader_base_spacing_left_relative_to_main_deck_updated(self, val: int):
        self._deck_list_image_generator_styles.leader_base_spacing_left_relative_to_main_deck = val
        self._start_save_timer()

    def _sideboard_box_changed(self, val: bool):
        self._deck_list_image_generator_styles.is_sideboard_enabled = val
        self._start_save_timer()

    def _alphabetical_box_changed(self, val: bool):
        self._deck_list_image_generator_styles.is_sorted_alphabetically = val
        self._start_save_timer()

    def _stacked_card_reveal_percentage_updated(self, val: float):
        self._deck_list_image_generator_styles.stacked_card_reveal_percentage = val
        self._start_save_timer()

    def _setup_view(self):
        VerticalBoxLayout([
            HorizontalLabeledInputRow("Leader and Base on top", R4UICheckBox(self._is_leader_base_on_top_updated, self._deck_list_image_generator_styles.is_leader_base_on_top)),

            HorizontalLabeledInputRow("Show sideboard", R4UICheckBox(self._sideboard_box_changed, self._deck_list_image_generator_styles.is_sideboard_enabled)),

            HorizontalLabeledInputRow("Sort alphabetically", R4UICheckBox(self._alphabetical_box_changed, self._deck_list_image_generator_styles.is_sorted_alphabetically)),

            HorizontalLabeledInputRow("Sideboard spacing left relative to main deck", 
                                      LineEditInt(self._deck_list_image_generator_styles.sideboard_left_spacing_relative_to_main_deck, 
                                                  self._sideboard_left_spacing_relative_to_main_deck_updated)),

            HorizontalLabeledInputRow("Main deck column spacing", 
                                      LineEditInt(self._deck_list_image_generator_styles.main_deck_column_spacing, 
                                                  self._main_deck_column_spacing_updated)),

            HorizontalLabeledInputRow("Main deck row spacing", 
                                      LineEditInt(self._deck_list_image_generator_styles.main_deck_row_spacing, 
                                                  self._main_deck_row_spacing_updated)),

            HorizontalLabeledInputRow("Leader Base spacing between", 
                                      LineEditInt(self._deck_list_image_generator_styles.leader_base_spacing_between, 
                                                  self._leader_base_spacing_between_updated)),

            HorizontalLabeledInputRow("Leader Base spacing left relative to main deck", 
                                      LineEditInt(self._deck_list_image_generator_styles.leader_base_spacing_left_relative_to_main_deck, 
                                                  self._leader_base_spacing_left_relative_to_main_deck_updated)),

            HorizontalLabeledInputRow("Stacked card reveal percentage", 
                                      LineEditFloat(self._deck_list_image_generator_styles.stacked_card_reveal_percentage, 
                                                  self._stacked_card_reveal_percentage_updated)),
        ]).set_layout_to_widget(self).add_spacer(R4UIVerticallyExpandingSpacer())

class DraftListImagePreviewViewController(R4UIWidget, TransmissionReceiverProtocol, ParsedDeckListProviding, DraftListImagePreviewInspectorPanelViewControllerDelegate):
    def __init__(self, 
                 observation_tower: ObservationTower,
                 draft_list_data_source: DataSourceDraftList, 
                 configuration_manager: SWUAppConfigurationManager):
        super().__init__()
        self._observation_tower = observation_tower
        self._draft_list_data_source = draft_list_data_source
        self._configuration_manager = configuration_manager
        self._image_generator: DraftListImageGenerator = DraftListImageGenerator(self, configuration_manager)
        self.pool = QThreadPool()
        self.mutex = QMutex()
        self.working_resources: Set[Hashable] = set()
        self._main_deck_cols = 6
        
        self._save_async_timer = QTimer()
        self._save_async_timer.setSingleShot(True)
        self._save_async_timer.timeout.connect(self._generate_image)
        self.debounce_time = 1000
        
        self._setup_view()
        
        self._observation_tower.subscribe_multi(self, [LocalAssetResourceFetchEvent, 
                                                       DraftListUpdatedEvent, 
                                                       DraftPackUpdatedEvent])
    
    # MARK: - DraftListImagePreviewInspectorPanelViewControllerDelegate
    def option_did_update(self):
        self._start_generate_image()

    def _setup_view(self):
        # TODO: remove after converting to window
        self.setMinimumSize(1300, 500)

        self._image_view = PhotoViewer(self)
        self._loading_spinner = LoadingSpinner(self._image_view)
        self._image_view.delegate = self
        
        HorizontalBoxLayout([
            HorizontalSplitter([
                self._image_view,
                DraftListImagePreviewInspectorPanelViewController(self._image_generator,
                                                                  self,
                                                                  self._configuration_manager)
            ], [1, None]),
            
        ]) \
        .set_layout_to_widget(self) \
        # .set_uniform_content_margins(0)
        
        self._start_generate_image()
    
    def _lock_resource_and_notify(self, local_resource: ParsedDeckList) -> bool:
        if local_resource in self.working_resources:
            return False
        self.mutex.lock()
        self.working_resources.add(local_resource)
        self.mutex.unlock()
        self._sync_spinner()
        return True
    
    def _sync_spinner(self):
        if len(self.working_resources) == 0:
            self._loading_spinner.stop()
        else:
            self._loading_spinner.start()

    def _start_generate_image(self):
        self._save_async_timer.stop()
        self._save_async_timer.start(self.debounce_time)
    
    def export_image(self) -> None:
        def finish(result: Tuple[QPixmap, QImage, Hashable, Optional[Exception]]):
            _, qimage, _, _ = result
            if local_resource in self.working_resources:
                self.mutex.lock()
                self.working_resources.remove(local_resource)
                self.mutex.unlock()
                self._sync_spinner()
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
                            local_resource)
            worker.signals.finished.connect(finish)
            self.pool.start(worker)
            
    def _generate_image(self):
        parsed_deck_list = ParsedDeckList.from_draft_packs(self._draft_list_data_source.draft_packs)
        if parsed_deck_list.has_cards == False:
            self._image_view.setPhoto(None)
            return
        
        start_event = DeckListImageGeneratedEvent(DeckListImageGeneratedEvent.EventType.STARTED, 
                                                  parsed_deck_list)
        self._observation_tower.notify(start_event)

        def _unlock_resource_and_notify(result: Tuple[QPixmap, QImage, Hashable, Optional[Exception]]):
            pix_map, _, local_resource, _ = result
            if local_resource in self.working_resources:
                self.mutex.lock()
                self.working_resources.remove(local_resource)
                self.mutex.unlock()
                self._image_view.setPhoto(pix_map, None)
                self._sync_spinner()

                end_event = DeckListImageGeneratedEvent(DeckListImageGeneratedEvent.EventType.FINISHED, 
                                                        parsed_deck_list)
                end_event.predecessor = start_event
                print(f"Generated image: {end_event.seconds_since_predecessor}")
                self._observation_tower.notify(end_event)

        if self._lock_resource_and_notify(parsed_deck_list):
            # should lock UI in case another job is added
            worker = Worker(self._image_generator, 
                            parsed_deck_list)
            worker.signals.finished.connect(_unlock_resource_and_notify)
            self.pool.start(worker)
    
    # MARK: - ParsedDeckListProviding
    @property
    def parsed_deck(self) -> ParsedDeckList:
        return ParsedDeckList.from_draft_packs(self._draft_list_data_source.draft_packs)
    
    # MARK: - Observation
    def handle_observation_tower_event(self, event: TransmissionProtocol) -> None:
        if type(event) is LocalAssetResourceFetchEvent:
            if event.local_resource in self._draft_list_data_source.draft_pack_flat_list:
                self._start_generate_image()
        if type(event) is DraftListUpdatedEvent or type(event) is DraftPackUpdatedEvent:
            self._start_generate_image()
            
            
class WorkerSignals(QObject):
    finished = pyqtSignal(object)

class Worker(QRunnable):
    def __init__(self, 
                 _image_generator: DraftListImageGenerator,
                 parsed_deck_list: Hashable):
        super(Worker, self).__init__()
        self._image_generator = _image_generator
        self.parsed_deck_list = parsed_deck_list
        self.signals = WorkerSignals()

    def run(self):
        generated_image = self._image_generator.generate_image()
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
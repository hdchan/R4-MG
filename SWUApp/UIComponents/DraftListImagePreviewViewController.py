
from typing import Optional
import copy
from PIL import Image
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QFileDialog

from AppCore.Observation import (TransmissionProtocol,
                                 TransmissionReceiverProtocol)
from AppCore.Observation.Events import (DraftListUpdatedEvent,
                                        DraftPackUpdatedEvent,
                                        LocalAssetResourceFetchEvent,
                                        LocalCardResourceFetchEvent)
from AppUI.UIComponents.Base.LoadingSpinner import LoadingSpinner
from R4UI import HorizontalBoxLayout, HorizontalSplitter, R4UIWidget

from ..Models.ParsedDeckList import ParsedDeckList
from ..SWUAppDependenciesProviding import SWUAppDependenciesProviding
from ..Utility.DraftListImageGenerator import DraftListImageGenerator
from .DraftListImagePreviewInspectorPanelViewController import (
    DraftListImagePreviewInspectorPanelViewController,
    DraftListImagePreviewInspectorPanelViewControllerDelegate)
from .PhotoViewer import PhotoViewer


class DraftListImagePreviewViewController(R4UIWidget, TransmissionReceiverProtocol, DraftListImagePreviewInspectorPanelViewControllerDelegate):
    def __init__(self, swu_app_dependencies_provider: SWUAppDependenciesProviding):
        super().__init__()
        self._observation_tower = swu_app_dependencies_provider.observation_tower
        self._draft_list_data_source = swu_app_dependencies_provider.data_source_draft_list
        self._configuration_manager = swu_app_dependencies_provider.configuration_manager
        self._image_generator: DraftListImageGenerator = DraftListImageGenerator(swu_app_dependencies_provider)
        
        self._save_async_timer = QTimer()
        self._save_async_timer.setSingleShot(True)
        self._save_async_timer.timeout.connect(self._generate_image)
        self.debounce_time = 1000 # TODO: vary depending on preview or not
        
        self._setup_view()
        
        self._observation_tower.subscribe_multi(self, [LocalAssetResourceFetchEvent, 
                                                       DraftListUpdatedEvent, 
                                                       DraftPackUpdatedEvent, 
                                                       LocalCardResourceFetchEvent])
    
    def _setup_view(self):
        # TODO: remove after converting to window
        self.setMinimumSize(1300, 500)

        self._image_view = PhotoViewer(self)
        self._loading_spinner = LoadingSpinner(self._image_view)
        self._image_view.delegate = self
        self._inspector_panel = DraftListImagePreviewInspectorPanelViewController(self._image_generator,
                                                                  self,
                                                                  self._configuration_manager)
        
        HorizontalBoxLayout([
            HorizontalSplitter([
                self._image_view,
                self._inspector_panel
            ], [1, None]),
            
        ]) \
        .set_layout_to_widget(self)

        self._start_generate_image_timer()

    @property
    def _parsed_deck(self) -> ParsedDeckList:
        return ParsedDeckList.from_draft_packs(copy.deepcopy(self._draft_list_data_source.draft_packs))

    # MARK: - DraftListImagePreviewInspectorPanelViewControllerDelegate
    def option_did_update(self):
        self._start_generate_image_timer()

    def regenerate_was_clicked(self) -> None:
        self._generate_image()

    def _sync_spinner(self):
        if self._image_generator.is_loading:
            self._loading_spinner.start()
            # self._inspector_panel.regenerate_button.setEnabled(False)
        else:
            self._loading_spinner.stop()
            # self._inspector_panel.regenerate_button.setEnabled(True)

    def _start_generate_image_timer(self):
        self._save_async_timer.stop()
        if self._configuration_manager.configuration.deck_list_image_generator_styles.is_auto_generate_preview:
            self._save_async_timer.start(self.debounce_time)
    
    def _generate_image(self):
        if self._parsed_deck.has_cards == False:
            self._image_view.setPhoto(None)
            return
        
        def _finished(pixmap: Optional[QPixmap], image: Optional[Image.Image]):
            try:
                self._image_view.setPhoto(pixmap, None)
                self._sync_spinner()
            except Exception as error:
                print(error)
        self._image_generator.generate_image(self._parsed_deck, False, _finished)
        self._sync_spinner()

    def export_image(self) -> None:
        def _finished(pixmap: Optional[QPixmap], image: Optional[Image.Image]):
            try:
                if image is None:
                    return
                self._sync_spinner()
                file_path, ok = QFileDialog.getSaveFileName(None, 
                                                        "Save File", 
                                                        "", 
                                                        f"PNG (*.png);;All Files (*)")
                if ok:
                    image.save(file_path)
            except Exception as error:
                print(error)
        self._image_generator.generate_image(self._parsed_deck, True, _finished)
        self._sync_spinner()
    
    # MARK: - Observation
    def handle_observation_tower_event(self, event: TransmissionProtocol) -> None:
        if type(event) is LocalAssetResourceFetchEvent:
            if event.local_resource in self._draft_list_data_source.draft_pack_flat_list:
                self._start_generate_image_timer()
        if type(event) is DraftListUpdatedEvent or type(event) is DraftPackUpdatedEvent:
            self._start_generate_image_timer()
        if type(event) == LocalCardResourceFetchEvent:
            self._sync_spinner() # spinner does not sync when downloading images
from typing import Optional

from PyQt5.QtWidgets import QWidget

from AppCore.Models import LocalResourceDraftListWindow
from AppCore.Observation import (TransmissionProtocol,
                                 TransmissionReceiverProtocol)
from AppCore.Observation.Events import DraftListWindowResourceUpdatedEvent, DraftPackUpdatedEvent
from AppUI.AppDependenciesInternalProviding import AppDependenciesInternalProviding
from R4UI import VerticalBoxLayout

from .DraftListTablePackPreviewViewController import (
    DraftListTablePackPreviewViewController,
    DraftListTablePackPreviewViewControllerDelegate)


class DraftListTablePackPreviewContainerViewController(QWidget,
                                                       DraftListTablePackPreviewViewControllerDelegate,
                                                       TransmissionReceiverProtocol):
    
    class VCConfiguration:
        def __init__(self, is_staging: bool, is_presentation: bool):
            self.is_staging = is_staging
            self.is_presentation = is_presentation
    
    def __init__(self, 
                 app_dependencies_provider: AppDependenciesInternalProviding,
                 vc_configuration: VCConfiguration,
                 resource: LocalResourceDraftListWindow):
        super().__init__()
        self._app_dependencies_provider = app_dependencies_provider
        self._data_source_draft_list = app_dependencies_provider.data_source_draft_list
        self._configuration_manager = app_dependencies_provider.configuration_manager
        self._app_ui_configuration_manager = app_dependencies_provider.app_ui_configuration_manager
        self._data_source_draft_list_window_resource_deployer = app_dependencies_provider.data_source_draft_list_window_resource_deployer
        self._vc_configuration = vc_configuration
        
        self._resource = resource
        self._draft_pack = self._data_source_draft_list.pack_for_draft_pack_identifier(resource.window_configuration.draft_pack_identifier)
        
        self._setup_view()
    
        app_dependencies_provider.observation_tower.subscribe_multi(self, [DraftListWindowResourceUpdatedEvent, DraftPackUpdatedEvent])
    
    def _setup_view(self):
        self._pack_preview = DraftListTablePackPreviewViewController(self._app_dependencies_provider, None)
        self._pack_preview.delegate = self
        VerticalBoxLayout([
            self._pack_preview
        ]) \
            .set_uniform_content_margins(0) \
                .set_layout_to_widget(self)
        self._sync_ui()
    
    @property
    def dlp_pack_index(self) -> Optional[int]:
        draft_pack = self._draft_pack
        if draft_pack is None:
            return None
        index = self._data_source_draft_list.pack_index_for_draft_pack_identifier(draft_pack.pack_identifier)
        if index is None:
            # TODO: logic should be moved to data source
            self._data_source_draft_list_window_resource_deployer.unbind_draft_pack_name(self._resource)
        return index
    
    @property
    def dlp_pack_identifier(self) -> Optional[str]:
        return self._resource.window_configuration.draft_pack_identifier
    
    @property
    def dlp_is_staging_view(self) -> bool:
        return self._vc_configuration.is_staging
    
    @property
    def dlp_is_presentation(self) -> bool:
        return self._vc_configuration.is_presentation
    
    def _sync_ui(self):
        if self._vc_configuration.is_staging == False:
            self.setWindowTitle(self._resource.file_name)
            window_height = self._resource.window_configuration.window_height
            window_width = self._resource.window_configuration.window_width
            self.setFixedSize(window_width, window_height)
        
        self._pack_preview.sync_ui()
    
    def handle_observation_tower_event(self, event: TransmissionProtocol) -> None:
        if type(event) == DraftListWindowResourceUpdatedEvent:
            if self._resource == event.old_resource:
                self._resource = event.new_resource
                self._draft_pack = self._data_source_draft_list.pack_for_draft_pack_identifier(event.new_resource.window_configuration.draft_pack_identifier)
            self._sync_ui()
        if type(event) == DraftPackUpdatedEvent:
            self._sync_ui()
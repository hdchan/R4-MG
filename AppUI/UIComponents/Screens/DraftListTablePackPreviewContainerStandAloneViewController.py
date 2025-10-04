from PyQt5.QtWidgets import QWidget

from AppCore.Models import LocalResourceDraftListWindow
from AppUI.AppDependenciesProviding import AppDependenciesProviding
from AppUI.UIComponents.DraftListDeployment.DraftListTablePackPreviewContainerViewController import \
    DraftListTablePackPreviewContainerViewController
from R4UI import VerticalBoxLayout

from AppCore.Observation import (TransmissionProtocol,
                                 TransmissionReceiverProtocol)
from AppCore.Observation.Events import DraftListWindowResourceUpdatedEvent
class DraftListTablePackPreviewContainerStandAloneViewController(QWidget, TransmissionReceiverProtocol):
    
    def __init__(self, 
                 app_dependencies_provider: AppDependenciesProviding, 
                 resource: LocalResourceDraftListWindow):
        super().__init__()
        self._app_dependencies_provider = app_dependencies_provider
        self._resource = resource
        
        app_dependencies_provider.observation_tower.subscribe_multi(self, [DraftListWindowResourceUpdatedEvent])
        
        self._setup_view()
        
    def _setup_view(self):
        self.setContentsMargins(0, 0, 0, 0)
        config = DraftListTablePackPreviewContainerViewController.VCConfiguration(is_staging=False, 
                                                                                  is_presentation=True)
        VerticalBoxLayout([
            DraftListTablePackPreviewContainerViewController(self._app_dependencies_provider, config, self._resource)
            ]) \
                .set_uniform_content_margins(0) \
                    .set_layout_to_widget(self)
                    
        self._sync_ui()
    
    def _sync_ui(self):
        self.setWindowTitle(self._resource.window_configuration.window_name)
        self.setFixedSize(self._resource.window_configuration.window_width, self._resource.window_configuration.window_height)
        
    def handle_observation_tower_event(self, event: TransmissionProtocol) -> None:
        if type(event) == DraftListWindowResourceUpdatedEvent:
            if self._resource == event.old_resource:
                self._resource = event.new_resource
                self._sync_ui()
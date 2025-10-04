from typing import List

from PyQt5.QtWidgets import QSizePolicy, QWidget

from AppCore.Observation import (TransmissionProtocol,
                                 TransmissionReceiverProtocol)
from AppCore.Observation.Events import DraftListWindowResourceLoadEvent
from AppUI.AppDependenciesProviding import AppDependenciesProviding
from R4UI import (HorizontalBoxLayout, PushButton, ScrollArea,
                    VerticalBoxLayout)

from .DraftListTablePackPreviewContainerViewController import \
    DraftListTablePackPreviewContainerViewController
from .DraftListWindowConfigViewController import \
    DraftListWindowConfigViewController

from R4UI import R4UIWidget
class DraftListWindowDeployerViewController(QWidget, TransmissionReceiverProtocol):
    def __init__(self, 
                 app_dependencies_provider: AppDependenciesProviding):
        super().__init__()
        self._app_dependencies_provider = app_dependencies_provider
        self._data_source_draft_list_window_resource_deployer = app_dependencies_provider.data_source_draft_list_window_resource_deployer
        self._router = app_dependencies_provider.router
        self._observation_tower = app_dependencies_provider.observation_tower
        
        self._observation_tower.subscribe_multi(self, [DraftListWindowResourceLoadEvent])
        
        self._setup_view()
        self._sync_ui()
        
    def _setup_view(self):
        self._cell_container = HorizontalBoxLayout()
        self._cell_container.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)
        VerticalBoxLayout([
            ScrollArea(self._cell_container),
            PushButton("Add window", self._add_new_window)
        ]).set_layout_to_widget(self)
    
    def _add_new_window(self):
        window_name, ok = self._router.prompt_text_input("Create new window instance", "Window name")
        if not ok:
            return
        try:
            self._data_source_draft_list_window_resource_deployer.create_new_window(window_name)
        except Exception as error:
            self._router.show_error(error)
    
    def _sync_ui(self):
        windows_resource = self._data_source_draft_list_window_resource_deployer.draft_list_windows
        
        widgets: List[R4UIWidget] = []
        for w in windows_resource:
            widgets.append(DraftListWindowConfigViewController(self._app_dependencies_provider, w))
        
        self._cell_container.replace_all_widgets(widgets)
        
    def handle_observation_tower_event(self, event: TransmissionProtocol) -> None:
        if type(event) is DraftListWindowResourceLoadEvent:
            self._sync_ui()
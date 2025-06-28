from typing import List

from PyQt5.QtWidgets import QLabel, QSizePolicy, QWidget

from AppCore.Observation import (TransmissionProtocol,
                                 TransmissionReceiverProtocol)
from AppCore.Observation.Events import DraftListWindowResourceLoadEvent
from AppUI.AppDependenciesProviding import AppDependenciesProviding
from PyQtUI import (HorizontalBoxLayout, PushButton, ScrollArea,
                    VerticalBoxLayout)

from .DraftListTablePackPreviewContainerViewController import \
    DraftListTablePackPreviewContainerViewController
from .DraftListWindowConfigViewController import \
    DraftListWindowConfigViewController


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
            ScrollArea(
                self._cell_container
                ),
            PushButton(
                "Add window",
                self._add_new_window
                )
        ]).set_to_layout(self)
    
    def _add_new_window(self):
        window_name, _ = self._router.prompt_text_input("Create new window instance", "Window name")
        try:
            self._data_source_draft_list_window_resource_deployer.create_new_window(window_name)
        except Exception as error:
            self._router.show_error(error)
    
    def _sync_ui(self):
        windows_resource = self._data_source_draft_list_window_resource_deployer.draft_list_windows
        
        widgets: List[QWidget] = []
        for w in windows_resource:
            cell = VerticalBoxLayout([
                QLabel(w.file_name),
                DraftListTablePackPreviewContainerViewController(
                    self._app_dependencies_provider,
                    DraftListTablePackPreviewContainerViewController.VCConfiguration(True),
                    w
                    ),
                
                DraftListWindowConfigViewController(
                    self._app_dependencies_provider, 
                    w
                    )
            ])
            widgets.append(cell)
        
        self._cell_container.replace_widgets(widgets)
        
    def handle_observation_tower_event(self, event: TransmissionProtocol) -> None:
        if type(event) is DraftListWindowResourceLoadEvent:
            self._sync_ui()
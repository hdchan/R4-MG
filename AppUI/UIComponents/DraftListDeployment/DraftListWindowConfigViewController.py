from typing import Optional

from PyQt5.QtWidgets import QWidget
from AppCore.Observation.Events import DraftListUpdatedEvent, DraftListWindowResourceUpdatedEvent
from AppCore.Observation import TransmissionProtocol, TransmissionReceiverProtocol
from AppCore.Models import (DraftListWindowConfiguration,
                            LocalResourceDraftListWindow)
from AppUI.AppDependenciesProviding import AppDependenciesProviding
from PyQtUI import ComboBox, PushButton, VerticalBoxLayout, HorizontalBoxLayout, HorizontalLabeledInputRow, LineEditInt


class DraftListWindowConfigViewController(QWidget, TransmissionReceiverProtocol):
    def __init__(self,
                 app_dependencies_provider: AppDependenciesProviding, 
                 resource: LocalResourceDraftListWindow):
        super().__init__()
        self._data_source_draft_list = app_dependencies_provider.data_source_draft_list
        self._data_source_draft_list_window_resource_deployer = app_dependencies_provider.data_source_draft_list_window_resource_deployer
        self._resource = resource
        self._router = app_dependencies_provider.router
        
        app_dependencies_provider.observation_tower.subscribe_multi(self, [DraftListUpdatedEvent, 
                                                                           DraftListWindowResourceUpdatedEvent])
        
        self._setup_view()
        
    def _setup_view(self):
        self._pack_list_combo_box = ComboBox()
        
        self._height_input = LineEditInt(self._resource.window_configuration.window_height)
        self._width_input = LineEditInt(self._resource.window_configuration.window_width)
        
        VerticalBoxLayout([
            self._pack_list_combo_box,
            
            PushButton("Spawn window", self._spawn_window),
            
            HorizontalLabeledInputRow("Height", self._height_input),
            HorizontalLabeledInputRow("Width", self._width_input),
            
            PushButton("Save window dimensions", self._save_window_dimensions),
            PushButton("Delete", self._delete_window)
        ]).set_to_layout(self)
        
        self._reset_pack_list_combo_box()
    
    def _reset_pack_list_combo_box(self):
        try:
            self._pack_list_combo_box.disconnect()
        except:
            pass
        self._pack_list_combo_box.replace_options(["None"] + self._data_source_draft_list.pack_names)
        self._pack_list_combo_box.currentIndexChanged.connect(self._update_pack_list)
        
        selected_pack_name = self._resource.window_configuration.draft_pack_name
        if selected_pack_name is not None:
            self._pack_list_combo_box.setCurrentText(selected_pack_name)
    
    def _update_pack_list(self):
        existing_config = self._resource.window_configuration
        selected_pack_identifier: Optional[str] = None
        if self._pack_list_combo_box.currentIndex() > 0:
            selected_pack_identifier = self._pack_list_combo_box.currentText()
        new_config = DraftListWindowConfiguration(
            existing_config.window_height,
            existing_config.window_width,
            selected_pack_identifier
        )
        self._data_source_draft_list_window_resource_deployer.update_window_configuration(self._resource, new_config)
    
    def _save_window_dimensions(self):
        existing_config = self._resource.window_configuration
        width, height = existing_config.window_width, existing_config.window_height
        if self._height_input.value is not None:
            height = self._height_input.value
        if self._width_input.value is not None:
            width = self._width_input.value
        new_config = DraftListWindowConfiguration(
            height,
            width,
            existing_config.draft_pack_name
        )
        self._data_source_draft_list_window_resource_deployer.update_window_configuration(self._resource, new_config)
        
    def _spawn_window(self):
        self._router.open_draft_list_standalone_view(self._resource)
        
    def _delete_window(self):
        if self._router.prompt_accept("Delete window", f"Are you sure you want to delete {self._resource.file_name}?"):
            self._data_source_draft_list_window_resource_deployer.delete_window_resource(self._resource) 
    
    def handle_observation_tower_event(self, event: TransmissionProtocol) -> None:
        if type(event) == DraftListWindowResourceUpdatedEvent:
            if event.old_resource == self._resource:
                self._resource = event.new_resource
                # self._reset_pack_list_combo_box()
        if type(event) == DraftListUpdatedEvent:
            self._update_pack_list()
            self._reset_pack_list_combo_box()
            
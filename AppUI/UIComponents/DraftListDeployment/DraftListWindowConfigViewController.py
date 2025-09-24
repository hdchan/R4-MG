from typing import Optional

from PyQt5.QtWidgets import QWidget

from AppCore.Models import DraftPack, LocalResourceDraftListWindow
from AppCore.Observation import (TransmissionProtocol,
                                 TransmissionReceiverProtocol)
from AppCore.Observation.Events import (DraftListWindowResourceUpdatedEvent,
                                        DraftPackUpdatedEvent)
from AppUI.AppDependenciesProviding import AppDependenciesProviding
from PyQtUI import (HorizontalBoxLayout, HorizontalLabeledInputRow,
                    LineEditInt, ObjectComboBox, PushButton, VerticalBoxLayout)


class DraftListWindowConfigViewController(QWidget, TransmissionReceiverProtocol):
    def __init__(self,
                 app_dependencies_provider: AppDependenciesProviding, 
                 resource: LocalResourceDraftListWindow):
        super().__init__()
        self._data_source_draft_list = app_dependencies_provider.data_source_draft_list
        self._data_source_draft_list_window_resource_deployer = app_dependencies_provider.data_source_draft_list_window_resource_deployer
        self._resource = resource
        self._router = app_dependencies_provider.router
        
        app_dependencies_provider.observation_tower.subscribe_multi(self, [DraftPackUpdatedEvent, 
                                                                           DraftListWindowResourceUpdatedEvent])
        
        self._setup_view()
        
    def _setup_view(self):
        self._pack_list_combo_box = ObjectComboBox()
        
        self._height_input = LineEditInt(self._resource.window_configuration.window_height)
        self._width_input = LineEditInt(self._resource.window_configuration.window_width)
        
        VerticalBoxLayout([
            self._pack_list_combo_box,
            
            HorizontalBoxLayout([
                PushButton("Spawn window", self._spawn_window),
                PushButton("Delete", self._delete_window),
                ]),
            
            
            HorizontalBoxLayout([
                HorizontalLabeledInputRow("Width", self._width_input),
                HorizontalLabeledInputRow("Height", self._height_input),
                ]),
            
            PushButton("Update window dimensions", self._save_window_dimensions),
            
        ]).set_to_layout(self)
        
        self._reset_pack_list_combo_box()
    
    def _reset_pack_list_combo_box(self):
        try:
            self._pack_list_combo_box.disconnect()
        except:
            pass
        
        mapped_values = list(map(lambda x: (x.pack_name, x), self._data_source_draft_list.draft_packs))
        
        self._pack_list_combo_box.replace_options([("None", None)] + mapped_values)
        self._pack_list_combo_box.currentIndexChanged.connect(self._update_pack_list)
        
        selected_pack = self._data_source_draft_list.pack_for_draft_pack_identifier(self._resource.window_configuration.draft_pack_identifier)
        if selected_pack is not None:
            self._pack_list_combo_box.setCurrentText(selected_pack.pack_name)
    
    def _update_pack_list(self):
        selected_pack: Optional[DraftPack] = self._pack_list_combo_box.currentData()
        pack_identifier = None
        if selected_pack is not None:
            pack_identifier = selected_pack.pack_identifier
        self._data_source_draft_list_window_resource_deployer.update_window_draft_pack(self._resource, pack_identifier)
    
    def _save_window_dimensions(self):
        self._data_source_draft_list_window_resource_deployer.update_window_dimension(self._resource, self._width_input.value, self._height_input.value)
        
    def _spawn_window(self):
        self._router.open_draft_list_standalone_view(self._resource)
        
    def _delete_window(self):
        if self._router.prompt_accept("Delete window", f"Are you sure you want to delete {self._resource.window_configuration.window_name}?"):
            self._data_source_draft_list_window_resource_deployer.delete_window_resource(self._resource) 
    
    def handle_observation_tower_event(self, event: TransmissionProtocol) -> None:
        if type(event) == DraftListWindowResourceUpdatedEvent:
            if event.old_resource == self._resource:
                self._resource = event.new_resource
                # self._reset_pack_list_combo_box()
        if type(event) == DraftPackUpdatedEvent:
            self._update_pack_list()
            self._reset_pack_list_combo_box()
            
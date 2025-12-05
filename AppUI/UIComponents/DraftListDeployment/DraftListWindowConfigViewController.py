from typing import Optional

from AppCore.Models import DraftPack, LocalResourceDraftListWindow
from AppCore.Observation import (TransmissionProtocol,
                                 TransmissionReceiverProtocol)
from AppCore.Observation.Events import (DraftListWindowResourceUpdatedEvent,
                                        DraftPackUpdatedEvent)
from AppUI.AppDependenciesInternalProviding import \
    AppDependenciesInternalProviding
from R4UI import (HorizontalBoxLayout, HorizontalLabeledInputRow, Label,
                  LineEditInt, RObjectComboBox, PushButton, RWidget,
                  VerticalBoxLayout)

from .DraftListTablePackPreviewContainerViewController import \
    DraftListTablePackPreviewContainerViewController


class DraftListWindowConfigViewController(RWidget, TransmissionReceiverProtocol):
    def __init__(self,
                 app_dependencies_provider: AppDependenciesInternalProviding, 
                 resource: LocalResourceDraftListWindow):
        super().__init__()
        self._app_dependencies_provider = app_dependencies_provider
        self._data_source_draft_list = app_dependencies_provider.data_source_draft_list
        self._data_source_draft_list_window_resource_deployer = app_dependencies_provider.data_source_draft_list_window_resource_deployer
        self._resource = resource
        self._router = app_dependencies_provider.router
        
        app_dependencies_provider.observation_tower.subscribe_multi(self, [DraftPackUpdatedEvent, 
                                                                           DraftListWindowResourceUpdatedEvent])
        
        self._setup_view()
        
    def _setup_view(self):
        self._pack_list_combo_box = RObjectComboBox()
        
        self._height_input = LineEditInt(self._resource.window_configuration.window_height)
        self._width_input = LineEditInt(self._resource.window_configuration.window_width)
        
        VerticalBoxLayout([
            HorizontalBoxLayout([
                Label(self._resource.window_configuration.window_name),
                PushButton("Spawn", self._spawn_window),
                PushButton("Delete", self._delete_window, tooltip="Delete"),
            ], weights=[1]),
            
            DraftListTablePackPreviewContainerViewController(
                self._app_dependencies_provider,
                DraftListTablePackPreviewContainerViewController.VCConfiguration(is_staging=True, 
                                                                                 is_presentation=True),
                self._resource
                ),

            HorizontalBoxLayout([
                Label("Assigned draft pack:"),
                self._pack_list_combo_box,
            ], [1, 3]),
            
            HorizontalBoxLayout([
                HorizontalLabeledInputRow("W", self._width_input).set_uniform_content_margins(0),
                HorizontalLabeledInputRow("H", self._height_input).set_uniform_content_margins(0),
                PushButton("Update dimensions", self._save_window_dimensions)
                ]).set_uniform_content_margins(0),
            
            
            
        ]).set_layout_to_widget(self)
        
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
        selected_pack: Optional[DraftPack] = self._pack_list_combo_box.current_data
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
        if type(event) is DraftListWindowResourceUpdatedEvent:
            if event.old_resource == self._resource:
                self._resource = event.new_resource
                # self._reset_pack_list_combo_box()
        if type(event) is DraftPackUpdatedEvent:
            self._update_pack_list()
            self._reset_pack_list_combo_box()
            
import copy
import os
from pathlib import Path
from typing import List, Optional

from AppCore.Config import Configuration, ConfigurationManager
from AppCore.Models import (DraftListWindowConfiguration,
                            LocalResourceDraftListWindow)
from AppCore.Observation import (ObservationTower, TransmissionProtocol,
                                 TransmissionReceiverProtocol)
from AppCore.Observation.Events import (DraftListUpdatedEvent,
                                        DraftListWindowResourceLoadEvent,
                                        DraftListWindowResourceUpdatedEvent)
from AppCore.Service.DataSerializer import DataSerializer

from .DataSourceDraftList import DataSourceDraftList

JSON_EXTENSION = 'json'



class DataSourceDraftListWindowResourceDeployer(TransmissionReceiverProtocol):
    def __init__(self, 
                 configuration_manager: ConfigurationManager, 
                 observation_tower: ObservationTower, 
                 data_source_draft_list: DataSourceDraftList, 
                 data_serializer: DataSerializer):
        self._configuration_manager = configuration_manager
        self._observation_tower = observation_tower
        self._data_source_draft_list = data_source_draft_list
        self._data_serializer = data_serializer
        self._draft_list_windows: List[LocalResourceDraftListWindow] = []
        self._observation_tower.subscribe(self, DraftListUpdatedEvent)
        self.load_resources()
        
    @property
    def _configuration(self) -> Configuration:
        return self._configuration_manager.configuration
    
    @property
    def draft_list_windows(self) -> List[LocalResourceDraftListWindow]:
        return sorted(copy.deepcopy(self._draft_list_windows), key=lambda x: x.created_date)
    
    def load_resources(self):
        start_event = DraftListWindowResourceLoadEvent(DraftListWindowResourceLoadEvent.EventType.STARTED)
        self._observation_tower.notify(start_event)
        
        self._generate_dir_if_needed()
        self._draft_list_windows = []
        
        file_list = os.listdir(self._configuration.draft_list_windows_dir_path)
        for file_name_with_ext in file_list[:]:
            file_path = Path(file_name_with_ext)
            if file_path.suffix == f'.{JSON_EXTENSION}':
                loaded_json = self._data_serializer.load(f'{self._configuration.draft_list_windows_dir_path}/{file_name_with_ext}')
                if loaded_json is None:
                    continue
                window_config = DraftListWindowConfiguration.from_json(loaded_json)
                draft_pack = self._data_source_draft_list.pack_for_draft_pack_identifier(window_config.draft_pack_identifier)
                if draft_pack is None:
                    window_config.draft_pack_identifier = None
                resource = LocalResourceDraftListWindow(file_path.stem, 
                                                        window_config, 
                                                        self._configuration.draft_list_windows_dir_path, 
                                                        draft_pack)
                self._draft_list_windows.append(resource)
                    
        end_event = DraftListWindowResourceLoadEvent(DraftListWindowResourceLoadEvent.EventType.FINISHED)
        end_event.predecessor = start_event
        self._observation_tower.notify(end_event)
        
    def create_new_window(self, window_name: str):
        self._generate_dir_if_needed()
        new_window_configuration = DraftListWindowConfiguration.default_window(window_name)
        resource = LocalResourceDraftListWindow(new_window_configuration.window_identifier, 
                                                new_window_configuration, 
                                                self._configuration.draft_list_windows_dir_path, 
                                                None)
        data = new_window_configuration.to_data()
        self._data_serializer.save_json_data(resource.asset_path, data)
            
        self._draft_list_windows.append(resource)
        # reload resources?
        self.load_resources()
    
    def delete_window_resource(self, resource: LocalResourceDraftListWindow):
        found: List[LocalResourceDraftListWindow] = list(filter(lambda x: x == resource, self._draft_list_windows))
        if len(found) > 0:
            resource = found[0]
            index = self._draft_list_windows.index(resource)
            Path(resource.asset_path).unlink()
            del self._draft_list_windows[index]
            self.load_resources()
    
        # Don't update window name to prevent more complications?
    # def update_window_name(self, resource: LocalResourceDraftListWindow, name: str):
    #     found_resources: List[LocalResourceDraftListWindow] = list(filter(lambda x: x == resource, self._draft_list_windows))
    #     if len(found_resources) == 0:
    #         raise Exception(f"Window {resource.file_name} does not exist")
        
    #     old_resource = found_resources[0]
    #     old_resource_index = self._draft_list_windows.index(old_resource)
        
    #     old_file_name = old_resource.asset_path
    #     new_file_name = f'{old_resource.asset_dir}/{name}'
    #     try:
    #         # Rename the file
    #         os.rename(old_file_name, new_file_name)
    #     except FileNotFoundError:
    #         raise Exception(f"Error: The file '{old_file_name}' was not found.")
    #     except OSError as e:
    #         raise Exception(f"Error renaming file: {e}")
        
    #     new_resource = LocalResourceDraftListWindow(name, old_resource.window_configuration, old_resource.asset_dir)
    #     self._draft_list_windows[old_resource_index] = new_resource
        
    #     event = DraftListWindowResourceUpdatedEvent(copy.deepcopy(new_resource), old_resource)
        
    #     self._observation_tower.notify(event)
    
    def unbind_draft_pack_name(self, resource: LocalResourceDraftListWindow):
        self.update_window_draft_pack(resource, None)
        
    
    def update_window_dimension(self, resource: LocalResourceDraftListWindow, width: Optional[int], height: Optional[int]):
        old_config = copy.deepcopy(resource.window_configuration)
        new_width = old_config.window_width
        new_height = old_config.window_height
        if width is not None:
            new_width = width
        if height is not None:
            new_height = height
        new_config = old_config
        new_config.window_width = new_width
        new_config.window_height = new_height
        self._update_window_configuration(resource, new_config)
        
    def update_window_draft_pack(self, resource: LocalResourceDraftListWindow, draft_pack_identifier: Optional[str]):
        old_config = copy.deepcopy(resource.window_configuration)
        new_config = old_config
        new_config.draft_pack_identifier = draft_pack_identifier
        self._update_window_configuration(resource, new_config)
    
    def _update_window_configuration(self, resource: LocalResourceDraftListWindow, new_configuration: DraftListWindowConfiguration):
        found_resources: List[LocalResourceDraftListWindow] = list(filter(lambda x: x == resource, self._draft_list_windows))
        if len(found_resources) == 0:
            raise Exception(f"Window {resource.file_name} does not exist")
        
        old_resource = copy.deepcopy(found_resources[0])
        old_resource_index = self._draft_list_windows.index(old_resource)
        
        updated_resource = self._draft_list_windows[old_resource_index]
        updated_resource.window_configuration = new_configuration
        
        self._draft_list_windows[old_resource_index] = updated_resource
        
        path_to_file = Path(resource.asset_path)
        if path_to_file.is_file():
            data = new_configuration.to_data()
            self._data_serializer.save_json_data(resource.asset_path, data)
            
            event = DraftListWindowResourceUpdatedEvent(copy.deepcopy(updated_resource), old_resource)
            
            self._observation_tower.notify(event)
            
            assert(updated_resource.window_configuration == new_configuration)
        
    def _generate_dir_if_needed(self):
        Path(self._configuration.draft_list_windows_dir_path).mkdir(parents=True, exist_ok=True)
        
    def handle_observation_tower_event(self, event: TransmissionProtocol) -> None:
        pass
         
import copy
import io
import os
from pathlib import Path
from typing import List

import yaml

from AppCore.Config import Configuration, ConfigurationManager
from AppCore.Models import (DraftListWindowConfiguration,
                            LocalResourceDraftListWindow)
from AppCore.Observation import ObservationTower, TransmissionProtocol, TransmissionReceiverProtocol
from AppCore.Observation.Events import DraftListWindowResourceLoadEvent, DraftListWindowResourceUpdatedEvent, DraftListUpdatedEvent
from .DataSourceDraftList import DataSourceDraftList

YAML_EXTENSION = 'yaml'



class DataSourceDraftListWindowResourceDeployer(TransmissionReceiverProtocol):
    def __init__(self, 
                 configuration_manager: ConfigurationManager, 
                 observation_tower: ObservationTower, 
                 data_source_draft_list: DataSourceDraftList):
        self._configuration_manager = configuration_manager
        self._observation_tower = observation_tower
        self._data_source_draft_list = data_source_draft_list
        self._draft_list_windows: List[LocalResourceDraftListWindow] = []
        self._observation_tower.subscribe(self, DraftListUpdatedEvent)
        self.load_resources()
        
    @property
    def _configuration(self) -> Configuration:
        return self._configuration_manager.configuration
    
    @property
    def draft_list_windows(self) -> List[LocalResourceDraftListWindow]:
        return copy.deepcopy(self._draft_list_windows)
    
    def load_resources(self):
        start_event = DraftListWindowResourceLoadEvent(DraftListWindowResourceLoadEvent.EventType.STARTED)
        self._observation_tower.notify(start_event)
        
        self._generate_dir_if_needed()
        self._draft_list_windows = []
        
        file_list = os.listdir(self._configuration.draft_list_windows_dir_path)
        for file_name_with_ext in file_list[:]:
            file_path = Path(file_name_with_ext)
            if file_path.suffix == f'.{YAML_EXTENSION}':
                with open(f'{self._configuration.draft_list_windows_dir_path}/{file_name_with_ext}', 'r') as stream:
                    window_config_json = yaml.safe_load(stream)
                    window_config = DraftListWindowConfiguration.from_json(window_config_json)
                    draft_pack = self._data_source_draft_list.pack_for_draft_pack_name(window_config.draft_pack_name)
                    if draft_pack is None:
                        window_config.draft_pack_name = None
                    # update file to have a None for pack name if it does not exist
                    updated_data = window_config.to_data()
                    with io.open(f'{self._configuration.draft_list_windows_dir_path}/{file_name_with_ext}', 'w', encoding='utf8') as outfile:
                        yaml.dump(updated_data, outfile, default_flow_style=False, allow_unicode=True)
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
        new_window_configuration = DraftListWindowConfiguration.default_window()
        resource = LocalResourceDraftListWindow(window_name, new_window_configuration, self._configuration.draft_list_windows_dir_path, None)
        path_to_file = Path(resource.asset_path)
        if path_to_file.is_file():
            raise Exception(f"Window already exists: {window_name}")
        data = new_window_configuration.to_data()
        with io.open(resource.asset_path, 'w', encoding='utf8') as outfile:
            yaml.dump(data, outfile, default_flow_style=False, allow_unicode=True)
            
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
        old_config = resource.window_configuration
        new_config = DraftListWindowConfiguration(old_config.window_height, old_config.window_width, None)
        self.update_window_configuration(resource, new_config)
        
    
    def update_window_configuration(self, resource: LocalResourceDraftListWindow, new_configuration: DraftListWindowConfiguration):
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
            with io.open(resource.asset_path, 'w', encoding='utf8') as outfile:
                yaml.dump(data, outfile, default_flow_style=False, allow_unicode=True)
            
            event = DraftListWindowResourceUpdatedEvent(copy.deepcopy(updated_resource), old_resource)
            
            self._observation_tower.notify(event)
            
            assert(updated_resource.window_configuration == new_configuration)
        
    def _generate_dir_if_needed(self):
        Path(self._configuration.draft_list_windows_dir_path).mkdir(parents=True, exist_ok=True)
        
    def handle_observation_tower_event(self, event: TransmissionProtocol) -> None:
        pass
         
import copy
from typing import List, Optional

from AppCore.Config import *
from AppCore.Models import DraftPack, LocalCardResource
from AppCore.Observation import ObservationTower
from AppCore.Observation.Events import DraftListUpdatedEvent
from AppCore.Service.DataSerializer import DataSerializer
from uuid import UUID

class DataSourceDraftList:
    
    def __init__(self, 
                 configuration_manager: ConfigurationManager,
                 observation_tower: ObservationTower, 
                 data_serializer: DataSerializer):
        self._configuration_manager = configuration_manager
        self._observation_tower = observation_tower
        self._data_serializer = data_serializer
        
        self._packs: List[DraftPack] = []
        
        self._file_path = f'{self._configuration_manager.configuration.cache_dir_path}draft_list.json'
        loaded = self._data_serializer.load(self._file_path)
        if loaded is not None:
            for pack_json in loaded:
                self._packs.append(DraftPack.from_json(pack_json))
    
    @property
    def draft_packs(self) -> List[DraftPack]:
        return copy.deepcopy(self._packs)
    
    @property
    def pack_list_count(self) -> int:
        return len(self._packs)
    
    def resource_list_for_pack(self, pack_index: int, aggregate_list: bool = True) -> List[LocalCardResource]:
        if pack_index >= 0 and pack_index < len(self._packs):
            result = self.draft_packs[pack_index].draft_list
            return result
        return []
    
    @property
    def pack_names(self) -> List[str]:
        return list(map(lambda x: x.pack_name, self._packs))
    
    def pack_name(self, pack_index: int) -> Optional[str]:
        if pack_index >= 0 and pack_index < len(self._packs):
            return self.pack_names[pack_index]
        
    def pack_for_draft_pack_name(self, draft_pack_name: Optional[str]) -> Optional[DraftPack]:
        if draft_pack_name is None:
            return None
        found: List[DraftPack] = list(filter(lambda x: x.pack_name == draft_pack_name, self._packs))
        if len(found) > 0:
            return found[0]
        return None
    
    def pack_index_for_draft_pack_identifier(self, draft_pack_identifier: str) -> Optional[int]:
        found: List[DraftPack] = list(filter(lambda x: x.pack_identifier == draft_pack_identifier, self._packs))
        if len(found) > 0:
            return self._packs.index(found[0])
        return None
    
    # MARK: - modify packs
    def clear_entire_draft_list(self):
        self._packs: List[DraftPack] = []
        self.create_new_pack()
        self._notify_and_save_temp_list()
        
    def keep_packs_clear_lists(self):
        for p in self._packs:
            p.clear_draft_list()
        self._notify_and_save_temp_list()
        
    def create_new_pack(self):
        starting_counter = len(self._packs) + 1
        name = f"New Pack {starting_counter}"
        while True:
            name = f"New Pack {starting_counter}"
            if name not in self.pack_names:
                break
            starting_counter += 1
        new_pack = DraftPack(name)
        self._packs.append(new_pack)
        self._notify_and_save_temp_list()
        
    def update_pack_name(self, pack_index: int, name: str):
        if pack_index >= 0 and pack_index < len(self._packs):
            pack = self._packs[pack_index]
            pack.update_pack_name(name)
            self._notify_and_save_temp_list()
            
    def remove_pack(self, pack_index: int):
        if pack_index >= 0 and pack_index < len(self._packs):
            del self._packs[pack_index]
            
            if len(self._packs) == 0:
                self.create_new_pack()
            
            self._notify_and_save_temp_list()
    
    # MARK: - modify resource order
    def add_resource_to_pack(self, pack_index: int, local_resource: LocalCardResource):
        if local_resource.trading_card is None:
            raise Exception("No underlying trading card. Use another.")
        if pack_index >= 0 and pack_index < len(self._packs):
            self._packs[pack_index].add_resource(local_resource)
            self._notify_and_save_temp_list()
            
    def remove_resource(self, pack_index: int, resource_index: int):
        if pack_index >= 0 and pack_index < len(self._packs):
            self._packs[pack_index].remove_resource(resource_index)
            self._notify_and_save_temp_list()

    def move_up(self, pack_index: int, resource_index: int):
        if pack_index >= 0 and pack_index < len(self._packs):
            self._packs[pack_index].move_up(resource_index)
            self._notify_and_save_temp_list()
        
    def move_down(self, pack_index: int, resource_index: int):
        if pack_index >= 0 and pack_index < len(self._packs):
            self._packs[pack_index].move_down(resource_index)
            self._notify_and_save_temp_list()
        
        
    def insert_above(self, pack_index: int, resource_index: int, local_resource: LocalCardResource):
        if pack_index >= 0 and pack_index < len(self._packs):
            self._packs[pack_index].insert_above(resource_index, local_resource)
            self._notify_and_save_temp_list()
        
    def insert_below(self, pack_index: int, resource_index: int, local_resource: LocalCardResource):
        if pack_index >= 0 and pack_index < len(self._packs):
            self._packs[pack_index].insert_below(resource_index, local_resource)
            self._notify_and_save_temp_list()
    
    
    def _notify_and_save_temp_list(self):
        self._data_serializer.save_json_data(self._file_path, self._packs)
        self._observation_tower.notify(DraftListUpdatedEvent())
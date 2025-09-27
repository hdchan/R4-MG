import copy
from typing import List, Optional

from AppCore.Config import *
from AppCore.Models import DraftPack, LocalCardResource
from AppCore.Observation import ObservationTower
from AppCore.Observation.Events import DraftListUpdatedEvent, DraftPackUpdatedEvent
from AppCore.Service.DataSerializer import DataSerializer

class DataSourceDraftList:
    
    def __init__(self, 
                 configuration_manager: ConfigurationManager,
                 observation_tower: ObservationTower, 
                 data_serializer: DataSerializer):
        self._configuration_manager = configuration_manager
        self._observation_tower = observation_tower
        self._data_serializer = data_serializer
        
        self._packs: List[DraftPack] = []
        
        self._file_path = f'{self._configuration_manager.configuration.draft_lists_dir_path}draft_list.json'
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
    
    @property
    def pack_names(self) -> List[str]:
        return list(map(lambda x: x.pack_name, self._packs))
    
    def pack_name(self, pack_index: int) -> Optional[str]:
        if pack_index >= 0 and pack_index < len(self._packs):
            return self.pack_names[pack_index]
        
    def pack_for_draft_pack_identifier(self, draft_pack_identifier: Optional[str]) -> Optional[DraftPack]:
        if draft_pack_identifier is None:
            return None
        found: List[DraftPack] = list(filter(lambda x: x.pack_identifier == draft_pack_identifier, self._packs))
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
        self._save_and_notify_draft_pack_update()
        self.create_new_pack() # TODO: Move this line to UI? or move UI line to DS?
        
    def keep_packs_clear_lists(self):
        for p in self._packs:
            p.clear_draft_list()
        self._save_and_notify_draft_pack_update()
        
    def create_new_pack(self):
        starting_counter = len(self._packs) + 1
        name = f"New Pack {starting_counter}"
        while True:
            name = f"New Pack {starting_counter}"
            if name not in self.pack_names:
                break
            starting_counter += 1
        new_pack = DraftPack.new_draft_pack(name)
        self._packs.append(new_pack)
        self._save_and_notify_draft_pack_update()
        
    def update_pack_name(self, pack_index: int, name: str):
        if pack_index >= 0 and pack_index < len(self._packs):
            pack = self._packs[pack_index]
            pack.update_pack_name(name)
            self._save_and_notify_draft_pack_update()
            
    def remove_pack(self, pack_index: int):
        if pack_index >= 0 and pack_index < len(self._packs):
            del self._packs[pack_index]
            
            if len(self._packs) == 0:
                self.create_new_pack()
            
            self._save_and_notify_draft_pack_update()
            
    def move_pack_left(self, pack_index: int):
        if pack_index >= 0 and pack_index < len(self._packs):
            self._swap_pack_positions(pack_index, pack_index - 1)
    
    def move_pack_right(self, pack_index: int):
        if pack_index >= 0 and pack_index < len(self._packs):
            self._swap_pack_positions(pack_index, pack_index + 1)
        
    def _swap_pack_positions(self, pi1: int, pi2: int):
        if pi1 >= 0 and pi1 < len(self._packs) and pi2 >= 0 and pi2 < len(self._packs):
            self._packs[pi1], self._packs[pi2] = self._packs[pi2], self._packs[pi1]
            self._save_and_notify_draft_pack_update()
    
    # MARK: - modify resource order
    def add_resource_to_pack(self, pack_index: int, local_resource: LocalCardResource):
        if local_resource.trading_card is None:
            raise Exception("No underlying trading card. Use another.")
        if pack_index >= 0 and pack_index < len(self._packs):
            self._packs[pack_index].add_resource(local_resource)
            event_type = DraftListUpdatedEvent.AddedResource(len(self._packs) - 1, copy.deepcopy(local_resource))
            self._save_and_notify_draft_list_update(self._packs[pack_index], event_type)
            
    def remove_resource(self, pack_index: int, resource_index: int):
        if pack_index >= 0 and pack_index < len(self._packs):
            self._packs[pack_index].remove_resource(resource_index)
            event_type = DraftListUpdatedEvent.RemovedResource(index=resource_index)
            self._save_and_notify_draft_list_update(self._packs[pack_index], event_type)

    def move_up(self, pack_index: int, resource_index: int):
        if pack_index >= 0 and pack_index < len(self._packs):
            self._packs[pack_index].move_up(resource_index)
            event_type = DraftListUpdatedEvent.SwappedResources(index_1=resource_index, index_2=resource_index - 1)
            self._save_and_notify_draft_list_update(self._packs[pack_index], event_type)
        
    def move_down(self, pack_index: int, resource_index: int):
        if pack_index >= 0 and pack_index < len(self._packs):
            self._packs[pack_index].move_down(resource_index)
            event_type = DraftListUpdatedEvent.SwappedResources(index_1=resource_index, index_2=resource_index + 1)
            self._save_and_notify_draft_list_update(self._packs[pack_index], event_type)
        
        
    def insert_above(self, pack_index: int, resource_index: int, local_resource: LocalCardResource):
        if pack_index >= 0 and pack_index < len(self._packs):
            self._packs[pack_index].insert_above(resource_index, local_resource)
            event_type = DraftListUpdatedEvent.InsertedResource(index=resource_index, local_resource=copy.deepcopy(local_resource))
            self._save_and_notify_draft_list_update(self._packs[pack_index], event_type)
        
    def insert_below(self, pack_index: int, resource_index: int, local_resource: LocalCardResource):
        if pack_index >= 0 and pack_index < len(self._packs):
            self._packs[pack_index].insert_below(resource_index, local_resource)
            event_type = DraftListUpdatedEvent.InsertedResource(index=resource_index + 1, local_resource=copy.deepcopy(local_resource))
            self._save_and_notify_draft_list_update(self._packs[pack_index], event_type)
    
    
    def _save_and_notify_draft_pack_update(self):
        self._data_serializer.save_json_data(self._file_path, self._packs)
        self._observation_tower.notify(DraftPackUpdatedEvent())
        
    def _save_and_notify_draft_list_update(self, draft_pack: DraftPack, event_type: DraftListUpdatedEvent.EventType):
        self._data_serializer.save_json_data(self._file_path, self._packs)
        self._observation_tower.notify(DraftListUpdatedEvent(copy.deepcopy(draft_pack), event_type))

from typing import Any, Dict, List
from uuid import UUID, uuid4

from AppCore.Config import *
from AppCore.Models import LocalCardResource


class DraftPack():
        
        class Keys:
            DRAFT_LIST = 'draft_list'
            PACK_NAME = 'pack_name'
        
        
        def __init__(self, 
                     pack_name: str):
            self._draft_list: List[LocalCardResource] = []
            self._pack_name = pack_name
            self._pack_identifier = pack_name
        
        def to_data(self) -> Dict[str, Any]:
            return {
                self.Keys.DRAFT_LIST: self._draft_list,
                self.Keys.PACK_NAME: self._pack_name,
            }

        def __eq__(self, other):  # type: ignore
            if not isinstance(other, DraftPack):
                # don't attempt to compare against unrelated types
                return NotImplemented

            return self._pack_identifier == other._pack_identifier
    
        @classmethod
        def from_json(cls, json: Dict[str, Any]):
            obj = cls.__new__(cls)
            obj._draft_list = []
            for resource_json in json[DraftPack.Keys.DRAFT_LIST]:
                obj._draft_list.append(LocalCardResource.from_json(resource_json))
            obj._pack_name = json[DraftPack.Keys.PACK_NAME]
            obj._pack_identifier = obj._pack_name
            return obj
        
        @property
        def pack_identifier(self) -> str:
            return self._pack_identifier
        
        @property
        def draft_list(self) -> List[LocalCardResource]:
            return self._draft_list
        
        @property
        def pack_name(self) -> str:
            return self._pack_name
        
        @pack_name.setter
        def pack_name(self, value: str):
            self._pack_name = value
        
        def clear_draft_list(self):
            self._draft_list = []
        
        def update_pack_name(self, pack_name: str):
            self._pack_name = pack_name
            
        def add_resource(self, resource: LocalCardResource):
            self._draft_list.append(resource)
            
        def remove_resource(self, resource_index: int):
            if resource_index >= 0 and resource_index < len(self._draft_list):
                del self._draft_list[resource_index]
            
        def move_up(self, resource_index: int):
            self._swap_resources(resource_index, resource_index - 1)
            
        def move_down(self, resource_index: int):
            self._swap_resources(resource_index, resource_index + 1)
            
        def _swap_resources(self, ri1: int, ri2: int):
            if (ri1 < len(self._draft_list) and ri1 >= 0) and (ri2 < len(self._draft_list) and ri2 >= 0):
                self._draft_list[ri1], self._draft_list[ri2] = self._draft_list[ri2], self._draft_list[ri1]
                
        def insert_above(self, resource_index: int, local_resource: LocalCardResource):
            self._insert_resource(resource_index, local_resource)
            
        def insert_below(self, resource_index: int, local_resource: LocalCardResource):
            self._insert_resource(resource_index + 1, local_resource)
            
        def _insert_resource(self, resource_index: int, local_resource: LocalCardResource):
            if resource_index < len(self.draft_list) + 1 and resource_index >= 0:
                self._draft_list.insert(resource_index, local_resource)
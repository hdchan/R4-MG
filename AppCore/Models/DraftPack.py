
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4

from AppCore.Models import LocalCardResource
import copy

class DraftPack():
        
        class Keys:
            DRAFT_LIST = 'draft_list'
            PACK_NAME = 'pack_name'
            PACK_IDENTIFIER = 'pack_identifier'
        
        def __init__(self,
                     pack_name: str, 
                     draft_list: List[LocalCardResource], 
                     pack_identifier: UUID):
            self._draft_list: List[LocalCardResource] = draft_list
            self._pack_name = pack_name
            self._pack_identifier = pack_identifier
        
        # def __hash__(self):
        #     return hash(self.pack_identifier)
        
        def __eq__(self, other):  # type: ignore
            if not isinstance(other, DraftPack):
                # don't attempt to compare against unrelated types
                return NotImplemented

            return self._pack_identifier == other._pack_identifier
        
        def to_data(self) -> Dict[str, Any]:
            return {
                self.Keys.DRAFT_LIST: self._draft_list,
                self.Keys.PACK_NAME: self._pack_name,
                self.Keys.PACK_IDENTIFIER: str(self._pack_identifier)
            }

        @classmethod
        def new_draft_pack(cls, pack_name: str):
            return cls(
                pack_name=pack_name,
                draft_list=[],
                # constructing uuid in default init value can cause collisions
                # not sure why so creating a class method and injecting here
                pack_identifier=uuid4() 
            )

        @classmethod
        def from_json(cls, json: Dict[str, Any]):
            draft_list: List[LocalCardResource] = []
            for resource_json in json[DraftPack.Keys.DRAFT_LIST]:
                draft_list.append(LocalCardResource.from_json(resource_json))
            pack_identifier = uuid4()
            retrieved_identifier_string: Optional[str] = json.get(DraftPack.Keys.PACK_IDENTIFIER, None)
            if retrieved_identifier_string is not None:
                pack_identifier = UUID(retrieved_identifier_string)
            return cls(
                pack_name=json[DraftPack.Keys.PACK_NAME],
                draft_list=draft_list,
                pack_identifier=pack_identifier
            )
        
        @property
        def pack_identifier(self) -> str:
            return str(self._pack_identifier)
        
        @property
        def draft_list(self) -> List[LocalCardResource]:
            return self._draft_list
        
        @property
        def pack_name(self) -> str:
            return self._pack_name
        
        @pack_name.setter
        def pack_name(self, value: str):
            self._pack_name = value
        
        def resource_at_index(self, resource_index: int) -> Optional[LocalCardResource]:
            if resource_index >= 0 and resource_index < len(self._draft_list):
                return copy.deepcopy(self._draft_list[resource_index])

        def mark_resource_as_sideboard(self, resource_index: int, key: str, value: Any):
            if resource_index >= 0 and resource_index < len(self._draft_list):
                self._draft_list[resource_index].set_resource_metadata(key, value)

        def clear_draft_list(self):
            self._draft_list = []
        
        def update_pack_name(self, pack_name: str):
            self._pack_name = pack_name
            
        def add_resource(self, resource: LocalCardResource):
            self._draft_list.append(resource)

        def add_resources(self, resources: List[LocalCardResource]):
            self._draft_list += resources
            
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
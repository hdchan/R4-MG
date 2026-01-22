
from typing import Any, List, Optional

from AppCore.Models import DraftPack, LocalCardResource
from enum import Enum

class DataSourceDraftListProtocol:
    @property
    def draft_packs(self) -> List[DraftPack]:
        raise Exception

    def resource_at_index(self, pack_index: int, resource_index: int) -> Optional[LocalCardResource]:
        if pack_index >= 0 and pack_index < len(self.draft_packs):
                pack = self.draft_packs[pack_index]
                return pack.resource_at_index(resource_index)

    @property
    def draft_pack_flat_list(self) -> List[LocalCardResource]:
        return [item for sublist in self.draft_packs for item in sublist.draft_list]
    
    @property
    def pack_list_count(self) -> int:
        return len(self.draft_packs)
    
    @property
    def pack_names(self) -> List[str]:
        return list(map(lambda x: x.pack_name, self.draft_packs))
    
    def pack_name(self, pack_index: int) -> Optional[str]:
        if pack_index >= 0 and pack_index < len(self.draft_packs):
            return self.pack_names[pack_index]
        
    def pack_for_draft_pack_identifier(self, draft_pack_identifier: Optional[str]) -> Optional[DraftPack]:
        if draft_pack_identifier is None:
            return None
        found: List[DraftPack] = list(filter(lambda x: x.pack_identifier == draft_pack_identifier, self.draft_packs))
        if len(found) > 0:
            return found[0]
        return None
    
    def pack_index_for_draft_pack_identifier(self, draft_pack_identifier: str) -> Optional[int]:
        found: List[DraftPack] = list(filter(lambda x: x.pack_identifier == draft_pack_identifier, self.draft_packs))
        if len(found) > 0:
            return self.draft_packs.index(found[0])
        return None

    # MARK: - modify packs
    def clear_entire_draft_list(self):
        raise Exception
        
    def keep_packs_clear_lists(self):
        raise Exception
        
    def create_new_pack(self) -> int:
        raise Exception

    def create_new_pack_from_list(self, name: str, list: List[LocalCardResource]):
        raise Exception
        
    def update_pack_name(self, pack_index: int, name: str):
        raise Exception
            
    def remove_pack(self, pack_index: int):
        raise Exception
            
    def move_pack_left(self, pack_index: int):
        raise Exception
    
    def move_pack_right(self, pack_index: int):
        raise Exception

    # MARK: - modify resource order
    def add_resource_to_pack(self, pack_index: int, local_resource: LocalCardResource):
        raise Exception
            
    def remove_resource(self, pack_index: int, resource_index: int):
        raise Exception

    def move_up(self, pack_index: int, resource_index: int):
        raise Exception
        
    def move_down(self, pack_index: int, resource_index: int):
        raise Exception
        
    def insert_above(self, pack_index: int, resource_index: int, local_resource: LocalCardResource):
        raise Exception
        
    def insert_below(self, pack_index: int, resource_index: int, local_resource: LocalCardResource):
        raise Exception
    
    def mark_resource_as_sideboard(self, pack_index: int, resource_index: int, key: str, value: Any):
        raise Exception

class DataSourceDraftListProviderConnectionStatus(int, Enum):
    NONE = 0
    IS_HOST = 1
    IS_CLIENT = 2
    ERROR = 3

class DataSourceDraftListProviding:
    @property
    def draft_list_data_source(self) -> DataSourceDraftListProtocol:
        raise Exception

    def connect_as_host(self) -> None:
        raise Exception

    def connect_as_client(self, ip: str, port: Optional[int]) -> None:
        raise Exception

    def disconnect(self) -> None:
        raise Exception

    @property
    def state(self) -> DataSourceDraftListProviderConnectionStatus:
        raise Exception

    @property
    def ip_address(self) -> str:
        raise Exception
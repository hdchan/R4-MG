
from typing import Any, List, Optional

from AppCore.Models import DraftPack, LocalCardResource

class DataSourceDraftListProtocol:
    def resource_at_index(self, pack_index: int, resource_index: int) -> Optional[LocalCardResource]:
        raise Exception

    @property
    def draft_packs(self) -> List[DraftPack]:
        raise Exception

    @property
    def draft_pack_flat_list(self) -> List[LocalCardResource]:
        raise Exception
    
    @property
    def pack_list_count(self) -> int:
        raise Exception
    
    @property
    def pack_names(self) -> List[str]:
        raise Exception
    
    def pack_name(self, pack_index: int) -> Optional[str]:
        raise Exception
        
    def pack_for_draft_pack_identifier(self, draft_pack_identifier: Optional[str]) -> Optional[DraftPack]:
        raise Exception
    
    def pack_index_for_draft_pack_identifier(self, draft_pack_identifier: str) -> Optional[int]:
        raise Exception

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

class DataSourceDraftListProviding:
    @property
    def draft_list_data_source(self) -> DataSourceDraftListProtocol:
        raise Exception
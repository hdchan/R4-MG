
import copy
import io
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

from ..CardSearchFlow import CardSearchFlow
from ..Config import Configuration
from ..Image import ImageResourceDeployer
from . import CardType, ResourceMetadata


class CardMetadataFlow:
    
    def __init__(self,
                 configuration: Configuration,
                 card_search_flow: CardSearchFlow, 
                 image_resource_deployer: ImageResourceDeployer):
        self._card_search_flow = card_search_flow
        self._configuration = configuration
        self._image_resource_deployer = image_resource_deployer
        self._card_type_map: Dict[str, ResourceMetadata] = self._load_metadata()
        
    @property
    def card_type_list(self) -> List[CardType]:
        return list(CardType)
    
    def metadata_for_row(self, row_index: int) -> Optional[ResourceMetadata]:
        file_name = self._image_resource_deployer.production_resources[row_index].file_name
        if file_name in self._card_type_map:
            return self._card_type_map[file_name]
        return None
    
    def set_search_configuration(self, card_type: CardType):
        search_configuration = copy.deepcopy(self._card_search_flow.search_configuration)
        search_configuration.card_type = card_type
        self._card_search_flow.user_update_search_configuration(search_configuration)
    
    def set_card_type_for_deployment_row(self, row_index: int, card_type: CardType):
        file_name = self._image_resource_deployer.production_resources[row_index].file_name
        if file_name not in self._card_type_map:
            self._card_type_map[file_name] = ResourceMetadata()
        self._card_type_map[file_name].card_type = card_type
        self._save_metadata()
    
    def search_with_context_for_row(self, row_index: int):
        search_configuration = copy.deepcopy(self._card_search_flow.search_configuration)
        file_name = self._image_resource_deployer.production_resources[row_index].file_name
        meta_data = self._card_type_map[file_name]
        card_type = meta_data.card_type
        if card_type is not None:
            search_configuration.card_type = card_type
            self._card_search_flow.system_update_search_configuration(search_configuration)
            self._card_search_flow.search("", is_system_initiated=True) # TODO: might want to pass None
    
    @property
    def _file_path(self) -> str:
        return self._configuration.production_file_path + '/metadata.yaml'
    
    def _load_metadata(self) -> Dict[str, ResourceMetadata]:
        mapping: Dict[str, ResourceMetadata] = {}
        my_file = Path(self._file_path)
        if my_file.is_file():
            with open(self._file_path, 'r') as stream:
                data_loaded = yaml.safe_load(stream)
                if data_loaded is not None:
                    for i, k in enumerate(data_loaded):
                        metadata = ResourceMetadata()
                        if data_loaded[k] is not None:
                            metadata.loadJSON(data_loaded[k])
                            mapping[k] = metadata
                    return mapping
        return {}
            
    def _save_metadata(self):
        mapping: Dict[str, Any] = {}
        for i, k in enumerate(self._card_type_map):
            mapping[k] = self._card_type_map[k].toJSON()
        with io.open(self._file_path, 'w', encoding='utf8') as outfile:
            yaml.dump(mapping, outfile, default_flow_style=False, allow_unicode=True)
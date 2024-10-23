
import io
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

from AppCore.ApplicationCore import ApplicationCore
from AppCore.Config import ConfigurationProvider
from AppCore.Models import SearchConfiguration

from .ResourceMetadata import CardType, ResourceMetadata


class CardMetadataFlow:
    
    def __init__(self,
                 configuration_provider: ConfigurationProvider,
                 app_core: ApplicationCore):
        self._configuration_provider = configuration_provider
        self._app_core = app_core
        self._card_type_map: Dict[str, ResourceMetadata] = self._load_metadata()
        
    @property
    def card_type_list(self) -> List[CardType]:
        return list(CardType)
    
    def metadata_for_row(self, row_index: int) -> Optional[ResourceMetadata]:
        file_name = self._app_core.retrieve_production_resource(row_index).file_name
        if file_name in self._card_type_map:
            return self._card_type_map[file_name]
        return None
    
    def search_with_context_for_row(self, row_index: int):
        search_configuration = SearchConfiguration()
        file_name = self._app_core.retrieve_production_resource(row_index).file_name
        meta_data = self._card_type_map[file_name]
        card_type = meta_data.card_type
        if card_type is not None:
            search_configuration.card_type = card_type
            self._app_core.search(search_configuration)
    
    @property
    def _file_path(self) -> str:
        return self._configuration_provider.configuration.production_file_path + '/metadata.yaml'
    
    def _load_metadata(self) -> Dict[str, ResourceMetadata]:
        mapping: Dict[str, ResourceMetadata] = {}
        my_file = Path(self._file_path)
        if my_file.is_file():
            with open(self._file_path, 'r') as stream:
                data_loaded = yaml.safe_load(stream)
                if data_loaded is not None:
                    for _, k in enumerate(data_loaded):
                        metadata = ResourceMetadata()
                        if data_loaded[k] is not None:
                            metadata.loadJSON(data_loaded[k])
                            mapping[k] = metadata
                    return mapping
        return {}
            
    def _save_metadata(self):
        mapping: Dict[str, Any] = {}
        for _, k in enumerate(self._card_type_map):
            mapping[k] = self._card_type_map[k].toJSON()
        with io.open(self._file_path, 'w', encoding='utf8') as outfile:
            yaml.dump(mapping, outfile, default_flow_style=False, allow_unicode=True)
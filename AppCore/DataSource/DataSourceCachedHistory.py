from copy import deepcopy
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from AppCore.Config import ConfigurationManager
from AppCore.ImageResource.ImageResourceProcessorProvider import \
    ImageResourceProcessorProviding
from AppCore.Models import LocalCardResource
from AppCore.Observation import ObservationTower
from AppCore.Observation.Events import \
    LocalCardResourceSelectedFromDataSourceEvent, CacheHistoryUpdatedEvent
from AppCore.Service import DataSerializer

from ..Models.DataSourceSelectedLocalCardResource import \
    DataSourceSelectedLocalCardResourceProtocol

class DataSourceCachedHistory(DataSourceSelectedLocalCardResourceProtocol):
    class Keys:
        DATETIME = 'datetime'
        LOCAL_RESOURCE = 'resource'

    class DataSourceCachedHistoryConfiguration:
        def __init__(self,
                     cache_history_page_size: int = 100,
                     cache_history_identifier: Optional[str] = None):
            self.cache_history_identifier = cache_history_identifier
            self.cache_history_page_size = cache_history_page_size

    def __init__(self, 
                 observation_tower: ObservationTower, 
                 image_resource_processor_provider: ImageResourceProcessorProviding, 
                 configuration_manager: ConfigurationManager, 
                 data_serializer: DataSerializer, 
                 configuration: DataSourceCachedHistoryConfiguration):
        self._observation_tower = observation_tower
        self._image_resource_processor_provider = image_resource_processor_provider
        self._configuration_manager = configuration_manager
        self._data_serializer = data_serializer
        self._configuration = configuration
        self._cached_history: List[Tuple[LocalCardResource, datetime]] = []
        
        Path(self._configuration_manager.configuration.cache_history_dir_path).mkdir(parents=True, exist_ok=True)

        self._cache_history_path: Optional[str] = None
        if self._configuration.cache_history_identifier is not None:
            self._cache_history_path = f'{self._configuration_manager.configuration.cache_history_dir_path}{configuration.cache_history_identifier}.json'
            
            loaded = self._data_serializer.load(self._cache_history_path)
            if loaded is not None:
                for l in loaded:
                    try:
                        self._cached_history.append((LocalCardResource.from_json(l[self.Keys.LOCAL_RESOURCE]), datetime.fromtimestamp(l[self.Keys.DATETIME])))
                    except: 
                        continue
                
        self._selected_index: Optional[int] = None
        self._selected_resource: Optional[LocalCardResource] = None
    
    @property
    def selected_local_resource(self) -> Optional[LocalCardResource]:
        if self._selected_resource is not None:
            return self._selected_resource
        return None
    
    @property
    def cached_resources_history(self) -> List[Tuple[LocalCardResource, datetime]]:
        return self._cached_history
    
    def select_card_resource_for_card_selection(self, index: int):
        if index < len(self._cached_history):
            if self._selected_index == index:
                return
            self._selected_index = index
            self._retrieve_card_resource_for_card_selection(index)
    
    def _retrieve_card_resource_for_card_selection(self, index: int, retry: bool = False):
        selected_resource = self._cached_history[index][0]
        self._selected_resource = selected_resource
        self._observation_tower.notify(LocalCardResourceSelectedFromDataSourceEvent(deepcopy(selected_resource), self))
        self._image_resource_processor_provider.image_resource_processor.async_store_local_resource(selected_resource, retry)
    
    def add_resource_and_save(self, local_resource: LocalCardResource, datetime: datetime = datetime.now()):
        self.add_resource(local_resource, datetime)
        self.save_data()

    def add_resource(self, local_resource: LocalCardResource, datetime: datetime = datetime.now()):
        self._cached_history.insert(0, (local_resource, datetime))
        self._observation_tower.notify(CacheHistoryUpdatedEvent())

    def save_data(self):
        # save async
        if self._cache_history_path is None or self._configuration.cache_history_page_size == 0:
            return
        data: List[Dict[str, Any]] = []
        for e in self._cached_history[:self._configuration.cache_history_page_size]:
            data.append({
                self.Keys.LOCAL_RESOURCE: e[0],
                self.Keys.DATETIME: e[1].timestamp()
            })
        self._data_serializer.save_json_data(self._cache_history_path, data)
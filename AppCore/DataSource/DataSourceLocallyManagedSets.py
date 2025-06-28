import os
import re
from io import TextIOWrapper
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from urllib import request

from PyQt5.QtCore import QObject, QRunnable, QThreadPool, pyqtSignal

from AppCore.Config import *
from AppCore.Models import LocalAssetResource, TradingCard
from AppCore.Observation import ObservationTower
from AppCore.Observation.Events import LocalAssetResourceFetchEvent
from AppCore.Service import DataSerializer


class DataSourceLocallyManagedSetsClientProtocol:
    def parse_asset(self, file: TextIOWrapper) -> List[TradingCard]:
        return NotImplemented
    
    def remote_url(self, deck_identifier: str) -> str:
        return  NotImplemented
    
    # should be constant, and not change
    @property
    def domain_identifier(self) -> str:
        return NotImplemented
    
    @property
    def file_extension(self) -> str:
        return NotImplemented

ASSET_TYPE_IDENTIFIER = 'managed_deck'

class DataSourceLocallyManagedSets:
    '''
    This class relies on the LocalAssetResource structure regarding temp files
    ready file = <asset_type>.<domain>.<deck_identifier>
    loading file = <asset_type>.<domain>.<deck_identifier>.temp
    '''
    def __init__(self, 
                 configuration_manager: ConfigurationManager,
                 observation_tower: ObservationTower,
                 data_serializer: DataSerializer,
                 client: DataSourceLocallyManagedSetsClientProtocol):
        self._configuration_manager = configuration_manager
        self._observation_tower = observation_tower
        self._data_serializer = data_serializer
        self._client = client
        self.pool = QThreadPool()
        self._hashed_cached_card_list: Dict[str, List[TradingCard]] = {}
    
    @property
    def _configuration(self) -> Configuration:
        return self._configuration_manager.configuration
    
    @property
    def _asset_dir_path(self) -> str:
        return self._configuration.assets_dir_path
    
    @property
    def _flat_mapped_hashed_cached_card_list(self) -> List[TradingCard]:
        result: List[TradingCard] = []
        for i in self._hashed_cached_card_list.values():
            result += i
        return result
    
    def retrieve_card_list(self) -> List[TradingCard]:
        if len(self._flat_mapped_hashed_cached_card_list) > 0:
            return self._flat_mapped_hashed_cached_card_list
        
        file_list = os.listdir(self._asset_dir_path)
        ready_resources = list(filter(None, map(self._map_ready_files_to_resource, file_list)))
        for resource in ready_resources:
            self._hashed_cached_card_list[resource.asset_path] = self.retrieve_set_card_list(resource)
        
        return self._flat_mapped_hashed_cached_card_list
    
    def retrieve_set_card_list(self, resource: LocalAssetResource) -> List[TradingCard]:
        if resource.asset_path in self._hashed_cached_card_list:
            return self._hashed_cached_card_list[resource.asset_path]
        
        # we don't want to cache this based on the retrieval logic above
        try:
            with open(resource.asset_path, 'r') as f:
                return self._client.parse_asset(f)
        except:
            raise Exception(f'Invalid deck: "{resource.display_name}"')
        
    
    @property
    def deck_resources(self) -> List[LocalAssetResource]:
        Path(self._asset_dir_path).mkdir(parents=True, exist_ok=True)
        file_list = os.listdir(self._asset_dir_path)
        
        ready_resources = list(filter(None, map(self._map_ready_files_to_resource, file_list)))
        loading_resources = list(filter(None, map(self._map_loading_files_to_resource, file_list)))
        
        # temp files may be the same as ready files...need to get a set from the list
        return list(set(sorted(ready_resources + loading_resources, key=lambda resource: resource.display_name)))
    
    def download(self, deck_identifier: str, force_download: bool = False):
        domain_identifier = self._replace_non_alphanumeric(self._client.domain_identifier, "_")
        sanitized_deck_identifier = self._replace_non_alphanumeric(deck_identifier.strip(), "") # NOTE: Assuming alphanumeric
        file_name = f'{ASSET_TYPE_IDENTIFIER}.{domain_identifier}.{sanitized_deck_identifier}'
        
        resource = LocalAssetResource(asset_dir=self._asset_dir_path, 
                                     file_name=file_name, 
                                     file_extension=self._client.file_extension, 
                                     display_name=file_name, 
                                     remote_url=self._client.remote_url(deck_identifier))
        
        if force_download:
            Path(resource.asset_path).unlink()
            
        open(resource.asset_temp_path, 'a').close() # add temp file
        
        initial_event = LocalAssetResourceFetchEvent(LocalAssetResourceFetchEvent.EventType.STARTED, 
                                                     resource)
        self._observation_tower.notify(initial_event)
        
        
        def finished(result: Tuple[LocalAssetResource, Optional[Exception]]):
            resource, error = result
            Path(resource.asset_temp_path).unlink() # remote temp file
            if error is None:
                success_event = LocalAssetResourceFetchEvent(LocalAssetResourceFetchEvent.EventType.FINISHED, 
                                                             resource)
                success_event.predecessor = initial_event
                self._observation_tower.notify(success_event)
            else:
                failed_event = LocalAssetResourceFetchEvent(LocalAssetResourceFetchEvent.EventType.FAILED,
                                                            resource)
                failed_event.predecessor = initial_event
                self._observation_tower.notify(failed_event)
            self._invalidate_cached_card_list()
            
        
        worker = StoreAssetWorker(resource, self._client, self._data_serializer)
        worker.signals.finished.connect(finished)
        self.pool.start(worker)
    
    def _invalidate_cached_card_list(self):
        self._hashed_cached_card_list = {}
    
    def remove(self, resource: LocalAssetResource):
        Path(resource.asset_path).unlink()
        self._invalidate_cached_card_list()
    
    def _path_for_deck_identifier(self, deck_identifier: str) -> str:
        file_name = self._replace_non_alphanumeric(self._client.remote_url(deck_identifier), "_")
        path = f'{self._asset_dir_path}{file_name}.{self._client.file_extension}'
        return path
    
    def _filter_managed_deck_file(self, file_name: str) -> bool:
            components = file_name.split('.') # assuming structure
            if len(components) >= 3:
                if (components[0] == ASSET_TYPE_IDENTIFIER and 
                    components[1] == self._replace_non_alphanumeric(self._client.domain_identifier, "_")):
                    return True
            return False
    
    def _filter_managed_deck_file_ready(self, file_name: str) -> bool:
        components = file_name.split('.')
        return components[-1] != 'temp' and self._filter_managed_deck_file(file_name)
    
    def _filter_managed_deck_file_loading(self, file_name: str) -> bool:
        return not self._filter_managed_deck_file_ready(file_name)
    
    def _map_ready_files_to_resource(self, file_name: str) -> Optional[LocalAssetResource]:
        if self._filter_managed_deck_file_ready(file_name):
            components = file_name.split('.')
            if len(components) >= 3:
                path = Path(file_name)
                return LocalAssetResource(asset_dir=self._asset_dir_path,
                                          file_name=path.stem,
                                          file_extension=path.suffix.removeprefix("."), # may need to rework Local Asset model
                                          display_name=components[2])
        return None
    
    def _map_loading_files_to_resource(self, file_name: str) -> Optional[LocalAssetResource]:
        if self._filter_managed_deck_file_loading(file_name):
            components = file_name.split('.')[:-1] # assuming .temp is at the end, we exclude it
            updated_file_name = '.'.join(components)
            if len(components) >= 3:
                path = Path(updated_file_name)
                return LocalAssetResource(asset_dir=self._asset_dir_path,
                                          file_name=path.stem,
                                          file_extension=path.suffix.removeprefix("."), # may need to rework Local Asset model
                                          display_name=components[2])
            
        return None
        
    def _replace_non_alphanumeric(self, text: str, replacement: str = '') -> str:
        return re.sub(r'[^a-zA-Z0-9]', replacement, text)
        
    
class WorkerSignals(QObject):
    finished = pyqtSignal(object)

class StoreAssetWorker(QRunnable):
    def __init__(self, 
                 resource: LocalAssetResource,
                 client: DataSourceLocallyManagedSetsClientProtocol, 
                 data_serializer: DataSerializer):
        super(StoreAssetWorker, self).__init__()
        self.resource = resource
        self.client = client
        self.data_serializer = data_serializer
        self.signals = WorkerSignals()

    def run(self):
        if self.resource.remote_url is not None:
            try:
                req = request.Request(self.resource.remote_url)
                buf = request.urlopen(req)
                # TODO: if exists, then create backup and create new file?
                self.data_serializer.save_buffer_data(self.resource.asset_path, buf)
                self.signals.finished.emit((self.resource, None))
            except Exception as error:
                self.signals.finished.emit((self.resource, error))
        else:
            self.signals.finished.emit((self.resource, Exception('No asset url')))
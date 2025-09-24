import os
import shutil
from copy import deepcopy
from pathlib import Path
from typing import List, Optional
from PyQt5.QtCore import QMutex, QObject, QRunnable, QThreadPool, pyqtSignal
from PIL import Image

from AppCore.Config import Configuration
from AppCore.ImageFetcher.ImageFetcherProvider import *
from AppCore.Models import DeploymentCardResource, LocalCardResource
from AppCore.Observation import *
from AppCore.Observation.Events import (DeploymentCardResourceEvent,
                                        ProductionCardResourcesLoadEvent,
                                        PublishStagedCardResourcesEvent,
                                        PublishStatusUpdatedEvent)

from ..ImageResource.ImageResourceProcessorProtocol import *

PNG_EXTENSION = 'png'

class ProductionLocalCardResource(LocalCardResource):
    def __init__(self, 
                 image_dir: str,
                 image_preview_dir: str,
                 file_name: str,
                 display_name: str,
                 display_name_short: str,
                 display_name_detailed: str):
        super().__init__(image_dir=image_dir,
                         image_preview_dir=image_preview_dir,
                         file_name=file_name, display_name=display_name,
                         display_name_short=display_name_short,
                         display_name_detailed=display_name_detailed, 
                         can_generate_placeholder=True)
 
class DataSourceImageResourceDeployer:
    def __init__(self,
                 configuration_manager: ConfigurationManager, 
                 observation_tower: ObservationTower, 
                 image_resource_processor_provider: ImageResourceProcessorProviding):
        self._observation_tower = observation_tower
        self._configuration_manager = configuration_manager
        self._image_resource_processor_provider = image_resource_processor_provider
        self._deployment_resources: List[DeploymentCardResource] = []
        self._can_publish_state = len(self._deployment_resources) != 0
        self._is_publishing = False
        
        self.pool = QThreadPool()
        self.mutex = QMutex()

    @property
    def deployment_resources(self) -> List[DeploymentCardResource]:
        return deepcopy(self._deployment_resources)
    
    def deployment_resource_for_file_name(self, file_name: str) -> Optional[DeploymentCardResource]:
        results = list(filter(lambda x: x.production_resource.file_name_with_ext == file_name, self.deployment_resources))
        if len(results) == 0:
            return None
        return results[0]

    @property
    def _configuration(self) -> Configuration:
        return self._configuration_manager.configuration
    
    @property
    def _image_resource_processor(self) -> ImageResourceProcessorProtocol:
        return self._image_resource_processor_provider.image_resource_processor
    
    def load_production_resources(self):
        """
        Will load images from production folder
        """
        
        start_load_event = ProductionCardResourcesLoadEvent(ProductionCardResourcesLoadEvent.EventType.STARTED)
        self._observation_tower.notify(start_load_event)
        
        self._generate_directories_if_needed()
        deployment_resources: List[DeploymentCardResource] = []
        file_list = os.listdir(self._configuration.production_dir_path)
        
        for production_file_name_with_ext in file_list[:]:
            path = Path(production_file_name_with_ext)
            if path.suffix == f'.{PNG_EXTENSION}':
                resource = ProductionLocalCardResource(image_dir=self._configuration.production_dir_path,
                                                       image_preview_dir=self._configuration.production_preview_dir_path, 
                                                       file_name=path.stem,
                                                       display_name=path.stem + path.suffix,
                                                       display_name_short=path.stem + path.suffix,
                                                       display_name_detailed=path.stem + path.suffix)
                
                staged_resource = DeploymentCardResource(resource)
                deployment_resources.append(staged_resource)

                if not resource.is_preview_ready:
                    self._image_resource_processor.regenerate_resource_preview(resource)

        # Maintains any existing staged resources when loading, removes any deleted prod files, and appends new prod files
        latest_prod_resources = list(map(lambda x: x.production_resource, deployment_resources))
        maintain_existing = list(filter(lambda x: x.production_resource in latest_prod_resources, self._deployment_resources))
        mapped_existing_prod_resources = list(map(lambda x: x.production_resource, maintain_existing))
        new_additions = list(filter(lambda x: x.production_resource not in mapped_existing_prod_resources, deployment_resources))
        
        
        self._deployment_resources = maintain_existing + new_additions
        
        if self._configuration.deployment_list_sort_criteria == Configuration.Settings.DeploymentListSortCriteria.FILE_NAME:
            self._deployment_resources.sort(key=lambda x: x.production_resource.file_name, reverse=self._configuration.deployment_list_sort_is_desc_order)
        elif self._configuration.deployment_list_sort_criteria == Configuration.Settings.DeploymentListSortCriteria.CREATED_DATE:
            self._deployment_resources.sort(key=lambda x: x.production_resource.created_date, reverse=self._configuration.deployment_list_sort_is_desc_order)
        
        finish_load_event = ProductionCardResourcesLoadEvent(ProductionCardResourcesLoadEvent.EventType.FINISHED)
        finish_load_event.predecessor = start_load_event
        self._observation_tower.notify(finish_load_event)

    def latest_deployment_resource(self, deployment_resource: DeploymentCardResource) -> Optional[DeploymentCardResource]:
        for r in self._deployment_resources:
            if r.production_resource == deployment_resource.production_resource:
                return deepcopy(r)
        return None

    def stage_resource(self, deployment_resource: DeploymentCardResource, selected_resource: LocalCardResource):
        for r in self._deployment_resources:
            if r.production_resource == deployment_resource.production_resource:
                r.stage(selected_resource)
                self._observation_tower.notify(DeploymentCardResourceEvent(r, DeploymentCardResourceEvent.EventType.STAGED))
        self._notify_publish_status_changed_if_needed()
        
    def unstage_resource(self, deployment_resource: DeploymentCardResource):
        for r in self._deployment_resources:
            if r.production_resource == deployment_resource.production_resource:
                r.clear_staged_resource()
                self._observation_tower.notify(DeploymentCardResourceEvent(r, DeploymentCardResourceEvent.EventType.CLEARED))
        self._notify_publish_status_changed_if_needed()

    def unstage_all_resources(self):
        for r in self._deployment_resources:
            self.unstage_resource(r)

    @property
    def can_publish_staged_resources(self) -> bool:
        result = False
        for i in self._deployment_resources:
            if i.can_publish_staged_resource:
                result = True
        return result

    def publish_staged_resources(self):
        """
        Publishes staged resources. Returns True if success.
        Otherwise returns false.
        """
        # if self._is_publishing:
        #     print("Can't publish right now")
        #     return
        
        self._is_publishing = True
        deployment_resources_copy = deepcopy(self._deployment_resources)
        initial_event = PublishStagedCardResourcesEvent(PublishStagedCardResourcesEvent.EventType.STARTED, deployment_resources_copy)
        self._observation_tower.notify(initial_event)
        if self.can_publish_staged_resources: # don't publish resources if one does not work
            self._generate_directories_if_needed()
            for r in self._deployment_resources:
                if r.staged_resource is not None:
                    # time.sleep(3)
                    production_dir_path = f'{self._configuration.production_dir_path}{r.production_resource.file_name_with_ext}'
                    production_preview_dir_path = f'{self._configuration.production_preview_dir_path}{r.production_resource.file_name_with_ext}'
                    # Resize if needed
                    if self._configuration.resize_prod_images and not r.staged_resource.is_local_only:
                        assert(not r.staged_resource.is_local_only) # Don't resize local only resources, assume that these are custom assets
                        cached_image = Image.open(r.staged_resource.image_path)
                        downscaled_image = self._image_resource_processor.down_scale_image(cached_image, self._configuration.resize_prod_images_max_size)
                        downscaled_image.save(production_dir_path)
                    else:
                        shutil.copy(r.staged_resource.image_path, production_dir_path)
                    try:
                        shutil.copy(r.staged_resource.image_preview_path, production_preview_dir_path) # raises exception can ignore
                    except:
                        Path(production_preview_dir_path).unlink() # remove previous preview file
                        # gets regenerated from reload
                        # do nothing because preview file is not critical, or maybe can regenerate file
                        
            # def finished():
            self.unstage_all_resources()
            finished_event = PublishStagedCardResourcesEvent(PublishStagedCardResourcesEvent.EventType.FINISHED, deployment_resources_copy)
            finished_event.predecessor = initial_event
            self._observation_tower.notify(finished_event)
            
            # NOTE: background thread causing crash when spamming publish from draft list, may need to add state for process of publishing
            # worker = PublishResourcesWorker(self._deployment_resources, self._configuration_manager, self._image_resource_processor_provider)
            # worker.signals.finished.connect(finished)
            # self.pool.start(worker)
            
        else:
            self._notify_publish_status_changed_if_needed()
            failed_event = PublishStagedCardResourcesEvent(PublishStagedCardResourcesEvent.EventType.FAILED, deployment_resources_copy)
            failed_event.predecessor = initial_event
            self._observation_tower.notify(failed_event)
            raise Exception("Failed to publish. Please redownload resources and retry.")
        
        # self._is_publishing = False
        
    def generate_new_file(self, file_name: str, placeholder_image_path: Optional[str]):
        local_resource = ProductionLocalCardResource(image_dir=self._configuration.production_dir_path,
                                                     image_preview_dir=self._configuration.production_preview_dir_path,
                                                     file_name=file_name,
                                                     display_name=file_name,
                                                     display_name_short=file_name,
                                                     display_name_detailed=file_name)
        self._image_resource_processor.generate_placeholder(local_resource, placeholder_image_path)

    def _notify_publish_status_changed_if_needed(self):
        if self._can_publish_state != self.can_publish_staged_resources:
            self._can_publish_state = self.can_publish_staged_resources
            self._observation_tower.notify(PublishStatusUpdatedEvent(self._can_publish_state))


    def _generate_directories_if_needed(self):
        Path(self._configuration.production_preview_dir_path).mkdir(parents=True, exist_ok=True)
        
        
class WorkerSignals(QObject):
    finished = pyqtSignal(object)

class PublishResourcesWorker(QRunnable):
    def __init__(self, 
                 deployment_resources: List[DeploymentCardResource], 
                 configuration_manager: ConfigurationManager, 
                 image_resource_processor_provider: ImageResourceProcessorProviding):
        super().__init__()
        self._deployment_resources = deployment_resources
        self._configuration_manager = configuration_manager
        self._image_resource_processor_provider = image_resource_processor_provider
        self.signals = WorkerSignals()

    @property
    def _configuration(self) -> Configuration:
        return self._configuration_manager.configuration

    @property
    def _image_resource_processor(self) -> ImageResourceProcessorProtocol:
        return self._image_resource_processor_provider.image_resource_processor
    
    def run(self):
        for r in self._deployment_resources:
            if r.staged_resource is not None:
                # time.sleep(3)
                production_dir_path = f'{self._configuration.production_dir_path}{r.production_resource.file_name_with_ext}'
                production_preview_dir_path = f'{self._configuration.production_preview_dir_path}{r.production_resource.file_name_with_ext}'
                # Resize if needed
                if self._configuration.resize_prod_images and not r.staged_resource.is_local_only:
                    assert(not r.staged_resource.is_local_only) # Don't resize local only resources, assume that these are custom assets
                    cached_image = Image.open(r.staged_resource.image_path)
                    downscaled_image = self._image_resource_processor.down_scale_image(cached_image, self._configuration.resize_prod_images_max_size)
                    downscaled_image.save(production_dir_path)
                else:
                    shutil.copy(r.staged_resource.image_path, production_dir_path)
                try:
                    shutil.copy(r.staged_resource.image_preview_path, production_preview_dir_path) # raises exception can ignore
                except:
                    Path(production_preview_dir_path).unlink() # remove previous preview file
                    # gets regenerated from reload
                    # do nothing because preview file is not critical, or maybe can regenerate file
        self.signals.finished.emit(None)
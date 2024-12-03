import os
import shutil
import time
from pathlib import Path
from typing import List, Optional

from PIL import Image
from PyQt5.QtCore import QThreadPool, pyqtSignal, QObject, QRunnable
from AppCore.Models import LocalCardResource
from AppCore.Observation import *
from AppCore.Observation.Events import (PublishStagedResourcesEvent,
                                        PublishStatusUpdatedEvent)

from ..ImageNetwork.ImageFetcherProvider import *

PNG_EXTENSION = '.png'
THUMBNAIL_SIZE = 256

class StagedCardResource:
    def __init__(self, local_card_resource: LocalCardResource, production_resource: LocalCardResource):
        self.local_card_resource = local_card_resource
        self.production_resource = production_resource

class ImageResourceDeployerDelegate:
    def rd_did_load_production_resources(self, rd: ..., local_resources: List[LocalCardResource]) -> None:
        pass
    
class ImageResourceDeployer:
    def __init__(self,
                 configuration_provider: ConfigurationProviderProtocol, 
                 observation_tower: ObservationTower):
        self.observation_tower = observation_tower
        self.configuration_provider = configuration_provider
        self.production_resources: List[LocalCardResource] = []
        self.staged_resources: List[StagedCardResource] = []
        self._can_publish_state = len(self.staged_resources) != 0
        self.pool = QThreadPool()
        self.delegate: Optional[ImageResourceDeployerDelegate]

    @property
    def configuration(self) -> Configuration:
        return self.configuration_provider.configuration
    
    def _downscale_image(self, original_img: Image.Image) -> Image.Image:
            size = THUMBNAIL_SIZE, THUMBNAIL_SIZE
            preview_img = original_img.copy().convert('RGBA')
            preview_img.thumbnail(size, Image.Resampling.BICUBIC)
            return preview_img
    
    def load_production_resources(self):
        """
        Will load images from production folder
        """
        self._generate_directories_if_needed()
        local_resources: List[LocalCardResource] = []
        filelist = os.listdir(self.configuration.production_file_path)
        filelist.sort()
        for production_file_name_with_ext in filelist[:]:
            path = Path(production_file_name_with_ext)
            if path.suffix == PNG_EXTENSION:
                resource = LocalCardResource(image_dir=self.configuration.production_file_path, 
                                             image_preview_dir=self.configuration.production_preview_file_path, 
                                             file_name=path.stem,
                                             display_name=path.stem + path.suffix,
                                             display_name_short=path.stem + path.suffix,
                                             display_name_detailed=path.stem + path.suffix,
                                             file_extension=path.suffix)
                local_resources.append(resource)

                if not Path(resource.image_preview_path).is_file():
                    # regnerate preview file
                    large_img = Image.open(resource.image_path)
                    preview_img = self._downscale_image(large_img)
                    preview_img.save(resource.image_preview_path)

        self.production_resources = local_resources
        if self.delegate is not None:
            self.delegate.rd_did_load_production_resources(self, local_resources)

    def stage_resource(self, local_card_resource: LocalCardResource, index: int):
        # Cache emptied handled on UI
        self.unstage_resource(index)
        staged_card_resource = StagedCardResource(local_card_resource, 
                                                  self.production_resources[index])
        self.staged_resources.append(staged_card_resource)
        self._notify_publish_status_changed_if_needed()
        assert(len(self.staged_resources) <= len(self.production_resources)) # should never have more staged resources than production resources

    def unstage_resource(self, index: int):
        production_resource = self.production_resources[index]
        for i, resource in enumerate(self.staged_resources):
            if resource.production_resource == production_resource:
                self.staged_resources.pop(i)
        self._notify_publish_status_changed_if_needed()
        assert(len(self.staged_resources) <= len(self.production_resources)) # should never have more staged resources than production resources

    def unstage_all_resources(self):
        self.staged_resources = []
        self._notify_publish_status_changed_if_needed()

    @property
    def can_publish_staged_resources(self):
        if len(self.staged_resources) == 0:
            return False
        for resource in self.staged_resources:
            if not resource.local_card_resource.is_ready:
                return False
        return True

    def publish_staged_resources(self):
        """
        Publishes staged resources. Returns True if success.
        Otherwise returns false.
        """
        self.observation_tower.notify(PublishStagedResourcesEvent(PublishStagedResourcesEvent.EventType.STARTED))
        if self.can_publish_staged_resources: # don't publish resources if one does not work
            self._generate_directories_if_needed()
            for r in self.staged_resources:
                # time.sleep(3)
                production_file_path = f'{self.configuration.production_file_path}{r.production_resource.file_name_with_ext}'
                production_preview_file_path = f'{self.configuration.production_preview_file_path}{r.production_resource.file_name_with_ext}'
                shutil.copy(r.local_card_resource.image_path, production_file_path)
                try:
                    shutil.copy(r.local_card_resource.image_preview_path, production_preview_file_path) # raises exception can ignore
                except:
                    Path(production_preview_file_path).unlink() # remove previous preview file
                    # gets regenerated from reload
                    # do nothing because preview file is not critical, or maybe can regenerate file
            self.unstage_all_resources()
            self.observation_tower.notify(PublishStagedResourcesEvent(PublishStagedResourcesEvent.EventType.FINISHED))
        else:
            self._notify_publish_status_changed_if_needed()
            self.observation_tower.notify(PublishStagedResourcesEvent(PublishStagedResourcesEvent.EventType.FAILED))
            raise Exception("Failed to publish. Please redownload resources and retry.")
        
    def generate_new_file(self, file_name: str, image: Optional[Image.Image] = None):
        local_resource = LocalCardResource(image_dir=self.configuration.production_file_path, 
                                           image_preview_dir=self.configuration.production_preview_file_path, 
                                           file_name=file_name,
                                           display_name=file_name + PNG_EXTENSION,
                                           display_name_short=file_name + PNG_EXTENSION,
                                           display_name_detailed=file_name + PNG_EXTENSION,
                                           file_extension=PNG_EXTENSION)
        
        self._generate_directories_if_needed()
        existing_file = Path(local_resource.image_path)
        if existing_file.is_file():
            raise Exception(f"File already exists: {local_resource.file_name_with_ext}")
        img = image or Image.new("RGB", (1, 1))
        img.save(local_resource.image_path, "PNG")
        
        preview_img = self._downscale_image(img)
        preview_img.save(local_resource.image_preview_path, "PNG")

    def _notify_publish_status_changed_if_needed(self):
        if self._can_publish_state != self.can_publish_staged_resources:
            # old_state = self._can_publish_state
            self._can_publish_state = self.can_publish_staged_resources
            # notify
            self.observation_tower.notify(PublishStatusUpdatedEvent(self._can_publish_state))


    def _generate_directories_if_needed(self):
        Path(self.configuration.production_preview_file_path).mkdir(parents=True, exist_ok=True)

class WorkerSignals(QObject):
    finished = pyqtSignal(object)

class RegenerateImageWorker(QRunnable):
    def __init__(self):
        pass

    def run(self):
        pass
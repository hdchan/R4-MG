import copy
import os
import shutil
from pathlib import Path
from typing import List, Optional

from PIL import Image

from ..ImageNetwork.ImageFetcherProvider import *
from AppCore.Models import LocalCardResource
from AppCore.Observation import ObservationTower
from AppCore.Observation.Events import ProductionResourceUpdatedEvent, LocalResourceEvent

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
                 configuration_provider: ConfigurationProvider, 
                 observation_tower: ObservationTower):
        self.observation_tower = observation_tower
        self.configuration_provider = configuration_provider
        self.production_resources: List[LocalCardResource] = []
        self.staged_resources: List[StagedCardResource] = []
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
        for production_file_name in filelist[:]:
            path = Path(production_file_name)
            if path.suffix == PNG_EXTENSION:
                image_dir = f'{self.configuration.production_file_path}'
                image_preview_dir = f'{self.configuration.production_preview_file_path}'
                resource = LocalCardResource(image_dir=image_dir, 
                                             image_preview_dir=image_preview_dir, 
                                             file_name=path.stem,
                                             display_name=path.stem + path.suffix,
                                             display_name_short=path.stem + path.suffix,
                                             display_name_detailed=path.stem + path.suffix,
                                             file_extension=path.suffix)
                local_resources.append(resource)

                existing_preview_file = Path(f'{self.configuration.production_preview_file_path}{production_file_name}')
                if not existing_preview_file.is_file():
                    # regnerate preview file
                    large_img = Image.open(f'{self.configuration.production_file_path}{production_file_name}')
                    preview_img = self._downscale_image(large_img)
                    preview_img_path = f'{self.configuration.production_preview_file_path}{production_file_name}'
                    preview_img.save(preview_img_path)

        self.production_resources = local_resources
        if self.delegate is not None:
            self.delegate.rd_did_load_production_resources(self, local_resources)

    def stage_resource(self, local_card_resource: LocalCardResource, index: int):
        # Cache emptied handled on UI
        self.unstage_resource(index)
        staged_card_resource = StagedCardResource(local_card_resource, 
                                                  self.production_resources[index])
        self.staged_resources.append(staged_card_resource)
        assert(len(self.staged_resources) <= len(self.production_resources)) # should never have more staged resources than production resources

    def unstage_resource(self, index: int):
        production_resource = self.production_resources[index]
        for i, resource in enumerate(self.staged_resources):
            if resource.production_resource == production_resource:
                self.staged_resources.pop(i)
        assert(len(self.staged_resources) <= len(self.production_resources)) # should never have more staged resources than production resources

    def unstage_all_resources(self):
        self.staged_resources = []

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
        if self.can_publish_staged_resources():
            self._generate_directories_if_needed()
            for r in self.staged_resources:
                # TODO: handle case where cache is emptied
                production_file_path = f'{self.configuration.production_file_path}{r.production_resource.file_name_with_ext}'
                production_preview_file_path = f'{self.configuration.production_preview_file_path}{r.production_resource.file_name_with_ext}'
                shutil.copy(r.local_card_resource.image_path, production_file_path)
                try:
                    shutil.copy(r.local_card_resource.image_preview_path, production_preview_file_path) # raises exception can ignore
                except:
                    Path(production_preview_file_path).unlink() # remove previous preview file
                    # gets regenerated from reload
                    # do nothing because preview file is not critical, or maybe can regenerate file
                self.observation_tower.notify(ProductionResourceUpdatedEvent(copy.deepcopy(r.local_card_resource)))
            self.staged_resources = []
        else:
            # notify resources that need to be addressed
            for resource in self.staged_resources:
                if not resource.local_card_resource.is_ready:
                    self.observation_tower.notify(LocalResourceEvent(LocalResourceEvent.EventType.FINISHED, resource.local_card_resource))
            raise Exception("Failed to publish. Please redownload resources and retry.")
        
    def generate_new_file(self, file_name: str, image: Optional[Image.Image] = None):
        self._generate_directories_if_needed()
        existing_file = Path(f'{self.configuration.production_file_path}{file_name}{PNG_EXTENSION}')
        if existing_file.is_file():
            raise Exception(f"File already exists: {file_name}{PNG_EXTENSION}")
        img = image or Image.new("RGB", (1, 1))
        img.save(f"{self.configuration.production_file_path}{file_name}{PNG_EXTENSION}", "PNG")
        
        preview_img = self._downscale_image(img)
        preview_img_path = f'{self.configuration.production_preview_file_path}{file_name}{PNG_EXTENSION}'
        preview_img.save(preview_img_path, "PNG")

    def _generate_directories_if_needed(self):
        Path(self.configuration.production_preview_file_path).mkdir(parents=True, exist_ok=True)
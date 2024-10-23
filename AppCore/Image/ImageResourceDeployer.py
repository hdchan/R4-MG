import os
import shutil
from pathlib import Path
from typing import List

from PIL import Image

from AppCore.Image.ImageFetcherProvider import *
from AppCore.Models.TradingCard import *

PNG_EXTENSION = '.png'
THUMBNAIL_SIZE = 256

class StagedCardResource:
    def __init__(self, local_card_resource: LocalCardResource, production_file_name: str):
        self.local_card_resource = local_card_resource
        self.production_file_name = production_file_name

class ImageResourceDeployerDelegate:
    def rd_did_load_production_resources(self, rd: ..., local_resources: List[LocalCardResource]) -> None:
        pass
    
class ImageResourceDeployer:
    def __init__(self,
                 configuration: Configuration):
        self.configuration = configuration
        self.production_resources: List[LocalCardResource] = []
        self.staged_resources: List[StagedCardResource] = []
        self.delegate: Optional[ImageResourceDeployerDelegate]

    def load_production_resources(self):
        """
        Will load images from production folder
        """
        def downscale_image(original_img: Image.Image) -> Image.Image:
            size = THUMBNAIL_SIZE, THUMBNAIL_SIZE
            preview_img = original_img.copy().convert('RGB')
            preview_img.thumbnail(size, Image.Resampling.LANCZOS)
            return preview_img
        
        self._generate_directories_if_needed()
        local_resources: List[LocalCardResource] = []
        filelist = os.listdir(self.configuration.production_file_path)
        filelist.sort()
        for production_file_name in filelist[:]:
            if production_file_name.endswith(PNG_EXTENSION):
                image_path = f'{self.configuration.production_file_path}{production_file_name}'
                image_preview_path = f'{self.configuration.production_preview_file_path}{production_file_name}'
                resource = LocalCardResource(image_path, 
                                             image_preview_path, 
                                             production_file_name, 
                                             production_file_name, 
                                             os.path.splitext(production_file_name)[1])
                resource.is_ready = True
                local_resources.append(resource)

                existing_preview_file = Path(f'{self.configuration.production_preview_file_path}{production_file_name}')
                if not existing_preview_file.is_file():
                    # regnerate preview file
                    large_img = Image.open(f'{self.configuration.production_file_path}{production_file_name}')
                    preview_img = downscale_image(large_img)
                    preview_img_path = f'{self.configuration.production_preview_file_path}{production_file_name}'
                    preview_img.save(preview_img_path)

        self.production_resources = local_resources
        if self.delegate is not None:
            self.delegate.rd_did_load_production_resources(self, local_resources)

    def stage_resource(self, local_card_resource: LocalCardResource, index: int):
        # TODO: Handle case where cache is emptied
        staged_card_resource = StagedCardResource(local_card_resource, 
                                                  self.production_resources[index].file_name)
        self.staged_resources.append(staged_card_resource)

    def unstage_resource(self, index: int):
        production_file_name = self.production_resources[index].file_name
        for i, resource in enumerate(self.staged_resources):
            if resource.production_file_name == production_file_name:
                self.staged_resources.pop(i)
                break

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
        # TODO: handle case where cache is emptied
        """
        Publishes staged resources. Returns True if success.
        Otherwise returns false.
        """
        if self.can_publish_staged_resources():
            self._generate_directories_if_needed()
            for r in self.staged_resources:
                shutil.copy(r.local_card_resource.image_path, f'{self.configuration.production_file_path}{r.production_file_name}')
                shutil.copy(r.local_card_resource.image_preview_path, f'{self.configuration.production_preview_file_path}{r.production_file_name}')
            self.staged_resources = []
            return True
        else:
            return False
        
    def generate_new_file(self, file_name: str):
        self._generate_directories_if_needed()
        existing_file = Path(f'{self.configuration.production_file_path}{file_name}{PNG_EXTENSION}')
        if existing_file.is_file():
            raise Exception(f"File already exists: {file_name}{PNG_EXTENSION}")
        img = Image.new("RGB", (1, 1))
        img.save(f"{self.configuration.production_file_path}{file_name}{PNG_EXTENSION}", "PNG")

    def _generate_directories_if_needed(self):
        Path(self.configuration.production_preview_file_path).mkdir(parents=True, exist_ok=True)
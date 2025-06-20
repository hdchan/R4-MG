
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

from PIL import Image

from .LocalAssetResource import LocalAssetResource

Width = int
Height = int
Size = Tuple[Width, Height]

PNG_EXTENSION = 'png'

class LocalCardResource(LocalAssetResource):
    def __init__(self, 
                 image_dir: str,
                 image_preview_dir: str,
                 file_name: str,
                 display_name: str,
                 display_name_short: str,
                 display_name_detailed: str,
                 remote_image_url: Optional[str] = None, 
                 can_generate_placeholder: bool = False):
        super().__init__(asset_dir=image_dir, 
                         file_name=file_name, 
                         file_extension=PNG_EXTENSION, 
                         display_name=display_name, 
                         remote_url=remote_image_url)
        self.image_preview_dir = image_preview_dir
        self.display_name_short = display_name_short
        self.display_name_detailed = display_name_detailed
        self._can_generate_placeholder = can_generate_placeholder

        assert(self.image_dir is not None)
        assert(self.image_preview_dir is not None)
        assert(self.file_name is not None)
        assert(self.display_name is not None)
        assert(self.display_name_short is not None)
        assert(self.display_name_detailed is not None)
        assert(self.file_extension is not None)

    @property
    def image_dir(self) -> str:
        return self.asset_dir
    
    @property
    def remote_image_url(self) -> Optional[str]:
        return self.remote_url
    
    class Keys:
        IMAGE_DIR = 'image_dir'
        IMAGE_PREVIEW_DIR = 'image_preview_dir'
        FILE_NAME = 'file_name'
        DISPLAY_NAME = 'display_name'
        DISPLAY_NAME_SHORT = 'display_name_short'
        DISPLAY_NAME_DETAILED = 'display_name_detailed'
        REMOTE_IMAGE_URL = 'remote_image_url'
        FILE_EXTENSION = 'file_extension'

    def to_data(self) -> Dict[str, Any]:
        return {
            self.Keys.IMAGE_DIR: self.image_dir,
            self.Keys.IMAGE_PREVIEW_DIR: self.image_preview_dir,
            self.Keys.FILE_NAME: self.file_name,
            self.Keys.DISPLAY_NAME: self.display_name,
            self.Keys.DISPLAY_NAME_SHORT: self.display_name_short,
            self.Keys.DISPLAY_NAME_DETAILED: self.display_name_detailed,
            self.Keys.REMOTE_IMAGE_URL: self.remote_image_url,
            self.Keys.FILE_EXTENSION: self.file_extension,
        }
    
    @classmethod
    def from_json(cls, json: Dict[str, Any]):
        obj = cls.__new__(cls)
        obj.asset_dir = json[LocalCardResource.Keys.IMAGE_DIR]
        obj.image_preview_dir = json[LocalCardResource.Keys.IMAGE_PREVIEW_DIR]
        obj.file_name = json[LocalCardResource.Keys.FILE_NAME]
        obj.display_name = json[LocalCardResource.Keys.DISPLAY_NAME]
        obj.display_name_short = json[LocalCardResource.Keys.DISPLAY_NAME_SHORT]
        obj.display_name_detailed = json[LocalCardResource.Keys.DISPLAY_NAME_DETAILED]
        obj.remote_url = json[LocalCardResource.Keys.REMOTE_IMAGE_URL]
        obj.file_extension = json[LocalCardResource.Keys.FILE_EXTENSION]
        return obj

    @property
    def can_be_replaced_with_placeholder(self) -> bool:
        return not self.is_ready and self._can_generate_placeholder
    
    @property
    def is_preview_ready(self) -> bool:
        return Path(self.image_preview_path).is_file()
    
    @property
    def image_path(self) -> str:
        return self.asset_path
    
    @property
    def image_preview_path(self) -> str:
        return f'{self.image_preview_dir}{self.file_name_with_ext}'
    
    @property
    def image_temp_path(self):
        return self.asset_temp_path

    @property
    def size(self) -> Tuple[int, int]:
        return Image.open(self.image_path).size
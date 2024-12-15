import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

from PIL import Image

Width = int
Height = int
Size = Tuple[Width, Height]

class LocalCardResource:
    def __init__(self, 
                 image_dir: str,
                 image_preview_dir: str,
                 file_name: str,
                 display_name: str,
                 display_name_short: str,
                 display_name_detailed: str,
                 file_extension: str,
                 remote_image_url: Optional[str] = None):
        self.image_dir = image_dir
        self.image_preview_dir = image_preview_dir
        self.file_name = file_name
        self.display_name = display_name
        self.display_name_short = display_name_short
        self.display_name_detailed = display_name_detailed
        self.remote_image_url = remote_image_url
        self.file_extension = file_extension

        assert(self.image_dir is not None)
        assert(self.image_preview_dir is not None)
        assert(self.file_name is not None)
        assert(self.display_name is not None)
        assert(self.display_name_short is not None)
        assert(self.display_name_detailed is not None)
        assert(self.file_extension is not None)

    def __eq__(self, other):  # type: ignore
        if not isinstance(other, LocalCardResource):
            # don't attempt to compare against unrelated types
            return NotImplemented

        return (self.image_path == other.image_path)
    
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
        super(LocalCardResource, obj).__init__()
        obj.image_dir = json[LocalCardResource.Keys.IMAGE_DIR]
        obj.image_preview_dir = json[LocalCardResource.Keys.IMAGE_PREVIEW_DIR]
        obj.file_name = json[LocalCardResource.Keys.FILE_NAME]
        obj.display_name = json[LocalCardResource.Keys.DISPLAY_NAME]
        obj.display_name_short = json[LocalCardResource.Keys.DISPLAY_NAME_SHORT]
        obj.display_name_detailed = json[LocalCardResource.Keys.DISPLAY_NAME_DETAILED]
        obj.remote_image_url = json[LocalCardResource.Keys.REMOTE_IMAGE_URL]
        obj.file_extension = json[LocalCardResource.Keys.FILE_EXTENSION]
        return obj
    
    '''
    is_ready = True, is_loading = True
    processing existing file? (loading)
    how to recover if file is artifact?

    is_ready = True, is_loading = False
    image is done processing and ready to be shown (no loading)
    happy path

    is_ready = False, is_loading = True
    image is being downloaded (loading)
    ok, but potential artifact where not actually loading
    

    is_ready = False, is_loading = False
    image is not being processed, and does not exist (no loading)
    can recover
    '''

    @property
    def is_ready(self) -> bool:
        return Path(self.image_path).is_file()
    
    @property 
    def is_loading(self) -> bool:
        return Path(self.image_temp_path).is_file() # temp file might be present as an artifact

    @property
    def file_name_with_ext(self) -> str:
        return f'{self.file_name}{self.file_extension}'
    
    @property
    def image_path(self):
        return f'{self.image_dir}{self.file_name_with_ext}'
    
    @property
    def image_preview_path(self):
        return f'{self.image_preview_dir}{self.file_name_with_ext}'
    
    @property
    def image_temp_path(self):
        return f'{self.image_preview_dir}temp-{self.file_name}'
    
    @property
    def image_old_path(self):
        return f'{self.image_preview_dir}old-{self.file_name}'

    @property
    def size(self):
        return Image.open(self.image_path).size
            
    
    @property
    def created_date(self) -> datetime:
        stat = os.stat(self.image_path)
        try:
            # On systems without birthtime (like Windows), use ctime instead
            return datetime.fromtimestamp(stat.st_ctime)
        except AttributeError:
            return datetime.fromtimestamp(stat.st_birthtime)

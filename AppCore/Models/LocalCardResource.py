from pathlib import Path
from typing import Optional, Tuple
import os
from datetime import datetime

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
        self._size: Optional[Size] = None

    def __eq__(self, other):  # type: ignore
        if not isinstance(other, LocalCardResource):
            # don't attempt to compare against unrelated types
            return NotImplemented

        return (self.image_path == other.image_path)

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
        # if self._size is None and self.is_ready:
        self._size = Image.open(self.image_path).size
        return self._size
            
    
    @property
    def created_date(self) -> datetime:
        stat = os.stat(self.image_path)
        try:
            # On systems without birthtime (like Windows), use ctime instead
            return datetime.fromtimestamp(stat.st_ctime)
        except AttributeError:
            return datetime.fromtimestamp(stat.st_birthtime)

from typing import Optional
from pathlib import Path

class LocalCardResource:
    def __init__(self, 
                 image_dir: str,
                 image_preview_dir: str,
                 file_name: str,
                 display_name: str,
                 file_extension: str,
                 remote_image_url: Optional[str] = None):
        self.image_dir = image_dir
        self.image_preview_dir = image_preview_dir
        self.file_name = file_name
        self.display_name = display_name
        self.remote_image_url = remote_image_url
        self.file_extension = file_extension
    
    @property
    def is_ready(self) -> bool:
        return Path(self.image_path).is_file()
    
    @property 
    def is_loading(self) -> bool:
        return Path(self.image_temp_path).is_file() 
    
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
        return f'{self.image_preview_dir}temp-{self.file_name_with_ext}'
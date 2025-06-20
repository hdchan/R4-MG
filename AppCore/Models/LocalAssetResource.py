import os
from datetime import datetime
from pathlib import Path
from typing import Optional


class LocalAssetResource:
    def __init__(self, 
                 asset_dir: str,
                 file_name: str,
                 file_extension: str,
                 display_name: str,
                 remote_url: Optional[str] = None):
        self.asset_dir = asset_dir
        self.file_name = file_name
        self.display_name = display_name
        self.remote_url = remote_url
        self.file_extension = file_extension
    
    def __hash__(self):
        return hash(self.asset_path)
    
    def __eq__(self, other):  # type: ignore
        if not isinstance(other, LocalAssetResource):
            # don't attempt to compare against unrelated types
            return NotImplemented

        return (self.asset_path == other.asset_path)
    
    @property
    def file_name_with_ext(self) -> str:
        value = f'{self.file_name}.{self.file_extension}'
        return value
    
    @property
    def asset_path(self) -> str:
        return f'{self.asset_dir}{self.file_name_with_ext}'
    
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
        return Path(self.asset_path).is_file()
    
    @property
    def is_local_only(self) -> bool:
        return self.remote_url is None
    
    @property
    def asset_temp_path(self):
        return f'{self.asset_dir}{self.file_name_with_ext}.temp'
    
    @property 
    def is_loading(self) -> bool:
        return Path(self.asset_temp_path).is_file() # temp file might be present as an artifact
    
    @property
    def created_date(self) -> datetime:
        stat = os.stat(self.asset_path)
        try:
            # On systems without birthtime (like Windows), use ctime instead
            return datetime.fromtimestamp(stat.st_ctime)
        except AttributeError:
            return datetime.fromtimestamp(stat.st_birthtime) # type: ignore
    
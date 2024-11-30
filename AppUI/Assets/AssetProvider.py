import os
import random
from pathlib import Path
from typing import List, Optional

# basedir = os.path.dirname(__file__)
appdir = os.path.dirname(os.path.abspath(__file__))
class AssetProvider:
    class Image:
        @property
        def logo_path(self) -> str:
            return self._image_path("logo.png")
        
        @property
        def swu_logo_black_path(self) -> str:
            return self._image_path('SWH_Logo_Black_preview.png')
        
        @property 
        def r4_head(self) -> str:
            return self._image_path('r4-head.png')
        
        @property
        def sor_background(self) -> str:
            return self._image_path('large_spark_of_rebellion_starfield_c4fdfaa6a7.png')
        
        def _image_path(self, file_name: str) -> str:
            return os.path.join(appdir, f'Images/{file_name}')
        
    class Audio:
        
        def __init__(self):
            self.__r2_file_list: Optional[List[str]] = None
        
        @property
        def _r2_file_list(self) -> Optional[List[str]]:
            if self.__r2_file_list is None:
                sound_effect_files = os.listdir(os.path.join(appdir, f'Audio/r2/'))
                filtered_list: List[str] = []
                for file in sound_effect_files[:]:
                    path = Path(file)
                    if path.suffix == '.wav':
                        filtered_list.append(file)
                self.__r2_file_list = filtered_list
            return self.__r2_file_list
        
        @property
        def r2_effect_path(self) -> str:
            if self._r2_file_list is not None:
                random_int = random.randint(0, len(self._r2_file_list) - 1)
                selected_file = self._r2_file_list[random_int]
                # https://stackoverflow.com/a/24386708
                return self._audio_path(selected_file)
            raise Exception
        
        
        def _audio_path(self, file_name: str) -> str:
            return os.path.join(appdir, f'Audio/r2/{file_name}')
    
    
    def __init__(self):
        self.image = self.Image()
        self.audio = self.Audio()
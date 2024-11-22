import os
import random

# basedir = os.path.dirname(__file__)
appdir = os.path.dirname(os.path.abspath(__file__))
class AssetProvider:
    class Image:
        @property
        def logo_path(self) -> str:
            return self._image_path("logo.png")
        
        def _image_path(self, file_name: str) -> str:
            return os.path.join(appdir, f'Images/{file_name}')
        
    class Audio:
        @property
        def r2_effect_path(self) -> str:
            random_int = random.randint(1, 67)
            # https://stackoverflow.com/a/24386708
            return self._audio_path(f'r2-{random_int:0>2}.wav')
        
        def _audio_path(self, file_name: str) -> str:
            return os.path.join(appdir, f'Audio/r2/{file_name}')
    
    
    def __init__(self):
        self.image = self.Image()
        self.audio = self.Audio()
import os
import random
from pathlib import Path
from typing import List, Optional


APP_DIR = os.path.dirname(os.path.abspath(__file__))
class AssetProvider:

    class Image:
        @property
        def logo_path(self) -> str:
            return self._image_path("logo.png")
        
        @property
        def swu_logo_black_path(self) -> str:
            return self._image_path('SWH_Logo_Black_preview.png')
        
        @property
        def swu_card_back(self) -> str:
            return self._image_path('cardback.png')
        
        @property 
        def r4_head(self) -> str:
            return self._image_path('r4-head.png')
        
        @property
        def sor_background(self) -> str:
            return self._image_path('large_spark_of_rebellion_starfield_c4fdfaa6a7.png')
        
        @property
        def set_identifier_example(self) -> str:
            return self._image_path('set-identifier-example.png')
        
        @property
        def aspect_aggression(self) -> str:
            return self._aspect_resource("Aggression")
        
        @property
        def aspect_command(self) -> str:
            return self._aspect_resource("Command")
        
        @property
        def aspect_cunning(self) -> str:
            return self._aspect_resource("Cunning")
        
        @property
        def aspect_heroism(self) -> str:
            return self._aspect_resource("Heroism")
        
        @property
        def aspect_vigilance(self) -> str:
            return self._aspect_resource("Vigilance")
        
        @property
        def aspect_villainy(self) -> str:
            return self._aspect_resource("Villainy")
        
        def _aspect_resource(self, aspect: str) -> str:
            return self._image_path(f'Aspects/SWH_Aspects_{aspect}_100.png')
        
        def _image_path(self, file_name: str) -> str:
            return os.path.join(APP_DIR, f'Images/{file_name}')
        
    class Audio:
        def __init__(self):
            self.__r2_file_list: Optional[List[str]] = None
        
        @property
        def _r2_file_list(self) -> Optional[List[str]]:
            if self.__r2_file_list is None:
                sound_effect_files = os.listdir(os.path.join(APP_DIR, f'Audio/r2/'))
                filtered_list: List[str] = []
                for file in sound_effect_files[:]:
                    path = Path(file)
                    if path.suffix == '.wav':
                        filtered_list.append(file)
                self.__r2_file_list = filtered_list
            return self.__r2_file_list
        
        @property
        def r4_affirmative_path(self) -> str:
            affirmative_list = [
                'r2-02.wav', 
                'r2-04.wav', 
                'r2-06.wav', 
                'r2-14.wav', 
                'r2-36.wav', 
                'r2-56.wav', 
                'r2-63.wav'
                ]
            random_int = random.randint(0, len(affirmative_list) - 1)
            selected_file = affirmative_list[random_int]
            # https://stackoverflow.com/a/24386708
            return self._audio_path(selected_file)

        @property
        def r4_effect_path(self) -> str:
            if self._r2_file_list is not None:
                random_int = random.randint(0, len(self._r2_file_list) - 1)
                selected_file = self._r2_file_list[random_int]
                # https://stackoverflow.com/a/24386708
                return self._audio_path(selected_file)
            raise Exception
        
        
        def _audio_path(self, file_name: str) -> str:
            return os.path.join(APP_DIR, f'Audio/r2/{file_name}')
    
    class Data:
        @property
        def sor_set_path(self):
            return self._data_path('sor.json')
        
        @property
        def shd_set_path(self):
            return self._data_path('shd.json')
        
        @property
        def twi_set_path(self):
            return self._data_path('twi.json')
        
        @property
        def jtl_set_path(self):
            return self._data_path('jtl.json')
        
        @property
        def lof_set_path(self):
            return self._data_path('lof.json')
        
        @property
        def starwarsunlimited_com_filter_path(self):
            return self._data_path('starwarsunlimited_com_filters.json')
        
        def _data_path(self, file_name: str) -> str:
            return os.path.join(APP_DIR, f'Data/{file_name}')
    
    
    def __init__(self):
        self.image = self.Image()
        self.audio = self.Audio()
        self.data = self.Data()
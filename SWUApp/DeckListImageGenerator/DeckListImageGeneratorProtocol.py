from typing import Callable, Optional

from PIL import Image
from PyQt5.QtGui import QPixmap

from ..Models import ParsedDeckList


class DeckListImageGeneratorProtocol:
    @property
    def is_loading(self) -> bool:
        return False
    
    def generate_image(self,
                       parsed_deck_list: ParsedDeckList,
                       is_export: bool, 
                       completion: Callable[[Optional[QPixmap], Optional[Image.Image]], None]) -> None:
        raise Exception
    
class DeckListImageGeneratorProviding:
    @property
    def image_generator(self) -> DeckListImageGeneratorProtocol:
        raise Exception
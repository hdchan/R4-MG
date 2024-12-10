from PIL import Image
from ..Config import ConfigurationManager
from .ImageFetcherRequestProtocol import *

class ImageFetcherProtocol:
    def __init__(self, configuration_manager: ConfigurationManager):
        self.configuration_manager = configuration_manager
        
    def fetch(self, image_url: str) ->Image.Image:
        raise Exception()
    
class ImageFetcherProviding:
    @property
    def image_fetcher(self) -> ImageFetcherProtocol:
        return NotImplemented
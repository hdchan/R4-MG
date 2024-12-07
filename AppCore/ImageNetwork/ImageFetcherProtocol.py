from PIL import Image
from ..Config import ConfigurationProviding
from .ImageFetcherRequestProtocol import *

class ImageFetcherProtocol:
    def __init__(self, configuration_provider: ConfigurationProviding):
        self.configuration_provider = configuration_provider
        
    def fetch(self, image_url: str) ->Image.Image:
        raise Exception()
    
class ImageFetcherProviding:
    @property
    def image_fetcher(self) -> ImageFetcherProtocol:
        return NotImplemented
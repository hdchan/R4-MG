from PIL import Image
from ..Config import ConfigurationProviderProtocol
from .ImageFetcherRequestProtocol import *

class ImageFetcherProtocol:
    def __init__(self, configuration_provider: ConfigurationProviderProtocol):
        self.configuration_provider = configuration_provider
        
    def fetch(self, image_url: str) ->Image.Image:
        raise Exception()
    
class ImageFetcherProviderProtocol:
    def provideImageFetcher(self) -> ImageFetcherProtocol:
        return NotImplemented
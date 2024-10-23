from PIL import Image
from ..Config import ConfigurationProvider

class ImageFetcherProtocol:
    def __init__(self, configuration_provider: ConfigurationProvider):
        self.configuration_provider = configuration_provider
        
    def fetch(self, image_url: str) -> Image.Image:
        raise Exception()
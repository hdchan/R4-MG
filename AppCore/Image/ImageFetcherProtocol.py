from PIL import Image
from ..Config import Configuration

class ImageFetcherProtocol:
    def __init__(self, configuration: Configuration):
        self.configuration = configuration
        
    def fetch(self, image_url: str) -> Image.Image:
        raise Exception()
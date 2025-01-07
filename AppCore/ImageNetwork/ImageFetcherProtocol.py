from PIL import Image

from ..Models import LocalCardResource
from .ImageFetcherRequestProtocol import *


class ImageFetcherProtocol:
    def fetch(self, local_resource: LocalCardResource) -> Image.Image:
        raise Exception()
    
class ImageFetcherProviding:
    @property
    def image_fetcher(self) -> ImageFetcherProtocol:
        return NotImplemented
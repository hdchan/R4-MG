from PIL import Image

from AppCore.Models import LocalCardResource


class ImageFetcherProtocol:
    def fetch(self, local_resource: LocalCardResource) -> Image.Image:
        raise Exception()
    
class ImageFetcherProviding:
    @property
    def image_fetcher(self) -> ImageFetcherProtocol:
        return NotImplemented
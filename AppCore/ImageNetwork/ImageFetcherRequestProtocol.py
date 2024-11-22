from PIL import Image

class ImageFetcherRequestProtocol:
    def image_url(self) -> str:
        return NotImplemented
    
    def image_response(self) -> Image.Image:
        return NotImplemented
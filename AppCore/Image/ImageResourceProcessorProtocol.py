from AppCore.Models import LocalCardResource
from PIL import Image

class ImageResourceProcessorProtocol:
    def async_store_local_resource(self, local_resource: LocalCardResource, retry: bool = False) -> None:
        raise Exception
    
    def rotate_and_save_resource(self, local_resource: LocalCardResource, angle: float) -> None:
        raise Exception
    
    def regenerate_resource_preview(self, local_resource: LocalCardResource) -> None:
        raise Exception
    
    def generate_preview_image(self, original_img: Image.Image) -> Image.Image:
        return NotImplemented
    
    def down_scale_image(self, original_img: Image.Image, max_size: float) -> Image.Image:
        return NotImplemented
    
class ImageResourceProcessorProviding:
    @property
    def image_resource_processor(self) -> ImageResourceProcessorProtocol:
        return NotImplemented
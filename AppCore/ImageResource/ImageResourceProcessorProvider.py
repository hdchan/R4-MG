from .ImageResourceProcessorProtocol import ImageResourceProcessorProviding, ImageResourceProcessorProtocol

class ImageResourceProcessorProvider(ImageResourceProcessorProviding):

    def __init__(self, image_resource_processor: ImageResourceProcessorProtocol):
        self._processor = image_resource_processor

    @property
    def image_resource_processor(self) -> ImageResourceProcessorProtocol:
        return self._processor
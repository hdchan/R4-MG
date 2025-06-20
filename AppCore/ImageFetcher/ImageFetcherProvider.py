from AppCore.Config import ConfigurationManager

from .ImageFetcherLocal import ImageFetcherLocal
from .ImageFetcherProtocol import *
from .ImageFetcherRemote import ImageFetcherRemote


class ImageFetcherProvider(ImageFetcherProviding):
    def __init__(self, 
                 configuration_manager: ConfigurationManager):
        self.configuration_manager = configuration_manager
        self.real_client = ImageFetcherRemote(configuration_manager)
        self.mock_client = ImageFetcherLocal(configuration_manager)

    @property
    def image_fetcher(self) -> ImageFetcherProtocol:
        if self.configuration_manager.configuration.is_mock_data:
            return self.mock_client
        else:
            return self.real_client

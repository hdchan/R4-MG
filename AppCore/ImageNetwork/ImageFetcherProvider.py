from ..Config import ConfigurationManager
from ..Config.Configuration import *
from .ImageFetcherProtocol import *


class ImageFetcherProvider(ImageFetcherProviding):
    def __init__(self, 
                 configuration_manager: ConfigurationManager, 
                 real_client: ImageFetcherProtocol,
                 mock_client: ImageFetcherProtocol):
        self.configuration_manager = configuration_manager
        self.real_client = real_client
        self.mock_client = mock_client

    @property
    def image_fetcher(self) -> ImageFetcherProtocol:
        if self.configuration_manager.configuration.is_mock_data:
            return self.mock_client
        else:
            return self.real_client

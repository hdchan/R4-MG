from ..Config.Configuration import *

from .ImageFetcherProtocol import *


class ImageFetcherProvider(ImageFetcherProviding):
    def __init__(self, 
                 configuration_provider: ConfigurationProviding, 
                 real_client: ImageFetcherProtocol, 
                 mock_client: ImageFetcherProtocol):
        self.configuration_provider = configuration_provider
        self.real_client = real_client
        self.mock_client = mock_client

    @property
    def image_fetcher(self) -> ImageFetcherProtocol:
        if self.configuration_provider.configuration.is_mock_data:
            return self.mock_client
        else:
            return self.real_client

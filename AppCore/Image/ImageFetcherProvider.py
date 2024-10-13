from ..Config.Configuration import *

from .ImageFetcherProtocol import *


class ImageFetcherProvider:
    def __init__(self, configuration: Configuration, 
                 real_client: ImageFetcherProtocol, 
                 mock_client: ImageFetcherProtocol):
        self.configuration = configuration
        self.real_client = real_client
        self.mock_client = mock_client

    def provideImageFetcher(self) -> ImageFetcherProtocol:
        if self.configuration.is_mock_data:
            return self.mock_client
        else:
            return self.real_client

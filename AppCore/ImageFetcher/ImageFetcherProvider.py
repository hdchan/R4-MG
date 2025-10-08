from AppCore.Config import ConfigurationManager

from .ImageFetcherLocal import ImageFetcherLocal
from .ImageFetcherProtocol import *
from .ImageFetcherRemote import ImageFetcherRemote


class ImageFetcherProvider(ImageFetcherProviding):
    def __init__(self, 
                 configuration_manager: ConfigurationManager):
        self.configuration_manager = configuration_manager
        self.real_client = ImageFetcherRemote()
        self.mock_client = ImageFetcherLocal()

    @property
    def image_fetcher(self) -> ImageFetcherProtocol:
        network_delay = self.configuration_manager.configuration.network_delay_duration
        if self.configuration_manager.configuration.is_mock_data:
            self.mock_client.network_delay_duration = network_delay
            return self.mock_client
        else:
            self.real_client.network_delay_duration = network_delay
            return self.real_client

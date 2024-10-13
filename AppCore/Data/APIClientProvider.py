from AppCore.Config.Configuration import *

from .APIClientProtocol import APIClientProtocol


class APIClientProvider:
    def __init__(self, 
                 configuration: Configuration, 
                 real_client: APIClientProtocol, 
                 mock_client: APIClientProtocol):
        self.configuration = configuration
        self.real_client = real_client
        self.mock_client = mock_client

    def provideClient(self) -> APIClientProtocol:
        if self.configuration.is_mock_data:
            return self.mock_client
        else:
            return self.real_client
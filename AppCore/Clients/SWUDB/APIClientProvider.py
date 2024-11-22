from AppCore.Config.Configuration import *

from ...Data.APIClientProtocol import *


class APIClientProvider(APIClientProviderProtocol):
    def __init__(self, 
                 configuration_provider: ConfigurationProvider, 
                 real_client: APIClientProtocol, 
                 mock_client: APIClientProtocol):
        self.configuration_provider = configuration_provider
        self.real_client = real_client
        self.mock_client = mock_client
        
    def provideClient(self) -> APIClientProtocol:
        if self.configuration_provider.configuration.is_mock_data:
            return self.mock_client
        else:
            return self.real_client
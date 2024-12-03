from AppCore.Config.Configuration import *
from AppCore.Data.APIClientProtocol import *


class SWUDBAPIClientProvider(APIClientProviderProtocol):
    def __init__(self, 
                 configuration_provider: ConfigurationProviderProtocol, 
                 real_client: APIClientProtocol, 
                 local_client: APIClientProtocol):
        self.configuration_provider = configuration_provider
        self.real_client = real_client
        self.local_client = local_client
        
    def provideClient(self) -> APIClientProtocol:
        if self.configuration_provider.configuration.search_source == Configuration.Settings.SearchSource.LOCAL:
            return self.local_client
        else:
            return self.real_client
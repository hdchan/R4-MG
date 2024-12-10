from AppCore.Config.ConfigurationManager import *
from AppCore.Data.APIClientProtocol import *


class SWUDBAPIClientProvider(APIClientProviding):
    def __init__(self, 
                 configuration_manager: ConfigurationManager, 
                 real_client: APIClientProtocol, 
                 local_client: APIClientProtocol):
        self.configuration_manager = configuration_manager
        self.real_client = real_client
        self.local_client = local_client
    
    @property
    def client(self) -> APIClientProtocol:
        if self.configuration_manager.configuration.search_source == Configuration.Settings.SearchSource.LOCAL:
            return self.local_client
        else:
            return self.real_client
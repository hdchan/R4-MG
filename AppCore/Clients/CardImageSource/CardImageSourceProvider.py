from ...Resource.CardImageSourceProtocol import CardImageSourceProtocol, CardImageSourceProviderProtocol
from ...Config import ConfigurationProvider, Configuration

class CardImageSourceProvider(CardImageSourceProviderProtocol):
    def __init__(self,
                 configuration_provider: ConfigurationProvider,
                 swudb_api: CardImageSourceProtocol,
                 swudb: CardImageSourceProtocol):
        self.configuration_provider = configuration_provider
        self.swudb_api = swudb_api
        self.swudb = swudb
        
    
    def provideSource(self) -> CardImageSourceProtocol:
        if self.configuration_provider.configuration.image_source == Configuration.Settings.ImageSource.SWUDB:
            return self.swudb
        else:
            return self.swudb_api
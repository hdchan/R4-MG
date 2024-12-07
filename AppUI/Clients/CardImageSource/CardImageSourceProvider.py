from AppCore.Resource.CardImageSourceProtocol import CardImageSourceProtocol, CardImageSourceProviding
from AppCore.Config import ConfigurationProviding, Configuration

class CardImageSourceProvider(CardImageSourceProviding):
    def __init__(self,
                 configuration_provider: ConfigurationProviding,
                 swudb_api: CardImageSourceProtocol,
                 swudb: CardImageSourceProtocol):
        self.configuration_provider = configuration_provider
        self.swudb_api = swudb_api
        self.swudb = swudb
        
    @property
    def card_image_source(self) -> CardImageSourceProtocol:
        if self.configuration_provider.configuration.image_source == Configuration.Settings.ImageSource.SWUDB:
            return self.swudb
        else:
            return self.swudb_api
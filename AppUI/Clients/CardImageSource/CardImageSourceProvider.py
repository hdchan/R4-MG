from AppCore.Resource.CardImageSourceProtocol import CardImageSourceProtocol, CardImageSourceProviding
from AppCore.Config import ConfigurationManager, Configuration

class CardImageSourceProvider(CardImageSourceProviding):
    def __init__(self,
                 configuration_manager: ConfigurationManager,
                 swudb_api: CardImageSourceProtocol,
                 swudb: CardImageSourceProtocol, 
                 custom_local: CardImageSourceProtocol):
        self.configuration_manager = configuration_manager
        self.swudb_api = swudb_api
        self.swudb = swudb
        self.custom_local = custom_local
        
    @property
    def card_image_source(self) -> CardImageSourceProtocol:
        configuration_source = self.configuration_manager.configuration.image_source
        if configuration_source == Configuration.Settings.ImageSource.SWUDB:
            return self.swudb
        elif configuration_source == Configuration.Settings.ImageSource.CUSTOM_LOCAL:
            return self.custom_local
        else:
            return self.swudb_api
from AppCore.Config.ConfigurationManager import *
from AppCore.Data.APIClientProtocol import *
from AppCore.Resource.CardImageSourceProtocol import (CardImageSourceProtocol,
                                                      CardImageSourceProviding)
from AppCore.Network import LocalNetworker, RemoteNetworker
from ..Assets import AssetProvider
from . import swu_db_com, starwarsunlimited_com, swudb_com, custom


class ClientProvider(APIClientProviding, CardImageSourceProviding):
    
    class Dependencies:
        def __init__(self, 
                     configuration_manager: ConfigurationManager,
                     asset_provider: AssetProvider, 
                     remote_networker: RemoteNetworker, 
                     local_networker: LocalNetworker):
            self.configuration_manager = configuration_manager
            self.asset_provider = asset_provider
            self.remote_networker = remote_networker
            self.local_networker = local_networker            
    
    def __init__(self, dependencies: Dependencies):
        self._configuration_manager = dependencies.configuration_manager
        self._swu_db_search = swu_db_com.SWUDBAPIRemoteClient(dependencies.remote_networker)
        self._local_search = swu_db_com.SWUDBAPILocalClient(dependencies.local_networker, 
                                                            dependencies.asset_provider)
        self._swu_db_image_source = swu_db_com.SWUDBAPIImageSource(dependencies.configuration_manager)
        self._swudb_image_source = swudb_com.SWUDBImageSource(dependencies.configuration_manager)
        self._starwarsulimited_search = starwarsunlimited_com.SearchClient(dependencies.remote_networker, dependencies.asset_provider)
        self._starwarsunlimited_image_source = starwarsunlimited_com.ImageSource(dependencies.configuration_manager)
        
        self._custom_image_source = custom.CustomLocalImageSource()
        self._custom_search = custom.CustomLocalSearchSource(dependencies.local_networker, 
                                                             self._custom_image_source.image_path, 
                                                             self._custom_image_source.image_preview_dir)
    
    @property
    def _configuration(self) -> Configuration:
        return self._configuration_manager.configuration
    
    @property
    def client(self) -> APIClientProtocol:
        if self._configuration.custom_xor_normal_search_source:
            return self._custom_search
        
        if self._configuration_manager.configuration.search_source == Configuration.Settings.SearchSource.LOCAL:
            return self._local_search
        elif self._configuration_manager.configuration.search_source == Configuration.Settings.SearchSource.SWUDBAPI:
            return self._swu_db_search
        elif self._configuration_manager.configuration.search_source == Configuration.Settings.SearchSource.STARWARSUNLIMITED_FFG:
            return self._starwarsulimited_search
        
        raise Exception("no such source")
    
    @property
    def card_image_source(self) -> CardImageSourceProtocol:
        if self._configuration_manager.configuration.search_source == Configuration.Settings.SearchSource.LOCAL:
            return self._swu_db_image_source
        elif self._configuration_manager.configuration.search_source == Configuration.Settings.SearchSource.SWUDBAPI:
            return self._swu_db_image_source
        elif self._configuration_manager.configuration.search_source == Configuration.Settings.SearchSource.STARWARSUNLIMITED_FFG:
            return self._starwarsunlimited_image_source
    
        raise Exception("no such source")
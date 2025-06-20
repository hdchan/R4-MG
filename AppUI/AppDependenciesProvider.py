
from AppCore.CoreDependenciesProvider import CoreDependenciesProvider
from AppCore.DataFetcher import *
from AppCore.DataSource import DataSourceLocallyManagedSets
from AppCore.DataSource.DataSourceCardSearch import *
from AppCore.DataSource.DataSourceRecentPublished import *
from AppCore.DataSource.DataSourceRecentSearch import *
from AppCore.ImageResource import *
from AppUI.Coordinators import MenuActionCoordinator, ShortcutActionCoordinator

from .AppDependenciesProviding import *
from .Assets import AssetProvider
from .Clients.ClientProvider import ClientProvider
from .Clients.swu_db_com.SWUDBLocalSetRetrieverClient import \
    SWUDBLocalSetRetrieverClient
from .ComponentProvider import ComponentProviding
from .Coordinators import MenuActionCoordinator, ShortcutActionCoordinator
from .Router import Router


class AppDependenciesProvider(CoreDependenciesProvider, AppDependenciesProviding):
        def __init__(self, component_provider: ComponentProviding):
            super().__init__()
            self._asset_provider = AssetProvider()
            self._shortcut_action_coordinator = ShortcutActionCoordinator()
            
            
            self._menu_action_coordinator = MenuActionCoordinator(self._configuration_manager, 
                                                                  self._platform_service_provider)
            
            
            self._local_managed_sets_data_source = DataSourceLocallyManagedSets(self._configuration_manager,
                                                                                  self._observation_tower,
                                                                                  client=SWUDBLocalSetRetrieverClient())
            
            
            client_provider_dependencies = ClientProvider.Dependencies(self._asset_provider,
                                                                      DataFetcherRemote(self._configuration_manager),
                                                                      DataFetcherLocal(self._configuration_manager),
                                                                      self._local_managed_sets_data_source,
                                                                      self._observation_tower)
            client_provider = ClientProvider(dependencies=client_provider_dependencies)
            self._search_client_provider = client_provider
            
            
            self._router = Router(self._image_resource_deployer, 
                                 self._asset_provider, 
                                 self._menu_action_coordinator, 
                                 component_provider, 
                                 self._platform_service_provider)

        @property
        def router(self) -> Router:
            return self._router

        @property
        def shortcut_action_coordinator(self) -> ShortcutActionCoordinator:
            return self._shortcut_action_coordinator
        
        @property
        def menu_action_coordinator(self) -> MenuActionCoordinator:
            return self._menu_action_coordinator
        
        @property
        def asset_provider(self) -> AssetProvider:
            return self._asset_provider

        @property
        def search_client_provider(self) -> DataSourceCardSearchClientProviding:
            return self._search_client_provider
        
        @property
        def local_managed_sets_data_source(self) -> DataSourceLocallyManagedSets:
            return self._local_managed_sets_data_source

from AppCore.CoreDependenciesProvider import CoreDependenciesProvider
from AppCore.DataFetcher import *
from AppCore.DataSource import DataSourceLocallyManagedSets
from AppCore.DataSource.DataSourceCardSearch import *
from AppCore.DataSource.DataSourceRecentPublished import *
from AppCore.DataSource.DataSourceRecentSearch import *
from AppCore.ImageResource import *
from AppUI.Coordinators import ShortcutActionCoordinator

from .AppDependenciesProviding import *
from .Assets import AssetProvider
from .Configuration.AppUIConfiguration import AppUIConfigurationManager
from .ExternalAppDependenciesProviding import ExternalAppDependenciesProviding
from .Router import Router
from .UIComponents.ScreenWidgetProvider import ScreenWidgetProvider


class AppDependenciesProvider(CoreDependenciesProvider, AppDependenciesProviding):
        def __init__(self, 
                     observation_tower: ObservationTower, 
                     configuration_manager: ConfigurationManager, 
                     asset_provider: AssetProvider, 
                     external_app_dependencies_provider: ExternalAppDependenciesProviding):
            super().__init__(observation_tower, configuration_manager)
            self._asset_provider = asset_provider
            self._external_app_dependencies_provider = external_app_dependencies_provider
            self._shortcut_action_coordinator = ShortcutActionCoordinator()
            self._app_ui_configuration = AppUIConfigurationManager(self._configuration_manager)
            
            self._local_managed_sets_data_source = DataSourceLocallyManagedSets(self._configuration_manager,
                                                                                self._observation_tower,
                                                                                self._data_serializer,
                                                                                client=self._external_app_dependencies_provider.locally_managed_sets_client)
            
            client_provider = external_app_dependencies_provider.data_source_card_search_client_provider(self._local_managed_sets_data_source)
            self._search_client_provider = client_provider
            
            self._router = Router(ScreenWidgetProvider(self))

        @property
        def router(self) -> Router:
            return self._router

        @property
        def shortcut_action_coordinator(self) -> ShortcutActionCoordinator:
            return self._shortcut_action_coordinator
        
        @property
        def asset_provider(self) -> AssetProvider:
            return self._asset_provider

        @property
        def search_client_provider(self) -> DataSourceCardSearchClientProviding:
            return self._search_client_provider
        
        @property
        def local_managed_sets_data_source(self) -> DataSourceLocallyManagedSets:
            return self._local_managed_sets_data_source
        
        @property
        def app_ui_configuration_manager(self) -> AppUIConfigurationManager:
            return self._app_ui_configuration
        
        @property
        def external_app_dependencies_provider(self) -> ExternalAppDependenciesProviding:
            return self._external_app_dependencies_provider
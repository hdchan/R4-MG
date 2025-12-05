
from AppCore.Config import ConfigurationManager
from AppCore.CoreDependenciesProvider import CoreDependenciesProvider
from AppCore.DataSource import (
        DataSourceCardSearchClientProviding,
        DataSourceLocallyManagedSets,
)
from AppCore.Models import ModelTransformer
from AppCore.Observation import ObservationTower
from AppUI.Coordinators import ShortcutActionCoordinator

from AppUI.AppDependenciesInternalProviding import AppDependenciesInternalProviding
from AppUI.AppDependenciesProviding import AppDependenciesProviding
from AppUI.Assets import AssetProvider
from AppUI.Configuration.AppUIConfiguration import AppUIConfigurationManager
from AppUI.ExternalAppDependenciesProviding import ExternalAppDependenciesProviding
from AppUI.Router.Router import Router
from AppUI.UIComponents.ScreenWidgetProvider import ScreenWidgetProvider


class AppDependenciesProvider(CoreDependenciesProvider, AppDependenciesProviding, AppDependenciesInternalProviding):
        def __init__(self, 
                     observation_tower: ObservationTower, 
                     configuration_manager: ConfigurationManager,
                     model_transformer: ModelTransformer,
                     external_app_dependencies_provider: ExternalAppDependenciesProviding):
            super().__init__(observation_tower, configuration_manager, model_transformer)
            self._asset_provider = AssetProvider()
            self._external_app_dependencies_provider = external_app_dependencies_provider
            self._shortcut_action_coordinator = ShortcutActionCoordinator()
            self._app_ui_configuration = AppUIConfigurationManager(self._configuration_manager)
            
            self._local_managed_sets_data_source = DataSourceLocallyManagedSets(self._configuration_manager,
                                                                                self._observation_tower,
                                                                                self._data_serializer,
                                                                                client=self._external_app_dependencies_provider.locally_managed_sets_client)
            
            self._router = Router(ScreenWidgetProvider(self, self))

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
            return self.external_app_dependencies_provider.data_source_card_search_client_provider(self._local_managed_sets_data_source)
        
        @property
        def local_managed_sets_data_source(self) -> DataSourceLocallyManagedSets:
            return self._local_managed_sets_data_source
        
        @property
        def app_ui_configuration_manager(self) -> AppUIConfigurationManager:
            return self._app_ui_configuration
        
        @property
        def external_app_dependencies_provider(self) -> ExternalAppDependenciesProviding:
            return self._external_app_dependencies_provider
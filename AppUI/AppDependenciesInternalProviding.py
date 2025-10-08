from AppCore.CoreDependenciesProviding import CoreDependenciesProviding
from AppCore.DataSource import DataSourceCardSearchClientProviding, DataSourceLocallyManagedSets

from .Assets import AssetProvider
from .Coordinators import ShortcutActionCoordinator
from .Router.Router import Router
from .Configuration.AppUIConfiguration import AppUIConfigurationManager
from .ExternalAppDependenciesProviding import ExternalAppDependenciesProviding

class AppDependenciesInternalProviding(CoreDependenciesProviding):
    
    @property
    def router(self) -> Router:
        raise Exception
    
    @property
    def asset_provider(self) -> AssetProvider:
        raise Exception
    
    @property
    def shortcut_action_coordinator(self) -> ShortcutActionCoordinator:
        raise Exception
    
    @property
    def search_client_provider(self) -> DataSourceCardSearchClientProviding:
        raise Exception
    
    @property
    def local_managed_sets_data_source(self) -> DataSourceLocallyManagedSets:
        raise Exception
    
    @property
    def app_ui_configuration_manager(self) -> AppUIConfigurationManager:
        raise Exception
    
    @property
    def external_app_dependencies_provider(self) -> ExternalAppDependenciesProviding:
        raise Exception
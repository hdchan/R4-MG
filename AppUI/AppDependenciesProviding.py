from AppCore.CoreDependenciesProviding import CoreDependenciesProviding
from AppCore.DataSource import DataSourceCardSearchClientProviding, DataSourceLocallyManagedSets

from .Assets import AssetProvider
from .Coordinators import MenuActionCoordinator, ShortcutActionCoordinator
from .Router import Router


class AppDependenciesProviding(CoreDependenciesProviding):
    
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
    def menu_action_coordinator(self) -> MenuActionCoordinator:
        raise Exception
    
    @property
    def search_client_provider(self) -> DataSourceCardSearchClientProviding:
        raise Exception
    
    @property
    def local_managed_sets_data_source(self) -> DataSourceLocallyManagedSets:
        raise Exception
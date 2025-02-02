from AppCore.CoreDependencyProviding import CoreDependencyProviding

from .Assets import AssetProvider
from .Coordinators import MenuActionCoordinator, ShortcutActionCoordinator
from .Router import Router


class AppDependencyProviding(CoreDependencyProviding):
    
    @property
    def router(self) -> Router:
        return NotImplemented
    
    @property
    def asset_provider(self) -> AssetProvider:
        return NotImplemented
    
    @property
    def shortcut_action_coordinator(self) -> ShortcutActionCoordinator:
        return NotImplemented
    
    @property
    def menu_action_coordinator(self) -> MenuActionCoordinator:
        return NotImplemented
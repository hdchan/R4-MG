from AppCore.CoreDependencyProviding import CoreDependencyProviding
from .Assets import AssetProvider

class AppDependencyProviding(CoreDependencyProviding):
    @property
    def asset_provider(self) -> AssetProvider:
        return NotImplemented
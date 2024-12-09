from AppCore.CoreDependencyProviding import CoreDependencyProviding
from AppCore.Data import APIClientProviding

from .Assets import AssetProvider


class AppDependencyProviding(CoreDependencyProviding):
    # TODO: should not make the available
    @property
    def api_client_provider(self) -> APIClientProviding:
        return NotImplemented
    
    @property
    def asset_provider(self) -> AssetProvider:
        return NotImplemented
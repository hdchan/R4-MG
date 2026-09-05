from AppCore.Config import Configuration

from ..SWUAppDependenciesProviding import SWUAppDependenciesProviding
from .DeckListImageGenerator import DeckListImageGenerator
from .DeckListImageGeneratorProtocol import (
    DeckListImageGeneratorProtocol,
    DeckListImageGeneratorProviding,
)


class DeckListImageGeneratorProvider(DeckListImageGeneratorProviding):
    def __init__(self, swu_app_dependencies_provider: SWUAppDependenciesProviding):
        self._configuration_manager = swu_app_dependencies_provider.configuration_manager
        self._latest = DeckListImageGenerator(swu_app_dependencies_provider)

    @property
    def _configuration(self) -> Configuration:
        return self._configuration_manager.configuration.core_configuration

    @property
    def image_generator(self) -> DeckListImageGeneratorProtocol:
        return self._latest
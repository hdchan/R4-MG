from typing import List, Union

from ..SWUAppDependenciesProviding import SWUAppDependenciesProviding
from .ExportImportFormattable import ExportFormattable, Importable
from .Handlers.MeleeGGHandler import MGGHandler
from .Handlers.SWUDBHandler import SWUDBHandler


class HandlerProvider:
    def __init__(self, 
                 swu_app_dependencies_provider: SWUAppDependenciesProviding):
        self._swu_app_dependencies_provider = swu_app_dependencies_provider
        self._handlers: List[Union[ExportFormattable, Importable]] = [
            MGGHandler(swu_app_dependencies_provider),
            SWUDBHandler(swu_app_dependencies_provider),
            # CSVHandler(swu_app_dependencies_provider),
        ]

    @property
    def import_handlers(self) -> List[Importable]:
        return self._handlers
    
    @property
    def export_handlers(self) -> List[ExportFormattable]:
        return self._handlers
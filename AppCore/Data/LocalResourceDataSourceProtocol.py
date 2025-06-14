from typing import Optional

from AppCore.Models import LocalCardResource


class LocalResourceDataSourceProtocol:
    @property
    def selected_local_resource(self) -> Optional[LocalCardResource]:
        return None

class LocalResourceDataSourceProviding:
    @property
    def data_source(self) -> LocalResourceDataSourceProtocol:
        return NotImplemented
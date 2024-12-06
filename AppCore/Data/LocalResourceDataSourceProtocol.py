from typing import Optional

from ..Models import LocalCardResource


class LocalResourceDataSourceProtocol:
    @property
    def selected_local_resource(self) -> Optional[LocalCardResource]:
        return NotImplemented

class LocalResourceDataSourceProviderProtocol:
    @property
    def data_source(self) -> LocalResourceDataSourceProtocol:
        return NotImplemented
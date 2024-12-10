from typing import Optional

from ..Models import LocalCardResource


class LocalResourceDataSourceProtocol:
    @property
    def selected_local_resource(self) -> Optional[LocalCardResource]:
        return NotImplemented
    
    @property
    def site_source_url(self) -> str:
        return NotImplemented

class LocalResourceDataSourceProviding:
    @property
    def data_source(self) -> LocalResourceDataSourceProtocol:
        return NotImplemented
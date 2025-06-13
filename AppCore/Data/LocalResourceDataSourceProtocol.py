from typing import Optional

from AppCore.Models import LocalCardResource


class LocalResourceDataSourceProtocol:
    @property
    def selected_local_resource(self) -> Optional[LocalCardResource]:
        return None
    
    @property
    def source_display_name(self) -> str:
        return NotImplemented
    
    @property
    def site_source_url(self) -> Optional[str]:
        return None

class LocalResourceDataSourceProviding:
    @property
    def data_source(self) -> LocalResourceDataSourceProtocol:
        return NotImplemented
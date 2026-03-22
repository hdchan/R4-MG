from typing import Optional

from AppCore.Models.LocalCardResource import LocalCardResource


class DataSourceSelectedLocalCardResourceProtocol:
    @property
    def selected_local_resource(self) -> Optional[LocalCardResource]:
        return None

class LocalResourceDataSourceProviding:
    @property
    def data_source(self) -> DataSourceSelectedLocalCardResourceProtocol:
        raise NotImplementedError
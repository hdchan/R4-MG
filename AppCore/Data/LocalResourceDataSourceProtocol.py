class LocalResourceDataSourceProtocol:
    pass

class LocalResourceDataSourceProviderProtocol:
    @property
    def data_source(self) -> LocalResourceDataSourceProtocol:
        return NotImplemented
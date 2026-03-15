from AppUI.AppDependenciesInternalProviding import AppDependenciesInternalProviding
from AppCore.DataSource.DraftList import (DataSourceDraftListProtocol)

class AppDependenciesInternalProvider_mock(AppDependenciesInternalProviding):
    
    @property
    def data_source_draft_list(self) -> DataSourceDraftListProtocol:
        pass
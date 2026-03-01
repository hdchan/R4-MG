from AppUI.AppDependenciesInternalProviding import AppDependenciesInternalProviding
from AppCore.DataSource import (DataSourceDraftList)

class AppDependenciesInternalProvider_mock(AppDependenciesInternalProviding):
    
    @property
    def data_source_draft_list(self) -> DataSourceDraftList:
        pass
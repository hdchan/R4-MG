from AppUI.AppDependenciesInternalProviding import AppDependenciesInternalProviding
from AppCore.DataSource.DraftList import (DataSourceDraftListProviding)

class AppDependenciesInternalProvider_mock(AppDependenciesInternalProviding):
    
    @property
    def data_source_draft_list_provider(self) -> DataSourceDraftListProviding:
        pass
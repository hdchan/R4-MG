from AppCore.CoreDependenciesProviding import CoreDependenciesProviding
from AppCore.DataSource import (DataSourceCardSearchClientProviding)

from .Configuration.AppUIConfiguration import AppUIConfigurationManager
from .Router.Router import Router


class AppDependenciesProviding(CoreDependenciesProviding):
    
    @property
    def router(self) -> Router:
        raise Exception
    
    @property
    def search_client_provider(self) -> DataSourceCardSearchClientProviding:
        raise Exception
    
    @property
    def app_ui_configuration_manager(self) -> AppUIConfigurationManager:
        raise Exception

from typing import Callable, Optional

from AppCore.DataSource import DataSourceDraftList
from AppCore.Observation.ObservationTower import ObservationTower
from AppUI.AppDependenciesInternalProviding import \
    AppDependenciesInternalProviding

from .Assets import AssetProvider
from .Config.SWUAppConfiguration import SWUAppConfigurationManager
from .SWUAppDependenciesProviding import SWUAppDependenciesProviding
from AppCore.DataSource.DataSourceCardSearch import DataSourceCardSearch, DataSourceCardSearchDelegate
from AppCore.DataSource.DataSourceCardSearchClientProtocol import DataSourceCardSearchClientProviding

class SWUAppDependenciesProvider(SWUAppDependenciesProviding):

    def __init__(self, 
                 lazy_app_ui_dependencies_provider: Callable[[], AppDependenciesInternalProviding]):
        self._lazy_app_ui_dependencies_provider = lazy_app_ui_dependencies_provider
        self._asset_provider = AssetProvider()
        self._configuration_manager: Optional[SWUAppConfigurationManager] = None

    @property
    def _app_ui_dependencies_provider(self) -> AppDependenciesInternalProviding:
        return self._lazy_app_ui_dependencies_provider()

    @property
    def observation_tower(self) -> ObservationTower:
        return self._app_ui_dependencies_provider.observation_tower
    
    @property
    def asset_provider(self) -> AssetProvider:
        return self._asset_provider
    
    @property
    def configuration_manager(self) -> SWUAppConfigurationManager:
        if self._configuration_manager is None:
            self._configuration_manager = SWUAppConfigurationManager(self._app_ui_dependencies_provider.configuration_manager)
        return self._configuration_manager
    
    @property
    def data_source_draft_list(self) -> DataSourceDraftList:
        return self._app_ui_dependencies_provider.data_source_draft_list
    
    def new_data_source_card_search(self,
                                    delegate: DataSourceCardSearchDelegate,
                                    search_client_provider: DataSourceCardSearchClientProviding) -> DataSourceCardSearch:
        return self._app_ui_dependencies_provider.new_instance_card_search_data_source(delegate, search_client_provider)
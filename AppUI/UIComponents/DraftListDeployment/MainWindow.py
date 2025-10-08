from AppUI.AppDependenciesInternalProviding import AppDependenciesInternalProviding
from AppUI.UIComponents import AppWindow, AppMenuBarBuilder

from .DraftListDeployerSearchComboViewController import \
    DraftListDeployerSearchComboViewController


class MainWindow(AppWindow):
    def __init__(self, app_dependencies_provider: AppDependenciesInternalProviding):
        super().__init__(app_dependencies_provider=app_dependencies_provider, 
                         central_widget=DraftListDeployerSearchComboViewController(app_dependencies_provider),
                         window_config_identifier="draft_list",
                         default_width=500, 
                         default_height=400)
        self._router = app_dependencies_provider.router
        self._data_source_draft_list = app_dependencies_provider.data_source_draft_list
        self._external_app_dependencies_provider = app_dependencies_provider.external_app_dependencies_provider
        self._observation_tower = app_dependencies_provider.observation_tower
        self._configuration_manager = app_dependencies_provider.configuration_manager
        self._menu_bar_provider = AppMenuBarBuilder(app_dependencies_provider)
        
        self._menu_bar_provider.build_draft_list_menu_bar(self)
from AppUI.AppDependenciesInternalProviding import AppDependenciesInternalProviding
from AppUI.UIComponents.Base import AppWindow

\
from AppUI.UIComponents.Menu.AppMenuBarBuilder import AppMenuBarBuilder

from .MainProgramViewController import MainProgramViewController


class Window(AppWindow):
    def __init__(self,
                 app_dependencies_provider: AppDependenciesInternalProviding):
        super().__init__(app_dependencies_provider=app_dependencies_provider, 
                         central_widget=MainProgramViewController(app_dependencies_provider),
                         window_config_identifier="image_deployer",
                         default_width=400+900, 
                         default_height=900)
        self.configuration_manager = app_dependencies_provider.configuration_manager
        self.asset_provider = app_dependencies_provider.asset_provider
        self._observation_tower = app_dependencies_provider.observation_tower
        self._router = app_dependencies_provider.router
        self._menu_bar_builder = AppMenuBarBuilder(app_dependencies_provider)

        self._menu_bar_builder.build_image_deployment_menu_bar(self)
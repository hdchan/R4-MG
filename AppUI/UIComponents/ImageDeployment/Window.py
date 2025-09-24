
from typing import Optional

from PyQt5.QtGui import QCloseEvent

from AppUI.AppDependenciesProviding import AppDependenciesProviding
from AppUI.UIComponents.Base import AppWindow

from .ImageDeploymentMenuBar import ImageDeploymentMenuBar
from .MainProgramViewController import MainProgramViewController


class Window(AppWindow):
    def __init__(self,
                 app_dependencies_provider: AppDependenciesProviding):
        super().__init__(app_dependencies_provider=app_dependencies_provider, 
                         central_widget=MainProgramViewController(app_dependencies_provider),
                         window_config_identifier="image_deployer",
                         default_width=400+900, 
                         default_height=900)
        self.configuration_manager = app_dependencies_provider.configuration_manager
        self.asset_provider = app_dependencies_provider.asset_provider
        self._observation_tower = app_dependencies_provider.observation_tower
        self._router = app_dependencies_provider.router
        
        self._menu_action_coordinator = ImageDeploymentMenuBar(app_dependencies_provider)
        
        self._menu_action_coordinator.setParent(self)
        self._menu_action_coordinator.setNativeMenuBar(False) # can only be called after set parent
        self.setMenuBar(self._menu_action_coordinator)


    def closeEvent(self, a0: Optional[QCloseEvent]):
        print('closing')
        # https://stackoverflow.com/a/70081754
        # for window in QApplication.topLevelWidgets():
        #     window.close()
        self._router.close_all_child_views()

from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication
from AppUI.Clients.ExternalAppDependenciesProvider import ExternalAppDependenciesProvider
from AppCore.Config import Configuration, ConfigurationManager
from AppUI.UIComponents.ImageDeployment.Window import Window
from AppCore.Observation import ObservationTower
from AppUI.Assets import AssetProvider
from AppUI.AppDependenciesProvider import AppDependenciesProvider
from AppUI.UIComponents.DraftListDeployment.MainWindow import MainWindow
# TODO: graphing algorithm to sort dependencies?

class MainAssembly:
    def __init__(self):
        self.app = QApplication([])
        # Ensure this is set before config manager writes out to settings file
        self.app.setApplicationName(Configuration.APP_NAME)
        self._asset_provider = AssetProvider()
        self.app.setWindowIcon(QIcon(self._asset_provider.image.logo_path))
        self._style_app()
        # https://www.pythonguis.com/tutorials/packaging-pyqt5-pyside2-applications-windows-pyinstaller/#setting-an-application-icon
        # https://stackoverflow.com/a/35865441
        self._observation_tower = ObservationTower()
        self._configuration_manager = ConfigurationManager(self._observation_tower)
        self._external_app_dependencies_provider = ExternalAppDependenciesProvider(self._observation_tower, 
                                                                                   self._configuration_manager,
                                                                                   self._asset_provider)
        self._app_dependencies_provider = AppDependenciesProvider(self._observation_tower, 
                                                                  self._configuration_manager,
                                                                  self._asset_provider, 
                                                                  self._external_app_dependencies_provider)
        
        # self._start_main_program()
        self._app_dependencies_provider.router.open_image_deployment_view()
        # self._start_other_program()
        self._app_dependencies_provider.router.open_draft_list_deployment_view()
        
        self.app.exec()
    
    def _style_app(self):
        custom_font = self.app.font()
        custom_font.setPointSize(10)
        self.app.setFont(custom_font)

    def _start_main_program(self):
        self.main_window = Window(self._app_dependencies_provider)
        self.main_window.show()
    
    def _start_other_program(self):
        self.another_window = MainWindow(self._app_dependencies_provider)
        self.another_window.show()
        
if __name__ == '__main__':
    MainAssembly()
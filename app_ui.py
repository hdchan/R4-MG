from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication

from AppCore.Config import Configuration, ConfigurationManager
from AppCore.Observation import ObservationTower
from AppUI.AppDependenciesProvider import AppDependenciesProvider
from AppUI.Assets import AssetProvider
# TODO: graphing algorithm to sort dependencies?
from AppUI.CrashReporter import CrashReporter
from AppUI.UIComponents.DraftListDeployment.MainWindow import MainWindow
from AppUI.UIComponents.ImageDeployment.Window import Window
from SWUApp.SWUAppDelegate import SWUAppDelegate
from SWUApp.SWUAppDependenciesProvider import SWUAppDependenciesProvider
from SWUApp.DomainModelTransformer import DomainModelTransformer
class MainAssembly:
    def __init__(self):
        
        self.app = QApplication([])
        # Ensure this is set before config manager writes out to settings file
        self.app.setApplicationName(Configuration.APP_NAME)
        self._asset_provider = AssetProvider()
        self._style_app()
        # https://www.pythonguis.com/tutorials/packaging-pyqt5-pyside2-applications-windows-pyinstaller/#setting-an-application-icon
        # https://stackoverflow.com/a/35865441
        self._observation_tower = ObservationTower()
        self._configuration_manager = ConfigurationManager(self._observation_tower)
        self._observation_tower.set_debug(self._configuration_manager.configuration.is_developer_mode)
        self._swu_app_dependencies_provider = SWUAppDependenciesProvider(self._lazy_app_ui_dependencies_provider)
        self._swu_app_delegate = SWUAppDelegate(self._swu_app_dependencies_provider,
                                                self._configuration_manager)
        self._swu_model_transformer = DomainModelTransformer()
        self._app_ui_dependencies_provider = AppDependenciesProvider(self._observation_tower, 
                                                                  self._configuration_manager,
                                                                  self._asset_provider, 
                                                                  self._swu_model_transformer,
                                                                  self._swu_app_delegate)
        CrashReporter(self._app_ui_dependencies_provider)
        self._app_ui_dependencies_provider.router.open_image_deployment_view()
        self._app_ui_dependencies_provider.router.open_draft_list_deployment_view()
        if self._configuration_manager.configuration.is_draft_list_image_preview_enabled:
            self._app_ui_dependencies_provider.router.open_draft_list_image_preview_view()
        
        self.app.setWindowIcon(QIcon(self._swu_app_delegate.logo_path))
        self.app.exec()

    def _lazy_app_ui_dependencies_provider(self) -> AppDependenciesProvider:
        return self._app_ui_dependencies_provider

    def _style_app(self):
        custom_font = self.app.font()
        custom_font.setPointSize(10)
        self.app.setFont(custom_font)

    def _start_main_program(self):
        self.main_window = Window(self._app_ui_dependencies_provider)
        self.main_window.show()
    
    def _start_other_program(self):
        self.another_window = MainWindow(self._app_ui_dependencies_provider)
        self.another_window.show()


if __name__ == '__main__':
        MainAssembly()
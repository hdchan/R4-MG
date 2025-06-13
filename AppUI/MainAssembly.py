from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QWidget

from AppCore import *
from AppCore.CoreDependencies import CoreDependencies
from AppCore.Data.CardSearchDataSource import *
from AppCore.Data.RecentSearchDataSource import *
from AppCore.Image import *
from AppCore.Network import *
from AppUI.Coordinators import MenuActionCoordinator, ShortcutActionCoordinator
from AppUI.MainProgramViewController import MainProgramViewController
from AppUI.UIComponents import (CardSearchPreviewViewController,
                                ImageDeploymentListViewController,
                                ImagePreviewLocalResourceDataSourceDecorator)
from AppUI.Window import Window

from .AppDependencyProviding import *
from .Assets import AssetProvider
from .Clients.ClientProvider import ClientProvider
from .ComponentProvider import ComponentProviding
from .Coordinators import MenuActionCoordinator, ShortcutActionCoordinator
from .Router import Router
from .UIComponents.Base.AboutViewController import AboutViewController
from .UIComponents.Base.SettingsViewController import SettingsViewController
from .UIComponents.Base.ShortcutsViewController import ShortcutsViewController

# TODO: graphing algorithm to sort dependencies?

class MainAssembly(ComponentProviding):
    class AppDependencies(CoreDependencies, AppDependencyProviding):
        def __init__(self, component_provider: ComponentProviding):
            super().__init__()
            self._asset_provider = AssetProvider()
            
            client_provider = ClientProvider(ClientProvider.Dependencies(
                self._configuration_manager,
                self._asset_provider,
                RemoteNetworker(self._configuration_manager),
                LocalNetworker(self._configuration_manager)
                ))
            self._api_client_provider = client_provider
            self._image_source_provider = client_provider
            self._shortcut_action_coordinator = ShortcutActionCoordinator()
            self._menu_action_coordinator = MenuActionCoordinator(self._configuration_manager, 
                                                                  self._platform_service_provider)
            self._router = Router(self._image_resource_deployer, 
                                 self._asset_provider, 
                                 self._menu_action_coordinator, 
                                 component_provider, 
                                 self._platform_service_provider)

        @property
        def router(self) -> Router:
            return self._router

        @property
        def shortcut_action_coordinator(self) -> ShortcutActionCoordinator:
            return self._shortcut_action_coordinator
        
        @property
        def menu_action_coordinator(self) -> MenuActionCoordinator:
            return self._menu_action_coordinator
        
        @property
        def asset_provider(self) -> AssetProvider:
            return self._asset_provider

        @property
        def api_client_provider(self) -> APIClientProviding:
            return self._api_client_provider
    

    def __init__(self):
        self.app = QApplication([])
        # Ensure this is set before config manager writes out to settings file
        self.app.setApplicationName(Configuration.APP_NAME)
        self._app_dependencies = self.AppDependencies(self)
        self.app.setWindowIcon(QIcon(self._app_dependencies.asset_provider.image.logo_path))
        self._style_app()

        # https://www.pythonguis.com/tutorials/packaging-pyqt5-pyside2-applications-windows-pyinstaller/#setting-an-application-icon
        # https://stackoverflow.com/a/35865441
        
        # https://forum.qt.io/topic/142136/how-to-change-the-application-name-pyqt5/4
        # self.app.setApplicationDisplayName(self.configuration_manager.configuration.app_display_name)
        
        self.main_window = Window(self._app_dependencies)
        
        main_widget = self._assemble_main_widget()
        
        self.main_window.setCentralWidget(main_widget)
        self.main_window.show()
        self.app.exec()
    
    
    def _style_app(self):
        custom_font = self.app.font()
        custom_font.setPointSize(10)
        self.app.setFont(custom_font)

    def _assemble_main_widget(self) -> QWidget:
        recent_published_data_source = RecentPublishedDataSource(self._app_dependencies)
        
        recent_search_data_source = RecentSearchDataSource(self._app_dependencies)

        image_preview_view = ImagePreviewLocalResourceDataSourceDecorator(self._app_dependencies)
        
        card_search_view = CardSearchPreviewViewController(self._app_dependencies, 
                                                           recent_published_data_source,
                                                           recent_search_data_source,
                                                           image_preview_view)
        
        deployment_view = ImageDeploymentListViewController(self._app_dependencies,  
                                                            image_preview_view)

        main_program = MainProgramViewController(self._app_dependencies,
                                                card_search_view, 
                                                deployment_view)
        
        
        return main_program
    
    @property
    def about_view(self) -> QWidget:
        return AboutViewController(self._app_dependencies)
    
    @property
    def settings_view(self) -> QWidget:
        return SettingsViewController(self._app_dependencies)
    
    @property
    def shortcuts_view(self) -> QWidget:
        return ShortcutsViewController(self._app_dependencies)
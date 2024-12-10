from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication

from AppCore import *
from AppCore.CoreDependencies import CoreDependencies
from AppCore.Data.CardSearchDataSource import *
from AppCore.Image import *
from AppCore.ImageNetwork import MockImageFetcher, RemoteImageFetcher
from AppCore.Network import *
from AppUI.Coordinators import MenuActionCoordinator, ShortcutActionCoordinator
from AppUI.MainProgramViewController import MainProgramViewController
from AppUI.UIComponents import (CardSearchPreviewViewController,
                                ImageDeploymentListViewController)
from AppUI.Window import Window

from .AppDependencyProviding import *
from .Assets import AssetProvider
from .Clients import *

# TODO: graphing algorithm to sort dependencies?

class MainAssembly:
    class AppDependencies(CoreDependencies, AppDependencyProviding):
        def __init__(self):
            super().__init__()
            self._asset_provider = AssetProvider()
            self._image_resource_processor_provider = self._assemble_image_resource_processor_provider()
            self._api_client_provider = self._assemble_api_client_provider()
            self._image_source_provider = self._assemble_image_source_provider()
            
        @property
        def asset_provider(self) -> AssetProvider:
            return self._asset_provider
        
        @property
        def image_resource_processor_provider(self) -> ImageResourceProcessorProviding:
            return self._image_resource_processor_provider

        @property
        def api_client_provider(self) -> APIClientProviding:
            return self._api_client_provider
        
        @property
        def image_source_provider(self) -> CardImageSourceProviding:
            return self._image_source_provider
        
        def _assemble_api_client_provider(self) -> APIClientProviding:
            return SWUDBAPIClientProvider(self._configuration_manager, 
                                         SWUDBAPIRemoteClient(RemoteNetworker(self._configuration_manager)), 
                                         SWUDBAPILocalClient(LocalNetworker(self._configuration_manager),
                                                             self.asset_provider))
    
        def _assemble_image_resource_processor_provider(self) -> ImageResourceProcessorProviding:
            image_fetcher_provider = self._assemble_image_fetcher_provider()
            return ImageResourceProcessorProvider(ImageResourceProcessor(image_fetcher_provider,
                                                                         self.observation_tower))
        
        def _assemble_image_fetcher_provider(self) -> ImageFetcherProviding:
            return ImageFetcherProvider(self._configuration_manager, 
                                        RemoteImageFetcher(self._configuration_manager),
                                        MockImageFetcher(self._configuration_manager))
        
        def _assemble_image_source_provider(self) -> CardImageSourceProviding:
            return CardImageSourceProvider(self._configuration_manager,
                                           SWUDBAPIImageSource(),
                                           SWUDBImageSource())

    def __init__(self):
        self.app = QApplication([])
        # Ensure this is set before config manager writes out to settings file
        self.app.setApplicationName(Configuration.APP_NAME)
        self._style_app()
        
        self._app_dependencies = self.AppDependencies()

        # https://www.pythonguis.com/tutorials/packaging-pyqt5-pyside2-applications-windows-pyinstaller/#setting-an-application-icon
        # https://stackoverflow.com/a/35865441
        self.app.setWindowIcon(QIcon(self._app_dependencies.asset_provider.image.logo_path))
        # https://forum.qt.io/topic/142136/how-to-change-the-application-name-pyqt5/4
        # self.app.setApplicationDisplayName(self.configuration_manager.configuration.app_display_name)
        
        main_window = Window(self._app_dependencies)
        
        card_search_data_source = CardSearchDataSource(self._app_dependencies, 
                                                       self._app_dependencies.api_client_provider)
        
        
        image_resource_deployer = ImageResourceDeployer(self._app_dependencies.configuration_manager,
                                                        self._app_dependencies.observation_tower)
        
        card_search_view = CardSearchPreviewViewController(self._app_dependencies, 
                                                           card_search_data_source, 
                                                           self._app_dependencies.recent_published_data_source)
        
        deployment_view = ImageDeploymentListViewController(self._app_dependencies, 
                                                            image_resource_deployer, 
                                                            card_search_data_source)

        main_program = MainProgramViewController(self._app_dependencies,
                                                image_resource_deployer,
                                                card_search_view, 
                                                deployment_view)
        # TODO - remove
        deployment_view.image_preview_delegate = main_program
        deployment_view.add_image_cta.delegate = main_program
        image_resource_deployer.load_production_resources()
        
        self.menu_action_coordinator = MenuActionCoordinator(main_window,
                                                            main_program, 
                                                            self._app_dependencies)
        
        self.shortcut_action_coordinator = ShortcutActionCoordinator(main_program, 
                                                                     card_search_view, 
                                                                     deployment_view)

        main_window.setCentralWidget(main_program)
        main_window.show()
        self.app.exec()
    
    
    def _style_app(self):
        custom_font = self.app.font()
        custom_font.setPointSize(10)
        self.app.setFont(custom_font)
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication

from AppCore import *
from AppCore.ApplicationCore import ApplicationCore
from AppCore.Config import ConfigurationManager
from AppCore.Image import *
from AppCore.ImageNetwork import MockImageFetcher, RemoteImageFetcher
from AppCore.Network import *
from AppCore.Observation.ObservationTower import ObservationTower
from AppUI.Coordinators import MenuActionCoordinator, ShortcutActionCoordinator
from AppUI.MainProgramViewController import MainProgramViewController
from AppUI.UIComponents import CardSearchPreviewViewController
from AppUI.Window import Window

from .Assets import AssetProvider
from .Clients import *
from .AppDependencyProviding import *


class MainAssembly:
    class CoreDependencies(AppDependencyProviding):
        def __init__(self):
            self._observation_tower = ObservationTower()
            self._configuration_manager = ConfigurationManager(self.observation_tower)
            self._asset_provider = AssetProvider()
            self._image_resource_processor_provider = self._assemble_image_resource_processor_provider()
            self._api_client_provider = self._assemble_api_client_provider()
            self._image_source_provider = self._assemble_image_source_provider()

        @property
        def observation_tower(self) -> ObservationTower:
            return self._observation_tower
        
        @property
        def configuration_provider(self) -> ConfigurationProviding:
            return self._configuration_manager
        
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
            return SWUDBAPIClientProvider(self.configuration_provider, 
                                         SWUDBAPIRemoteClient(RemoteNetworker(self.configuration_provider)), 
                                         SWUDBAPILocalClient(LocalNetworker(self.configuration_provider),
                                                            self.asset_provider))
    
        def _assemble_image_resource_processor_provider(self) -> ImageResourceProcessorProviding:
            image_fetcher_provider = self._assemble_image_fetcher_provider()
            return ImageResourceProcessorProvider(ImageResourceProcessor(image_fetcher_provider,
                                                                         self.observation_tower))
        
        def _assemble_image_fetcher_provider(self) -> ImageFetcherProviding:
            return ImageFetcherProvider(self.configuration_provider, 
                                        RemoteImageFetcher(self.configuration_provider),
                                        MockImageFetcher(self.configuration_provider))
        
        def _assemble_image_source_provider(self) -> CardImageSourceProviding:
            return CardImageSourceProvider(self.configuration_provider,
                                           SWUDBAPIImageSource(),
                                           SWUDBImageSource())

    def __init__(self):
        self.app = QApplication([])
        # Ensure this is set before config manager writes out to settings file
        self.app.setApplicationName(Configuration.APP_NAME)
        self._style_app()
        
        self._app_dependencies = self.CoreDependencies()

        # https://www.pythonguis.com/tutorials/packaging-pyqt5-pyside2-applications-windows-pyinstaller/#setting-an-application-icon
        # https://stackoverflow.com/a/35865441
        self.app.setWindowIcon(QIcon(self._app_dependencies.asset_provider.image.logo_path))
        # https://forum.qt.io/topic/142136/how-to-change-the-application-name-pyqt5/4
        # self.app.setApplicationDisplayName(self.configuration_manager.configuration.app_display_name)
        
        main_window = Window(self._app_dependencies._configuration_manager,
                            self._app_dependencies.observation_tower, 
                            self._app_dependencies.asset_provider)
        
        main_program = self._assemble_main_program()
        main_program.load()
        
        self.menu_action_coordinator = MenuActionCoordinator(main_window,
                                                            main_program,
                                                            self._app_dependencies._configuration_manager, 
                                                            self._app_dependencies.asset_provider)
        
        self.shortcut_action_coordinator = ShortcutActionCoordinator(main_program)

        main_window.setCentralWidget(main_program)
        main_window.show()
        self.app.exec()
    
    
    def _style_app(self):
        custom_font = self.app.font()
        custom_font.setPointSize(10)
        self.app.setFont(custom_font)

    def _assemble_main_program(self) -> MainProgramViewController:
        application_core = ApplicationCore(self._app_dependencies.observation_tower,
                                           self._app_dependencies.configuration_provider)
        # TODO: inject card search data source into card search view
        card_search_data_source = CardSearchDataSource(self._app_dependencies.observation_tower, 
                                                       self._app_dependencies.api_client_provider, 
                                                       self._app_dependencies.image_resource_processor_provider, 
                                                       self._app_dependencies.configuration_provider, 
                                                       self._app_dependencies.image_source_provider)
        
        card_search_view = CardSearchPreviewViewController(self._app_dependencies)
        
        return MainProgramViewController(self._app_dependencies,
                                         application_core,
                                         card_search_data_source,
                                         card_search_view)

    

    
    
    
        
    